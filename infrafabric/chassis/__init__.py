"""IF.chassis - WASM sandbox runtime for secure swarm execution

This module provides WASM-based sandboxing for swarms to ensure:
- Resource isolation (CPU/memory limits)
- Security containment
- Scoped credentials
- SLO tracking
- Reputation system

Philosophy: IF.ground (Wu Lun - 五倫)
- Security through isolation
- Trust through reputation
- Transparency through SLOs

Part of Phase 0: Bug #3 (Security/Isolation) fix
"""

from .runtime import IFChassis, ServiceContract
from .limits import ResourceLimits, ResourceEnforcer, TokenBucket

__all__ = [
    'IFChassis',
    'ServiceContract',
    'ResourceLimits',
    'ResourceEnforcer',
    'TokenBucket',
]
