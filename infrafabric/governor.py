"""
IF.governor - Capability-Aware Resource Manager

This module implements the capability matching and resource management system
for InfraFabric S² (Swarm of Swarms). It solves Bug #2: 57% cost waste by
ensuring tasks are assigned to the right agents based on capabilities, cost,
and reputation.

Key Features:
- Capability-based task assignment (70%+ match threshold)
- Budget tracking and enforcement
- Circuit breaker pattern for cost control
- Reputation-aware scoring
- Policy engine for governance rules

Author: Session 3 (H.323 Guardian Council)
Version: 1.0
Status: Phase 0 Development
"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
import logging
import time

from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
    calculate_capability_overlap,
)

logger = logging.getLogger(__name__)


class IFGovernor:
    """
    Capability-aware resource and budget management

    IF.governor is the core resource manager for InfraFabric S².
    It implements capability matching, budget tracking, and circuit
    breakers to prevent cost spirals.

    The Problem (Bug #2):
    - Before: 57% cost waste from poor task assignment
    - After: <10% waste with capability matching

    Example:
        >>> from infrafabric.schemas.capability import SwarmProfile, Capability, ResourcePolicy
        >>> policy = ResourcePolicy(min_capability_match=0.7)
        >>> governor = IFGovernor(coordinator=None, policy=policy)
        >>>
        >>> # Register guardian council
        >>> guardian_profile = SwarmProfile(
        ...     swarm_id="guardian-council",
        ...     capabilities=[Capability.GOVERNANCE_VOTING, Capability.INTEGRATION_H323],
        ...     cost_per_hour=15.0,
        ...     reputation_score=0.98,
        ...     current_budget_remaining=100.0,
        ...     model="sonnet"
        ... )
        >>> governor.register_swarm(guardian_profile)
        >>>
        >>> # Find best swarm for H.323 task
        >>> swarm_id = governor.find_qualified_swarm(
        ...     required_capabilities=[Capability.INTEGRATION_H323],
        ...     max_cost=20.0
        ... )
        >>> swarm_id
        'guardian-council'
    """

    def __init__(self, coordinator, policy: ResourcePolicy):
        """
        Initialize IF.governor

        Args:
            coordinator: IF.coordinator instance (for event bus notifications)
            policy: ResourcePolicy with governance rules
        """
        self.coordinator = coordinator
        self.policy = policy
        self.swarm_registry: Dict[str, SwarmProfile] = {}
        self.failure_counts: Dict[str, int] = {}

        logger.info(
            f"IF.governor initialized with policy: "
            f"max_swarms={policy.max_swarms_per_task}, "
            f"max_cost=${policy.max_cost_per_task}, "
            f"min_match={policy.min_capability_match}"
        )

    def register_swarm(self, profile: SwarmProfile):
        """
        Register swarm with capabilities and budget

        Args:
            profile: SwarmProfile with capabilities, cost, reputation, budget

        Example:
            >>> profile = SwarmProfile(
            ...     swarm_id="session-1-ndi",
            ...     capabilities=[Capability.INTEGRATION_NDI, Capability.DOCS_TECHNICAL_WRITING],
            ...     cost_per_hour=2.0,
            ...     reputation_score=0.92,
            ...     current_budget_remaining=50.0,
            ...     model="haiku"
            ... )
            >>> governor.register_swarm(profile)
        """
        self.swarm_registry[profile.swarm_id] = profile
        self.failure_counts[profile.swarm_id] = 0

        logger.info(
            f"Registered swarm '{profile.swarm_id}': "
            f"{len(profile.capabilities)} capabilities, "
            f"${profile.cost_per_hour}/hr, "
            f"reputation={profile.reputation_score:.2f}, "
            f"budget=${profile.current_budget_remaining}"
        )

    def find_qualified_swarm(
        self,
        required_capabilities: List[Capability],
        max_cost: float
    ) -> Optional[str]:
        """
        Find best swarm based on capability match and cost

        This is the core capability matching algorithm that implements:
        1. Jaccard similarity for capability overlap
        2. 70% minimum match threshold (configurable via policy)
        3. Combined scoring: (capability × reputation) / cost
        4. Budget enforcement (excludes swarms with $0 budget)

        Args:
            required_capabilities: List of required Capability enum values
            max_cost: Maximum acceptable cost per hour

        Returns:
            swarm_id of best-qualified swarm, or None if no match found

        Algorithm:
            For each swarm:
                1. Calculate capability overlap (Jaccard similarity)
                2. Filter by policy.min_capability_match (default 70%)
                3. Filter by max_cost
                4. Filter by budget > 0
                5. Calculate score = (overlap × reputation) / cost
                6. Return highest-scoring swarm

        Example:
            >>> # Find swarm for documentation task
            >>> swarm_id = governor.find_qualified_swarm(
            ...     required_capabilities=[Capability.DOCS_TECHNICAL_WRITING],
            ...     max_cost=10.0
            ... )
            >>> print(f"Selected: {swarm_id}")
            Selected: session-1-ndi  # Cheapest qualified swarm ($2/hr Haiku)
        """
        if not required_capabilities:
            logger.warning("find_qualified_swarm called with empty required_capabilities")
            return None

        candidates: List[Tuple[str, float, float]] = []

        logger.debug(
            f"Finding qualified swarm for {len(required_capabilities)} required capabilities, "
            f"max_cost=${max_cost}"
        )

        for swarm_id, profile in self.swarm_registry.items():
            # Step 1: Calculate capability overlap (Jaccard similarity)
            capability_overlap = calculate_capability_overlap(
                profile.capabilities,
                required_capabilities
            )

            # Step 2: Filter by minimum capability match threshold
            if capability_overlap < self.policy.min_capability_match:
                logger.debug(
                    f"  {swarm_id}: REJECTED (capability {capability_overlap:.1%} < "
                    f"{self.policy.min_capability_match:.1%} threshold)"
                )
                continue

            # Step 3: Filter by max cost
            if profile.cost_per_hour > max_cost:
                logger.debug(
                    f"  {swarm_id}: REJECTED (cost ${profile.cost_per_hour} > ${max_cost})"
                )
                continue

            # Step 4: Filter by budget availability
            if profile.current_budget_remaining <= 0:
                logger.debug(
                    f"  {swarm_id}: REJECTED (budget exhausted: "
                    f"${profile.current_budget_remaining})"
                )
                continue

            # Step 5: Calculate combined score
            # Score = (capability_overlap × reputation_score) / cost_per_hour
            # Higher score = better candidate
            score = (capability_overlap * profile.reputation_score) / profile.cost_per_hour

            candidates.append((swarm_id, score, capability_overlap))

            logger.debug(
                f"  {swarm_id}: QUALIFIED "
                f"(capability={capability_overlap:.1%}, "
                f"reputation={profile.reputation_score:.2f}, "
                f"cost=${profile.cost_per_hour}/hr, "
                f"score={score:.4f})"
            )

        # No qualified swarms found
        if not candidates:
            logger.warning(
                f"No qualified swarms found for required capabilities: "
                f"{[cap.value for cap in required_capabilities]}"
            )
            return None

        # Step 6: Sort by score (highest first) and return best swarm
        candidates.sort(key=lambda x: x[1], reverse=True)
        selected_swarm_id, selected_score, selected_overlap = candidates[0]

        logger.info(
            f"Selected swarm '{selected_swarm_id}' with score={selected_score:.4f}, "
            f"capability_match={selected_overlap:.1%}"
        )

        # Log capability matching decision to IF.witness (if available)
        self._log_capability_match(
            required_capabilities=required_capabilities,
            selected_swarm=selected_swarm_id,
            match_score=selected_score,
            capability_overlap=selected_overlap,
            candidates_considered=len(self.swarm_registry),
            candidates_qualified=len(candidates)
        )

        return selected_swarm_id

    def get_swarm_profile(self, swarm_id: str) -> Optional[SwarmProfile]:
        """
        Get SwarmProfile for a registered swarm

        Args:
            swarm_id: Swarm identifier

        Returns:
            SwarmProfile or None if not found
        """
        return self.swarm_registry.get(swarm_id)

    def track_cost(self, swarm_id: str, operation: str, cost: float):
        """
        Track costs and enforce budget limits

        This method deducts the cost from the swarm's budget and logs
        the operation to IF.optimise and IF.witness. If budget is exhausted,
        triggers circuit breaker.

        Args:
            swarm_id: Swarm identifier
            operation: Operation name (e.g., "guardian_vote", "code_review")
            cost: Cost in dollars

        Raises:
            ValueError: If swarm_id is not registered

        Example:
            >>> governor.track_cost("guardian-council", "h323_vote", 2.50)
            >>> profile = governor.get_swarm_profile("guardian-council")
            >>> profile.current_budget_remaining
            97.50  # Was 100.00, now 97.50
        """
        if swarm_id not in self.swarm_registry:
            raise ValueError(f"Unknown swarm: {swarm_id}")

        profile = self.swarm_registry[swarm_id]
        old_budget = profile.current_budget_remaining

        # Deduct cost from budget
        profile.current_budget_remaining -= cost

        logger.info(
            f"Cost tracked for '{swarm_id}': ${cost:.2f} for '{operation}' "
            f"(budget: ${old_budget:.2f} → ${profile.current_budget_remaining:.2f})"
        )

        # Check budget warning threshold (default 20%)
        budget_pct = profile.current_budget_remaining / (old_budget + cost) if (old_budget + cost) > 0 else 0
        if budget_pct <= self.policy.budget_warning_threshold and budget_pct > 0:
            logger.warning(
                f"⚠️  Low budget warning for '{swarm_id}': "
                f"${profile.current_budget_remaining:.2f} remaining "
                f"({budget_pct:.1%} of original budget)"
            )

        # Log cost to IF.optimise (stub - will be implemented in separate component)
        self._log_cost_to_optimise(swarm_id, operation, cost)

        # Log to IF.witness (stub - will be implemented in P0.4.3)
        self._log_cost_to_witness(
            swarm_id=swarm_id,
            operation=operation,
            cost=cost,
            remaining_budget=profile.current_budget_remaining
        )

        # Check if budget exhausted → trip circuit breaker
        if profile.current_budget_remaining <= 0:
            logger.error(
                f"🚨 Budget exhausted for '{swarm_id}': "
                f"${profile.current_budget_remaining:.2f}"
            )
            self._trip_circuit_breaker(swarm_id, reason='budget_exhausted')

    def get_budget_report(self) -> Dict[str, Dict[str, float]]:
        """
        Get budget status for all swarms

        Returns:
            Dictionary mapping swarm_id to budget details

        Example:
            >>> report = governor.get_budget_report()
            >>> report['guardian-council']
            {
                'remaining': 75.50,
                'cost_per_hour': 15.0,
                'model': 'sonnet',
                'reputation': 0.98
            }
        """
        return {
            swarm_id: {
                'remaining': profile.current_budget_remaining,
                'cost_per_hour': profile.cost_per_hour,
                'model': profile.model,
                'reputation': profile.reputation_score
            }
            for swarm_id, profile in self.swarm_registry.items()
        }

    def _log_cost_to_optimise(self, swarm_id: str, operation: str, cost: float):
        """
        Log cost to IF.optimise for cost tracking and optimization

        This is a stub that will integrate with IF.optimise when available.
        IF.optimise provides cost analytics and optimization recommendations.

        Args:
            swarm_id: Swarm that incurred the cost
            operation: Operation name
            cost: Cost in dollars
        """
        # Stub for IF.optimise integration
        # Will be replaced with actual IF.optimise API call
        logger.debug(
            f"IF.optimise: track_operation_cost(provider={swarm_id}, "
            f"operation={operation}, cost=${cost:.2f})"
        )

    def _log_cost_to_witness(
        self,
        swarm_id: str,
        operation: str,
        cost: float,
        remaining_budget: float
    ):
        """
        Log cost tracking event to IF.witness for audit trail

        This provides audit trail for all budget changes. Will be fully
        implemented when IF.witness is available (P0.4.3).

        Args:
            swarm_id: Swarm that incurred the cost
            operation: Operation name
            cost: Cost in dollars
            remaining_budget: Budget remaining after deduction
        """
        # Stub for IF.witness integration (P0.4.3)
        # Will be replaced with actual IF.witness API call
        logger.debug(
            f"IF.witness: cost_tracked(swarm_id={swarm_id}, operation={operation}, "
            f"cost=${cost:.2f}, remaining=${remaining_budget:.2f})"
        )

    def _log_capability_match(
        self,
        required_capabilities: List[Capability],
        selected_swarm: str,
        match_score: float,
        capability_overlap: float,
        candidates_considered: int,
        candidates_qualified: int
    ):
        """
        Log capability matching decision to IF.witness

        This provides audit trail for task assignment decisions.

        Args:
            required_capabilities: Capabilities that were required
            selected_swarm: Swarm that was selected
            match_score: Combined score of selected swarm
            capability_overlap: Capability overlap percentage
            candidates_considered: Total swarms considered
            candidates_qualified: Swarms that met threshold
        """
        # IF.witness integration will be added in P0.4.3
        # For now, just log to Python logger
        logger.info(
            f"CAPABILITY_MATCH: "
            f"selected={selected_swarm}, "
            f"score={match_score:.4f}, "
            f"overlap={capability_overlap:.1%}, "
            f"candidates={candidates_considered}, "
            f"qualified={candidates_qualified}, "
            f"required_caps={[c.value for c in required_capabilities]}"
        )

    def record_failure(self, swarm_id: str):
        """
        Record task failure for circuit breaker tracking

        Tracks consecutive failures. After reaching the threshold
        (default: 3 failures), trips the circuit breaker.

        Args:
            swarm_id: Swarm that failed a task

        Raises:
            ValueError: If swarm_id is not registered

        Example:
            >>> governor.record_failure("test-swarm")
            >>> governor.record_failure("test-swarm")
            >>> governor.record_failure("test-swarm")
            # Circuit breaker trips after 3rd failure
        """
        if swarm_id not in self.swarm_registry:
            raise ValueError(f"Unknown swarm: {swarm_id}")

        # Increment failure count
        if swarm_id not in self.failure_counts:
            self.failure_counts[swarm_id] = 0

        self.failure_counts[swarm_id] += 1

        logger.warning(
            f"Failure recorded for '{swarm_id}': "
            f"{self.failure_counts[swarm_id]} consecutive failures"
        )

        # Check if threshold exceeded
        if self.failure_counts[swarm_id] >= self.policy.circuit_breaker_failure_threshold:
            logger.error(
                f"🚨 Failure threshold exceeded for '{swarm_id}': "
                f"{self.failure_counts[swarm_id]} >= {self.policy.circuit_breaker_failure_threshold}"
            )
            self._trip_circuit_breaker(swarm_id, reason='repeated_failures')

    def _trip_circuit_breaker(self, swarm_id: str, reason: str):
        """
        Halt swarm to prevent cost spirals or repeated failures

        This is a SAFETY mechanism that requires human approval to reset.
        When tripped, the swarm:
        1. Has budget set to $0 (cannot be assigned new tasks)
        2. Is marked as unavailable in IF.coordinator
        3. Triggers HIGH severity incident log
        4. Escalates to human for manual intervention

        Args:
            swarm_id: Swarm to halt
            reason: Reason for tripping ('budget_exhausted' or 'repeated_failures')

        Example:
            >>> governor._trip_circuit_breaker("test-swarm", "budget_exhausted")
            # Swarm halted, human escalation triggered
        """
        if swarm_id not in self.swarm_registry:
            logger.error(f"Cannot trip circuit breaker for unknown swarm: {swarm_id}")
            return

        profile = self.swarm_registry[swarm_id]

        # Mark swarm as unavailable (set budget to 0)
        profile.current_budget_remaining = 0.0

        logger.error(
            f"🚨 CIRCUIT BREAKER TRIPPED: '{swarm_id}' "
            f"(reason: {reason})"
        )

        # Notify IF.coordinator to stop sending tasks (stub)
        self._notify_coordinator_circuit_breaker(swarm_id, 'circuit_breaker_tripped')

        # Log incident with HIGH severity to IF.witness (stub)
        self._log_circuit_breaker_trip(swarm_id, reason)

        # Escalate to human (CRITICAL)
        self._escalate_to_human(swarm_id, {
            'type': 'circuit_breaker',
            'reason': reason,
            'failure_count': self.failure_counts.get(swarm_id, 0),
            'budget_remaining': profile.current_budget_remaining,
            'action_required': 'manual_reset'
        })

    def reset_circuit_breaker(self, swarm_id: str, new_budget: float):
        """
        Manually reset circuit breaker (requires human approval)

        This method should only be called after:
        1. Investigating the root cause of the circuit breaker trip
        2. Confirming the swarm is safe to resume
        3. Allocating appropriate new budget

        Args:
            swarm_id: Swarm to reset
            new_budget: New budget allocation (must be > 0)

        Raises:
            ValueError: If swarm_id is not registered or new_budget <= 0

        Example:
            >>> # After investigation and approval
            >>> governor.reset_circuit_breaker("test-swarm", 50.0)
            # Swarm reactivated with $50 budget
        """
        if swarm_id not in self.swarm_registry:
            raise ValueError(f"Unknown swarm: {swarm_id}")

        if new_budget <= 0:
            raise ValueError("New budget must be positive")

        profile = self.swarm_registry[swarm_id]
        old_budget = profile.current_budget_remaining

        # Restore budget
        profile.current_budget_remaining = new_budget

        # Clear failure count
        if swarm_id in self.failure_counts:
            old_failure_count = self.failure_counts[swarm_id]
            self.failure_counts[swarm_id] = 0
        else:
            old_failure_count = 0

        logger.info(
            f"✅ Circuit breaker RESET for '{swarm_id}': "
            f"budget ${old_budget} → ${new_budget}, "
            f"failures {old_failure_count} → 0"
        )

        # Notify IF.coordinator to resume sending tasks (stub)
        self._notify_coordinator_circuit_breaker(swarm_id, 'active')

        # Log reset to IF.witness (stub)
        self._log_circuit_breaker_reset(
            swarm_id=swarm_id,
            old_budget=old_budget,
            new_budget=new_budget,
            old_failure_count=old_failure_count
        )

    def _notify_coordinator_circuit_breaker(self, swarm_id: str, status: str):
        """
        Notify IF.coordinator of circuit breaker state change

        Stub for IF.coordinator integration. Will send event bus message
        to coordinator to update swarm availability status.

        Args:
            swarm_id: Swarm whose status changed
            status: New status ('circuit_breaker_tripped' or 'active')
        """
        # Stub for IF.coordinator integration
        # In production, would use:
        # asyncio.create_task(
        #     self.coordinator.event_bus.put(
        #         f'/swarms/{swarm_id}/status',
        #         status
        #     )
        # )
        logger.debug(
            f"IF.coordinator: event_bus.put('/swarms/{swarm_id}/status', '{status}')"
        )

    def _log_circuit_breaker_trip(self, swarm_id: str, reason: str):
        """
        Log circuit breaker trip to IF.witness with HIGH severity

        Stub for IF.witness integration (P0.4.3).

        Args:
            swarm_id: Swarm that was halted
            reason: Reason for circuit breaker trip
        """
        # Stub for IF.witness integration
        logger.debug(
            f"IF.witness: circuit_breaker_tripped("
            f"swarm_id={swarm_id}, "
            f"reason={reason}, "
            f"severity=HIGH, "
            f"timestamp={time.time()})"
        )

    def _log_circuit_breaker_reset(
        self,
        swarm_id: str,
        old_budget: float,
        new_budget: float,
        old_failure_count: int
    ):
        """
        Log circuit breaker reset to IF.witness

        Stub for IF.witness integration (P0.4.3).

        Args:
            swarm_id: Swarm that was reset
            old_budget: Budget before reset
            new_budget: Budget after reset
            old_failure_count: Failure count before reset
        """
        # Stub for IF.witness integration
        logger.debug(
            f"IF.witness: circuit_breaker_reset("
            f"swarm_id={swarm_id}, "
            f"old_budget=${old_budget:.2f}, "
            f"new_budget=${new_budget:.2f}, "
            f"old_failures={old_failure_count}, "
            f"approved_by='human_operator')"
        )

    def _escalate_to_human(self, swarm_id: str, issue: Dict):
        """
        ESCALATE pattern: Notify human for intervention

        This implements the S² principle: "Escalate, don't guess"

        Creates a formatted notification with:
        - Issue details
        - Investigation checklist
        - Reset command examples
        - Philosophical context (Ubuntu)

        Args:
            swarm_id: Swarm requiring intervention
            issue: Dictionary with issue details
        """
        failure_count = issue.get('failure_count', 0)
        budget = issue.get('budget_remaining', 0.0)

        notification = f"""
🚨 S² System Escalation Required

**Component**: IF.governor
**Swarm**: {swarm_id}
**Issue Type**: {issue.get('type', 'unknown')}
**Reason**: {issue.get('reason', 'unknown')}
**Failure Count**: {failure_count}
**Budget Remaining**: ${budget:.2f}

**Action Required**: Manual review and intervention

**To reset circuit breaker**:
```python
from infrafabric.governor import IFGovernor
governor.reset_circuit_breaker('{swarm_id}', new_budget=50.0)
```

**Or via CLI**:
```bash
if governor reset-circuit-breaker {swarm_id} --budget 50.0
```

**Investigation checklist**:
- [ ] Review IF.witness logs for root cause
- [ ] Check swarm reputation score
- [ ] Verify task assignments were appropriate
- [ ] Confirm budget allocation is sufficient
- [ ] Assess if swarm needs capability retraining
- [ ] Check for external service failures

**Philosophy**: Ubuntu ("I am because we are") - System health depends on collective well-being
"""

        # In production, this would send to notification system
        # For now, log to console
        logger.critical(notification)

    def __repr__(self) -> str:
        """String representation of IF.governor state"""
        return (
            f"IFGovernor(swarms={len(self.swarm_registry)}, "
            f"policy={self.policy})"
        )


class CapabilityMatchError(Exception):
    """Raised when no qualified swarm can be found for a task"""
    pass


class InsufficientBudgetError(Exception):
    """Raised when swarm has insufficient budget for operation"""
    pass
