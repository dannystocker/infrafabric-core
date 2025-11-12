"""
IF.executor - Policy-Governed Command Execution Service

Provides secure, audited execution of allow-listed shell commands from sandboxed
environments. Enables external process management without granting direct shell access.

**Problem Solved**: Sandboxed adapters need to manage external processes (Meilisearch,
Kamailio, Asterisk, GStreamer, FFmpeg) but shouldn't have unrestricted shell access.

**Impact**: Enables Phase 1-6 provider integrations with strong security boundaries.

Example:
    ```python
    from infrafabric.event_bus import EventBus
    from infrafabric.executor import IFExecutor

    bus = await EventBus().connect()
    executor = IFExecutor(bus, policy_dir='/etc/infrafabric/policies')
    await executor.start()

    # Swarm makes request via IF.bus
    await bus.publish('if.command.system.execute', {
        'trace_id': 'trace-123',
        'swarm_id': 'navidocs-adapter',
        'executable': '/usr/bin/pgrep',
        'args': ['-f', 'meilisearch'],
        'timeout_ms': 5000
    })

    # IF.executor validates policy, executes, and returns result
    # Result published to: if.event.system.execute.result
    ```

Architecture:
    IF.executor subscribes to IF.bus command topic, validates requests against
    per-swarm policy files, executes allow-listed commands with timeout enforcement,
    and logs all operations to IF.witness for audit trail.

Security:
    - Policy files define allow-list of executables and argument patterns
    - IF.governor capability check required: 'system.process.execute'
    - All executions logged to IF.witness (audit trail)
    - Timeout enforcement (default 5000ms)
    - No shell expansion (direct subprocess execution)
"""

import asyncio
import subprocess
import json
import time
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from infrafabric.event_bus import EventBus

logger = logging.getLogger(__name__)


class ExecutorError(Exception):
    """Base exception for executor errors"""
    pass


class PolicyViolationError(ExecutorError):
    """Command not allowed by policy"""
    pass


class TimeoutError(ExecutorError):
    """Command execution exceeded timeout"""
    pass


@dataclass
class ExecutionResult:
    """Result of command execution"""
    success: bool
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


@dataclass
class PolicyRule:
    """Single policy allow-list rule"""
    executable: str
    args_pattern: Optional[str] = None  # Regex pattern for args
    description: Optional[str] = None


@dataclass
class ExecutionPolicy:
    """Execution policy for a swarm"""
    swarm_id: str
    allow: List[PolicyRule]
    default_timeout_ms: int = 5000
    max_timeout_ms: int = 30000


class IFExecutor:
    """
    Policy-governed command execution service for IF

    Provides:
    - Secure command execution from sandboxed environments
    - Per-swarm policy enforcement (allow-list)
    - IF.witness audit logging (all executions)
    - Timeout enforcement (default 5000ms)
    - IF.governor capability integration

    Use Cases:
    - Start/stop external services (Meilisearch, Kamailio, Asterisk)
    - Check process status (pgrep, ps)
    - Manage system resources from sandboxed adapters

    Security Model:
        1. Check IF.governor capability: 'system.process.execute'
        2. Load swarm-specific policy file
        3. Validate executable + args against allow-list
        4. Execute with timeout enforcement
        5. Log to IF.witness (audit trail)
    """

    def __init__(
        self,
        event_bus: EventBus,
        policy_dir: str = '/etc/infrafabric/policies',
        witness_logger: Optional[Any] = None
    ):
        """
        Initialize IF.executor

        Args:
            event_bus: EventBus for IF.bus communication
            policy_dir: Directory containing per-swarm policy files
            witness_logger: Optional IF.witness logger (for testing, can be mock)
        """
        self.bus = event_bus
        self.policy_dir = Path(policy_dir)
        self.witness_logger = witness_logger
        self._policies: Dict[str, ExecutionPolicy] = {}
        self._watch_id: Optional[str] = None

    async def start(self):
        """
        Start IF.executor service

        Subscribes to IF.bus command topic: if.command.system.execute
        """
        logger.info("IF.executor starting...")

        # Subscribe to command execution requests
        self._watch_id = await self.bus.watch(
            'if.command.system.execute',
            callback=self._handle_execute_request
        )

        logger.info(f"IF.executor started (watch_id: {self._watch_id})")

    async def stop(self):
        """Stop IF.executor service"""
        if self._watch_id:
            # Note: EventBus doesn't have unwatch yet, would be added
            logger.info("IF.executor stopped")

    async def _handle_execute_request(self, event):
        """
        Process command execution request from IF.bus

        Message format:
        {
            'trace_id': 'trace-123',
            'swarm_id': 'navidocs-adapter',
            'executable': '/usr/bin/pgrep',
            'args': ['-f', 'meilisearch'],
            'timeout_ms': 5000
        }
        """
        try:
            if event.event_type != 'put':
                return

            msg = json.loads(event.value)

            trace_id = msg.get('trace_id')
            swarm_id = msg.get('swarm_id')
            executable = msg.get('executable')
            args = msg.get('args', [])
            timeout_ms = msg.get('timeout_ms', 5000)

            # Validate required fields
            if not all([trace_id, swarm_id, executable]):
                await self._send_result(
                    trace_id or 'unknown',
                    success=False,
                    error='Missing required fields: trace_id, swarm_id, executable'
                )
                return

            # 1. Check IF.governor capability
            if not await self._check_capability(swarm_id, 'system.process.execute'):
                await self._send_result(
                    trace_id,
                    success=False,
                    error=f'Swarm {swarm_id} lacks capability: system.process.execute'
                )
                self._log_witness('command_denied_capability', swarm_id, executable, args)
                return

            # 2. Load and validate policy
            try:
                policy = await self._load_policy(swarm_id)
            except Exception as e:
                await self._send_result(
                    trace_id,
                    success=False,
                    error=f'Policy load failed: {str(e)}'
                )
                return

            # 3. Validate command against policy
            if not self._validate_command(policy, executable, args):
                await self._send_result(
                    trace_id,
                    success=False,
                    error=f'Policy violation: {executable} {args} not allowed'
                )
                self._log_witness('command_denied_policy', swarm_id, executable, args)
                logger.warning(
                    f"Policy violation: swarm={swarm_id} executable={executable} args={args}"
                )
                return

            # 4. Execute with timeout
            timeout_ms = min(timeout_ms, policy.max_timeout_ms)

            try:
                result = await asyncio.wait_for(
                    self._execute(executable, args),
                    timeout=timeout_ms / 1000
                )

                await self._send_result(trace_id, **asdict(result))

                self._log_witness(
                    'command_executed',
                    swarm_id,
                    executable,
                    args,
                    {
                        'exit_code': result.exit_code,
                        'execution_time_ms': result.execution_time_ms,
                        'success': result.success
                    }
                )

                logger.info(
                    f"Executed: swarm={swarm_id} executable={executable} "
                    f"exit_code={result.exit_code} time={result.execution_time_ms:.2f}ms"
                )

            except asyncio.TimeoutError:
                await self._send_result(
                    trace_id,
                    success=False,
                    error=f'Execution timeout ({timeout_ms}ms exceeded)'
                )
                self._log_witness('command_timeout', swarm_id, executable, args,
                                {'timeout_ms': timeout_ms})
                logger.warning(
                    f"Timeout: swarm={swarm_id} executable={executable} timeout={timeout_ms}ms"
                )

        except Exception as e:
            logger.error(f"Error handling execute request: {e}", exc_info=True)
            if 'trace_id' in locals():
                await self._send_result(
                    trace_id,
                    success=False,
                    error=f'Internal error: {str(e)}'
                )

    async def _check_capability(self, swarm_id: str, capability: str) -> bool:
        """
        Check if swarm has required capability via IF.governor

        In production, this would query IF.governor. For now, checks etcd directly.
        """
        try:
            # Check if swarm has capability registered
            key = f'/swarms/{swarm_id}/capabilities'
            capabilities_json = await self.bus.get(key)

            if not capabilities_json:
                logger.warning(f"Swarm {swarm_id} not registered")
                return False

            capabilities = json.loads(capabilities_json)
            return capability in capabilities

        except Exception as e:
            logger.error(f"Capability check failed: {e}")
            return False

    async def _load_policy(self, swarm_id: str) -> ExecutionPolicy:
        """
        Load execution policy for swarm

        Policy file: {policy_dir}/{swarm_id}/executor_policy.json

        Format:
        {
            "swarm_id": "navidocs-adapter",
            "allow": [
                {
                    "executable": "/usr/bin/pgrep",
                    "args_pattern": "^-f\\s+meilisearch$",
                    "description": "Check if Meilisearch is running"
                },
                {
                    "executable": "/usr/bin/systemctl",
                    "args_pattern": "^(start|stop|status)\\s+meilisearch$",
                    "description": "Manage Meilisearch service"
                }
            ],
            "default_timeout_ms": 5000,
            "max_timeout_ms": 30000
        }
        """
        # Check cache first
        if swarm_id in self._policies:
            return self._policies[swarm_id]

        policy_file = self.policy_dir / swarm_id / 'executor_policy.json'

        if not policy_file.exists():
            raise PolicyViolationError(f"No policy file for swarm: {swarm_id}")

        with open(policy_file, 'r') as f:
            policy_data = json.load(f)

        # Parse policy
        policy = ExecutionPolicy(
            swarm_id=policy_data['swarm_id'],
            allow=[
                PolicyRule(**rule) for rule in policy_data.get('allow', [])
            ],
            default_timeout_ms=policy_data.get('default_timeout_ms', 5000),
            max_timeout_ms=policy_data.get('max_timeout_ms', 30000)
        )

        # Cache policy
        self._policies[swarm_id] = policy

        return policy

    def _validate_command(
        self,
        policy: ExecutionPolicy,
        executable: str,
        args: List[str]
    ) -> bool:
        """
        Validate command against policy allow-list

        Returns True if command matches any allow rule, False otherwise
        """
        args_str = ' '.join(args)

        for rule in policy.allow:
            # Check executable match
            if rule.executable != executable:
                continue

            # If no args pattern, allow any args
            if not rule.args_pattern:
                return True

            # Check args pattern match
            if re.match(rule.args_pattern, args_str):
                return True

        return False

    async def _execute(
        self,
        executable: str,
        args: List[str]
    ) -> ExecutionResult:
        """
        Execute command and capture output

        Uses subprocess without shell expansion for security
        """
        start_time = time.time()

        try:
            # Execute without shell (security)
            proc = await asyncio.create_subprocess_exec(
                executable,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout_bytes, stderr_bytes = await proc.communicate()

            execution_time_ms = (time.time() - start_time) * 1000

            stdout = stdout_bytes.decode('utf-8', errors='replace').strip()
            stderr = stderr_bytes.decode('utf-8', errors='replace').strip()

            return ExecutionResult(
                success=(proc.returncode == 0),
                exit_code=proc.returncode,
                stdout=stdout if stdout else None,
                stderr=stderr if stderr else None,
                execution_time_ms=execution_time_ms
            )

        except FileNotFoundError:
            return ExecutionResult(
                success=False,
                error=f'Executable not found: {executable}'
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f'Execution failed: {str(e)}'
            )

    async def _send_result(self, trace_id: str, **kwargs):
        """
        Publish execution result to IF.bus

        Topic: if.event.system.execute.result

        Message format:
        {
            'trace_id': 'trace-123',
            'success': True,
            'exit_code': 0,
            'stdout': '12345\\n',
            'stderr': None,
            'error': None,
            'execution_time_ms': 45.2
        }
        """
        result = {
            'trace_id': trace_id,
            **kwargs
        }

        await self.bus.put(
            f'if.event.system.execute.result/{trace_id}',
            json.dumps(result)
        )

    def _log_witness(
        self,
        operation: str,
        swarm_id: str,
        executable: str,
        args: List[str],
        extra: Optional[Dict] = None
    ):
        """
        Log operation to IF.witness for audit trail

        All command executions (allowed and denied) are logged
        """
        if not self.witness_logger:
            return

        log_entry = {
            'component': 'IF.executor',
            'operation': operation,
            'timestamp': time.time(),
            'swarm_id': swarm_id,
            'executable': executable,
            'args': args,
            **(extra or {})
        }

        # Support both callable and dict-based loggers
        if callable(self.witness_logger):
            self.witness_logger(log_entry)
        elif hasattr(self.witness_logger, 'log'):
            self.witness_logger.log(log_entry)
        elif hasattr(self.witness_logger, 'events'):
            self.witness_logger.events.append(log_entry)
