"""IF.governor - Capability-Aware Resource Management (P0.2.2)

This module implements intelligent task assignment based on swarm capabilities,
cost, and reputation. The governor ensures tasks are assigned to qualified
swarms that meet the 70% capability match threshold.

Philosophy:
- IF.TTT Trustworthy: Objective capability scoring prevents favoritism
- IF.ground Observable: All assignment decisions are auditable
- Wu Lun (朋友): Fair evaluation of peer swarms based on capabilities

Task: P0.2.2 - Implement 70%+ match algorithm
Est: 2h (Sonnet)
Session: 4 (SIP)
Dependencies: P0.2.1 (Capability schema)
Unblocks: P0.2.4 (Circuit breakers), P0.2.6 (Integration tests)
"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
import json
from infrafabric.schemas.capability import Capability, SwarmProfile, ResourcePolicy


@dataclass
class MatchScore:
    """Capability match score for a swarm

    Attributes:
        swarm_id: Swarm identifier
        capability_match: Capability overlap ratio (0.0-1.0)
        reputation: Swarm reputation score (0.0-1.0)
        cost_per_hour: Hourly cost
        combined_score: (capability × reputation) / cost
        qualified: Whether swarm meets 70% threshold
    """
    swarm_id: str
    capability_match: float
    reputation: float
    cost_per_hour: float
    combined_score: float
    qualified: bool

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary"""
        return {
            "swarm_id": self.swarm_id,
            "capability_match": self.capability_match,
            "reputation": self.reputation,
            "cost_per_hour": self.cost_per_hour,
            "combined_score": self.combined_score,
            "qualified": self.qualified,
        }


class IFGovernor:
    """Capability-aware resource and budget management

    The IFGovernor handles smart task assignment based on:
    - Capability matching (Jaccard similarity ≥70%)
    - Swarm reputation (from IF.chassis reputation system)
    - Cost optimization (lower cost preferred)
    - Budget tracking

    The governor uses a combined score:
        (capability_match × reputation) / cost

    This ensures qualified, high-reputation, cost-effective swarms are
    prioritized for task assignment.

    Example:
        >>> policy = ResourcePolicy(min_capability_match=0.7)
        >>> governor = IFGovernor(coordinator=None, policy=policy)
        >>> governor.register_swarm(SwarmProfile(
        ...     swarm_id="session-4-sip",
        ...     capabilities=[Capability.INTEGRATION_SIP],
        ...     cost_per_hour=2.0,
        ...     reputation_score=0.95,
        ...     current_budget_remaining=10.0,
        ...     model="sonnet"
        ... ))
        >>> swarm_id = governor.find_qualified_swarm(
        ...     required_capabilities=[Capability.INTEGRATION_SIP],
        ...     max_cost=5.0
        ... )
        >>> assert swarm_id == "session-4-sip"
    """

    def __init__(self, coordinator=None, policy: Optional[ResourcePolicy] = None):
        """Initialize IF.governor

        Args:
            coordinator: IF.coordinator instance (optional)
            policy: Resource policy (default: min_capability_match=0.7)
        """
        self.coordinator = coordinator
        self.policy = policy or ResourcePolicy()
        self.swarm_registry: Dict[str, SwarmProfile] = {}
        self.assignment_history: List[Dict[str, any]] = []

    def register_swarm(self, profile: SwarmProfile) -> None:
        """Register swarm with capabilities

        Args:
            profile: Swarm profile with capabilities, cost, reputation

        Example:
            >>> governor = IFGovernor()
            >>> governor.register_swarm(SwarmProfile(
            ...     swarm_id="session-1-ndi",
            ...     capabilities=[Capability.INTEGRATION_NDI],
            ...     cost_per_hour=1.5,
            ...     reputation_score=0.90,
            ...     current_budget_remaining=15.0,
            ...     model="haiku"
            ... ))
        """
        self.swarm_registry[profile.swarm_id] = profile

        self._log_operation(
            operation='swarm_registered',
            params={
                'swarm_id': profile.swarm_id,
                'capabilities': [c.value for c in profile.capabilities],
                'cost_per_hour': profile.cost_per_hour,
                'reputation': profile.reputation_score
            }
        )

    def unregister_swarm(self, swarm_id: str) -> bool:
        """Unregister swarm from governor

        Args:
            swarm_id: Swarm identifier

        Returns:
            True if swarm was registered, False otherwise
        """
        if swarm_id in self.swarm_registry:
            del self.swarm_registry[swarm_id]
            self._log_operation(
                operation='swarm_unregistered',
                params={'swarm_id': swarm_id}
            )
            return True
        return False

    def find_qualified_swarm(
        self,
        required_capabilities: List[Capability],
        max_cost: float
    ) -> Optional[str]:
        """Find best swarm based on capability match, reputation, and cost

        Uses Jaccard similarity for capability matching:
            overlap = len(swarm_caps ∩ required_caps) / len(required_caps)

        Combined score for ranking:
            score = (capability_match × reputation) / cost

        Args:
            required_capabilities: List of required capabilities
            max_cost: Maximum acceptable hourly cost

        Returns:
            Best-scoring swarm ID if qualified swarm found, None otherwise

        Example:
            >>> governor = IFGovernor()
            >>> # Register two swarms
            >>> governor.register_swarm(SwarmProfile(
            ...     swarm_id="expensive",
            ...     capabilities=[Capability.INTEGRATION_SIP],
            ...     cost_per_hour=20.0,
            ...     reputation_score=1.0,
            ...     current_budget_remaining=5.0,
            ...     model="opus"
            ... ))
            >>> governor.register_swarm(SwarmProfile(
            ...     swarm_id="cheap",
            ...     capabilities=[Capability.INTEGRATION_SIP],
            ...     cost_per_hour=2.0,
            ...     reputation_score=0.95,
            ...     current_budget_remaining=10.0,
            ...     model="sonnet"
            ... ))
            >>> # Cheap swarm should win due to better score
            >>> result = governor.find_qualified_swarm(
            ...     [Capability.INTEGRATION_SIP],
            ...     max_cost=25.0
            ... )
            >>> assert result == "cheap"
        """
        if not required_capabilities:
            return None

        candidates = []

        for swarm_id, profile in self.swarm_registry.items():
            # Calculate capability overlap (Jaccard similarity)
            required_set = set(required_capabilities)
            profile_set = set(profile.capabilities)
            intersection = len(required_set & profile_set)

            # Capability match: intersection / required (not union!)
            capability_match = intersection / len(required_capabilities)

            # Filter by policy (70% threshold)
            if capability_match < self.policy.min_capability_match:
                continue  # Not qualified

            # Filter by cost
            if profile.cost_per_hour > max_cost:
                continue  # Too expensive

            # Filter by budget
            if profile.current_budget_remaining <= 0:
                continue  # Budget exhausted

            # Combined score: (capability × reputation) / cost
            # Higher is better
            combined_score = (
                capability_match * profile.reputation_score
            ) / profile.cost_per_hour

            match_score = MatchScore(
                swarm_id=swarm_id,
                capability_match=capability_match,
                reputation=profile.reputation_score,
                cost_per_hour=profile.cost_per_hour,
                combined_score=combined_score,
                qualified=True
            )

            candidates.append(match_score)

        if not candidates:
            self._log_operation(
                operation='no_qualified_swarm',
                params={
                    'required_capabilities': [c.value for c in required_capabilities],
                    'max_cost': max_cost,
                    'registered_swarms': len(self.swarm_registry)
                },
                severity='WARNING'
            )
            return None

        # Sort by combined score (highest first)
        candidates.sort(key=lambda x: x.combined_score, reverse=True)

        # Return highest-scoring swarm
        best_match = candidates[0]

        self._log_operation(
            operation='swarm_matched',
            params={
                'swarm_id': best_match.swarm_id,
                'capability_match': best_match.capability_match,
                'reputation': best_match.reputation,
                'cost_per_hour': best_match.cost_per_hour,
                'combined_score': best_match.combined_score,
                'candidates_evaluated': len(candidates)
            }
        )

        # Record assignment
        self.assignment_history.append({
            'swarm_id': best_match.swarm_id,
            'required_capabilities': [c.value for c in required_capabilities],
            'match_score': best_match.to_dict()
        })

        return best_match.swarm_id

    def calculate_match_scores(
        self,
        required_capabilities: List[Capability],
        max_cost: float
    ) -> List[MatchScore]:
        """Calculate match scores for all swarms (for debugging/testing)

        Args:
            required_capabilities: List of required capabilities
            max_cost: Maximum acceptable hourly cost

        Returns:
            List of MatchScore objects, sorted by combined_score descending
        """
        if not required_capabilities:
            return []

        scores = []

        for swarm_id, profile in self.swarm_registry.items():
            # Calculate capability overlap
            required_set = set(required_capabilities)
            profile_set = set(profile.capabilities)
            intersection = len(required_set & profile_set)
            capability_match = intersection / len(required_capabilities)

            # Check qualification
            qualified = (
                capability_match >= self.policy.min_capability_match and
                profile.cost_per_hour <= max_cost and
                profile.current_budget_remaining > 0
            )

            # Combined score
            combined_score = (
                capability_match * profile.reputation_score
            ) / profile.cost_per_hour

            scores.append(MatchScore(
                swarm_id=swarm_id,
                capability_match=capability_match,
                reputation=profile.reputation_score,
                cost_per_hour=profile.cost_per_hour,
                combined_score=combined_score,
                qualified=qualified
            ))

        # Sort by combined score
        scores.sort(key=lambda x: x.combined_score, reverse=True)
        return scores

    def get_swarm_profile(self, swarm_id: str) -> Optional[SwarmProfile]:
        """Get registered swarm profile

        Args:
            swarm_id: Swarm identifier

        Returns:
            SwarmProfile if registered, None otherwise
        """
        return self.swarm_registry.get(swarm_id)

    def get_all_swarms(self) -> List[SwarmProfile]:
        """Get all registered swarms

        Returns:
            List of all registered swarm profiles
        """
        return list(self.swarm_registry.values())

    def get_assignment_history(
        self,
        swarm_id: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """Get assignment history

        Args:
            swarm_id: Optional filter by swarm ID

        Returns:
            List of assignment records
        """
        if swarm_id:
            return [
                a for a in self.assignment_history
                if a['swarm_id'] == swarm_id
            ]
        return self.assignment_history

    def track_cost(
        self,
        swarm_id: str,
        operation: str,
        cost: float
    ) -> None:
        """Track costs and enforce budget limits (P0.2.3)

        Deducts cost from swarm's remaining budget and logs to IF.witness
        and IF.optimise. If budget is exhausted, prevents further task
        assignment (handled by find_qualified_swarm budget check).

        Args:
            swarm_id: Swarm identifier
            operation: Operation description (e.g., "task_execution", "sip_call")
            cost: Cost in USD

        Raises:
            ValueError: If swarm_id is not registered

        Example:
            >>> governor = IFGovernor()
            >>> governor.register_swarm(SwarmProfile(
            ...     "session-4", [Capability.INTEGRATION_SIP],
            ...     2.0, 0.95, 10.0, "sonnet"
            ... ))
            >>> governor.track_cost("session-4", "sip_integration", 0.50)
            >>> profile = governor.get_swarm_profile("session-4")
            >>> assert profile.current_budget_remaining == 9.50
        """
        if swarm_id not in self.swarm_registry:
            raise ValueError(f"Unknown swarm: {swarm_id}")

        profile = self.swarm_registry[swarm_id]
        old_budget = profile.current_budget_remaining
        profile.current_budget_remaining -= cost

        # Log cost to IF.optimise (if available)
        try:
            from infrafabric.optimise import track_operation_cost
            track_operation_cost(
                provider=swarm_id,
                operation=operation,
                cost=cost
            )
        except ImportError:
            # IF.optimise not available - that's OK
            pass

        # Log to IF.witness
        self._log_operation(
            operation='cost_tracked',
            params={
                'swarm_id': swarm_id,
                'operation': operation,
                'cost': cost,
                'old_budget': old_budget,
                'remaining_budget': profile.current_budget_remaining
            }
        )

        # Check if budget exhausted
        if profile.current_budget_remaining <= 0:
            self._log_operation(
                operation='budget_exhausted',
                params={
                    'swarm_id': swarm_id,
                    'final_budget': profile.current_budget_remaining
                },
                severity='WARNING'
            )
            # TODO: P0.2.4 - Call circuit breaker when implemented
            # self._trip_circuit_breaker(swarm_id, reason='budget_exhausted')

    def get_budget_report(self) -> Dict[str, float]:
        """Get budget status for all swarms

        Returns:
            Dictionary mapping swarm_id to remaining budget

        Example:
            >>> governor = IFGovernor()
            >>> governor.register_swarm(SwarmProfile(
            ...     "session-4", [Capability.INTEGRATION_SIP],
            ...     2.0, 0.95, 10.0, "sonnet"
            ... ))
            >>> report = governor.get_budget_report()
            >>> assert report["session-4"] == 10.0
        """
        return {
            swarm_id: profile.current_budget_remaining
            for swarm_id, profile in self.swarm_registry.items()
        }

    def get_total_cost_tracked(self) -> float:
        """Get total cost tracked across all swarms

        Calculates total spend based on budget deductions from initial
        budgets (not directly tracked, inferred from remaining budgets).

        Returns:
            Total cost tracked in USD

        Note:
            This is an approximation based on current budget status.
            For accurate cost tracking, use IF.optimise integration.
        """
        # This is a simplified calculation
        # In reality, we'd need to track initial budgets separately
        # For now, we can't calculate total spend without initial values
        # This will be improved when IF.optimise is integrated
        return 0.0  # Placeholder until IF.optimise integration

    def _log_operation(
        self,
        operation: str,
        params: Dict[str, any],
        severity: str = 'INFO'
    ) -> None:
        """Log operation to IF.witness

        Args:
            operation: Operation name
            params: Operation parameters
            severity: Log severity
        """
        try:
            from infrafabric.witness import log_operation
            log_operation(
                component='IF.governor',
                operation=operation,
                params=params,
                severity=severity
            )
        except ImportError:
            # IF.witness not available - log to stderr
            import sys
            print(
                f"[IF.governor] {severity}: {operation} - {json.dumps(params)}",
                file=sys.stderr
            )


__all__ = [
    "IFGovernor",
    "MatchScore",
]
