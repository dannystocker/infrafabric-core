# CLI Integration Audit - Phase 0 Components
## Session 5 Documentation Review for CLI Integration Points

**Created by**: Session 5 (CLI)
**Purpose**: Identify CLI integration needs for Phase 0 (IF.coordinator, IF.governor, IF.chassis)
**Date**: 2025-11-12
**Status**: F5.22 Filler Task Deliverable

---

## Executive Summary

This audit reviews all InfraFabric documentation to identify CLI integration points for Phase 0 components. While comprehensive CLI integration exists for IF.witness and legacy sessions (NDI, WebRTC, H.323, SIP), **Phase 0 components lack CLI tooling**.

### Key Findings

**✅ Well-Documented CLI Integration:**
- IF.witness (6 commands: log, query, verify, trace, cost, export)
- IF.optimise (cost tracking, budget alerts)
- Legacy provider sessions (NDI, WebRTC, H.323, SIP)

**❌ Missing CLI Integration for Phase 0:**
- IF.coordinator (NO CLI commands for task management)
- IF.governor (NO CLI commands for capability matching, budget enforcement)
- IF.chassis (NO CLI commands for WASM sandbox management)

**Impact:** Phase 0 components are currently only accessible programmatically. Operators lack visibility and control over:
- Task claims and coordination status
- Budget enforcement and cost tracking
- WASM sandbox lifecycle and resource limits

---

## Current State Analysis

### Existing CLI Tools (Pre-Phase 0)

#### 1. IF.witness CLI ✅ COMPLETE

**File**: `src/cli/if_witness.py`
**Commands**: 6 total
- `if witness log` - Create provenance entry
- `if witness query` - Search with filters (NEW in P0.4.3)
- `if witness verify` - Verify hash chain
- `if witness trace` - Follow trace chain
- `if witness cost` - Cost breakdown
- `if witness export` - Export audit trail (JSON/CSV/PDF)

**Documentation**:
- docs/CLI-USER-GUIDE.md (35KB, 77 examples)
- docs/CLI-WITNESS-GUIDE.md (18KB)
- docs/CLI-WITNESS-INTEGRATION.md (11KB)
- docs/CLI-INTEGRATION-GUIDE.md (59KB, cross-session)

**Integration Status**: ✅ Excellent
- All 4 legacy sessions have witness integration examples
- Python examples for NDI, WebRTC, H.323, SIP
- Trace ID propagation documented
- Cost tracking integrated

#### 2. IF.optimise CLI ✅ COMPLETE

**File**: `src/cli/if_optimise.py`
**Commands**: Multiple cost management commands
- Budget tracking
- Spend alerts
- Cost analysis

**Integration Status**: ✅ Good
- Integrated with IF.witness cost tracking
- Per-component reporting

#### 3. Legacy Provider CLIs ✅ COMPLETE

**vMix**: `src/cli/vmix_commands.py` (27 commands)
**OBS**: `src/cli/obs_commands.py` (33 commands)
**Home Assistant**: `src/cli/ha_commands.py` (29 commands)

**Integration Status**: ✅ Excellent
- Full production control
- NDI, streaming, PTZ, automation
- 80 tests passing

---

## Phase 0 CLI Gaps

### 1. IF.coordinator CLI ❌ MISSING

**Component Status**: P0.1.1 ✅, P0.1.2 🟡, P0.1.3 🟡, P0.1.4 ⏳
**Current Interface**: Python API only (infrafabric/coordinator.py)

**Missing CLI Commands:**

```bash
# Task Management
if coordinator tasks list [--status pending|claimed|complete]
if coordinator tasks claim <task_id> --swarm <swarm_id>
if coordinator tasks release <task_id> --swarm <swarm_id>
if coordinator tasks status <task_id>
if coordinator tasks watch [--follow]

# Swarm Coordination
if coordinator swarms list [--active]
if coordinator swarms status <swarm_id>
if coordinator swarms tasks <swarm_id>

# Performance & Diagnostics
if coordinator stats [--json]
if coordinator latency benchmark [--iterations 100]
if coordinator health check

# Event Bus Management
if coordinator eventbus status
if coordinator eventbus watch <key_pattern>
```

**Use Cases Blocked by Missing CLI:**
1. **Operations**: Can't view task claims in real-time
2. **Debugging**: No visibility into CAS failures or race conditions
3. **Monitoring**: No latency metrics without code instrumentation
4. **Testing**: Can't manually claim/release tasks for integration tests

**Priority**: 🔴 HIGH (operators blind to coordination state)

**Recommended Implementation:**
- **File**: `src/cli/if_coordinator.py`
- **Estimate**: 2-3 hours
- **Tests**: 15-20 command tests
- **Dependencies**: P0.1.2 (CAS), P0.1.3 (pub/sub)

---

### 2. IF.governor CLI ❌ MISSING

**Component Status**: P0.2.1 ✅, P0.2.2 ✅, P0.2.3 ✅, P0.2.4 ✅, P0.2.5 ✅
**Current Interface**: Python API only (infrafabric/governor.py expected)

**Missing CLI Commands:**

```bash
# Capability Matching
if governor capabilities list
if governor capabilities match <task_id> [--threshold 0.7]
if governor capabilities swarm <swarm_id>

# Budget Management
if governor budget status [--swarm <swarm_id>]
if governor budget set --swarm <swarm_id> --limit <usd>
if governor budget history [--start-date YYYY-MM-DD]
if governor budget alerts list

# Circuit Breakers
if governor circuit status [--component <name>]
if governor circuit reset <component>
if governor circuit config <component> --threshold <n>

# Policy Engine
if governor policy list
if governor policy apply <policy_file.yaml>
if governor policy validate <policy_file.yaml>
if governor policy test --task <task_id> --swarm <swarm_id>

# Cost Optimization
if governor cost analyze [--group-by capability|swarm]
if governor cost waste report
if governor cost recommendations
```

**Use Cases Blocked by Missing CLI:**
1. **Operations**: Can't see budget enforcement in real-time
2. **Debugging**: No way to test capability matching manually
3. **Policy Management**: Can't apply/validate policies without code
4. **Cost Analysis**: No way to see 57% → <10% waste reduction impact

**Priority**: 🔴 HIGH (core value proposition invisible to operators)

**Recommended Implementation:**
- **File**: `src/cli/if_governor.py`
- **Estimate**: 3-4 hours
- **Tests**: 20-25 command tests
- **Dependencies**: P0.2.1-P0.2.5 (all complete)

---

### 3. IF.chassis CLI ❌ MISSING

**Component Status**: P0.3.1 ✅, P0.3.2 ✅, P0.3.3 🟡, P0.3.4 ⏳
**Current Interface**: Python API only (infrafabric/chassis.py expected)

**Missing CLI Commands:**

```bash
# WASM Sandbox Lifecycle
if chassis sandbox create --swarm <swarm_id> [--wasm <path>]
if chassis sandbox list [--status running|stopped]
if chassis sandbox start <sandbox_id>
if chassis sandbox stop <sandbox_id>
if chassis sandbox destroy <sandbox_id>
if chassis sandbox logs <sandbox_id> [--follow]

# Resource Management
if chassis resources limits <sandbox_id>
if chassis resources usage <sandbox_id> [--json]
if chassis resources set <sandbox_id> --cpu <percent> --memory <mb>

# Security & Credentials
if chassis credentials scope <sandbox_id> --allow <service>
if chassis credentials revoke <sandbox_id> <credential_id>
if chassis credentials audit <sandbox_id>

# SLO Tracking
if chassis slo status [--sandbox <sandbox_id>]
if chassis slo violations [--since 1h]
if chassis slo metrics <sandbox_id>

# Reputation & Audit
if chassis reputation score <swarm_id>
if chassis reputation history <swarm_id>
if chassis audit trail <sandbox_id> [--export json]
```

**Use Cases Blocked by Missing CLI:**
1. **Operations**: Can't inspect running sandboxes
2. **Security**: No way to audit credential scoping
3. **Performance**: Can't see resource usage in real-time
4. **SLO Monitoring**: No CLI access to SLO violations

**Priority**: 🟡 MEDIUM (less critical than coordinator/governor)

**Recommended Implementation:**
- **File**: `src/cli/if_chassis.py`
- **Estimate**: 2-3 hours
- **Tests**: 15-20 command tests
- **Dependencies**: P0.3.1, P0.3.2

---

## Documentation Gaps

### 1. Phase 0 CLI User Guide ❌ MISSING

**File**: `docs/CLI-PHASE-0-USER-GUIDE.md` (does not exist)

**Should Include:**
- Complete command reference for IF.coordinator, IF.governor, IF.chassis
- Workflow examples (e.g., "How to claim a task manually")
- Integration with IF.witness (trace IDs across all components)
- Troubleshooting common issues (CAS failures, budget exhaustion)
- Performance tuning tips (latency optimization)

**Estimate**: 1-2 hours
**Priority**: 🔴 HIGH (operators need usage guidance)

---

### 2. Phase 0 Integration Patterns ❌ MISSING

**File**: `docs/CLI-PHASE-0-INTEGRATION-PATTERNS.md` (does not exist)

**Should Include:**
- How to integrate coordinator, governor, chassis in pipelines
- CI/CD examples using Phase 0 CLI commands
- Monitoring and alerting setup
- Log aggregation patterns
- Grafana/Prometheus integration examples

**Estimate**: 1 hour
**Priority**: 🟡 MEDIUM

---

### 3. Unified CLI Entry Point Documentation ⚠️ INCOMPLETE

**Current State**: Multiple CLI entry points
- `if-witness` (installed)
- `if-optimise` (installed)
- `vmix` (installed)
- `obs` (installed)
- `ha` (installed)

**Missing**: Unified `if` command

```bash
# Current (fragmented)
if-witness log ...
if-optimise budget ...
vmix start-stream ...

# Desired (unified)
if witness log ...
if coordinator tasks list
if governor budget status
if chassis sandbox create ...
```

**Implementation**: P0.4.1 (blocked on P0.1.2)

**Documentation Needed**:
- Update CLI-USER-GUIDE.md with unified `if` command
- Migration guide from legacy commands
- Alias setup for backward compatibility

---

## Integration Point Analysis

### Cross-Component CLI Workflows

#### Workflow 1: Manual Task Claiming (Blocked)

**Current Problem**: No CLI access to coordinator

**Desired Workflow**:
```bash
# 1. List available tasks
if coordinator tasks list --status pending

# 2. Check if swarm has capability
if governor capabilities match task-rust-123 --swarm swarm-7

# 3. Claim task
if coordinator tasks claim task-rust-123 --swarm swarm-7

# 4. Watch witness log for execution
if witness query --trace-id task-rust-123 --follow

# 5. Check cost
if governor budget status --swarm swarm-7
```

**Blocked On**: IF.coordinator CLI, IF.governor CLI

---

#### Workflow 2: Budget Enforcement Debugging (Partially Blocked)

**Current Capability**:
```bash
# Can see cost in witness
if witness cost --component IF.swarm

# Can export audit trail
if witness export --format pdf
```

**Missing**:
```bash
# Can't see governor decisions
if governor budget status --swarm swarm-7

# Can't see circuit breaker state
if governor circuit status --component IF.swarm

# Can't see why task was rejected
if governor policy test --task task-123 --swarm swarm-7
```

**Blocked On**: IF.governor CLI

---

#### Workflow 3: WASM Sandbox Lifecycle (Blocked)

**Current Problem**: No visibility into chassis

**Desired Workflow**:
```bash
# 1. Create sandbox for swarm
if chassis sandbox create --swarm swarm-7 --wasm target/wasm32-wasi/release/swarm.wasm

# 2. Set resource limits
if chassis resources set sandbox-abc123 --cpu 25 --memory 512

# 3. Scope credentials
if chassis credentials scope sandbox-abc123 --allow github:read --allow s3:write

# 4. Monitor resource usage
if chassis resources usage sandbox-abc123 --follow

# 5. Check SLO violations
if chassis slo violations --sandbox sandbox-abc123

# 6. Witness audit
if witness query --component IF.chassis --trace-id sandbox-abc123
```

**Blocked On**: IF.chassis CLI

---

## Recommendations

### Immediate Actions (Phase 0 Completion)

1. **Implement IF.coordinator CLI** (Priority: HIGH)
   - Essential for operations visibility
   - Blocks P0.1.5 (integration tests benefit from CLI)
   - Estimate: 2-3 hours
   - File: `src/cli/if_coordinator.py`

2. **Implement IF.governor CLI** (Priority: HIGH)
   - Core value proposition (57% waste → <10%)
   - Demonstrates budget enforcement working
   - Estimate: 3-4 hours
   - File: `src/cli/if_governor.py`

3. **Create Phase 0 CLI User Guide** (Priority: HIGH)
   - Operators need documentation
   - Show off new capabilities
   - Estimate: 1-2 hours
   - File: `docs/CLI-PHASE-0-USER-GUIDE.md`

4. **Implement IF.chassis CLI** (Priority: MEDIUM)
   - Less critical than coordinator/governor
   - Still needed for WASM visibility
   - Estimate: 2-3 hours
   - File: `src/cli/if_chassis.py`

### Future Enhancements (Post-Phase 0)

5. **Unified `if` Command** (P0.4.1)
   - Better UX than multiple entry points
   - Requires coordinator CLI to exist first
   - Estimate: 2 hours
   - File: `src/cli/if_main.py`

6. **Phase 0 Integration Patterns Doc**
   - CI/CD examples
   - Monitoring setup
   - Estimate: 1 hour

7. **CLI Performance Benchmarks**
   - Ensure CLI overhead <10ms
   - Document best practices
   - Estimate: 1 hour

---

## Phase 0 CLI Command Matrix

### Proposed Command Structure

| Component | Commands | Status | Blocking |
|-----------|----------|--------|----------|
| **IF.coordinator** | 11 commands | ❌ Missing | P0.1.2, P0.1.3 |
| `tasks list` | Show pending/claimed tasks | ❌ | P0.1.2 |
| `tasks claim` | Atomically claim task | ❌ | P0.1.2 |
| `tasks release` | Release claimed task | ❌ | P0.1.2 |
| `tasks status` | Check task state | ❌ | P0.1.2 |
| `tasks watch` | Real-time task stream | ❌ | P0.1.3 |
| `swarms list` | Show active swarms | ❌ | P0.1.1 |
| `swarms status` | Swarm coordination state | ❌ | P0.1.1 |
| `stats` | Coordination metrics | ❌ | P0.1.2 |
| `latency benchmark` | Performance test | ❌ | P0.1.2 |
| `health check` | System health | ❌ | P0.1.1 |
| `eventbus status` | Event bus diagnostics | ❌ | P0.1.1 |
| **IF.governor** | 15 commands | ❌ Missing | None (all P0.2.x complete) |
| `capabilities list` | Show all capabilities | ❌ | P0.2.1 |
| `capabilities match` | Test capability matching | ❌ | P0.2.2 |
| `budget status` | Current budget state | ❌ | P0.2.3 |
| `budget set` | Update budget limits | ❌ | P0.2.3 |
| `budget history` | Historical spend | ❌ | P0.2.3 |
| `budget alerts` | Budget alert config | ❌ | P0.2.3 |
| `circuit status` | Circuit breaker state | ❌ | P0.2.4 |
| `circuit reset` | Reset circuit breaker | ❌ | P0.2.4 |
| `circuit config` | Configure thresholds | ❌ | P0.2.4 |
| `policy list` | Show active policies | ❌ | P0.2.5 |
| `policy apply` | Apply policy file | ❌ | P0.2.5 |
| `policy validate` | Validate policy syntax | ❌ | P0.2.5 |
| `policy test` | Test policy decision | ❌ | P0.2.5 |
| `cost analyze` | Cost breakdown | ❌ | P0.2.3 |
| `cost recommendations` | Optimization tips | ❌ | P0.2.2 |
| **IF.chassis** | 13 commands | ❌ Missing | P0.3.1, P0.3.2 |
| `sandbox create` | Create WASM sandbox | ❌ | P0.3.1 |
| `sandbox list` | List sandboxes | ❌ | P0.3.1 |
| `sandbox start/stop/destroy` | Lifecycle ops | ❌ | P0.3.1 |
| `sandbox logs` | View sandbox logs | ❌ | P0.3.1 |
| `resources limits` | Show resource limits | ❌ | P0.3.2 |
| `resources usage` | Real-time usage | ❌ | P0.3.2 |
| `resources set` | Configure limits | ❌ | P0.3.2 |
| `credentials scope/revoke/audit` | Security ops | ❌ | P0.3.3 |
| `slo status/violations/metrics` | SLO tracking | ❌ | P0.3.4 |
| `reputation score/history` | Reputation system | ❌ | P0.3.5 |
| `audit trail` | Security audit | ❌ | P0.3.6 |
| **IF.witness** | 6 commands | ✅ Complete | None |
| `log/query/verify/trace/cost/export` | All working | ✅ | - |

**Total New Commands Needed**: 39 commands across 3 components

---

## Integration Testing Strategy

### CLI Integration Tests (Currently Missing)

```python
# tests/integration/test_phase0_cli_integration.py

def test_end_to_end_task_workflow():
    """
    Test complete workflow:
    1. List tasks (coordinator)
    2. Check capability match (governor)
    3. Claim task (coordinator)
    4. Verify budget (governor)
    5. Create sandbox (chassis)
    6. Execute task
    7. Verify witness log
    """
    # List available tasks
    result = run_cli("if coordinator tasks list --status pending --format json")
    tasks = json.loads(result.stdout)
    task_id = tasks[0]['id']

    # Check if swarm can handle task
    result = run_cli(f"if governor capabilities match {task_id} --swarm swarm-test-1")
    assert result.returncode == 0
    assert "match_score: 0.85" in result.stdout

    # Claim task
    result = run_cli(f"if coordinator tasks claim {task_id} --swarm swarm-test-1")
    assert result.returncode == 0
    assert "Task claimed successfully" in result.stdout

    # Verify budget
    result = run_cli("if governor budget status --swarm swarm-test-1 --json")
    budget = json.loads(result.stdout)
    assert budget['remaining'] > 0

    # Create sandbox
    result = run_cli("if chassis sandbox create --swarm swarm-test-1")
    sandbox_id = extract_sandbox_id(result.stdout)

    # Verify witness logged everything
    result = run_cli(f"if witness query --trace-id {task_id} --json")
    events = json.loads(result.stdout)

    assert any(e['event'] == 'task_claimed' for e in events)
    assert any(e['event'] == 'sandbox_created' for e in events)
    assert any(e['component'] == 'IF.coordinator' for e in events)
    assert any(e['component'] == 'IF.chassis' for e in events)
```

**Estimate to Implement**: 2-3 hours
**Value**: Validates entire Phase 0 stack working together

---

## Cost-Benefit Analysis

### Development Investment

| Component | Hours | Priority | ROI |
|-----------|-------|----------|-----|
| IF.coordinator CLI | 2-3h | HIGH | ⭐⭐⭐⭐⭐ Essential |
| IF.governor CLI | 3-4h | HIGH | ⭐⭐⭐⭐⭐ Core value |
| IF.chassis CLI | 2-3h | MEDIUM | ⭐⭐⭐ Important |
| Phase 0 User Guide | 1-2h | HIGH | ⭐⭐⭐⭐ Docs critical |
| Integration Tests | 2-3h | MEDIUM | ⭐⭐⭐⭐ Quality |
| **Total** | **10-15h** | - | - |

### Value Delivered

**With CLI Integration:**
- ✅ Operators can see coordination state
- ✅ Budget enforcement visible in real-time
- ✅ WASM sandboxes inspectable
- ✅ Integration tests possible
- ✅ Demos show 57% → <10% waste reduction
- ✅ Production readiness verified

**Without CLI Integration:**
- ❌ Operators blind to Phase 0 components
- ❌ Budget enforcement "invisible magic"
- ❌ Hard to debug coordination issues
- ❌ Can't demonstrate value proposition
- ❌ Not production-ready

**Verdict**: 🔴 CRITICAL for Phase 0 completion

---

## Next Steps for Session 5

As Session 5 (CLI), I recommend:

1. **Claim IF.coordinator CLI task** once P0.1.2 complete
   - Wait for Session 7 to finish P0.1.2 (CAS operations)
   - Implement 11 coordinator commands
   - Write integration tests
   - Document in CLI-PHASE-0-USER-GUIDE.md

2. **Claim IF.governor CLI task** (can start now!)
   - All dependencies complete (P0.2.1-P0.2.5)
   - Implement 15 governor commands
   - Show off 57% → <10% waste reduction
   - Critical for demo value

3. **Create CLI-PHASE-0-USER-GUIDE.md**
   - While waiting for dependencies
   - Document planned command structure
   - Write examples even before implementation
   - Get user feedback early

4. **Implement IF.chassis CLI** once P0.3.3 complete
   - Less critical than coordinator/governor
   - Still valuable for WASM visibility

---

## Conclusion

**Current State**: Phase 0 components lack CLI integration, making them invisible to operators and hard to demonstrate.

**Gap Impact**: HIGH - Core value proposition (57% → <10% waste) not visible without IF.governor CLI.

**Recommendation**: Prioritize IF.governor CLI (can start now) and IF.coordinator CLI (once P0.1.2 complete).

**Timeline**: 10-15 hours to deliver all Phase 0 CLI integration (3 components + docs + tests).

**Outcome**: Production-ready Phase 0 with full operational visibility and demonstrable value.

---

**Document Status**: ✅ COMPLETE
**Created**: 2025-11-12 by Session 5 (CLI)
**Filler Task**: F5.22 - Review all session docs for CLI integration points
**Next Action**: Implement IF.governor CLI (all dependencies met)
