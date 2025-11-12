"""
Unit Tests for IF.policies - Policy Engine

Tests policy loading, validation, and enforcement.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from infrafabric.policies import PolicyEngine
from infrafabric.schemas.capability import ResourcePolicy


# ==================== Policy Engine Tests ====================


def test_policy_engine_default():
    """Test PolicyEngine with default policy."""
    engine = PolicyEngine()
    assert engine.policy is not None
    assert engine.policy.max_swarms_per_task == 3
    assert engine.policy.max_cost_per_task == 10.0  # ResourcePolicy default
    assert engine.policy.min_capability_match == 0.7


def test_load_policy_from_yaml():
    """Test loading policy from YAML file."""
    # Create temporary YAML file
    config = {
        'resource_policy': {
            'max_swarms_per_task': 5,
            'max_cost_per_task': 50.0,
            'min_capability_match': 0.8,
            'circuit_breaker_failure_threshold': 5
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        config_path = f.name

    try:
        engine = PolicyEngine(config_path)
        assert engine.policy.max_swarms_per_task == 5
        assert engine.policy.max_cost_per_task == 50.0
        assert engine.policy.min_capability_match == 0.8
        assert engine.policy.circuit_breaker_failure_threshold == 5
    finally:
        Path(config_path).unlink()


def test_load_policy_file_not_found():
    """Test that loading non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        PolicyEngine("nonexistent.yaml")


def test_load_policy_invalid_yaml():
    """Test that invalid YAML raises error."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid: yaml: content:")
        config_path = f.name

    try:
        with pytest.raises(yaml.YAMLError):
            PolicyEngine(config_path)
    finally:
        Path(config_path).unlink()


def test_load_policy_not_dict():
    """Test that non-dict YAML raises ValueError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("- list\n- items\n")
        config_path = f.name

    try:
        with pytest.raises(ValueError, match="must be a dictionary"):
            PolicyEngine(config_path)
    finally:
        Path(config_path).unlink()


def test_validate_assignment_valid():
    """Test validating valid task assignment."""
    engine = PolicyEngine()
    valid = engine.validate_assignment(
        swarm_ids=["swarm-1", "swarm-2"],
        task_budget=8.0
    )
    assert valid is True


def test_validate_assignment_too_many_swarms():
    """Test that too many swarms fails validation."""
    engine = PolicyEngine()
    # Default policy allows max 3 swarms
    valid = engine.validate_assignment(
        swarm_ids=["swarm-1", "swarm-2", "swarm-3", "swarm-4"],
        task_budget=8.0
    )
    assert valid is False


def test_validate_assignment_exceeds_budget():
    """Test that exceeding budget fails validation."""
    engine = PolicyEngine()
    # Default policy allows max $25
    valid = engine.validate_assignment(
        swarm_ids=["swarm-1"],
        task_budget=30.0
    )
    assert valid is False


def test_check_max_swarms_within_limit():
    """Test checking max swarms within limit."""
    engine = PolicyEngine()
    assert engine.check_max_swarms(["swarm-1", "swarm-2"]) is True


def test_check_max_swarms_at_limit():
    """Test checking max swarms at exact limit."""
    engine = PolicyEngine()
    assert engine.check_max_swarms(["swarm-1", "swarm-2", "swarm-3"]) is True


def test_check_max_swarms_exceeds_limit():
    """Test checking max swarms exceeds limit."""
    engine = PolicyEngine()
    assert engine.check_max_swarms(["s1", "s2", "s3", "s4"]) is False


def test_check_max_cost_within_limit():
    """Test checking cost within limit."""
    engine = PolicyEngine()
    assert engine.check_max_cost(8.0) is True  # Below default 10.0


def test_check_max_cost_at_limit():
    """Test checking cost at exact limit."""
    engine = PolicyEngine()
    assert engine.check_max_cost(10.0) is True  # At default limit


def test_check_max_cost_exceeds_limit():
    """Test checking cost exceeds limit."""
    engine = PolicyEngine()
    assert engine.check_max_cost(30.0) is False


def test_check_capability_match_above_threshold():
    """Test capability match above threshold."""
    engine = PolicyEngine()
    assert engine.check_capability_match(0.85) is True


def test_check_capability_match_at_threshold():
    """Test capability match at exact threshold."""
    engine = PolicyEngine()
    assert engine.check_capability_match(0.7) is True


def test_check_capability_match_below_threshold():
    """Test capability match below threshold."""
    engine = PolicyEngine()
    assert engine.check_capability_match(0.65) is False


def test_get_policy_summary():
    """Test getting policy summary."""
    engine = PolicyEngine()
    summary = engine.get_policy_summary()

    assert 'max_swarms_per_task' in summary
    assert 'max_cost_per_task' in summary
    assert 'min_capability_match' in summary
    assert summary['max_swarms_per_task'] == 3
    assert summary['max_cost_per_task'] == 10.0  # ResourcePolicy default


def test_policy_with_all_fields():
    """Test loading policy with all fields."""
    config = {
        'resource_policy': {
            'max_swarms_per_task': 5,
            'max_cost_per_task': 100.0,
            'min_capability_match': 0.9,
            'circuit_breaker_failure_threshold': 10,
            'prefer_reputation': False,
            'allow_budget_overdraft': 1.2
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        config_path = f.name

    try:
        engine = PolicyEngine(config_path)
        summary = engine.get_policy_summary()

        assert summary['max_swarms_per_task'] == 5
        assert summary['max_cost_per_task'] == 100.0
        assert summary['min_capability_match'] == 0.9
        assert summary['circuit_breaker_failure_threshold'] == 10
        assert summary['prefer_reputation'] is False
        assert summary['allow_budget_overdraft'] == 1.2
    finally:
        Path(config_path).unlink()


def test_policy_with_partial_fields():
    """Test loading policy with only some fields (uses defaults for others)."""
    config = {
        'resource_policy': {
            'max_swarms_per_task': 10
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        config_path = f.name

    try:
        engine = PolicyEngine(config_path)
        # Custom field
        assert engine.policy.max_swarms_per_task == 10
        # Default fields
        assert engine.policy.max_cost_per_task == 10.0  # ResourcePolicy default
        assert engine.policy.min_capability_match == 0.7
    finally:
        Path(config_path).unlink()
