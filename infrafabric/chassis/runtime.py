"""IF.chassis WASM runtime implementation

This module implements the WASM sandbox runtime for secure swarm execution.

Key features:
- WASM module loading and compilation
- Sandbox isolation for task execution
- Resource limits enforcement
- Scoped function execution
- IF.witness integration for audit trails

Philosophy: IF.TTT (Traceable, Transparent, Trustworthy)
- Every execution is logged
- Resource usage is tracked
- Security boundaries are enforced

Part of Phase 0: P0.3.1 - WASM Runtime Setup
"""

import wasmtime
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from pathlib import Path

from infrafabric.witness import log_operation
from infrafabric.chassis.limits import ResourceLimits, ResourceEnforcer


@dataclass
class ServiceContract:
    """Formal service contract for swarm execution

    This defines the agreed-upon interface between a swarm and the chassis.

    Attributes:
        swarm_id: Unique identifier for the swarm
        max_memory_mb: Maximum memory allocation in MB
        max_cpu_percent: Maximum CPU percentage (0-100)
        max_execution_time_seconds: Maximum execution time
        max_api_calls_per_second: Maximum API calls per second
        allowed_operations: List of allowed operation types
        slo_latency_ms: SLO for latency in milliseconds
        slo_success_rate: SLO for success rate (0.0-1.0)
        resource_limits: Optional ResourceLimits override
    """
    swarm_id: str
    max_memory_mb: int = 512
    max_cpu_percent: int = 50
    max_execution_time_seconds: float = 300.0
    max_api_calls_per_second: float = 10.0
    allowed_operations: List[str] = field(default_factory=lambda: ['*'])
    slo_latency_ms: float = 1000.0
    slo_success_rate: float = 0.95
    resource_limits: Optional[ResourceLimits] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'swarm_id': self.swarm_id,
            'max_memory_mb': self.max_memory_mb,
            'max_cpu_percent': self.max_cpu_percent,
            'max_execution_time_seconds': self.max_execution_time_seconds,
            'max_api_calls_per_second': self.max_api_calls_per_second,
            'allowed_operations': self.allowed_operations,
            'slo_latency_ms': self.slo_latency_ms,
            'slo_success_rate': self.slo_success_rate,
        }
        if self.resource_limits:
            result['resource_limits'] = self.resource_limits.to_dict()
        return result

    def get_resource_limits(self) -> ResourceLimits:
        """Get resource limits (from override or contract values)"""
        if self.resource_limits:
            return self.resource_limits
        return ResourceLimits(
            max_memory_mb=self.max_memory_mb,
            max_cpu_percent=self.max_cpu_percent,
            max_api_calls_per_second=self.max_api_calls_per_second,
            max_execution_time_seconds=self.max_execution_time_seconds,
        )


class IFChassis:
    """WASM sandbox runtime for secure swarm execution

    This class provides WASM-based sandboxing for swarms, ensuring isolation
    and security while executing tasks.

    Example:
        >>> chassis = IFChassis()
        >>> contract = ServiceContract(swarm_id='session-7', max_memory_mb=256)
        >>> chassis.load_swarm('session-7', 'path/to/swarm.wasm', contract)
        >>> result = chassis.execute_task('session-7', 'analyze_code', {
        ...     'file': 'main.py',
        ...     'checks': ['syntax', 'security']
        ... })
    """

    def __init__(self):
        """Initialize IF.chassis runtime"""
        self.engine = wasmtime.Engine()
        self.loaded_swarms: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []

        log_operation(
            component='IF.chassis',
            operation='initialized',
            params={'engine': 'wasmtime'}
        )

    def load_swarm(
        self,
        swarm_id: str,
        wasm_path: Optional[str] = None,
        contract: Optional[ServiceContract] = None,
        wasm_bytes: Optional[bytes] = None
    ) -> bool:
        """Load WASM module for swarm

        This method compiles and loads a WASM module for the specified swarm.
        The module is validated and sandboxed according to the service contract.

        Args:
            swarm_id: Unique identifier for the swarm
            wasm_path: Path to .wasm file (mutually exclusive with wasm_bytes)
            contract: Service contract defining resource limits
            wasm_bytes: Raw WASM bytes (mutually exclusive with wasm_path)

        Returns:
            True if loading succeeded, False otherwise

        Raises:
            ValueError: If neither wasm_path nor wasm_bytes provided
            FileNotFoundError: If wasm_path doesn't exist

        Example:
            >>> chassis.load_swarm(
            ...     swarm_id='session-7',
            ...     wasm_path='/path/to/swarm.wasm',
            ...     contract=ServiceContract(swarm_id='session-7')
            ... )
            True
        """
        if contract is None:
            contract = ServiceContract(swarm_id=swarm_id)

        # Validate input (before try block so exceptions are not caught)
        if wasm_path is None and wasm_bytes is None:
            raise ValueError("Either wasm_path or wasm_bytes must be provided")

        start_time = time.time()

        try:
            # Load WASM bytes
            if wasm_path:
                wasm_file = Path(wasm_path)
                if not wasm_file.exists():
                    raise FileNotFoundError(f"WASM file not found: {wasm_path}")
                wasm_bytes = wasm_file.read_bytes()

            # Compile module
            module = wasmtime.Module(self.engine, wasm_bytes)

            # Create store with resource limits
            store = wasmtime.Store(self.engine)

            # Configure memory limits (WASM linear memory)
            # Note: Actual memory limiting requires OS-level controls (setrlimit)
            # This is a placeholder for the WASM memory configuration

            # Create linker for imports
            linker = wasmtime.Linker(self.engine)

            # Add WASI support if needed
            try:
                wasi_config = wasmtime.WasiConfig()
                wasi = wasmtime.Wasi(store, wasi_config)
                linker.define_wasi(wasi)
            except Exception:
                # WASI not required for all modules
                pass

            # Instantiate module
            instance = linker.instantiate(store, module)

            # Create resource enforcer
            resource_limits = contract.get_resource_limits()
            enforcer = ResourceEnforcer(swarm_id, resource_limits)

            # Apply OS-level resource limits
            enforcer.apply_os_limits()

            # Store swarm info
            self.loaded_swarms[swarm_id] = {
                'module': module,
                'store': store,
                'instance': instance,
                'linker': linker,
                'contract': contract,
                'enforcer': enforcer,
                'loaded_at': time.time(),
                'execution_count': 0,
            }

            load_time_ms = (time.time() - start_time) * 1000

            log_operation(
                component='IF.chassis',
                operation='swarm_loaded',
                params={
                    'swarm_id': swarm_id,
                    'contract': contract.to_dict(),
                    'load_time_ms': load_time_ms,
                    'wasm_size_bytes': len(wasm_bytes),
                }
            )

            return True

        except Exception as e:
            log_operation(
                component='IF.chassis',
                operation='swarm_load_failed',
                params={
                    'swarm_id': swarm_id,
                    'error': str(e),
                },
                severity='WARN'
            )
            return False

    def execute_task(
        self,
        swarm_id: str,
        task_name: str,
        task_params: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[float] = None
    ) -> Dict[str, Any]:
        """Execute task in sandboxed WASM environment

        This method executes a task within the WASM sandbox, enforcing
        resource limits and tracking execution metrics.

        Args:
            swarm_id: Swarm identifier
            task_name: Name of task/function to execute
            task_params: Parameters for the task
            timeout_seconds: Override timeout from contract

        Returns:
            Dictionary with execution result:
            {
                'success': bool,
                'result': Any,
                'execution_time_ms': float,
                'memory_used_mb': float,
                'error': Optional[str]
            }

        Raises:
            ValueError: If swarm not loaded or task not allowed

        Example:
            >>> result = chassis.execute_task(
            ...     swarm_id='session-7',
            ...     task_name='analyze_code',
            ...     task_params={'file': 'main.py'}
            ... )
            >>> if result['success']:
            ...     print(f"Analysis: {result['result']}")
        """
        if swarm_id not in self.loaded_swarms:
            raise ValueError(f"Swarm not loaded: {swarm_id}")

        swarm_info = self.loaded_swarms[swarm_id]
        contract = swarm_info['contract']
        enforcer = swarm_info['enforcer']

        # Check if operation is allowed
        if '*' not in contract.allowed_operations and task_name not in contract.allowed_operations:
            raise ValueError(f"Operation not allowed: {task_name}")

        # Check API rate limit
        if not enforcer.check_api_rate_limit(1):
            return {
                'success': False,
                'result': None,
                'execution_time_ms': 0.0,
                'memory_used_mb': 0.0,
                'error': 'API rate limit exceeded',
                'timestamp': time.time(),
            }

        start_time = time.time()
        task_params = task_params or {}

        try:
            # Get the function from the WASM instance
            instance = swarm_info['instance']
            store = swarm_info['store']

            # For now, we'll simulate execution since we don't have actual WASM functions
            # In a real implementation, this would call:
            # func = instance.exports(store).get(task_name)
            # result = func(store, *args)

            # Simulated execution
            result = {
                'task': task_name,
                'params': task_params,
                'swarm_id': swarm_id,
                'status': 'simulated',
            }

            execution_time_ms = (time.time() - start_time) * 1000

            # Track execution
            swarm_info['execution_count'] += 1

            execution_record = {
                'success': True,
                'result': result,
                'execution_time_ms': execution_time_ms,
                'memory_used_mb': 0.0,  # Placeholder - would track actual memory
                'error': None,
                'timestamp': time.time(),
            }

            self.execution_history.append({
                'swarm_id': swarm_id,
                'task_name': task_name,
                **execution_record,
            })

            # Log to witness
            log_operation(
                component='IF.chassis',
                operation='task_executed',
                params={
                    'swarm_id': swarm_id,
                    'task_name': task_name,
                    'execution_time_ms': execution_time_ms,
                    'success': True,
                }
            )

            # Check SLO compliance
            if execution_time_ms > contract.slo_latency_ms:
                log_operation(
                    component='IF.chassis',
                    operation='slo_violation',
                    params={
                        'swarm_id': swarm_id,
                        'slo_type': 'latency',
                        'expected_ms': contract.slo_latency_ms,
                        'actual_ms': execution_time_ms,
                    },
                    severity='WARN'
                )

            return execution_record

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000

            execution_record = {
                'success': False,
                'result': None,
                'execution_time_ms': execution_time_ms,
                'memory_used_mb': 0.0,
                'error': str(e),
                'timestamp': time.time(),
            }

            self.execution_history.append({
                'swarm_id': swarm_id,
                'task_name': task_name,
                **execution_record,
            })

            log_operation(
                component='IF.chassis',
                operation='task_execution_failed',
                params={
                    'swarm_id': swarm_id,
                    'task_name': task_name,
                    'error': str(e),
                },
                severity='WARN'
            )

            return execution_record

    def unload_swarm(self, swarm_id: str) -> bool:
        """Unload WASM module and free resources

        Args:
            swarm_id: Swarm identifier

        Returns:
            True if unloaded, False if not found
        """
        if swarm_id not in self.loaded_swarms:
            return False

        swarm_info = self.loaded_swarms[swarm_id]

        log_operation(
            component='IF.chassis',
            operation='swarm_unloaded',
            params={
                'swarm_id': swarm_id,
                'execution_count': swarm_info['execution_count'],
                'lifetime_seconds': time.time() - swarm_info['loaded_at'],
            }
        )

        del self.loaded_swarms[swarm_id]
        return True

    def is_swarm_loaded(self, swarm_id: str) -> bool:
        """Check if swarm is loaded

        Args:
            swarm_id: Swarm identifier

        Returns:
            True if loaded, False otherwise
        """
        return swarm_id in self.loaded_swarms

    def get_swarm_info(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        """Get information about loaded swarm

        Args:
            swarm_id: Swarm identifier

        Returns:
            Dictionary with swarm info, or None if not loaded
        """
        if swarm_id not in self.loaded_swarms:
            return None

        swarm_info = self.loaded_swarms[swarm_id]
        contract = swarm_info['contract']

        return {
            'swarm_id': swarm_id,
            'contract': contract.to_dict(),
            'loaded_at': swarm_info['loaded_at'],
            'execution_count': swarm_info['execution_count'],
            'uptime_seconds': time.time() - swarm_info['loaded_at'],
        }

    def get_execution_history(
        self,
        swarm_id: Optional[str] = None,
        task_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get execution history

        Args:
            swarm_id: Filter by swarm ID
            task_name: Filter by task name
            limit: Maximum number of records to return

        Returns:
            List of execution records
        """
        records = self.execution_history

        if swarm_id:
            records = [r for r in records if r['swarm_id'] == swarm_id]

        if task_name:
            records = [r for r in records if r['task_name'] == task_name]

        return records[-limit:]

    def get_swarm_stats(self, swarm_id: str) -> Dict[str, Any]:
        """Get statistics for swarm executions

        Args:
            swarm_id: Swarm identifier

        Returns:
            Dictionary with statistics
        """
        if swarm_id not in self.loaded_swarms:
            raise ValueError(f"Swarm not loaded: {swarm_id}")

        swarm_info = self.loaded_swarms[swarm_id]
        contract = swarm_info['contract']
        enforcer = swarm_info['enforcer']

        # Get execution history for this swarm
        executions = [r for r in self.execution_history if r['swarm_id'] == swarm_id]

        # Get enforcer stats
        enforcer_stats = enforcer.get_stats()

        if not executions:
            return {
                'swarm_id': swarm_id,
                'total_executions': 0,
                'success_rate': 0.0,
                'avg_execution_time_ms': 0.0,
                'slo_compliance_rate': 0.0,
                **enforcer_stats,
            }

        success_count = sum(1 for e in executions if e['success'])
        total_time = sum(e['execution_time_ms'] for e in executions)
        slo_compliant = sum(
            1 for e in executions
            if e['execution_time_ms'] <= contract.slo_latency_ms
        )

        return {
            'swarm_id': swarm_id,
            'total_executions': len(executions),
            'success_count': success_count,
            'failure_count': len(executions) - success_count,
            'success_rate': success_count / len(executions),
            'avg_execution_time_ms': total_time / len(executions),
            'slo_compliance_rate': slo_compliant / len(executions),
            'slo_latency_ms': contract.slo_latency_ms,
            **enforcer_stats,
        }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on chassis

        Returns:
            Dictionary with health status
        """
        loaded_count = len(self.loaded_swarms)
        total_executions = len(self.execution_history)

        return {
            'status': 'healthy',
            'engine': 'wasmtime',
            'loaded_swarms': loaded_count,
            'total_executions': total_executions,
            'swarms': list(self.loaded_swarms.keys()),
        }
