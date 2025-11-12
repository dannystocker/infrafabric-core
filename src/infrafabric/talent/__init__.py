"""
IF.talent - AI Capability Onboarding Pipeline

Scout → Sandbox → Certify → Deploy pipeline for onboarding new AI capabilities
into InfraFabric's IF.governor capability registry.

Pipeline Phases:
1. Scout: Discover and evaluate new AI capabilities (Haiku agents)
2. Sandbox: Test capabilities in isolated IF.chassis environment
3. Certify: Validate against F6.12 schema and F6.11 reputation requirements
4. Deploy: Register in IF.governor capability registry

Integration Points:
- IF.governor: Capability registry (F6.12 schema)
- IF.chassis: Sandbox runtime for safe testing
- IF.coordinator: Task distribution for pipeline phases
- IF.witness: Audit logging for certification decisions
"""

from .pipeline import TalentPipeline
from .scout import Scout
from .sandbox import Sandbox
from .certify import Certifier
from .deploy import Deployer

__all__ = [
    'TalentPipeline',
    'Scout',
    'Sandbox',
    'Certifier',
    'Deployer'
]

__version__ = '0.1.0'
