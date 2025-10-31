"""
InfraFabric: Infrastructure-Level Weighted Coordination

A library implementing weighted coordination mechanisms for multi-agent systems,
governance frameworks, and self-improving infrastructure.

Core Modules:
- guardians: Pluridisciplinary oversight panel with weighted debate
- coordination: Weighted agent coordination (0.0 → 2.0 adaptive weighting)
- manifests: Self-documenting provenance and manifest generation
- discovery: Contact discovery using multiple agent strategies

Philosophy:
  "The same coordination mechanism that builds the system governs the system"

Author: InfraFabric Research
License: MIT (to be formalized)
"""

__version__ = "0.1.0"
__author__ = "InfraFabric Research"

# Core exports
from .guardians import GuardianPanel, Guardian, debate_proposal
from .coordination import WeightedCoordinator, Agent, AgentProfile
from .manifests import ManifestGenerator, create_manifest

__all__ = [
    'GuardianPanel',
    'Guardian',
    'debate_proposal',
    'WeightedCoordinator',
    'Agent',
    'AgentProfile',
    'ManifestGenerator',
    'create_manifest',
]
