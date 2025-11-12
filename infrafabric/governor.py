"""
IF.governor - Capability-aware Resource and Budget Management

Implements intelligent task assignment with 70%+ capability matching threshold.
Addresses IF Bug #2: Reduces 57% cost waste to <10% through capability matching.

Integrates:
- P0.2.1: Capability Registry Schema
- F6.3: Assignment Scoring Algorithm
- F6.11: Reputation Scoring System
"""

from typing import List, Optional, Dict, Tuple, Any
import time
from dataclasses import dataclass
from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
    TaskRequirements,
    BloomPattern
)


@dataclass
class MatchResult:
    """Result of capability matching"""
    swarm_id: str
    capability_match_score: float  # 0.0-1.0 (Jaccard similarity)
    combined_score: float          # (cap_match × reputation) / cost
    reputation_score: float
    cost_per_hour: float
    bloom_match: bool              # Does bloom pattern match?
    qualified: bool                # Meets 70%+ threshold?
    reason: str                    # Why qualified or not


class IFGovernor:
    """
    Capability-aware resource and budget management for InfraFabric

    Core responsibilities:
    - Register swarms with capabilities (P0.2.1 schema)
    - Match tasks to qualified swarms (70%+ threshold from F6.3)
    - Track budgets and enforce limits (Bug #2 fix)
    - Integrate with IF.coordinator for task assignment
    """

    def __init__(self, coordinator=None, policy: Optional[ResourcePolicy] = None):
        """
        Initialize IF.governor

        Args:
            coordinator: IF.coordinator instance (optional, for integration)
            policy: ResourcePolicy with governance constraints
        """
        self.coordinator = coordinator
        self.policy = policy or ResourcePolicy()
        self.swarm_registry: Dict[str, SwarmProfile] = {}

        # Metrics
        self.total_matches = 0
        self.successful_matches = 0
        self.failed_matches = 0
        self.total_cost_allocated = 0.0

    def register_swarm(self, profile: SwarmProfile) -> bool:
        """
        Register swarm with capabilities

        Args:
            profile: SwarmProfile from P0.2.1 schema

        Returns:
            True if registration successful
        """
        from infrafabric.schemas.capability import validate_swarm_profile

        # Validate profile
        is_valid, error = validate_swarm_profile(profile)
        if not is_valid:
            print(f"[IF.governor] ❌ Swarm registration failed: {error}")
            return False

        # Register
        self.swarm_registry[profile.swarm_id] = profile
        print(f"[IF.governor] ✓ Registered swarm: {profile.swarm_id} "
              f"({len(profile.capabilities)} capabilities, "
              f"${profile.cost_per_hour}/hr, "
              f"reputation={profile.reputation_score:.2f})")

        return True

    def unregister_swarm(self, swarm_id: str) -> bool:
        """Remove swarm from registry"""
        if swarm_id in self.swarm_registry:
            del self.swarm_registry[swarm_id]
            print(f"[IF.governor] Unregistered swarm: {swarm_id}")
            return True
        return False

    def get_swarm(self, swarm_id: str) -> Optional[SwarmProfile]:
        """Get swarm profile by ID"""
        return self.swarm_registry.get(swarm_id)

    def find_qualified_swarms(
        self,
        task: TaskRequirements,
        max_results: Optional[int] = None
    ) -> List[MatchResult]:
        """
        Find all qualified swarms for a task (70%+ capability match)

        Implements F6.3 Assignment Scoring Algorithm:
        Combined Score = (capability_match × reputation) / cost

        Args:
            task: TaskRequirements with required capabilities
            max_results: Maximum number of results to return (default: all)

        Returns:
            List of MatchResult, sorted by combined_score (highest first)
        """
        self.total_matches += 1
        results = []

        for swarm_id, profile in self.swarm_registry.items():
            result = self._calculate_match(profile, task)
            results.append(result)

        # Sort by combined score (highest first)
        results.sort(key=lambda r: r.combined_score, reverse=True)

        # Filter to qualified swarms only (70%+ threshold)
        qualified_results = [r for r in results if r.qualified]

        # Track metrics
        if qualified_results:
            self.successful_matches += 1
        else:
            self.failed_matches += 1

        # Limit results if requested
        if max_results:
            qualified_results = qualified_results[:max_results]

        return qualified_results

    def find_best_swarm(self, task: TaskRequirements) -> Optional[MatchResult]:
        """
        Find single best swarm for a task

        Args:
            task: TaskRequirements with required capabilities

        Returns:
            Best MatchResult or None if no qualified swarm found
        """
        qualified = self.find_qualified_swarms(task, max_results=1)

        if qualified:
            return qualified[0]
        return None

    def _calculate_match(
        self,
        swarm: SwarmProfile,
        task: TaskRequirements
    ) -> MatchResult:
        """
        Calculate capability match score for a swarm

        Uses Jaccard similarity for capability overlap:
        Overlap = |required ∩ available| / |required|

        Combined score from F6.3:
        Score = (capability_match × reputation) / cost

        Args:
            swarm: SwarmProfile to evaluate
            task: TaskRequirements to match against

        Returns:
            MatchResult with scores and qualification status
        """
        # Calculate capability overlap (Jaccard similarity)
        required_caps = set(task.required_capabilities)
        available_caps = swarm.get_capability_names()

        # Check if swarm has each required capability at minimum skill level
        matching_caps = set()
        for req_cap in required_caps:
            if swarm.has_capability(req_cap, task.min_skill_level):
                matching_caps.add(req_cap)

        capability_match = len(matching_caps) / len(required_caps) if required_caps else 0.0

        # Check bloom pattern match (optional preference)
        bloom_match = True
        if task.preferred_bloom_pattern:
            bloom_match = (swarm.bloom_pattern == task.preferred_bloom_pattern)

        # Check constraints
        within_budget = swarm.cost_per_hour <= task.max_cost_per_hour
        has_budget = swarm.has_budget()
        meets_reputation = swarm.reputation_score >= task.min_reputation
        is_active = swarm.active

        # Calculate combined score (F6.3 algorithm)
        # Score = (capability_match × reputation) / cost
        # Higher is better
        if swarm.cost_per_hour > 0:
            combined_score = (capability_match * swarm.reputation_score) / swarm.cost_per_hour
        else:
            combined_score = 0.0

        # Apply bloom pattern bonus (10% boost if matches)
        if bloom_match and task.preferred_bloom_pattern:
            combined_score *= 1.10

        # Determine qualification
        qualified = (
            capability_match >= self.policy.min_capability_match and  # 70%+ threshold
            within_budget and
            has_budget and
            meets_reputation and
            is_active
        )

        # Generate reason
        if not qualified:
            reasons = []
            if capability_match < self.policy.min_capability_match:
                reasons.append(f"capability match {capability_match:.0%} < {self.policy.min_capability_match:.0%}")
            if not within_budget:
                reasons.append(f"cost ${swarm.cost_per_hour}/hr > ${task.max_cost_per_hour}/hr budget")
            if not has_budget:
                reasons.append("budget exhausted")
            if not meets_reputation:
                reasons.append(f"reputation {swarm.reputation_score:.2f} < {task.min_reputation:.2f}")
            if not is_active:
                reasons.append("swarm inactive")
            reason = "Not qualified: " + ", ".join(reasons)
        else:
            reason = f"Qualified: {capability_match:.0%} capability match, score={combined_score:.4f}"

        return MatchResult(
            swarm_id=swarm.swarm_id,
            capability_match_score=capability_match,
            combined_score=combined_score,
            reputation_score=swarm.reputation_score,
            cost_per_hour=swarm.cost_per_hour,
            bloom_match=bloom_match,
            qualified=qualified,
            reason=reason
        )

    def assign_task_to_swarm(
        self,
        task_id: str,
        swarm_id: str,
        estimated_hours: float = 1.0
    ) -> bool:
        """
        Assign task to swarm and reserve budget

        Args:
            task_id: Task identifier
            swarm_id: Swarm to assign task to
            estimated_hours: Estimated task duration in hours

        Returns:
            True if assignment successful
        """
        swarm = self.get_swarm(swarm_id)
        if not swarm:
            print(f"[IF.governor] ❌ Swarm {swarm_id} not found")
            return False

        # Calculate cost
        estimated_cost = swarm.cost_per_hour * estimated_hours

        # Check budget
        if not swarm.has_budget(estimated_cost):
            print(f"[IF.governor] ❌ Insufficient budget for {swarm_id}: "
                  f"need ${estimated_cost:.2f}, have ${swarm.current_budget_remaining:.2f}")
            return False

        # Reserve budget (will be finalized on task completion)
        swarm.current_budget_remaining -= estimated_cost
        self.total_cost_allocated += estimated_cost

        print(f"[IF.governor] ✓ Assigned task {task_id} to {swarm_id} "
              f"(est. ${estimated_cost:.2f}, "
              f"remaining budget: ${swarm.current_budget_remaining:.2f})")

        return True

    def complete_task(
        self,
        task_id: str,
        swarm_id: str,
        actual_hours: float,
        success: bool = True
    ) -> bool:
        """
        Mark task as complete and finalize costs

        Args:
            task_id: Task identifier
            swarm_id: Swarm that completed the task
            actual_hours: Actual task duration in hours
            success: Whether task completed successfully

        Returns:
            True if completion recorded successfully
        """
        swarm = self.get_swarm(swarm_id)
        if not swarm:
            return False

        # Calculate actual cost
        actual_cost = swarm.cost_per_hour * actual_hours

        # Update swarm stats
        swarm.total_cost_spent += actual_cost
        swarm.total_tasks_completed += 1
        swarm.last_active = time.time()

        print(f"[IF.governor] ✓ Task {task_id} completed by {swarm_id} "
              f"(actual: ${actual_cost:.2f}, "
              f"total spent: ${swarm.total_cost_spent:.2f})")

        return True

    def get_metrics(self) -> Dict[str, Any]:
        """Get IF.governor metrics"""
        return {
            'total_swarms': len(self.swarm_registry),
            'active_swarms': sum(1 for s in self.swarm_registry.values() if s.active),
            'total_matches_attempted': self.total_matches,
            'successful_matches': self.successful_matches,
            'failed_matches': self.failed_matches,
            'match_success_rate': self.successful_matches / self.total_matches if self.total_matches > 0 else 0.0,
            'total_cost_allocated': self.total_cost_allocated,
            'policy': self.policy.to_dict()
        }

    def get_swarm_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all registered swarms"""
        return [
            {
                'swarm_id': s.swarm_id,
                'name': s.name,
                'model': s.model,
                'num_capabilities': len(s.capabilities),
                'cost_per_hour': s.cost_per_hour,
                'budget_remaining': s.current_budget_remaining,
                'reputation': s.reputation_score,
                'reputation_tier': s.reputation_tier,
                'bloom_pattern': s.bloom_pattern.value,
                'tasks_completed': s.total_tasks_completed,
                'active': s.active
            }
            for s in self.swarm_registry.values()
        ]


# Convenience function for IF.coordinator integration
async def register_capability(payload: Dict[str, Any]) -> Dict[str, bool]:
    """
    Register capability with IF.governor (called by IF.talent Deploy phase)

    Args:
        payload: Capability registration payload from IF.talent

    Returns:
        Dictionary with success status
    """
    # This is a placeholder for future IF.coordinator integration
    # Real implementation will store in etcd/NATS
    print(f"[IF.governor] Registered capability: {payload.get('capability_id')}")
    return {'success': True}
