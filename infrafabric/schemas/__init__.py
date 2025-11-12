"""
InfraFabric Schema Definitions

Data structures and validation for IF components.
"""

from .capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
    TaskRequirements,
    validate_capability_manifest,
    validate_swarm_profile
)

__all__ = [
    'Capability',
    'SwarmProfile',
    'ResourcePolicy',
    'TaskRequirements',
    'validate_capability_manifest',
    'validate_swarm_profile'
]
