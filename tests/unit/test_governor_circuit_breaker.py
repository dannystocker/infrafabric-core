"""Unit tests for P0.2.4 - Circuit Breaker Implementation

This test suite validates circuit breaker functionality for IF.governor.
Circuit breakers prevent cost spirals and repeated failures by halting
problematic swarms until manual intervention.

Philosophy:
- IF.TTT Trustworthy: Automatic safeguards prevent runaway costs
- IF.ground Observable: All circuit breaker events are auditable
- Wu Lun (朋友): Peer accountability through automated enforcement

Test Coverage:
- Circuit breaker tripping
- Tripped swarms excluded from assignment
- Manual reset functionality
- Human escalation
- Various trip reasons
"""

import pytest
import time
from infrafabric.governor import IFGovernor
from infrafabric.schemas.capability import Capability, SwarmProfile


class TestCircuitBreakerTripping:
    """Test circuit breaker tripping functionality"""

    @pytest.fixture
    def governor(self):
        """Create governor with swarm"""
        gov = IFGovernor()
        gov.register_swarm(SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=5.0,
            model="sonnet"
        ))
        return gov

    def test_trip_circuit_breaker(self, governor):
        """Test tripping circuit breaker marks swarm as tripped"""
        governor._trip_circuit_breaker("test-swarm", "budget_exhausted")

        assert "test-swarm" in governor.circuit_breaker_tripped
        assert governor.circuit_breaker_tripped["test-swarm"]["reason"] == "budget_exhausted"

    def test_trip_circuit_breaker_sets_budget_zero(self, governor):
        """Test that tripping circuit breaker sets budget to zero"""
        governor._trip_circuit_breaker("test-swarm", "repeated_failures")

        profile = governor.get_swarm_profile("test-swarm")
        assert profile.current_budget_remaining == 0

    def test_trip_circuit_breaker_unknown_swarm(self, governor):
        """Test tripping circuit breaker for unknown swarm raises error"""
        with pytest.raises(ValueError, match="Unknown swarm"):
            governor._trip_circuit_breaker("unknown-swarm", "budget_exhausted")

    def test_trip_circuit_breaker_records_timestamp(self, governor):
        """Test that circuit breaker trip records timestamp"""
        before = time.time()
        governor._trip_circuit_breaker("test-swarm", "budget_exhausted")
        after = time.time()

        trip_info = governor.circuit_breaker_tripped["test-swarm"]
        assert "tripped_at" in trip_info
        assert before <= trip_info["tripped_at"] <= after

    def test_trip_circuit_breaker_stores_reason(self, governor):
        """Test that various trip reasons are stored correctly"""
        reasons = [
            "budget_exhausted",
            "repeated_failures",
            "performance_degradation",
            "manual_override"
        ]

        for i, reason in enumerate(reasons):
            swarm_id = f"swarm-{i}"
            governor.register_swarm(SwarmProfile(
                swarm_id, [Capability.INTEGRATION_SIP],
                2.0, 0.95, 5.0, "sonnet"
            ))
            governor._trip_circuit_breaker(swarm_id, reason)

            assert governor.circuit_breaker_tripped[swarm_id]["reason"] == reason


class TestCircuitBreakerExclusion:
    """Test that tripped swarms are excluded from assignment"""

    def test_tripped_swarm_excluded_from_matching(self):
        """Test that tripped swarms are not returned by find_qualified_swarm"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "tripped-swarm",
            [Capability.INTEGRATION_SIP],
            2.0, 0.95, 10.0, "sonnet"
        ))

        # Verify swarm is initially assignable
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result == "tripped-swarm"

        # Trip circuit breaker
        governor._trip_circuit_breaker("tripped-swarm", "budget_exhausted")

        # Should now return None
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result is None

    def test_tripped_swarm_excluded_even_with_best_match(self):
        """Test that tripped swarm is excluded even if it has the best match"""
        governor = IFGovernor()

        # Register perfect match swarm
        governor.register_swarm(SwarmProfile(
            "perfect-match",
            [Capability.INTEGRATION_SIP, Capability.INTEGRATION_H323],
            1.0,  # Cheapest
            1.0,  # Perfect reputation
            10.0,
            "haiku"
        ))

        # Register mediocre swarm
        governor.register_swarm(SwarmProfile(
            "mediocre",
            [Capability.INTEGRATION_SIP],
            5.0,  # Expensive
            0.70,  # Lower reputation
            5.0,
            "opus"
        ))

        # Trip perfect match
        governor._trip_circuit_breaker("perfect-match", "repeated_failures")

        # Should get mediocre swarm despite worse stats
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=10.0)
        assert result == "mediocre"

    def test_budget_exhaustion_trips_circuit_breaker(self):
        """Test that budget exhaustion automatically trips circuit breaker"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "low-budget",
            [Capability.INTEGRATION_SIP],
            2.0, 0.95, 2.0, "sonnet"
        ))

        # Exhaust budget
        governor.track_cost("low-budget", "expensive_op", 3.0)

        # Circuit breaker should be tripped
        assert "low-budget" in governor.circuit_breaker_tripped
        assert governor.circuit_breaker_tripped["low-budget"]["reason"] == "budget_exhausted"

        # Should not be assignable
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result is None


class TestCircuitBreakerReset:
    """Test manual circuit breaker reset"""

    @pytest.fixture
    def governor(self):
        """Create governor with tripped swarm"""
        gov = IFGovernor()
        gov.register_swarm(SwarmProfile(
            "tripped-swarm",
            [Capability.INTEGRATION_SIP],
            2.0, 0.95, 5.0, "sonnet"
        ))
        gov._trip_circuit_breaker("tripped-swarm", "budget_exhausted")
        return gov

    def test_reset_circuit_breaker(self, governor):
        """Test resetting circuit breaker removes trip status"""
        governor.reset_circuit_breaker("tripped-swarm", new_budget=10.0)

        assert "tripped-swarm" not in governor.circuit_breaker_tripped

    def test_reset_circuit_breaker_restores_budget(self, governor):
        """Test that reset restores budget"""
        governor.reset_circuit_breaker("tripped-swarm", new_budget=15.0)

        profile = governor.get_swarm_profile("tripped-swarm")
        assert profile.current_budget_remaining == 15.0

    def test_reset_circuit_breaker_makes_swarm_assignable(self, governor):
        """Test that reset makes swarm assignable again"""
        # Initially not assignable
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result is None

        # Reset
        governor.reset_circuit_breaker("tripped-swarm", new_budget=10.0)

        # Now assignable
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result == "tripped-swarm"

    def test_reset_circuit_breaker_unknown_swarm(self, governor):
        """Test resetting unknown swarm raises error"""
        with pytest.raises(ValueError, match="Unknown swarm"):
            governor.reset_circuit_breaker("unknown-swarm", new_budget=10.0)

    def test_reset_circuit_breaker_not_tripped(self):
        """Test resetting non-tripped swarm raises error"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "healthy-swarm",
            [Capability.INTEGRATION_SIP],
            2.0, 0.95, 10.0, "sonnet"
        ))

        with pytest.raises(ValueError, match="Circuit breaker not tripped"):
            governor.reset_circuit_breaker("healthy-swarm", new_budget=15.0)


class TestCircuitBreakerStatus:
    """Test circuit breaker status reporting"""

    def test_get_circuit_breaker_status_empty(self):
        """Test getting status when no circuit breakers tripped"""
        governor = IFGovernor()
        status = governor.get_circuit_breaker_status()

        assert status == {}

    def test_get_circuit_breaker_status_single(self):
        """Test getting status for single tripped swarm"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "tripped", [Capability.INTEGRATION_SIP],
            2.0, 0.95, 5.0, "sonnet"
        ))
        governor._trip_circuit_breaker("tripped", "budget_exhausted")

        status = governor.get_circuit_breaker_status()

        assert "tripped" in status
        assert status["tripped"]["reason"] == "budget_exhausted"

    def test_get_circuit_breaker_status_multiple(self):
        """Test getting status for multiple tripped swarms"""
        governor = IFGovernor()

        swarms = [
            ("swarm-1", "budget_exhausted"),
            ("swarm-2", "repeated_failures"),
            ("swarm-3", "performance_degradation"),
        ]

        for swarm_id, reason in swarms:
            governor.register_swarm(SwarmProfile(
                swarm_id, [Capability.INTEGRATION_SIP],
                2.0, 0.95, 5.0, "sonnet"
            ))
            governor._trip_circuit_breaker(swarm_id, reason)

        status = governor.get_circuit_breaker_status()

        assert len(status) == 3
        for swarm_id, reason in swarms:
            assert status[swarm_id]["reason"] == reason


class TestCircuitBreakerIntegration:
    """Test circuit breaker integration with other features"""

    def test_multiple_swarms_independent_circuit_breakers(self):
        """Test that circuit breakers are independent per swarm"""
        governor = IFGovernor()

        # Register 3 swarms
        for i in range(3):
            governor.register_swarm(SwarmProfile(
                f"swarm-{i}",
                [Capability.INTEGRATION_SIP],
                2.0, 0.95, 10.0, "sonnet"
            ))

        # Trip one swarm
        governor._trip_circuit_breaker("swarm-1", "budget_exhausted")

        # Only swarm-1 should be tripped
        assert "swarm-1" in governor.circuit_breaker_tripped
        assert "swarm-0" not in governor.circuit_breaker_tripped
        assert "swarm-2" not in governor.circuit_breaker_tripped

        # Other swarms should still be assignable
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result in ["swarm-0", "swarm-2"]

    def test_circuit_breaker_with_budget_tracking(self):
        """Test circuit breaker interaction with budget tracking"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "test-swarm",
            [Capability.INTEGRATION_SIP],
            2.0, 0.95, 5.0, "sonnet"
        ))

        # Track costs
        governor.track_cost("test-swarm", "op1", 2.0)
        governor.track_cost("test-swarm", "op2", 2.0)

        # Budget not yet exhausted
        assert "test-swarm" not in governor.circuit_breaker_tripped

        # Exhaust budget
        governor.track_cost("test-swarm", "op3", 2.0)

        # Circuit breaker should be tripped
        assert "test-swarm" in governor.circuit_breaker_tripped

    def test_circuit_breaker_prevents_cost_spiral(self):
        """Test that circuit breaker prevents cost spirals"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "runaway-swarm",
            [Capability.INTEGRATION_SIP],
            2.0, 0.95, 10.0, "sonnet"
        ))

        # Simulate cost spiral - exhaust budget
        governor.track_cost("runaway-swarm", "expensive_op", 15.0)

        # Circuit breaker should be tripped
        assert "runaway-swarm" in governor.circuit_breaker_tripped

        # Further operations should not be assigned
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result is None

        # Get budget report
        report = governor.get_budget_report()
        assert report["runaway-swarm"] <= 0  # Budget exhausted or negative


class TestSession4Integration:
    """Test Session 4 (SIP) circuit breaker scenarios"""

    def test_session_4_budget_exhaustion_trips_breaker(self):
        """Test Session 4 swarm circuit breaker on budget exhaustion"""
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
            current_budget_remaining=10.44,
            model="sonnet"
        ))

        # Simulate expensive operations
        operations = [
            ("sip_integration", 3.0),
            ("h323_gateway", 4.0),
            ("security_audit", 5.0),
        ]

        for op, cost in operations:
            # Check if still has budget
            profile = governor.get_swarm_profile("session-4-sip")
            if profile.current_budget_remaining > 0:
                governor.track_cost("session-4-sip", op, cost)

        # Circuit breaker should be tripped
        assert "session-4-sip" in governor.circuit_breaker_tripped
        assert governor.circuit_breaker_tripped["session-4-sip"]["reason"] == "budget_exhausted"

    def test_session_4_circuit_breaker_reset(self):
        """Test resetting Session 4 circuit breaker"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "session-4-sip",
            [Capability.INTEGRATION_SIP],
            2.0, 0.95, 1.0, "sonnet"
        ))

        # Trip circuit breaker
        governor.track_cost("session-4-sip", "expensive_op", 2.0)
        assert "session-4-sip" in governor.circuit_breaker_tripped

        # Reset with new budget allocation
        governor.reset_circuit_breaker("session-4-sip", new_budget=25.0)

        # Should be operational again
        result = governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        assert result == "session-4-sip"

        profile = governor.get_swarm_profile("session-4-sip")
        assert profile.current_budget_remaining == 25.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
