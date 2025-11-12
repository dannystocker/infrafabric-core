"""
Unit tests for IF.governor Capability Registry Schema

Tests P0.2.1 implementation:
- Capability enum validation
- SwarmProfile validation
- ResourcePolicy validation
- Manifest validation
- JSON serialization
"""

import pytest
from datetime import datetime
from infrafabric.schemas.capability import (
    Capability,
    SkillLevel,
    BloomPattern,
    CapabilityProfile,
    SwarmProfile,
    TaskRequirements,
    ResourcePolicy,
    validate_capability_manifest,
    validate_swarm_profile,
    capability_from_string,
    get_capabilities_by_domain,
    get_all_domains
)


class TestCapabilityEnum:
    """Test Capability enum"""

    def test_capability_enum_exists(self):
        """Test capability enum has values"""
        assert len(list(Capability)) >= 20, "Should have at least 20 capability types"

    def test_capability_format(self):
        """Test capability values follow domain:category:skill format"""
        for cap in Capability:
            parts = cap.value.split(':')
            assert len(parts) == 3, f"Capability {cap.value} should have 3 parts"

    def test_video_capabilities(self):
        """Test video domain capabilities"""
        assert Capability.VIDEO_STREAMING_NDI.value == "video:streaming:ndi"
        assert Capability.VIDEO_PRODUCTION_VMIX.value == "video:production:vmix"
        assert Capability.VIDEO_PRODUCTION_OBS.value == "video:production:obs"

    def test_telephony_capabilities(self):
        """Test telephony domain capabilities"""
        assert Capability.TELEPHONY_SIP_PROTOCOL.value == "telephony:sip:protocol"
        assert Capability.TELEPHONY_WEBRTC_SIGNALING.value == "telephony:webrtc:signaling"

    def test_crypto_capabilities(self):
        """Test crypto domain capabilities"""
        assert Capability.CRYPTO_SIGNATURES_ED25519.value == "crypto:signatures:ed25519"
        assert Capability.CRYPTO_WITNESS_PROVENANCE.value == "crypto:witness:provenance"

    def test_programming_capabilities(self):
        """Test programming domain capabilities"""
        assert Capability.PROGRAMMING_PYTHON_ASYNC.value == "programming:python:async"
        assert Capability.PROGRAMMING_RUST_WASM.value == "programming:rust:wasm"


class TestSkillLevel:
    """Test SkillLevel enum"""

    def test_skill_levels_exist(self):
        """Test all skill levels defined"""
        assert SkillLevel.NOVICE.value == "novice"
        assert SkillLevel.INTERMEDIATE.value == "intermediate"
        assert SkillLevel.ADVANCED.value == "advanced"
        assert SkillLevel.EXPERT.value == "expert"


class TestBloomPattern:
    """Test BloomPattern enum"""

    def test_bloom_patterns_exist(self):
        """Test all bloom patterns defined"""
        assert BloomPattern.EARLY_BLOOMER.value == "early_bloomer"
        assert BloomPattern.STEADY_PERFORMER.value == "steady_performer"
        assert BloomPattern.LATE_BLOOMER.value == "late_bloomer"


class TestCapabilityProfile:
    """Test CapabilityProfile dataclass"""

    def test_create_capability_profile(self):
        """Test creating capability profile"""
        profile = CapabilityProfile(
            capability=Capability.PROGRAMMING_PYTHON_ASYNC,
            skill_level=SkillLevel.ADVANCED,
            experience_hours=150.0,
            success_rate=0.92
        )

        assert profile.capability == Capability.PROGRAMMING_PYTHON_ASYNC
        assert profile.skill_level == SkillLevel.ADVANCED
        assert profile.experience_hours == 150.0
        assert profile.success_rate == 0.92

    def test_capability_profile_defaults(self):
        """Test default values"""
        profile = CapabilityProfile(
            capability=Capability.VIDEO_STREAMING_NDI,
            skill_level=SkillLevel.NOVICE
        )

        assert profile.experience_hours == 0.0
        assert profile.success_rate == 0.70
        assert profile.tasks_completed == 0
        assert profile.last_used is None

    def test_capability_profile_to_dict(self):
        """Test JSON serialization"""
        profile = CapabilityProfile(
            capability=Capability.CRYPTO_SIGNATURES_ED25519,
            skill_level=SkillLevel.EXPERT,
            experience_hours=500.0
        )

        data = profile.to_dict()
        assert data['capability'] == "crypto:signatures:ed25519"
        assert data['skill_level'] == "expert"
        assert data['experience_hours'] == 500.0


class TestSwarmProfile:
    """Test SwarmProfile dataclass"""

    def test_create_swarm_profile(self):
        """Test creating swarm profile"""
        profile = SwarmProfile(
            swarm_id="session-1-ndi",
            name="Session 1 (NDI)",
            model="sonnet",
            cost_per_hour=15.0,
            current_budget_remaining=100.0
        )

        assert profile.swarm_id == "session-1-ndi"
        assert profile.name == "Session 1 (NDI)"
        assert profile.model == "sonnet"
        assert profile.cost_per_hour == 15.0
        assert profile.current_budget_remaining == 100.0

    def test_swarm_profile_defaults(self):
        """Test default values"""
        profile = SwarmProfile(
            swarm_id="test-swarm",
            name="Test Swarm",
            model="haiku"
        )

        assert profile.reputation_score == 0.70
        assert profile.reputation_tier == "acceptable"
        assert profile.bloom_pattern == BloomPattern.STEADY_PERFORMER
        assert profile.total_tasks_completed == 0
        assert profile.active is True

    def test_get_capability_names(self):
        """Test getting capability names"""
        profile = SwarmProfile(
            swarm_id="test",
            name="Test",
            model="haiku",
            capabilities=[
                CapabilityProfile(Capability.VIDEO_STREAMING_NDI, SkillLevel.ADVANCED),
                CapabilityProfile(Capability.CRYPTO_SIGNATURES_ED25519, SkillLevel.INTERMEDIATE)
            ]
        )

        cap_names = profile.get_capability_names()
        assert Capability.VIDEO_STREAMING_NDI in cap_names
        assert Capability.CRYPTO_SIGNATURES_ED25519 in cap_names
        assert len(cap_names) == 2

    def test_get_capability_profile(self):
        """Test getting specific capability profile"""
        cap_profile = CapabilityProfile(Capability.PROGRAMMING_PYTHON_ASYNC, SkillLevel.EXPERT)
        profile = SwarmProfile(
            swarm_id="test",
            name="Test",
            model="sonnet",
            capabilities=[cap_profile]
        )

        found = profile.get_capability_profile(Capability.PROGRAMMING_PYTHON_ASYNC)
        assert found == cap_profile

        not_found = profile.get_capability_profile(Capability.VIDEO_STREAMING_NDI)
        assert not_found is None

    def test_has_capability(self):
        """Test capability checking"""
        profile = SwarmProfile(
            swarm_id="test",
            name="Test",
            model="sonnet",
            capabilities=[
                CapabilityProfile(Capability.PROGRAMMING_RUST_WASM, SkillLevel.ADVANCED)
            ]
        )

        # Has capability
        assert profile.has_capability(Capability.PROGRAMMING_RUST_WASM) is True

        # Doesn't have capability
        assert profile.has_capability(Capability.VIDEO_STREAMING_NDI) is False

        # Has capability at advanced level
        assert profile.has_capability(Capability.PROGRAMMING_RUST_WASM, SkillLevel.ADVANCED) is True

        # Doesn't have at expert level
        assert profile.has_capability(Capability.PROGRAMMING_RUST_WASM, SkillLevel.EXPERT) is False

    def test_has_budget(self):
        """Test budget checking"""
        profile = SwarmProfile(
            swarm_id="test",
            name="Test",
            model="haiku",
            current_budget_remaining=50.0
        )

        assert profile.has_budget(10.0) is True
        assert profile.has_budget(50.0) is True
        assert profile.has_budget(51.0) is False

    def test_swarm_profile_to_dict(self):
        """Test JSON serialization"""
        profile = SwarmProfile(
            swarm_id="session-2-webrtc",
            name="Session 2 (WebRTC)",
            model="sonnet",
            cost_per_hour=18.0,
            capabilities=[
                CapabilityProfile(Capability.TELEPHONY_WEBRTC_SIGNALING, SkillLevel.EXPERT)
            ]
        )

        data = profile.to_dict()
        assert data['swarm_id'] == "session-2-webrtc"
        assert data['model'] == "sonnet"
        assert data['cost_per_hour'] == 18.0
        assert len(data['capabilities']) == 1
        assert data['capabilities'][0]['capability'] == "telephony:webrtc:signaling"


class TestTaskRequirements:
    """Test TaskRequirements dataclass"""

    def test_create_task_requirements(self):
        """Test creating task requirements"""
        req = TaskRequirements(
            task_id="T123",
            required_capabilities=[
                Capability.VIDEO_STREAMING_NDI,
                Capability.CRYPTO_WITNESS_PROVENANCE
            ],
            min_skill_level=SkillLevel.ADVANCED,
            max_cost_per_hour=20.0
        )

        assert req.task_id == "T123"
        assert len(req.required_capabilities) == 2
        assert req.min_skill_level == SkillLevel.ADVANCED

    def test_task_requirements_to_dict(self):
        """Test JSON serialization"""
        req = TaskRequirements(
            task_id="T456",
            required_capabilities=[Capability.PROGRAMMING_PYTHON_ASYNC]
        )

        data = req.to_dict()
        assert data['task_id'] == "T456"
        assert data['required_capabilities'] == ["programming:python:async"]


class TestResourcePolicy:
    """Test ResourcePolicy dataclass"""

    def test_create_resource_policy(self):
        """Test creating resource policy"""
        policy = ResourcePolicy(
            max_swarms_per_task=5,
            min_capability_match=0.80,
            max_cost_per_task=25.0
        )

        assert policy.max_swarms_per_task == 5
        assert policy.min_capability_match == 0.80
        assert policy.max_cost_per_task == 25.0

    def test_resource_policy_defaults(self):
        """Test default values"""
        policy = ResourcePolicy()

        assert policy.max_swarms_per_task == 3
        assert policy.min_capability_match == 0.70
        assert policy.max_cost_per_task == 10.0
        assert policy.enable_budget_tracking is True
        assert policy.circuit_breaker_enabled is True

    def test_resource_policy_to_dict(self):
        """Test JSON serialization"""
        policy = ResourcePolicy()
        data = policy.to_dict()

        assert 'max_swarms_per_task' in data
        assert 'min_capability_match' in data
        assert data['min_capability_match'] == 0.70


class TestManifestValidation:
    """Test capability manifest validation"""

    def test_valid_manifest(self):
        """Test validating valid manifest"""
        manifest = {
            'swarm_id': 'session-1-ndi',
            'name': 'Session 1 (NDI)',
            'model': 'sonnet',
            'capabilities': [
                {
                    'capability': 'video:streaming:ndi',
                    'skill_level': 'advanced'
                }
            ],
            'cost_per_hour': 15.0
        }

        is_valid, error = validate_capability_manifest(manifest)
        assert is_valid is True
        assert error is None

    def test_missing_swarm_id(self):
        """Test manifest with missing swarm_id"""
        manifest = {
            'name': 'Test',
            'model': 'haiku',
            'capabilities': [],
            'cost_per_hour': 2.0
        }

        is_valid, error = validate_capability_manifest(manifest)
        assert is_valid is False
        assert 'swarm_id' in error

    def test_invalid_model(self):
        """Test manifest with invalid model"""
        manifest = {
            'swarm_id': 'test',
            'name': 'Test',
            'model': 'invalid_model',
            'capabilities': [],
            'cost_per_hour': 2.0
        }

        is_valid, error = validate_capability_manifest(manifest)
        assert is_valid is False
        assert 'model' in error

    def test_invalid_capability(self):
        """Test manifest with invalid capability"""
        manifest = {
            'swarm_id': 'test',
            'name': 'Test',
            'model': 'haiku',
            'capabilities': [
                {'capability': 'invalid:capability:name'}
            ],
            'cost_per_hour': 2.0
        }

        is_valid, error = validate_capability_manifest(manifest)
        assert is_valid is False
        assert 'capability' in error.lower()

    def test_negative_cost(self):
        """Test manifest with negative cost"""
        manifest = {
            'swarm_id': 'test',
            'name': 'Test',
            'model': 'haiku',
            'capabilities': [],
            'cost_per_hour': -5.0
        }

        is_valid, error = validate_capability_manifest(manifest)
        assert is_valid is False
        assert 'cost' in error.lower()

    def test_invalid_reputation_score(self):
        """Test manifest with out-of-range reputation score"""
        manifest = {
            'swarm_id': 'test',
            'name': 'Test',
            'model': 'haiku',
            'capabilities': [],
            'cost_per_hour': 2.0,
            'reputation_score': 1.5  # Out of range
        }

        is_valid, error = validate_capability_manifest(manifest)
        assert is_valid is False
        assert 'reputation_score' in error


class TestSwarmProfileValidation:
    """Test SwarmProfile validation"""

    def test_valid_swarm_profile(self):
        """Test validating valid swarm profile"""
        profile = SwarmProfile(
            swarm_id="test",
            name="Test Swarm",
            model="sonnet"
        )

        is_valid, error = validate_swarm_profile(profile)
        assert is_valid is True
        assert error is None

    def test_empty_swarm_id(self):
        """Test profile with empty swarm_id"""
        profile = SwarmProfile(
            swarm_id="",
            name="Test",
            model="haiku"
        )

        is_valid, error = validate_swarm_profile(profile)
        assert is_valid is False
        assert 'swarm_id' in error

    def test_invalid_model(self):
        """Test profile with invalid model"""
        profile = SwarmProfile(
            swarm_id="test",
            name="Test",
            model="gpt4"  # Invalid model
        )

        is_valid, error = validate_swarm_profile(profile)
        assert is_valid is False
        assert 'model' in error

    def test_invalid_reputation_score(self):
        """Test profile with out-of-range reputation score"""
        profile = SwarmProfile(
            swarm_id="test",
            name="Test",
            model="haiku",
            reputation_score=1.5  # Out of range
        )

        is_valid, error = validate_swarm_profile(profile)
        assert is_valid is False
        assert 'reputation_score' in error

    def test_negative_cost(self):
        """Test profile with negative cost"""
        profile = SwarmProfile(
            swarm_id="test",
            name="Test",
            model="haiku",
            cost_per_hour=-10.0
        )

        is_valid, error = validate_swarm_profile(profile)
        assert is_valid is False
        assert 'cost' in error.lower()


class TestHelperFunctions:
    """Test helper functions"""

    def test_capability_from_string(self):
        """Test converting string to Capability"""
        cap = capability_from_string("video:streaming:ndi")
        assert cap == Capability.VIDEO_STREAMING_NDI

        invalid = capability_from_string("invalid:capability:name")
        assert invalid is None

    def test_get_capabilities_by_domain(self):
        """Test getting capabilities by domain"""
        video_caps = get_capabilities_by_domain("video")
        assert len(video_caps) > 0
        assert all('video:' in cap.value for cap in video_caps)

        telephony_caps = get_capabilities_by_domain("telephony")
        assert len(telephony_caps) > 0
        assert all('telephony:' in cap.value for cap in telephony_caps)

    def test_get_all_domains(self):
        """Test getting all domains"""
        domains = get_all_domains()
        assert 'video' in domains
        assert 'telephony' in domains
        assert 'crypto' in domains
        assert 'infra' in domains
        assert 'programming' in domains
        assert len(domains) >= 10  # Should have at least 10 domains


class TestIntegration:
    """Integration tests for capability schema"""

    def test_full_swarm_registration(self):
        """Test complete swarm registration workflow"""
        # Create capability profiles
        cap1 = CapabilityProfile(
            capability=Capability.VIDEO_STREAMING_NDI,
            skill_level=SkillLevel.EXPERT,
            experience_hours=200.0,
            success_rate=0.95
        )

        cap2 = CapabilityProfile(
            capability=Capability.CRYPTO_WITNESS_PROVENANCE,
            skill_level=SkillLevel.ADVANCED,
            experience_hours=100.0,
            success_rate=0.88
        )

        # Create swarm profile
        profile = SwarmProfile(
            swarm_id="session-1-ndi",
            name="Session 1 (NDI)",
            model="sonnet",
            capabilities=[cap1, cap2],
            cost_per_hour=18.0,
            current_budget_remaining=500.0,
            reputation_score=0.92,
            reputation_tier="excellent",
            bloom_pattern=BloomPattern.LATE_BLOOMER
        )

        # Validate profile
        is_valid, error = validate_swarm_profile(profile)
        assert is_valid is True

        # Test capability queries
        assert profile.has_capability(Capability.VIDEO_STREAMING_NDI) is True
        assert profile.has_capability(Capability.CRYPTO_WITNESS_PROVENANCE) is True
        assert profile.has_capability(Capability.PROGRAMMING_RUST_WASM) is False

        # Test budget
        assert profile.has_budget(100.0) is True

        # Serialize to JSON
        data = profile.to_dict()
        assert data['swarm_id'] == "session-1-ndi"
        assert len(data['capabilities']) == 2

    def test_task_matching_workflow(self):
        """Test task requirements matching"""
        # Create task requirements
        task = TaskRequirements(
            task_id="T789",
            required_capabilities=[
                Capability.VIDEO_STREAMING_NDI,
                Capability.VIDEO_PRODUCTION_OBS
            ],
            min_skill_level=SkillLevel.ADVANCED,
            max_cost_per_hour=25.0,
            preferred_bloom_pattern=BloomPattern.STEADY_PERFORMER,
            min_reputation=0.75
        )

        # Create matching swarm
        swarm = SwarmProfile(
            swarm_id="video-specialist",
            name="Video Specialist",
            model="sonnet",
            capabilities=[
                CapabilityProfile(Capability.VIDEO_STREAMING_NDI, SkillLevel.EXPERT),
                CapabilityProfile(Capability.VIDEO_PRODUCTION_OBS, SkillLevel.ADVANCED),
                CapabilityProfile(Capability.VIDEO_ENCODING_H264, SkillLevel.INTERMEDIATE)
            ],
            cost_per_hour=20.0,
            reputation_score=0.88,
            bloom_pattern=BloomPattern.STEADY_PERFORMER
        )

        # Verify swarm meets requirements
        for req_cap in task.required_capabilities:
            assert swarm.has_capability(req_cap, task.min_skill_level)

        assert swarm.cost_per_hour <= task.max_cost_per_hour
        assert swarm.reputation_score >= task.min_reputation
        assert swarm.bloom_pattern == task.preferred_bloom_pattern


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
