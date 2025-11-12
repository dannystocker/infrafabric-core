"""Policy Engine for InfraFabric S² Resource Governance

This module implements centralized policy management and enforcement
for the IF.governor component.

Philosophy:
- Wu Lun (五倫) 朋友: Policies ensure fair resource allocation among peer swarms
- IF.ground Observable: All policy decisions are logged and auditable
- IF.TTT Trustworthy: Deterministic policy enforcement prevents favoritism

Task: P0.2.5 - Policy engine implementation
Est: 2h (Sonnet)
Session: 4 (SIP - External Expert Escalation)
Dependencies: P0.2.2 (capability matching), P0.2.3 (budget tracking), P0.2.4 (circuit breakers)
"""

import yaml
import json
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from infrafabric.schemas.capability import ResourcePolicy, Capability


@dataclass
class PolicyViolation:
    """Record of a policy violation

    Attributes:
        violation_type: Type of violation (e.g., "budget_exceeded", "max_swarms_exceeded")
        swarm_id: ID of swarm that violated policy
        task_id: ID of task related to violation
        details: Additional violation details
        timestamp: When violation occurred
    """
    violation_type: str
    swarm_id: str
    task_id: str
    details: Dict[str, Any]
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary"""
        return asdict(self)


class PolicyEngine:
    """Manage and enforce resource policies

    The PolicyEngine loads policies from YAML configuration and enforces
    constraints on swarm resource allocation, including:
    - Maximum swarms per task
    - Maximum cost per task
    - Minimum capability match requirements
    - Budget limits

    Example:
        >>> engine = PolicyEngine(config_path="config/policy.yaml")
        >>> valid, reason = engine.validate_assignment(
        ...     swarm_ids=["session-1", "session-2"],
        ...     task_budget=5.0
        ... )
        >>> assert valid
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize policy engine

        Args:
            config_path: Optional path to YAML config file
        """
        self.policy = ResourcePolicy()
        self.violations: List[PolicyViolation] = []

        if config_path:
            self.load_policy(config_path)

    def load_policy(self, config_path: str) -> None:
        """Load policy from YAML configuration

        Args:
            config_path: Path to YAML configuration file

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
            ValueError: If policy values are invalid

        Example YAML:
            resource_policy:
              max_swarms_per_task: 3
              max_cost_per_task: 10.0
              min_capability_match: 0.7
              circuit_breaker_failure_threshold: 3
              enable_budget_enforcement: true
              enable_reputation_scoring: true
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Policy config not found: {config_path}")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        if config is None:
            raise ValueError("Empty YAML configuration")

        policy_config = config.get('resource_policy', {})

        # Create policy from config
        self.policy = ResourcePolicy(
            max_swarms_per_task=policy_config.get('max_swarms_per_task', 3),
            max_cost_per_task=policy_config.get('max_cost_per_task', 10.0),
            min_capability_match=policy_config.get('min_capability_match', 0.7),
            circuit_breaker_failure_threshold=policy_config.get('circuit_breaker_failure_threshold', 3),
            enable_budget_enforcement=policy_config.get('enable_budget_enforcement', True),
            enable_reputation_scoring=policy_config.get('enable_reputation_scoring', True),
        )

    def validate_assignment(
        self,
        swarm_ids: List[str],
        task_budget: float,
        task_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Validate proposed task assignment against policies

        Args:
            swarm_ids: List of swarm IDs to assign to task
            task_budget: Estimated cost for task in USD
            task_id: Optional task ID for violation logging

        Returns:
            Tuple of (is_valid, reason)
            - is_valid: True if assignment is valid
            - reason: None if valid, otherwise description of violation

        Example:
            >>> engine = PolicyEngine()
            >>> valid, reason = engine.validate_assignment(
            ...     swarm_ids=["s1", "s2"],
            ...     task_budget=5.0
            ... )
            >>> assert valid
        """
        import time

        # Check max_swarms_per_task
        if len(swarm_ids) > self.policy.max_swarms_per_task:
            violation = PolicyViolation(
                violation_type="max_swarms_exceeded",
                swarm_id=",".join(swarm_ids),
                task_id=task_id or "unknown",
                details={
                    "swarm_count": len(swarm_ids),
                    "max_allowed": self.policy.max_swarms_per_task,
                },
                timestamp=time.time()
            )
            self.violations.append(violation)
            self._log_violation(violation)

            return False, (
                f"Too many swarms: {len(swarm_ids)} exceeds limit of "
                f"{self.policy.max_swarms_per_task}"
            )

        # Check max_cost_per_task
        if task_budget > self.policy.max_cost_per_task:
            violation = PolicyViolation(
                violation_type="budget_exceeded",
                swarm_id=",".join(swarm_ids),
                task_id=task_id or "unknown",
                details={
                    "task_budget": task_budget,
                    "max_allowed": self.policy.max_cost_per_task,
                },
                timestamp=time.time()
            )
            self.violations.append(violation)
            self._log_violation(violation)

            return False, (
                f"Task budget ${task_budget:.2f} exceeds limit of "
                f"${self.policy.max_cost_per_task:.2f}"
            )

        # Check for duplicate swarms
        if len(swarm_ids) != len(set(swarm_ids)):
            return False, "Duplicate swarms in assignment"

        # Check for empty assignment
        if not swarm_ids:
            return False, "No swarms assigned to task"

        return True, None

    def validate_capability_match(
        self,
        required_capabilities: List[Capability],
        swarm_capabilities: List[Capability]
    ) -> Tuple[bool, float]:
        """Validate capability match meets minimum threshold

        Uses Jaccard similarity to compute capability overlap.

        Args:
            required_capabilities: Required capabilities for task
            swarm_capabilities: Capabilities possessed by swarm

        Returns:
            Tuple of (meets_threshold, match_score)
            - meets_threshold: True if match >= min_capability_match
            - match_score: Capability overlap score (0.0-1.0)

        Example:
            >>> engine = PolicyEngine()
            >>> meets_threshold, score = engine.validate_capability_match(
            ...     required_capabilities=[Capability.INTEGRATION_SIP],
            ...     swarm_capabilities=[Capability.INTEGRATION_SIP, Capability.ARCHITECTURE_SECURITY]
            ... )
            >>> assert meets_threshold
            >>> assert score == 1.0  # 100% match (SIP required, SIP provided)
        """
        if not required_capabilities:
            return True, 1.0  # No requirements = perfect match

        if not swarm_capabilities:
            return False, 0.0  # No capabilities = no match

        # Compute Jaccard similarity (intersection / union)
        required_set = set(required_capabilities)
        swarm_set = set(swarm_capabilities)

        # For task assignment, we use: intersection / required
        # (Different from P0.2.2 which uses union for ranking)
        intersection = len(required_set & swarm_set)
        match_score = intersection / len(required_set)

        meets_threshold = match_score >= self.policy.min_capability_match

        return meets_threshold, match_score

    def check_budget_limit(
        self,
        swarm_id: str,
        remaining_budget: float
    ) -> Tuple[bool, Optional[str]]:
        """Check if swarm has sufficient budget remaining

        Args:
            swarm_id: Swarm identifier
            remaining_budget: Remaining budget in USD

        Returns:
            Tuple of (has_budget, reason)
            - has_budget: True if budget is available
            - reason: None if available, otherwise explanation
        """
        if not self.policy.enable_budget_enforcement:
            return True, None

        if remaining_budget <= 0:
            return False, f"Swarm {swarm_id} has exhausted budget"

        return True, None

    def get_violations(
        self,
        violation_type: Optional[str] = None,
        swarm_id: Optional[str] = None
    ) -> List[PolicyViolation]:
        """Get policy violations (for auditing)

        Args:
            violation_type: Optional filter by violation type
            swarm_id: Optional filter by swarm ID

        Returns:
            List of violations matching filters
        """
        violations = self.violations

        if violation_type:
            violations = [v for v in violations if v.violation_type == violation_type]

        if swarm_id:
            violations = [v for v in violations if swarm_id in v.swarm_id]

        return violations

    def get_policy_summary(self) -> Dict[str, Any]:
        """Get current policy configuration

        Returns:
            Dictionary with policy settings and statistics
        """
        return {
            "policy": self.policy.to_dict(),
            "violations": {
                "total": len(self.violations),
                "by_type": self._count_violations_by_type(),
            }
        }

    def _count_violations_by_type(self) -> Dict[str, int]:
        """Count violations by type"""
        counts: Dict[str, int] = {}
        for violation in self.violations:
            counts[violation.violation_type] = counts.get(violation.violation_type, 0) + 1
        return counts

    def _log_violation(self, violation: PolicyViolation) -> None:
        """Log policy violation to IF.witness

        Args:
            violation: Policy violation to log
        """
        # Import here to avoid circular dependency
        try:
            from infrafabric.witness import log_operation
            log_operation(
                component='IF.governor.policy',
                operation='policy_violation',
                params=violation.to_dict(),
                severity='WARNING'
            )
        except ImportError:
            # IF.witness not available - log to console
            import sys
            import json
            print(
                f"[POLICY VIOLATION] {json.dumps(violation.to_dict())}",
                file=sys.stderr
            )

    def export_violations_json(self, output_path: str) -> None:
        """Export violations to JSON file for analysis

        Args:
            output_path: Path to write JSON file
        """
        violations_data = [v.to_dict() for v in self.violations]

        with open(output_path, 'w') as f:
            json.dump({
                "policy": self.policy.to_dict(),
                "violations": violations_data,
                "summary": self.get_policy_summary()
            }, f, indent=2)


# Integration helpers for IFGovernor (P0.2.2, P0.2.3, P0.2.4)
def extract_required_capabilities(blocker_description: dict) -> List[Capability]:
    """Extract required capabilities from blocker description

    This is a helper function for IFGovernor.request_help_for_blocker().

    Args:
        blocker_description: Dictionary describing the blocker
            Expected keys: "required_skills", "error_type", "context"

    Returns:
        List of required capabilities

    Example:
        >>> desc = {
        ...     "error_type": "integration_failure",
        ...     "required_skills": ["integration:sip", "architecture:security"]
        ... }
        >>> caps = extract_required_capabilities(desc)
        >>> assert Capability.INTEGRATION_SIP in caps
    """
    capabilities = []

    # Check for explicit required_skills
    if "required_skills" in blocker_description:
        for skill_str in blocker_description["required_skills"]:
            cap = Capability.from_string(skill_str)
            if cap:
                capabilities.append(cap)

    # Infer capabilities from error_type
    error_type = blocker_description.get("error_type", "")

    error_capability_map = {
        "integration_failure": [Capability.INFRA_DISTRIBUTED_SYSTEMS],
        "security_issue": [Capability.ARCHITECTURE_SECURITY],
        "performance_degradation": [Capability.ARCHITECTURE_PERFORMANCE],
        "test_failure": [Capability.TESTING_INTEGRATION],
        "documentation_gap": [Capability.DOCS_TECHNICAL_WRITING],
    }

    if error_type in error_capability_map:
        capabilities.extend(error_capability_map[error_type])

    # Remove duplicates while preserving order
    seen = set()
    unique_caps = []
    for cap in capabilities:
        if cap not in seen:
            seen.add(cap)
            unique_caps.append(cap)

    return unique_caps


__all__ = [
    "PolicyEngine",
    "PolicyViolation",
    "extract_required_capabilities",
]
