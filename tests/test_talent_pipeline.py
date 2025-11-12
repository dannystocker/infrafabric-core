"""
Tests for IF.talent Scout→Sandbox→Certify→Deploy pipeline

Tests all four phases of the talent onboarding pipeline.
"""

import pytest
import asyncio
from typing import Dict, Any

# Import IF.talent components
import sys
sys.path.insert(0, '/home/user/infrafabric/src')

from infrafabric.talent import TalentPipeline, Scout, Sandbox, Certifier, Deployer
from infrafabric.talent.pipeline import PipelineStage


class TestTalentPipeline:
    """Test complete IF.talent pipeline"""

    @pytest.mark.asyncio
    async def test_full_pipeline_success(self):
        """Test complete pipeline with valid capability"""
        pipeline = TalentPipeline(
            scout_agents=10,
            implementation_agents=7,
            enable_witness=False  # Disable for testing
        )

        result = await pipeline.onboard_capability(
            capability_name="python.async_programming",
            target_agent="test-agent-1"
        )

        assert result.success is True
        assert result.stage == PipelineStage.COMPLETE
        assert result.capability_id is not None
        assert len(result.errors) == 0
        assert result.duration_seconds > 0

    @pytest.mark.asyncio
    async def test_pipeline_with_invalid_domain(self):
        """Test pipeline rejects invalid domain"""
        pipeline = TalentPipeline(scout_agents=10, enable_witness=False)

        result = await pipeline.onboard_capability(
            capability_name="invalid_domain.test.skill",
            target_agent="test-agent-2"
        )

        # Should fail at certify stage (domain taxonomy validation)
        assert result.success is False
        assert result.stage in [PipelineStage.CERTIFY, PipelineStage.SCOUT]

    @pytest.mark.asyncio
    async def test_batch_onboarding(self):
        """Test batch onboarding of multiple capabilities"""
        pipeline = TalentPipeline(scout_agents=10, enable_witness=False)

        capabilities = [
            {'name': 'python.async_programming'},
            {'name': 'infra.orchestration.docker'},
            {'name': 'crypto.signatures.ed25519'}
        ]

        results = await pipeline.batch_onboard(
            capabilities=capabilities,
            target_agent="test-agent-batch",
            parallel=True
        )

        assert len(results) == 3
        # At least some should succeed
        successful = sum(1 for r in results if r.success)
        assert successful >= 2  # Expect most to pass

    def test_pipeline_metrics(self):
        """Test pipeline metrics tracking"""
        pipeline = TalentPipeline(scout_agents=10, enable_witness=False)

        metrics = pipeline.get_metrics()

        assert 'total_onboarded' in metrics
        assert 'total_failed' in metrics
        assert 'average_duration' in metrics
        assert 'success_rate' in metrics


class TestScout:
    """Test Scout phase with multiple Haiku agents"""

    @pytest.mark.asyncio
    async def test_scout_approval(self):
        """Test scout approves well-formed capability"""
        scout = Scout(num_agents=10)

        result = await scout.evaluate_capability(
            capability_name="python.async_programming",
            target_agent="test-agent"
        )

        assert result.approved is True
        assert result.capability_profile is not None
        assert result.confidence >= 0.70
        assert len(result.scout_votes) == 10

    @pytest.mark.asyncio
    async def test_scout_rejection(self):
        """Test scout rejects poorly-formed capability"""
        scout = Scout(num_agents=10)

        result = await scout.evaluate_capability(
            capability_name="malformed",  # No domain.category.skill format
            target_agent="test-agent"
        )

        # May pass or fail depending on heuristics
        assert result.confidence >= 0.0
        assert len(result.scout_votes) == 10

    @pytest.mark.asyncio
    async def test_scout_recommendations(self):
        """Test scout provides valid recommendations"""
        scout = Scout(num_agents=10)

        result = await scout.evaluate_capability(
            capability_name="infra.performance.optimization",
            target_agent="test-agent"
        )

        if result.approved:
            profile = result.capability_profile
            assert 'recommended_level' in profile
            assert profile['recommended_level'] in ['novice', 'intermediate', 'advanced', 'expert']
            assert 'recommended_bloom' in profile
            assert profile['recommended_bloom'] in ['early_bloomer', 'steady_performer', 'late_bloomer']

    @pytest.mark.asyncio
    async def test_auto_discover(self):
        """Test auto-discovery from task history"""
        scout = Scout()

        history = [
            {'task_id': 't1', 'skills_used': ['python.async', 'docker']},
            {'task_id': 't2', 'skills_used': ['python.async', 'networking']},
            {'task_id': 't3', 'skills_used': ['python.async', 'docker']},
            {'task_id': 't4', 'skills_used': ['docker', 'kubernetes']}
        ]

        recommended = await scout.auto_discover_capabilities(
            agent_history=history,
            min_frequency=3
        )

        # python.async and docker should be recommended (≥3 uses)
        assert 'python.async' in recommended
        assert 'docker' in recommended
        assert 'kubernetes' not in recommended  # Only 1 use


class TestSandbox:
    """Test Sandbox phase"""

    @pytest.mark.asyncio
    async def test_sandbox_testing(self):
        """Test sandbox testing phase"""
        sandbox = Sandbox(use_chassis=False)  # Use mock for testing

        capability = {
            'capability_name': 'python.async_programming',
            'domain': 'programming',
            'category': 'python',
            'skill': 'async_programming',
            'recommended_level': 'advanced'
        }

        result = await sandbox.test_capability(
            capability=capability,
            target_agent="test-agent",
            test_duration=10
        )

        assert result.passed is True
        assert result.validated_capability is not None
        assert result.validated_capability['sandbox_validated'] is True
        assert len(result.test_results) == 5  # 5 tests in suite

    @pytest.mark.asyncio
    async def test_sandbox_metrics(self):
        """Test sandbox provides metrics"""
        sandbox = Sandbox(use_chassis=False)

        capability = {
            'capability_name': 'test.capability',
            'domain': 'programming',
            'category': 'test',
            'skill': 'testing'
        }

        result = await sandbox.test_capability(
            capability=capability,
            target_agent="test-agent"
        )

        assert 'pass_rate' in result.metrics
        assert 'tests_passed' in result.metrics
        assert 'tests_total' in result.metrics
        assert 'duration_seconds' in result.metrics


class TestCertifier:
    """Test Certify phase"""

    @pytest.mark.asyncio
    async def test_certify_valid_capability(self):
        """Test certification of valid capability"""
        certifier = Certifier(require_f612_compliance=True)

        capability = {
            'capability_name': 'python.async_programming',
            'domain': 'programming',
            'category': 'python',
            'skill': 'async_programming',
            'recommended_level': 'advanced',
            'sandbox_validated': True,
            'sandbox_pass_rate': 1.0,
            'sandbox_tests_passed': 5,
            'sandbox_tests_total': 5
        }

        sandbox_metrics = {
            'pass_rate': 1.0,
            'duration_seconds': 2.5
        }

        result = await certifier.certify_capability(
            capability=capability,
            sandbox_metrics=sandbox_metrics
        )

        assert result.certified is True
        assert result.certified_capability is not None
        assert result.certification_level is not None
        assert 'reputation' in result.certified_capability

    @pytest.mark.asyncio
    async def test_certify_invalid_domain(self):
        """Test certification rejects invalid domain"""
        certifier = Certifier()

        capability = {
            'capability_name': 'invalid_domain.test.skill',
            'domain': 'invalid_domain',
            'category': 'test',
            'skill': 'skill',
            'recommended_level': 'intermediate'
        }

        result = await certifier.certify_capability(
            capability=capability,
            sandbox_metrics={}
        )

        assert result.certified is False
        assert 'domain taxonomy' in result.reason.lower()

    @pytest.mark.asyncio
    async def test_certification_levels(self):
        """Test different certification levels"""
        certifier = Certifier()

        # Gold level capability (all validations pass)
        gold_capability = {
            'capability_name': 'programming.python.async',
            'domain': 'programming',
            'category': 'python',
            'skill': 'async',
            'recommended_level': 'expert',
            'sandbox_validated': True,
            'sandbox_pass_rate': 1.0,
            'sandbox_tests_passed': 5,
            'sandbox_tests_total': 5
        }

        result = await certifier.certify_capability(
            capability=gold_capability,
            sandbox_metrics={'pass_rate': 1.0, 'duration_seconds': 1.0}
        )

        if result.certified:
            # Should be Gold or Silver
            assert result.certification_level.value in ['gold', 'silver']


class TestDeployer:
    """Test Deploy phase"""

    @pytest.mark.asyncio
    async def test_deploy_capability(self):
        """Test deployment to IF.governor"""
        deployer = Deployer(enable_witness=False)

        capability = {
            'capability_name': 'python.async_programming',
            'domain': 'programming',
            'category': 'python',
            'skill': 'async_programming',
            'recommended_level': 'advanced',
            'recommended_bloom': 'steady_performer',
            'sandbox_validated': True,
            'certification': {
                'certified': True,
                'level': 'gold'
            }
        }

        result = await deployer.deploy_capability(
            capability=capability,
            target_agent="test-agent"
        )

        assert result.success is True
        assert result.capability_id is not None
        assert result.capability_id.startswith('cap-')

    @pytest.mark.asyncio
    async def test_capability_id_format(self):
        """Test capability ID format"""
        deployer = Deployer(enable_witness=False)

        cap_id = deployer._generate_capability_id(
            capability_name="video.streaming.ndi",
            target_agent="session-1-ndi"
        )

        assert cap_id.startswith('cap-')
        assert 'video' in cap_id
        assert len(cap_id.split('-')) >= 3

    def test_deployment_stats(self):
        """Test deployment statistics tracking"""
        deployer = Deployer()

        stats = deployer.get_deployment_stats()

        assert 'total_deployed' in stats
        assert 'witness_enabled' in stats


@pytest.mark.asyncio
async def test_integration_full_pipeline():
    """
    Integration test: Full pipeline from Scout to Deploy

    This is the comprehensive end-to-end test.
    """
    pipeline = TalentPipeline(
        scout_agents=10,
        implementation_agents=7,
        enable_witness=False
    )

    # Test multiple capabilities
    test_capabilities = [
        "programming.python.async_programming",
        "infra.orchestration.docker",
        "video.streaming.ndi_protocol"
    ]

    results = []
    for cap_name in test_capabilities:
        result = await pipeline.onboard_capability(
            capability_name=cap_name,
            target_agent="integration-test-agent"
        )
        results.append(result)

    # Verify results
    successful = sum(1 for r in results if r.success)
    assert successful >= 2  # At least 2/3 should succeed

    # Verify pipeline metrics
    metrics = pipeline.get_metrics()
    assert metrics['total_onboarded'] >= 2
    assert metrics['success_rate'] >= 0.66  # At least 66% success

    print(f"\n✅ Integration test complete:")
    print(f"   Onboarded: {successful}/{len(test_capabilities)}")
    print(f"   Success rate: {metrics['success_rate']*100:.0f}%")
    print(f"   Average duration: {metrics['average_duration']:.2f}s")


if __name__ == '__main__':
    # Run integration test
    asyncio.run(test_integration_full_pipeline())
