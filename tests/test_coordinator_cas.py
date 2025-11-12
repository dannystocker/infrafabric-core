"""Unit tests for IF.coordinator atomic CAS operations (P0.1.2)

Tests atomic task claiming with compare-and-swap to prevent race conditions:
- Single swarm claiming
- Concurrent claim attempts (race prevention)
- Task lifecycle (create → claim → complete/fail)
- Performance (<5ms claim latency)
- IF.witness integration

Run with: python -m pytest tests/test_coordinator_cas.py -v
"""

import pytest
import asyncio
import time
from infrafabric.coordinator import IFCoordinator
from infrafabric.event_bus import EventBus
from infrafabric.schemas.capability import Capability
from infrafabric import witness


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state before each test"""
    witness.clear_operations()
    yield
    witness.clear_operations()


@pytest.fixture
async def coordinator():
    """Create connected coordinator with fresh event bus"""
    # Create fresh event bus for each test
    event_bus = EventBus()
    coord = IFCoordinator(event_bus=event_bus)
    await coord.connect()
    yield coord
    await coord.disconnect()


# ========== Basic Task Creation Tests ==========

@pytest.mark.asyncio
async def test_create_task(coordinator):
    """Test creating a new task"""
    success = await coordinator.create_task(
        'task-123',
        [Capability.CODE_ANALYSIS_PYTHON],
        priority=10
    )

    assert success == True

    # Verify task exists
    task = await coordinator.get_task_status('task-123')
    assert task is not None
    assert task['task_id'] == 'task-123'
    assert task['status'] == 'available'
    assert task['priority'] == 10


@pytest.mark.asyncio
async def test_create_duplicate_task_fails(coordinator):
    """Test that creating duplicate task fails"""
    # Create first task
    success1 = await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])
    assert success1 == True

    # Try to create same task again
    success2 = await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_RUST])
    assert success2 == False  # Should fail - task already exists


@pytest.mark.asyncio
async def test_get_nonexistent_task(coordinator):
    """Test getting non-existent task returns None"""
    task = await coordinator.get_task_status('nonexistent-task')
    assert task is None


# ========== Atomic CAS Claim Tests ==========

@pytest.mark.asyncio
async def test_claim_task_success(coordinator):
    """Test successful atomic task claim (P0.1.2)"""
    # Create task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])

    # Claim task
    success = await coordinator.claim_task('session-7', 'task-123')
    assert success == True

    # Verify task is claimed
    task = await coordinator.get_task_status('task-123')
    assert task['status'] == 'claimed'
    assert task['claimed_by'] == 'session-7'
    assert 'claimed_at' in task


@pytest.mark.asyncio
async def test_claim_nonexistent_task_fails(coordinator):
    """Test claiming non-existent task fails"""
    success = await coordinator.claim_task('session-7', 'nonexistent-task')
    assert success == False


@pytest.mark.asyncio
async def test_claim_already_claimed_task_fails(coordinator):
    """Test that claiming already-claimed task fails (race prevention)"""
    # Create and claim task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.claim_task('session-7', 'task-123')

    # Another swarm tries to claim
    success = await coordinator.claim_task('session-5', 'task-123')
    assert success == False  # Fails - already claimed

    # Verify still claimed by original swarm
    task = await coordinator.get_task_status('task-123')
    assert task['claimed_by'] == 'session-7'


@pytest.mark.asyncio
async def test_concurrent_claim_attempts(coordinator):
    """Test concurrent claim attempts - only one succeeds (critical test)

    This is the core race condition test for P0.1.2
    """
    # Create task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])

    # Simulate concurrent claims from 5 swarms
    claim_tasks = [
        coordinator.claim_task(f'session-{i}', 'task-123')
        for i in range(5)
    ]

    # Execute all claims concurrently
    results = await asyncio.gather(*claim_tasks)

    # Exactly ONE claim should succeed
    successful_claims = sum(1 for r in results if r == True)
    assert successful_claims == 1, f"Expected 1 successful claim, got {successful_claims}"

    # Verify task is claimed by one swarm
    task = await coordinator.get_task_status('task-123')
    assert task['status'] == 'claimed'
    assert task['claimed_by'] is not None


@pytest.mark.asyncio
async def test_claim_completed_task_fails(coordinator):
    """Test that claiming completed task fails"""
    # Create, claim, and complete task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.claim_task('session-7', 'task-123')
    await coordinator.complete_task('session-7', 'task-123')

    # Another swarm tries to claim
    success = await coordinator.claim_task('session-5', 'task-123')
    assert success == False


# ========== Task Completion Tests ==========

@pytest.mark.asyncio
async def test_complete_task_success(coordinator):
    """Test completing a claimed task"""
    # Create and claim task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.claim_task('session-7', 'task-123')

    # Complete task
    success = await coordinator.complete_task(
        'session-7',
        'task-123',
        result={'analysis': 'complete', 'issues': 0}
    )
    assert success == True

    # Verify task is completed
    task = await coordinator.get_task_status('task-123')
    assert task['status'] == 'completed'
    assert 'completed_at' in task
    assert task['result']['analysis'] == 'complete'


@pytest.mark.asyncio
async def test_complete_task_by_wrong_swarm_fails(coordinator):
    """Test that only claiming swarm can complete task"""
    # Create and claim task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.claim_task('session-7', 'task-123')

    # Different swarm tries to complete
    success = await coordinator.complete_task('session-5', 'task-123')
    assert success == False  # Fails - not the claiming swarm

    # Verify task still claimed (not completed)
    task = await coordinator.get_task_status('task-123')
    assert task['status'] == 'claimed'


@pytest.mark.asyncio
async def test_complete_unclaimed_task_fails(coordinator):
    """Test completing unclaimed task fails"""
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])

    success = await coordinator.complete_task('session-7', 'task-123')
    assert success == False


# ========== Task Failure Tests ==========

@pytest.mark.asyncio
async def test_fail_task_success(coordinator):
    """Test failing a claimed task"""
    # Create and claim task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.claim_task('session-7', 'task-123')

    # Fail task
    success = await coordinator.fail_task(
        'session-7',
        'task-123',
        reason='Dependency not available'
    )
    assert success == True

    # Verify task is failed
    task = await coordinator.get_task_status('task-123')
    assert task['status'] == 'failed'
    assert task['failure_reason'] == 'Dependency not available'


@pytest.mark.asyncio
async def test_fail_task_by_wrong_swarm_fails(coordinator):
    """Test that only claiming swarm can fail task"""
    # Create and claim task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.claim_task('session-7', 'task-123')

    # Different swarm tries to fail
    success = await coordinator.fail_task('session-5', 'task-123', 'error')
    assert success == False


# ========== Performance Tests (P0.1.2 Target: <5ms) ==========

@pytest.mark.asyncio
async def test_claim_latency_under_5ms(coordinator):
    """Test claim latency meets <5ms target (P0.1.2 requirement)"""
    # Create task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])

    # Warm-up claim
    coordinator2 = IFCoordinator()
    await coordinator2.connect()
    await coordinator2.create_task('warmup', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator2.claim_task('session-warmup', 'warmup')
    await coordinator2.disconnect()

    # Benchmark claim
    start = time.perf_counter()
    success = await coordinator.claim_task('session-7', 'task-123')
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert success == True
    assert elapsed_ms < 5.0, f"Claim latency {elapsed_ms:.2f}ms exceeds 5ms target"

    print(f"\n✅ Claim latency: {elapsed_ms:.3f}ms (target: <5ms)")


@pytest.mark.asyncio
async def test_claim_latency_average_100_operations(coordinator):
    """Test average claim latency over 100 operations"""
    # Create 100 tasks
    for i in range(100):
        await coordinator.create_task(f'task-{i}', [Capability.CODE_ANALYSIS_PYTHON])

    # Claim all tasks
    start = time.perf_counter()
    for i in range(100):
        await coordinator.claim_task(f'session-{i % 10}', f'task-{i}')
    elapsed_ms = (time.perf_counter() - start) * 1000

    avg_ms = elapsed_ms / 100

    assert avg_ms < 5.0, f"Average claim latency {avg_ms:.2f}ms exceeds 5ms target"

    print(f"\n✅ 100 claims: {elapsed_ms:.2f}ms total, {avg_ms:.3f}ms average")


@pytest.mark.asyncio
async def test_performance_stats(coordinator):
    """Test coordinator performance statistics"""
    # Create and claim tasks
    await coordinator.create_task('task-1', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.claim_task('session-7', 'task-1')

    await coordinator.create_task('task-2', [Capability.CODE_ANALYSIS_RUST])
    await coordinator.claim_task('session-7', 'task-2')

    # Get stats
    stats = coordinator.get_performance_stats()

    assert stats['total_claims'] == 2
    assert stats['avg_claim_latency_ms'] < 5.0  # P0.1.2 target
    assert stats['claim_latency_target_met'] == True
    assert 'max_claim_latency_ms' in stats


# ========== IF.witness Integration Tests ==========

@pytest.mark.asyncio
async def test_task_claim_logged_to_witness(coordinator):
    """Test successful claim logged to IF.witness"""
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.claim_task('session-7', 'task-123')

    # Verify witness logging
    ops = witness.get_operations(component='IF.coordinator', operation='task_claimed')
    assert len(ops) == 1
    assert ops[0].params['swarm_id'] == 'session-7'
    assert ops[0].params['task_id'] == 'task-123'


@pytest.mark.asyncio
async def test_failed_claim_logged_to_witness(coordinator):
    """Test failed claim logged to IF.witness"""
    await coordinator.claim_task('session-7', 'nonexistent-task')

    # Verify witness logging
    ops = witness.get_operations(component='IF.coordinator', operation='claim_failed')
    assert len(ops) == 1
    assert ops[0].params['reason'] == 'task_not_found'


@pytest.mark.asyncio
async def test_race_lost_logged_to_witness(coordinator):
    """Test race condition loss logged to IF.witness"""
    # Create and claim task
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.claim_task('session-7', 'task-123')

    # Another swarm tries to claim (loses race)
    await coordinator.claim_task('session-5', 'task-123')

    # Verify witness logging - logs as claim_failed (not available)
    # True race loss (CAS failure) is logged as 'claim_race_lost'
    # This scenario is claim_failed because task status != 'available'
    ops = witness.get_operations(component='IF.coordinator', operation='claim_failed')
    assert len(ops) >= 1
    # Find the session-5 claim failure
    session5_failures = [op for op in ops if op.params['swarm_id'] == 'session-5']
    assert len(session5_failures) == 1
    assert session5_failures[0].params['reason'] == 'task_not_available'


@pytest.mark.asyncio
async def test_task_completion_logged_to_witness(coordinator):
    """Test task completion logged to IF.witness"""
    await coordinator.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])
    await coordinator.claim_task('session-7', 'task-123')
    await coordinator.complete_task('session-7', 'task-123')

    # Verify witness logging
    ops = witness.get_operations(component='IF.coordinator', operation='task_completed')
    assert len(ops) == 1
    assert ops[0].params['swarm_id'] == 'session-7'
    assert 'execution_time' in ops[0].params


# ========== Health Check Tests ==========

@pytest.mark.asyncio
async def test_health_check(coordinator):
    """Test coordinator health check"""
    health = coordinator.health_check()

    assert health['status'] == 'healthy'
    assert health['connected'] == True
    assert 'event_bus' in health
    assert 'performance' in health


@pytest.mark.asyncio
async def test_disconnected_coordinator_health(coordinator):
    """Test health check when disconnected"""
    await coordinator.disconnect()

    health = coordinator.health_check()
    assert health['status'] == 'disconnected'
    assert health['connected'] == False


# ========== Error Handling Tests ==========

@pytest.mark.asyncio
async def test_operations_without_connection_fail():
    """Test operations fail gracefully without connection"""
    coord = IFCoordinator()
    # Not connected

    with pytest.raises(ConnectionError):
        await coord.create_task('task-123', [Capability.CODE_ANALYSIS_PYTHON])

    with pytest.raises(ConnectionError):
        await coord.claim_task('session-7', 'task-123')


# ========== Full Workflow Integration Test ==========

@pytest.mark.asyncio
async def test_full_task_lifecycle(coordinator):
    """Test complete task lifecycle: create → claim → complete"""
    # Step 1: Create task
    success = await coordinator.create_task(
        'task-123',
        [Capability.CODE_ANALYSIS_PYTHON, Capability.TESTING_UNIT],
        priority=10
    )
    assert success == True

    # Verify created
    task = await coordinator.get_task_status('task-123')
    assert task['status'] == 'available'

    # Step 2: Claim task
    success = await coordinator.claim_task('session-7', 'task-123')
    assert success == True

    # Verify claimed
    task = await coordinator.get_task_status('task-123')
    assert task['status'] == 'claimed'
    assert task['claimed_by'] == 'session-7'

    # Step 3: Complete task
    success = await coordinator.complete_task(
        'session-7',
        'task-123',
        result={'status': 'success', 'tests_passed': 42}
    )
    assert success == True

    # Verify completed
    task = await coordinator.get_task_status('task-123')
    assert task['status'] == 'completed'
    assert task['result']['tests_passed'] == 42

    # Verify witness logged all stages
    create_ops = witness.get_operations(component='IF.coordinator', operation='task_created')
    claim_ops = witness.get_operations(component='IF.coordinator', operation='task_claimed')
    complete_ops = witness.get_operations(component='IF.coordinator', operation='task_completed')

    assert len(create_ops) == 1
    assert len(claim_ops) == 1
    assert len(complete_ops) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
