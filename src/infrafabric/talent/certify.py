"""
IF.talent Certify Phase - Validate capabilities against F6.12 schema and F6.11 reputation

Ensures capabilities meet InfraFabric standards before deployment.
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class CertificationLevel(Enum):
    """Certification trust levels"""
    BRONZE = "bronze"      # Basic validation passed
    SILVER = "silver"      # Full validation + performance tests
    GOLD = "gold"          # Silver + security audit + reputation history
    PLATINUM = "platinum"  # Gold + external verification


@dataclass
class CertifyResult:
    """Result of certification phase"""
    certified: bool
    certified_capability: Optional[Dict[str, Any]]
    reason: str
    certification_level: Optional[CertificationLevel]
    metrics: Dict[str, Any]
    validation_results: Dict[str, bool]


class Certifier:
    """
    Certify phase: Validate capabilities against InfraFabric standards

    Validates against:
    - F6.12: Capability Registry Schema (YAML structure, domain taxonomy)
    - F6.11: Reputation Scoring System (initial reputation assignment)
    - Security requirements (scoped credentials, sandbox compliance)
    - Performance requirements (latency, throughput)
    """

    def __init__(self, require_f612_compliance: bool = True):
        """
        Initialize certifier

        Args:
            require_f612_compliance: Enforce F6.12 schema compliance (default: True)
        """
        self.require_f612_compliance = require_f612_compliance

    async def certify_capability(self,
                                capability: Dict[str, Any],
                                sandbox_metrics: Dict[str, Any]) -> CertifyResult:
        """
        Certify capability against InfraFabric standards

        Args:
            capability: Validated capability from Sandbox phase
            sandbox_metrics: Performance metrics from sandbox testing

        Returns:
            CertifyResult with certification decision and level
        """
        print(f"[Certify] Validating capability '{capability['capability_name']}' against standards...")

        start_time = time.time()
        validation_results = {}

        # Validation 1: F6.12 Schema Compliance
        print(f"[Certify]   Checking F6.12 schema compliance...")
        f612_valid = await self._validate_f612_schema(capability)
        validation_results['f612_schema'] = f612_valid

        if self.require_f612_compliance and not f612_valid:
            return self._build_failure_result(
                reason="Failed F6.12 schema validation",
                validation_results=validation_results,
                start_time=start_time
            )

        # Validation 2: Domain Taxonomy
        print(f"[Certify]   Checking domain taxonomy...")
        taxonomy_valid = await self._validate_domain_taxonomy(capability)
        validation_results['domain_taxonomy'] = taxonomy_valid

        if not taxonomy_valid:
            return self._build_failure_result(
                reason="Invalid domain taxonomy (not in F6.12 domain list)",
                validation_results=validation_results,
                start_time=start_time
            )

        # Validation 3: Skill Level Assignment
        print(f"[Certify]   Validating skill level...")
        skill_level_valid = await self._validate_skill_level(capability)
        validation_results['skill_level'] = skill_level_valid

        # Validation 4: Initial Reputation Score (F6.11)
        print(f"[Certify]   Assigning initial reputation...")
        reputation_assigned = await self._assign_initial_reputation(capability)
        validation_results['reputation_assigned'] = reputation_assigned

        # Validation 5: Security Requirements
        print(f"[Certify]   Checking security requirements...")
        security_valid = await self._validate_security(capability, sandbox_metrics)
        validation_results['security'] = security_valid

        if not security_valid:
            return self._build_failure_result(
                reason="Failed security validation",
                validation_results=validation_results,
                start_time=start_time
            )

        # Validation 6: Performance Requirements
        print(f"[Certify]   Checking performance requirements...")
        performance_valid = await self._validate_performance(sandbox_metrics)
        validation_results['performance'] = performance_valid

        # Determine certification level
        cert_level = self._determine_certification_level(validation_results)

        # Build certified capability
        certified_capability = {
            **capability,
            'certification': {
                'certified': True,
                'level': cert_level.value,
                'validated_at': time.time(),
                'validation_results': validation_results,
                'certifier_version': '1.0'
            }
        }

        passed_validations = sum(1 for v in validation_results.values() if v)
        total_validations = len(validation_results)

        print(f"[Certify] ✅ Certification complete: {cert_level.value.upper()} level ({passed_validations}/{total_validations} validations passed)")

        return CertifyResult(
            certified=True,
            certified_capability=certified_capability,
            reason=f"Certified at {cert_level.value.upper()} level",
            certification_level=cert_level,
            metrics={
                'certification_level': cert_level.value,
                'validations_passed': passed_validations,
                'validations_total': total_validations,
                'duration_seconds': time.time() - start_time
            },
            validation_results=validation_results
        )

    async def _validate_f612_schema(self, capability: Dict[str, Any]) -> bool:
        """
        Validate capability against F6.12 Capability Registry Schema

        Required fields from F6.12:
        - capability_name
        - domain
        - category
        - skill
        - recommended_level (or level)
        """
        required_fields = ['capability_name', 'domain', 'category', 'skill']

        for field in required_fields:
            if field not in capability:
                return False

        # Check for level field (can be recommended_level or level)
        has_level = 'recommended_level' in capability or 'level' in capability

        return has_level

    async def _validate_domain_taxonomy(self, capability: Dict[str, Any]) -> bool:
        """
        Validate that domain is in F6.12 recognized taxonomy

        From F6.12 CAPABILITY-REGISTRY-SCHEMA.md:
        - video, telephony, crypto, infra, cloud, smart_home
        - programming, documentation, architecture, talent
        - payment, chat, ai_ml
        """
        recognized_domains = [
            'video', 'telephony', 'crypto', 'infra', 'cloud',
            'smart_home', 'programming', 'documentation', 'architecture',
            'talent', 'payment', 'chat', 'ai_ml'
        ]

        domain = capability.get('domain', '').lower()
        return domain in recognized_domains

    async def _validate_skill_level(self, capability: Dict[str, Any]) -> bool:
        """
        Validate skill level assignment

        From F6.12 skill levels: novice, intermediate, advanced, expert
        """
        valid_levels = ['novice', 'intermediate', 'advanced', 'expert']

        level = capability.get('recommended_level') or capability.get('level', '')
        return level.lower() in valid_levels

    async def _assign_initial_reputation(self, capability: Dict[str, Any]) -> bool:
        """
        Assign initial reputation score per F6.11 Reputation Scoring System

        New capabilities start with neutral reputation (0.70 - Acceptable tier)
        per F6.11 design.
        """
        capability['reputation'] = {
            'overall_score': 0.70,      # Neutral for new capabilities (F6.11)
            'reliability': 0.70,
            'quality': 0.70,
            'speed': 0.70,
            'cost_efficiency': 0.70,
            'bloom_accuracy': 0.70,
            'tier': 'acceptable',       # Acceptable tier (0.60-0.74)
            'tasks_completed': 0,
            'last_updated': time.time(),
            'notes': 'Initial reputation for new capability'
        }

        return True

    async def _validate_security(self,
                                capability: Dict[str, Any],
                                sandbox_metrics: Dict[str, Any]) -> bool:
        """
        Validate security requirements

        Requirements:
        - Sandbox validation passed
        - No critical security test failures
        """
        # Check sandbox was validated
        sandbox_validated = capability.get('sandbox_validated', False)

        if not sandbox_validated:
            return False

        # Check pass rate
        pass_rate = capability.get('sandbox_pass_rate', 0.0)

        # Require 100% pass rate (all tests passed)
        return pass_rate == 1.0

    async def _validate_performance(self, sandbox_metrics: Dict[str, Any]) -> bool:
        """
        Validate performance requirements

        From sandbox metrics:
        - Pass rate should be 1.0 (100%)
        - Duration should be reasonable (<60s)
        """
        pass_rate = sandbox_metrics.get('pass_rate', 0.0)
        duration = sandbox_metrics.get('duration_seconds', 0.0)

        return pass_rate == 1.0 and duration < 60.0

    def _determine_certification_level(self,
                                      validation_results: Dict[str, bool]) -> CertificationLevel:
        """
        Determine certification level based on validation results

        Levels:
        - Bronze: Basic validation (F6.12 schema, taxonomy)
        - Silver: Bronze + skill level + reputation
        - Gold: Silver + security + performance
        - Platinum: Gold + external verification (not implemented in Phase 0)
        """
        required_for_gold = [
            'f612_schema',
            'domain_taxonomy',
            'skill_level',
            'reputation_assigned',
            'security',
            'performance'
        ]

        required_for_silver = [
            'f612_schema',
            'domain_taxonomy',
            'skill_level',
            'reputation_assigned'
        ]

        required_for_bronze = [
            'f612_schema',
            'domain_taxonomy'
        ]

        # Check Gold (highest achievable in Phase 0)
        if all(validation_results.get(key, False) for key in required_for_gold):
            return CertificationLevel.GOLD

        # Check Silver
        if all(validation_results.get(key, False) for key in required_for_silver):
            return CertificationLevel.SILVER

        # Check Bronze
        if all(validation_results.get(key, False) for key in required_for_bronze):
            return CertificationLevel.BRONZE

        # Should not reach here if certification passed
        return CertificationLevel.BRONZE

    def _build_failure_result(self,
                             reason: str,
                             validation_results: Dict[str, bool],
                             start_time: float) -> CertifyResult:
        """Build a failure result"""
        return CertifyResult(
            certified=False,
            certified_capability=None,
            reason=reason,
            certification_level=None,
            metrics={
                'duration_seconds': time.time() - start_time,
                'validation_results': validation_results
            },
            validation_results=validation_results
        )
