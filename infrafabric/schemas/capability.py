"""Capability registry schema for IF.governor task-swarm matching."""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any


class Capability(Enum):
    """Enumeration of swarm capabilities for task matching.

    Covers code analysis, integrations, infrastructure, CLI/tools,
    architecture, and documentation capabilities.
    """

    # Code Analysis - Language-specific
    CODE_ANALYSIS_RUST = "code-analysis:rust"
    CODE_ANALYSIS_PYTHON = "code-analysis:python"
    CODE_ANALYSIS_JAVASCRIPT = "code-analysis:javascript"
    CODE_ANALYSIS_GO = "code-analysis:go"
    CODE_ANALYSIS_TYPESCRIPT = "code-analysis:typescript"
    CODE_ANALYSIS_GENERAL = "code-analysis:general"

    # Integrations - Communication protocols
    INTEGRATION_SIP = "integration:sip"
    INTEGRATION_NDI = "integration:ndi"
    INTEGRATION_WEBRTC = "integration:webrtc"
    INTEGRATION_H323 = "integration:h323"
    INTEGRATION_RTSP = "integration:rtsp"

    # Infrastructure - Distributed systems and operations
    INFRA_DISTRIBUTED_SYSTEMS = "infra:distributed-systems"
    INFRA_NETWORKING = "infra:networking"
    INFRA_DATABASES = "infra:databases"
    INFRA_KUBERNETES = "infra:kubernetes"
    INFRA_CLOUD_PLATFORMS = "infra:cloud-platforms"
    INFRA_MONITORING = "infra:monitoring"

    # CLI/Tools - Development and testing tools
    CLI_DESIGN = "cli:design"
    CLI_TESTING = "cli:testing"
    CLI_UX = "cli:ux"
    CLI_AUTOMATION = "cli:automation"

    # Architecture - Design patterns and principles
    ARCHITECTURE_PATTERNS = "architecture:patterns"
    ARCHITECTURE_SECURITY = "architecture:security"
    ARCHITECTURE_SCALABILITY = "architecture:scalability"
    ARCHITECTURE_PERFORMANCE = "architecture:performance"

    # Documentation - Technical writing and guides
    DOCS_TECHNICAL_WRITING = "docs:technical-writing"
    DOCS_API_DESIGN = "docs:api-design"
    DOCS_TUTORIALS = "docs:tutorials"
    DOCS_ARCHITECTURE = "docs:architecture"


@dataclass
class SwarmProfile:
    """Profile describing a swarm's capabilities and resources.

    Attributes:
        swarm_id: Unique identifier for the swarm
        capabilities: List of Capability enum values the swarm possesses
        cost_per_hour: USD per hour to operate this swarm
        reputation_score: Reputation score from 0.0 to 1.0
        current_budget_remaining: USD remaining in budget
        model: Claude model used ("haiku", "sonnet", or "opus")
    """

    swarm_id: str
    capabilities: List[Capability]
    cost_per_hour: float
    reputation_score: float
    current_budget_remaining: float
    model: str

    def __post_init__(self) -> None:
        """Validate profile after initialization.

        Raises:
            ValueError: If any field value is invalid
        """
        if not self.swarm_id or not isinstance(self.swarm_id, str):
            raise ValueError("swarm_id must be a non-empty string")

        if not isinstance(self.capabilities, list) or not self.capabilities:
            raise ValueError("capabilities must be a non-empty list")

        if not all(isinstance(cap, Capability) for cap in self.capabilities):
            raise ValueError("All capabilities must be Capability enum values")

        if not 0.0 <= self.reputation_score <= 1.0:
            raise ValueError("Reputation score must be between 0.0 and 1.0")

        if self.cost_per_hour < 0:
            raise ValueError("Cost per hour must be non-negative")

        if self.current_budget_remaining < 0:
            raise ValueError("Budget remaining cannot be negative")

        if self.model not in ["haiku", "sonnet", "opus"]:
            raise ValueError("Model must be 'haiku', 'sonnet', or 'opus'")

    def has_capability(self, capability: Capability) -> bool:
        """Check if swarm has a specific capability.

        Args:
            capability: The capability to check for

        Returns:
            True if swarm has the capability, False otherwise
        """
        return capability in self.capabilities

    def get_hourly_cost(self) -> float:
        """Get the hourly cost of operating this swarm.

        Returns:
            Cost in USD per hour
        """
        return self.cost_per_hour

    def has_sufficient_budget(self, required_amount: float) -> bool:
        """Check if swarm has sufficient budget for a task.

        Args:
            required_amount: Amount in USD needed

        Returns:
            True if budget is sufficient, False otherwise
        """
        return self.current_budget_remaining >= required_amount


@dataclass
class ResourcePolicy:
    """Policy constraints for resource allocation and task assignment.

    Attributes:
        max_swarms_per_task: Maximum number of swarms to assign to a single task
        max_cost_per_task: Maximum cost in USD allowed per task
        min_capability_match: Minimum fraction (0.0-1.0) of task requirements
                             that swarm must satisfy (70% threshold default)
        circuit_breaker_failure_threshold: Number of failures before circuit
                                          breaker opens for a swarm
    """

    max_swarms_per_task: int = 3
    max_cost_per_task: float = 10.0
    min_capability_match: float = 0.7
    circuit_breaker_failure_threshold: int = 3

    def __post_init__(self) -> None:
        """Validate policy after initialization.

        Raises:
            ValueError: If any field value is invalid
        """
        if self.max_swarms_per_task < 1:
            raise ValueError("Must allow at least 1 swarm per task")

        if self.max_cost_per_task <= 0:
            raise ValueError("Max cost per task must be positive")

        if not 0.0 <= self.min_capability_match <= 1.0:
            raise ValueError("Capability match threshold must be between 0.0 and 1.0")

        if self.circuit_breaker_failure_threshold < 1:
            raise ValueError("Circuit breaker threshold must be at least 1")


def validate_capability_manifest(manifest: Dict[str, Any]) -> bool:
    """Validate a capability manifest dictionary.

    Checks that all required fields are present and have valid types.

    Args:
        manifest: Dictionary containing swarm profile data

    Returns:
        True if valid

    Raises:
        ValueError: If manifest is invalid
    """
    required_fields = [
        'swarm_id',
        'capabilities',
        'cost_per_hour',
        'reputation_score',
        'current_budget_remaining',
        'model'
    ]

    # Check required fields
    for field_name in required_fields:
        if field_name not in manifest:
            raise ValueError(f"Missing required field: {field_name}")

    # Validate field types and values
    if not isinstance(manifest['swarm_id'], str) or not manifest['swarm_id']:
        raise ValueError("swarm_id must be a non-empty string")

    if not isinstance(manifest['capabilities'], list) or not manifest['capabilities']:
        raise ValueError("capabilities must be a non-empty list")

    if not isinstance(manifest['cost_per_hour'], (int, float)):
        raise ValueError("cost_per_hour must be a number")

    if manifest['cost_per_hour'] < 0:
        raise ValueError("cost_per_hour must be non-negative")

    if not isinstance(manifest['reputation_score'], (int, float)):
        raise ValueError("reputation_score must be a number")

    if not 0.0 <= manifest['reputation_score'] <= 1.0:
        raise ValueError("reputation_score must be between 0.0 and 1.0")

    if not isinstance(manifest['current_budget_remaining'], (int, float)):
        raise ValueError("current_budget_remaining must be a number")

    if manifest['current_budget_remaining'] < 0:
        raise ValueError("current_budget_remaining cannot be negative")

    if manifest['model'] not in ['haiku', 'sonnet', 'opus']:
        raise ValueError("model must be 'haiku', 'sonnet', or 'opus'")

    # Validate capabilities are valid capability names
    valid_capability_values = {cap.value for cap in Capability}
    for cap in manifest['capabilities']:
        if isinstance(cap, str):
            if cap not in valid_capability_values:
                raise ValueError(f"Invalid capability: {cap}")
        else:
            raise ValueError("All capabilities must be strings")

    return True


def validate_swarm_profile(profile: SwarmProfile) -> bool:
    """Validate a SwarmProfile instance.

    Args:
        profile: SwarmProfile to validate

    Returns:
        True if valid

    Raises:
        ValueError: If profile is invalid
    """
    if not isinstance(profile, SwarmProfile):
        raise ValueError("Input must be a SwarmProfile instance")

    if not profile.swarm_id:
        raise ValueError("swarm_id cannot be empty")

    if not profile.capabilities:
        raise ValueError("capabilities cannot be empty")

    # Additional validation already done in __post_init__
    return True
