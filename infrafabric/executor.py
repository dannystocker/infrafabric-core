#!/usr/bin/env python3
"""
IF.executor - Policy-Governed Command Execution Service

Secure, policy-governed service for executing allow-listed shell commands
from sandboxed environments. Enables external process management without
giving direct shell access.

Use Cases:
- Start/stop external services (Meilisearch, Kamailio, Asterisk, GStreamer, FFmpeg)
- Check process status (pgrep, ps)
- Manage system resources from sandboxed adapters
- Enable provider integrations in Phases 1-6

Architecture:
- IF.bus integration for command requests/responses
- IF.governor capability checks (system.process.execute)
- IF.witness audit logging for all executions
- Policy-based allow-listing per swarm
- Timeout enforcement and resource limits

License: MIT
"""

import asyncio
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ExecutionPolicy:
    """Policy for allowed command executions"""

    def __init__(self, policy_data: Dict[str, Any]):
        """
        Initialize policy from JSON data

        Args:
            policy_data: Policy definition with 'allow' list

        Example policy:
            {
                "allow": [
                    {
                        "executable": "/usr/bin/pgrep",
                        "args_pattern": "^-f\\s+.*$",
                        "description": "Check process by name"
                    },
                    {
                        "executable": "/usr/bin/systemctl",
                        "args_pattern": "^(start|stop|status|restart)\\s+[a-zA-Z0-9_-]+\\.service$",
                        "description": "Manage systemd services"
                    }
                ]
            }
        """
        self.allow_list = policy_data.get('allow', [])
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance"""
        for rule in self.allow_list:
            if 'args_pattern' in rule:
                rule['_compiled_pattern'] = re.compile(rule['args_pattern'])

    def is_allowed(self, executable: str, args: List[str]) -> bool:
        """
        Check if command execution is allowed by policy

        Args:
            executable: Path to executable
            args: List of command arguments

        Returns:
            True if allowed, False otherwise
        """
        args_string = ' '.join(args)

        for rule in self.allow_list:
            # Check executable match
            if rule['executable'] != executable:
                continue

            # Check args pattern match
            if '_compiled_pattern' in rule:
                if rule['_compiled_pattern'].match(args_string):
                    logger.debug(f"Command allowed by rule: {rule.get('description', 'unnamed')}")
                    return True
            elif not args:  # No args required, no pattern specified
                return True

        logger.warning(f"Command denied: {executable} {args_string}")
        return False

    def get_matching_rule(self, executable: str, args: List[str]) -> Optional[Dict]:
        """Get the rule that matches this command"""
        args_string = ' '.join(args)

        for rule in self.allow_list:
            if rule['executable'] != executable:
                continue

            if '_compiled_pattern' in rule:
                if rule['_compiled_pattern'].match(args_string):
                    return rule
            elif not args:
                return rule

        return None


class IFExecutor:
    """
    Policy-governed command execution service

    Provides secure command execution with:
    - Policy-based allow-listing
    - IF.governor capability checks
    - IF.witness audit logging
    - Timeout enforcement
    - Resource isolation
    """

    def __init__(
        self,
        event_bus: Any,  # Type: EventBus from infrafabric.event_bus
        policy_dir: str = '/etc/infrafabric/policies',
        default_timeout_ms: int = 5000,
        max_timeout_ms: int = 30000
    ):
        """
        Initialize IF.executor service

        Args:
            event_bus: IF.bus event bus instance
            policy_dir: Directory containing swarm policy files
            default_timeout_ms: Default command timeout (ms)
            max_timeout_ms: Maximum allowed timeout (ms)
        """
        self.bus = event_bus
        self.policy_dir = Path(policy_dir)
        self.default_timeout_ms = default_timeout_ms
        self.max_timeout_ms = max_timeout_ms

        # Policy cache
        self._policy_cache: Dict[str, ExecutionPolicy] = {}

        # Statistics
        self.stats = {
            'total_requests': 0,
            'allowed': 0,
            'denied': 0,
            'executed': 0,
            'failed': 0,
            'timeouts': 0
        }

        logger.info(f"IF.executor initialized (policy_dir={policy_dir}, default_timeout={default_timeout_ms}ms)")

    async def start(self):
        """Start the executor service and subscribe to command requests"""
        logger.info("Starting IF.executor service...")

        await self.bus.subscribe(
            topic='if.command.system.execute',
            callback=self._handle_execute_request
        )

        logger.info("IF.executor service started - listening for commands")

    async def stop(self):
        """Stop the executor service"""
        logger.info("Stopping IF.executor service...")
        await self.bus.unsubscribe('if.command.system.execute')
        logger.info("IF.executor service stopped")

    async def _handle_execute_request(self, msg: Dict[str, Any]):
        """
        Handle incoming command execution request

        Message format:
            {
                "trace_id": "unique-trace-id",
                "swarm_id": "session-1-ndi",
                "executable": "/usr/bin/pgrep",
                "args": ["-f", "meilisearch"],
                "timeout_ms": 5000  # optional
            }
        """
        self.stats['total_requests'] += 1

        # Extract request fields
        trace_id = msg.get('trace_id', 'unknown')
        swarm_id = msg.get('swarm_id')
        executable = msg.get('executable')
        args = msg.get('args', [])
        timeout_ms = msg.get('timeout_ms', self.default_timeout_ms)

        # Validate required fields
        if not swarm_id:
            await self._send_error(trace_id, 'Missing required field: swarm_id')
            return

        if not executable:
            await self._send_error(trace_id, 'Missing required field: executable')
            return

        # Validate timeout
        if timeout_ms > self.max_timeout_ms:
            await self._send_error(
                trace_id,
                f'Timeout exceeds maximum: {timeout_ms}ms > {self.max_timeout_ms}ms'
            )
            return

        # Check capability
        if not await self._check_capability(swarm_id):
            self.stats['denied'] += 1
            await self._send_error(
                trace_id,
                f'Missing required capability: system.process.execute'
            )
            await self._log_operation(
                'command_denied_capability',
                swarm_id,
                executable,
                args,
                reason='Missing capability'
            )
            return

        # Load and check policy
        policy = await self._load_policy(swarm_id)
        if not policy:
            self.stats['denied'] += 1
            await self._send_error(trace_id, f'No policy found for swarm: {swarm_id}')
            await self._log_operation(
                'command_denied_policy',
                swarm_id,
                executable,
                args,
                reason='No policy'
            )
            return

        if not policy.is_allowed(executable, args):
            self.stats['denied'] += 1
            await self._send_error(
                trace_id,
                f'Command not allowed by policy: {executable} {" ".join(args)}'
            )
            await self._log_operation(
                'command_denied_policy',
                swarm_id,
                executable,
                args,
                reason='Not in allow-list'
            )
            return

        # Command is allowed - execute it
        self.stats['allowed'] += 1

        try:
            result = await asyncio.wait_for(
                self._execute_command(executable, args),
                timeout=timeout_ms / 1000
            )

            self.stats['executed'] += 1

            await self._send_result(
                trace_id=trace_id,
                success=True,
                exit_code=result['exit_code'],
                stdout=result['stdout'],
                stderr=result['stderr'],
                execution_time_ms=result['execution_time_ms']
            )

            await self._log_operation(
                'command_executed',
                swarm_id,
                executable,
                args,
                exit_code=result['exit_code'],
                execution_time_ms=result['execution_time_ms']
            )

        except asyncio.TimeoutError:
            self.stats['timeouts'] += 1
            await self._send_error(
                trace_id,
                f'Command execution timeout after {timeout_ms}ms'
            )
            await self._log_operation(
                'command_timeout',
                swarm_id,
                executable,
                args,
                timeout_ms=timeout_ms
            )

        except Exception as e:
            self.stats['failed'] += 1
            await self._send_error(trace_id, f'Execution failed: {str(e)}')
            await self._log_operation(
                'command_failed',
                swarm_id,
                executable,
                args,
                error=str(e)
            )

    async def _execute_command(self, executable: str, args: List[str]) -> Dict[str, Any]:
        """
        Execute command and capture output

        Args:
            executable: Path to executable
            args: Command arguments

        Returns:
            Dict with exit_code, stdout, stderr, execution_time_ms
        """
        start_time = datetime.now(timezone.utc)

        proc = await asyncio.create_subprocess_exec(
            executable,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout_bytes, stderr_bytes = await proc.communicate()

        end_time = datetime.now(timezone.utc)
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

        return {
            'exit_code': proc.returncode,
            'stdout': stdout_bytes.decode('utf-8', errors='replace'),
            'stderr': stderr_bytes.decode('utf-8', errors='replace'),
            'execution_time_ms': execution_time_ms
        }

    async def _check_capability(self, swarm_id: str) -> bool:
        """
        Check if swarm has required capability

        Args:
            swarm_id: Swarm identifier

        Returns:
            True if swarm has system.process.execute capability
        """
        # TODO: Integrate with IF.governor once available
        # For now, return True for development
        # In production, this should call:
        # return await IF.governor.check_capability(swarm_id, 'system.process.execute')

        logger.debug(f"Capability check for {swarm_id}: system.process.execute (dev mode: allowed)")
        return True

    async def _load_policy(self, swarm_id: str) -> Optional[ExecutionPolicy]:
        """
        Load execution policy for swarm

        Args:
            swarm_id: Swarm identifier

        Returns:
            ExecutionPolicy instance or None if not found
        """
        # Check cache
        if swarm_id in self._policy_cache:
            return self._policy_cache[swarm_id]

        # Load from file
        policy_file = self.policy_dir / swarm_id / 'executor_policy.json'

        if not policy_file.exists():
            logger.warning(f"Policy file not found: {policy_file}")
            return None

        try:
            with open(policy_file, 'r') as f:
                policy_data = json.load(f)

            policy = ExecutionPolicy(policy_data)
            self._policy_cache[swarm_id] = policy

            logger.info(f"Loaded policy for {swarm_id}: {len(policy.allow_list)} rules")
            return policy

        except Exception as e:
            logger.error(f"Failed to load policy {policy_file}: {e}")
            return None

    async def _send_result(
        self,
        trace_id: str,
        success: bool,
        exit_code: int = 0,
        stdout: str = '',
        stderr: str = '',
        execution_time_ms: int = 0
    ):
        """Send execution result to IF.bus"""
        message = {
            'trace_id': trace_id,
            'success': success,
            'exit_code': exit_code,
            'stdout': stdout,
            'stderr': stderr,
            'execution_time_ms': execution_time_ms,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        await self.bus.publish(
            topic='if.event.system.execute.result',
            message=message
        )

    async def _send_error(self, trace_id: str, error: str):
        """Send error response to IF.bus"""
        message = {
            'trace_id': trace_id,
            'success': False,
            'error': error,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        await self.bus.publish(
            topic='if.event.system.execute.result',
            message=message
        )

    async def _log_operation(
        self,
        operation: str,
        swarm_id: str,
        executable: str,
        args: List[str],
        **kwargs
    ):
        """
        Log operation to IF.witness for audit trail

        Args:
            operation: Operation type (command_executed, command_denied, etc.)
            swarm_id: Swarm identifier
            executable: Executable path
            args: Command arguments
            **kwargs: Additional metadata
        """
        # TODO: Integrate with IF.witness once available
        # For now, log to Python logger
        # In production, this should call:
        # await IF.witness.record_event(...)

        log_data = {
            'operation': operation,
            'swarm_id': swarm_id,
            'executable': executable,
            'args': args,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            **kwargs
        }

        logger.info(f"IF.witness log: {json.dumps(log_data)}")

    def get_stats(self) -> Dict[str, int]:
        """Get executor statistics"""
        return self.stats.copy()

    def clear_policy_cache(self):
        """Clear policy cache (useful for testing or policy updates)"""
        self._policy_cache.clear()
        logger.info("Policy cache cleared")


# Example usage
async def main():
    """Example usage of IF.executor"""
    from infrafabric.event_bus import EventBus

    # Initialize event bus and executor
    bus = EventBus()
    await bus.connect()

    executor = IFExecutor(bus, policy_dir='/etc/infrafabric/policies')
    await executor.start()

    # Executor is now listening for commands on IF.bus
    # Commands are sent via:
    # await bus.publish('if.command.system.execute', {
    #     'trace_id': 'trace-001',
    #     'swarm_id': 'session-1-ndi',
    #     'executable': '/usr/bin/pgrep',
    #     'args': ['-f', 'meilisearch'],
    #     'timeout_ms': 5000
    # })

    print("IF.executor running... Press Ctrl+C to stop")

    try:
        await asyncio.Event().wait()  # Run forever
    except KeyboardInterrupt:
        await executor.stop()
        await bus.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
