"""Tests for IF.coordinator - P0.1.3 Real-Time Task Broadcast

Tests cover:
- Swarm registration and subscriptions
- Real-time task notifications
- Direct task pushing (<10ms target)
- Blocker detection and escalation (<10ms target)
- Multiple swarm coordination
- Performance benchmarks

Part of Phase 0: P0.1.3 - Real-Time Task Broadcast
"""

import pytest
import asyncio
import time
from infrafabric.coordinator import IFCoordinator
from infrafabric.event_bus import EventBus
from infrafabric.schemas.capability import Capability
from infrafabric import witness


@pytest.fixture
async def coordinator():
    """Create connected coordinator with fresh event bus"""
    # Create fresh event bus for each test
    event_bus = EventBus()
    coord = IFCoordinator(event_bus=event_bus)
    await coord.connect()
    yield coord
    await coord.disconnect()


@pytest.fixture
def clear_witness():
    """Clear witness logs before each test"""
    witness.clear_operations()
    yield
    # No teardown needed


# ========== Swarm Registration Tests ==========

@pytest.mark.asyncio
async def test_register_swarm_creates_subscription(coordinator):
    """Test swarm registration creates subscription"""
    success = await coordinator.register_swarm(
        'session-7',
        [Capability.CODE_ANALYSIS_PYTHON]
    )

    assert success == True
    assert 'session-7' in coordinator.swarm_registry

    registration = coordinator.swarm_registry['session-7']
    assert registration.swarm_id == 'session-7'
    assert Capability.CODE_ANALYSIS_PYTHON in registration.capabilities
    assert registration.subscription_id is not None


@pytest.mark.asyncio
async def test_register_multiple_swarms(coordinator):
    """Test registering multiple swarms independently"""
    # Register swarm 1
    success1 = await coordinator.register_swarm(
        'session-7',
        [Capability.CODE_ANALYSIS_PYTHON, Capability.TESTING_UNIT]
    )

    # Register swarm 2
    success2 = await coordinator.register_swarm(
        'session-5',
        [Capability.INFRA_KUBERNETES]
    )

    assert success1 == True
    assert success2 == True
    assert len(coordinator.swarm_registry) == 2

    # Verify independent registrations
    assert 'session-7' in coordinator.swarm_registry
    assert 'session-5' in coordinator.swarm_registry

    reg1 = coordinator.swarm_registry['session-7']
    reg2 = coordinator.swarm_registry['session-5']

    assert len(reg1.capabilities) == 2
    assert len(reg2.capabilities) == 1
    assert reg1.subscription_id != reg2.subscription_id


@pytest.mark.asyncio
async def test_register_swarm_logged_to_witness(coordinator, clear_witness):
    """Test swarm registration logged to IF.witness"""
    await coordinator.register_swarm(
        'session-7',
        [Capability.CODE_ANALYSIS_PYTHON]
    )

    # Verify witness logging
    ops = witness.get_operations(component='IF.coordinator', operation='swarm_registered')
    assert len(ops) == 1
    assert ops[0].params['swarm_id'] == 'session-7'
    assert 'code-analysis:python' in ops[0].params['capabilities']
    assert ops[0].params['subscription_id'] is not None


# ========== Task Notification Tests ==========

@pytest.mark.asyncio
async def test_registered_swarm_receives_task_notifications(coordinator, clear_witness):
    """Test registered swarm receives task update notifications"""
    # Register swarm
    await coordinator.register_swarm(
        'session-7',
        [Capability.CODE_ANALYSIS_PYTHON]
    )

    # Create task (should trigger notification)
    await coordinator.create_task(
        'task-123',
        [Capability.CODE_ANALYSIS_PYTHON]
    )

    # Allow async notification to process
    await asyncio.sleep(0.01)

    # Verify notification was sent
    ops = witness.get_operations(component='IF.coordinator', operation='task_notification_sent')
    assert len(ops) >= 1

    # Find notification for session-7
    session7_notifications = [op for op in ops if op.params['swarm_id'] == 'session-7']
    assert len(session7_notifications) >= 1
    assert session7_notifications[0].params['task_id'] == 'task-123'
    assert session7_notifications[0].params['status'] == 'available'


@pytest.mark.asyncio
async def test_multiple_swarms_receive_independent_notifications(coordinator, clear_witness):
    """Test multiple swarms receive notifications independently"""
    # Register three swarms
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.register_swarm('session-5', [Capability.TESTING_UNIT])
    await coordinator.register_swarm('session-3', [Capability.CODE_ANALYSIS_PYTHON])

    # Create task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])

    # Allow notifications to process
    await asyncio.sleep(0.01)

    # Verify all swarms received notifications
    ops = witness.get_operations(component='IF.coordinator', operation='task_notification_sent')

    # All 3 swarms should receive notifications (subscribed to /tasks/)
    swarm_ids = {op.params['swarm_id'] for op in ops}
    assert 'session-7' in swarm_ids
    assert 'session-5' in swarm_ids
    assert 'session-3' in swarm_ids


@pytest.mark.asyncio
async def test_task_claim_triggers_notification(coordinator, clear_witness):
    """Test task claiming triggers notification to subscribers"""
    # Register swarm
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])

    # Create task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])

    # Clear previous notifications
    witness.clear_operations()

    # Claim task (should trigger notification)
    await coordinator.claim_task('session-7', 'task-123')

    # Allow notification to process
    await asyncio.sleep(0.01)

    # Verify notification for claim
    ops = witness.get_operations(component='IF.coordinator', operation='task_notification_sent')
    assert len(ops) >= 1

    # Find notification with status 'claimed'
    claimed_notifications = [op for op in ops if op.params.get('status') == 'claimed']
    assert len(claimed_notifications) >= 1


# ========== Direct Push Notification Tests ==========

@pytest.mark.asyncio
async def test_push_task_to_registered_swarm(coordinator):
    """Test pushing task notification directly to swarm"""
    # Register swarm
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])

    # Create task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])

    # Push task to swarm
    success = await coordinator.push_task_to_swarm('session-7', 'task-123')

    assert success == True

    # Verify notification was created
    notification_key = '/notifications/session-7/task-123'
    notification = await coordinator.event_bus.get(notification_key)

    assert notification is not None
    assert notification['task_id'] == 'task-123'
    assert notification['task_data'] is not None
    assert 'timestamp' in notification


@pytest.mark.asyncio
async def test_push_to_unregistered_swarm_fails(coordinator):
    """Test pushing to unregistered swarm fails"""
    # Create task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])

    # Try to push to unregistered swarm
    success = await coordinator.push_task_to_swarm('session-999', 'task-123')

    assert success == False


@pytest.mark.asyncio
async def test_push_nonexistent_task_fails(coordinator):
    """Test pushing nonexistent task fails"""
    # Register swarm
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])

    # Try to push nonexistent task
    success = await coordinator.push_task_to_swarm('session-7', 'task-999')

    assert success == False


@pytest.mark.asyncio
async def test_push_latency_under_10ms(coordinator):
    """Test push latency meets <10ms target (P0.1.3 requirement)"""
    # Register swarm
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])

    # Create task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])

    # Benchmark push
    start = time.perf_counter()
    success = await coordinator.push_task_to_swarm('session-7', 'task-123')
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert success == True
    assert elapsed_ms < 10.0, f"Push latency {elapsed_ms:.2f}ms exceeds 10ms target"

    print(f"\n✅ Push latency: {elapsed_ms:.3f}ms (target: <10ms)")


@pytest.mark.asyncio
async def test_push_logged_to_witness(coordinator, clear_witness):
    """Test task push logged to IF.witness"""
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])

    await coordinator.push_task_to_swarm('session-7', 'task-123')

    # Verify witness logging
    ops = witness.get_operations(component='IF.coordinator', operation='task_pushed')
    assert len(ops) == 1
    assert ops[0].params['swarm_id'] == 'session-7'
    assert ops[0].params['task_id'] == 'task-123'
    assert 'latency_ms' in ops[0].params


@pytest.mark.asyncio
async def test_multiple_pushes_tracked(coordinator):
    """Test multiple pushes tracked in performance stats"""
    # Register swarms
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.register_swarm('session-5', [Capability.CODE_ANALYSIS_PYTHON])

    # Create tasks
    await coordinator.create_task('task-1', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.create_task('task-2', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.create_task('task-3', [Capability.CODE_ANALYSIS_PYTHON])

    # Push to different swarms
    await coordinator.push_task_to_swarm('session-7', 'task-1')
    await coordinator.push_task_to_swarm('session-5', 'task-2')
    await coordinator.push_task_to_swarm('session-7', 'task-3')

    # Verify stats
    stats = coordinator.get_performance_stats()
    assert stats['total_pushes'] == 3
    assert stats['avg_push_latency_ms'] > 0
    assert stats['max_push_latency_ms'] > 0
    assert stats['push_latency_target_met'] == True  # All under 10ms


# ========== Blocker Detection and Escalation Tests ==========

@pytest.mark.asyncio
async def test_detect_blocker_escalates_to_orchestrator(coordinator):
    """Test blocker detection escalates to orchestrator"""
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])

    blocker_info = {
        'type': 'circuit_breaker_tripped',
        'reason': 'budget_exhausted',
        'task_id': 'task-123'
    }

    success = await coordinator.detect_blocker('session-7', blocker_info)

    assert success == True

    # Verify blocker was stored (would be read by orchestrator)
    # Format: /blockers/{swarm_id}/{timestamp}
    # We can't predict exact timestamp, but we can check event bus has blocker keys
    health = coordinator.event_bus.health_check()
    assert health['num_keys'] >= 1  # At least one blocker key exists


@pytest.mark.asyncio
async def test_blocker_escalation_latency_under_10ms(coordinator):
    """Test blocker escalation meets <10ms target (P0.1.3 requirement)"""
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])

    blocker_info = {
        'type': 'circuit_breaker_tripped',
        'reason': 'budget_exhausted'
    }

    # Benchmark escalation
    start = time.perf_counter()
    success = await coordinator.detect_blocker('session-7', blocker_info)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert success == True
    assert elapsed_ms < 10.0, f"Escalation latency {elapsed_ms:.2f}ms exceeds 10ms target"

    print(f"\n✅ Blocker escalation latency: {elapsed_ms:.3f}ms (target: <10ms)")


@pytest.mark.asyncio
async def test_blocker_logged_to_witness(coordinator, clear_witness):
    """Test blocker escalation logged to IF.witness"""
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])

    blocker_info = {
        'type': 'circuit_breaker_tripped',
        'reason': 'budget_exhausted',
        'task_id': 'task-123'
    }

    await coordinator.detect_blocker('session-7', blocker_info)

    # Verify witness logging
    ops = witness.get_operations(component='IF.coordinator', operation='blocker_escalated')
    assert len(ops) == 1
    assert ops[0].params['swarm_id'] == 'session-7'
    assert ops[0].params['blocker_type'] == 'circuit_breaker_tripped'
    assert 'latency_ms' in ops[0].params
    assert ops[0].severity == 'HIGH'


@pytest.mark.asyncio
async def test_multiple_blockers_from_same_swarm(coordinator, clear_witness):
    """Test multiple blockers can be escalated from same swarm"""
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])

    # Escalate first blocker
    await coordinator.detect_blocker('session-7', {
        'type': 'circuit_breaker_tripped',
        'reason': 'budget_exhausted'
    })

    # Escalate second blocker
    await coordinator.detect_blocker('session-7', {
        'type': 'dependency_failure',
        'reason': 'external_service_down'
    })

    # Verify both logged
    ops = witness.get_operations(component='IF.coordinator', operation='blocker_escalated')
    assert len(ops) == 2
    assert ops[0].params['blocker_type'] == 'circuit_breaker_tripped'
    assert ops[1].params['blocker_type'] == 'dependency_failure'


# ========== Performance Statistics Tests ==========

@pytest.mark.asyncio
async def test_performance_stats_include_push_metrics(coordinator):
    """Test performance stats include push latency metrics"""
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])

    # Perform push
    await coordinator.push_task_to_swarm('session-7', 'task-123')

    # Get stats
    stats = coordinator.get_performance_stats()

    assert 'total_pushes' in stats
    assert 'avg_push_latency_ms' in stats
    assert 'max_push_latency_ms' in stats
    assert 'push_latency_target_met' in stats

    assert stats['total_pushes'] == 1
    assert stats['avg_push_latency_ms'] < 10.0
    assert stats['push_latency_target_met'] == True


@pytest.mark.asyncio
async def test_performance_stats_include_swarm_count(coordinator):
    """Test performance stats include registered swarm count"""
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.register_swarm('session-5', [Capability.TESTING_UNIT])

    stats = coordinator.get_performance_stats()

    assert 'registered_swarms' in stats
    assert stats['registered_swarms'] == 2


# ========== Integration Tests ==========

@pytest.mark.asyncio
async def test_full_broadcast_workflow(coordinator, clear_witness):
    """Test full workflow: register → create → push → claim → complete"""
    # 1. Register swarm
    await coordinator.register_swarm(
        'session-7',
        [Capability.CODE_ANALYSIS_PYTHON]
    )

    # 2. Create task
    await coordinator.create_task(
        'task-123',
        [Capability.CODE_ANALYSIS_PYTHON],
        priority=10
    )

    # 3. Push task to swarm
    push_success = await coordinator.push_task_to_swarm('session-7', 'task-123')
    assert push_success == True

    # 4. Claim task
    claim_success = await coordinator.claim_task('session-7', 'task-123')
    assert claim_success == True

    # 5. Complete task
    complete_success = await coordinator.complete_task(
        'session-7',
        'task-123',
        result={'status': 'success'}
    )
    assert complete_success == True

    # Verify witness trail
    ops = witness.get_operations(component='IF.coordinator')
    operation_types = {op.operation for op in ops}

    assert 'swarm_registered' in operation_types
    assert 'task_created' in operation_types
    assert 'task_pushed' in operation_types
    assert 'task_claimed' in operation_types
    assert 'task_completed' in operation_types


@pytest.mark.asyncio
async def test_concurrent_pushes_to_multiple_swarms(coordinator):
    """Test concurrent pushes to multiple swarms"""
    # Register 5 swarms
    for i in range(5):
        await coordinator.register_swarm(
            f'session-{i}',
            [Capability.CODE_ANALYSIS_PYTHON]
        )

    # Create 5 tasks
    for i in range(5):
        await coordinator.create_task(
            f'task-{i}',
            [Capability.CODE_ANALYSIS_PYTHON]
        )

    # Push tasks concurrently
    push_tasks = [
        coordinator.push_task_to_swarm(f'session-{i}', f'task-{i}')
        for i in range(5)
    ]

    results = await asyncio.gather(*push_tasks)

    # All pushes should succeed
    assert all(results)
    assert sum(1 for r in results if r == True) == 5

    # Verify performance stats
    stats = coordinator.get_performance_stats()
    assert stats['total_pushes'] == 5
    assert stats['avg_push_latency_ms'] < 10.0  # P0.1.3 target


@pytest.mark.asyncio
async def test_health_check_includes_broadcast_metrics(coordinator):
    """Test health check includes broadcast-related metrics"""
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.push_task_to_swarm('session-7', 'task-123')

    health = coordinator.health_check()

    assert health['status'] == 'healthy'
    assert health['connected'] == True
    assert 'performance' in health
    assert 'swarms_registered' in health
    assert 'session-7' in health['swarms_registered']
    assert health['performance']['total_pushes'] == 1


@pytest.mark.asyncio
async def test_orchestrator_workflow_with_blocker(coordinator, clear_witness):
    """Test orchestrator workflow with blocker detection"""
    # 1. Register swarm
    await coordinator.register_swarm('session-7', [Capability.CODE_ANALYSIS_PYTHON])

    # 2. Create and push task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.push_task_to_swarm('session-7', 'task-123')

    # 3. Claim task
    await coordinator.claim_task('session-7', 'task-123')

    # 4. Swarm encounters blocker
    await coordinator.detect_blocker('session-7', {
        'type': 'circuit_breaker_tripped',
        'reason': 'budget_exhausted',
        'task_id': 'task-123'
    })

    # 5. Orchestrator could reassign task (simulated by failing and recreating)
    await coordinator.fail_task('session-7', 'task-123', 'blocker_detected')

    # Verify blocker was escalated
    blocker_ops = witness.get_operations(
        component='IF.coordinator',
        operation='blocker_escalated'
    )
    assert len(blocker_ops) == 1
    assert blocker_ops[0].severity == 'HIGH'

    # Verify task was failed
    fail_ops = witness.get_operations(
        component='IF.coordinator',
        operation='task_failed'
    )
    assert len(fail_ops) == 1
