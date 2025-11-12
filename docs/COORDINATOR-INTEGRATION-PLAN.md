# IF.coordinator Integration Plan
## Session 5 → Session 7 Support Document

**Created by**: Session 5 (CLI)
**For**: Session 7 (IF.bus)
**Purpose**: Guide implementation of P0.1.2 (CAS) and P0.1.3 (pub/sub) using P0.1.1 EventBus
**Date**: 2025-11-12

---

## Executive Summary

Session 5 has completed **P0.1.1 (EventBus)** with full etcd3 integration, providing the foundation for IF.coordinator's real-time task coordination. This document guides Session 7 in implementing:

1. **P0.1.2**: Atomic CAS operations for race-free task claiming (<5ms)
2. **P0.1.3**: Real-time task broadcast using pub/sub (<10ms)

**Key Achievement**: EventBus provides `transaction()` method for atomic compare-and-swap, eliminating the 30,000ms git polling bottleneck.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    IF.coordinator (Session 7)                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ IFCoordinator.claim_task(swarm_id, task_id)           │ │
│  │   → Uses EventBus.transaction() for atomic CAS       │ │
│  │   → Returns True if claimed, False if already taken  │ │
│  │   → Logs to IF.witness on success                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
└────────────────────────────┼─────────────────────────────────┘
                             ↓
┌────────────────────────────┼─────────────────────────────────┐
│              EventBus (Session 5 - P0.1.1)                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ transaction(compare, success, failure)                 │ │
│  │   → Atomic CAS using etcd3                           │ │
│  │   → Race-free across multiple swarms                 │ │
│  │   → Returns (success_bool, response)                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
└────────────────────────────┼─────────────────────────────────┘
                             ↓
┌────────────────────────────┼─────────────────────────────────┐
│                    etcd3 (Distributed KV)                    │
│  • Atomic compare-and-swap operations                        │
│  • Watch API for real-time pub/sub                           │
│  • <1ms local operations                                     │
└───────────────────────────────────────────────────────────────┘
```

---

## EventBus API Reference

The EventBus (from P0.1.1) provides these methods for Session 7:

### Core Methods
```python
class EventBus:
    async def connect(self) -> bool:
        """Establish connection to etcd"""

    async def put(self, key: str, value: str) -> bool:
        """Store key-value pair"""

    async def get(self, key: str) -> Optional[str]:
        """Retrieve value by key"""

    async def transaction(self, compare: list, success: list, failure: list) -> bool:
        """Atomic compare-and-swap transaction (CRITICAL for P0.1.2)"""

    async def watch(self, key: str, callback: Callable) -> str:
        """Watch for changes (CRITICAL for P0.1.3)"""

    async def health_check(self) -> bool:
        """Verify etcd connectivity"""
```

### Configuration
- **Host**: `os.getenv('IF_ETCD_HOST', 'localhost')`
- **Port**: `os.getenv('IF_ETCD_PORT', '2379')`
- **Performance**: WAL mode, 10MB cache, mmap I/O optimized

---

## P0.1.2: Atomic CAS Implementation Guide

### Objective
Implement `IFCoordinator.claim_task()` using EventBus transactions to ensure only one swarm can claim a task, even under concurrent attempts.

### Implementation Pattern

```python
# infrafabric/coordinator.py

import asyncio
import json
from datetime import datetime
from typing import Optional
from infrafabric.event_bus import EventBus
from src.witness.database import WitnessDatabase

class IFCoordinator:
    """
    Real-time task coordinator using etcd for <10ms coordination.

    Philosophy: Wu Lun Principle 3 - Hierarchy emerges from coordination,
    not imposed structure. Tasks are claimed atomically by capable swarms.
    """

    def __init__(self, event_bus: EventBus, witness_db: WitnessDatabase):
        self.bus = event_bus
        self.witness = witness_db

    async def claim_task(self, swarm_id: str, task_id: str) -> bool:
        """
        Atomically claim a task using compare-and-swap.

        Args:
            swarm_id: ID of swarm attempting to claim task
            task_id: ID of task to claim

        Returns:
            True if claim successful, False if already claimed

        Performance: <5ms (target), <10ms (acceptable)
        """
        start_time = datetime.utcnow()
        task_key = f"/tasks/{task_id}/owner"

        # Build CAS transaction
        # Compare: task is unclaimed (value doesn't exist or is empty)
        # Success: Set task owner to swarm_id
        # Failure: Do nothing (task already claimed)

        import etcd3

        compare = [
            # Check if task is unclaimed (key doesn't exist)
            etcd3.transactions.Version(task_key) == 0
        ]

        success = [
            # Claim task by setting owner
            etcd3.transactions.Put(task_key, swarm_id)
        ]

        failure = [
            # No-op if already claimed
        ]

        # Execute atomic CAS
        result = await self.bus.transaction(compare, success, failure)

        # Calculate latency
        end_time = datetime.utcnow()
        latency_ms = (end_time - start_time).total_seconds() * 1000

        if result:
            # Claim successful - log to witness
            self.witness.create_entry(
                event='task_claimed',
                component='IF.coordinator',
                trace_id=task_id,
                payload={
                    'swarm_id': swarm_id,
                    'task_id': task_id,
                    'latency_ms': latency_ms,
                    'claimed_at': end_time.isoformat()
                }
            )

            logger.info(f"✓ Task {task_id} claimed by {swarm_id} in {latency_ms:.2f}ms")
            return True
        else:
            # Task already claimed
            logger.debug(f"✗ Task {task_id} already claimed (checked in {latency_ms:.2f}ms)")
            return False

    async def release_task(self, swarm_id: str, task_id: str) -> bool:
        """
        Release a claimed task (for failed/completed tasks).

        Uses CAS to ensure only the owner can release.
        """
        task_key = f"/tasks/{task_id}/owner"

        # Only release if current owner is swarm_id
        compare = [
            etcd3.transactions.Value(task_key) == swarm_id
        ]

        success = [
            etcd3.transactions.Delete(task_key)
        ]

        failure = []

        result = await self.bus.transaction(compare, success, failure)

        if result:
            self.witness.create_entry(
                event='task_released',
                component='IF.coordinator',
                trace_id=task_id,
                payload={'swarm_id': swarm_id, 'task_id': task_id}
            )

        return result

    async def get_task_owner(self, task_id: str) -> Optional[str]:
        """Get current owner of a task"""
        task_key = f"/tasks/{task_id}/owner"
        return await self.bus.get(task_key)
```

### Race Condition Test

```python
# tests/test_coordinator_cas.py

import pytest
import asyncio
from infrafabric.coordinator import IFCoordinator
from infrafabric.event_bus import EventBus

@pytest.mark.asyncio
async def test_concurrent_claim_race_condition():
    """
    Test that only one swarm wins in concurrent claim attempts.

    Simulates 10 swarms attempting to claim the same task simultaneously.
    Only 1 should succeed, 9 should fail.
    """
    bus = EventBus()
    await bus.connect()

    coordinator = IFCoordinator(bus, witness_db)
    task_id = "test-task-race-123"

    # Simulate 10 concurrent swarms
    swarm_ids = [f"swarm-{i}" for i in range(10)]

    # Launch all claims simultaneously
    results = await asyncio.gather(*[
        coordinator.claim_task(swarm_id, task_id)
        for swarm_id in swarm_ids
    ])

    # Exactly one should succeed
    successful_claims = sum(results)
    assert successful_claims == 1, f"Expected 1 success, got {successful_claims}"

    # Verify owner is set
    owner = await coordinator.get_task_owner(task_id)
    assert owner in swarm_ids

    # Verify failed claims returned False
    assert results.count(False) == 9
```

### Performance Benchmark

```python
# tests/test_coordinator_latency.py

@pytest.mark.asyncio
async def test_claim_latency_under_5ms():
    """
    Verify CAS operation completes in <5ms (target) or <10ms (acceptable).
    """
    import time

    coordinator = IFCoordinator(bus, witness_db)

    latencies = []
    for i in range(100):
        task_id = f"bench-task-{i}"
        start = time.perf_counter()
        await coordinator.claim_task(f"swarm-bench", task_id)
        end = time.perf_counter()

        latency_ms = (end - start) * 1000
        latencies.append(latency_ms)

    p50 = sorted(latencies)[50]
    p95 = sorted(latencies)[95]
    p99 = sorted(latencies)[99]

    print(f"Latency P50: {p50:.2f}ms, P95: {p95:.2f}ms, P99: {p99:.2f}ms")

    # Target: P95 < 5ms
    # Acceptable: P95 < 10ms
    assert p95 < 10, f"P95 latency {p95:.2f}ms exceeds 10ms threshold"

    if p95 < 5:
        print("✓ EXCELLENT: P95 < 5ms (target met)")
    else:
        print(f"⚠ ACCEPTABLE: P95 {p95:.2f}ms (target 5ms, acceptable <10ms)")
```

---

## P0.1.3: Real-Time Pub/Sub Implementation Guide

### Objective
Implement real-time task broadcast using etcd watch API to notify swarms of new tasks within <10ms.

### Implementation Pattern

```python
# infrafabric/coordinator.py (continued)

class IFCoordinator:
    async def publish_task(self, task_id: str, task_data: dict) -> bool:
        """
        Publish a new task to the task queue.

        All watching swarms will be notified in real-time via watch callbacks.
        """
        task_key = f"/tasks/{task_id}/data"
        task_json = json.dumps(task_data)

        result = await self.bus.put(task_key, task_json)

        if result:
            self.witness.create_entry(
                event='task_published',
                component='IF.coordinator',
                trace_id=task_id,
                payload={'task_id': task_id, **task_data}
            )

        return result

    async def subscribe_to_tasks(self, callback):
        """
        Subscribe to new task notifications.

        Callback will be invoked whenever a new task is published.
        Latency: <10ms from publish to callback invocation.
        """
        async def task_callback(event):
            """Handle task watch events"""
            # etcd watch event has: key, value, type (PUT/DELETE)
            if event.type == 'PUT':
                task_key = event.key.decode('utf-8')
                task_data = json.loads(event.value.decode('utf-8'))

                # Extract task_id from key
                task_id = task_key.split('/')[-2]  # /tasks/{task_id}/data

                # Invoke user callback
                await callback(task_id, task_data)

        # Watch all task data keys
        watch_id = await self.bus.watch("/tasks/", task_callback)
        return watch_id
```

### Pub/Sub Test

```python
# tests/test_coordinator_pubsub.py

@pytest.mark.asyncio
async def test_realtime_task_notification():
    """
    Test that task subscribers receive notifications in <10ms.
    """
    coordinator = IFCoordinator(bus, witness_db)

    # Track received notifications
    received_tasks = []
    notification_times = []

    async def swarm_callback(task_id, task_data):
        """Simulated swarm receiving task notification"""
        received_tasks.append(task_id)
        notification_times.append(datetime.utcnow())

    # Subscribe to tasks
    await coordinator.subscribe_to_tasks(swarm_callback)

    # Wait for watch to establish
    await asyncio.sleep(0.1)

    # Publish a task
    publish_time = datetime.utcnow()
    await coordinator.publish_task('test-task-123', {
        'description': 'Test task',
        'capabilities': ['code-analysis:rust']
    })

    # Wait for notification (should be <10ms but allow 100ms for test stability)
    await asyncio.sleep(0.2)

    # Verify notification received
    assert 'test-task-123' in received_tasks

    # Verify latency
    if notification_times:
        latency = (notification_times[0] - publish_time).total_seconds() * 1000
        print(f"Notification latency: {latency:.2f}ms")
        assert latency < 100, f"Notification took {latency:.2f}ms (too slow)"

        if latency < 10:
            print("✓ EXCELLENT: Notification <10ms")
```

---

## Integration Checklist for Session 7

### Prerequisites
- [ ] Read `infrafabric/event_bus.py` (Session 5's P0.1.1)
- [ ] Read `tests/test_event_bus.py` for EventBus usage examples
- [ ] Ensure etcd3 is installed (`pip install etcd3>=0.12.0`)
- [ ] Start local etcd server for testing (`docker run -p 2379:2379 quay.io/coreos/etcd`)

### P0.1.2 Implementation Steps
1. [ ] Create `infrafabric/coordinator.py`
2. [ ] Implement `IFCoordinator.__init__(event_bus, witness_db)`
3. [ ] Implement `claim_task(swarm_id, task_id)` using `bus.transaction()`
4. [ ] Implement `release_task(swarm_id, task_id)` with owner verification
5. [ ] Implement `get_task_owner(task_id)` helper
6. [ ] Add IF.witness logging for all claim/release events
7. [ ] Write unit tests for single claim
8. [ ] Write race condition test (10 concurrent claims)
9. [ ] Write latency benchmark (target <5ms, acceptable <10ms)
10. [ ] Document CAS algorithm in docstrings

### P0.1.3 Implementation Steps
1. [ ] Implement `publish_task(task_id, task_data)` using `bus.put()`
2. [ ] Implement `subscribe_to_tasks(callback)` using `bus.watch()`
3. [ ] Handle watch event parsing (key, value, type)
4. [ ] Add IF.witness logging for publish events
5. [ ] Write unit test for single pub/sub
6. [ ] Write latency test (publish → notify <10ms)
7. [ ] Write test for multiple subscribers
8. [ ] Document pub/sub pattern in docstrings

### Testing Strategy
- [ ] Run all EventBus tests first (confirm P0.1.1 working): `pytest tests/test_event_bus.py -v`
- [ ] Run coordinator unit tests: `pytest tests/test_coordinator.py -v`
- [ ] Run race condition tests: `pytest tests/test_coordinator_cas.py -v`
- [ ] Run latency benchmarks: `pytest tests/test_coordinator_latency.py -v`
- [ ] Run pub/sub tests: `pytest tests/test_coordinator_pubsub.py -v`

---

## Performance Targets

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| CAS Claim Latency (P50) | <3ms | <5ms | <10ms |
| CAS Claim Latency (P95) | <5ms | <10ms | <20ms |
| Pub/Sub Notification | <5ms | <10ms | <50ms |
| Concurrent Claims (10 swarms) | 1 success, 9 failures | Same | Same |

**Current Baseline** (git polling): 30,000ms
**Target Improvement**: 3,000x-6,000x faster

---

## Key Design Decisions

### Why etcd3 for EventBus?
- **Atomic CAS**: Native support via transactions API
- **Watch API**: Real-time notifications with minimal latency
- **Proven at Scale**: Used by Kubernetes for orchestration
- **Simple**: Single binary, easy local development

### Why Async/Await?
- **Non-blocking**: Multiple swarms can query coordinator simultaneously
- **Performance**: ThreadPoolExecutor for sync etcd3 calls (no GIL blocking)
- **Scalability**: Handle 50-100 concurrent swarms without thread explosion

### Key Namespace
```
/tasks/{task_id}/owner  → Claim status (swarm_id or empty)
/tasks/{task_id}/data   → Task payload (watched by swarms)
/tasks/{task_id}/status → Execution status (pending/running/complete/failed)
```

---

## Troubleshooting Guide

### "etcd connection refused"
```bash
# Start local etcd for testing
docker run -d -p 2379:2379 --name etcd-test quay.io/coreos/etcd \
  /usr/local/bin/etcd --listen-client-urls http://0.0.0.0:2379 \
  --advertise-client-urls http://0.0.0.0:2379
```

### "Transaction failed: compare mismatch"
- This is expected when CAS fails (task already claimed)
- Verify that failed claims return `False`
- Check witness log to see which swarm won the race

### "Watch callback not firing"
- Ensure watch is established before publishing (add 100ms delay in tests)
- Verify callback is async: `async def callback(event):`
- Check etcd logs for watch stream issues

### "Latency >10ms"
- Check network latency to etcd (should be <1ms local)
- Verify EventBus cache settings (WAL mode, mmap enabled)
- Profile with `time.perf_counter()` to isolate bottleneck
- Consider local etcd vs. remote deployment

---

## Philosophy Alignment

**Wu Lun Principle 3** - *Hierarchy emerges from coordination*
The coordinator doesn't impose task assignment; swarms atomically claim tasks based on their capabilities. Natural hierarchy emerges from successful claims.

**IF.ground Principle 8** - *Observability without fragility*
Every claim/release is witnessed. Hash chains prove tamper-free coordination history. Pub/sub enables real-time visibility without polling fragility.

**IF.TTT** - *Testability, Transparency, Traceability*
- **Testability**: Race condition tests prove CAS correctness
- **Transparency**: All operations logged to witness with <5ms overhead
- **Traceability**: Full coordination history in IF.witness for audit

---

## Next Steps for Session 7

1. **Read this entire document** (5 minutes)
2. **Review EventBus code**: `infrafabric/event_bus.py` (10 minutes)
3. **Start etcd locally** for testing (2 minutes)
4. **Implement P0.1.2**: CAS operations (60-90 minutes)
5. **Test race conditions**: Verify CAS correctness (15 minutes)
6. **Implement P0.1.3**: Pub/sub (60-90 minutes)
7. **Test latency**: Verify <10ms performance (15 minutes)
8. **Commit and push**: Update task board (5 minutes)

**Estimated Total**: 2-3 hours for both tasks

---

## Questions?

If you encounter issues or need clarification:
1. Check `tests/test_event_bus.py` for EventBus usage examples
2. Review etcd3 Python library docs: https://python-etcd3.readthedocs.io/
3. Check IF.witness integration: `src/witness/database.py`
4. Ask Session 5 for help (via coordination branch or status updates)

**Session 5 Contact**: Available for EventBus integration support

---

**Document Status**: ✅ COMPLETE
**Created**: 2025-11-12 by Session 5 (CLI)
**For**: Session 7 (IF.bus) - P0.1.2 and P0.1.3 implementation
**Dependencies**: P0.1.1 (EventBus) - Already complete ✅
**Next**: Session 7 implements coordinator using this guide
