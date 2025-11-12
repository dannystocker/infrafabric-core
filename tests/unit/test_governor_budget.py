"""Unit tests for P0.2.3 - Budget Tracking and Enforcement

This test suite validates budget tracking and enforcement for IF.governor.
Budget limits prevent cost spirals and ensure fair resource allocation.

Philosophy:
- IF.TTT Trustworthy: Hard budget limits prevent runaway costs
- IF.ground Observable: All cost tracking is auditable
- Wu Lun (朋友): Fair budget allocation across peer swarms

Test Coverage:
- Cost tracking and deduction
- Budget exhaustion detection
- Budget reports
- Integration with find_qualified_swarm
"""

import pytest
from infrafabric.governor import IFGovernor
from infrafabric.schemas.capability import Capability, SwarmProfile, ResourcePolicy


class TestBudgetTracking:
    """Test budget tracking functionality"""

    @pytest.fixture
    def governor(self):
        """Create governor with swarm"""
        gov = IFGovernor()
        gov.register_swarm(SwarmProfile(
            swarm_id="session-4-sip",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.0,
            model="sonnet"
        ))
        return gov

    def test_track_cost_deducts_from_budget(self, governor):
        """Test that tracking cost deducts from remaining budget"""
        governor.track_cost("session-4-sip", "sip_integration", 2.5)

        profile = governor.get_swarm_profile("session-4-sip")
        assert profile.current_budget_remaining == pytest.approx(7.5, rel=0.01)

    def test_track_cost_multiple_operations(self, governor):
        """Test tracking multiple costs"""
        governor.track_cost("session-4-sip", "operation_1", 1.0)
        governor.track_cost("session-4-sip", "operation_2", 2.0)
        governor.track_cost("session-4-sip", "operation_3", 1.5)

        profile = governor.get_swarm_profile("session-4-sip")
        assert profile.current_budget_remaining == pytest.approx(5.5, rel=0.01)

    def test_track_cost_unknown_swarm_raises_error(self, governor):
        """Test tracking cost for unknown swarm raises ValueError"""
        with pytest.raises(ValueError, match="Unknown swarm"):
            governor.track_cost("unknown-swarm", "operation", 1.0)

    def test_track_cost_zero_cost(self, governor):
        """Test tracking zero cost (no-op)"""
        governor.track_cost("session-4-sip", "free_operation", 0.0)

        profile = governor.get_swarm_profile("session-4-sip")
        assert profile.current_budget_remaining == 10.0

    def test_track_cost_fractional_amounts(self, governor):
        """Test tracking fractional costs"""
        governor.track_cost("session-4-sip", "small_op", 0.123)

        profile = governor.get_swarm_profile("session-4-sip")
        assert profile.current_budget_remaining == pytest.approx(9.877, rel=0.001)


class TestBudgetExhaustion:
    """Test budget exhaustion detection"""

    @pytest.fixture
    def governor(self):
        """Create governor with low-budget swarm"""
        gov = IFGovernor()
        gov.register_swarm(SwarmProfile(
            swarm_id="low-budget",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=1.0,
            model="sonnet"
        ))
        return gov

    def test_budget_exhaustion_sets_zero(self, governor):
        """Test that exhausting budget sets remaining to zero or negative"""
        governor.track_cost("low-budget", "expensive_op", 1.5)

        profile = governor.get_swarm_profile("low-budget")
        assert profile.current_budget_remaining <= 0

    def test_exhausted_swarm_excluded_from_matching(self):
        """Test that swarms with exhausted budgets are excluded from matching"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "broke-swarm",
            [Capability.INTEGRATION_SIP],
            2.0, 0.95, 5.0, "sonnet"
        ))

        # Exhaust budget
        governor.track_cost("broke-swarm", "big_operation", 6.0)

        # Try to find qualified swarm
        result = governor.find_qualified_swarm(
            [Capability.INTEGRATION_SIP],
            max_cost=5.0
        )

        # Should return None (no qualified swarms)
        assert result is None

    def test_negative_budget_persists(self, governor):
        """Test that budget can go negative"""
        governor.track_cost("low-budget", "huge_op", 10.0)

        profile = governor.get_swarm_profile("low-budget")
        assert profile.current_budget_remaining == pytest.approx(-9.0, rel=0.01)


class TestBudgetReports:
    """Test budget reporting"""

    def test_get_budget_report_single_swarm(self):
        """Test getting budget report for single swarm"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "session-4", [Capability.INTEGRATION_SIP],
            2.0, 0.95, 10.0, "sonnet"
        ))

        report = governor.get_budget_report()

        assert "session-4" in report
        assert report["session-4"] == 10.0

    def test_get_budget_report_multiple_swarms(self):
        """Test getting budget report for multiple swarms"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile("s1", [Capability.INTEGRATION_SIP], 2.0, 0.95, 10.0, "sonnet"))
        governor.register_swarm(SwarmProfile("s2", [Capability.INTEGRATION_NDI], 1.5, 0.90, 15.0, "haiku"))
        governor.register_swarm(SwarmProfile("s3", [Capability.INTEGRATION_H323], 1.8, 0.88, 8.0, "haiku"))

        report = governor.get_budget_report()

        assert len(report) == 3
        assert report["s1"] == 10.0
        assert report["s2"] == 15.0
        assert report["s3"] == 8.0

    def test_get_budget_report_after_costs(self):
        """Test budget report reflects tracked costs"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile("s1", [Capability.INTEGRATION_SIP], 2.0, 0.95, 10.0, "sonnet"))

        governor.track_cost("s1", "op1", 3.0)
        governor.track_cost("s1", "op2", 2.0)

        report = governor.get_budget_report()
        assert report["s1"] == pytest.approx(5.0, rel=0.01)

    def test_get_budget_report_empty(self):
        """Test budget report when no swarms registered"""
        governor = IFGovernor()
        report = governor.get_budget_report()

        assert report == {}


class TestBudgetIntegration:
    """Test budget tracking integration with other features"""

    def test_budget_prevents_assignment_after_exhaustion(self):
        """Test that exhausted budget prevents new assignments"""
        governor = IFGovernor()

        # Register two swarms
        governor.register_swarm(SwarmProfile(
            "healthy-swarm",
            [Capability.INTEGRATION_SIP],
            2.0, 0.95, 10.0, "sonnet"
        ))
        governor.register_swarm(SwarmProfile(
            "broke-swarm",
            [Capability.INTEGRATION_SIP, Capability.INTEGRATION_H323],
            2.0, 1.0,  # Higher reputation
            5.0, "sonnet"
        ))

        # Exhaust broke-swarm's budget
        governor.track_cost("broke-swarm", "expensive_operation", 6.0)

        # Find qualified swarm
        result = governor.find_qualified_swarm(
            [Capability.INTEGRATION_SIP],
            max_cost=5.0
        )

        # Should get healthy-swarm, not broke-swarm despite higher reputation
        assert result == "healthy-swarm"

    def test_budget_updates_reflect_in_profile(self):
        """Test that budget updates are reflected in swarm profile"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "test-swarm", [Capability.INTEGRATION_SIP],
            2.0, 0.95, 10.0, "sonnet"
        ))

        # Track multiple costs
        costs = [1.0, 2.5, 0.75, 1.25]
        for i, cost in enumerate(costs):
            governor.track_cost("test-swarm", f"op{i}", cost)

        # Get profile
        profile = governor.get_swarm_profile("test-swarm")

        # Should reflect all costs
        expected_remaining = 10.0 - sum(costs)
        assert profile.current_budget_remaining == pytest.approx(expected_remaining, rel=0.01)

    def test_concurrent_cost_tracking(self):
        """Test tracking costs for multiple swarms concurrently"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile("s1", [Capability.INTEGRATION_SIP], 2.0, 0.95, 10.0, "sonnet"))
        governor.register_swarm(SwarmProfile("s2", [Capability.INTEGRATION_NDI], 1.5, 0.90, 15.0, "haiku"))

        # Track costs for both swarms
        governor.track_cost("s1", "op1", 2.0)
        governor.track_cost("s2", "op1", 3.0)
        governor.track_cost("s1", "op2", 1.5)
        governor.track_cost("s2", "op2", 2.5)

        # Check budgets
        assert governor.get_swarm_profile("s1").current_budget_remaining == pytest.approx(6.5, rel=0.01)
        assert governor.get_swarm_profile("s2").current_budget_remaining == pytest.approx(9.5, rel=0.01)


class TestBudgetEdgeCases:
    """Test edge cases in budget tracking"""

    def test_large_cost_values(self):
        """Test tracking very large costs"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "big-budget", [Capability.INTEGRATION_SIP],
            2.0, 0.95, 1000.0, "opus"
        ))

        governor.track_cost("big-budget", "huge_op", 999.99)

        profile = governor.get_swarm_profile("big-budget")
        assert profile.current_budget_remaining == pytest.approx(0.01, rel=0.01)

    def test_very_small_cost_values(self):
        """Test tracking very small costs"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "test-swarm", [Capability.INTEGRATION_SIP],
            2.0, 0.95, 10.0, "sonnet"
        ))

        governor.track_cost("test-swarm", "tiny_op", 0.0001)

        profile = governor.get_swarm_profile("test-swarm")
        assert profile.current_budget_remaining == pytest.approx(9.9999, rel=0.0001)

    def test_budget_exactly_zero(self):
        """Test when budget reaches exactly zero"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "precise-swarm", [Capability.INTEGRATION_SIP],
            2.0, 0.95, 5.0, "sonnet"
        ))

        governor.track_cost("precise-swarm", "exact_op", 5.0)

        profile = governor.get_swarm_profile("precise-swarm")
        assert profile.current_budget_remaining == pytest.approx(0.0, abs=0.0001)

        # Should not be assignable
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=10.0)
        assert result is None


class TestSession4Integration:
    """Test Session 4 (SIP) budget tracking scenarios"""

    def test_session_4_budget_tracking(self):
        """Test budget tracking for Session 4 SIP integration"""
        governor = IFGovernor()

        # Register Session 4 swarm with realistic budget
        governor.register_swarm(SwarmProfile(
            swarm_id="session-4-sip",
            capabilities=[
                Capability.INTEGRATION_SIP,
                Capability.INTEGRATION_H323,
                Capability.ARCHITECTURE_SECURITY,
            ],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.44,  # Real remaining budget
            model="sonnet"
        ))

        # Track some SIP operations
        governor.track_cost("session-4-sip", "sip_call_handling", 0.50)
        governor.track_cost("session-4-sip", "h323_gateway", 0.75)

        profile = governor.get_swarm_profile("session-4-sip")
        assert profile.current_budget_remaining == pytest.approx(9.19, rel=0.01)

        # Should still be assignable
        result = governor.find_qualified_swarm(
            [Capability.INTEGRATION_SIP],
            max_cost=5.0
        )
        assert result == "session-4-sip"

    def test_realistic_multi_swarm_budget_scenario(self):
        """Test realistic scenario with multiple swarms and budget tracking"""
        governor = IFGovernor()

        # Register multiple session swarms
        swarms = [
            ("session-1-ndi", [Capability.INTEGRATION_NDI], 1.5, 0.90, 15.0, "haiku"),
            ("session-2-webrtc", [Capability.INTEGRATION_WEBRTC], 2.0, 0.92, 12.0, "sonnet"),
            ("session-3-h323", [Capability.INTEGRATION_H323], 1.8, 0.88, 18.0, "haiku"),
            ("session-4-sip", [Capability.INTEGRATION_SIP], 2.0, 0.95, 10.44, "sonnet"),
        ]

        for swarm_id, caps, cost, rep, budget, model in swarms:
            governor.register_swarm(SwarmProfile(swarm_id, caps, cost, rep, budget, model))

        # Track costs for various operations
        governor.track_cost("session-1-ndi", "ndi_stream", 2.0)
        governor.track_cost("session-2-webrtc", "webrtc_call", 3.0)
        governor.track_cost("session-4-sip", "sip_integration", 1.5)

        # Check budget report
        report = governor.get_budget_report()
        assert report["session-1-ndi"] == pytest.approx(13.0, rel=0.01)
        assert report["session-2-webrtc"] == pytest.approx(9.0, rel=0.01)
        assert report["session-3-h323"] == pytest.approx(18.0, rel=0.01)  # Unchanged
        assert report["session-4-sip"] == pytest.approx(8.94, rel=0.01)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
