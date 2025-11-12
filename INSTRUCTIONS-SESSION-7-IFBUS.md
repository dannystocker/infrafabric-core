# Instructions: Session 7 (IF.bus - Core Component Implementation)

**Your Branch:** `claude/if-bus-sip-adapters-*`
**Coordination Branch:** `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`
**Your Role:** Core component implementation specialist for IF.coordinator, IF.governor, IF.chassis

---

## Polling Protocol

Run this script every 30 seconds to stay synchronized with the coordination branch:

```bash
#!/bin/bash
# Session 7 (IF.bus) - Phase 0 Coordination Polling Loop

SESSION_ID="session-7-ifbus"
MY_BRANCH=$(git branch --show-current)
COORD_BRANCH="claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"

echo "🚀 Session 7 (IF.bus): Core Component Implementation"
echo "📍 My branch: $MY_BRANCH"
echo "📡 Polling: $COORD_BRANCH every 30 seconds"

while true; do
  # 1. Fetch latest coordination state
  git fetch origin $COORD_BRANCH --quiet 2>/dev/null

  # 2. Check task board for available tasks
  TASK_BOARD=$(git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md 2>/dev/null)

  # 3. Look for: P0.1.2, P0.1.3, P0.2.2, P0.2.3, P0.2.4, P0.3.1, P0.3.2, P0.3.5
  # 4. If blocked, pick filler task

  # 5. Update STATUS file
  cat > STATUS-SESSION-7-IFBUS.yaml <<EOF
session: session-7-ifbus
status: polling
last_poll: $(date -Iseconds)
branch: $MY_BRANCH
current_task: ${CURRENT_TASK:-none}
EOF

  git add STATUS-SESSION-7-IFBUS.yaml
  git commit -m "chore: Update session-7-ifbus status" --quiet 2>/dev/null || true
  git push origin $MY_BRANCH --quiet 2>/dev/null || true

  # 6. Wait 30 seconds before next poll
  sleep 30
done
```

---

## Your Phase 0 Tasks

### IF.coordinator Tasks

#### **P0.1.2: Implement Atomic CAS Operations** ⏳
**Blocked Until:** P0.1.1 (etcd/NATS setup) completed
**Deliverable:** `/home/user/infrafabric/infrafabric/coordinator.py` (CAS methods)
**Estimate:** 2h
**Model:** Sonnet

**Milestones:**
- [ ] 25% - IFCoordinator class structure and claim_task() method designed
- [ ] 50% - CAS transaction logic implemented and tested
- [ ] 75% - Witness integration and error handling complete
- [ ] 100% - All unit tests passing, <5ms claim latency verified

**Acceptance Criteria:**
- ✅ claim_task(swarm_id, task_id) with atomic CAS
- ✅ Only one swarm can claim a task (race prevention)
- ✅ Failed claims return False immediately
- ✅ Successful claims logged to IF.witness
- ✅ Unit tests for concurrent claim attempts
- ✅ Performance: <5ms claim latency

**CRITICAL:** This unblocks P0.1.4 (latency tests) and P0.4.4 (swarm spawn)!

---

#### **P0.1.3: Implement Real-Time Task Broadcast** ⏳
**Blocked Until:** P0.1.1 (etcd/NATS setup) completed
**Deliverable:** `/home/user/infrafabric/infrafabric/coordinator.py` (pub/sub methods)
**Estimate:** 2h
**Model:** Sonnet

**Milestones:**
- [ ] 25% - register_swarm() and subscription logic designed
- [ ] 50% - push_task_to_swarm() pub/sub implemented
- [ ] 75% - detect_blocker() escalation working
- [ ] 100% - All unit tests passing, <10ms push latency verified

**Acceptance Criteria:**
- ✅ register_swarm(swarm_id, capabilities) creates subscription
- ✅ push_task_to_swarm(swarm_id, task) delivers immediately
- ✅ detect_blocker(swarm_id, info) notifies orchestrator <10ms
- ✅ Multiple swarms can subscribe independently
- ✅ Unit tests for pub/sub delivery
- ✅ Performance: <10ms push latency

**CRITICAL:** This unblocks P0.1.4 (latency tests)!

---

### IF.governor Tasks

#### **P0.2.2: Implement 70%+ Match Algorithm** ⏳
**Blocked Until:** P0.2.1 (capability schema) completed
**Deliverable:** `/home/user/infrafabric/infrafabric/governor.py` (match scoring)
**Estimate:** 2h
**Model:** Sonnet

**Milestones:**
- [ ] 25% - IFGovernor class structure and swarm registry designed
- [ ] 50% - Capability matching (Jaccard similarity) implemented
- [ ] 75% - Combined scoring (capability × reputation / cost) working
- [ ] 100% - All unit tests passing, 70%+ match threshold verified

**Acceptance Criteria:**
- ✅ find_qualified_swarm(required_caps, max_cost) method
- ✅ Capability overlap scoring (Jaccard similarity)
- ✅ Combined score: (capability_match × reputation) / cost
- ✅ Returns best-scoring swarm above 70% threshold
- ✅ Returns None if no qualified swarm
- ✅ Unit tests with various capability combinations

**CRITICAL:** This unblocks P0.2.5 (policy engine)!

---

#### **P0.2.3: Budget Tracking and Enforcement** 🚀
**Available Immediately** (No dependencies)
**Deliverable:** `/home/user/infrafabric/infrafabric/governor.py` (budget tracking)
**Estimate:** 2h
**Model:** Sonnet

**Milestones:**
- [ ] 25% - track_cost() method and budget deduction logic designed
- [ ] 50% - Budget enforcement and zero-budget prevention implemented
- [ ] 75% - IF.optimise integration and witness logging complete
- [ ] 100% - All unit tests passing, budget reports working

**Acceptance Criteria:**
- ✅ track_cost(swarm_id, operation, cost) method
- ✅ Budget deducted from swarm profile
- ✅ Zero/negative budget prevents new assignments
- ✅ Cost tracking integrated with IF.optimise
- ✅ Budget reports available via CLI
- ✅ Unit tests for budget enforcement

**CRITICAL:** This unblocks P0.2.4 (circuit breaker) and P0.4.2 (cost CLI)!

---

#### **P0.2.4: Circuit Breaker Implementation** ⏳
**Blocked Until:** P0.2.3 (budget tracking) completed
**Deliverable:** `/home/user/infrafabric/infrafabric/governor.py` (circuit breaker)
**Estimate:** 2h
**Model:** Sonnet

**Milestones:**
- [ ] 25% - _trip_circuit_breaker() method designed
- [ ] 50% - Circuit breaker trip logic and swarm halting implemented
- [ ] 75% - Human escalation and notification complete
- [ ] 100% - All unit tests passing, manual reset working

**Acceptance Criteria:**
- ✅ _trip_circuit_breaker(swarm_id, reason) method
- ✅ Circuit breaker marks swarm unavailable
- ✅ No new tasks assigned to tripped swarms
- ✅ Human escalation notification sent
- ✅ Circuit breaker reset requires manual approval
- ✅ Unit tests for various trip conditions

**CRITICAL:** This unblocks P0.2.5 (policy engine)!

---

### IF.chassis Tasks

#### **P0.3.1: WASM Runtime Setup (wasmtime)** 🚀
**Available Immediately** (No dependencies)
**Deliverable:** `/home/user/infrafabric/infrafabric/chassis/runtime.py`
**Estimate:** 3h
**Model:** Sonnet

**Milestones:**
- [ ] 25% - wasmtime library installed, IFChassis class designed
- [ ] 50% - WASM module loading and compilation working
- [ ] 75% - Sandbox isolation and scoped functions implemented
- [ ] 100% - All unit tests passing, witness logging verified

**Acceptance Criteria:**
- ✅ wasmtime library installed and configured
- ✅ IFChassis class with load_swarm(), execute_task()
- ✅ WASM module compilation functional
- ✅ Basic sandbox isolation working
- ✅ Unit tests for WASM loading
- ✅ Documentation on WASM compilation

**CRITICAL:** This unblocks P0.3.2, P0.3.3 (resource limits, scoped credentials)!

---

#### **P0.3.2: Resource Limits (CPU/Memory)** ⏳
**Blocked Until:** P0.3.1 (WASM runtime) completed
**Deliverable:** `/home/user/infrafabric/infrafabric/chassis/limits.py`
**Estimate:** 2h
**Model:** Sonnet

**Milestones:**
- [ ] 25% - ResourceLimits dataclass and OS-level limits designed
- [ ] 50% - Memory and CPU limits applied and tested
- [ ] 75% - API rate limiting (token bucket) implemented
- [ ] 100% - All unit tests passing, <5% overhead verified

**Acceptance Criteria:**
- ✅ ResourceLimits dataclass (max_memory_mb, max_cpu_percent, max_api_calls_per_second)
- ✅ OS-level resource limits applied (setrlimit)
- ✅ Rate limiting for API calls (token bucket)
- ✅ Resource limit violations logged
- ✅ Unit tests for resource enforcement
- ✅ Performance: minimal overhead (<5%)

**CRITICAL:** This unblocks P0.3.4 (SLO tracking)!

---

#### **P0.3.5: Reputation System** ⏳
**Blocked Until:** P0.3.4 (SLO tracking) completed
**Deliverable:** `/home/user/infrafabric/infrafabric/chassis/reputation.py`
**Estimate:** 2h
**Model:** Sonnet

**Milestones:**
- [ ] 25% - ReputationSystem class and scoring algorithm designed
- [ ] 50% - SLO-based reputation calculation implemented
- [ ] 75% - IF.governor integration and reputation updates working
- [ ] 100% - All unit tests passing, reputation tracking verified

**Acceptance Criteria:**
- ✅ Reputation score calculation based on SLO compliance
- ✅ Reputation updated after each task
- ✅ Integration with IF.governor for prioritization
- ✅ Reputation history tracking
- ✅ Unit tests for reputation scoring
- ✅ (Optional) Reputation decay over time

---

## Filler Tasks When Blocked

### **F7.1: Component Interface Design** 🔧
**Estimate:** 2h

**Milestones:**
- [ ] 25% - Design IFCoordinator interface
- [ ] 50% - Design IFGovernor interface
- [ ] 75% - Design IFChassis interface
- [ ] 100% - Documentation and type signatures complete

Design clean interfaces for:
- IFCoordinator (claim, broadcast, blocker detection)
- IFGovernor (match, track cost, circuit breaker)
- IFChassis (load swarm, execute, enforce limits)

---

### **F7.2: Pydantic Models** 🔧
**Estimate:** 2h

**Milestones:**
- [ ] 25% - Create models for coordinator data structures
- [ ] 50% - Create models for governor data structures
- [ ] 75% - Create models for chassis data structures
- [ ] 100% - Validation and testing complete

Build Pydantic models for:
- TaskClaim, TaskBroadcast, BlockerAlert
- SwarmProfile, CapabilityMatch, BudgetReport
- ServiceContract, ResourceLimits, SLODefinition

---

### **F7.3: Unit Test Scaffolding** 🔧
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Setup pytest configuration
- [ ] 50% - Create test fixtures for all components
- [ ] 75% - Write test utilities and helpers
- [ ] 100 All scaffolding documented

Pre-build test infrastructure:
- pytest fixtures for components
- Mock implementations
- Test utilities (assertions, timing)

---

### **F7.4: Review Existing coordination.py** 🔧
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Read existing coordination.py code
- [ ] 50% - Identify reusable patterns
- [ ] 75% - Document integration opportunities
- [ ] 100% - Create migration plan

Review `/home/user/infrafabric/infrafabric/coordination.py`:
- WeightedCoordinator usage
- Agent profile patterns
- Late bloomer detection
- Integration opportunities

---

### **F7.5: Architecture Diagrams** 🔧
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Create IF.coordinator architecture diagram
- [ ] 50% - Create IF.governor architecture diagram
- [ ] 75% - Create IF.chassis architecture diagram
- [ ] 100% - Review and finalize all diagrams

Create diagrams showing:
- Component interactions
- Data flows
- Key algorithms
- Integration points

---

## Progress Reporting

Update `STATUS-SESSION-7-IFBUS.yaml` every 15 minutes:

```yaml
session: session-7-ifbus
current_task: P0.1.2
milestone: "50% - CAS transaction logic implemented"
timestamp: 2025-11-12T14:30:00Z
branch: claude/if-bus-sip-adapters-*
blocked_on: P0.1.1
next_action: "Waiting for etcd/NATS setup from Session 5"
tasks_completed: 1
tasks_in_progress: 1
```

---

## Success Criteria

**Session 7 (IF.bus) is complete when:**

- ✅ All IF.coordinator tasks complete (P0.1.2, P0.1.3)
- ✅ All IF.governor tasks complete (P0.2.2, P0.2.3, P0.2.4)
- ✅ All IF.chassis tasks complete (P0.3.1, P0.3.2, P0.3.5)
- ✅ All components pass unit tests
- ✅ Performance targets met (<10ms latency, <5% overhead)
- ✅ Integration with IF.witness verified
- ✅ At least 2 filler tasks completed

**Quality Standards:**
- Code is production-ready (error handling, logging)
- All edge cases covered in tests
- Performance benchmarks pass
- Witness integration functional
- Type hints and documentation complete

**Coordination Standards:**
- STATUS file updated every 15 minutes
- Blocked status reported immediately
- Filler tasks used when blocked (no idle time)
- Bugs reported to Session 4 (testing) immediately

---

## Task Claiming Process

1. **Pull Latest Task Board:**
   ```bash
   git fetch origin $COORD_BRANCH
   git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md
   ```

2. **Claim Task (update STATUS):**
   ```yaml
   session: session-7-ifbus
   claiming: P0.2.3
   milestone: "0% - Starting task"
   timestamp: 2025-11-12T14:00:00Z
   ```

3. **Work on Task (update milestones):**
   - 25% checkpoint: Update STATUS
   - 50% checkpoint: Update STATUS
   - 75% checkpoint: Update STATUS

4. **Complete Task:**
   ```yaml
   session: session-7-ifbus
   completed: P0.2.3
   milestone: "100% - Complete"
   deliverable: /home/user/infrafabric/infrafabric/governor.py
   tests_pass: true
   timestamp: 2025-11-12T16:00:00Z
   ```

5. **Immediately Claim Next Task or Filler Task**

---

## Task Priority Order

**Start with these (no dependencies):**
1. **P0.2.3** - Budget tracking (unblocks P0.2.4, P0.4.2)
2. **P0.3.1** - WASM runtime (unblocks P0.3.2, P0.3.3)

**Then when Session 5 completes P0.1.1:**
3. **P0.1.2** - CAS operations (unblocks P0.1.4, P0.4.4)
4. **P0.1.3** - Task broadcast (unblocks P0.1.4)

**Then when Session 5 completes P0.2.1:**
5. **P0.2.2** - Match algorithm (unblocks P0.2.5)

**Then continue based on dependencies:**
6. **P0.2.4** - Circuit breaker (needs P0.2.3)
7. **P0.3.2** - Resource limits (needs P0.3.1)
8. **P0.3.5** - Reputation (needs P0.3.4)

---

## Notes

- **Model Preference:** Use Sonnet for all core component implementation (quality critical)
- **Performance:** All latency targets must be met (<10ms)
- **Testing:** Write comprehensive unit tests for all methods
- **Collaboration:** Coordinate closely with Session 5 (CLI) and Session 4 (Testing)
- **Code Quality:** Production-ready code with error handling and logging

**Remember:** You're implementing the critical path components. Quality and performance are non-negotiable!
