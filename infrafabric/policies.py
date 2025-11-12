"""
IF.policies - Centralized Policy Management and Enforcement

The policy engine is responsible for:
- Loading resource policies from YAML configuration
- Validating task assignments against policies
- Enforcing constraints (max swarms, max cost, capability match)
- Policy violation detection and logging
"""

import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path
from infrafabric.schemas.capability import ResourcePolicy


class PolicyEngine:
    """
    Centralized policy management for InfraFabric.

    The PolicyEngine loads, validates, and enforces resource policies
    that govern swarm allocation, budget limits, and capability matching.

    Example:
        # Load policy from YAML
        engine = PolicyEngine("config/policy.yaml")

        # Validate task assignment
        if engine.validate_assignment(["swarm-1", "swarm-2"], task_budget=5.0):
            print("Assignment valid")

        # Check specific constraints
        if engine.check_max_swarms(["swarm-1", "swarm-2", "swarm-3", "swarm-4"]):
            print("Too many swarms!")
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize PolicyEngine.

        Args:
            config_path: Path to YAML policy configuration (optional)
        """
        # Default policy
        self.policy = ResourcePolicy()

        # Load from file if provided
        if config_path:
            self.load_policy(config_path)

    def load_policy(self, config_path: str) -> None:
        """
        Load resource policy from YAML configuration file.

        Args:
            config_path: Path to YAML policy file

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
            ValueError: If policy configuration is invalid

        Example YAML:
            resource_policy:
              max_swarms_per_task: 3
              max_cost_per_task: 10.0
              min_capability_match: 0.7
              circuit_breaker_failure_threshold: 3
              prefer_reputation: true
              allow_budget_overdraft: 1.1
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Policy configuration not found: {config_path}")

        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        if not isinstance(config, dict):
            raise ValueError("Policy configuration must be a dictionary")

        policy_config = config.get('resource_policy', {})
        if not isinstance(policy_config, dict):
            raise ValueError("'resource_policy' must be a dictionary")

        # Create ResourcePolicy with loaded configuration
        self.policy = ResourcePolicy(
            max_swarms_per_task=policy_config.get('max_swarms_per_task', 3),
            max_cost_per_task=policy_config.get('max_cost_per_task', 10.0),
            min_capability_match=policy_config.get('min_capability_match', 0.7),
            circuit_breaker_failure_threshold=policy_config.get('circuit_breaker_failure_threshold', 3),
            prefer_reputation=policy_config.get('prefer_reputation', True),
            allow_budget_overdraft=policy_config.get('allow_budget_overdraft', 1.1)
        )

    def validate_assignment(
        self,
        swarm_ids: List[str],
        task_budget: float
    ) -> bool:
        """
        Validate proposed task assignment against all policies.

        Args:
            swarm_ids: List of swarm IDs to assign to task
            task_budget: Budget allocated for the task

        Returns:
            True if assignment is valid, False if policy violation

        Example:
            valid = engine.validate_assignment(
                swarm_ids=["swarm-1", "swarm-2"],
                task_budget=8.0
            )
        """
        # Check max swarms per task
        if not self.check_max_swarms(swarm_ids):
            return False

        # Check max cost per task
        if not self.check_max_cost(task_budget):
            return False

        return True

    def check_max_swarms(self, swarm_ids: List[str]) -> bool:
        """
        Check if number of swarms exceeds policy limit.

        Args:
            swarm_ids: List of swarm IDs

        Returns:
            True if within limit, False if exceeds
        """
        return len(swarm_ids) <= self.policy.max_swarms_per_task

    def check_max_cost(self, task_budget: float) -> bool:
        """
        Check if task budget exceeds policy limit.

        Args:
            task_budget: Budget for the task

        Returns:
            True if within limit, False if exceeds
        """
        return task_budget <= self.policy.max_cost_per_task

    def check_capability_match(self, match_score: float) -> bool:
        """
        Check if capability match meets policy threshold.

        Args:
            match_score: Capability match score (0.0-1.0)

        Returns:
            True if meets threshold, False otherwise
        """
        return match_score >= self.policy.min_capability_match

    def get_policy_summary(self) -> Dict[str, Any]:
        """
        Get summary of current policy configuration.

        Returns:
            Dictionary with policy settings
        """
        return {
            'max_swarms_per_task': self.policy.max_swarms_per_task,
            'max_cost_per_task': self.policy.max_cost_per_task,
            'min_capability_match': self.policy.min_capability_match,
            'circuit_breaker_failure_threshold': self.policy.circuit_breaker_failure_threshold,
            'prefer_reputation': self.policy.prefer_reputation,
            'allow_budget_overdraft': self.policy.allow_budget_overdraft
        }
