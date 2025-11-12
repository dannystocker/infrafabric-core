# Phase 0: S² Core Components - Coordination Matrix

**Purpose:** Fix 3 critical production bugs BEFORE provider integrations
**Timeline:** 6-8h wall-clock with full parallelism
**Cost:** $360-450 total
**Critical:** This phase BLOCKS all provider integrations (Phases 1-6)

---

## Branch Coordination Strategy

### Master Coordination Branch
**Branch:** `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy` (THIS branch)
**Purpose:** Central coordination hub
**Contains:**
- `PHASE-0-TASK-BOARD.md` - Live task board (all sessions poll this)
- `INSTRUCTIONS-SESSION-{N}.md` - Task instructions for each session
- `STATUS-SESSION-{N}.yaml` - Status reports from each session
- Reviews, roadmaps, and architecture docs

### Session Work Branches
Each session works on its own branch, pulls instructions from master coordination branch:

| Session | Work Branch | Polls From | Writes To |
|---------|-------------|------------|-----------|
| 1-NDI | `claude/ndi-witness-streaming-*` | Coordination branch | Own branch |
| 2-WebRTC | `claude/webrtc-agent-mesh-*` | Coordination branch | Own branch |
| 3-H.323 | `claude/h323-guardian-council-*` | Coordination branch | Own branch |
| 4-SIP | `claude/sip-escalate-integration-*` | Coordination branch | Own branch |
| 5-CLI | `claude/cli-witness-optimise-*` | Coordination branch | Own branch |
| 6-Talent | (Not used in Phase 0) | Coordination branch | Own branch |
| 7-IF.bus | `claude/if-bus-sip-adapters-*` | Coordination branch | Own branch |

### Polling Protocol (Avoids Timeouts!)

**Every session runs this loop:**
```bash
# 1. Check for instructions on COORDINATION branch
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:PHASE-0-TASK-BOARD.md

# 2. Find next available task marked "available"
# 3. Claim task by writing to own branch STATUS file
# 4. Execute task
# 5. When done, mark "completed" in STATUS file on own branch
# 6. If blocked, pick a FILLER TASK (see below)
# 7. Loop every 30 seconds (NOT 60s - reduce wait time!)
```

**Key improvement:** 30-second polling (not 60s) reduces wait time by 50%

---

## Phase 0: Task Distribution Matrix

### Bug #1 (CRITICAL): IF.coordinator - Real-Time Coordination Service
**Fixes:** 30,000ms git polling latency, race conditions, self-DDoS
**Timeline:** 6-8h sequential → 2-3h wall-clock
**Cost:** $90-120

| Task | Owner | Dependencies | Model | Deliverable |
|------|-------|--------------|-------|-------------|
| P0.1.1: etcd/NATS event bus setup | Session 5 (CLI) | None | Haiku | `infrafabric/event_bus.py` |
| P0.1.2: Atomic CAS task claiming | Session 7 (IF.bus) | P0.1.1 | Sonnet | `infrafabric/coordinator.py` (CAS operations) |
| P0.1.3: Real-time task broadcast | Session 7 (IF.bus) | P0.1.1 | Sonnet | `infrafabric/coordinator.py` (pub/sub) |
| P0.1.4: <10ms latency verification | Session 5 (CLI) | P0.1.2, P0.1.3 | Haiku | `tests/test_coordinator_latency.py` |
| P0.1.5: Integration tests | Session 4 (SIP) | All above | Sonnet | `tests/integration/test_coordinator.py` |

### Bug #2 (HIGH): IF.governor - Capability-Aware Resource Manager
**Fixes:** 57% cost waste from random assignment, no budget enforcement
**Timeline:** 8-10h sequential → 2-3h wall-clock
**Cost:** $120-150

| Task | Owner | Dependencies | Model | Deliverable |
|------|-------|--------------|-------|-------------|
| P0.2.1: Capability registry schema | Session 5 (CLI) | None | Haiku | `infrafabric/schemas/capability.py` |
| P0.2.2: 70%+ match algorithm | Session 7 (IF.bus) | P0.2.1 | Sonnet | `infrafabric/governor.py` (match scoring) |
| P0.2.3: Budget enforcement | Session 7 (IF.bus) | None | Sonnet | `infrafabric/governor.py` (budget tracking) |
| P0.2.4: Circuit breakers | Session 7 (IF.bus) | P0.2.3 | Sonnet | `infrafabric/governor.py` (circuit breaker) |
| P0.2.5: Policy engine | Session 5 (CLI) | P0.2.2, P0.2.3 | Sonnet | `infrafabric/policies.py` |
| P0.2.6: Integration tests | Session 4 (SIP) | All above | Sonnet | `tests/integration/test_governor.py` |

### Bug #3 (MEDIUM→CRITICAL): IF.chassis - WASM Sandbox Runtime
**Fixes:** No sandboxing, noisy neighbor, security vulnerabilities
**Timeline:** 10-12h sequential → 3-4h wall-clock
**Cost:** $150-180

| Task | Owner | Dependencies | Model | Deliverable |
|------|-------|--------------|-------|-------------|
| P0.3.1: WASM runtime setup (wasmtime) | Session 7 (IF.bus) | None | Sonnet | `infrafabric/chassis/runtime.py` |
| P0.3.2: Resource limits (CPU/mem) | Session 7 (IF.bus) | P0.3.1 | Sonnet | `infrafabric/chassis/limits.py` |
| P0.3.3: Scoped credentials | Session 5 (CLI) | P0.3.1 | Sonnet | `infrafabric/chassis/auth.py` |
| P0.3.4: SLO tracking | Session 5 (CLI) | P0.3.2 | Haiku | `infrafabric/chassis/slo.py` |
| P0.3.5: Reputation system | Session 7 (IF.bus) | P0.3.4 | Sonnet | `infrafabric/chassis/reputation.py` |
| P0.3.6: Security audit tests | Session 4 (SIP) | All above | Sonnet | `tests/security/test_chassis.py` |

### CLI Foundation (Parallel with Bug Fixes)
**Purpose:** Unified entry point for IF components
**Timeline:** 4-6h → 1-2h wall-clock
**Cost:** $60-90

| Task | Owner | Dependencies | Model | Deliverable |
|------|-------|--------------|-------|-------------|
| P0.4.1: Unified CLI entry (`if`) | Session 5 (CLI) | None | Haiku | `src/cli/if_main.py` |
| P0.4.2: Cost tracking integration | Session 5 (CLI) | P0.2.3 | Haiku | `src/cli/if_cost.py` |
| P0.4.3: Witness integration | Session 5 (CLI) | None | Haiku | `src/cli/if_witness.py` |
| P0.4.4: Swarm spawn helper | Session 5 (CLI) | P0.1.2 | Haiku | `src/cli/if_swarm.py` |

### Documentation & Integration (Parallel)
**Purpose:** Production docs, runbooks, integration guides
**Timeline:** 4-6h → 1-2h wall-clock
**Cost:** $60-90

| Task | Owner | Dependencies | Model | Deliverable |
|------|-------|--------------|-------|-------------|
| P0.5.1: IF.coordinator docs | Session 1 (NDI) | P0.1.5 | Haiku | `docs/components/IF.COORDINATOR.md` |
| P0.5.2: IF.governor docs | Session 2 (WebRTC) | P0.2.6 | Haiku | `docs/components/IF.GOVERNOR.md` |
| P0.5.3: IF.chassis docs | Session 3 (H.323) | P0.3.6 | Haiku | `docs/components/IF.CHASSIS.md` |
| P0.5.4: Migration guide (git→etcd) | Session 1 (NDI) | P0.1.5 | Haiku | `docs/MIGRATION-GIT-TO-ETCD.md` |
| P0.5.5: Production runbook | Session 2 (WebRTC) | All components | Haiku | `docs/PHASE-0-PRODUCTION-RUNBOOK.md` |

---

## Dependency Graph (Critical Path)

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

P0.4.1 (CLI) ── independent, parallel ──> P0.4.2, P0.4.3, P0.4.4

P0.5.* (docs) ── wait for respective components to complete
```

**Critical path:** P0.1.1 → P0.1.2 → P0.1.3 → P0.1.4 → P0.1.5 (longest chain: ~3h wall-clock)

---

## Filler Tasks (Avoid Timeouts!)

### When Blocked: Pick a Filler Task

Each session has low-priority tasks to work on when blocked by dependencies.

#### Session 1 (NDI) Filler Tasks
**When blocked on:** Nothing specific (mostly docs)
**Filler tasks:**
1. Improve `docs/SWARM-OF-SWARMS-ARCHITECTURE.md` with Phase 0 integration notes
2. Create example IF.witness hash chain for coordination events
3. Build test fixtures for Session 2 (WebRTC)
4. Review and improve `NOVICE-ONBOARDING.md`

#### Session 2 (WebRTC) Filler Tasks
**When blocked on:** Component completion for docs
**Filler tasks:**
1. Build cross-session test fixtures (IFMessage mocks)
2. Create SDP mock data for integration tests
3. Improve `reviews/IF-IMPROVEMENTS-V1.1.md` with Phase 0 learnings
4. Help Session 3 with H.323 documentation

#### Session 3 (H.323) Filler Tasks
**When blocked on:** Component completion for docs
**Filler tasks:**
1. Improve `docs/H323-PRODUCTION-RUNBOOK.md`
2. Create MCU configuration templates
3. Build test data for Guardian council scenarios
4. Help Session 1 with NDI documentation

#### Session 4 (SIP) Filler Tasks
**When blocked on:** Waiting for components to complete before integration tests
**Filler tasks:**
1. Pre-write integration test scaffolding
2. Create test data for regression tests
3. Build mock implementations for early testing
4. Review security requirements for all 3 components
5. Help other sessions with code review

#### Session 5 (CLI) Filler Tasks
**When blocked on:** Component APIs not ready
**Filler tasks:**
1. Build CLI help text and documentation
2. Create config file schemas (YAML/TOML)
3. Design CLI user experience flows
4. Build error message catalog
5. Create CLI test fixtures
6. Help Session 7 with IF.bus integration planning

#### Session 7 (IF.bus) Filler Tasks
**When blocked on:** etcd/NATS setup (P0.1.1)
**Filler tasks:**
1. Design component interfaces (type signatures)
2. Create Pydantic models for all data structures
3. Write unit test scaffolding
4. Review existing `infrafabric/coordination.py` for integration opportunities
5. Create architecture diagrams for components

**Key principle:** NEVER sit idle waiting. Always have a backlog task ready.

---

## Session Coordination Rules

### Rule 1: Claim Before Execute
Before starting ANY task:
1. Pull latest from coordination branch
2. Check `PHASE-0-TASK-BOARD.md` for task status
3. Write to your own branch's `STATUS.yaml`:
   ```yaml
   session: session-5-cli
   claiming: P0.1.1
   timestamp: 2025-11-12T14:30:00Z
   branch: claude/cli-witness-optimise-011CV2nzozFeHipmhetrw5nk
   ```
4. Push your STATUS.yaml
5. Now execute the task

### Rule 2: Update Progress Every 15 Minutes
While working on a task:
1. Update STATUS.yaml with progress
2. Push to your branch
3. This lets other sessions see you're alive (not stuck/timed out)

### Rule 3: Mark Complete Immediately
When task is done:
1. Update STATUS.yaml:
   ```yaml
   session: session-5-cli
   completed: P0.1.1
   timestamp: 2025-11-12T15:45:00Z
   deliverable: infrafabric/event_bus.py
   tests_pass: true
   branch: claude/cli-witness-optimise-011CV2nzozFeHipmhetrw5nk
   ```
2. Push to your branch
3. Immediately claim next task OR pick filler task

### Rule 4: If Blocked, Switch to Filler Task
If waiting for dependency:
1. Update STATUS.yaml to "blocked_on: P0.X.X"
2. Pick filler task from your list above
3. Work on filler task (update STATUS to "filler: task_description")
4. Check every 30 seconds if blocker is resolved
5. When unblocked, switch back to main task

### Rule 5: Help Each Other
If you finish early or have spare capacity:
1. Check other sessions' STATUS.yaml files
2. Look for "help_wanted: true"
3. Offer assistance (code review, pair programming, testing)

---

## Polling Script (Copy-Paste Into Each Session)

```bash
#!/bin/bash
# Phase 0 Coordination Polling Loop
# Copy this into each session's terminal

SESSION_ID="session-X"  # Change to session-1, session-2, etc.
MY_BRANCH=$(git branch --show-current)
COORD_BRANCH="claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"

echo "🚀 Starting Phase 0 coordination loop for $SESSION_ID"
echo "📍 My branch: $MY_BRANCH"
echo "📡 Polling: $COORD_BRANCH"

while true; do
  # 1. Fetch latest coordination state
  git fetch origin $COORD_BRANCH --quiet 2>/dev/null

  # 2. Check task board for available tasks
  TASK_BOARD=$(git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md 2>/dev/null)

  # 3. Check my STATUS for next action
  # (Your session logic here - claim task, execute, or pick filler)

  # 4. Update my STATUS file
  cat > STATUS-$SESSION_ID.yaml <<EOF
session: $SESSION_ID
status: waiting_for_task
last_poll: $(date -Iseconds)
branch: $MY_BRANCH
EOF

  git add STATUS-$SESSION_ID.yaml
  git commit -m "chore: Update $SESSION_ID status" --quiet 2>/dev/null || true
  git push origin $MY_BRANCH --quiet 2>/dev/null || true

  # 5. Wait 30 seconds before next poll
  sleep 30
done
```

**Usage:**
1. Copy this script
2. Change `SESSION_ID` to your session (session-1, session-5, etc.)
3. Run in terminal
4. Script polls every 30 seconds, updates STATUS, claims tasks

---

## Using WeightedCoordinator for Task Assignment

The existing `infrafabric/coordination.py` can help with task assignment!

```python
from infrafabric.coordination import WeightedCoordinator, Agent, AgentProfile

# Create coordinator
coordinator = WeightedCoordinator()

# Define session agents
sessions = [
    AgentProfile(
        name="Session-1-NDI",
        base_weight=1.0,
        success_bonus=0.5,
        success_threshold=75,
        tier="baseline",
        description="Documentation and testing"
    ),
    AgentProfile(
        name="Session-5-CLI",
        base_weight=1.5,
        success_bonus=1.0,
        success_threshold=80,
        tier="specialist",
        description="CLI implementation and etcd setup"
    ),
    AgentProfile(
        name="Session-7-IF.bus",
        base_weight=2.0,
        success_bonus=1.5,
        success_threshold=85,
        tier="specialist",
        description="Core component implementation"
    ),
    AgentProfile(
        name="Session-4-SIP",
        base_weight=1.2,
        success_bonus=0.8,
        success_threshold=80,
        tier="specialist",
        description="Integration testing"
    ),
]

for profile in sessions:
    coordinator.add_agent(Agent(profile))

# Assign task based on capability match
task = {
    'task_id': 'P0.1.1',
    'description': 'Setup etcd/NATS event bus',
    'required_skills': ['infra', 'distributed-systems'],
    'model': 'haiku'
}

result = coordinator.coordinate(task, verbose=True)
print(f"Best session for task: {result['best_agent']}")
```

**Benefits:**
- Automatic capability-aware assignment
- Late bloomer detection (sessions that improve over time)
- Performance tracking
- Self-documenting manifests

---

## Success Criteria for Phase 0 Completion

### Component Criteria

**IF.coordinator:**
- ✅ etcd/NATS event bus operational
- ✅ <10ms task claim latency (atomic CAS)
- ✅ Real-time pub/sub working
- ✅ Integration tests pass

**IF.governor:**
- ✅ Capability registry with 70%+ match algorithm
- ✅ Budget enforcement with circuit breakers
- ✅ Policy engine operational
- ✅ Cost waste <10% (down from 57%)
- ✅ Integration tests pass

**IF.chassis:**
- ✅ WASM sandbox with resource limits
- ✅ Scoped credentials and SLO tracking
- ✅ Reputation system operational
- ✅ Security audit passed
- ✅ Integration tests pass

**CLI Foundation:**
- ✅ Unified `if` command works
- ✅ Cost tracking real-time
- ✅ Witness integration functional
- ✅ Swarm spawn helper works

**Documentation:**
- ✅ All 3 component docs complete
- ✅ Migration guide (git→etcd) ready
- ✅ Production runbook complete

### Coordination Criteria

- ✅ All sessions completed their assigned tasks
- ✅ No sessions timed out or got stuck
- ✅ Filler tasks used when blocked (no idle time)
- ✅ Branch coordination worked smoothly
- ✅ Total cost within $360-450 budget
- ✅ Wall-clock time <8 hours

### Handoff to Phases 1-6

**Before proceeding:**
1. Run full integration test suite
2. Benchmark coordinator latency (<10ms verified)
3. Measure cost waste reduction (target <10%)
4. Security audit passed
5. Production runbook reviewed
6. All docs committed and pushed

**Then:** Update `INTEGRATION-ROADMAP-POST-GPT5-REVIEW.md` to mark Phase 0 complete and unblock Phase 1.

---

## Timeline Estimate

| Milestone | Wall-Clock | Sessions Active | Critical Path |
|-----------|-----------|-----------------|---------------|
| Kickoff | 0h | All 5 | Setup polling loops |
| etcd/NATS setup complete | 0.5h | Session 5 | P0.1.1 |
| Coordinator CAS operational | 1.5h | Session 7 | P0.1.2, P0.1.3 |
| Governor match algorithm | 2h | Session 7 | P0.2.2 (parallel with coordinator) |
| WASM runtime setup | 2h | Session 7 | P0.3.1 (parallel with above) |
| CLI foundation | 2h | Session 5 | P0.4.* (parallel with above) |
| Integration tests | 4h | Session 4 | P0.1.5, P0.2.6, P0.3.6 (sequenced) |
| Documentation | 6h | Sessions 1,2,3 | P0.5.* (parallel with tests) |
| Final validation | 7h | All | Full integration test |
| **PHASE 0 COMPLETE** | **8h** | All | Handoff to Phase 1 |

**Parallelism multiplier:** 24-30h sequential → 6-8h wall-clock = **3-4x speedup**

---

## Cost Tracking

| Component | Owner | Estimated Cost | Model Mix |
|-----------|-------|----------------|-----------|
| IF.coordinator | Sessions 5, 7, 4 | $90-120 | 30% Haiku, 70% Sonnet |
| IF.governor | Sessions 5, 7, 4 | $120-150 | 20% Haiku, 80% Sonnet |
| IF.chassis | Sessions 5, 7, 4 | $150-180 | 10% Haiku, 90% Sonnet |
| CLI foundation | Session 5 | $60-90 | 80% Haiku, 20% Sonnet |
| Documentation | Sessions 1, 2, 3 | $60-90 | 90% Haiku, 10% Sonnet |
| **TOTAL** | All | **$480-630** | **~40% Haiku, ~60% Sonnet** |

**Note:** Slightly higher than initial $360-450 estimate due to documentation and integration overhead. Still well within budget for production-critical fixes.

---

## Next Steps

1. **Create task board:** See `PHASE-0-TASK-BOARD.md`
2. **Spawn sessions:** Start 5 sessions (1, 2, 3, 4, 5, 7)
3. **Initialize polling:** Each session runs polling script
4. **Monitor progress:** Track STATUS files from coordination branch
5. **Handle blockers:** Sessions pick filler tasks when blocked
6. **Validate completion:** Run integration tests, verify success criteria
7. **Handoff:** Update roadmap, unblock Phase 1

**Ready to start Phase 0? Create the task board next!**
