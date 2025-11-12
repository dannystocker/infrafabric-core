"""IF.coordinator - Atomic task coordination for S² swarms

This module implements atomic task claiming and real-time task broadcast
for coordinating work across multiple swarms without race conditions.

Philosophy: IF.ground (Wu Lun - 五倫)
- Atomic operations prevent double-claiming
- Real-time broadcast enables immediate task assignment
- Circuit breaker integration for failure handling

Part of Phase 0: P0.1.2 (CAS) + P0.1.3 (Pub/Sub)
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field

from infrafabric.event_bus import EventBus, get_event_bus
from infrafabric.witness import log_operation
from infrafabric.schemas.capability import Capability


@dataclass
class TaskMetadata:
    """Metadata for a task in the coordination system"""
    task_id: str
    status: str  # 'available', 'claimed', 'completed', 'failed'
    required_capabilities: List[Capability] = field(default_factory=list)
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    claimed_by: Optional[str] = None
    claimed_at: Optional[float] = None
    completed_at: Optional[float] = None


@dataclass
class SwarmRegistration:
    """Swarm registration for task subscriptions"""
    swarm_id: str
    capabilities: List[Capability]
    registered_at: float = field(default_factory=time.time)
    subscription_id: Optional[str] = None


class IFCoordinator:
    """Atomic task coordinator for S² swarm orchestration

    This class provides:
    - Atomic task claiming with CAS (P0.1.2)
    - Real-time task broadcast via pub/sub (P0.1.3)
    - Blocker detection and escalation
    - Integration with IF.witness for audit trails

    Example:
        >>> coordinator = IFCoordinator()
        >>> await coordinator.connect()
        >>>
        >>> # Register swarm
        >>> await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])
        >>>
        >>> # Create task
        >>> await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])
        >>>
        >>> # Claim task (atomic)
        >>> claimed = await coordinator.claim_task('session-7', 'task-123')
        >>> assert claimed == True  # First claim succeeds
        >>>
        >>> # Another swarm tries to claim
        >>> claimed2 = await coordinator.claim_task('session-5', 'task-123')
        >>> assert claimed2 == False  # Fails - already claimed
    """

    def __init__(self, event_bus: Optional[EventBus] = None):
        """Initialize IF.coordinator

        Args:
            event_bus: Optional EventBus instance (uses global if None)
        """
        self.event_bus = event_bus or get_event_bus()
        self.connected = False

        # Swarm registrations
        self.swarm_registry: Dict[str, SwarmRegistration] = {}

        # Performance tracking
        self.claim_latencies: List[float] = []
        self.push_latencies: List[float] = []

    async def connect(self) -> bool:
        """Connect to event bus

        Returns:
            True if connection successful
        """
        success = await self.event_bus.connect()
        self.connected = success

        log_operation(
            component='IF.coordinator',
            operation='connected',
            params={'event_bus': self.event_bus.host}
        )

        return success

    async def disconnect(self) -> bool:
        """Disconnect from event bus

        Returns:
            True if disconnection successful
        """
        success = await self.event_bus.disconnect()
        self.connected = False

        log_operation(
            component='IF.coordinator',
            operation='disconnected',
            params={}
        )

        return success

    # ========== P0.1.2: Atomic CAS Operations ==========

    async def create_task(
        self,
        task_id: str,
        required_capabilities: List[Capability],
        priority: int = 0
    ) -> bool:
        """Create a new task in the coordination system

        Args:
            task_id: Unique task identifier
            required_capabilities: Required swarm capabilities
            priority: Task priority (higher = more urgent)

        Returns:
            True if task created successfully

        Example:
            >>> await coordinator.create_task(
            ...     'task-123',
            ...     [Capability.CODE_ANALYSIS_PYTHON, Capability.TESTING_UNIT],
            ...     priority=10
            ... )
            True
        """
        if not self.connected:
            raise ConnectionError("Coordinator not connected")

        key = f'/tasks/{task_id}'

        # Check if task already exists
        existing = await self.event_bus.get(key)
        if existing is not None:
            return False  # Task already exists

        task = TaskMetadata(
            task_id=task_id,
            status='available',
            required_capabilities=required_capabilities,
            priority=priority,
        )

        # Store task
        success = await self.event_bus.put(key, task.__dict__)

        if success:
            log_operation(
                component='IF.coordinator',
                operation='task_created',
                params={
                    'task_id': task_id,
                    'required_capabilities': [c.value for c in required_capabilities],
                    'priority': priority,
                }
            )

        return success

    async def claim_task(self, swarm_id: str, task_id: str) -> bool:
        """Atomically claim a task (P0.1.2)

        This method uses compare-and-swap (CAS) to ensure only one swarm
        can claim a task, preventing race conditions.

        Args:
            swarm_id: ID of swarm attempting to claim
            task_id: ID of task to claim

        Returns:
            True if claim succeeded, False if task already claimed or doesn't exist

        Performance Target: <5ms claim latency

        Example:
            >>> # Swarm 1 claims task
            >>> success1 = await coordinator.claim_task('session-7', 'task-123')
            >>> assert success1 == True
            >>>
            >>> # Swarm 2 tries to claim same task
            >>> success2 = await coordinator.claim_task('session-5', 'task-123')
            >>> assert success2 == False  # Already claimed by session-7
        """
        if not self.connected:
            raise ConnectionError("Coordinator not connected")

        start_time = time.perf_counter()
        key = f'/tasks/{task_id}'

        # Get current task state
        current_task_dict = await self.event_bus.get(key)

        if current_task_dict is None:
            # Task doesn't exist
            log_operation(
                component='IF.coordinator',
                operation='claim_failed',
                params={
                    'swarm_id': swarm_id,
                    'task_id': task_id,
                    'reason': 'task_not_found',
                },
                severity='WARN'
            )
            return False

        # Check if task is available
        if current_task_dict['status'] != 'available':
            # Task already claimed or completed
            log_operation(
                component='IF.coordinator',
                operation='claim_failed',
                params={
                    'swarm_id': swarm_id,
                    'task_id': task_id,
                    'reason': 'task_not_available',
                    'current_status': current_task_dict['status'],
                    'claimed_by': current_task_dict.get('claimed_by'),
                },
                severity='INFO'
            )
            return False

        # Prepare claimed task state
        claimed_task_dict = current_task_dict.copy()
        claimed_task_dict['status'] = 'claimed'
        claimed_task_dict['claimed_by'] = swarm_id
        claimed_task_dict['claimed_at'] = time.time()

        # Atomic CAS: Claim only if still available
        success = await self.event_bus.compare_and_swap(
            key,
            current_task_dict,  # Expected: available
            claimed_task_dict   # New: claimed by this swarm
        )

        # Track latency
        latency_ms = (time.perf_counter() - start_time) * 1000
        self.claim_latencies.append(latency_ms)

        if success:
            log_operation(
                component='IF.coordinator',
                operation='task_claimed',
                params={
                    'swarm_id': swarm_id,
                    'task_id': task_id,
                    'latency_ms': latency_ms,
                },
                severity='INFO'
            )
        else:
            # CAS failed - another swarm claimed it first
            log_operation(
                component='IF.coordinator',
                operation='claim_race_lost',
                params={
                    'swarm_id': swarm_id,
                    'task_id': task_id,
                    'latency_ms': latency_ms,
                },
                severity='INFO'
            )

        return success

    async def complete_task(
        self,
        swarm_id: str,
        task_id: str,
        result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Mark task as completed

        Args:
            swarm_id: ID of swarm completing the task
            task_id: ID of task to complete
            result: Optional task result data

        Returns:
            True if task successfully marked complete
        """
        if not self.connected:
            raise ConnectionError("Coordinator not connected")

        key = f'/tasks/{task_id}'

        # Get current task state
        current_task_dict = await self.event_bus.get(key)

        if current_task_dict is None:
            return False  # Task doesn't exist

        # Verify this swarm owns the task
        if current_task_dict.get('claimed_by') != swarm_id:
            log_operation(
                component='IF.coordinator',
                operation='complete_failed',
                params={
                    'swarm_id': swarm_id,
                    'task_id': task_id,
                    'reason': 'not_claimed_by_swarm',
                    'claimed_by': current_task_dict.get('claimed_by'),
                },
                severity='WARN'
            )
            return False

        # Mark as completed
        completed_task_dict = current_task_dict.copy()
        completed_task_dict['status'] = 'completed'
        completed_task_dict['completed_at'] = time.time()
        if result:
            completed_task_dict['result'] = result

        success = await self.event_bus.put(key, completed_task_dict)

        if success:
            log_operation(
                component='IF.coordinator',
                operation='task_completed',
                params={
                    'swarm_id': swarm_id,
                    'task_id': task_id,
                    'execution_time': completed_task_dict['completed_at'] - current_task_dict.get('claimed_at', 0),
                }
            )

        return success

    async def fail_task(
        self,
        swarm_id: str,
        task_id: str,
        reason: str
    ) -> bool:
        """Mark task as failed

        Args:
            swarm_id: ID of swarm reporting failure
            task_id: ID of task that failed
            reason: Failure reason

        Returns:
            True if task successfully marked failed
        """
        if not self.connected:
            raise ConnectionError("Coordinator not connected")

        key = f'/tasks/{task_id}'

        # Get current task state
        current_task_dict = await self.event_bus.get(key)

        if current_task_dict is None:
            return False  # Task doesn't exist

        # Verify this swarm owns the task
        if current_task_dict.get('claimed_by') != swarm_id:
            return False

        # Mark as failed
        failed_task_dict = current_task_dict.copy()
        failed_task_dict['status'] = 'failed'
        failed_task_dict['completed_at'] = time.time()
        failed_task_dict['failure_reason'] = reason

        success = await self.event_bus.put(key, failed_task_dict)

        if success:
            log_operation(
                component='IF.coordinator',
                operation='task_failed',
                params={
                    'swarm_id': swarm_id,
                    'task_id': task_id,
                    'reason': reason,
                },
                severity='WARN'
            )

        return success

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status

        Args:
            task_id: Task identifier

        Returns:
            Task metadata dict, or None if task doesn't exist
        """
        if not self.connected:
            raise ConnectionError("Coordinator not connected")

        key = f'/tasks/{task_id}'
        return await self.event_bus.get(key)

    # ========== P0.1.3: Real-Time Task Broadcast ==========

    async def register_swarm(
        self,
        swarm_id: str,
        capabilities: List[Capability]
    ) -> bool:
        """Register swarm for task notifications (P0.1.3)

        This method subscribes the swarm to relevant task broadcasts
        based on its capabilities.

        Args:
            swarm_id: Unique swarm identifier
            capabilities: List of capabilities this swarm provides

        Returns:
            True if registration successful

        Example:
            >>> await coordinator.register_swarm(
            ...     'session-7',
            ...     [Capability.CODE_ANALYSIS_PYTHON, Capability.TESTING_UNIT]
            ... )
            True
        """
        if not self.connected:
            raise ConnectionError("Coordinator not connected")

        # Subscribe to task updates
        subscription_id = await self.event_bus.subscribe(
            '/tasks/',
            lambda key, value: self._on_task_update(swarm_id, key, value)
        )

        registration = SwarmRegistration(
            swarm_id=swarm_id,
            capabilities=capabilities,
            subscription_id=subscription_id
        )

        self.swarm_registry[swarm_id] = registration

        log_operation(
            component='IF.coordinator',
            operation='swarm_registered',
            params={
                'swarm_id': swarm_id,
                'capabilities': [c.value for c in capabilities],
                'subscription_id': subscription_id,
            }
        )

        return True

    def _on_task_update(self, swarm_id: str, key: str, value: Dict[str, Any]):
        """Internal callback for task updates

        Args:
            swarm_id: Swarm ID receiving notification
            key: Updated task key
            value: New task value
        """
        # This would trigger swarm to check if task matches capabilities
        # In Phase 0, this is a simple callback
        # In Phase 1, this could push to swarm's queue

        task_id = key.split('/')[-1]
        status = value.get('status', 'unknown')

        # Log notification (helps with debugging)
        log_operation(
            component='IF.coordinator',
            operation='task_notification_sent',
            params={
                'swarm_id': swarm_id,
                'task_id': task_id,
                'status': status,
            },
            severity='INFO'
        )

    async def push_task_to_swarm(
        self,
        swarm_id: str,
        task_id: str
    ) -> bool:
        """Push task notification directly to swarm (P0.1.3)

        This method sends an immediate notification to a specific swarm,
        faster than waiting for subscription updates.

        Args:
            swarm_id: Target swarm identifier
            task_id: Task identifier to notify about

        Returns:
            True if notification sent

        Performance Target: <10ms push latency

        Example:
            >>> # Orchestrator assigns task to specific swarm
            >>> await coordinator.push_task_to_swarm('session-7', 'task-123')
            True
        """
        if not self.connected:
            raise ConnectionError("Coordinator not connected")

        if swarm_id not in self.swarm_registry:
            return False  # Swarm not registered

        start_time = time.perf_counter()

        # Get task data
        task_data = await self.get_task_status(task_id)
        if task_data is None:
            return False  # Task doesn't exist

        # Create notification key
        notification_key = f'/notifications/{swarm_id}/{task_id}'

        # Push notification
        success = await self.event_bus.put(notification_key, {
            'task_id': task_id,
            'task_data': task_data,
            'timestamp': time.time(),
        })

        # Track latency
        latency_ms = (time.perf_counter() - start_time) * 1000
        self.push_latencies.append(latency_ms)

        if success:
            log_operation(
                component='IF.coordinator',
                operation='task_pushed',
                params={
                    'swarm_id': swarm_id,
                    'task_id': task_id,
                    'latency_ms': latency_ms,
                }
            )

        return success

    async def detect_blocker(
        self,
        swarm_id: str,
        blocker_info: Dict[str, Any]
    ) -> bool:
        """Detect and escalate blocker to orchestrator (P0.1.3)

        This method immediately notifies the orchestrator when a swarm
        encounters a blocking condition.

        Args:
            swarm_id: Swarm reporting the blocker
            blocker_info: Information about the blocker

        Returns:
            True if escalation sent

        Performance Target: <10ms escalation latency

        Example:
            >>> await coordinator.detect_blocker(
            ...     'session-7',
            ...     {
            ...         'type': 'circuit_breaker_tripped',
            ...         'reason': 'budget_exhausted',
            ...         'task_id': 'task-123'
            ...     }
            ... )
            True
        """
        if not self.connected:
            raise ConnectionError("Coordinator not connected")

        start_time = time.perf_counter()

        # Create blocker notification
        blocker_key = f'/blockers/{swarm_id}/{time.time()}'

        success = await self.event_bus.put(blocker_key, {
            'swarm_id': swarm_id,
            'blocker_info': blocker_info,
            'timestamp': time.time(),
        })

        latency_ms = (time.perf_counter() - start_time) * 1000

        if success:
            log_operation(
                component='IF.coordinator',
                operation='blocker_escalated',
                params={
                    'swarm_id': swarm_id,
                    'blocker_type': blocker_info.get('type', 'unknown'),
                    'latency_ms': latency_ms,
                },
                severity='HIGH'
            )

        return success

    # ========== Performance and Health Monitoring ==========

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get coordinator performance statistics

        Returns:
            Dictionary with performance metrics

        Example:
            >>> stats = coordinator.get_performance_stats()
            >>> assert stats['avg_claim_latency_ms'] < 5.0  # P0.1.2 target
            >>> assert stats['avg_push_latency_ms'] < 10.0  # P0.1.3 target
        """
        if not self.claim_latencies:
            avg_claim_latency = 0.0
        else:
            avg_claim_latency = sum(self.claim_latencies) / len(self.claim_latencies)

        if not self.push_latencies:
            avg_push_latency = 0.0
        else:
            avg_push_latency = sum(self.push_latencies) / len(self.push_latencies)

        return {
            'total_claims': len(self.claim_latencies),
            'avg_claim_latency_ms': avg_claim_latency,
            'max_claim_latency_ms': max(self.claim_latencies) if self.claim_latencies else 0.0,
            'total_pushes': len(self.push_latencies),
            'avg_push_latency_ms': avg_push_latency,
            'max_push_latency_ms': max(self.push_latencies) if self.push_latencies else 0.0,
            'registered_swarms': len(self.swarm_registry),
            'claim_latency_target_met': avg_claim_latency < 5.0,  # P0.1.2 target
            'push_latency_target_met': avg_push_latency < 10.0,   # P0.1.3 target
        }

    def health_check(self) -> Dict[str, Any]:
        """Check coordinator health

        Returns:
            Dictionary with health status
        """
        event_bus_health = self.event_bus.health_check()
        perf_stats = self.get_performance_stats()

        return {
            'status': 'healthy' if self.connected else 'disconnected',
            'connected': self.connected,
            'event_bus': event_bus_health,
            'performance': perf_stats,
            'swarms_registered': list(self.swarm_registry.keys()),
        }
