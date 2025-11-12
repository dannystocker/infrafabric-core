"""Unit tests for capability registry schema.

Tests the Capability enum, SwarmProfile, ResourcePolicy classes,
and validation functions for IF.governor task-swarm matching.
"""

import pytest
from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
    validate_capability_manifest,
    validate_swarm_profile,
)


class TestCapabilityEnum:
    """Test Capability enum completeness and values."""

    def test_capability_enum_exists(self):
        """Test that Capability enum is defined."""
        assert Capability is not None

    def test_capability_enum_has_minimum_count(self):
        """Test capability enum has at least 20 types."""
        capabilities = list(Capability)
        assert len(capabilities) >= 20

    def test_code_analysis_capabilities(self):
        """Test code analysis capabilities exist."""
        assert Capability.CODE_ANALYSIS_RUST.value == "code-analysis:rust"
        assert Capability.CODE_ANALYSIS_PYTHON.value == "code-analysis:python"
        assert Capability.CODE_ANALYSIS_JAVASCRIPT.value == "code-analysis:javascript"
        assert Capability.CODE_ANALYSIS_GO.value == "code-analysis:go"
        assert Capability.CODE_ANALYSIS_TYPESCRIPT.value == "code-analysis:typescript"

    def test_integration_capabilities(self):
        """Test integration capabilities exist."""
        assert Capability.INTEGRATION_SIP.value == "integration:sip"
        assert Capability.INTEGRATION_NDI.value == "integration:ndi"
        assert Capability.INTEGRATION_WEBRTC.value == "integration:webrtc"
        assert Capability.INTEGRATION_H323.value == "integration:h323"

    def test_infrastructure_capabilities(self):
        """Test infrastructure capabilities exist."""
        assert Capability.INFRA_DISTRIBUTED_SYSTEMS.value == "infra:distributed-systems"
        assert Capability.INFRA_NETWORKING.value == "infra:networking"
        assert Capability.INFRA_DATABASES.value == "infra:databases"
        assert Capability.INFRA_KUBERNETES.value == "infra:kubernetes"

    def test_cli_capabilities(self):
        """Test CLI/Tools capabilities exist."""
        assert Capability.CLI_DESIGN.value == "cli:design"
        assert Capability.CLI_TESTING.value == "cli:testing"
        assert Capability.CLI_UX.value == "cli:ux"

    def test_architecture_capabilities(self):
        """Test architecture capabilities exist."""
        assert Capability.ARCHITECTURE_PATTERNS.value == "architecture:patterns"
        assert Capability.ARCHITECTURE_SECURITY.value == "architecture:security"
        assert Capability.ARCHITECTURE_SCALABILITY.value == "architecture:scalability"

    def test_documentation_capabilities(self):
        """Test documentation capabilities exist."""
        assert Capability.DOCS_TECHNICAL_WRITING.value == "docs:technical-writing"
        assert Capability.DOCS_API_DESIGN.value == "docs:api-design"
        assert Capability.DOCS_TUTORIALS.value == "docs:tutorials"


class TestSwarmProfile:
    """Test SwarmProfile dataclass."""

    def test_swarm_profile_creation_valid(self):
        """Test creating a valid swarm profile."""
        profile = SwarmProfile(
            swarm_id="session-1-ndi",
            capabilities=[Capability.INTEGRATION_NDI, Capability.DOCS_TECHNICAL_WRITING],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.0,
            model="haiku"
        )

        assert profile.swarm_id == "session-1-ndi"
        assert len(profile.capabilities) == 2
        assert profile.cost_per_hour == 2.0
        assert profile.reputation_score == 0.95
        assert profile.current_budget_remaining == 10.0
        assert profile.model == "haiku"

    def test_swarm_profile_invalid_reputation_too_high(self):
        """Test SwarmProfile rejects reputation > 1.0."""
        with pytest.raises(ValueError, match="Reputation score"):
            SwarmProfile(
                swarm_id="test",
                capabilities=[Capability.CLI_DESIGN],
                cost_per_hour=2.0,
                reputation_score=1.5,
                current_budget_remaining=10.0,
                model="haiku"
            )

    def test_swarm_profile_invalid_reputation_negative(self):
        """Test SwarmProfile rejects negative reputation."""
        with pytest.raises(ValueError, match="Reputation score"):
            SwarmProfile(
                swarm_id="test",
                capabilities=[Capability.CLI_DESIGN],
                cost_per_hour=2.0,
                reputation_score=-0.1,
                current_budget_remaining=10.0,
                model="haiku"
            )

    def test_swarm_profile_invalid_model(self):
        """Test SwarmProfile rejects invalid model."""
        with pytest.raises(ValueError, match="Model must be"):
            SwarmProfile(
                swarm_id="test",
                capabilities=[Capability.CLI_DESIGN],
                cost_per_hour=2.0,
                reputation_score=0.8,
                current_budget_remaining=10.0,
                model="invalid"
            )

    def test_swarm_profile_invalid_negative_cost(self):
        """Test SwarmProfile rejects negative cost."""
        with pytest.raises(ValueError, match="Cost per hour"):
            SwarmProfile(
                swarm_id="test",
                capabilities=[Capability.CLI_DESIGN],
                cost_per_hour=-1.0,
                reputation_score=0.8,
                current_budget_remaining=10.0,
                model="haiku"
            )

    def test_swarm_profile_invalid_negative_budget(self):
        """Test SwarmProfile rejects negative budget."""
        with pytest.raises(ValueError, match="Budget remaining"):
            SwarmProfile(
                swarm_id="test",
                capabilities=[Capability.CLI_DESIGN],
                cost_per_hour=2.0,
                reputation_score=0.8,
                current_budget_remaining=-5.0,
                model="haiku"
            )

    def test_swarm_profile_empty_swarm_id(self):
        """Test SwarmProfile rejects empty swarm_id."""
        with pytest.raises(ValueError, match="swarm_id"):
            SwarmProfile(
                swarm_id="",
                capabilities=[Capability.CLI_DESIGN],
                cost_per_hour=2.0,
                reputation_score=0.8,
                current_budget_remaining=10.0,
                model="haiku"
            )

    def test_swarm_profile_empty_capabilities(self):
        """Test SwarmProfile rejects empty capabilities list."""
        with pytest.raises(ValueError, match="capabilities"):
            SwarmProfile(
                swarm_id="test",
                capabilities=[],
                cost_per_hour=2.0,
                reputation_score=0.8,
                current_budget_remaining=10.0,
                model="haiku"
            )

    def test_swarm_profile_has_capability(self):
        """Test has_capability method."""
        profile = SwarmProfile(
            swarm_id="test",
            capabilities=[Capability.INTEGRATION_NDI, Capability.CLI_DESIGN],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=10.0,
            model="haiku"
        )

        assert profile.has_capability(Capability.INTEGRATION_NDI) is True
        assert profile.has_capability(Capability.CLI_DESIGN) is True
        assert profile.has_capability(Capability.ARCHITECTURE_SECURITY) is False

    def test_swarm_profile_get_hourly_cost(self):
        """Test get_hourly_cost method."""
        profile = SwarmProfile(
            swarm_id="test",
            capabilities=[Capability.CLI_DESIGN],
            cost_per_hour=3.5,
            reputation_score=0.8,
            current_budget_remaining=10.0,
            model="haiku"
        )

        assert profile.get_hourly_cost() == 3.5

    def test_swarm_profile_has_sufficient_budget(self):
        """Test has_sufficient_budget method."""
        profile = SwarmProfile(
            swarm_id="test",
            capabilities=[Capability.CLI_DESIGN],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=10.0,
            model="haiku"
        )

        assert profile.has_sufficient_budget(5.0) is True
        assert profile.has_sufficient_budget(10.0) is True
        assert profile.has_sufficient_budget(10.1) is False
        assert profile.has_sufficient_budget(0.0) is True

    def test_swarm_profile_model_variants(self):
        """Test all valid model types."""
        for model in ["haiku", "sonnet", "opus"]:
            profile = SwarmProfile(
                swarm_id="test",
                capabilities=[Capability.CLI_DESIGN],
                cost_per_hour=2.0,
                reputation_score=0.8,
                current_budget_remaining=10.0,
                model=model
            )
            assert profile.model == model


class TestResourcePolicy:
    """Test ResourcePolicy dataclass."""

    def test_resource_policy_defaults(self):
        """Test ResourcePolicy default values."""
        policy = ResourcePolicy()

        assert policy.max_swarms_per_task == 3
        assert policy.max_cost_per_task == 10.0
        assert policy.min_capability_match == 0.7
        assert policy.circuit_breaker_failure_threshold == 3

    def test_resource_policy_custom_values(self):
        """Test creating ResourcePolicy with custom values."""
        policy = ResourcePolicy(
            max_swarms_per_task=5,
            max_cost_per_task=20.0,
            min_capability_match=0.8,
            circuit_breaker_failure_threshold=5
        )

        assert policy.max_swarms_per_task == 5
        assert policy.max_cost_per_task == 20.0
        assert policy.min_capability_match == 0.8
        assert policy.circuit_breaker_failure_threshold == 5

    def test_resource_policy_invalid_max_swarms_zero(self):
        """Test ResourcePolicy rejects max_swarms_per_task < 1."""
        with pytest.raises(ValueError, match="at least 1 swarm"):
            ResourcePolicy(max_swarms_per_task=0)

    def test_resource_policy_invalid_max_swarms_negative(self):
        """Test ResourcePolicy rejects negative max_swarms_per_task."""
        with pytest.raises(ValueError, match="at least 1 swarm"):
            ResourcePolicy(max_swarms_per_task=-1)

    def test_resource_policy_invalid_max_cost_zero(self):
        """Test ResourcePolicy rejects max_cost_per_task <= 0."""
        with pytest.raises(ValueError, match="Max cost"):
            ResourcePolicy(max_cost_per_task=0.0)

    def test_resource_policy_invalid_max_cost_negative(self):
        """Test ResourcePolicy rejects negative max_cost_per_task."""
        with pytest.raises(ValueError, match="Max cost"):
            ResourcePolicy(max_cost_per_task=-1.0)

    def test_resource_policy_invalid_capability_match_too_high(self):
        """Test ResourcePolicy rejects capability match > 1.0."""
        with pytest.raises(ValueError, match="Capability match"):
            ResourcePolicy(min_capability_match=1.5)

    def test_resource_policy_invalid_capability_match_negative(self):
        """Test ResourcePolicy rejects negative capability match."""
        with pytest.raises(ValueError, match="Capability match"):
            ResourcePolicy(min_capability_match=-0.1)

    def test_resource_policy_invalid_circuit_breaker_zero(self):
        """Test ResourcePolicy rejects circuit_breaker_failure_threshold < 1."""
        with pytest.raises(ValueError, match="Circuit breaker"):
            ResourcePolicy(circuit_breaker_failure_threshold=0)

    def test_resource_policy_invalid_circuit_breaker_negative(self):
        """Test ResourcePolicy rejects negative circuit_breaker_failure_threshold."""
        with pytest.raises(ValueError, match="Circuit breaker"):
            ResourcePolicy(circuit_breaker_failure_threshold=-1)

    def test_resource_policy_boundary_values(self):
        """Test ResourcePolicy with boundary values."""
        # Min capability match at boundaries
        policy = ResourcePolicy(min_capability_match=0.0)
        assert policy.min_capability_match == 0.0

        policy = ResourcePolicy(min_capability_match=1.0)
        assert policy.min_capability_match == 1.0


class TestValidateCapabilityManifest:
    """Test validate_capability_manifest function."""

    def test_validate_manifest_valid(self):
        """Test valid capability manifest."""
        manifest = {
            'swarm_id': 'session-1',
            'capabilities': ['integration:ndi', 'cli:design'],
            'cost_per_hour': 2.0,
            'reputation_score': 0.95,
            'current_budget_remaining': 10.0,
            'model': 'haiku'
        }

        assert validate_capability_manifest(manifest) is True

    def test_validate_manifest_missing_swarm_id(self):
        """Test manifest missing swarm_id."""
        manifest = {
            'capabilities': ['integration:ndi'],
            'cost_per_hour': 2.0,
            'reputation_score': 0.95,
            'current_budget_remaining': 10.0,
            'model': 'haiku'
        }

        with pytest.raises(ValueError, match="Missing required field: swarm_id"):
            validate_capability_manifest(manifest)

    def test_validate_manifest_missing_capabilities(self):
        """Test manifest missing capabilities."""
        manifest = {
            'swarm_id': 'session-1',
            'cost_per_hour': 2.0,
            'reputation_score': 0.95,
            'current_budget_remaining': 10.0,
            'model': 'haiku'
        }

        with pytest.raises(ValueError, match="Missing required field: capabilities"):
            validate_capability_manifest(manifest)

    def test_validate_manifest_empty_swarm_id(self):
        """Test manifest with empty swarm_id."""
        manifest = {
            'swarm_id': '',
            'capabilities': ['integration:ndi'],
            'cost_per_hour': 2.0,
            'reputation_score': 0.95,
            'current_budget_remaining': 10.0,
            'model': 'haiku'
        }

        with pytest.raises(ValueError, match="swarm_id"):
            validate_capability_manifest(manifest)

    def test_validate_manifest_empty_capabilities(self):
        """Test manifest with empty capabilities list."""
        manifest = {
            'swarm_id': 'session-1',
            'capabilities': [],
            'cost_per_hour': 2.0,
            'reputation_score': 0.95,
            'current_budget_remaining': 10.0,
            'model': 'haiku'
        }

        with pytest.raises(ValueError, match="capabilities"):
            validate_capability_manifest(manifest)

    def test_validate_manifest_invalid_reputation(self):
        """Test manifest with invalid reputation."""
        manifest = {
            'swarm_id': 'session-1',
            'capabilities': ['integration:ndi'],
            'cost_per_hour': 2.0,
            'reputation_score': 1.5,
            'current_budget_remaining': 10.0,
            'model': 'haiku'
        }

        with pytest.raises(ValueError, match="reputation_score"):
            validate_capability_manifest(manifest)

    def test_validate_manifest_invalid_model(self):
        """Test manifest with invalid model."""
        manifest = {
            'swarm_id': 'session-1',
            'capabilities': ['integration:ndi'],
            'cost_per_hour': 2.0,
            'reputation_score': 0.95,
            'current_budget_remaining': 10.0,
            'model': 'invalid'
        }

        with pytest.raises(ValueError, match="model"):
            validate_capability_manifest(manifest)

    def test_validate_manifest_invalid_capability_value(self):
        """Test manifest with invalid capability value."""
        manifest = {
            'swarm_id': 'session-1',
            'capabilities': ['invalid:capability'],
            'cost_per_hour': 2.0,
            'reputation_score': 0.95,
            'current_budget_remaining': 10.0,
            'model': 'haiku'
        }

        with pytest.raises(ValueError, match="Invalid capability"):
            validate_capability_manifest(manifest)

    def test_validate_manifest_negative_cost(self):
        """Test manifest with negative cost."""
        manifest = {
            'swarm_id': 'session-1',
            'capabilities': ['integration:ndi'],
            'cost_per_hour': -1.0,
            'reputation_score': 0.95,
            'current_budget_remaining': 10.0,
            'model': 'haiku'
        }

        with pytest.raises(ValueError, match="cost_per_hour"):
            validate_capability_manifest(manifest)

    def test_validate_manifest_negative_budget(self):
        """Test manifest with negative budget."""
        manifest = {
            'swarm_id': 'session-1',
            'capabilities': ['integration:ndi'],
            'cost_per_hour': 2.0,
            'reputation_score': 0.95,
            'current_budget_remaining': -5.0,
            'model': 'haiku'
        }

        with pytest.raises(ValueError, match="current_budget_remaining"):
            validate_capability_manifest(manifest)


class TestValidateSwarmProfile:
    """Test validate_swarm_profile function."""

    def test_validate_swarm_profile_valid(self):
        """Test valid swarm profile."""
        profile = SwarmProfile(
            swarm_id="session-1",
            capabilities=[Capability.INTEGRATION_NDI],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.0,
            model="haiku"
        )

        assert validate_swarm_profile(profile) is True

    def test_validate_swarm_profile_invalid_type(self):
        """Test validate_swarm_profile with invalid type."""
        with pytest.raises(ValueError, match="SwarmProfile instance"):
            validate_swarm_profile("not a profile")

    def test_validate_swarm_profile_empty_swarm_id(self):
        """Test that SwarmProfile constructor catches empty swarm_id."""
        # This is caught during construction, not by validate_swarm_profile
        with pytest.raises(ValueError, match="swarm_id"):
            SwarmProfile(
                swarm_id="",
                capabilities=[Capability.CLI_DESIGN],
                cost_per_hour=2.0,
                reputation_score=0.8,
                current_budget_remaining=10.0,
                model="haiku"
            )

    def test_validate_swarm_profile_empty_capabilities(self):
        """Test that SwarmProfile constructor catches empty capabilities."""
        # This is caught during construction, not by validate_swarm_profile
        with pytest.raises(ValueError, match="capabilities"):
            SwarmProfile(
                swarm_id="test",
                capabilities=[],
                cost_per_hour=2.0,
                reputation_score=0.8,
                current_budget_remaining=10.0,
                model="haiku"
            )


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_create_haiku_swarm_profile(self):
        """Test creating a Haiku model swarm profile."""
        profile = SwarmProfile(
            swarm_id="session-1-haiku",
            capabilities=[
                Capability.CODE_ANALYSIS_PYTHON,
                Capability.CLI_TESTING,
            ],
            cost_per_hour=1.5,
            reputation_score=0.85,
            current_budget_remaining=50.0,
            model="haiku"
        )

        assert profile.model == "haiku"
        assert 1.0 <= profile.cost_per_hour <= 2.0

    def test_create_sonnet_swarm_profile(self):
        """Test creating a Sonnet model swarm profile."""
        profile = SwarmProfile(
            swarm_id="session-1-sonnet",
            capabilities=[
                Capability.ARCHITECTURE_PATTERNS,
                Capability.ARCHITECTURE_SECURITY,
            ],
            cost_per_hour=18.0,
            reputation_score=0.92,
            current_budget_remaining=200.0,
            model="sonnet"
        )

        assert profile.model == "sonnet"
        assert 15.0 <= profile.cost_per_hour <= 20.0

    def test_task_swarm_matching_scenario(self):
        """Test a realistic task-swarm matching scenario."""
        # Create resource policy
        policy = ResourcePolicy(
            max_swarms_per_task=2,
            max_cost_per_task=15.0,
            min_capability_match=0.7
        )

        # Create swarm profiles
        swarm1 = SwarmProfile(
            swarm_id="swarm-rust",
            capabilities=[
                Capability.CODE_ANALYSIS_RUST,
                Capability.ARCHITECTURE_PERFORMANCE,
            ],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=100.0,
            model="haiku"
        )

        swarm2 = SwarmProfile(
            swarm_id="swarm-integration",
            capabilities=[
                Capability.INTEGRATION_NDI,
                Capability.INTEGRATION_SIP,
                Capability.INFRA_NETWORKING,
            ],
            cost_per_hour=18.0,
            reputation_score=0.88,
            current_budget_remaining=150.0,
            model="sonnet"
        )

        # Verify swarm characteristics
        assert policy.max_swarms_per_task == 2
        assert swarm1.has_capability(Capability.CODE_ANALYSIS_RUST)
        assert swarm2.has_capability(Capability.INTEGRATION_NDI)
        assert swarm1.has_sufficient_budget(10.0)
        assert swarm2.has_sufficient_budget(50.0)

    def test_manifest_to_profile_workflow(self):
        """Test converting manifest to SwarmProfile."""
        manifest = {
            'swarm_id': 'test-swarm',
            'capabilities': ['cli:design', 'cli:testing'],
            'cost_per_hour': 1.5,
            'reputation_score': 0.9,
            'current_budget_remaining': 50.0,
            'model': 'haiku'
        }

        # Validate manifest
        assert validate_capability_manifest(manifest) is True

        # Convert to SwarmProfile
        profile = SwarmProfile(
            swarm_id=manifest['swarm_id'],
            capabilities=[Capability(cap) for cap in manifest['capabilities']],
            cost_per_hour=manifest['cost_per_hour'],
            reputation_score=manifest['reputation_score'],
            current_budget_remaining=manifest['current_budget_remaining'],
            model=manifest['model']
        )

        # Validate profile
        assert validate_swarm_profile(profile) is True
        assert profile.swarm_id == 'test-swarm'
