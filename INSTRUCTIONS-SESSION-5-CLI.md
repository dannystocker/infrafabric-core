# Instructions: Session 5 (CLI - CLI Foundation & Infrastructure)

**Your Branch:** `claude/cli-witness-optimise-*`
**Coordination Branch:** `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`
**Your Role:** CLI implementation specialist and infrastructure setup

---

## Polling Protocol

Run this script every 30 seconds to stay synchronized with the coordination branch:

```bash
#!/bin/bash
# Session 5 (CLI) - Phase 0 Coordination Polling Loop

SESSION_ID="session-5-cli"
MY_BRANCH=$(git branch --show-current)
COORD_BRANCH="claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"

echo "🚀 Session 5 (CLI): CLI Foundation & Infrastructure"
echo "📍 My branch: $MY_BRANCH"
echo "📡 Polling: $COORD_BRANCH every 30 seconds"

while true; do
  # 1. Fetch latest coordination state
  git fetch origin $COORD_BRANCH --quiet 2>/dev/null

  # 2. Check task board for available tasks
  TASK_BOARD=$(git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md 2>/dev/null)

  # 3. Look for: P0.1.1, P0.1.4, P0.2.1, P0.2.5, P0.3.3, P0.3.4, P0.4.*
  # 4. If blocked, pick filler task

  # 5. Update STATUS file
  cat > STATUS-SESSION-5-CLI.yaml <<EOF
session: session-5-cli
status: polling
last_poll: $(date -Iseconds)
branch: $MY_BRANCH
current_task: ${CURRENT_TASK:-none}
EOF

  git add STATUS-SESSION-5-CLI.yaml
  git commit -m "chore: Update session-5-cli status" --quiet 2>/dev/null || true
  git push origin $MY_BRANCH --quiet 2>/dev/null || true

  # 6. Wait 30 seconds before next poll
  sleep 30
done
```

---

## Your Phase 0 Tasks

### Infrastructure Tasks

#### **P0.1.1: Setup etcd/NATS Event Bus** 🚀
**Available Immediately** (No dependencies)
**Deliverable:** `/home/user/infrafabric/infrafabric/event_bus.py`
**Estimate:** 1h
**Model:** Haiku

**Milestones:**
- [ ] 25% - Library installed, EventBus class designed
- [ ] 50% - Connect/disconnect and basic put/get working
- [ ] 75% - Watch functionality and health checks implemented
- [ ] 100% - All unit tests passing, graceful reconnection verified

**Acceptance Criteria:**
- ✅ etcd or NATS client library installed
- ✅ EventBus class with connect(), disconnect(), put(), get(), watch()
- ✅ Connection health check functional
- ✅ Unit tests for connection handling
- ✅ Environment-based configuration
- ✅ Graceful reconnection on connection loss

**CRITICAL:** This unblocks Session 7 tasks P0.1.2 and P0.1.3!

---

#### **P0.1.4: Latency Verification (<10ms)** ⏳
**Blocked Until:** P0.1.2, P0.1.3 completed
**Deliverable:** `/home/user/infrafabric/tests/test_coordinator_latency.py`
**Estimate:** 1h
**Model:** Haiku

**Milestones:**
- [ ] 25% - Benchmark framework setup
- [ ] 50% - claim_task() latency tests passing
- [ ] 75% - push_task() latency tests passing
- [ ] 100% - Load tests passing, CI integration complete

**Acceptance Criteria:**
- ✅ p95 latency <10ms for claim_task()
- ✅ p95 latency <10ms for push_task_to_swarm()
- ✅ p99 latency <15ms
- ✅ Load test: 100 operations/second sustained
- ✅ Performance regression tests in CI

---

### Governor Tasks

#### **P0.2.1: Create Capability Registry Schema** 🚀
**Available Immediately** (No dependencies)
**Deliverable:** `/home/user/infrafabric/infrafabric/schemas/capability.py`
**Estimate:** 1h
**Model:** Haiku

**Milestones:**
- [ ] 25% - Capability enum with 20+ types defined
- [ ] 50% - SwarmProfile and ResourcePolicy dataclasses complete
- [ ] 75% - JSON schema and validation logic implemented
- [ ] 100% - All unit tests passing

**Acceptance Criteria:**
- ✅ Capability enum with 20+ capability types
- ✅ SwarmProfile dataclass (capabilities, cost, reputation)
- ✅ ResourcePolicy dataclass (limits, thresholds)
- ✅ JSON schema validation
- ✅ Unit tests for schema validation

**CRITICAL:** This unblocks Session 7 task P0.2.2!

---

#### **P0.2.5: Policy Engine** ⏳
**Blocked Until:** P0.2.2, P0.2.3 completed
**Deliverable:** `/home/user/infrafabric/infrafabric/policies.py`
**Estimate:** 2h
**Model:** Sonnet

**Milestones:**
- [ ] 25% - YAML policy loading implemented
- [ ] 50% - Policy validation and enforcement logic complete
- [ ] 75% - request_help_for_blocker() with capability matching working
- [ ] 100% - All unit tests passing, integration verified

**Acceptance Criteria:**
- ✅ Load policies from YAML configuration
- ✅ request_help_for_blocker() uses capability matching
- ✅ Respects max_swarms_per_task limit
- ✅ Enforces budget constraints
- ✅ Policy violation logging
- ✅ Unit tests for policy enforcement

---

### Chassis Tasks

#### **P0.3.3: Scoped Credentials** ⏳
**Blocked Until:** P0.3.1 completed
**Deliverable:** `/home/user/infrafabric/infrafabric/chassis/auth.py`
**Estimate:** 2h
**Model:** Sonnet

**Milestones:**
- [ ] 25% - ScopedCredentials dataclass and CredentialManager designed
- [ ] 50% - Credential generation and expiration logic working
- [ ] 75% - Endpoint whitelist and validation implemented
- [ ] 100% - All unit tests passing, vault integration complete

**Acceptance Criteria:**
- ✅ ScopedCredentials with TTL and endpoint whitelist
- ✅ Credentials expire after TTL
- ✅ Allowed endpoints whitelist enforced
- ✅ Credential injection into WASM sandbox
- ✅ Unit tests for expiration
- ✅ Integration with secrets vault

---

#### **P0.3.4: SLO Tracking** ⏳
**Blocked Until:** P0.3.2 completed
**Deliverable:** `/home/user/infrafabric/infrafabric/chassis/slo.py`
**Estimate:** 2h
**Model:** Haiku

**Milestones:**
- [ ] 25% - ServiceLevelObjective and PerformanceMetric dataclasses defined
- [ ] 50% - Metric recording and storage working
- [ ] 75% - SLO compliance calculation implemented
- [ ] 100% - All unit tests passing, dashboard integration ready

**Acceptance Criteria:**
- ✅ ServiceLevelObjective dataclass (p99 latency, success rate, availability)
- ✅ Performance metrics collection (latency, success/failure)
- ✅ SLO compliance calculation
- ✅ SLO violations logged
- ✅ Unit tests for SLO tracking
- ✅ Dashboard integration ready

---

### CLI Tasks

#### **P0.4.1: Unified CLI Entry (`if` command)** 🚀
**Available Immediately** (No dependencies)
**Deliverable:** `/home/user/infrafabric/src/cli/if_main.py`
**Estimate:** 2h
**Model:** Haiku

**Milestones:**
- [ ] 25% - CLI structure and subcommands defined
- [ ] 50% - Coordinator and governor subcommands implemented
- [ ] 75% - Chassis, witness, optimise subcommands implemented
- [ ] 100% - All tests passing, installation working

**Acceptance Criteria:**
- ✅ `if` command registered (click or argparse)
- ✅ Subcommands: coordinator, governor, chassis, witness, optimise
- ✅ `--why --trace --mode=falsify` flags on all commands
- ✅ Help text and documentation
- ✅ Unit tests for CLI parsing
- ✅ Installation via pip/setuptools

---

#### **P0.4.2: Cost Tracking Integration** ⏳
**Blocked Until:** P0.2.3 completed
**Deliverable:** `/home/user/infrafabric/src/cli/if_cost.py`
**Estimate:** 1h
**Model:** Haiku

**Milestones:**
- [ ] 25% - Cost report command implemented
- [ ] 50% - Budget status command implemented
- [ ] 75% - Cost history and CSV export implemented
- [ ] 100% - All tests passing, IF.optimise integration verified

**Acceptance Criteria:**
- ✅ `if cost report` shows cost breakdown
- ✅ `if cost budget` shows remaining budgets
- ✅ `if cost history` shows cost over time
- ✅ Integration with IF.optimise
- ✅ CSV export functionality
- ✅ Unit tests for cost commands

---

#### **P0.4.3: Witness Integration** 🚀
**Available Immediately** (No dependencies)
**Deliverable:** `/home/user/infrafabric/src/cli/if_witness.py`
**Estimate:** 1h
**Model:** Haiku

**Milestones:**
- [ ] 25% - Witness query command implemented
- [ ] 50% - Trace command implemented
- [ ] 75% - Verify command implemented
- [ ] 100% - All tests passing, JSON output working

**Acceptance Criteria:**
- ✅ `if witness query` searches witness log
- ✅ `if witness trace <token>` shows full chain
- ✅ `if witness verify` checks hash chain integrity
- ✅ JSON output format
- ✅ Unit tests for witness commands

---

#### **P0.4.4: Swarm Spawn Helper** ⏳
**Blocked Until:** P0.1.2 completed
**Deliverable:** `/home/user/infrafabric/src/cli/if_swarm.py`
**Estimate:** 2h
**Model:** Haiku

**Milestones:**
- [ ] 25% - Swarm spawn command structure implemented
- [ ] 50% - Coordinator registration working
- [ ] 75% - Capability detection and budget assignment implemented
- [ ] 100% - All tests passing, full workflow verified

**Acceptance Criteria:**
- ✅ `if swarm spawn <swarm-id>` creates new swarm
- ✅ Automatic registration with IF.coordinator
- ✅ Capability detection from swarm code
- ✅ Budget assignment
- ✅ Unit tests for swarm spawning

---

## Filler Tasks When Blocked

### **F5.1: CLI Help Text** 🔧
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Document all coordinator commands
- [ ] 50% - Document all governor commands
- [ ] 75% - Document all chassis, witness, optimise commands
- [ ] 100% - Review and finalize help documentation

---

### **F5.2: Config File Schemas** 🔧
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Design YAML/TOML structure
- [ ] 50% - Create schemas for coordinator, governor, chassis
- [ ] 75% - Add validation and examples
- [ ] 100% - Documentation complete

---

### **F5.3: CLI UX Flows** 🔧
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Design onboarding flow
- [ ] 50% - Design common operation flows
- [ ] 75% - Design troubleshooting flows
- [ ] 100% - User testing and refinement

---

### **F5.4: Error Message Catalog** 🔧
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Catalog all error conditions
- [ ] 50% - Write user-friendly error messages
- [ ] 75% - Add remediation suggestions
- [ ] 100% - Integration and testing

---

### **F5.5: CLI Test Fixtures** 🔧
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Create test data for coordinator commands
- [ ] 50% - Create test data for governor commands
- [ ] 75% - Create test data for chassis commands
- [ ] 100% - All fixtures documented

---

### **F5.6: Help Session 7 with IF.bus Planning** 🔧
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Review Session 7 needs
- [ ] 50% - Provide architecture guidance
- [ ] 75% - Help with interface design
- [ ] 100% - Code review support

---

## Progress Reporting

Update `STATUS-SESSION-5-CLI.yaml` every 15 minutes:

```yaml
session: session-5-cli
current_task: P0.1.1
milestone: "50% - Basic put/get working"
timestamp: 2025-11-12T14:30:00Z
branch: claude/cli-witness-optimise-*
blocked_on: null
next_action: "Implementing watch functionality"
tasks_completed: 0
tasks_in_progress: 1
```

---

## Success Criteria

**Session 5 (CLI) is complete when:**

- ✅ All infrastructure tasks complete (P0.1.1, P0.1.4)
- ✅ All governor tasks complete (P0.2.1, P0.2.5)
- ✅ All chassis tasks complete (P0.3.3, P0.3.4)
- ✅ All CLI tasks complete (P0.4.1-P0.4.4)
- ✅ etcd/NATS latency <10ms verified
- ✅ CLI commands fully functional and tested
- ✅ At least 3 filler tasks completed

**Remember:** P0.1.1 is CRITICAL PATH - complete it first to unblock Session 7!
