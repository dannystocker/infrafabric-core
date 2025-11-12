"""Unit tests for IF.chassis resource limits (P0.3.2)

Tests resource limit enforcement:
- Memory limits
- CPU limits
- API rate limiting (token bucket)
- OS-level resource enforcement
- Resource violation tracking
"""

import pytest
import time
from infrafabric.chassis import IFChassis, ServiceContract, ResourceLimits, ResourceEnforcer, TokenBucket
from infrafabric import witness


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state before each test"""
    witness.clear_operations()
    yield
    witness.clear_operations()


@pytest.fixture
def sample_wasm_bytes():
    """Create minimal valid WASM module bytes"""
    # Minimal WASM module: (module)
    return bytes([
        0x00, 0x61, 0x73, 0x6d,  # \0asm - magic number
        0x01, 0x00, 0x00, 0x00,  # version 1
    ])


# ========== ResourceLimits Tests ==========

def test_resource_limits_defaults():
    """Test ResourceLimits default values"""
    limits = ResourceLimits()

    assert limits.max_memory_mb == 512
    assert limits.max_cpu_percent == 50
    assert limits.max_api_calls_per_second == 10.0
    assert limits.max_execution_time_seconds == 300.0
    assert limits.enable_os_limits == True


def test_resource_limits_custom():
    """Test ResourceLimits with custom values"""
    limits = ResourceLimits(
        max_memory_mb=256,
        max_cpu_percent=25,
        max_api_calls_per_second=5.0,
        max_execution_time_seconds=60.0,
        enable_os_limits=False,
    )

    assert limits.max_memory_mb == 256
    assert limits.max_cpu_percent == 25
    assert limits.max_api_calls_per_second == 5.0
    assert limits.max_execution_time_seconds == 60.0
    assert limits.enable_os_limits == False


def test_resource_limits_to_dict():
    """Test ResourceLimits serialization"""
    limits = ResourceLimits(max_memory_mb=256)
    data = limits.to_dict()

    assert data['max_memory_mb'] == 256
    assert data['max_cpu_percent'] == 50
    assert 'max_api_calls_per_second' in data


def test_resource_limits_from_dict():
    """Test ResourceLimits deserialization"""
    data = {
        'max_memory_mb': 128,
        'max_cpu_percent': 30,
    }

    limits = ResourceLimits.from_dict(data)

    assert limits.max_memory_mb == 128
    assert limits.max_cpu_percent == 30


# ========== TokenBucket Tests ==========

def test_token_bucket_initialization():
    """Test TokenBucket initialization"""
    bucket = TokenBucket(rate=10.0)

    assert bucket.rate == 10.0
    assert bucket.capacity == 20  # Default: rate * 2
    assert bucket.tokens == 20.0


def test_token_bucket_custom_capacity():
    """Test TokenBucket with custom capacity"""
    bucket = TokenBucket(rate=10.0, capacity=50)

    assert bucket.rate == 10.0
    assert bucket.capacity == 50
    assert bucket.tokens == 50.0


def test_token_bucket_consume_success():
    """Test successful token consumption"""
    bucket = TokenBucket(rate=10.0, capacity=10)

    success = bucket.consume(1)
    assert success == True
    assert bucket.tokens == 9.0


def test_token_bucket_consume_multiple():
    """Test consuming multiple tokens"""
    bucket = TokenBucket(rate=10.0, capacity=10)

    success = bucket.consume(5)
    assert success == True
    assert bucket.tokens == 5.0


def test_token_bucket_consume_failure():
    """Test failed token consumption"""
    bucket = TokenBucket(rate=10.0, capacity=5)

    # Consume all tokens
    bucket.consume(5)

    # Try to consume more
    success = bucket.consume(1)
    assert success == False
    assert bucket.tokens < 0.1  # Nearly 0 (some tiny refill may occur)


def test_token_bucket_refill():
    """Test token bucket refill over time"""
    bucket = TokenBucket(rate=10.0, capacity=10)

    # Consume all tokens
    bucket.consume(10)
    assert bucket.tokens == 0.0

    # Wait for refill (0.5 seconds = 5 tokens)
    time.sleep(0.5)

    available = bucket.get_available_tokens()
    assert available >= 4.5  # Allow for timing variations


def test_token_bucket_max_capacity():
    """Test that tokens don't exceed capacity"""
    bucket = TokenBucket(rate=10.0, capacity=10)

    # Wait for more than capacity worth of time
    time.sleep(2.0)

    available = bucket.get_available_tokens()
    assert available <= 10.0  # Should not exceed capacity


# ========== ResourceEnforcer Tests ==========

def test_resource_enforcer_initialization():
    """Test ResourceEnforcer initialization"""
    limits = ResourceLimits(max_api_calls_per_second=5.0)
    enforcer = ResourceEnforcer('session-7', limits)

    assert enforcer.swarm_id == 'session-7'
    assert enforcer.limits == limits
    assert enforcer.violation_count == 0
    assert enforcer.api_calls_blocked == 0

    # Check witness logging
    ops = witness.get_operations(component='IF.chassis.limits', operation='enforcer_initialized')
    assert len(ops) == 1


def test_resource_enforcer_apply_os_limits():
    """Test applying OS-level resource limits"""
    limits = ResourceLimits(enable_os_limits=True)
    enforcer = ResourceEnforcer('session-7', limits)

    # Try to apply OS limits (may not work on all systems)
    result = enforcer.apply_os_limits()

    # Result depends on system support, just check it returns bool
    assert isinstance(result, bool)


def test_resource_enforcer_apply_os_limits_disabled():
    """Test OS limits when disabled"""
    limits = ResourceLimits(enable_os_limits=False)
    enforcer = ResourceEnforcer('session-7', limits)

    result = enforcer.apply_os_limits()
    assert result == False


def test_resource_enforcer_check_api_rate_limit_allowed():
    """Test API rate limit when allowed"""
    limits = ResourceLimits(max_api_calls_per_second=10.0)
    enforcer = ResourceEnforcer('session-7', limits)

    allowed = enforcer.check_api_rate_limit(1)
    assert allowed == True
    assert enforcer.api_calls_blocked == 0


def test_resource_enforcer_check_api_rate_limit_exceeded():
    """Test API rate limit when exceeded"""
    limits = ResourceLimits(max_api_calls_per_second=2.0)
    enforcer = ResourceEnforcer('session-7', limits)

    # Consume all tokens
    for i in range(4):  # Capacity is rate * 2 = 4
        enforcer.check_api_rate_limit(1)

    # Next call should be blocked
    allowed = enforcer.check_api_rate_limit(1)
    assert allowed == False
    assert enforcer.api_calls_blocked >= 1

    # Check witness logging
    ops = witness.get_operations(component='IF.chassis.limits', operation='api_rate_limit_exceeded')
    assert len(ops) >= 1


def test_resource_enforcer_record_violation():
    """Test recording resource violations"""
    limits = ResourceLimits()
    enforcer = ResourceEnforcer('session-7', limits)

    enforcer.record_violation('memory', {'usage_mb': 600, 'limit_mb': 512})

    assert enforcer.violation_count == 1

    # Check witness logging
    ops = witness.get_operations(component='IF.chassis.limits', operation='resource_violation')
    assert len(ops) == 1
    assert ops[0].params['violation_type'] == 'memory'


def test_resource_enforcer_get_stats():
    """Test getting enforcer statistics"""
    limits = ResourceLimits(max_api_calls_per_second=5.0)
    enforcer = ResourceEnforcer('session-7', limits)

    # Generate some activity
    enforcer.check_api_rate_limit(1)
    enforcer.record_violation('cpu', {'usage': 80})

    stats = enforcer.get_stats()

    assert stats['swarm_id'] == 'session-7'
    assert stats['violation_count'] == 1
    assert 'limits' in stats
    assert 'api_tokens_available' in stats


def test_resource_enforcer_reset_stats():
    """Test resetting enforcer statistics"""
    limits = ResourceLimits()
    enforcer = ResourceEnforcer('session-7', limits)

    # Generate violations
    enforcer.record_violation('memory', {})
    enforcer.record_violation('cpu', {})

    assert enforcer.violation_count == 2

    # Reset
    enforcer.reset_stats()

    assert enforcer.violation_count == 0
    assert enforcer.api_calls_blocked == 0


# ========== Integration with IFChassis Tests ==========

def test_chassis_loads_swarm_with_resource_limits(sample_wasm_bytes):
    """Test that chassis loads swarm with resource enforcer"""
    chassis = IFChassis()

    limits = ResourceLimits(
        max_memory_mb=128,
        max_api_calls_per_second=5.0,
        enable_os_limits=False  # Disable to prevent test abortion
    )
    contract = ServiceContract(
        swarm_id='session-7',
        resource_limits=limits
    )

    success = chassis.load_swarm('session-7', wasm_bytes=sample_wasm_bytes, contract=contract)

    assert success == True

    # Check enforcer is present
    swarm_info = chassis.loaded_swarms['session-7']
    assert 'enforcer' in swarm_info
    assert isinstance(swarm_info['enforcer'], ResourceEnforcer)


def test_chassis_execute_task_checks_api_rate_limit(sample_wasm_bytes):
    """Test that execute_task enforces API rate limits"""
    chassis = IFChassis()

    limits = ResourceLimits(max_api_calls_per_second=2.0, enable_os_limits=False)
    contract = ServiceContract(swarm_id='session-7', resource_limits=limits)

    chassis.load_swarm('session-7', wasm_bytes=sample_wasm_bytes, contract=contract)

    # Exhaust rate limit
    for i in range(4):  # Capacity is 4
        result = chassis.execute_task('session-7', 'task')
        assert result['success'] == True

    # Next call should be blocked
    result = chassis.execute_task('session-7', 'task')
    assert result['success'] == False
    assert result['error'] == 'API rate limit exceeded'


def test_chassis_get_swarm_stats_includes_enforcer_stats(sample_wasm_bytes):
    """Test that swarm stats include enforcer statistics"""
    chassis = IFChassis()

    limits = ResourceLimits(max_api_calls_per_second=5.0, enable_os_limits=False)
    contract = ServiceContract(swarm_id='session-7', resource_limits=limits)

    chassis.load_swarm('session-7', wasm_bytes=sample_wasm_bytes, contract=contract)
    chassis.execute_task('session-7', 'task1')

    stats = chassis.get_swarm_stats('session-7')

    assert 'violation_count' in stats
    assert 'api_calls_blocked' in stats
    assert 'api_tokens_available' in stats
    assert 'limits' in stats


def test_service_contract_get_resource_limits():
    """Test ServiceContract.get_resource_limits() method"""
    # Without resource_limits override
    contract1 = ServiceContract(
        swarm_id='test',
        max_memory_mb=256,
        max_api_calls_per_second=5.0
    )

    limits1 = contract1.get_resource_limits()
    assert limits1.max_memory_mb == 256
    assert limits1.max_api_calls_per_second == 5.0

    # With resource_limits override
    custom_limits = ResourceLimits(max_memory_mb=128)
    contract2 = ServiceContract(
        swarm_id='test',
        max_memory_mb=256,
        resource_limits=custom_limits
    )

    limits2 = contract2.get_resource_limits()
    assert limits2.max_memory_mb == 128  # Uses override


def test_service_contract_includes_api_calls_in_dict():
    """Test that ServiceContract.to_dict() includes API rate limit"""
    contract = ServiceContract(
        swarm_id='test',
        max_api_calls_per_second=15.0
    )

    data = contract.to_dict()
    assert data['max_api_calls_per_second'] == 15.0


def test_multiple_swarms_independent_rate_limits(sample_wasm_bytes):
    """Test that multiple swarms have independent rate limits"""
    chassis = IFChassis()

    # Swarm 1: Low rate limit
    limits1 = ResourceLimits(max_api_calls_per_second=1.0, enable_os_limits=False)
    contract1 = ServiceContract(swarm_id='session-1', resource_limits=limits1)
    chassis.load_swarm('session-1', wasm_bytes=sample_wasm_bytes, contract=contract1)

    # Swarm 2: High rate limit
    limits2 = ResourceLimits(max_api_calls_per_second=10.0, enable_os_limits=False)
    contract2 = ServiceContract(swarm_id='session-7', resource_limits=limits2)
    chassis.load_swarm('session-7', wasm_bytes=sample_wasm_bytes, contract=contract2)

    # Exhaust session-1 rate limit
    chassis.execute_task('session-1', 'task')
    chassis.execute_task('session-1', 'task')

    result1 = chassis.execute_task('session-1', 'task')
    assert result1['success'] == False  # Rate limited

    # session-7 should still work
    result7 = chassis.execute_task('session-7', 'task')
    assert result7['success'] == True  # Not rate limited


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
