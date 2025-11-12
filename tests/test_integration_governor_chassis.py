"""Integration tests for IF.governor + IF.chassis

This module tests the integration between:
- IF.governor: Capability-aware resource and budget management
- IF.chassis: WASM sandbox runtime with resource limits

Scenarios tested:
1. Full workflow: Find swarm → Load → Execute → Track cost
2. Budget exhaustion → Circuit breaker → Prevents execution
3. API rate limiting across governor and chassis
4. Resource limit enforcement during task execution
5. Multi-swarm coordination with independent limits

These tests verify that P0.2.2, P0.2.3, P0.2.4, P0.3.1, P0.3.2 work together.

Run with: python -m pytest tests/test_integration_governor_chassis.py -v
"""

import pytest
import time
from typing import List
from infrafabric.governor import IFGovernor
from infrafabric.chassis import IFChassis, ServiceContract, ResourceLimits
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
def sample_wasm_bytes():
    """Create minimal valid WASM module bytes"""
    # Minimal WASM module: (module)
    return bytes([
        0x00, 0x61, 0x73, 0x6d,  # \0asm - magic number
        0x01, 0x00, 0x00, 0x00,  # version 1
    ])


@pytest.fixture
def governor_with_swarms():
    """Create governor with multiple registered swarms"""
    policy = ResourcePolicy(
        min_capability_match=0.7,
        max_cost_per_task=50.0,
    )
    governor = IFGovernor(coordinator=None, policy=policy)

    # Register swarms with different capabilities
    swarms = [
        SwarmProfile(
            swarm_id='python-swarm',
            capabilities=[Capability.CODE_ANALYSIS_PYTHON, Capability.TESTING_UNIT],
            cost_per_hour=10.0,
            reputation_score=0.95,
            current_budget_remaining=100.0,
        ),
        SwarmProfile(
            swarm_id='rust-swarm',
            capabilities=[Capability.CODE_ANALYSIS_RUST, Capability.ARCHITECTURE_PERFORMANCE],
            cost_per_hour=15.0,
            reputation_score=0.90,
            current_budget_remaining=100.0,
        ),
        SwarmProfile(
            swarm_id='sip-swarm',
            capabilities=[Capability.INTEGRATION_SIP, Capability.TESTING_INTEGRATION],
            cost_per_hour=20.0,
            reputation_score=0.85,
            current_budget_remaining=100.0,
        ),
    ]

    for swarm in swarms:
        governor.register_swarm(swarm)

    return governor


@pytest.fixture
def chassis():
    """Create chassis instance"""
    return IFChassis()


# ========== Full Workflow Integration Tests ==========

def test_full_workflow_find_load_execute_track(governor_with_swarms, chassis, sample_wasm_bytes):
    """Test complete workflow: Find → Load → Execute → Track Cost

    This is the primary integration test verifying all Phase 0 components work together.
    """
    governor = governor_with_swarms

    # Step 1: Find qualified swarm (P0.2.2)
    required_caps = [Capability.CODE_ANALYSIS_PYTHON]
    swarm_id = governor.find_qualified_swarm(required_caps, max_cost=50.0)

    assert swarm_id == 'python-swarm'  # Best match by score

    # Step 2: Load swarm into chassis (P0.3.1)
    limits = ResourceLimits(
        max_memory_mb=256,
        max_api_calls_per_second=10.0,
        enable_os_limits=False,
    )
    contract = ServiceContract(swarm_id=swarm_id, resource_limits=limits)

    success = chassis.load_swarm(swarm_id, wasm_bytes=sample_wasm_bytes, contract=contract)
    assert success == True
    assert chassis.is_swarm_loaded(swarm_id)

    # Step 3: Execute task (P0.3.2 - resource limits enforced)
    result = chassis.execute_task(
        swarm_id=swarm_id,
        task_name='analyze_code',
        task_params={'file': 'main.py', 'checks': ['syntax', 'security']}
    )

    assert result['success'] == True
    assert result['error'] is None

    # Step 4: Track cost in governor (P0.2.3)
    execution_cost = 2.5  # $2.50 for this task
    governor.track_cost(swarm_id, 'analyze_code', execution_cost)

    # Verify budget was deducted
    budget_report = governor.get_budget_report(swarm_id)
    assert budget_report[swarm_id]['remaining'] == 97.5  # 100 - 2.5

    # Verify cost was logged
    cost_report = optimise.get_total_cost(provider=swarm_id)
    assert cost_report == execution_cost

    # Verify swarm is still available
    assert governor.is_swarm_available(swarm_id) == True


def test_workflow_with_task_success_tracking(governor_with_swarms, chassis, sample_wasm_bytes):
    """Test workflow with success tracking and reputation"""
    governor = governor_with_swarms

    # Find and load swarm
    swarm_id = governor.find_qualified_swarm([Capability.CODE_ANALYSIS_PYTHON], max_cost=50.0)
    limits = ResourceLimits(max_memory_mb=256, enable_os_limits=False)
    contract = ServiceContract(swarm_id=swarm_id, resource_limits=limits)
    chassis.load_swarm(swarm_id, wasm_bytes=sample_wasm_bytes, contract=contract)

    # Execute task
    result = chassis.execute_task(swarm_id, 'unit_test', {'test_file': 'test_main.py'})
    assert result['success'] == True

    # Record success in governor (P0.2.4)
    execution_time = result['execution_time_ms']
    governor.record_task_success(swarm_id, 'task-001', execution_time)

    # Verify success was recorded via witness logs
    ops = witness.get_operations(component='IF.governor', operation='task_succeeded')
    assert len(ops) == 1
    assert ops[0].params['swarm_id'] == swarm_id
    assert ops[0].params['task_id'] == 'task-001'


def test_workflow_with_multiple_swarms(governor_with_swarms, chassis, sample_wasm_bytes):
    """Test coordinating multiple swarms simultaneously"""
    governor = governor_with_swarms

    # Load multiple swarms
    swarms_to_load = ['python-swarm', 'rust-swarm', 'sip-swarm']

    for swarm_id in swarms_to_load:
        limits = ResourceLimits(
            max_memory_mb=128,
            max_api_calls_per_second=5.0,
            enable_os_limits=False,
        )
        contract = ServiceContract(swarm_id=swarm_id, resource_limits=limits)
        success = chassis.load_swarm(swarm_id, wasm_bytes=sample_wasm_bytes, contract=contract)
        assert success == True

    # Execute tasks on different swarms
    python_result = chassis.execute_task('python-swarm', 'analyze_python', {})
    rust_result = chassis.execute_task('rust-swarm', 'analyze_rust', {})
    sip_result = chassis.execute_task('sip-swarm', 'test_sip_call', {})

    assert python_result['success'] == True
    assert rust_result['success'] == True
    assert sip_result['success'] == True

    # Track costs for all swarms
    governor.track_cost('python-swarm', 'analyze_python', 1.5)
    governor.track_cost('rust-swarm', 'analyze_rust', 2.0)
    governor.track_cost('sip-swarm', 'test_sip_call', 3.0)

    # Verify all swarms still available
    assert governor.is_swarm_available('python-swarm') == True
    assert governor.is_swarm_available('rust-swarm') == True
    assert governor.is_swarm_available('sip-swarm') == True

    # Verify total cost
    assert optimise.get_total_cost() == 6.5


# ========== Budget Exhaustion and Circuit Breaker Tests ==========

def test_budget_exhaustion_prevents_task_execution(governor_with_swarms, chassis, sample_wasm_bytes):
    """Test that budget exhaustion trips circuit breaker and prevents execution

    Integration of P0.2.3 (Budget Tracking) + P0.2.4 (Circuit Breaker)
    """
    governor = governor_with_swarms

    # Find and load swarm
    swarm_id = 'python-swarm'
    limits = ResourceLimits(max_memory_mb=256, enable_os_limits=False)
    contract = ServiceContract(swarm_id=swarm_id, resource_limits=limits)
    chassis.load_swarm(swarm_id, wasm_bytes=sample_wasm_bytes, contract=contract)

    # Exhaust budget (budget is 100.0)
    governor.track_cost(swarm_id, 'expensive_operation', 100.0)

    # Verify circuit breaker tripped
    assert governor.is_swarm_available(swarm_id) == False

    # Attempt to execute task - should be rejected by governor's circuit breaker
    # (Note: In real usage, you'd check is_swarm_available() before calling chassis)
    # For this test, we verify the circuit breaker state
    circuit_breaker_status = governor._circuit_breakers.get(swarm_id, False)
    assert circuit_breaker_status == True

    # Verify witness logged the circuit breaker trip
    ops = witness.get_operations(component='IF.governor', operation='circuit_breaker_tripped')
    assert len(ops) == 1
    assert ops[0].params['swarm_id'] == swarm_id
    assert ops[0].params['reason'] == 'budget_exhausted'


def test_budget_tracking_with_circuit_breaker_reset(governor_with_swarms, chassis, sample_wasm_bytes):
    """Test circuit breaker can be reset after budget exhaustion"""
    governor = governor_with_swarms

    swarm_id = 'python-swarm'
    limits = ResourceLimits(max_memory_mb=256, enable_os_limits=False)
    contract = ServiceContract(swarm_id=swarm_id, resource_limits=limits)
    chassis.load_swarm(swarm_id, wasm_bytes=sample_wasm_bytes, contract=contract)

    # Exhaust budget
    governor.track_cost(swarm_id, 'task', 100.0)
    assert governor.is_swarm_available(swarm_id) == False

    # Reset circuit breaker and restore budget
    governor.reset_circuit_breaker(swarm_id, new_budget=50.0)

    # Verify swarm is available again
    assert governor.is_swarm_available(swarm_id) == True

    # Execute task successfully
    result = chassis.execute_task(swarm_id, 'task', {})
    assert result['success'] == True


def test_repeated_failures_trip_circuit_breaker(governor_with_swarms, chassis, sample_wasm_bytes):
    """Test that repeated task failures trip circuit breaker

    Integration of P0.2.4 (Circuit Breaker) with task execution
    """
    governor = governor_with_swarms

    swarm_id = 'python-swarm'

    # Record failures (threshold is 3 by default)
    for i in range(5):
        governor.record_task_failure(swarm_id, f'task-{i}', 'Simulated failure')

    # Circuit breaker should trip
    assert governor.is_swarm_available(swarm_id) == False

    # Verify witness logged (may trip multiple times as failures continue after threshold)
    ops = witness.get_operations(component='IF.governor', operation='circuit_breaker_tripped')
    assert len(ops) >= 1  # At least one trip
    assert ops[0].params['reason'] == 'repeated_failures'


# ========== API Rate Limiting Integration Tests ==========

def test_api_rate_limiting_across_governor_and_chassis(governor_with_swarms, chassis, sample_wasm_bytes):
    """Test that API rate limiting in chassis works correctly

    Integration of P0.3.2 (Resource Limits) with task execution
    """
    governor = governor_with_swarms

    # Load swarm with low rate limit
    swarm_id = 'python-swarm'
    limits = ResourceLimits(max_api_calls_per_second=2.0, enable_os_limits=False)
    contract = ServiceContract(swarm_id=swarm_id, resource_limits=limits)
    chassis.load_swarm(swarm_id, wasm_bytes=sample_wasm_bytes, contract=contract)

    # Exhaust rate limit (capacity is 4 tokens)
    for i in range(4):
        result = chassis.execute_task(swarm_id, f'task-{i}', {})
        assert result['success'] == True

    # Next call should be rate limited
    result = chassis.execute_task(swarm_id, 'task-blocked', {})
    assert result['success'] == False
    assert result['error'] == 'API rate limit exceeded'

    # Verify stats
    stats = chassis.get_swarm_stats(swarm_id)
    assert stats['api_calls_blocked'] >= 1


def test_independent_rate_limits_per_swarm(governor_with_swarms, chassis, sample_wasm_bytes):
    """Test that different swarms have independent rate limits"""
    governor = governor_with_swarms

    # Load swarm 1 with low rate limit
    limits1 = ResourceLimits(max_api_calls_per_second=1.0, enable_os_limits=False)
    contract1 = ServiceContract(swarm_id='python-swarm', resource_limits=limits1)
    chassis.load_swarm('python-swarm', wasm_bytes=sample_wasm_bytes, contract=contract1)

    # Load swarm 2 with high rate limit
    limits2 = ResourceLimits(max_api_calls_per_second=10.0, enable_os_limits=False)
    contract2 = ServiceContract(swarm_id='rust-swarm', resource_limits=limits2)
    chassis.load_swarm('rust-swarm', wasm_bytes=sample_wasm_bytes, contract=contract2)

    # Exhaust swarm 1's rate limit
    chassis.execute_task('python-swarm', 'task1', {})
    chassis.execute_task('python-swarm', 'task2', {})

    result1 = chassis.execute_task('python-swarm', 'task3', {})
    assert result1['success'] == False  # Rate limited

    # Swarm 2 should still work
    result2 = chassis.execute_task('rust-swarm', 'task1', {})
    assert result2['success'] == True


# ========== Resource Limit Enforcement Tests ==========

def test_resource_limits_enforced_during_execution(governor_with_swarms, chassis, sample_wasm_bytes):
    """Test that resource limits are enforced during task execution

    Integration of P0.3.2 (Resource Limits) with P0.3.1 (WASM Runtime)
    """
    governor = governor_with_swarms

    # Load swarm with strict resource limits
    swarm_id = 'python-swarm'
    limits = ResourceLimits(
        max_memory_mb=128,
        max_cpu_percent=25,
        max_api_calls_per_second=5.0,
        enable_os_limits=False,  # Disable for test
    )
    contract = ServiceContract(swarm_id=swarm_id, resource_limits=limits)
    chassis.load_swarm(swarm_id, wasm_bytes=sample_wasm_bytes, contract=contract)

    # Verify enforcer is present
    swarm_info = chassis.loaded_swarms[swarm_id]
    assert 'enforcer' in swarm_info

    enforcer = swarm_info['enforcer']
    assert enforcer.limits.max_memory_mb == 128
    assert enforcer.limits.max_cpu_percent == 25

    # Execute task
    result = chassis.execute_task(swarm_id, 'task', {})
    assert result['success'] == True


def test_get_swarm_stats_includes_resource_stats(governor_with_swarms, chassis, sample_wasm_bytes):
    """Test that swarm stats include resource enforcement statistics"""
    governor = governor_with_swarms

    swarm_id = 'python-swarm'
    limits = ResourceLimits(max_api_calls_per_second=5.0, enable_os_limits=False)
    contract = ServiceContract(swarm_id=swarm_id, resource_limits=limits)
    chassis.load_swarm(swarm_id, wasm_bytes=sample_wasm_bytes, contract=contract)

    # Execute some tasks
    chassis.execute_task(swarm_id, 'task1', {})
    chassis.execute_task(swarm_id, 'task2', {})

    # Get stats
    stats = chassis.get_swarm_stats(swarm_id)

    # Verify resource stats are included
    assert 'violation_count' in stats
    assert 'api_calls_blocked' in stats
    assert 'api_tokens_available' in stats
    assert 'limits' in stats
    assert stats['total_executions'] == 2


# ========== Capability Matching with Execution Tests ==========

def test_capability_matching_selects_correct_swarm(governor_with_swarms, chassis, sample_wasm_bytes):
    """Test that capability matching (P0.2.2) selects the right swarm for execution"""
    governor = governor_with_swarms

    # Find swarm for Python task
    python_swarm = governor.find_qualified_swarm([Capability.CODE_ANALYSIS_PYTHON], max_cost=50.0)
    assert python_swarm == 'python-swarm'

    # Find swarm for Rust task
    rust_swarm = governor.find_qualified_swarm([Capability.CODE_ANALYSIS_RUST], max_cost=50.0)
    assert rust_swarm == 'rust-swarm'

    # Find swarm for SIP integration
    sip_swarm = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=50.0)
    assert sip_swarm == 'sip-swarm'

    # Load all three swarms
    for swarm_id in [python_swarm, rust_swarm, sip_swarm]:
        limits = ResourceLimits(max_memory_mb=256, enable_os_limits=False)
        contract = ServiceContract(swarm_id=swarm_id, resource_limits=limits)
        chassis.load_swarm(swarm_id, wasm_bytes=sample_wasm_bytes, contract=contract)

    # Execute tasks on correct swarms
    result1 = chassis.execute_task(python_swarm, 'analyze_python', {})
    result2 = chassis.execute_task(rust_swarm, 'analyze_rust', {})
    result3 = chassis.execute_task(sip_swarm, 'sip_integration', {})

    assert all([result1['success'], result2['success'], result3['success']])


def test_no_qualified_swarm_available(governor_with_swarms, chassis, sample_wasm_bytes):
    """Test behavior when no swarm matches capability requirements"""
    governor = governor_with_swarms

    # Request capability that no swarm has
    swarm_id = governor.find_qualified_swarm([Capability.INTEGRATION_WEBRTC], max_cost=50.0)

    # No swarm should be found
    assert swarm_id is None


# ========== Comprehensive Integration Test ==========

def test_comprehensive_multi_swarm_workflow(governor_with_swarms, chassis, sample_wasm_bytes):
    """Comprehensive test of governor + chassis with multiple swarms and various scenarios

    This test exercises all Phase 0 components in a realistic scenario:
    - P0.2.2: Capability matching
    - P0.2.3: Budget tracking
    - P0.2.4: Circuit breaker
    - P0.3.1: WASM runtime
    - P0.3.2: Resource limits
    """
    governor = governor_with_swarms

    # Scenario 1: Find and use Python swarm for code analysis
    python_swarm = governor.find_qualified_swarm([Capability.CODE_ANALYSIS_PYTHON], max_cost=50.0)
    limits1 = ResourceLimits(
        max_memory_mb=256,
        max_api_calls_per_second=10.0,
        enable_os_limits=False,
    )
    contract1 = ServiceContract(swarm_id=python_swarm, resource_limits=limits1)
    chassis.load_swarm(python_swarm, wasm_bytes=sample_wasm_bytes, contract=contract1)

    result1 = chassis.execute_task(python_swarm, 'analyze_code', {'file': 'app.py'})
    assert result1['success'] == True

    governor.track_cost(python_swarm, 'analyze_code', 5.0)
    governor.record_task_success(python_swarm, 'task-001', result1['execution_time_ms'])

    # Scenario 2: Find and use SIP swarm for integration testing
    sip_swarm = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=50.0)
    limits2 = ResourceLimits(
        max_memory_mb=512,
        max_api_calls_per_second=5.0,
        enable_os_limits=False,
    )
    contract2 = ServiceContract(swarm_id=sip_swarm, resource_limits=limits2)
    chassis.load_swarm(sip_swarm, wasm_bytes=sample_wasm_bytes, contract=contract2)

    result2 = chassis.execute_task(sip_swarm, 'sip_integration_test', {})
    assert result2['success'] == True

    governor.track_cost(sip_swarm, 'sip_integration_test', 10.0)
    governor.record_task_success(sip_swarm, 'task-002', result2['execution_time_ms'])

    # Scenario 3: Exhaust Python swarm budget and verify circuit breaker
    governor.track_cost(python_swarm, 'expensive_task', 95.0)  # Total: 100.0
    assert governor.is_swarm_available(python_swarm) == False

    # Scenario 4: SIP swarm should still be available
    assert governor.is_swarm_available(sip_swarm) == True

    result3 = chassis.execute_task(sip_swarm, 'another_sip_test', {})
    assert result3['success'] == True

    # Verify total cost tracking
    total_cost = optimise.get_total_cost()
    assert total_cost == 110.0  # 5.0 + 10.0 + 95.0

    # Verify budget report
    budget_report = governor.get_budget_report()
    assert len(budget_report) == 3  # All three swarms registered

    assert budget_report[python_swarm]['remaining'] == 0.0
    assert budget_report[python_swarm]['circuit_breaker'] == True

    assert budget_report[sip_swarm]['remaining'] == 90.0
    assert budget_report[sip_swarm]['circuit_breaker'] == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
