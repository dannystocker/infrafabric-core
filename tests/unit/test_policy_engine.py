"""Unit tests for PolicyEngine (P0.2.5)

Tests cover:
- YAML policy loading
- Task assignment validation (max swarms, budget limits)
- Capability matching validation
- Budget limit checks
- Policy violation logging
- Integration helpers

Task: P0.2.5 - Policy engine implementation
Session: 4 (SIP)
Model: Sonnet
"""

import pytest
import tempfile
import yaml
import json
from pathlib import Path
from infrafabric.policies import (
    PolicyEngine,
    PolicyViolation,
    extract_required_capabilities,
)
from infrafabric.schemas.capability import ResourcePolicy, Capability


class TestPolicyEngineInitialization:
    """Test PolicyEngine initialization"""

    def test_create_with_default_policy(self):
        """Create policy engine with default policy"""
        engine = PolicyEngine()

        assert engine.policy.max_swarms_per_task == 3
        assert engine.policy.max_cost_per_task == 10.0
        assert engine.policy.min_capability_match == 0.7
        assert len(engine.violations) == 0

    def test_create_with_config_file(self, tmp_path):
        """Create policy engine from YAML config"""
        config_file = tmp_path / "policy.yaml"
        config_file.write_text("""
resource_policy:
  max_swarms_per_task: 5
  max_cost_per_task: 25.0
  min_capability_match: 0.8
  circuit_breaker_failure_threshold: 5
  enable_budget_enforcement: true
  enable_reputation_scoring: true
""")

        engine = PolicyEngine(config_path=str(config_file))

        assert engine.policy.max_swarms_per_task == 5
        assert engine.policy.max_cost_per_task == 25.0
        assert engine.policy.min_capability_match == 0.8
        assert engine.policy.circuit_breaker_failure_threshold == 5

    def test_config_file_not_found(self):
        """Non-existent config file raises error"""
        with pytest.raises(FileNotFoundError):
            PolicyEngine(config_path="/nonexistent/policy.yaml")

    def test_empty_yaml_config(self, tmp_path):
        """Empty YAML config raises error"""
        config_file = tmp_path / "empty.yaml"
        config_file.write_text("")

        with pytest.raises(ValueError, match="Empty YAML"):
            PolicyEngine(config_path=str(config_file))

    def test_invalid_yaml_syntax(self, tmp_path):
        """Invalid YAML syntax raises error"""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("{ invalid yaml syntax")

        with pytest.raises(yaml.YAMLError):
            PolicyEngine(config_path=str(config_file))


class TestAssignmentValidation:
    """Test task assignment validation"""

    def test_valid_assignment(self):
        """Valid assignment passes validation"""
        engine = PolicyEngine()

        valid, reason = engine.validate_assignment(
            swarm_ids=["session-1", "session-2"],
            task_budget=5.0,
            task_id="task-123"
        )

        assert valid is True
        assert reason is None
        assert len(engine.violations) == 0

    def test_max_swarms_exceeded(self):
        """Assignment with too many swarms fails"""
        engine = PolicyEngine()
        engine.policy.max_swarms_per_task = 2

        valid, reason = engine.validate_assignment(
            swarm_ids=["s1", "s2", "s3"],
            task_budget=5.0,
            task_id="task-123"
        )

        assert valid is False
        assert "Too many swarms" in reason
        assert len(engine.violations) == 1
        assert engine.violations[0].violation_type == "max_swarms_exceeded"

    def test_budget_exceeded(self):
        """Assignment with excessive budget fails"""
        engine = PolicyEngine()
        engine.policy.max_cost_per_task = 10.0

        valid, reason = engine.validate_assignment(
            swarm_ids=["s1"],
            task_budget=15.0,
            task_id="task-123"
        )

        assert valid is False
        assert "budget" in reason.lower()
        assert "15.00" in reason
        assert len(engine.violations) == 1
        assert engine.violations[0].violation_type == "budget_exceeded"

    def test_duplicate_swarms(self):
        """Assignment with duplicate swarms fails"""
        engine = PolicyEngine()

        valid, reason = engine.validate_assignment(
            swarm_ids=["s1", "s1"],
            task_budget=5.0
        )

        assert valid is False
        assert "Duplicate" in reason

    def test_empty_assignment(self):
        """Empty assignment fails"""
        engine = PolicyEngine()

        valid, reason = engine.validate_assignment(
            swarm_ids=[],
            task_budget=5.0
        )

        assert valid is False
        assert "No swarms" in reason

    def test_single_swarm_assignment(self):
        """Single swarm assignment is valid"""
        engine = PolicyEngine()

        valid, reason = engine.validate_assignment(
            swarm_ids=["session-4-sip"],
            task_budget=2.0
        )

        assert valid is True
        assert reason is None

    def test_max_swarms_at_limit(self):
        """Assignment at max swarms limit is valid"""
        engine = PolicyEngine()
        engine.policy.max_swarms_per_task = 3

        valid, reason = engine.validate_assignment(
            swarm_ids=["s1", "s2", "s3"],
            task_budget=5.0
        )

        assert valid is True

    def test_budget_at_limit(self):
        """Assignment at budget limit is valid"""
        engine = PolicyEngine()
        engine.policy.max_cost_per_task = 10.0

        valid, reason = engine.validate_assignment(
            swarm_ids=["s1"],
            task_budget=10.0
        )

        assert valid is True


class TestCapabilityMatching:
    """Test capability matching validation"""

    def test_perfect_match(self):
        """100% capability match meets threshold"""
        engine = PolicyEngine()

        meets_threshold, score = engine.validate_capability_match(
            required_capabilities=[Capability.INTEGRATION_SIP],
            swarm_capabilities=[Capability.INTEGRATION_SIP, Capability.ARCHITECTURE_SECURITY]
        )

        assert meets_threshold is True
        assert score == 1.0  # 1/1 required capabilities matched

    def test_partial_match_above_threshold(self):
        """Partial match above 70% threshold passes"""
        engine = PolicyEngine()
        engine.policy.min_capability_match = 0.5  # 50% threshold

        meets_threshold, score = engine.validate_capability_match(
            required_capabilities=[
                Capability.INTEGRATION_SIP,
                Capability.ARCHITECTURE_SECURITY
            ],
            swarm_capabilities=[
                Capability.INTEGRATION_SIP
            ]
        )

        assert meets_threshold is True
        assert score == 0.5  # 1/2 required capabilities matched

    def test_partial_match_below_threshold(self):
        """Partial match below 70% threshold fails"""
        engine = PolicyEngine()
        engine.policy.min_capability_match = 0.7  # 70% threshold

        meets_threshold, score = engine.validate_capability_match(
            required_capabilities=[
                Capability.INTEGRATION_SIP,
                Capability.ARCHITECTURE_SECURITY,
                Capability.TESTING_INTEGRATION
            ],
            swarm_capabilities=[
                Capability.INTEGRATION_SIP
            ]
        )

        assert meets_threshold is False
        assert score < 0.7  # 1/3 = 0.33

    def test_no_match(self):
        """No capability overlap fails"""
        engine = PolicyEngine()

        meets_threshold, score = engine.validate_capability_match(
            required_capabilities=[Capability.INTEGRATION_SIP],
            swarm_capabilities=[Capability.INTEGRATION_NDI]
        )

        assert meets_threshold is False
        assert score == 0.0

    def test_no_requirements(self):
        """No requirements = perfect match"""
        engine = PolicyEngine()

        meets_threshold, score = engine.validate_capability_match(
            required_capabilities=[],
            swarm_capabilities=[Capability.INTEGRATION_SIP]
        )

        assert meets_threshold is True
        assert score == 1.0

    def test_no_capabilities(self):
        """No capabilities = no match"""
        engine = PolicyEngine()

        meets_threshold, score = engine.validate_capability_match(
            required_capabilities=[Capability.INTEGRATION_SIP],
            swarm_capabilities=[]
        )

        assert meets_threshold is False
        assert score == 0.0

    def test_multiple_capabilities_full_match(self):
        """Multiple required capabilities all matched"""
        engine = PolicyEngine()

        meets_threshold, score = engine.validate_capability_match(
            required_capabilities=[
                Capability.INTEGRATION_SIP,
                Capability.ARCHITECTURE_SECURITY,
                Capability.INFRA_NETWORKING
            ],
            swarm_capabilities=[
                Capability.INTEGRATION_SIP,
                Capability.ARCHITECTURE_SECURITY,
                Capability.INFRA_NETWORKING,
                Capability.DOCS_TECHNICAL_WRITING
            ]
        )

        assert meets_threshold is True
        assert score == 1.0  # 3/3 required matched


class TestBudgetLimits:
    """Test budget limit checks"""

    def test_sufficient_budget(self):
        """Swarm with positive budget passes"""
        engine = PolicyEngine()

        has_budget, reason = engine.check_budget_limit(
            swarm_id="session-4-sip",
            remaining_budget=10.44
        )

        assert has_budget is True
        assert reason is None

    def test_zero_budget(self):
        """Swarm with zero budget fails"""
        engine = PolicyEngine()

        has_budget, reason = engine.check_budget_limit(
            swarm_id="session-4-sip",
            remaining_budget=0.0
        )

        assert has_budget is False
        assert "exhausted" in reason

    def test_negative_budget(self):
        """Swarm with negative budget fails"""
        engine = PolicyEngine()

        has_budget, reason = engine.check_budget_limit(
            swarm_id="session-4-sip",
            remaining_budget=-5.0
        )

        assert has_budget is False
        assert "exhausted" in reason

    def test_budget_enforcement_disabled(self):
        """Budget check passes when enforcement disabled"""
        engine = PolicyEngine()
        engine.policy.enable_budget_enforcement = False

        has_budget, reason = engine.check_budget_limit(
            swarm_id="session-4-sip",
            remaining_budget=0.0
        )

        assert has_budget is True
        assert reason is None


class TestViolationTracking:
    """Test policy violation tracking"""

    def test_violations_recorded(self):
        """Violations are recorded and retrievable"""
        engine = PolicyEngine()

        # Trigger max_swarms violation
        engine.validate_assignment(
            swarm_ids=["s1", "s2", "s3", "s4"],
            task_budget=5.0,
            task_id="task-1"
        )

        # Trigger budget violation
        engine.validate_assignment(
            swarm_ids=["s1"],
            task_budget=20.0,
            task_id="task-2"
        )

        assert len(engine.violations) == 2

    def test_get_violations_by_type(self):
        """Filter violations by type"""
        engine = PolicyEngine()

        # Create multiple violations
        engine.validate_assignment(swarm_ids=["s1", "s2", "s3", "s4"], task_budget=5.0)
        engine.validate_assignment(swarm_ids=["s1"], task_budget=20.0)
        engine.validate_assignment(swarm_ids=["s1", "s2", "s3", "s4"], task_budget=5.0)

        max_swarms_violations = engine.get_violations(violation_type="max_swarms_exceeded")
        budget_violations = engine.get_violations(violation_type="budget_exceeded")

        assert len(max_swarms_violations) == 2
        assert len(budget_violations) == 1

    def test_get_violations_by_swarm(self):
        """Filter violations by swarm ID"""
        engine = PolicyEngine()

        engine.validate_assignment(swarm_ids=["s1", "s2", "s3", "s4"], task_budget=5.0)
        engine.validate_assignment(swarm_ids=["s5"], task_budget=20.0)

        s1_violations = engine.get_violations(swarm_id="s1")
        s5_violations = engine.get_violations(swarm_id="s5")

        assert len(s1_violations) == 1
        assert len(s5_violations) == 1

    def test_violation_to_dict(self):
        """PolicyViolation converts to dict"""
        violation = PolicyViolation(
            violation_type="test_violation",
            swarm_id="s1",
            task_id="task-1",
            details={"key": "value"},
            timestamp=1234567890.0
        )

        data = violation.to_dict()

        assert data["violation_type"] == "test_violation"
        assert data["swarm_id"] == "s1"
        assert data["task_id"] == "task-1"
        assert data["details"]["key"] == "value"


class TestPolicySummary:
    """Test policy summary and reporting"""

    def test_get_policy_summary(self):
        """Get policy summary with statistics"""
        engine = PolicyEngine()

        # Create some violations
        engine.validate_assignment(swarm_ids=["s1", "s2", "s3", "s4"], task_budget=5.0)
        engine.validate_assignment(swarm_ids=["s1"], task_budget=20.0)

        summary = engine.get_policy_summary()

        assert "policy" in summary
        assert "violations" in summary
        assert summary["violations"]["total"] == 2
        assert "by_type" in summary["violations"]

    def test_violations_export_json(self, tmp_path):
        """Export violations to JSON file"""
        engine = PolicyEngine()

        # Create violations
        engine.validate_assignment(swarm_ids=["s1", "s2", "s3", "s4"], task_budget=5.0)

        output_file = tmp_path / "violations.json"
        engine.export_violations_json(str(output_file))

        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert "policy" in data
        assert "violations" in data
        assert "summary" in data
        assert len(data["violations"]) == 1


class TestCapabilityExtraction:
    """Test capability extraction helper"""

    def test_extract_explicit_capabilities(self):
        """Extract capabilities from required_skills"""
        blocker = {
            "required_skills": ["integration:sip", "architecture:security"]
        }

        caps = extract_required_capabilities(blocker)

        assert Capability.INTEGRATION_SIP in caps
        assert Capability.ARCHITECTURE_SECURITY in caps
        assert len(caps) == 2

    def test_extract_from_error_type(self):
        """Infer capabilities from error_type"""
        blocker = {
            "error_type": "security_issue"
        }

        caps = extract_required_capabilities(blocker)

        assert Capability.ARCHITECTURE_SECURITY in caps

    def test_extract_combined(self):
        """Extract from both explicit and inferred"""
        blocker = {
            "error_type": "integration_failure",
            "required_skills": ["integration:sip"]
        }

        caps = extract_required_capabilities(blocker)

        assert Capability.INTEGRATION_SIP in caps
        assert Capability.INFRA_DISTRIBUTED_SYSTEMS in caps

    def test_extract_unknown_error_type(self):
        """Unknown error type returns only explicit skills"""
        blocker = {
            "error_type": "unknown_error",
            "required_skills": ["integration:sip"]
        }

        caps = extract_required_capabilities(blocker)

        assert Capability.INTEGRATION_SIP in caps
        assert len(caps) == 1

    def test_extract_no_duplicates(self):
        """Duplicate capabilities are removed"""
        blocker = {
            "required_skills": ["integration:sip", "integration:sip"]
        }

        caps = extract_required_capabilities(blocker)

        assert len(caps) == 1
        assert caps[0] == Capability.INTEGRATION_SIP

    def test_extract_invalid_capability(self):
        """Invalid capability strings are ignored"""
        blocker = {
            "required_skills": ["integration:sip", "invalid:capability"]
        }

        caps = extract_required_capabilities(blocker)

        assert len(caps) == 1
        assert caps[0] == Capability.INTEGRATION_SIP

    def test_error_capability_mappings(self):
        """Test all error type mappings"""
        test_cases = [
            ("integration_failure", Capability.INFRA_DISTRIBUTED_SYSTEMS),
            ("security_issue", Capability.ARCHITECTURE_SECURITY),
            ("performance_degradation", Capability.ARCHITECTURE_PERFORMANCE),
            ("test_failure", Capability.TESTING_INTEGRATION),
            ("documentation_gap", Capability.DOCS_TECHNICAL_WRITING),
        ]

        for error_type, expected_cap in test_cases:
            blocker = {"error_type": error_type}
            caps = extract_required_capabilities(blocker)
            assert expected_cap in caps, f"Failed for error_type: {error_type}"


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""

    def test_session_4_sip_assignment(self):
        """Session 4 (SIP) valid assignment scenario"""
        engine = PolicyEngine()

        # Session 4 gets assigned integration:sip task
        valid, reason = engine.validate_assignment(
            swarm_ids=["session-4-sip"],
            task_budget=2.0,  # Haiku cost
            task_id="sip-integration-123"
        )

        assert valid is True

        # Check capability match
        meets_threshold, score = engine.validate_capability_match(
            required_capabilities=[Capability.INTEGRATION_SIP],
            swarm_capabilities=[
                Capability.INTEGRATION_SIP,
                Capability.ARCHITECTURE_SECURITY,
                Capability.INFRA_NETWORKING
            ]
        )

        assert meets_threshold is True
        assert score == 1.0

    def test_gang_up_on_blocker_scenario(self):
        """Multiple swarms collaborate on blocker"""
        engine = PolicyEngine()
        engine.policy.max_swarms_per_task = 3

        # 3 sessions collaborate on security issue
        valid, reason = engine.validate_assignment(
            swarm_ids=["session-1", "session-4", "session-7"],
            task_budget=8.0,
            task_id="security-blocker"
        )

        assert valid is True

        # Extract capabilities from blocker
        blocker = {
            "error_type": "security_issue",
            "required_skills": ["architecture:security", "testing:security"]
        }

        caps = extract_required_capabilities(blocker)
        assert Capability.ARCHITECTURE_SECURITY in caps
        assert Capability.TESTING_SECURITY in caps

    def test_budget_circuit_breaker_scenario(self):
        """Budget exhaustion prevents assignment"""
        engine = PolicyEngine()

        # Swarm with exhausted budget
        has_budget, reason = engine.check_budget_limit(
            swarm_id="session-x",
            remaining_budget=0.0
        )

        assert has_budget is False
        assert "exhausted" in reason


# Run tests with: pytest tests/unit/test_policy_engine.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
