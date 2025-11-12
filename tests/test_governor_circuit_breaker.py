"""Unit tests for IF.governor circuit breaker (P0.2.4)

Tests circuit breaker implementation:
- Budget exhaustion triggers circuit breaker
- Repeated failures trigger circuit breaker
- Circuit breaker prevents new task assignment
- Human escalation notifications
- Manual circuit breaker reset
- Failure count tracking
"""

import pytest
from infrafabric.governor import IFGovernor
from infrafabric.schemas.capability import (
    SwarmProfile,
    ResourcePolicy,
    Capability,
)
from infrafabric import witness, optimise


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state before each test"""
    witness.clear_operations()
    optimise.clear_cost_records()
    yield
    witness.clear_operations()
    optimise.clear_cost_records()


@pytest.fixture
def governor():
    """Create IF.governor instance"""
    policy = ResourcePolicy(
        max_cost_per_task=10.0,
        circuit_breaker_failure_threshold=3,
    )
    return IFGovernor(coordinator=None, policy=policy)


@pytest.fixture
def sample_profile():
    """Create sample swarm profile"""
    return SwarmProfile(
        swarm_id='session-7-test',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        reputation_score=0.95,
        current_budget_remaining=100.0,
    )


def test_circuit_breaker_trips_on_budget_exhaustion(governor, sample_profile):
    """Test circuit breaker trips when budget is exhausted"""
    governor.register_swarm(sample_profile)

    # Exhaust budget
    governor.track_cost('session-7-test', 'expensive-operation', 100.0)

    # Check circuit breaker tripped
    assert governor._circuit_breakers['session-7-test'] == True

    # Check witness logging
    ops = witness.get_operations(component='IF.governor', operation='circuit_breaker_tripped')
    assert len(ops) == 1
    assert ops[0].params['reason'] == 'budget_exhausted'
    assert ops[0].severity == 'HIGH'


def test_circuit_breaker_prevents_task_assignment(governor, sample_profile):
    """Test that circuit breaker prevents new task assignments"""
    governor.register_swarm(sample_profile)

    # Trip circuit breaker
    governor.track_cost('session-7-test', 'operation', 100.0)

    # Try to find swarm for task
    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        max_cost=20.0
    )

    # Swarm should not be returned
    assert swarm is None


def test_is_swarm_available_with_circuit_breaker(governor, sample_profile):
    """Test swarm availability check with circuit breaker"""
    governor.register_swarm(sample_profile)

    # Initially available
    assert governor.is_swarm_available('session-7-test') == True

    # Trip circuit breaker
    governor._trip_circuit_breaker('session-7-test', 'test_reason')

    # No longer available
    assert governor.is_swarm_available('session-7-test') == False


def test_reset_circuit_breaker(governor, sample_profile):
    """Test manual circuit breaker reset"""
    governor.register_swarm(sample_profile)

    # Trip circuit breaker
    governor.track_cost('session-7-test', 'operation', 100.0)
    assert governor._circuit_breakers['session-7-test'] == True

    # Reset circuit breaker
    governor.reset_circuit_breaker('session-7-test', new_budget=50.0)

    # Check circuit breaker cleared
    assert governor._circuit_breakers['session-7-test'] == False

    # Check swarm available again
    assert governor.is_swarm_available('session-7-test') == True

    # Check budget updated
    profile = governor.swarm_registry['session-7-test']
    assert profile.current_budget_remaining == 50.0

    # Check witness logging
    ops = witness.get_operations(component='IF.governor', operation='circuit_breaker_reset')
    assert len(ops) == 1


def test_reset_circuit_breaker_without_new_budget(governor, sample_profile):
    """Test resetting circuit breaker without changing budget"""
    governor.register_swarm(sample_profile)

    # Trip circuit breaker (but not via budget exhaustion)
    governor._trip_circuit_breaker('session-7-test', 'test_reason')

    # Reset without new budget
    governor.reset_circuit_breaker('session-7-test')

    # Circuit breaker should be cleared
    assert governor._circuit_breakers['session-7-test'] == False

    # Budget should be unchanged
    profile = governor.swarm_registry['session-7-test']
    assert profile.current_budget_remaining == 100.0


def test_reset_circuit_breaker_unknown_swarm(governor):
    """Test resetting circuit breaker for unknown swarm raises error"""
    with pytest.raises(ValueError, match="Unknown swarm"):
        governor.reset_circuit_breaker('unknown-swarm')


def test_record_task_failure_increments_count(governor, sample_profile):
    """Test that recording task failure increments failure count"""
    governor.register_swarm(sample_profile)

    # Record failures
    governor.record_task_failure('session-7-test', 'task-1', 'timeout')
    governor.record_task_failure('session-7-test', 'task-2', 'error')

    # Check failure count
    assert governor._failure_counts['session-7-test'] == 2

    # Check witness logging
    ops = witness.get_operations(component='IF.governor', operation='task_failed')
    assert len(ops) == 2


def test_record_task_failure_trips_circuit_breaker_at_threshold(governor, sample_profile):
    """Test circuit breaker trips after threshold failures"""
    governor.register_swarm(sample_profile)

    # Record failures up to threshold (3)
    governor.record_task_failure('session-7-test', 'task-1', 'error1')
    assert governor._circuit_breakers['session-7-test'] == False

    governor.record_task_failure('session-7-test', 'task-2', 'error2')
    assert governor._circuit_breakers['session-7-test'] == False

    governor.record_task_failure('session-7-test', 'task-3', 'error3')
    # Circuit breaker should trip on 3rd failure
    assert governor._circuit_breakers['session-7-test'] == True

    # Check witness logging
    ops = witness.get_operations(component='IF.governor', operation='circuit_breaker_tripped')
    assert len(ops) == 1
    assert ops[0].params['reason'] == 'repeated_failures'


def test_record_task_success_resets_failure_count(governor, sample_profile):
    """Test that successful task resets failure count"""
    governor.register_swarm(sample_profile)

    # Record some failures
    governor.record_task_failure('session-7-test', 'task-1', 'error')
    governor.record_task_failure('session-7-test', 'task-2', 'error')
    assert governor._failure_counts['session-7-test'] == 2

    # Record success
    governor.record_task_success('session-7-test', 'task-3', 120.0)

    # Failure count should be reset
    assert governor._failure_counts['session-7-test'] == 0

    # Circuit breaker should not trip
    assert governor._circuit_breakers['session-7-test'] == False


def test_record_task_success_logs_to_witness(governor, sample_profile):
    """Test that task success is logged to witness"""
    governor.register_swarm(sample_profile)

    governor.record_task_success('session-7-test', 'task-1', 60.5)

    ops = witness.get_operations(component='IF.governor', operation='task_succeeded')
    assert len(ops) == 1
    assert ops[0].params['swarm_id'] == 'session-7-test'
    assert ops[0].params['task_id'] == 'task-1'
    assert ops[0].params['duration_seconds'] == 60.5


def test_circuit_breaker_with_custom_threshold():
    """Test circuit breaker with custom failure threshold"""
    policy = ResourcePolicy(circuit_breaker_failure_threshold=5)
    governor = IFGovernor(coordinator=None, policy=policy)

    profile = SwarmProfile(
        swarm_id='session-test',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        current_budget_remaining=100.0,
    )
    governor.register_swarm(profile)

    # Record 4 failures (below threshold of 5)
    for i in range(4):
        governor.record_task_failure('session-test', f'task-{i}', 'error')

    # Circuit breaker should NOT trip
    assert governor._circuit_breakers['session-test'] == False

    # Record 5th failure
    governor.record_task_failure('session-test', 'task-5', 'error')

    # Circuit breaker should trip
    assert governor._circuit_breakers['session-test'] == True


def test_circuit_breaker_escalation_logged(governor, sample_profile, capsys):
    """Test that circuit breaker escalation is logged"""
    governor.register_swarm(sample_profile)

    # Trip circuit breaker
    governor._trip_circuit_breaker('session-7-test', 'test_escalation', {
        'details': 'test details'
    })

    # Check escalation was logged
    ops = witness.get_operations(component='IF.governor', operation='escalated_to_human')
    assert len(ops) == 1
    assert ops[0].params['swarm_id'] == 'session-7-test'
    assert ops[0].severity == 'HIGH'

    # Check console output (human notification)
    captured = capsys.readouterr()
    assert 'S² System Escalation Required' in captured.out
    assert 'session-7-test' in captured.out


def test_multiple_swarms_independent_circuit_breakers(governor):
    """Test that circuit breakers are independent per swarm"""
    profile1 = SwarmProfile(
        swarm_id='session-1',
        capabilities=[Capability.INTEGRATION_NDI],
        cost_per_hour=2.0,
        current_budget_remaining=100.0,
    )
    profile2 = SwarmProfile(
        swarm_id='session-7',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        current_budget_remaining=100.0,
    )

    governor.register_swarm(profile1)
    governor.register_swarm(profile2)

    # Trip circuit breaker for session-1
    governor._trip_circuit_breaker('session-1', 'test')

    # Check session-1 circuit breaker tripped
    assert governor._circuit_breakers['session-1'] == True

    # Check session-7 circuit breaker NOT tripped
    assert governor._circuit_breakers['session-7'] == False

    # Check availability
    assert governor.is_swarm_available('session-1') == False
    assert governor.is_swarm_available('session-7') == True


def test_circuit_breaker_details_in_witness(governor, sample_profile):
    """Test that circuit breaker includes details in witness log"""
    governor.register_swarm(sample_profile)

    details = {
        'final_operation': 'expensive_task',
        'final_cost': 100.0,
        'total_spent': 100.0,
    }

    governor._trip_circuit_breaker('session-7-test', 'budget_exhausted', details)

    ops = witness.get_operations(component='IF.governor', operation='circuit_breaker_tripped')
    assert len(ops) == 1
    assert ops[0].params['details'] == details


def test_reset_circuit_breaker_clears_failure_count(governor, sample_profile):
    """Test that resetting circuit breaker clears failure count"""
    governor.register_swarm(sample_profile)

    # Build up failure count
    governor.record_task_failure('session-7-test', 'task-1', 'error')
    governor.record_task_failure('session-7-test', 'task-2', 'error')
    governor.record_task_failure('session-7-test', 'task-3', 'error')

    # Circuit breaker tripped
    assert governor._circuit_breakers['session-7-test'] == True
    assert governor._failure_counts['session-7-test'] == 3

    # Reset
    governor.reset_circuit_breaker('session-7-test', new_budget=50.0)

    # Failure count should be cleared
    assert governor._failure_counts['session-7-test'] == 0


def test_get_budget_report_shows_circuit_breaker_status(governor, sample_profile):
    """Test that budget report includes circuit breaker status"""
    governor.register_swarm(sample_profile)

    # Initial report
    report = governor.get_budget_report('session-7-test')
    assert report['session-7-test']['circuit_breaker'] == False

    # Trip circuit breaker
    governor._trip_circuit_breaker('session-7-test', 'test')

    # Updated report
    report = governor.get_budget_report('session-7-test')
    assert report['session-7-test']['circuit_breaker'] == True


def test_get_swarm_stats_shows_circuit_breaker_and_failures(governor, sample_profile):
    """Test that swarm stats include circuit breaker and failure count"""
    governor.register_swarm(sample_profile)

    # Record some failures
    governor.record_task_failure('session-7-test', 'task-1', 'error')
    governor.record_task_failure('session-7-test', 'task-2', 'error')

    stats = governor.get_swarm_stats('session-7-test')

    assert stats['circuit_breaker'] == False
    assert stats['failure_count'] == 2
    assert stats['available'] == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
