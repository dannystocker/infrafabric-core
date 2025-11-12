"""
IF.governor - Capability-aware Resource and Budget Management

The governor is responsible for:
- Swarm capability matching (find best-fit swarms for tasks)
- Budget tracking and enforcement (prevent overspend)
- Circuit breaker pattern (detect and isolate failing swarms)
- Resource policy enforcement (cost limits, capability thresholds)

Key Algorithms:
- Jaccard similarity for capability matching (|intersection| / |union|)
- Combined scoring: (capability_match × reputation) / cost
- Circuit breaker: track failures, open circuit after threshold
"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
import time
from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
)


@dataclass
class MatchResult:
    """Result of capability matching operation."""
    swarm_id: str
    match_score: float  # Capability overlap (0.0-1.0)
    combined_score: float  # (match × reputation) / cost
    reputation_score: float
    cost_per_hour: float
    capabilities_matched: int
    capabilities_required: int


@dataclass
class SwarmStats:
    """Statistics for a swarm (failures, costs, etc.)."""
    swarm_id: str
    total_operations: int = 0
    failed_operations: int = 0
    consecutive_failures: int = 0
    total_cost: float = 0.0
    circuit_open: bool = False
    circuit_opened_at: Optional[float] = None


class IFGovernor:
    """
    Capability-aware resource and budget management service.

    The governor makes decisions about which swarms should handle which tasks
    based on:
    - Capability matching (does the swarm have required skills?)
    - Cost optimization (prefer cheaper swarms when capable)
    - Reputation (prefer reliable swarms)
    - Budget enforcement (prevent overspend)
    - Circuit breaker (isolate failing swarms)

    Example:
        policy = ResourcePolicy(
            max_swarms_per_task=3,
            max_cost_per_task=10.0,
            min_capability_match=0.7
        )

        governor = IFGovernor(coordinator, policy)

        # Register swarms
        governor.register_swarm(webrtc_profile)
        governor.register_swarm(sip_profile)

        # Find best swarm for task
        swarm_id = governor.find_qualified_swarm(
            required_capabilities=[Capability.INTEGRATION_WEBRTC],
            max_cost=20.0
        )
    """

    def __init__(self, coordinator, policy: ResourcePolicy):
        """
        Initialize IF.governor.

        Args:
            coordinator: IF.coordinator instance (for task coordination)
            policy: ResourcePolicy with constraints (cost, match threshold, etc.)
        """
        self.coordinator = coordinator
        self.policy = policy

        # Swarm registry: swarm_id → SwarmProfile
        self.swarm_registry: Dict[str, SwarmProfile] = {}

        # Swarm statistics: swarm_id → SwarmStats
        self.swarm_stats: Dict[str, SwarmStats] = {}

    # ==================== Swarm Registration ====================

    def register_swarm(self, profile: SwarmProfile) -> None:
        """
        Register a swarm with its capabilities and cost.

        Args:
            profile: SwarmProfile containing capabilities, cost, reputation, etc.

        Raises:
            ValueError: If profile is invalid
        """
        if not profile.swarm_id:
            raise ValueError("SwarmProfile must have swarm_id")

        if not profile.capabilities:
            raise ValueError("SwarmProfile must have at least one capability")

        self.swarm_registry[profile.swarm_id] = profile

        # Initialize stats if not present
        if profile.swarm_id not in self.swarm_stats:
            self.swarm_stats[profile.swarm_id] = SwarmStats(swarm_id=profile.swarm_id)

    def unregister_swarm(self, swarm_id: str) -> None:
        """
        Unregister a swarm (remove from registry).

        Args:
            swarm_id: ID of swarm to unregister
        """
        if swarm_id in self.swarm_registry:
            del self.swarm_registry[swarm_id]

    def get_swarm_profile(self, swarm_id: str) -> Optional[SwarmProfile]:
        """Get swarm profile by ID."""
        return self.swarm_registry.get(swarm_id)

    def get_all_swarms(self) -> List[SwarmProfile]:
        """Get all registered swarms."""
        return list(self.swarm_registry.values())

    def get_swarm_stats(self, swarm_id: str) -> Optional[SwarmStats]:
        """Get statistics for a swarm."""
        return self.swarm_stats.get(swarm_id)

    # ==================== Capability Matching (P0.2.2) ====================

    def find_qualified_swarm(
        self,
        required_capabilities: List[Capability],
        max_cost: Optional[float] = None
    ) -> Optional[str]:
        """
        Find the best-qualified swarm for a task based on capability matching.

        Selection criteria (in order):
        1. Capability match >= policy.min_capability_match (default 70%)
        2. Cost <= max_cost (if specified)
        3. Budget remaining > 0
        4. Circuit breaker not open
        5. Highest combined score: (capability_match × reputation) / cost

        Args:
            required_capabilities: List of capabilities needed for the task
            max_cost: Maximum cost per hour (optional, uses policy default)

        Returns:
            swarm_id of best-qualified swarm, or None if no qualified swarms

        Example:
            swarm_id = governor.find_qualified_swarm(
                required_capabilities=[
                    Capability.INTEGRATION_WEBRTC,
                    Capability.TESTING_INTEGRATION
                ],
                max_cost=20.0
            )
        """
        if not required_capabilities:
            raise ValueError("required_capabilities cannot be empty")

        # Use policy max cost if not specified
        if max_cost is None:
            max_cost = self.policy.max_cost_per_task

        candidates: List[Tuple[str, float, MatchResult]] = []

        for swarm_id, profile in self.swarm_registry.items():
            # Check circuit breaker
            stats = self.swarm_stats.get(swarm_id)
            if stats and stats.circuit_open:
                continue  # Circuit open, skip this swarm

            # Check budget
            if profile.current_budget_remaining <= 0:
                continue  # Budget exhausted

            # Check cost
            if profile.cost_per_hour > max_cost:
                continue  # Too expensive

            # Calculate capability match (Jaccard similarity)
            match_score = self._calculate_capability_match(
                profile.capabilities,
                required_capabilities
            )

            # Check against policy threshold
            if match_score < self.policy.min_capability_match:
                continue  # Below 70% threshold (or configured threshold)

            # Calculate combined score: (capability × reputation) / cost
            # Higher is better
            combined_score = (match_score * profile.reputation_score) / profile.cost_per_hour

            # Create match result
            match_result = MatchResult(
                swarm_id=swarm_id,
                match_score=match_score,
                combined_score=combined_score,
                reputation_score=profile.reputation_score,
                cost_per_hour=profile.cost_per_hour,
                capabilities_matched=len(set(profile.capabilities) & set(required_capabilities)),
                capabilities_required=len(required_capabilities)
            )

            candidates.append((swarm_id, combined_score, match_result))

        # No qualified swarms found
        if not candidates:
            return None

        # Sort by combined score (highest first)
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Return best swarm
        best_swarm_id = candidates[0][0]
        return best_swarm_id

    def find_all_qualified_swarms(
        self,
        required_capabilities: List[Capability],
        max_cost: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[MatchResult]:
        """
        Find all qualified swarms for a task, ranked by combined score.

        This is useful for "Gang Up on Blocker" pattern where multiple
        swarms may be needed.

        Args:
            required_capabilities: List of capabilities needed
            max_cost: Maximum cost per hour (optional)
            limit: Maximum number of swarms to return (optional)

        Returns:
            List of MatchResult objects, sorted by combined_score (best first)
        """
        if not required_capabilities:
            raise ValueError("required_capabilities cannot be empty")

        if max_cost is None:
            max_cost = self.policy.max_cost_per_task

        if limit is None:
            limit = self.policy.max_swarms_per_task

        candidates: List[MatchResult] = []

        for swarm_id, profile in self.swarm_registry.items():
            # Check circuit breaker
            stats = self.swarm_stats.get(swarm_id)
            if stats and stats.circuit_open:
                continue

            # Check budget
            if profile.current_budget_remaining <= 0:
                continue

            # Check cost
            if profile.cost_per_hour > max_cost:
                continue

            # Calculate capability match
            match_score = self._calculate_capability_match(
                profile.capabilities,
                required_capabilities
            )

            # Check threshold
            if match_score < self.policy.min_capability_match:
                continue

            # Calculate combined score
            combined_score = (match_score * profile.reputation_score) / profile.cost_per_hour

            match_result = MatchResult(
                swarm_id=swarm_id,
                match_score=match_score,
                combined_score=combined_score,
                reputation_score=profile.reputation_score,
                cost_per_hour=profile.cost_per_hour,
                capabilities_matched=len(set(profile.capabilities) & set(required_capabilities)),
                capabilities_required=len(required_capabilities)
            )

            candidates.append(match_result)

        # Sort by combined score
        candidates.sort(key=lambda x: x.combined_score, reverse=True)

        # Apply limit
        if limit:
            candidates = candidates[:limit]

        return candidates

    def _calculate_capability_match(
        self,
        swarm_capabilities: List[Capability],
        required_capabilities: List[Capability]
    ) -> float:
        """
        Calculate capability match using Jaccard similarity.

        Jaccard similarity = |intersection| / |required|

        NOTE: We use |required| as the denominator (not |union|) because
        we care about coverage of required capabilities. A swarm with extra
        capabilities doesn't hurt the match score.

        Args:
            swarm_capabilities: Capabilities provided by swarm
            required_capabilities: Capabilities required for task

        Returns:
            Match score between 0.0 and 1.0

        Examples:
            - Swarm has [A, B, C], task needs [A, B] → 2/2 = 1.0 (perfect match)
            - Swarm has [A, B], task needs [A, B, C] → 2/3 = 0.67 (missing C)
            - Swarm has [A], task needs [B, C] → 0/2 = 0.0 (no match)
        """
        if not required_capabilities:
            return 1.0  # No requirements = perfect match

        swarm_set = set(swarm_capabilities)
        required_set = set(required_capabilities)

        # Count how many required capabilities the swarm has
        intersection = swarm_set & required_set

        # Match score = coverage of required capabilities
        match_score = len(intersection) / len(required_set)

        return match_score

    # ==================== Circuit Breaker ====================

    def record_operation_success(self, swarm_id: str) -> None:
        """
        Record a successful operation for a swarm.

        This resets the consecutive failure count and may close the circuit
        if it was open.

        Args:
            swarm_id: ID of swarm that succeeded
        """
        if swarm_id not in self.swarm_stats:
            self.swarm_stats[swarm_id] = SwarmStats(swarm_id=swarm_id)

        stats = self.swarm_stats[swarm_id]
        stats.total_operations += 1
        stats.consecutive_failures = 0

        # Close circuit if it was open
        if stats.circuit_open:
            stats.circuit_open = False
            stats.circuit_opened_at = None

    def record_operation_failure(self, swarm_id: str) -> None:
        """
        Record a failed operation for a swarm.

        If consecutive failures exceed the circuit breaker threshold,
        the circuit will open and the swarm will be excluded from
        future task assignments.

        Args:
            swarm_id: ID of swarm that failed
        """
        if swarm_id not in self.swarm_stats:
            self.swarm_stats[swarm_id] = SwarmStats(swarm_id=swarm_id)

        stats = self.swarm_stats[swarm_id]
        stats.total_operations += 1
        stats.failed_operations += 1
        stats.consecutive_failures += 1

        # Check circuit breaker threshold
        if stats.consecutive_failures >= self.policy.circuit_breaker_failure_threshold:
            if not stats.circuit_open:
                stats.circuit_open = True
                stats.circuit_opened_at = time.time()

    def reset_circuit_breaker(self, swarm_id: str) -> None:
        """
        Manually reset the circuit breaker for a swarm.

        This is useful for recovering from temporary failures or after
        investigating and fixing the root cause.

        Args:
            swarm_id: ID of swarm to reset
        """
        if swarm_id in self.swarm_stats:
            stats = self.swarm_stats[swarm_id]
            stats.circuit_open = False
            stats.circuit_opened_at = None
            stats.consecutive_failures = 0

    # ==================== Budget Tracking (P0.2.3) ====================

    def allocate_budget(self, swarm_id: str, budget: float) -> None:
        """
        Allocate budget to a swarm.

        This sets the initial budget for a swarm. The budget will be
        decremented as costs are tracked via track_cost().

        Args:
            swarm_id: ID of swarm to allocate budget to
            budget: Budget amount in USD

        Raises:
            ValueError: If swarm not found or budget is negative
        """
        if swarm_id not in self.swarm_registry:
            raise ValueError(f"Unknown swarm: {swarm_id}")

        if budget < 0:
            raise ValueError(f"Budget must be non-negative, got {budget}")

        profile = self.swarm_registry[swarm_id]
        profile.current_budget_remaining = budget

    def track_cost(self, swarm_id: str, operation: str, cost: float) -> None:
        """
        Track cost for a swarm operation and deduct from budget.

        This method:
        1. Deducts cost from swarm's remaining budget
        2. Updates swarm statistics
        3. Opens circuit breaker if budget exhausted
        4. Optionally integrates with IF.optimise for cost tracking

        Args:
            swarm_id: ID of swarm that incurred the cost
            operation: Operation type (e.g., "task_execution", "api_call")
            cost: Cost amount in USD

        Raises:
            ValueError: If swarm not found or cost is negative

        Example:
            # Track cost of a task execution
            governor.track_cost("swarm-webrtc", "task_execution", 2.50)

            # Check remaining budget
            profile = governor.get_swarm_profile("swarm-webrtc")
            print(f"Remaining: ${profile.current_budget_remaining}")
        """
        if swarm_id not in self.swarm_registry:
            raise ValueError(f"Unknown swarm: {swarm_id}")

        if cost < 0:
            raise ValueError(f"Cost must be non-negative, got {cost}")

        # Get profile and stats
        profile = self.swarm_registry[swarm_id]
        stats = self.swarm_stats.get(swarm_id)
        if not stats:
            stats = SwarmStats(swarm_id=swarm_id)
            self.swarm_stats[swarm_id] = stats

        # Deduct cost from budget
        profile.current_budget_remaining -= cost

        # Update stats
        stats.total_cost += cost

        # Check for budget exhaustion
        if profile.current_budget_remaining <= 0:
            # Open circuit breaker
            if not stats.circuit_open:
                stats.circuit_open = True
                stats.circuit_opened_at = time.time()

        # TODO: Integrate with IF.optimise when available
        # from infrafabric.optimise import track_operation_cost
        # track_operation_cost(provider=swarm_id, operation=operation, cost=cost)

        # TODO: Integrate with IF.witness when available
        # from infrafabric.witness import log_operation
        # log_operation(
        #     component='IF.governor',
        #     operation='cost_tracked',
        #     params={
        #         'swarm_id': swarm_id,
        #         'operation': operation,
        #         'cost': cost,
        #         'remaining_budget': profile.current_budget_remaining
        #     }
        # )

    def get_budget_report(self) -> Dict[str, float]:
        """
        Get budget status for all registered swarms.

        Returns:
            Dictionary mapping swarm_id to remaining budget

        Example:
            report = governor.get_budget_report()
            for swarm_id, remaining in report.items():
                print(f"{swarm_id}: ${remaining:.2f}")
        """
        return {
            swarm_id: profile.current_budget_remaining
            for swarm_id, profile in self.swarm_registry.items()
        }

    def get_cost_report(self) -> Dict[str, float]:
        """
        Get total costs incurred by each swarm.

        Returns:
            Dictionary mapping swarm_id to total cost

        Example:
            costs = governor.get_cost_report()
            total_spend = sum(costs.values())
            print(f"Total spend: ${total_spend:.2f}")
        """
        return {
            swarm_id: stats.total_cost
            for swarm_id, stats in self.swarm_stats.items()
        }

    def is_budget_exhausted(self, swarm_id: str) -> bool:
        """
        Check if a swarm's budget is exhausted.

        Args:
            swarm_id: ID of swarm to check

        Returns:
            True if budget is exhausted (<= 0), False otherwise

        Raises:
            ValueError: If swarm not found
        """
        if swarm_id not in self.swarm_registry:
            raise ValueError(f"Unknown swarm: {swarm_id}")

        profile = self.swarm_registry[swarm_id]
        return profile.current_budget_remaining <= 0

    # ==================== Gang Up on Blocker (P0.2.5) ====================

    def request_help_for_blocker(
        self,
        blocked_swarm_id: str,
        required_capabilities: List[Capability],
        max_helpers: Optional[int] = None
    ) -> List[str]:
        """
        Request help from other swarms for a blocker (Gang Up on Blocker pattern).

        This method finds qualified swarms that can help resolve a blocker
        by matching required capabilities. It respects policy constraints
        (max swarms per task, budget limits) and excludes the blocked swarm.

        Args:
            blocked_swarm_id: ID of swarm that is blocked
            required_capabilities: Capabilities needed to resolve blocker
            max_helpers: Maximum number of helper swarms (defaults to policy limit)

        Returns:
            List of swarm IDs that can help (may be empty if no qualified swarms)

        Example:
            # Swarm is blocked on WebRTC integration
            helpers = governor.request_help_for_blocker(
                blocked_swarm_id="swarm-cli",
                required_capabilities=[Capability.INTEGRATION_WEBRTC],
                max_helpers=2
            )
            # Returns: ["swarm-webrtc", "swarm-sip"]
        """
        if not required_capabilities:
            raise ValueError("required_capabilities cannot be empty")

        if max_helpers is None:
            # Use policy limit minus 1 (for the blocked swarm itself)
            max_helpers = self.policy.max_swarms_per_task - 1

        # Find all qualified swarms
        qualified = self.find_all_qualified_swarms(
            required_capabilities=required_capabilities,
            max_cost=self.policy.max_cost_per_task,
            limit=max_helpers + 1  # Get extra in case blocked swarm is in list
        )

        # Filter out the blocked swarm and apply limit
        helpers = [
            match.swarm_id
            for match in qualified
            if match.swarm_id != blocked_swarm_id
        ][:max_helpers]

        return helpers
