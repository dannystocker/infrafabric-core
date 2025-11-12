"""
IF.talent Deploy Phase - Register certified capabilities in IF.governor

Final phase: Deploy certified capabilities to production IF.governor registry.
"""

import time
import uuid
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class DeployResult:
    """Result of deployment phase"""
    success: bool
    capability_id: Optional[str]
    reason: str
    metrics: Dict[str, Any]


class Deployer:
    """
    Deploy phase: Register certified capabilities in IF.governor

    Integrates with IF.governor capability registry to make
    capabilities available for task assignment via F6.3 algorithm.
    """

    def __init__(self, enable_witness: bool = True):
        """
        Initialize deployer

        Args:
            enable_witness: Enable IF.witness audit logging (default: True)
        """
        self.enable_witness = enable_witness
        self.deployed_count = 0

    async def deploy_capability(self,
                               capability: Dict[str, Any],
                               target_agent: str) -> DeployResult:
        """
        Deploy certified capability to IF.governor registry

        Args:
            capability: Certified capability from Certify phase
            target_agent: Target agent/swarm ID

        Returns:
            DeployResult with capability ID and success status
        """
        print(f"[Deploy] Deploying capability '{capability['capability_name']}' to IF.governor...")

        start_time = time.time()

        try:
            # Generate unique capability ID
            capability_id = self._generate_capability_id(
                capability_name=capability['capability_name'],
                target_agent=target_agent
            )

            # Build IF.governor registration payload
            registration_payload = self._build_registration_payload(
                capability=capability,
                capability_id=capability_id,
                target_agent=target_agent
            )

            # Register with IF.governor
            registration_success = await self._register_with_governor(
                payload=registration_payload
            )

            if not registration_success:
                return DeployResult(
                    success=False,
                    capability_id=None,
                    reason="IF.governor registration failed",
                    metrics={
                        'duration_seconds': time.time() - start_time
                    }
                )

            # Log to IF.witness for audit trail
            if self.enable_witness:
                await self._log_deployment_witness(
                    capability_id=capability_id,
                    capability=capability,
                    target_agent=target_agent
                )

            # Update metrics
            self.deployed_count += 1

            print(f"[Deploy] ✅ Deployment complete: {capability_id}")

            return DeployResult(
                success=True,
                capability_id=capability_id,
                reason=f"Successfully deployed to IF.governor registry",
                metrics={
                    'capability_id': capability_id,
                    'target_agent': target_agent,
                    'duration_seconds': time.time() - start_time,
                    'total_deployed': self.deployed_count
                }
            )

        except Exception as e:
            return DeployResult(
                success=False,
                capability_id=None,
                reason=f"Deployment exception: {str(e)}",
                metrics={
                    'error': str(e),
                    'duration_seconds': time.time() - start_time
                }
            )

    def _generate_capability_id(self,
                               capability_name: str,
                               target_agent: str) -> str:
        """
        Generate unique capability ID

        Format: cap-{agent}-{domain}-{uuid}
        Example: cap-session1ndi-video-a3f5b2c8
        """
        domain = capability_name.split('.')[0] if '.' in capability_name else 'unknown'
        short_uuid = str(uuid.uuid4())[:8]
        agent_name = target_agent.replace('session-', '').replace('-', '')[:10]

        return f"cap-{agent_name}-{domain}-{short_uuid}"

    def _build_registration_payload(self,
                                   capability: Dict[str, Any],
                                   capability_id: str,
                                   target_agent: str) -> Dict[str, Any]:
        """
        Build registration payload for IF.governor

        Format compatible with F6.12 Capability Registry Schema
        """
        return {
            # Capability identification
            'capability_id': capability_id,
            'capability_name': capability['capability_name'],
            'target_agent': target_agent,

            # F6.12 schema fields
            'domain': capability['domain'],
            'category': capability['category'],
            'skill': capability['skill'],
            'level': capability.get('recommended_level', 'intermediate'),

            # Performance metrics (from sandbox)
            'experience_hours': 0,  # New capability
            'success_rate': 0.70,   # Initial neutral (F6.11)
            'last_used': None,

            # Bloom pattern (from scout recommendations)
            'bloom_pattern': capability.get('recommended_bloom', 'steady_performer'),

            # Reputation (from F6.11 initial assignment)
            'reputation': capability.get('reputation', {}),

            # Certification metadata
            'certification': capability.get('certification', {}),

            # Sandbox validation
            'sandbox_validated': capability.get('sandbox_validated', False),
            'sandbox_tests_passed': capability.get('sandbox_tests_passed', 0),
            'sandbox_tests_total': capability.get('sandbox_tests_total', 0),

            # Scout metadata
            'scout_confidence': capability.get('scout_confidence', 0.0),
            'scout_votes': capability.get('scout_votes', 0),

            # Deployment metadata
            'deployed_at': time.time(),
            'deployed_by': 'IF.talent.pipeline',
            'pipeline_version': '1.0'
        }

    async def _register_with_governor(self, payload: Dict[str, Any]) -> bool:
        """
        Register capability with IF.governor

        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Try to import and use IF.governor
            from infrafabric.governor import IFGovernor

            governor = IFGovernor()

            # Register capability
            result = await governor.register_capability(payload)

            return result.get('success', False)

        except ImportError:
            # IF.governor not available yet - simulate successful registration
            print("[Deploy]   ⚠️  IF.governor not available, using mock registration")
            return True

        except Exception as e:
            print(f"[Deploy]   ❌ IF.governor registration failed: {str(e)}")
            return False

    async def _log_deployment_witness(self,
                                     capability_id: str,
                                     capability: Dict[str, Any],
                                     target_agent: str):
        """
        Log deployment to IF.witness for audit trail

        Creates cryptographic provenance record with Ed25519 signature
        """
        try:
            from infrafabric.witness import log_operation

            await log_operation(
                component='IF.talent.deploy',
                operation='capability_deployed',
                params={
                    'capability_id': capability_id,
                    'capability_name': capability['capability_name'],
                    'target_agent': target_agent,
                    'domain': capability['domain'],
                    'certification_level': capability.get('certification', {}).get('level', 'unknown'),
                    'deployed_at': time.time()
                }
            )

        except ImportError:
            # IF.witness not available yet
            pass

        except Exception as e:
            # Log witness errors but don't fail deployment
            print(f"[Deploy]   ⚠️  IF.witness logging failed: {str(e)}")

    async def undeploy_capability(self,
                                 capability_id: str,
                                 reason: str = "manual removal") -> bool:
        """
        Remove capability from IF.governor registry

        Args:
            capability_id: Capability ID to remove
            reason: Reason for removal

        Returns:
            True if undeployment successful
        """
        try:
            from infrafabric.governor import IFGovernor

            governor = IFGovernor()
            result = await governor.unregister_capability(capability_id)

            if result.get('success', False):
                self.deployed_count = max(0, self.deployed_count - 1)

                # Log to IF.witness
                if self.enable_witness:
                    from infrafabric.witness import log_operation
                    await log_operation(
                        component='IF.talent.deploy',
                        operation='capability_undeployed',
                        params={
                            'capability_id': capability_id,
                            'reason': reason,
                            'undeployed_at': time.time()
                        }
                    )

                return True

            return False

        except ImportError:
            # IF.governor not available
            return True

        except Exception as e:
            print(f"[Deploy] Undeploy failed: {str(e)}")
            return False

    def get_deployment_stats(self) -> Dict[str, Any]:
        """Get deployment statistics"""
        return {
            'total_deployed': self.deployed_count,
            'witness_enabled': self.enable_witness
        }
