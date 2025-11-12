"""
IF: InfraFabric - Infrastructure-Level Weighted Coordination

Developer-friendly library for weighted coordination, governance, and self-improving systems.

Import Style (Developer Ergonomics):
    # Style 1: Direct import (explicit, brand awareness)
    from infrafabric.guardians import debate_proposal
    from infrafabric.coordination import WeightedCoordinator
    from infrafabric.manifests import create_manifest

    # Style 2: Shorthand alias (practical, developer-friendly)
    import infrafabric as IF
    result = IF.guardians.debate_proposal(proposal)

    # Style 3: Short module name (balanced)
    from infrafabric import guardians, coordination, manifests
    guardians.debate_proposal(proposal)

Brand Recognition:
    "InfraFabric" - Full name for brand awareness
    "IF" - Uppercase alias for Python ergonomics (if is reserved)

Philosophy:
  "The same coordination mechanism that builds the system governs the system"

Core Modules:
- infrafabric.guardians: Pluridisciplinary oversight panel with weighted debate
- infrafabric.coordination: Weighted agent coordination (0.0 → 2.0 adaptive weighting)
- infrafabric.manifests: Self-documenting provenance and manifest generation
- infrafabric.discovery: Contact discovery using multiple agent strategies (coming soon)

Phase 0 Modules (Swarm of Swarms):
- infrafabric.coordinator: Atomic task coordination and real-time broadcast
- infrafabric.event_bus: Event bus for S² real-time coordination
- infrafabric.governor: Capability-aware resource and budget management
- infrafabric.chassis: WASM sandbox runtime with resource limits
- infrafabric.witness: Cryptographic provenance and audit logging
- infrafabric.optimise: Cost tracking and optimization
- infrafabric.schemas: Data schemas for swarms and capabilities

Author: InfraFabric Research
License: MIT (to be formalized)
Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "InfraFabric Research"
__brand__ = "InfraFabric"
__shorthand__ = "IF"

# Core exports
from .guardians import GuardianPanel, Guardian, debate_proposal
from .coordination import WeightedCoordinator, Agent, AgentProfile
from .manifests import ManifestGenerator, create_manifest

# Phase 0 exports
from .coordinator import IFCoordinator
from .event_bus import EventBus, get_event_bus
from .governor import IFGovernor
from .schemas.capability import Capability, SwarmProfile, ResourcePolicy

__all__ = [
    'GuardianPanel',
    'Guardian',
    'debate_proposal',
    'WeightedCoordinator',
    'Agent',
    'AgentProfile',
    'ManifestGenerator',
    'create_manifest',
    # Phase 0
    'IFCoordinator',
    'EventBus',
    'get_event_bus',
    'IFGovernor',
    'Capability',
    'SwarmProfile',
    'ResourcePolicy',
]
