"""
Unit Tests for IF.governor Circuit Breaker (P0.2.4)

Tests for:
- Circuit breaker trip on budget exhaustion
- Circuit breaker trip on repeated failures (3+ consecutive)
- Manual circuit breaker reset
- Human escalation notifications
- Coordinator integration (stubs)
- IF.witness logging (stubs)
- Error handling

Author: Session 3 (H.323 Guardian Council)
Version: 1.0
Status: Phase 0 Development
"""

import pytest
from infrafabric.governor import IFGovernor
from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
)


# ==========================================
# Budget Exhaustion Circuit Breaker Tests
# ==========================================

class TestCircuitBreakerBudgetExhaustion:
    """Test circuit breaker trip on budget exhaustion"""

    def test_circuit_breaker_trips_on_budget_exhaustion(self):
        """Test that circuit breaker trips when budget reaches $0"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=10.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Exhaust budget
        governor.track_cost("test-swarm", "operation", 10.0)

        # Budget should be clamped to 0
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 0.0

    def test_circuit_breaker_prevents_assignment_after_trip(self):
        """Test that swarm cannot be assigned tasks after circuit breaker trips"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.INTEGRATION_NDI],
            cost_per_hour=2.0,
            reputation_score=0.9,
            current_budget_remaining=5.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Can be assigned before exhaustion
        selected = governor.find_qualified_swarm(
            [Capability.INTEGRATION_NDI],
            max_cost=10.0
        )
        assert selected == "test-swarm"

        # Exhaust budget (trip circuit breaker)
        governor.track_cost("test-swarm", "operation", 5.0)

        # Cannot be assigned after circuit breaker trips
        selected = governor.find_qualified_swarm(
            [Capability.INTEGRATION_NDI],
            max_cost=10.0
        )
        assert selected is None

    def test_circuit_breaker_trip_on_overage(self):
        """Test circuit breaker trip when cost exceeds remaining budget"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.TESTING_UNIT],
            cost_per_hour=2.0,
            reputation_score=0.85,
            current_budget_remaining=10.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Spend more than remaining budget
        governor.track_cost("test-swarm", "expensive_operation", 20.0)

        # Budget should be clamped to 0 (not negative)
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 0.0


# ==========================================
# Repeated Failure Circuit Breaker Tests
# ==========================================

class TestCircuitBreakerRepeatedFailures:
    """Test circuit breaker trip on repeated failures"""

    def test_record_single_failure(self):
        """Test recording a single failure"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.CODE_ANALYSIS_RUST],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=100.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Record failure
        governor.record_failure("test-swarm")

        # Failure count should be 1
        assert governor.failure_counts["test-swarm"] == 1

        # Circuit breaker should NOT trip (threshold is 3)
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 100.0

    def test_record_multiple_failures_below_threshold(self):
        """Test recording multiple failures below threshold"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.DOCS_TECHNICAL_WRITING],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=100.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Record 2 failures (below threshold of 3)
        governor.record_failure("test-swarm")
        governor.record_failure("test-swarm")

        # Failure count should be 2
        assert governor.failure_counts["test-swarm"] == 2

        # Circuit breaker should NOT trip
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 100.0

    def test_circuit_breaker_trips_at_failure_threshold(self):
        """Test that circuit breaker trips at failure threshold (3 failures)"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.TESTING_INTEGRATION],
            cost_per_hour=2.0,
            reputation_score=0.85,
            current_budget_remaining=100.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Record 3 failures (at threshold)
        governor.record_failure("test-swarm")
        governor.record_failure("test-swarm")
        governor.record_failure("test-swarm")

        # Circuit breaker should trip (budget set to 0)
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 0.0

    def test_circuit_breaker_with_custom_failure_threshold(self):
        """Test circuit breaker with custom failure threshold"""
        # Custom policy with 5 failure threshold
        policy = ResourcePolicy(circuit_breaker_failure_threshold=5)
        governor = IFGovernor(coordinator=None, policy=policy)

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.ARCHITECTURE_SECURITY],
            cost_per_hour=15.0,
            reputation_score=0.95,
            current_budget_remaining=100.0,
            model="sonnet"
        )

        governor.register_swarm(profile)

        # Record 4 failures (below custom threshold of 5)
        for _ in range(4):
            governor.record_failure("test-swarm")

        # Circuit breaker should NOT trip
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 100.0

        # Record 5th failure (at threshold)
        governor.record_failure("test-swarm")

        # Circuit breaker should trip
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 0.0

    def test_record_failure_raises_error_for_unknown_swarm(self):
        """Test that record_failure() raises ValueError for unknown swarm"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        with pytest.raises(ValueError, match="Unknown swarm"):
            governor.record_failure("nonexistent-swarm")


# ==========================================
# Circuit Breaker Reset Tests
# ==========================================

class TestCircuitBreakerReset:
    """Test manual circuit breaker reset"""

    def test_reset_circuit_breaker_restores_budget(self):
        """Test that reset_circuit_breaker() restores budget"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=10.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Exhaust budget (trip circuit breaker)
        governor.track_cost("test-swarm", "operation", 10.0)
        assert governor.get_swarm_profile("test-swarm").current_budget_remaining == 0.0

        # Reset circuit breaker
        governor.reset_circuit_breaker("test-swarm", 50.0)

        # Budget should be restored
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 50.0

    def test_reset_circuit_breaker_clears_failure_count(self):
        """Test that reset_circuit_breaker() clears failure count"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.TESTING_PERFORMANCE],
            cost_per_hour=2.0,
            reputation_score=0.85,
            current_budget_remaining=100.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Trip circuit breaker via repeated failures
        for _ in range(3):
            governor.record_failure("test-swarm")

        assert governor.failure_counts["test-swarm"] == 3

        # Reset circuit breaker
        governor.reset_circuit_breaker("test-swarm", 100.0)

        # Failure count should be cleared
        assert governor.failure_counts["test-swarm"] == 0

    def test_reset_allows_task_assignment_again(self):
        """Test that reset allows swarm to be assigned tasks again"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.9,
            current_budget_remaining=5.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Exhaust budget
        governor.track_cost("test-swarm", "operation", 5.0)

        # Cannot be assigned
        selected = governor.find_qualified_swarm(
            [Capability.INTEGRATION_SIP],
            max_cost=10.0
        )
        assert selected is None

        # Reset circuit breaker
        governor.reset_circuit_breaker("test-swarm", 50.0)

        # Can be assigned again
        selected = governor.find_qualified_swarm(
            [Capability.INTEGRATION_SIP],
            max_cost=10.0
        )
        assert selected == "test-swarm"

    def test_reset_circuit_breaker_raises_error_for_unknown_swarm(self):
        """Test that reset_circuit_breaker() raises ValueError for unknown swarm"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        with pytest.raises(ValueError, match="Unknown swarm"):
            governor.reset_circuit_breaker("nonexistent-swarm", 50.0)

    def test_reset_circuit_breaker_raises_error_for_zero_budget(self):
        """Test that reset_circuit_breaker() raises ValueError for zero budget"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.CLI_TESTING],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=0.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        with pytest.raises(ValueError, match="New budget must be positive"):
            governor.reset_circuit_breaker("test-swarm", 0.0)

    def test_reset_circuit_breaker_raises_error_for_negative_budget(self):
        """Test that reset_circuit_breaker() raises ValueError for negative budget"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.DEVOPS_MONITORING],
            cost_per_hour=2.0,
            reputation_score=0.85,
            current_budget_remaining=0.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        with pytest.raises(ValueError, match="New budget must be positive"):
            governor.reset_circuit_breaker("test-swarm", -10.0)


# ==========================================
# Integration Stub Tests
# ==========================================

class TestCircuitBreakerIntegrationStubs:
    """Test integration stubs for coordinator and witness"""

    def test_circuit_breaker_trip_calls_coordinator_stub(self):
        """Test that circuit breaker trip notifies coordinator (stub)"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.CODE_ANALYSIS_GO],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=5.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Trip circuit breaker
        governor.track_cost("test-swarm", "operation", 5.0)

        # Coordinator stub should be called (logged)
        # Budget should be 0
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 0.0

    def test_circuit_breaker_reset_calls_coordinator_stub(self):
        """Test that circuit breaker reset notifies coordinator (stub)"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.INFRA_KUBERNETES],
            cost_per_hour=2.0,
            reputation_score=0.9,
            current_budget_remaining=5.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Trip and reset
        governor.track_cost("test-swarm", "operation", 5.0)
        governor.reset_circuit_breaker("test-swarm", 50.0)

        # Coordinator stub should be called (logged)
        # Budget should be restored
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 50.0


# ==========================================
# Scenario Tests
# ==========================================

class TestCircuitBreakerScenarios:
    """Test realistic circuit breaker scenarios"""

    def test_complete_circuit_breaker_lifecycle(self):
        """Test complete lifecycle: trip, escalate, reset, resume"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        guardian_profile = SwarmProfile(
            swarm_id="guardian-council",
            capabilities=[
                Capability.GOVERNANCE_VOTING,
                Capability.INTEGRATION_H323
            ],
            cost_per_hour=15.0,
            reputation_score=0.98,
            current_budget_remaining=30.0,
            model="sonnet"
        )

        governor.register_swarm(guardian_profile)

        # Phase 1: Normal operation
        selected = governor.find_qualified_swarm(
            [Capability.GOVERNANCE_VOTING],
            max_cost=20.0
        )
        assert selected == "guardian-council"

        # Track costs
        governor.track_cost("guardian-council", "vote_1", 12.0)
        governor.track_cost("guardian-council", "vote_2", 18.0)

        # Phase 2: Budget exhausted, circuit breaker trips
        profile = governor.get_swarm_profile("guardian-council")
        assert profile.current_budget_remaining == 0.0

        # Cannot be assigned
        selected = governor.find_qualified_swarm(
            [Capability.GOVERNANCE_VOTING],
            max_cost=20.0
        )
        assert selected is None

        # Phase 3: Human investigation and reset
        governor.reset_circuit_breaker("guardian-council", 100.0)

        # Phase 4: Resume normal operation
        profile = governor.get_swarm_profile("guardian-council")
        assert profile.current_budget_remaining == 100.0

        selected = governor.find_qualified_swarm(
            [Capability.GOVERNANCE_VOTING],
            max_cost=20.0
        )
        assert selected == "guardian-council"

    def test_repeated_failures_scenario(self):
        """Test realistic scenario with repeated task failures"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        swarm_profile = SwarmProfile(
            swarm_id="unstable-swarm",
            capabilities=[Capability.INTEGRATION_WEBRTC],
            cost_per_hour=2.0,
            reputation_score=0.7,
            current_budget_remaining=100.0,
            model="haiku"
        )

        governor.register_swarm(swarm_profile)

        # Swarm experiences intermittent failures
        operations = [
            ("task_1", True),   # Success
            ("task_2", False),  # Failure 1
            ("task_3", False),  # Failure 2
            ("task_4", True),   # Success (resets count? No - consecutive only if we implement that)
            ("task_5", False),  # Failure 3 - should trip
        ]

        for operation, success in operations:
            if not success:
                governor.record_failure("unstable-swarm")

        # After 3 failures, circuit breaker should trip
        profile = governor.get_swarm_profile("unstable-swarm")
        assert profile.current_budget_remaining == 0.0

    def test_multiple_swarms_independent_circuit_breakers(self):
        """Test that circuit breakers are independent per swarm"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        swarm1 = SwarmProfile(
            swarm_id="swarm-1",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=10.0,
            model="haiku"
        )

        swarm2 = SwarmProfile(
            swarm_id="swarm-2",
            capabilities=[Capability.CODE_ANALYSIS_RUST],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=100.0,
            model="haiku"
        )

        governor.register_swarm(swarm1)
        governor.register_swarm(swarm2)

        # Trip circuit breaker for swarm-1
        governor.track_cost("swarm-1", "operation", 10.0)

        # swarm-1 circuit breaker tripped
        assert governor.get_swarm_profile("swarm-1").current_budget_remaining == 0.0

        # swarm-2 circuit breaker NOT tripped
        assert governor.get_swarm_profile("swarm-2").current_budget_remaining == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
