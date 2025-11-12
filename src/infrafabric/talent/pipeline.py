"""
IF.talent Pipeline - Main orchestrator for Scout→Sandbox→Certify→Deploy

This is the entry point for onboarding new AI capabilities into InfraFabric.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .scout import Scout
from .sandbox import Sandbox
from .certify import Certifier
from .deploy import Deployer


class PipelineStage(Enum):
    """Pipeline execution stages"""
    SCOUT = "scout"
    SANDBOX = "sandbox"
    CERTIFY = "certify"
    DEPLOY = "deploy"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class PipelineResult:
    """Result of pipeline execution"""
    success: bool
    stage: PipelineStage
    capability_id: Optional[str]
    errors: List[str]
    duration_seconds: float
    metrics: Dict[str, Any]


class TalentPipeline:
    """
    Main orchestrator for IF.talent capability onboarding pipeline

    Usage:
        pipeline = TalentPipeline()
        result = await pipeline.onboard_capability(
            capability_name="python.async_programming",
            target_agent="new-agent-123"
        )
    """

    def __init__(self,
                 scout_agents: int = 10,
                 implementation_agents: int = 7,
                 enable_witness: bool = True):
        """
        Initialize talent onboarding pipeline

        Args:
            scout_agents: Number of Haiku agents for scouting (default: 10)
            implementation_agents: Number of Sonnet agents for implementation (default: 7)
            enable_witness: Enable IF.witness audit logging (default: True)
        """
        self.scout = Scout(num_agents=scout_agents)
        self.sandbox = Sandbox()
        self.certifier = Certifier()
        self.deployer = Deployer()
        self.enable_witness = enable_witness

        self.metrics = {
            'total_onboarded': 0,
            'total_failed': 0,
            'average_duration': 0.0
        }

    async def onboard_capability(self,
                                capability_name: str,
                                target_agent: str,
                                domain: Optional[str] = None,
                                category: Optional[str] = None,
                                skill: Optional[str] = None) -> PipelineResult:
        """
        Execute full onboarding pipeline for a new capability

        Args:
            capability_name: Name of capability to onboard (e.g., "python.async_programming")
            target_agent: Agent/swarm ID to receive capability
            domain: Optional domain override (parsed from capability_name if not provided)
            category: Optional category override
            skill: Optional skill override

        Returns:
            PipelineResult with success status and metrics
        """
        start_time = time.time()
        errors = []
        current_stage = PipelineStage.SCOUT

        try:
            # Log pipeline start
            if self.enable_witness:
                await self._log_witness(
                    operation="pipeline_start",
                    params={
                        'capability_name': capability_name,
                        'target_agent': target_agent
                    }
                )

            # Phase 1: Scout - Discover and evaluate capability
            print(f"[IF.talent] Phase 1/4: Scouting capability '{capability_name}'...")
            scout_result = await self.scout.evaluate_capability(
                capability_name=capability_name,
                target_agent=target_agent
            )

            if not scout_result.approved:
                errors.append(f"Scout phase rejected: {scout_result.reason}")
                return self._build_result(
                    success=False,
                    stage=PipelineStage.SCOUT,
                    errors=errors,
                    start_time=start_time
                )

            # Phase 2: Sandbox - Test capability in isolation
            current_stage = PipelineStage.SANDBOX
            print(f"[IF.talent] Phase 2/4: Sandbox testing capability...")
            sandbox_result = await self.sandbox.test_capability(
                capability=scout_result.capability_profile,
                target_agent=target_agent
            )

            if not sandbox_result.passed:
                errors.append(f"Sandbox phase failed: {sandbox_result.reason}")
                return self._build_result(
                    success=False,
                    stage=PipelineStage.SANDBOX,
                    errors=errors,
                    start_time=start_time
                )

            # Phase 3: Certify - Validate against F6.12 schema and F6.11 reputation
            current_stage = PipelineStage.CERTIFY
            print(f"[IF.talent] Phase 3/4: Certifying capability...")
            cert_result = await self.certifier.certify_capability(
                capability=sandbox_result.validated_capability,
                sandbox_metrics=sandbox_result.metrics
            )

            if not cert_result.certified:
                errors.append(f"Certification failed: {cert_result.reason}")
                return self._build_result(
                    success=False,
                    stage=PipelineStage.CERTIFY,
                    errors=errors,
                    start_time=start_time
                )

            # Phase 4: Deploy - Register in IF.governor
            current_stage = PipelineStage.DEPLOY
            print(f"[IF.talent] Phase 4/4: Deploying to IF.governor...")
            deploy_result = await self.deployer.deploy_capability(
                capability=cert_result.certified_capability,
                target_agent=target_agent
            )

            if not deploy_result.success:
                errors.append(f"Deployment failed: {deploy_result.reason}")
                return self._build_result(
                    success=False,
                    stage=PipelineStage.DEPLOY,
                    errors=errors,
                    start_time=start_time
                )

            # Success!
            duration = time.time() - start_time
            self.metrics['total_onboarded'] += 1
            self.metrics['average_duration'] = (
                (self.metrics['average_duration'] * (self.metrics['total_onboarded'] - 1) + duration) /
                self.metrics['total_onboarded']
            )

            print(f"[IF.talent] ✅ Pipeline complete! Capability '{capability_name}' deployed in {duration:.2f}s")

            if self.enable_witness:
                await self._log_witness(
                    operation="pipeline_complete",
                    params={
                        'capability_name': capability_name,
                        'target_agent': target_agent,
                        'capability_id': deploy_result.capability_id,
                        'duration_seconds': duration
                    }
                )

            return PipelineResult(
                success=True,
                stage=PipelineStage.COMPLETE,
                capability_id=deploy_result.capability_id,
                errors=[],
                duration_seconds=duration,
                metrics={
                    'scout': scout_result.metrics,
                    'sandbox': sandbox_result.metrics,
                    'certify': cert_result.metrics,
                    'deploy': deploy_result.metrics
                }
            )

        except Exception as e:
            errors.append(f"Pipeline exception in {current_stage.value}: {str(e)}")
            self.metrics['total_failed'] += 1

            if self.enable_witness:
                await self._log_witness(
                    operation="pipeline_failed",
                    params={
                        'capability_name': capability_name,
                        'target_agent': target_agent,
                        'stage': current_stage.value,
                        'error': str(e)
                    }
                )

            return self._build_result(
                success=False,
                stage=current_stage,
                errors=errors,
                start_time=start_time
            )

    async def batch_onboard(self,
                           capabilities: List[Dict[str, str]],
                           target_agent: str,
                           parallel: bool = True) -> List[PipelineResult]:
        """
        Onboard multiple capabilities in batch

        Args:
            capabilities: List of capability dicts with 'name', optional 'domain', etc.
            target_agent: Target agent/swarm ID
            parallel: Run onboarding in parallel (default: True)

        Returns:
            List of PipelineResult for each capability
        """
        if parallel:
            tasks = [
                self.onboard_capability(
                    capability_name=cap['name'],
                    target_agent=target_agent,
                    domain=cap.get('domain'),
                    category=cap.get('category'),
                    skill=cap.get('skill')
                )
                for cap in capabilities
            ]
            return await asyncio.gather(*tasks)
        else:
            results = []
            for cap in capabilities:
                result = await self.onboard_capability(
                    capability_name=cap['name'],
                    target_agent=target_agent,
                    domain=cap.get('domain'),
                    category=cap.get('category'),
                    skill=cap.get('skill')
                )
                results.append(result)
            return results

    def _build_result(self,
                     success: bool,
                     stage: PipelineStage,
                     errors: List[str],
                     start_time: float,
                     capability_id: Optional[str] = None) -> PipelineResult:
        """Build a PipelineResult object"""
        return PipelineResult(
            success=success,
            stage=stage,
            capability_id=capability_id,
            errors=errors,
            duration_seconds=time.time() - start_time,
            metrics={}
        )

    async def _log_witness(self, operation: str, params: Dict[str, Any]):
        """Log operation to IF.witness for audit trail"""
        try:
            from infrafabric.witness import log_operation
            await log_operation(
                component='IF.talent.pipeline',
                operation=operation,
                params=params
            )
        except ImportError:
            # IF.witness not available yet
            pass

    def get_metrics(self) -> Dict[str, Any]:
        """Get pipeline execution metrics"""
        return {
            **self.metrics,
            'success_rate': (
                self.metrics['total_onboarded'] /
                (self.metrics['total_onboarded'] + self.metrics['total_failed'])
                if (self.metrics['total_onboarded'] + self.metrics['total_failed']) > 0
                else 0.0
            )
        }
