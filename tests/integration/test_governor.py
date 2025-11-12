"""Integration tests for P0.2.6 - IF.governor End-to-End

This test suite validates IF.governor functionality end-to-end, testing how
all components (capability matching, budget tracking, circuit breakers, policy
engine) work together in realistic scenarios.

Philosophy:
- IF.TTT Trustworthy: Integration tests verify real-world behavior
- IF.ground Observable: Test scenarios mirror production workflows
- Wu Lun (朋友): Fair resource allocation across peer swarms

Test Coverage:
- Capability-based task assignment
- Budget enforcement with circuit breakers
- Policy engine integration
- Multiple swarms competing for tasks
- Cost optimization scenarios
- Realistic S² workflows
"""

import pytest
from infrafabric.governor import IFGovernor
from infrafabric.schemas.capability import SwarmProfile, ResourcePolicy, Capability
from infrafabric.policies import PolicyEngine


class TestCapabilityMatching:
    """Test end-to-end capability matching"""

    def test_perfect_capability_match_assignment(self):
        """Test swarm selection with perfect capability match"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        # Register swarms with different capabilities
        governor.register_swarm(SwarmProfile(
            swarm_id='session-1-ndi',
            capabilities=[Capability.INTEGRATION_NDI, Capability.DOCS_TECHNICAL_WRITING],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.0,
            model='haiku'
        ))

        governor.register_swarm(SwarmProfile(
            swarm_id='session-4-sip',
            capabilities=[Capability.INTEGRATION_SIP, Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.90,
            current_budget_remaining=10.0,
            model='sonnet'
        ))

        # Find swarm for SIP task
        swarm = governor.find_qualified_swarm(
            required_capabilities=[Capability.INTEGRATION_SIP],
            max_cost=5.0
        )

        assert swarm == 'session-4-sip'

    def test_multiple_qualified_swarms_chooses_best(self):
        """Test that best-scoring swarm is chosen when multiple qualify"""
        governor = IFGovernor(coordinator=None)

        # Register three swarms with varying stats
        governor.register_swarm(SwarmProfile(
            "expensive", [Capability.INTEGRATION_SIP],
            20.0, 1.0, 10.0, "opus"  # Expensive but perfect reputation
        ))
        governor.register_swarm(SwarmProfile(
            "cheap", [Capability.INTEGRATION_SIP],
            1.5, 0.95, 10.0, "haiku"  # Cheap with good reputation
        ))
        governor.register_swarm(SwarmProfile(
            "mediocre", [Capability.INTEGRATION_SIP],
            5.0, 0.80, 10.0, "sonnet"  # Mid-range
        ))

        # Cheap should win: (1.0 * 0.95) / 1.5 = 0.633 > others
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=25.0)
        assert result == "cheap"


class TestBudgetEnforcementIntegration:
    """Test budget enforcement with circuit breakers"""

    def test_budget_exhaustion_triggers_circuit_breaker(self):
        """Test that exhausting budget trips circuit breaker automatically"""
        governor = IFGovernor(coordinator=None)
        governor.register_swarm(SwarmProfile(
            "test-swarm",
            [Capability.INTEGRATION_SIP],
            2.0, 0.95, 10.0, "sonnet"
        ))

        # Verify swarm is initially assignable
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result == "test-swarm"

        # Exhaust budget
        governor.track_cost("test-swarm", "expensive_operation", 15.0)

        # Circuit breaker should be tripped
        assert "test-swarm" in governor.circuit_breaker_tripped

        # Swarm should no longer be assignable
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result is None

        # Budget report should show zero/negative
        report = governor.get_budget_report()
        assert report["test-swarm"] <= 0

    def test_circuit_breaker_recovery_workflow(self):
        """Test complete circuit breaker trip and recovery workflow"""
        governor = IFGovernor(coordinator=None)
        governor.register_swarm(SwarmProfile(
            "recoverable-swarm",
            [Capability.INTEGRATION_SIP],
            2.0, 0.95, 5.0, "sonnet"
        ))

        # 1. Normal operation
        assert governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0) == "recoverable-swarm"

        # 2. Trip circuit breaker
        governor.track_cost("recoverable-swarm", "op", 10.0)
        assert "recoverable-swarm" in governor.circuit_breaker_tripped
        assert governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0) is None

        # 3. Manual recovery
        governor.reset_circuit_breaker("recoverable-swarm", new_budget=20.0)
        assert "recoverable-swarm" not in governor.circuit_breaker_tripped

        # 4. Restored operation
        assert governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0) == "recoverable-swarm"
        profile = governor.get_swarm_profile("recoverable-swarm")
        assert profile.current_budget_remaining == 20.0


class TestPolicyEngineIntegration:
    """Test policy engine integration with governor"""

    def test_policy_engine_validates_governor_decisions(self):
        """Test that policy engine validates governor's assignment decisions"""
        policy_engine = PolicyEngine()
        governor = IFGovernor(coordinator=None, policy=policy_engine.policy)

        # Register swarms
        governor.register_swarm(SwarmProfile(
            "swarm-1", [Capability.INTEGRATION_SIP],
            2.0, 0.95, 10.0, "sonnet"
        ))
        governor.register_swarm(SwarmProfile(
            "swarm-2", [Capability.INTEGRATION_NDI],
            1.5, 0.90, 15.0, "haiku"
        ))

        # Find qualified swarm
        swarm_id = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)

        # Policy engine should validate this assignment
        profile = governor.get_swarm_profile(swarm_id)
        valid, match_score = policy_engine.validate_capability_match(
            [Capability.INTEGRATION_SIP],
            profile.capabilities
        )
        assert valid is True
        assert match_score >= 0.7

    def test_policy_violations_prevented(self):
        """Test that policy violations are prevented"""
        # Custom strict policy
        strict_policy = ResourcePolicy(
            max_swarms_per_task=1,
            max_cost_per_task=5.0,
            min_capability_match=0.9  # 90% match required
        )
        policy_engine = PolicyEngine()  # Uses default policy
        governor = IFGovernor(coordinator=None, policy=strict_policy)

        # Register swarm with partial match (80%)
        governor.register_swarm(SwarmProfile(
            "partial-match",
            [Capability.INTEGRATION_SIP, Capability.INTEGRATION_H323,
             Capability.CODE_ANALYSIS_PYTHON, Capability.DOCS_TECHNICAL_WRITING],
            2.0, 0.95, 10.0, "sonnet"
        ))

        # Require 5 capabilities (only has 4 = 80% match)
        required_caps = [
            Capability.INTEGRATION_SIP,
            Capability.INTEGRATION_H323,
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.DOCS_TECHNICAL_WRITING,
            Capability.INTEGRATION_WEBRTC  # Missing
        ]

        # Should fail due to <90% match
        result = governor.find_qualified_swarm(required_caps, max_cost=5.0)
        assert result is None


class TestRealisticScenarios:
    """Test realistic S² scenarios"""

    def test_session_4_sip_integration_workflow(self):
        """Test realistic Session 4 SIP integration workflow"""
        governor = IFGovernor(coordinator=None)

        # Register Session 4 swarm
        governor.register_swarm(SwarmProfile(
            swarm_id="session-4-sip",
            capabilities=[
                Capability.INTEGRATION_SIP,
                Capability.INTEGRATION_H323,
                Capability.ARCHITECTURE_SECURITY,
                Capability.CODE_ANALYSIS_PYTHON,
            ],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.44,  # Real remaining budget
            model="sonnet"
        ))

        # Task 1: SIP integration (should succeed)
        swarm = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert swarm == "session-4-sip"
        governor.track_cost("session-4-sip", "sip_integration", 2.0)

        # Task 2: H.323 gateway (should succeed)
        swarm = governor.find_qualified_swarm([Capability.INTEGRATION_H323], max_cost=5.0)
        assert swarm == "session-4-sip"
        governor.track_cost("session-4-sip", "h323_gateway", 3.0)

        # Task 3: Security audit (should succeed)
        swarm = governor.find_qualified_swarm([Capability.ARCHITECTURE_SECURITY], max_cost=5.0)
        assert swarm == "session-4-sip"
        governor.track_cost("session-4-sip", "security_audit", 4.0)

        # Task 4: Code review (should succeed)
        swarm = governor.find_qualified_swarm([Capability.CODE_ANALYSIS_PYTHON], max_cost=5.0)
        assert swarm == "session-4-sip"
        governor.track_cost("session-4-sip", "code_review", 2.0)

        # Budget should now be exhausted (10.44 - 11.0 = -0.56)
        profile = governor.get_swarm_profile("session-4-sip")
        assert profile.current_budget_remaining < 0

        # Circuit breaker should be tripped
        assert "session-4-sip" in governor.circuit_breaker_tripped

        # Task 5: Should fail (no budget)
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result is None

    def test_multi_session_task_distribution(self):
        """Test task distribution across multiple sessions"""
        governor = IFGovernor(coordinator=None)

        # Register all sessions
        sessions = [
            ("session-1-ndi", [Capability.INTEGRATION_NDI], 1.5, 0.90, 15.0, "haiku"),
            ("session-2-webrtc", [Capability.INTEGRATION_WEBRTC], 2.0, 0.92, 12.0, "sonnet"),
            ("session-3-h323", [Capability.INTEGRATION_H323], 1.8, 0.88, 18.0, "haiku"),
            ("session-4-sip", [Capability.INTEGRATION_SIP], 2.0, 0.95, 10.44, "sonnet"),
        ]

        for swarm_id, caps, cost, rep, budget, model in sessions:
            governor.register_swarm(SwarmProfile(swarm_id, caps, cost, rep, budget, model))

        # Distribute tasks to appropriate sessions
        tasks = [
            ([Capability.INTEGRATION_NDI], "session-1-ndi"),
            ([Capability.INTEGRATION_WEBRTC], "session-2-webrtc"),
            ([Capability.INTEGRATION_H323], "session-3-h323"),
            ([Capability.INTEGRATION_SIP], "session-4-sip"),
        ]

        for required_caps, expected_swarm in tasks:
            result = governor.find_qualified_swarm(required_caps, max_cost=5.0)
            assert result == expected_swarm

    def test_cost_optimization_scenario(self):
        """Test that governor optimizes for cost when capabilities equal"""
        governor = IFGovernor(coordinator=None)

        # Register three swarms with same capabilities but different costs
        governor.register_swarm(SwarmProfile(
            "haiku-swarm", [Capability.CODE_ANALYSIS_PYTHON],
            1.5, 0.90, 10.0, "haiku"  # Cheapest
        ))
        governor.register_swarm(SwarmProfile(
            "sonnet-swarm", [Capability.CODE_ANALYSIS_PYTHON],
            15.0, 0.95, 10.0, "sonnet"  # Mid-range
        ))
        governor.register_swarm(SwarmProfile(
            "opus-swarm", [Capability.CODE_ANALYSIS_PYTHON],
            75.0, 1.0, 10.0, "opus"  # Most expensive
        ))

        # Should choose haiku despite lower reputation (best cost/value)
        result = governor.find_qualified_swarm([Capability.CODE_ANALYSIS_PYTHON], max_cost=100.0)
        assert result == "haiku-swarm"


class TestFailureScenarios:
    """Test failure and edge case scenarios"""

    def test_no_qualified_swarms_available(self):
        """Test behavior when no swarms meet requirements"""
        governor = IFGovernor(coordinator=None)

        governor.register_swarm(SwarmProfile(
            "wrong-capability", [Capability.INTEGRATION_NDI],
            2.0, 0.95, 10.0, "sonnet"
        ))

        # Request SIP capability (not available)
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result is None

    def test_all_swarms_over_budget(self):
        """Test when all swarms are too expensive"""
        governor = IFGovernor(coordinator=None)

        governor.register_swarm(SwarmProfile(
            "expensive", [Capability.INTEGRATION_SIP],
            100.0, 0.95, 10.0, "opus"
        ))

        # Max cost too low
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result is None

    def test_all_swarms_budget_exhausted(self):
        """Test when all qualified swarms have exhausted budgets"""
        governor = IFGovernor(coordinator=None)

        # Register multiple swarms
        for i in range(3):
            governor.register_swarm(SwarmProfile(
                f"swarm-{i}", [Capability.INTEGRATION_SIP],
                2.0, 0.95, 10.0, "sonnet"
            ))
            # Exhaust each budget
            governor.track_cost(f"swarm-{i}", "expensive_op", 15.0)

        # All should be circuit breaker tripped
        for i in range(3):
            assert f"swarm-{i}" in governor.circuit_breaker_tripped

        # Should return None
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result is None


class TestStatefulBehavior:
    """Test stateful behavior across multiple operations"""

    def test_sequential_task_assignments(self):
        """Test multiple sequential task assignments"""
        governor = IFGovernor(coordinator=None)

        governor.register_swarm(SwarmProfile(
            "worker", [Capability.CODE_ANALYSIS_PYTHON],
            2.0, 0.95, 20.0, "sonnet"
        ))

        # Assign 5 tasks sequentially
        for i in range(5):
            result = governor.find_qualified_swarm([Capability.CODE_ANALYSIS_PYTHON], max_cost=5.0)
            assert result == "worker"
            governor.track_cost("worker", f"task-{i}", 3.0)

        # After 5 tasks (15 total cost), should still have budget
        profile = governor.get_swarm_profile("worker")
        assert profile.current_budget_remaining == 5.0

        # One more task should work
        result = governor.find_qualified_swarm([Capability.CODE_ANALYSIS_PYTHON], max_cost=5.0)
        assert result == "worker"
        governor.track_cost("worker", "final-task", 4.0)

        # Budget now at 1.0 (20 - 19 = 1.0), still assignable
        profile = governor.get_swarm_profile("worker")
        assert profile.current_budget_remaining == 1.0

        # One more task exhausts budget
        result = governor.find_qualified_swarm([Capability.CODE_ANALYSIS_PYTHON], max_cost=5.0)
        assert result == "worker"
        governor.track_cost("worker", "final-final-task", 2.0)

        # Now budget exhausted (-1.0) and circuit breaker tripped
        result = governor.find_qualified_swarm([Capability.CODE_ANALYSIS_PYTHON], max_cost=5.0)
        assert result is None
        assert "worker" in governor.circuit_breaker_tripped

    def test_assignment_history_tracking(self):
        """Test that assignment history is properly tracked"""
        governor = IFGovernor(coordinator=None)

        governor.register_swarm(SwarmProfile(
            "tracked", [Capability.INTEGRATION_SIP],
            2.0, 0.95, 20.0, "sonnet"
        ))

        # Make 3 assignments
        for i in range(3):
            governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)

        # Check history
        history = governor.get_assignment_history()
        assert len(history) == 3
        assert all(h['swarm_id'] == "tracked" for h in history)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
