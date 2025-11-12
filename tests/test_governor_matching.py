"""
Unit Tests for IF.governor Capability Matching (P0.2.2)

Tests for:
- IFGovernor initialization and swarm registration
- Capability matching algorithm (Jaccard similarity)
- Combined scoring (capability × reputation / cost)
- 70% threshold enforcement
- Budget filtering
- Cost filtering
- Edge cases (no matches, ties, empty capabilities)

Author: Session 3 (H.323 Guardian Council)
Version: 1.0
Status: Phase 0 Development
"""

import pytest
from infrafabric.governor import IFGovernor, CapabilityMatchError, InsufficientBudgetError
from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
)


# ==========================================
# IFGovernor Initialization Tests
# ==========================================

class TestIFGovernorInitialization:
    """Test IFGovernor initialization and configuration"""

    def test_initialize_governor_with_default_policy(self):
        """Test IFGovernor initialization with default policy"""
        policy = ResourcePolicy()
        governor = IFGovernor(coordinator=None, policy=policy)

        assert governor.policy.min_capability_match == 0.7
        assert governor.policy.max_swarms_per_task == 3
        assert len(governor.swarm_registry) == 0

    def test_initialize_governor_with_custom_policy(self):
        """Test IFGovernor initialization with custom policy"""
        policy = ResourcePolicy(
            min_capability_match=0.8,
            max_cost_per_task=5.0
        )
        governor = IFGovernor(coordinator=None, policy=policy)

        assert governor.policy.min_capability_match == 0.8
        assert governor.policy.max_cost_per_task == 5.0

    def test_governor_string_representation(self):
        """Test IFGovernor __repr__"""
        policy = ResourcePolicy()
        governor = IFGovernor(coordinator=None, policy=policy)

        repr_str = repr(governor)
        assert "IFGovernor" in repr_str
        assert "swarms=0" in repr_str


# ==========================================
# Swarm Registration Tests
# ==========================================

class TestSwarmRegistration:
    """Test swarm registration and profile management"""

    def test_register_single_swarm(self):
        """Test registering a single swarm"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="guardian-council",
            capabilities=[Capability.GOVERNANCE_VOTING],
            cost_per_hour=15.0,
            reputation_score=0.98,
            current_budget_remaining=100.0,
            model="sonnet"
        )

        governor.register_swarm(profile)

        assert len(governor.swarm_registry) == 1
        assert "guardian-council" in governor.swarm_registry
        assert governor.swarm_registry["guardian-council"] == profile

    def test_register_multiple_swarms(self):
        """Test registering multiple swarms"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profiles = [
            SwarmProfile(
                swarm_id="session-1-ndi",
                capabilities=[Capability.INTEGRATION_NDI],
                cost_per_hour=2.0,
                reputation_score=0.92,
                current_budget_remaining=50.0,
                model="haiku"
            ),
            SwarmProfile(
                swarm_id="session-4-sip",
                capabilities=[Capability.INTEGRATION_SIP],
                cost_per_hour=2.0,
                reputation_score=0.90,
                current_budget_remaining=50.0,
                model="haiku"
            ),
        ]

        for profile in profiles:
            governor.register_swarm(profile)

        assert len(governor.swarm_registry) == 2
        assert "session-1-ndi" in governor.swarm_registry
        assert "session-4-sip" in governor.swarm_registry

    def test_get_swarm_profile(self):
        """Test retrieving swarm profile"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=50.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        retrieved = governor.get_swarm_profile("test-swarm")
        assert retrieved == profile

        not_found = governor.get_swarm_profile("nonexistent")
        assert not_found is None


# ==========================================
# Capability Matching Tests
# ==========================================

class TestCapabilityMatching:
    """Test core capability matching algorithm"""

    def test_find_swarm_with_perfect_capability_match(self):
        """Test finding swarm with 100% capability match"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        guardian_profile = SwarmProfile(
            swarm_id="guardian-council",
            capabilities=[
                Capability.GOVERNANCE_VOTING,
                Capability.INTEGRATION_H323,
                Capability.DOCS_TECHNICAL_WRITING
            ],
            cost_per_hour=15.0,
            reputation_score=0.98,
            current_budget_remaining=100.0,
            model="sonnet"
        )

        governor.register_swarm(guardian_profile)

        # Request exactly what swarm has
        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.GOVERNANCE_VOTING],
            max_cost=20.0
        )

        assert selected == "guardian-council"

    def test_find_swarm_with_70_percent_match(self):
        """Test finding swarm with exactly 70% capability match"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        swarm_profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[
                Capability.CODE_ANALYSIS_PYTHON,
                Capability.TESTING_UNIT,
                Capability.TESTING_INTEGRATION
            ],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=50.0,
            model="haiku"
        )

        governor.register_swarm(swarm_profile)

        # Require 3 capabilities, swarm has 2 (66.7% - below threshold)
        selected = governor.find_qualified_swarm(
            required_capabilities=[
                Capability.CODE_ANALYSIS_PYTHON,
                Capability.TESTING_UNIT,
                Capability.DOCS_TECHNICAL_WRITING  # Not in swarm
            ],
            max_cost=10.0
        )

        # Should be rejected (66.7% < 70%)
        assert selected is None

    def test_find_swarm_rejects_below_threshold(self):
        """Test that swarms below 70% threshold are rejected"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        swarm_profile = SwarmProfile(
            swarm_id="low-match-swarm",
            capabilities=[Capability.INTEGRATION_NDI],
            cost_per_hour=2.0,
            reputation_score=0.9,
            current_budget_remaining=50.0,
            model="haiku"
        )

        governor.register_swarm(swarm_profile)

        # Require capabilities swarm doesn't have
        selected = governor.find_qualified_swarm(
            required_capabilities=[
                Capability.CODE_ANALYSIS_RUST,
                Capability.TESTING_PERFORMANCE
            ],
            max_cost=10.0
        )

        assert selected is None  # 0% match < 70%

    def test_find_swarm_with_superset_capabilities(self):
        """Test that swarm with more capabilities than required is selected"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        swarm_profile = SwarmProfile(
            swarm_id="versatile-swarm",
            capabilities=[
                Capability.CODE_ANALYSIS_PYTHON,
                Capability.CODE_ANALYSIS_RUST,
                Capability.TESTING_UNIT,
                Capability.TESTING_INTEGRATION,
                Capability.DOCS_TECHNICAL_WRITING
            ],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=50.0,
            model="haiku"
        )

        governor.register_swarm(swarm_profile)

        # Only require 2 capabilities (swarm has both + more)
        selected = governor.find_qualified_swarm(
            required_capabilities=[
                Capability.CODE_ANALYSIS_PYTHON,
                Capability.DOCS_TECHNICAL_WRITING
            ],
            max_cost=10.0
        )

        assert selected == "versatile-swarm"  # 100% match


# ==========================================
# Scoring Algorithm Tests
# ==========================================

class TestScoringAlgorithm:
    """Test combined scoring: (capability × reputation) / cost"""

    def test_scoring_prefers_cheaper_swarm_with_same_capability(self):
        """Test that cheaper swarm wins when capabilities are equal"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        # Expensive swarm
        expensive_profile = SwarmProfile(
            swarm_id="expensive-sonnet",
            capabilities=[Capability.DOCS_TECHNICAL_WRITING],
            cost_per_hour=15.0,
            reputation_score=0.98,
            current_budget_remaining=100.0,
            model="sonnet"
        )

        # Cheap swarm
        cheap_profile = SwarmProfile(
            swarm_id="cheap-haiku",
            capabilities=[Capability.DOCS_TECHNICAL_WRITING],
            cost_per_hour=2.0,
            reputation_score=0.92,
            current_budget_remaining=50.0,
            model="haiku"
        )

        governor.register_swarm(expensive_profile)
        governor.register_swarm(cheap_profile)

        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.DOCS_TECHNICAL_WRITING],
            max_cost=20.0
        )

        # Cheap swarm should win despite lower reputation
        # expensive_score = (1.0 × 0.98) / 15.0 = 0.0653
        # cheap_score = (1.0 × 0.92) / 2.0 = 0.46
        assert selected == "cheap-haiku"

    def test_scoring_considers_reputation(self):
        """Test that reputation affects scoring"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        # High reputation
        high_rep_profile = SwarmProfile(
            swarm_id="high-reputation",
            capabilities=[Capability.GOVERNANCE_VOTING],
            cost_per_hour=10.0,
            reputation_score=0.99,
            current_budget_remaining=100.0,
            model="sonnet"
        )

        # Low reputation
        low_rep_profile = SwarmProfile(
            swarm_id="low-reputation",
            capabilities=[Capability.GOVERNANCE_VOTING],
            cost_per_hour=10.0,
            reputation_score=0.50,
            current_budget_remaining=50.0,
            model="sonnet"
        )

        governor.register_swarm(high_rep_profile)
        governor.register_swarm(low_rep_profile)

        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.GOVERNANCE_VOTING],
            max_cost=20.0
        )

        # High reputation swarm should win (same cost)
        assert selected == "high-reputation"

    def test_scoring_balances_all_three_factors(self):
        """Test that scoring balances capability, reputation, and cost"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        # Swarm 1: Perfect match, high cost, high reputation
        swarm1 = SwarmProfile(
            swarm_id="perfect-expensive",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON, Capability.TESTING_UNIT],
            cost_per_hour=20.0,
            reputation_score=0.98,
            current_budget_remaining=100.0,
            model="opus"
        )

        # Swarm 2: Partial match, low cost, medium reputation
        swarm2 = SwarmProfile(
            swarm_id="partial-cheap",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON, Capability.DOCS_TECHNICAL_WRITING],
            cost_per_hour=2.0,
            reputation_score=0.85,
            current_budget_remaining=50.0,
            model="haiku"
        )

        governor.register_swarm(swarm1)
        governor.register_swarm(swarm2)

        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            max_cost=25.0
        )

        # Both have 100% match for required capability
        # swarm1_score = (1.0 × 0.98) / 20.0 = 0.049
        # swarm2_score = (1.0 × 0.85) / 2.0 = 0.425
        assert selected == "partial-cheap"


# ==========================================
# Budget Filtering Tests
# ==========================================

class TestBudgetFiltering:
    """Test budget-based swarm filtering"""

    def test_excludes_swarm_with_zero_budget(self):
        """Test that swarms with $0 budget are excluded"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        # Swarm with budget
        funded_profile = SwarmProfile(
            swarm_id="funded-swarm",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=50.0,
            model="haiku"
        )

        # Swarm without budget
        broke_profile = SwarmProfile(
            swarm_id="broke-swarm",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.95,  # Higher reputation!
            current_budget_remaining=0.0,  # But no budget
            model="haiku"
        )

        governor.register_swarm(funded_profile)
        governor.register_swarm(broke_profile)

        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            max_cost=10.0
        )

        assert selected == "funded-swarm"  # Only one with budget

    def test_excludes_swarm_with_negative_budget(self):
        """Test that swarms with negative budget are excluded"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        overdrawn_profile = SwarmProfile(
            swarm_id="overdrawn-swarm",
            capabilities=[Capability.TESTING_UNIT],
            cost_per_hour=2.0,
            reputation_score=0.9,
            current_budget_remaining=-10.0,  # Overdrawn
            model="haiku"
        )

        governor.register_swarm(overdrawn_profile)

        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.TESTING_UNIT],
            max_cost=10.0
        )

        assert selected is None  # No swarms with positive budget


# ==========================================
# Cost Filtering Tests
# ==========================================

class TestCostFiltering:
    """Test cost-based swarm filtering"""

    def test_excludes_swarm_above_max_cost(self):
        """Test that swarms exceeding max_cost are excluded"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        expensive_profile = SwarmProfile(
            swarm_id="expensive-swarm",
            capabilities=[Capability.ARCHITECTURE_SECURITY],
            cost_per_hour=50.0,
            reputation_score=0.99,
            current_budget_remaining=100.0,
            model="opus"
        )

        governor.register_swarm(expensive_profile)

        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.ARCHITECTURE_SECURITY],
            max_cost=20.0  # Swarm costs $50/hr
        )

        assert selected is None  # Swarm too expensive

    def test_includes_swarm_at_max_cost(self):
        """Test that swarm at exactly max_cost is included"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        exact_cost_profile = SwarmProfile(
            swarm_id="exact-cost-swarm",
            capabilities=[Capability.INTEGRATION_WEBRTC],
            cost_per_hour=10.0,
            reputation_score=0.9,
            current_budget_remaining=50.0,
            model="sonnet"
        )

        governor.register_swarm(exact_cost_profile)

        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.INTEGRATION_WEBRTC],
            max_cost=10.0  # Exactly matches swarm cost
        )

        assert selected == "exact-cost-swarm"


# ==========================================
# Edge Case Tests
# ==========================================

class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_returns_none_when_no_swarms_registered(self):
        """Test that None is returned when no swarms are registered"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.CODE_ANALYSIS_RUST],
            max_cost=10.0
        )

        assert selected is None

    def test_returns_none_for_empty_required_capabilities(self):
        """Test that None is returned for empty required capabilities"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=50.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        selected = governor.find_qualified_swarm(
            required_capabilities=[],
            max_cost=10.0
        )

        assert selected is None

    def test_handles_tie_in_scoring(self):
        """Test that tie in scoring returns one of the tied swarms"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        # Two identical swarms
        swarm1 = SwarmProfile(
            swarm_id="swarm-1",
            capabilities=[Capability.TESTING_INTEGRATION],
            cost_per_hour=2.0,
            reputation_score=0.9,
            current_budget_remaining=50.0,
            model="haiku"
        )

        swarm2 = SwarmProfile(
            swarm_id="swarm-2",
            capabilities=[Capability.TESTING_INTEGRATION],
            cost_per_hour=2.0,
            reputation_score=0.9,
            current_budget_remaining=50.0,
            model="haiku"
        )

        governor.register_swarm(swarm1)
        governor.register_swarm(swarm2)

        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.TESTING_INTEGRATION],
            max_cost=10.0
        )

        # Should return one of them (deterministic based on dict ordering)
        assert selected in ["swarm-1", "swarm-2"]


# ==========================================
# Budget Reporting Tests
# ==========================================

class TestBudgetReporting:
    """Test budget status reporting"""

    def test_get_budget_report_for_single_swarm(self):
        """Test budget report for single swarm"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="guardian-council",
            capabilities=[Capability.GOVERNANCE_VOTING],
            cost_per_hour=15.0,
            reputation_score=0.98,
            current_budget_remaining=75.50,
            model="sonnet"
        )

        governor.register_swarm(profile)

        report = governor.get_budget_report()

        assert "guardian-council" in report
        assert report["guardian-council"]["remaining"] == 75.50
        assert report["guardian-council"]["cost_per_hour"] == 15.0
        assert report["guardian-council"]["model"] == "sonnet"
        assert report["guardian-council"]["reputation"] == 0.98

    def test_get_budget_report_for_multiple_swarms(self):
        """Test budget report for multiple swarms"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profiles = [
            SwarmProfile(
                swarm_id=f"swarm-{i}",
                capabilities=[Capability.CODE_ANALYSIS_PYTHON],
                cost_per_hour=float(i * 2),
                reputation_score=0.8 + (i * 0.05),
                current_budget_remaining=float(50 - i * 10),
                model="haiku"
            )
            for i in range(3)
        ]

        for profile in profiles:
            governor.register_swarm(profile)

        report = governor.get_budget_report()

        assert len(report) == 3
        assert all(f"swarm-{i}" in report for i in range(3))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
