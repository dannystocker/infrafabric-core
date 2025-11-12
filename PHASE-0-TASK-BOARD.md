# Phase 0 Task Board (Live Status)

**Last Updated:** 2025-11-12T00:00:00Z
**Status:** IN_PROGRESS
**Sessions Active:** 5 (1-NDI, 2-WebRTC, 3-H.323, 4-SIP, 5-CLI, 7-IF.bus)
**Total Tasks:** 46 (26 critical path + 20 filler)
**Coordination Branch:** `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`

---

## Task Status Key

- 🔵 **AVAILABLE** - Ready to claim (no blockers)
- 🟡 **CLAIMED** - Someone is working on it
- 🟢 **COMPLETED** - Done and tested
- 🔴 **BLOCKED** - Waiting for dependency

---

## Critical Path Overview

```
P0.1.1 (etcd setup) ──┬──> P0.1.2 (CAS) ──┬──> P0.1.4 (latency tests) ──> P0.1.5 (integration)
                      │                    │
                      └──> P0.1.3 (pub/sub)┘

P0.2.1 (capability schema) ──> P0.2.2 (match) ──┬──> P0.2.5 (policy engine) ──> P0.2.6 (integration)
                                                 │
P0.2.3 (budget) ──> P0.2.4 (circuit breakers) ──┘

P0.3.1 (WASM runtime) ──┬──> P0.3.2 (limits) ──> P0.3.4 (SLO) ──> P0.3.5 (reputation) ──> P0.3.6 (audit)
                        │
                        └──> P0.3.3 (scoped creds) ──────────────┘
```

**Estimated Wall-Clock:** 6-8 hours with full parallelism
**Estimated Cost:** $360-450

---

## IF.coordinator Tasks (Bug #1 - CRITICAL)

**Fixes:** 30,000ms git polling latency → <10ms real-time coordination

| ID | Task | Status | Owner | Dependencies | Deliverable | Est | Model |
|----|------|--------|-------|--------------|-------------|-----|-------|
| P0.1.1 | Setup etcd/NATS event bus | 🔵 AVAILABLE | - | None | `/home/user/infrafabric/infrafabric/event_bus.py` | 1h | Haiku |
| P0.1.2 | Implement atomic CAS operations | 🔵 AVAILABLE | - | P0.1.1 | `/home/user/infrafabric/infrafabric/coordinator.py` (CAS methods) | 2h | Sonnet |
| P0.1.3 | Implement real-time task broadcast | 🔵 AVAILABLE | - | P0.1.1 | `/home/user/infrafabric/infrafabric/coordinator.py` (pub/sub) | 2h | Sonnet |
| P0.1.4 | Latency verification (<10ms) | 🔴 BLOCKED | - | P0.1.2, P0.1.3 | `/home/user/infrafabric/tests/test_coordinator_latency.py` | 1h | Haiku |
| P0.1.5 | Integration tests | 🔴 BLOCKED | - | P0.1.1, P0.1.2, P0.1.3, P0.1.4 | `/home/user/infrafabric/tests/integration/test_coordinator.py` | 2h | Sonnet |

### P0.1.1: Setup etcd/NATS event bus

**Description:** Create event bus infrastructure using either etcd or NATS for real-time coordination

**Acceptance Criteria:**
- [ ] etcd or NATS client library installed and configured
- [ ] EventBus class with connect(), disconnect(), put(), get() methods
- [ ] Connection health check functional
- [ ] Unit tests for connection handling
- [ ] Environment-based configuration (localhost default, production-ready)
- [ ] Graceful reconnection on connection loss

**Implementation Guide:**
```python
# infrafabric/event_bus.py

import etcd3  # or import nats
from typing import Optional, Any
import asyncio

class EventBus:
    """Real-time event bus for IF.coordinator"""

    def __init__(self, host='localhost', port=2379):
        self.host = host
        self.port = port
        self.client = None

    async def connect(self):
        """Establish connection to event bus"""
        # Implementation here
        pass

    async def put(self, key: str, value: str) -> bool:
        """Store key-value pair"""
        pass

    async def get(self, key: str) -> Optional[str]:
        """Retrieve value by key"""
        pass

    async def watch(self, prefix: str, callback):
        """Watch for changes to keys with prefix"""
        pass

    async def health_check(self) -> bool:
        """Check connection health"""
        pass
```

**Testing:**
- Connection successful to local etcd/NATS
- Put/get operations work correctly
- Watch notifications trigger callbacks
- Health check detects disconnection

---

### P0.1.2: Implement atomic CAS operations

**Description:** Add Compare-And-Swap (CAS) operations for race-free task claiming

**Acceptance Criteria:**
- [ ] `claim_task(swarm_id, task_id)` method with atomic CAS
- [ ] Only one swarm can claim a task (race condition eliminated)
- [ ] Failed claims return False (task already claimed)
- [ ] Successful claims logged to IF.witness
- [ ] Unit tests for concurrent claim attempts
- [ ] Performance: claim operation <5ms

**Implementation Guide:**
```python
# infrafabric/coordinator.py

from infrafabric.event_bus import EventBus
import json
import time

class IFCoordinator:
    """Real-time coordination service for S² swarms"""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    async def claim_task(self, swarm_id: str, task_id: str) -> bool:
        """
        Atomically claim a task (CAS operation)
        Returns True if claim successful, False if already claimed
        """
        key = f'/tasks/{task_id}/owner'

        # Atomic compare-and-swap
        success = await self.event_bus.transaction(
            compare=[('value', key, '==', 'unclaimed')],
            success=[('put', key, swarm_id)],
            failure=[]
        )

        if success:
            # Log to IF.witness
            from infrafabric.witness import log_operation
            log_operation(
                component='IF.coordinator',
                operation='task_claimed',
                params={'task_id': task_id, 'swarm_id': swarm_id},
                timestamp=time.time()
            )

        return success
```

**Testing:**
- Two concurrent claim attempts → only one succeeds
- Claimed task shows correct owner
- Failed claim returns False immediately
- Witness log contains claim event
- Benchmark: 1000 claims in <5 seconds

---

### P0.1.3: Implement real-time task broadcast

**Description:** Push-based task distribution (no polling) with pub/sub

**Acceptance Criteria:**
- [ ] `register_swarm(swarm_id, capabilities)` creates task queue
- [ ] `push_task_to_swarm(swarm_id, task)` delivers task immediately
- [ ] `detect_blocker(swarm_id, info)` notifies orchestrator <10ms
- [ ] Multiple swarms can subscribe to different task channels
- [ ] Unit tests for pub/sub delivery
- [ ] Performance: push latency <10ms

**Implementation Guide:**
```python
# infrafabric/coordinator.py (continued)

class IFCoordinator:
    async def register_swarm(self, swarm_id: str, capabilities: list):
        """Register swarm and create task queue"""
        # Store capabilities in event bus
        await self.event_bus.put(
            f'/swarms/{swarm_id}/capabilities',
            json.dumps(capabilities)
        )

        # Subscribe to task channel
        await self.event_bus.subscribe(
            f'/tasks/broadcast/{swarm_id}',
            callback=self._handle_task
        )

    async def push_task_to_swarm(self, swarm_id: str, task: dict):
        """Push task immediately (no polling delay)"""
        start_time = time.time()

        await self.event_bus.publish(
            f'/tasks/broadcast/{swarm_id}',
            json.dumps(task)
        )

        latency_ms = (time.time() - start_time) * 1000
        assert latency_ms < 10, f"Latency {latency_ms}ms exceeds 10ms target"

    async def detect_blocker(self, swarm_id: str, blocker_info: dict):
        """Real-time blocker detection and escalation"""
        await self.push_task_to_swarm('orchestrator', {
            'type': 'blocker_detected',
            'swarm_id': swarm_id,
            'blocker_info': blocker_info,
            'timestamp': time.time()
        })
```

**Testing:**
- Swarm registration creates subscription
- Pushed task arrives at swarm <10ms
- Blocker notification reaches orchestrator immediately
- Multiple swarms receive independent task streams

---

### P0.1.4: Latency verification (<10ms)

**Description:** Benchmark and verify coordinator meets <10ms latency target

**Acceptance Criteria:**
- [ ] Benchmark test for claim_task() latency
- [ ] Benchmark test for push_task_to_swarm() latency
- [ ] p95 latency <10ms for both operations
- [ ] p99 latency <15ms
- [ ] Load test: 100 operations/second sustained
- [ ] Performance regression tests in CI

**Implementation Guide:**
```python
# tests/test_coordinator_latency.py

import pytest
import time
import asyncio
from infrafabric.coordinator import IFCoordinator
from infrafabric.event_bus import EventBus

@pytest.mark.asyncio
async def test_claim_task_latency():
    """Verify claim_task() meets <10ms p95 latency"""
    coordinator = IFCoordinator(EventBus())
    latencies = []

    for i in range(100):
        start = time.time()
        await coordinator.claim_task(f'swarm-1', f'task-{i}')
        latency_ms = (time.time() - start) * 1000
        latencies.append(latency_ms)

    latencies.sort()
    p95 = latencies[95]
    p99 = latencies[99]

    assert p95 < 10, f"p95 latency {p95}ms exceeds 10ms target"
    assert p99 < 15, f"p99 latency {p99}ms exceeds 15ms target"

@pytest.mark.asyncio
async def test_push_task_latency():
    """Verify push_task_to_swarm() meets <10ms p95 latency"""
    # Similar test for push operations
    pass

@pytest.mark.asyncio
async def test_concurrent_load():
    """Verify sustained 100 ops/sec"""
    # Load test implementation
    pass
```

**Testing:**
- All benchmarks pass with margin (<8ms average)
- No performance degradation under load
- CI runs benchmarks on every commit

---

### P0.1.5: Integration tests

**Description:** End-to-end integration tests for IF.coordinator

**Acceptance Criteria:**
- [ ] Test: swarm registration → task claim → task execution → completion
- [ ] Test: blocker detection → orchestrator notification → help assignment
- [ ] Test: race condition prevention (2 swarms, 1 task)
- [ ] Test: connection failure recovery
- [ ] All tests pass consistently
- [ ] Integration with IF.witness verified

**Implementation Guide:**
```python
# tests/integration/test_coordinator.py

import pytest
from infrafabric.coordinator import IFCoordinator
from infrafabric.event_bus import EventBus

@pytest.mark.asyncio
async def test_full_task_lifecycle():
    """Test complete task workflow"""
    coordinator = IFCoordinator(EventBus())

    # 1. Register swarm
    await coordinator.register_swarm('swarm-1', ['code-analysis:python'])

    # 2. Create task
    task = {'id': 'task-1', 'type': 'code-review', 'status': 'unclaimed'}
    await coordinator.create_task(task)

    # 3. Swarm claims task
    success = await coordinator.claim_task('swarm-1', 'task-1')
    assert success == True

    # 4. Verify ownership
    owner = await coordinator.get_task_owner('task-1')
    assert owner == 'swarm-1'

    # 5. Complete task
    await coordinator.complete_task('swarm-1', 'task-1', {'result': 'done'})

    # 6. Verify witness log
    from infrafabric.witness import get_operations
    ops = get_operations(component='IF.coordinator', operation='task_claimed')
    assert len(ops) > 0

@pytest.mark.asyncio
async def test_gang_up_on_blocker():
    """Test blocker detection and help coordination"""
    # Implementation here
    pass

@pytest.mark.asyncio
async def test_race_condition_prevention():
    """Two swarms try to claim same task - only one succeeds"""
    coordinator = IFCoordinator(EventBus())

    # Create task
    await coordinator.create_task({'id': 'task-1', 'status': 'unclaimed'})

    # Two swarms claim simultaneously
    results = await asyncio.gather(
        coordinator.claim_task('swarm-1', 'task-1'),
        coordinator.claim_task('swarm-2', 'task-1')
    )

    # Only one should succeed
    assert results.count(True) == 1
    assert results.count(False) == 1
```

**Testing:**
- All integration tests pass
- No race conditions detected
- Blocker workflow completes <100ms
- Witness logging verified

---

## IF.governor Tasks (Bug #2 - HIGH)

**Fixes:** 57% cost waste → <10% through capability matching and budget enforcement

| ID | Task | Status | Owner | Dependencies | Deliverable | Est | Model |
|----|------|--------|-------|--------------|-------------|-----|-------|
| P0.2.1 | Create capability registry schema | 🔵 AVAILABLE | - | None | `/home/user/infrafabric/infrafabric/schemas/capability.py` | 1h | Haiku |
| P0.2.2 | Implement 70%+ match algorithm | 🔴 BLOCKED | - | P0.2.1 | `/home/user/infrafabric/infrafabric/governor.py` (match scoring) | 2h | Sonnet |
| P0.2.3 | Budget tracking and enforcement | 🔵 AVAILABLE | - | None | `/home/user/infrafabric/infrafabric/governor.py` (budget tracking) | 2h | Sonnet |
| P0.2.4 | Circuit breaker implementation | 🔴 BLOCKED | - | P0.2.3 | `/home/user/infrafabric/infrafabric/governor.py` (circuit breaker) | 2h | Sonnet |
| P0.2.5 | Policy engine | 🔴 BLOCKED | - | P0.2.2, P0.2.3 | `/home/user/infrafabric/infrafabric/policies.py` | 2h | Sonnet |
| P0.2.6 | Integration tests | 🔴 BLOCKED | - | All above | `/home/user/infrafabric/tests/integration/test_governor.py` | 2h | Sonnet |

### P0.2.1: Create capability registry schema

**Description:** Define capability types and swarm profile data structures

**Acceptance Criteria:**
- [ ] Capability enum with 20+ capability types
- [ ] SwarmProfile dataclass with capabilities, cost, reputation
- [ ] ResourcePolicy dataclass with max_swarms, max_cost, min_capability_match
- [ ] JSON schema for capability manifests
- [ ] Validation logic for capability definitions
- [ ] Unit tests for schema validation

**Implementation Guide:**
```python
# infrafabric/schemas/capability.py

from enum import Enum
from dataclasses import dataclass
from typing import List

class Capability(Enum):
    # Code Analysis
    CODE_ANALYSIS_RUST = "code-analysis:rust"
    CODE_ANALYSIS_PYTHON = "code-analysis:python"
    CODE_ANALYSIS_JAVASCRIPT = "code-analysis:javascript"
    CODE_ANALYSIS_GO = "code-analysis:go"

    # Integrations
    INTEGRATION_SIP = "integration:sip"
    INTEGRATION_NDI = "integration:ndi"
    INTEGRATION_WEBRTC = "integration:webrtc"
    INTEGRATION_H323 = "integration:h323"

    # Infrastructure
    INFRA_DISTRIBUTED_SYSTEMS = "infra:distributed-systems"
    INFRA_NETWORKING = "infra:networking"

    # CLI/Tools
    CLI_DESIGN = "cli:design"
    CLI_TESTING = "cli:testing"

    # Architecture
    ARCHITECTURE_PATTERNS = "architecture:patterns"
    ARCHITECTURE_SECURITY = "architecture:security"

    # Documentation
    DOCS_TECHNICAL_WRITING = "docs:technical-writing"
    DOCS_API_DESIGN = "docs:api-design"

@dataclass
class SwarmProfile:
    """Profile for a swarm/session agent"""
    swarm_id: str
    capabilities: List[Capability]
    cost_per_hour: float  # Haiku: $1-2, Sonnet: $15-20
    reputation_score: float  # 0.0-1.0
    current_budget_remaining: float
    model: str  # "haiku", "sonnet", "opus"

@dataclass
class ResourcePolicy:
    """Policy constraints for resource allocation"""
    max_swarms_per_task: int = 3
    max_cost_per_task: float = 10.0
    min_capability_match: float = 0.7  # 70% match required
    circuit_breaker_failure_threshold: int = 3

def validate_capability_manifest(manifest: dict) -> bool:
    """Validate capability manifest JSON"""
    required_fields = ['swarm_id', 'capabilities', 'cost_per_hour']
    return all(field in manifest for field in required_fields)
```

**Testing:**
- All capability types defined
- SwarmProfile creation successful
- Policy validation works
- Invalid manifests rejected

---

### P0.2.2: Implement 70%+ match algorithm

**Description:** Capability matching algorithm for smart task assignment

**Acceptance Criteria:**
- [ ] `find_qualified_swarm(required_caps, max_cost)` method
- [ ] Capability overlap scoring (Jaccard similarity)
- [ ] Combined score: (capability_match × reputation) / cost
- [ ] Returns best-scoring swarm above 70% threshold
- [ ] Returns None if no qualified swarm found
- [ ] Unit tests with various capability combinations

**Implementation Guide:**
```python
# infrafabric/governor.py

from typing import List, Optional, Dict
from infrafabric.schemas.capability import Capability, SwarmProfile, ResourcePolicy

class IFGovernor:
    """Capability-aware resource and budget management"""

    def __init__(self, coordinator, policy: ResourcePolicy):
        self.coordinator = coordinator
        self.policy = policy
        self.swarm_registry: Dict[str, SwarmProfile] = {}

    def register_swarm(self, profile: SwarmProfile):
        """Register swarm with capabilities"""
        self.swarm_registry[profile.swarm_id] = profile

    def find_qualified_swarm(
        self,
        required_capabilities: List[Capability],
        max_cost: float
    ) -> Optional[str]:
        """Find best swarm based on capability match and cost"""

        candidates = []

        for swarm_id, profile in self.swarm_registry.items():
            # Calculate capability overlap (Jaccard similarity)
            capability_overlap = len(
                set(profile.capabilities) & set(required_capabilities)
            ) / len(required_capabilities)

            # Filter by policy
            if capability_overlap < self.policy.min_capability_match:
                continue  # Not qualified (below 70%)

            if profile.cost_per_hour > max_cost:
                continue  # Too expensive

            if profile.current_budget_remaining <= 0:
                continue  # Budget exhausted

            # Combined score: (capability × reputation) / cost
            # Higher is better
            score = (capability_overlap * profile.reputation_score) / profile.cost_per_hour

            candidates.append((swarm_id, score, capability_overlap))

        if not candidates:
            return None

        # Return highest-scoring swarm
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
```

**Testing:**
- 100% capability match returns swarm
- 50% capability match rejected (below 70%)
- Higher reputation swarm preferred over lower
- Cheaper swarm preferred when capabilities equal
- Budget exhaustion excludes swarm

---

### P0.2.3: Budget tracking and enforcement

**Description:** Track costs and enforce hard budget limits

**Acceptance Criteria:**
- [ ] `track_cost(swarm_id, operation, cost)` method
- [ ] Budget deducted from swarm profile
- [ ] Zero/negative budget prevents new task assignment
- [ ] Cost tracking integrated with IF.optimise
- [ ] Budget reports available via CLI
- [ ] Unit tests for budget enforcement

**Implementation Guide:**
```python
# infrafabric/governor.py (continued)

class IFGovernor:
    def track_cost(self, swarm_id: str, operation: str, cost: float):
        """Track costs and enforce budget limits"""

        if swarm_id not in self.swarm_registry:
            raise ValueError(f"Unknown swarm: {swarm_id}")

        profile = self.swarm_registry[swarm_id]
        profile.current_budget_remaining -= cost

        # Log cost to IF.optimise
        from infrafabric.optimise import track_operation_cost
        track_operation_cost(
            provider=swarm_id,
            operation=operation,
            cost=cost
        )

        # Log to IF.witness
        from infrafabric.witness import log_operation
        log_operation(
            component='IF.governor',
            operation='cost_tracked',
            params={
                'swarm_id': swarm_id,
                'operation': operation,
                'cost': cost,
                'remaining_budget': profile.current_budget_remaining
            }
        )

        # Check if budget exhausted
        if profile.current_budget_remaining <= 0:
            self._trip_circuit_breaker(swarm_id, reason='budget_exhausted')

    def get_budget_report(self) -> Dict[str, float]:
        """Get budget status for all swarms"""
        return {
            swarm_id: profile.current_budget_remaining
            for swarm_id, profile in self.swarm_registry.items()
        }
```

**Testing:**
- Cost deducted correctly
- Budget exhaustion detected
- IF.optimise receives cost events
- Budget report accurate

---

### P0.2.4: Circuit breaker implementation

**Description:** Halt swarms that exceed budget or fail repeatedly

**Acceptance Criteria:**
- [ ] `_trip_circuit_breaker(swarm_id, reason)` method
- [ ] Circuit breaker marks swarm unavailable
- [ ] No new tasks assigned to tripped swarms
- [ ] Human escalation notification sent
- [ ] Circuit breaker reset requires manual approval
- [ ] Unit tests for various trip conditions

**Implementation Guide:**
```python
# infrafabric/governor.py (continued)

class IFGovernor:
    def _trip_circuit_breaker(self, swarm_id: str, reason: str):
        """Halt swarm to prevent cost spirals or repeated failures"""

        # Mark swarm as unavailable
        profile = self.swarm_registry[swarm_id]
        profile.current_budget_remaining = 0

        # Notify coordinator to stop sending tasks
        import asyncio
        asyncio.create_task(
            self.coordinator.event_bus.put(
                f'/swarms/{swarm_id}/status',
                'circuit_breaker_tripped'
            )
        )

        # Log incident with HIGH severity
        from infrafabric.witness import log_operation
        log_operation(
            component='IF.governor',
            operation='circuit_breaker_tripped',
            params={'swarm_id': swarm_id, 'reason': reason},
            severity='HIGH'
        )

        # Escalate to human
        asyncio.create_task(
            self._escalate_to_human(swarm_id, {
                'type': 'circuit_breaker',
                'reason': reason
            })
        )

    async def _escalate_to_human(self, swarm_id: str, issue: dict):
        """ESCALATE pattern: Notify human for intervention"""

        notification = f"""
        🚨 S² System Escalation Required

        Swarm: {swarm_id}
        Issue: {issue}

        Action Required: Manual review and intervention

        To reset: if governor reset-circuit-breaker {swarm_id}
        """

        # Send notification (implementation depends on notification system)
        print(notification)  # Placeholder

    def reset_circuit_breaker(self, swarm_id: str, new_budget: float):
        """Manually reset circuit breaker (requires human approval)"""

        if swarm_id not in self.swarm_registry:
            raise ValueError(f"Unknown swarm: {swarm_id}")

        profile = self.swarm_registry[swarm_id]
        profile.current_budget_remaining = new_budget

        # Update status
        import asyncio
        asyncio.create_task(
            self.coordinator.event_bus.put(
                f'/swarms/{swarm_id}/status',
                'active'
            )
        )
```

**Testing:**
- Budget exhaustion trips breaker
- Repeated failures trip breaker
- Tripped swarm not assigned tasks
- Manual reset restores functionality

---

### P0.2.5: Policy engine

**Description:** Centralized policy management and enforcement

**Acceptance Criteria:**
- [ ] Load policies from YAML configuration
- [ ] `request_help_for_blocker()` uses capability matching
- [ ] Respects max_swarms_per_task limit
- [ ] Enforces budget constraints
- [ ] Policy violation logging
- [ ] Unit tests for policy enforcement

**Implementation Guide:**
```python
# infrafabric/policies.py

import yaml
from typing import List
from infrafabric.schemas.capability import ResourcePolicy

class PolicyEngine:
    """Manage and enforce resource policies"""

    def __init__(self, config_path: str = None):
        self.policy = ResourcePolicy()
        if config_path:
            self.load_policy(config_path)

    def load_policy(self, config_path: str):
        """Load policy from YAML configuration"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        policy_config = config.get('resource_policy', {})
        self.policy = ResourcePolicy(
            max_swarms_per_task=policy_config.get('max_swarms_per_task', 3),
            max_cost_per_task=policy_config.get('max_cost_per_task', 10.0),
            min_capability_match=policy_config.get('min_capability_match', 0.7),
            circuit_breaker_failure_threshold=policy_config.get('circuit_breaker_failure_threshold', 3)
        )

    def validate_assignment(self, swarm_ids: List[str], task_budget: float) -> bool:
        """Validate proposed task assignment against policies"""

        # Check max_swarms_per_task
        if len(swarm_ids) > self.policy.max_swarms_per_task:
            return False

        # Check max_cost_per_task
        if task_budget > self.policy.max_cost_per_task:
            return False

        return True

# Integration with IFGovernor
# infrafabric/governor.py (continued)

class IFGovernor:
    async def request_help_for_blocker(
        self,
        blocked_swarm_id: str,
        blocker_description: dict
    ) -> List[str]:
        """Smart 'Gang Up on Blocker' with capability matching"""

        # Parse required capabilities from blocker
        required_caps = self._extract_required_capabilities(blocker_description)

        task_budget = self.policy.max_cost_per_task
        assigned_swarms = []

        for capability in required_caps:
            # Find best swarm for this capability
            swarm_id = self.find_qualified_swarm(
                required_capabilities=[capability],
                max_cost=task_budget
            )

            if swarm_id and swarm_id not in assigned_swarms:
                assigned_swarms.append(swarm_id)

            # Respect policy limit
            if len(assigned_swarms) >= self.policy.max_swarms_per_task:
                break

        if not assigned_swarms:
            # No qualified swarms - escalate to human
            await self._escalate_to_human(blocked_swarm_id, blocker_description)
            return []

        # Log to witness
        from infrafabric.witness import log_operation
        log_operation(
            component='IF.governor',
            operation='help_requested',
            params={
                'blocked_swarm': blocked_swarm_id,
                'assigned_swarms': assigned_swarms,
                'required_capabilities': [c.value for c in required_caps],
                'budget': task_budget
            }
        )

        return assigned_swarms
```

**Testing:**
- Policy loaded from YAML
- Max swarms limit enforced
- Budget limit enforced
- Capability matching works
- Escalation triggered when no qualified swarms

---

### P0.2.6: Integration tests

**Description:** End-to-end tests for IF.governor

**Acceptance Criteria:**
- [ ] Test: capability matching with various swarm profiles
- [ ] Test: budget enforcement and circuit breaker
- [ ] Test: help request with qualified swarms
- [ ] Test: help request with no qualified swarms (escalation)
- [ ] Test: policy violation prevention
- [ ] All tests pass consistently

**Implementation Guide:**
```python
# tests/integration/test_governor.py

import pytest
from infrafabric.governor import IFGovernor
from infrafabric.schemas.capability import SwarmProfile, ResourcePolicy, Capability

@pytest.mark.asyncio
async def test_capability_matching():
    """Test swarm selection based on capabilities"""
    governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

    # Register swarms
    governor.register_swarm(SwarmProfile(
        swarm_id='session-1-ndi',
        capabilities=[Capability.INTEGRATION_NDI, Capability.DOCS_TECHNICAL_WRITING],
        cost_per_hour=2.0,
        reputation_score=0.95,
        current_budget_remaining=10.0,
        model='haiku'
    ))

    governor.register_swarm(SwarmProfile(
        swarm_id='session-4-sip',
        capabilities=[Capability.INTEGRATION_SIP, Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=2.0,
        reputation_score=0.90,
        current_budget_remaining=10.0,
        model='haiku'
    ))

    # Find swarm for SIP task
    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.INTEGRATION_SIP],
        max_cost=5.0
    )

    assert swarm == 'session-4-sip'

@pytest.mark.asyncio
async def test_budget_enforcement():
    """Test budget exhaustion and circuit breaker"""
    # Implementation here
    pass

@pytest.mark.asyncio
async def test_gang_up_on_blocker():
    """Test help request workflow"""
    # Implementation here
    pass
```

**Testing:**
- All integration tests pass
- Capability matching accurate
- Budget limits enforced
- Circuit breakers functional

---

## IF.chassis Tasks (Bug #3 - MEDIUM→CRITICAL)

**Fixes:** No sandboxing → WASM isolation, noisy neighbor prevention, SLO tracking

| ID | Task | Status | Owner | Dependencies | Deliverable | Est | Model |
|----|------|--------|-------|--------------|-------------|-----|-------|
| P0.3.1 | WASM runtime setup (wasmtime) | 🔵 AVAILABLE | - | None | `/home/user/infrafabric/infrafabric/chassis/runtime.py` | 3h | Sonnet |
| P0.3.2 | Resource limits (CPU/memory) | 🔴 BLOCKED | - | P0.3.1 | `/home/user/infrafabric/infrafabric/chassis/limits.py` | 2h | Sonnet |
| P0.3.3 | Scoped credentials | 🔴 BLOCKED | - | P0.3.1 | `/home/user/infrafabric/infrafabric/chassis/auth.py` | 2h | Sonnet |
| P0.3.4 | SLO tracking | 🔴 BLOCKED | - | P0.3.2 | `/home/user/infrafabric/infrafabric/chassis/slo.py` | 2h | Haiku |
| P0.3.5 | Reputation system | 🔴 BLOCKED | - | P0.3.4 | `/home/user/infrafabric/infrafabric/chassis/reputation.py` | 2h | Sonnet |
| P0.3.6 | Security audit tests | 🔴 BLOCKED | - | All above | `/home/user/infrafabric/tests/security/test_chassis.py` | 2h | Sonnet |

### P0.3.1: WASM runtime setup (wasmtime)

**Description:** Initialize WASM sandbox runtime for secure swarm execution

**Acceptance Criteria:**
- [ ] wasmtime library installed and configured
- [ ] IFChassis class with load_swarm(), execute_task() methods
- [ ] WASM module compilation functional
- [ ] Basic sandbox isolation working
- [ ] Unit tests for WASM loading
- [ ] Documentation on WASM compilation

**Implementation Guide:**
```python
# infrafabric/chassis/runtime.py

import wasmtime
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class ServiceContract:
    """Formal service contract for swarm"""
    swarm_id: str
    capabilities: list
    resource_limits: dict
    slos: dict
    version: str

class IFChassis:
    """WASM sandbox runtime for secure swarm execution"""

    def __init__(self):
        self.engine = wasmtime.Engine()
        self.swarm_runtimes: Dict[str, wasmtime.Instance] = {}
        self.contracts: Dict[str, ServiceContract] = {}

    def load_swarm(self, swarm_id: str, wasm_module: bytes, contract: ServiceContract):
        """Load swarm WASM module into sandbox"""

        # Compile WASM module
        module = wasmtime.Module(self.engine, wasm_module)

        # Create linker with limited host functions
        linker = wasmtime.Linker(self.engine)

        # Only expose safe, scoped APIs
        linker.define_func("env", "log", self._scoped_log)
        # No filesystem, no network, no exec

        # Create store
        store = wasmtime.Store(self.engine)

        # Instantiate WASM module
        instance = linker.instantiate(store, module)
        self.swarm_runtimes[swarm_id] = instance
        self.contracts[swarm_id] = contract

        # Log to witness
        from infrafabric.witness import log_operation
        log_operation(
            component='IF.chassis',
            operation='swarm_loaded',
            params={'swarm_id': swarm_id, 'version': contract.version}
        )

    def _scoped_log(self, message: str):
        """Scoped logging function for WASM modules"""
        print(f"[WASM] {message}")
```

**Testing:**
- WASM module loads successfully
- Scoped functions accessible from WASM
- Unsafe operations blocked
- Witness logging functional

---

### P0.3.2: Resource limits (CPU/memory)

**Description:** Enforce per-swarm resource limits to prevent noisy neighbor

**Acceptance Criteria:**
- [ ] ResourceLimits dataclass with max_memory_mb, max_cpu_percent, max_api_calls_per_second
- [ ] OS-level resource limits applied (setrlimit)
- [ ] Rate limiting for API calls (token bucket)
- [ ] Resource limit violations logged
- [ ] Unit tests for resource enforcement
- [ ] Performance: minimal overhead (<5%)

**Implementation Guide:**
```python
# infrafabric/chassis/limits.py

import resource
import asyncio
from dataclasses import dataclass
from typing import Dict
import time

@dataclass
class ResourceLimits:
    """Per-swarm resource limits"""
    max_memory_mb: int = 256
    max_cpu_percent: int = 25
    max_api_calls_per_second: int = 10
    max_execution_time_seconds: int = 300

class ResourceEnforcer:
    """Enforce resource limits per swarm"""

    def __init__(self):
        self.rate_limiters: Dict[str, TokenBucket] = {}

    def apply_limits(self, swarm_id: str, limits: ResourceLimits):
        """Apply OS-level resource limits"""

        # Limit memory
        resource.setrlimit(
            resource.RLIMIT_AS,
            (limits.max_memory_mb * 1024 * 1024, limits.max_memory_mb * 1024 * 1024)
        )

        # Limit CPU time
        resource.setrlimit(
            resource.RLIMIT_CPU,
            (limits.max_execution_time_seconds, limits.max_execution_time_seconds)
        )

        # No core dumps
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

        # Setup rate limiter
        self.rate_limiters[swarm_id] = TokenBucket(limits.max_api_calls_per_second)

    async def check_rate_limit(self, swarm_id: str) -> bool:
        """Check if swarm can make API call (rate limiting)"""
        if swarm_id not in self.rate_limiters:
            return True

        return await self.rate_limiters[swarm_id].consume()

class TokenBucket:
    """Token bucket rate limiter"""

    def __init__(self, rate: int):
        self.rate = rate
        self.tokens = rate
        self.last_update = time.time()

    async def consume(self) -> bool:
        """Try to consume a token"""
        now = time.time()
        elapsed = now - self.last_update

        # Refill tokens
        self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
        self.last_update = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True

        return False
```

**Testing:**
- Memory limit enforced (process killed on excess)
- CPU limit enforced (process stopped)
- Rate limiter prevents API flooding
- Performance overhead <5%

---

### P0.3.3: Scoped credentials

**Description:** Temporary, task-scoped credentials (not long-lived API keys)

**Acceptance Criteria:**
- [ ] ScopedCredentials dataclass with swarm_id, task_id, api_token, ttl_seconds
- [ ] Credentials expire after TTL
- [ ] Allowed endpoints whitelist
- [ ] Credential injection into WASM sandbox
- [ ] Unit tests for expiration
- [ ] Integration with secrets vault

**Implementation Guide:**
```python
# infrafabric/chassis/auth.py

from dataclasses import dataclass
from typing import List
import time
import secrets

@dataclass
class ScopedCredentials:
    """Temporary, task-scoped credentials"""
    swarm_id: str
    task_id: str
    api_token: str
    ttl_seconds: int
    allowed_endpoints: List[str]
    created_at: float

    @property
    def is_expired(self) -> bool:
        """Check if credentials have expired"""
        return time.time() > self.created_at + self.ttl_seconds

class CredentialManager:
    """Manage scoped credentials for swarms"""

    def __init__(self):
        self.active_credentials = {}

    def generate_scoped_credentials(
        self,
        swarm_id: str,
        task_id: str,
        ttl_seconds: int = 300,
        allowed_endpoints: List[str] = None
    ) -> ScopedCredentials:
        """Generate temporary credentials for a task"""

        # Generate secure token
        api_token = secrets.token_urlsafe(32)

        credentials = ScopedCredentials(
            swarm_id=swarm_id,
            task_id=task_id,
            api_token=api_token,
            ttl_seconds=ttl_seconds,
            allowed_endpoints=allowed_endpoints or [],
            created_at=time.time()
        )

        self.active_credentials[api_token] = credentials

        # Log to witness
        from infrafabric.witness import log_operation
        log_operation(
            component='IF.chassis',
            operation='credentials_generated',
            params={
                'swarm_id': swarm_id,
                'task_id': task_id,
                'ttl_seconds': ttl_seconds
            }
        )

        return credentials

    def validate_credentials(self, api_token: str, endpoint: str) -> bool:
        """Validate credentials for API call"""

        if api_token not in self.active_credentials:
            return False

        creds = self.active_credentials[api_token]

        # Check expiration
        if creds.is_expired:
            del self.active_credentials[api_token]
            return False

        # Check endpoint whitelist
        if creds.allowed_endpoints and endpoint not in creds.allowed_endpoints:
            return False

        return True
```

**Testing:**
- Credentials generated successfully
- Expired credentials rejected
- Non-whitelisted endpoints blocked
- Token rotation functional

---

### P0.3.4: SLO tracking

**Description:** Track swarm performance against Service Level Objectives

**Acceptance Criteria:**
- [ ] ServiceLevelObjective dataclass with p99_latency_ms, success_rate, availability
- [ ] Performance metrics collection (latency, success/failure)
- [ ] SLO compliance calculation
- [ ] SLO violations logged
- [ ] Unit tests for SLO tracking
- [ ] Dashboard integration

**Implementation Guide:**
```python
# infrafabric/chassis/slo.py

from dataclasses import dataclass
from typing import List, Dict, Optional
import time

@dataclass
class ServiceLevelObjective:
    """SLO definition"""
    p99_latency_ms: int
    success_rate: float  # 0.0-1.0
    availability: float  # 0.0-1.0

@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    timestamp: float
    latency_ms: Optional[float]
    success: bool

class SLOTracker:
    """Track swarm performance against SLOs"""

    def __init__(self):
        self.metrics: Dict[str, List[PerformanceMetric]] = {}
        self.slos: Dict[str, ServiceLevelObjective] = {}

    def set_slo(self, swarm_id: str, slo: ServiceLevelObjective):
        """Set SLO for swarm"""
        self.slos[swarm_id] = slo

    def record_metric(self, swarm_id: str, latency_ms: Optional[float], success: bool):
        """Record performance metric"""

        if swarm_id not in self.metrics:
            self.metrics[swarm_id] = []

        metric = PerformanceMetric(
            timestamp=time.time(),
            latency_ms=latency_ms,
            success=success
        )

        self.metrics[swarm_id].append(metric)

        # Keep only recent metrics (last 1000)
        self.metrics[swarm_id] = self.metrics[swarm_id][-1000:]

    def calculate_slo_compliance(self, swarm_id: str) -> Dict[str, float]:
        """Calculate SLO compliance"""

        if swarm_id not in self.metrics or swarm_id not in self.slos:
            return {}

        metrics = self.metrics[swarm_id]
        slo = self.slos[swarm_id]

        # Calculate success rate
        total = len(metrics)
        successes = sum(1 for m in metrics if m.success)
        success_rate = successes / total if total > 0 else 0.0

        # Calculate p99 latency
        latencies = [m.latency_ms for m in metrics if m.latency_ms is not None]
        if latencies:
            latencies.sort()
            p99_latency = latencies[int(len(latencies) * 0.99)]
        else:
            p99_latency = 0

        # Check compliance
        compliance = {
            'success_rate': success_rate,
            'success_rate_compliant': success_rate >= slo.success_rate,
            'p99_latency_ms': p99_latency,
            'p99_latency_compliant': p99_latency <= slo.p99_latency_ms,
            'overall_compliant': (
                success_rate >= slo.success_rate and
                p99_latency <= slo.p99_latency_ms
            )
        }

        return compliance
```

**Testing:**
- Metrics recorded correctly
- SLO compliance calculated accurately
- p99 latency calculation correct
- Success rate calculation correct

---

### P0.3.5: Reputation system

**Description:** SLO-based reputation scoring for swarm prioritization

**Acceptance Criteria:**
- [ ] Reputation score calculation based on SLO compliance
- [ ] Reputation updated after each task
- [ ] Integration with IF.governor for prioritization
- [ ] Reputation history tracking
- [ ] Unit tests for reputation scoring
- [ ] Reputation decay over time (optional)

**Implementation Guide:**
```python
# infrafabric/chassis/reputation.py

from typing import Dict
from infrafabric.chassis.slo import SLOTracker

class ReputationSystem:
    """SLO-based reputation scoring"""

    def __init__(self, slo_tracker: SLOTracker):
        self.slo_tracker = slo_tracker
        self.reputation_scores: Dict[str, float] = {}

    def calculate_reputation(self, swarm_id: str) -> float:
        """Calculate reputation score (0.0-1.0)"""

        compliance = self.slo_tracker.calculate_slo_compliance(swarm_id)

        if not compliance:
            return 1.0  # Benefit of doubt for new swarms

        # Base reputation on SLO compliance
        reputation = 1.0

        # Success rate penalty
        if not compliance['success_rate_compliant']:
            reputation *= 0.8  # 20% penalty

        # Latency penalty
        if not compliance['p99_latency_compliant']:
            reputation *= 0.9  # 10% penalty

        # Weighted by actual success rate
        reputation *= compliance['success_rate']

        # Update stored reputation
        self.reputation_scores[swarm_id] = reputation

        # Update IF.governor
        try:
            from infrafabric.governor import update_reputation
            update_reputation(swarm_id, reputation)
        except ImportError:
            pass

        return reputation

    def get_reputation(self, swarm_id: str) -> float:
        """Get current reputation score"""
        return self.reputation_scores.get(swarm_id, 1.0)
```

**Testing:**
- Reputation calculated correctly
- SLO violations decrease reputation
- High performers have high reputation
- IF.governor integration works

---

### P0.3.6: Security audit tests

**Description:** Security tests to verify sandbox isolation

**Acceptance Criteria:**
- [ ] Test: WASM cannot access filesystem
- [ ] Test: WASM cannot make network calls
- [ ] Test: Memory limit enforced (OOM killed)
- [ ] Test: CPU limit enforced (timeout)
- [ ] Test: Credential expiration prevents access
- [ ] All security tests pass

**Implementation Guide:**
```python
# tests/security/test_chassis.py

import pytest
from infrafabric.chassis.runtime import IFChassis
from infrafabric.chassis.limits import ResourceEnforcer, ResourceLimits
from infrafabric.chassis.auth import CredentialManager

@pytest.mark.security
def test_wasm_cannot_access_filesystem():
    """Verify WASM module cannot access filesystem"""
    # Load WASM module that tries to open a file
    # Should fail with permission denied
    pass

@pytest.mark.security
def test_wasm_cannot_make_network_calls():
    """Verify WASM module cannot make network requests"""
    # Load WASM module that tries to make HTTP request
    # Should fail (no network access)
    pass

@pytest.mark.security
def test_memory_limit_enforcement():
    """Verify memory limit kills process on excess"""
    enforcer = ResourceEnforcer()
    limits = ResourceLimits(max_memory_mb=128)

    # Try to allocate 256MB (should fail)
    enforcer.apply_limits('test-swarm', limits)

    # Allocation should fail or process should be killed
    pass

@pytest.mark.security
def test_credential_expiration():
    """Verify expired credentials are rejected"""
    manager = CredentialManager()

    # Generate credentials with 1 second TTL
    creds = manager.generate_scoped_credentials(
        swarm_id='test',
        task_id='task-1',
        ttl_seconds=1
    )

    # Wait for expiration
    import time
    time.sleep(2)

    # Validation should fail
    assert creds.is_expired == True
    assert manager.validate_credentials(creds.api_token, 'https://api.example.com') == False

@pytest.mark.security
def test_api_rate_limiting():
    """Verify rate limiting prevents API flooding"""
    # Implementation here
    pass
```

**Testing:**
- All security tests pass
- No security vulnerabilities found
- Sandbox isolation verified

---

## CLI Foundation Tasks

**Purpose:** Unified entry point for IF components

| ID | Task | Status | Owner | Dependencies | Deliverable | Est | Model |
|----|------|--------|-------|--------------|-------------|-----|-------|
| P0.4.1 | Unified CLI entry (`if` command) | 🔵 AVAILABLE | - | None | `/home/user/infrafabric/src/cli/if_main.py` | 2h | Haiku |
| P0.4.2 | Cost tracking integration | 🔴 BLOCKED | - | P0.2.3 | `/home/user/infrafabric/src/cli/if_cost.py` | 1h | Haiku |
| P0.4.3 | Witness integration | 🔵 AVAILABLE | - | None | `/home/user/infrafabric/src/cli/if_witness.py` | 1h | Haiku |
| P0.4.4 | Swarm spawn helper | 🔴 BLOCKED | - | P0.1.2 | `/home/user/infrafabric/src/cli/if_swarm.py` | 2h | Haiku |

### P0.4.1: Unified CLI entry (`if` command)

**Description:** Create main CLI entry point with subcommands

**Acceptance Criteria:**
- [ ] `if` command registered (click or argparse)
- [ ] Subcommands: coordinator, governor, chassis, witness, optimise
- [ ] `--why --trace --mode=falsify` flags on all commands
- [ ] Help text and documentation
- [ ] Unit tests for CLI parsing
- [ ] Installation via pip/setuptools

**Implementation Guide:**
```python
# src/cli/if_main.py

import click

@click.group()
@click.version_option()
def cli():
    """InfraFabric CLI - Unified infrastructure orchestration"""
    pass

@cli.group()
def coordinator():
    """IF.coordinator commands"""
    pass

@coordinator.command()
@click.option('--backend', type=click.Choice(['etcd', 'nats']), default='etcd')
@click.option('--host', default='localhost:2379')
def start(backend, host):
    """Start IF.coordinator service"""
    click.echo(f"Starting IF.coordinator with {backend} backend at {host}")

@coordinator.command()
def status():
    """Show coordinator status"""
    click.echo("Coordinator status: running")

@cli.group()
def governor():
    """IF.governor commands"""
    pass

@governor.command()
@click.argument('swarm_id')
@click.option('--capabilities', multiple=True)
@click.option('--cost-per-hour', type=float)
@click.option('--budget', type=float)
def register(swarm_id, capabilities, cost_per_hour, budget):
    """Register swarm with capabilities"""
    click.echo(f"Registering {swarm_id} with capabilities: {capabilities}")

@cli.group()
def chassis():
    """IF.chassis commands"""
    pass

@cli.group()
def witness():
    """IF.witness commands"""
    pass

@cli.group()
def optimise():
    """IF.optimise commands"""
    pass

if __name__ == '__main__':
    cli()
```

**Testing:**
- All subcommands accessible
- Help text clear and useful
- Flags parsed correctly
- Installation works

---

### P0.4.2: Cost tracking integration

**Description:** CLI commands for cost visibility

**Acceptance Criteria:**
- [ ] `if cost report` shows cost breakdown
- [ ] `if cost budget` shows remaining budgets
- [ ] `if cost history` shows cost over time
- [ ] Integration with IF.optimise
- [ ] CSV export functionality
- [ ] Unit tests for cost commands

---

### P0.4.3: Witness integration

**Description:** CLI commands for witness queries

**Acceptance Criteria:**
- [ ] `if witness query` searches witness log
- [ ] `if witness trace <token>` shows full chain
- [ ] `if witness verify` checks hash chain integrity
- [ ] JSON output format
- [ ] Unit tests for witness commands

---

### P0.4.4: Swarm spawn helper

**Description:** CLI helper to spawn and register swarms

**Acceptance Criteria:**
- [ ] `if swarm spawn <swarm-id>` creates new swarm
- [ ] Automatic registration with IF.coordinator
- [ ] Capability detection from swarm code
- [ ] Budget assignment
- [ ] Unit tests for swarm spawning

---

## Documentation Tasks

**Purpose:** Production docs, runbooks, integration guides

| ID | Task | Status | Owner | Dependencies | Deliverable | Est | Model |
|----|------|--------|-------|--------------|-------------|-----|-------|
| P0.5.1 | IF.coordinator documentation | 🔴 BLOCKED | - | P0.1.5 | `/home/user/infrafabric/docs/components/IF.COORDINATOR.md` | 1h | Haiku |
| P0.5.2 | IF.governor documentation | 🔴 BLOCKED | - | P0.2.6 | `/home/user/infrafabric/docs/components/IF.GOVERNOR.md` | 1h | Haiku |
| P0.5.3 | IF.chassis documentation | 🔴 BLOCKED | - | P0.3.6 | `/home/user/infrafabric/docs/components/IF.CHASSIS.md` | 1h | Haiku |
| P0.5.4 | Migration guide (git→etcd) | 🔴 BLOCKED | - | P0.1.5 | `/home/user/infrafabric/docs/MIGRATION-GIT-TO-ETCD.md` | 2h | Haiku |
| P0.5.5 | Production runbook | 🔴 BLOCKED | - | All components | `/home/user/infrafabric/docs/PHASE-0-PRODUCTION-RUNBOOK.md` | 2h | Haiku |

### P0.5.1: IF.coordinator documentation

**Description:** Complete component documentation

**Acceptance Criteria:**
- [ ] Architecture overview
- [ ] API reference
- [ ] Configuration guide
- [ ] Deployment instructions
- [ ] Troubleshooting guide
- [ ] Example usage

---

### P0.5.2: IF.governor documentation

**Description:** Complete component documentation

**Acceptance Criteria:**
- [ ] Architecture overview
- [ ] Capability registry guide
- [ ] Policy configuration
- [ ] Budget management
- [ ] Circuit breaker tuning
- [ ] Example policies

---

### P0.5.3: IF.chassis documentation

**Description:** Complete component documentation

**Acceptance Criteria:**
- [ ] Architecture overview
- [ ] WASM compilation guide
- [ ] Resource limits configuration
- [ ] SLO definition guide
- [ ] Security best practices
- [ ] Example service contracts

---

### P0.5.4: Migration guide (git→etcd)

**Description:** Migration guide from git polling to IF.coordinator

**Acceptance Criteria:**
- [ ] Step-by-step migration process
- [ ] Rollback procedures
- [ ] Testing checklist
- [ ] Performance comparison
- [ ] Troubleshooting

---

### P0.5.5: Production runbook

**Description:** Complete production operations guide

**Acceptance Criteria:**
- [ ] Deployment procedures
- [ ] Monitoring setup
- [ ] Incident response
- [ ] Backup/restore procedures
- [ ] Performance tuning
- [ ] Security checklist

---

## Filler Tasks by Session

### Session 1 (NDI) Filler Tasks

**When blocked:** Work on these low-priority tasks

| ID | Task | Description | Est |
|----|------|-------------|-----|
| F1.1 | Improve S² architecture docs | Add Phase 0 integration notes to SWARM-OF-SWARMS-ARCHITECTURE.md | 1h |
| F1.2 | IF.witness hash chain example | Create example hash chain for coordination events | 1h |
| F1.3 | Test fixtures for Session 2 | Build IFMessage mocks for WebRTC | 1h |
| F1.4 | Review NOVICE-ONBOARDING.md | Improve onboarding documentation | 1h |

---

### Session 2 (WebRTC) Filler Tasks

**When blocked:** Work on these low-priority tasks

| ID | Task | Description | Est |
|----|------|-------------|-----|
| F2.1 | Cross-session test fixtures | Build IFMessage mocks for all sessions | 1h |
| F2.2 | SDP mock data | Create SDP mocks for integration tests | 1h |
| F2.3 | Improve IF-IMPROVEMENTS-V1.1.md | Add Phase 0 learnings | 1h |
| F2.4 | Help Session 3 with H.323 docs | Assist with documentation | 1h |

---

### Session 3 (H.323) Filler Tasks

**When blocked:** Work on these low-priority tasks

| ID | Task | Description | Est |
|----|------|-------------|-----|
| F3.1 | Improve H.323 runbook | Update H323-PRODUCTION-RUNBOOK.md | 1h |
| F3.2 | MCU configuration templates | Create templates for MCU configs | 1h |
| F3.3 | Guardian council test data | Build test scenarios | 1h |
| F3.4 | Help Session 1 with NDI docs | Assist with documentation | 1h |

---

### Session 4 (SIP) Filler Tasks

**When blocked:** Work on these low-priority tasks

| ID | Task | Description | Est |
|----|------|-------------|-----|
| F4.1 | Integration test scaffolding | Pre-write test framework | 2h |
| F4.2 | Regression test data | Create test data for all components | 1h |
| F4.3 | Mock implementations | Build mocks for early testing | 1h |
| F4.4 | Security requirements review | Review security for all 3 components | 1h |
| F4.5 | Code review assistance | Help other sessions with reviews | 1h |

---

### Session 5 (CLI) Filler Tasks

**When blocked:** Work on these low-priority tasks

| ID | Task | Description | Est |
|----|------|-------------|-----|
| F5.1 | CLI help text | Build comprehensive help documentation | 1h |
| F5.2 | Config file schemas | Create YAML/TOML schemas | 1h |
| F5.3 | CLI UX flows | Design user experience flows | 1h |
| F5.4 | Error message catalog | Create standardized error messages | 1h |
| F5.5 | CLI test fixtures | Build test data for CLI commands | 1h |
| F5.6 | Help Session 7 planning | Assist with IF.bus integration | 1h |

---

### Session 7 (IF.bus) Filler Tasks

**When blocked:** Work on these low-priority tasks

| ID | Task | Description | Est |
|----|------|-------------|-----|
| F7.1 | Component interface design | Design type signatures for all components | 2h |
| F7.2 | Pydantic models | Create data models for all structures | 2h |
| F7.3 | Unit test scaffolding | Write test framework | 1h |
| F7.4 | Review existing coordination.py | Integration analysis | 1h |
| F7.5 | Architecture diagrams | Create component diagrams | 1h |

---

## Coordination Protocol

### How to Use This Board

**1. Claim a Task:**
```bash
# Pull latest board
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:PHASE-0-TASK-BOARD.md

# Find 🔵 AVAILABLE task with no dependencies
# Update your STATUS file
cat > STATUS-SESSION-{N}.yaml <<EOF
session: session-{N}
claiming: P0.X.X
timestamp: $(date -Iseconds)
branch: $(git branch --show-current)
EOF

# Commit and push
git add STATUS-SESSION-{N}.yaml
git commit -m "claim: P0.X.X"
git push
```

**2. Work on Task:**
- Follow implementation guide
- Meet all acceptance criteria
- Write tests
- Update progress every 15 minutes

**3. Mark Complete:**
```bash
# Update STATUS file
cat > STATUS-SESSION-{N}.yaml <<EOF
session: session-{N}
completed: P0.X.X
timestamp: $(date -Iseconds)
deliverable: /path/to/file.py
tests_pass: true
branch: $(git branch --show-current)
EOF

# Commit and push
git add STATUS-SESSION-{N}.yaml
git commit -m "complete: P0.X.X"
git push
```

**4. If Blocked:**
- Update STATUS to show blocker
- Pick filler task from your session list
- Check every 30 seconds if blocker resolved

### Success Criteria (Phase 0 Complete)

**IF.coordinator:**
- ✅ etcd/NATS operational
- ✅ <10ms latency (p95)
- ✅ Race conditions eliminated
- ✅ Integration tests pass

**IF.governor:**
- ✅ 70%+ capability matching
- ✅ Budget enforcement working
- ✅ Circuit breakers functional
- ✅ Cost waste <10%

**IF.chassis:**
- ✅ WASM sandbox operational
- ✅ Resource limits enforced
- ✅ SLO tracking functional
- ✅ Security audit passed

**CLI:**
- ✅ All subcommands working
- ✅ Cost visibility functional
- ✅ Witness queries working

**Documentation:**
- ✅ All component docs complete
- ✅ Migration guide ready
- ✅ Runbook complete

**Coordination:**
- ✅ No sessions timed out
- ✅ Total cost within $360-450
- ✅ Wall-clock time <8 hours

---

**Next Steps:** Each session should start polling this board every 30 seconds, claim available tasks, and execute according to the implementation guides above.
