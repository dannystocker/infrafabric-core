"""IF.event_bus - Real-time event bus for S² coordination

This module provides a lightweight event bus abstraction for IF.coordinator.
Uses in-memory storage for Phase 0, with production etcd/NATS planned for Phase 1.

Philosophy: IF.ground (Wu Lun - 五倫)
- Real-time coordination between swarms
- Atomic operations for task claiming
- Publish/subscribe for task broadcast

Part of Phase 0: P0.1.1 - Event Bus Setup
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
import threading


@dataclass
class EventBusMessage:
    """Message in the event bus"""
    key: str
    value: Any
    timestamp: float
    version: int  # For CAS operations


class EventBus:
    """Real-time event bus for IF.coordinator

    Phase 0 Implementation: In-memory with threading locks
    Phase 1 Plan: Replace with etcd or NATS for production

    This class provides:
    - Key-value storage with versioning
    - Compare-and-swap (CAS) for atomic updates
    - Publish/subscribe for real-time notifications
    - Thread-safe operations

    Example:
        >>> bus = EventBus()
        >>> await bus.connect()
        >>> await bus.put('/tasks/task-123', {'status': 'available'})
        >>> value = await bus.get('/tasks/task-123')
    """

    def __init__(self, host: str = 'localhost', port: int = 2379):
        """Initialize event bus

        Args:
            host: Event bus host (unused in Phase 0)
            port: Event bus port (unused in Phase 0)
        """
        self.host = host
        self.port = port
        self.connected = False

        # In-memory storage (Phase 0)
        self._store: Dict[str, EventBusMessage] = {}
        self._store_lock = threading.RLock()

        # Pub/sub subscriptions
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._subscription_lock = threading.RLock()

        # Version counter for CAS
        self._version_counter = 0

    async def connect(self) -> bool:
        """Establish connection to event bus

        Returns:
            True if connection successful

        Example:
            >>> bus = EventBus()
            >>> success = await bus.connect()
            >>> assert success == True
        """
        # Phase 0: Immediate success (in-memory)
        # Phase 1: Actual etcd/NATS connection
        self.connected = True
        return True

    async def disconnect(self) -> bool:
        """Close connection to event bus

        Returns:
            True if disconnection successful
        """
        self.connected = False
        return True

    async def put(self, key: str, value: Any) -> bool:
        """Store value at key

        Args:
            key: Storage key (e.g., '/tasks/task-123')
            value: Value to store (any JSON-serializable type)

        Returns:
            True if successful

        Example:
            >>> await bus.put('/tasks/task-123', {'status': 'claimed', 'swarm': 'session-7'})
            True
        """
        if not self.connected:
            raise ConnectionError("Event bus not connected")

        with self._store_lock:
            self._version_counter += 1
            self._store[key] = EventBusMessage(
                key=key,
                value=value,
                timestamp=time.time(),
                version=self._version_counter
            )

        # Notify subscribers
        await self._notify_subscribers(key, value)

        return True

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value at key

        Args:
            key: Storage key

        Returns:
            Value if key exists, None otherwise

        Example:
            >>> value = await bus.get('/tasks/task-123')
            >>> print(value['status'])
            'claimed'
        """
        if not self.connected:
            raise ConnectionError("Event bus not connected")

        with self._store_lock:
            message = self._store.get(key)
            return message.value if message else None

    async def compare_and_swap(
        self,
        key: str,
        expected_value: Any,
        new_value: Any
    ) -> bool:
        """Atomically update value if it matches expected value

        This is the core primitive for task claiming without race conditions.

        Args:
            key: Storage key
            expected_value: Expected current value
            new_value: New value to set if expectation matches

        Returns:
            True if swap succeeded, False if value didn't match

        Example:
            >>> # Try to claim a task
            >>> success = await bus.compare_and_swap(
            ...     '/tasks/task-123',
            ...     {'status': 'available'},
            ...     {'status': 'claimed', 'swarm': 'session-7'}
            ... )
            >>> assert success == True  # First claim succeeds
            >>>
            >>> # Another swarm tries to claim same task
            >>> success2 = await bus.compare_and_swap(
            ...     '/tasks/task-123',
            ...     {'status': 'available'},
            ...     {'status': 'claimed', 'swarm': 'session-5'}
            ... )
            >>> assert success2 == False  # Fails - already claimed
        """
        if not self.connected:
            raise ConnectionError("Event bus not connected")

        with self._store_lock:
            message = self._store.get(key)

            # Key doesn't exist - treat as null expectation
            if message is None:
                if expected_value is None:
                    # Create new key
                    self._version_counter += 1
                    self._store[key] = EventBusMessage(
                        key=key,
                        value=new_value,
                        timestamp=time.time(),
                        version=self._version_counter
                    )
                    await self._notify_subscribers(key, new_value)
                    return True
                else:
                    # Expected non-null but key doesn't exist
                    return False

            # Compare current value with expected
            if message.value == expected_value:
                # Values match - perform swap
                self._version_counter += 1
                self._store[key] = EventBusMessage(
                    key=key,
                    value=new_value,
                    timestamp=time.time(),
                    version=self._version_counter
                )
                await self._notify_subscribers(key, new_value)
                return True
            else:
                # Values don't match - swap failed
                return False

    async def subscribe(
        self,
        key_prefix: str,
        callback: Callable[[str, Any], None]
    ) -> str:
        """Subscribe to events matching key prefix

        Args:
            key_prefix: Key prefix to watch (e.g., '/tasks/')
            callback: Async function to call on updates

        Returns:
            Subscription ID

        Example:
            >>> async def on_task_update(key, value):
            ...     print(f"Task {key} updated: {value}")
            >>>
            >>> sub_id = await bus.subscribe('/tasks/', on_task_update)
        """
        if not self.connected:
            raise ConnectionError("Event bus not connected")

        subscription_id = f"sub-{key_prefix}-{time.time()}"

        with self._subscription_lock:
            if key_prefix not in self._subscriptions:
                self._subscriptions[key_prefix] = []
            self._subscriptions[key_prefix].append(callback)

        return subscription_id

    async def _notify_subscribers(self, key: str, value: Any):
        """Notify subscribers of key update

        Args:
            key: Updated key
            value: New value
        """
        with self._subscription_lock:
            for prefix, callbacks in self._subscriptions.items():
                if key.startswith(prefix):
                    for callback in callbacks:
                        try:
                            # Call async callback
                            if asyncio.iscoroutinefunction(callback):
                                await callback(key, value)
                            else:
                                callback(key, value)
                        except Exception as e:
                            # Log error but don't fail the notify
                            print(f"[EventBus] Subscriber callback error: {e}")

    def health_check(self) -> Dict[str, Any]:
        """Check event bus health

        Returns:
            Dictionary with health status

        Example:
            >>> health = bus.health_check()
            >>> assert health['connected'] == True
        """
        with self._store_lock:
            num_keys = len(self._store)

        with self._subscription_lock:
            num_subscriptions = sum(len(callbacks) for callbacks in self._subscriptions.values())

        return {
            'connected': self.connected,
            'implementation': 'in-memory (Phase 0)',
            'host': self.host,
            'port': self.port,
            'num_keys': num_keys,
            'num_subscriptions': num_subscriptions,
            'production_ready': False,  # Phase 0 stub
        }


# Singleton instance for easy import
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get global event bus instance

    Returns:
        Global EventBus instance

    Example:
        >>> from infrafabric.event_bus import get_event_bus
        >>> bus = get_event_bus()
        >>> await bus.connect()
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus
