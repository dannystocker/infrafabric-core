# Phases 4-6 Coordinator Quick Guide

## Three Matrix Files (Choose Your Detail Level)

1. **PHASES-4-6-MATRIX-ULTRA-CONDENSED.txt** ← START HERE
   - 22 lines total
   - One-liner per session per phase
   - Dependencies, idle tasks, critical path at a glance

2. **PHASES-4-6-COORDINATION-MATRIX.txt** ← OPERATIONAL
   - 38 lines, expanded view
   - Task breakdown per session with model assignments
   - Clear BLOCKED/SUPPORT/IDLE annotations
   - Effort & cost per session

3. **PHASES-4-6-CROSS-SESSION-MATRIX.md** ← REFERENCE
   - 79 lines, markdown format
   - Full task details with file paths
   - Success criteria per phase
   - Wall-clock vs effort analysis

---

## At a Glance

### PHASE 4: Integration Hardening (CRITICAL BLOCKER)

**Dependency Graph:**
```
Session 4 (SIP) ━━━ UNBLOCKS ━━━> Sessions 1,2,3 AND 6
   ↓ All bridges (SIP-H.323, SIP-WebRTC, NDI-SIP)
```

**Who's Waiting:**
- 1-NDI, 2-WebRTC, 3-H.323: BLOCKED (fix SIP integration bugs)
- 5-CLI, 6-Talent: SUPPORT (not blocked, but supporting)

**Idle Task Strategy:**
- Sessions 1,2,3: Help each other's test coverage
- Session 6: Build IF.swarm routing improvements while waiting
- Session 5: Pre-build Phase 5 test fixtures

**Wall-clock:** Start all 6 sessions → Session 4 is critical path → ~8 hours to completion

---

### PHASE 5: Optimization (FULLY PARALLEL)

**No blockers.** All 6 sessions work independently on their optimization targets.

**Idle Task Strategy:**
- Pair-test with neighbors (1↔2 WebRTC/NDI, 3↔4 H.323/SIP)
- When own work is done, help adjacent sessions with similar optimization patterns
- Example: 1-NDI compression patterns → help 2-WebRTC codec selection

**Wall-clock:** ~6 hours (can overlap with Phase 4 tail)

---

### PHASE 6: Final Production + Autonomous Mode (GATES)

**Gate:** Session 4 must complete P6 before Session 6 goes autonomous
```
4: Expert call + sign-off ┐
                          ├──> 6: Go autonomous
                          ┘
```

**Success Criteria per Session:**
- 1-NDI: 24/7 uptime tracking + witness alerts
- 2-WebRTC: Seamless failover, zero message loss
- 3-H.323: 12 Guardian MCU <200ms join/leave, <50ms latency
- 4-SIP: All SLA metrics passed + runbook signed off
- 5-CLI: Real-time cost monitoring + 10min reports active
- 6-Talent: Autonomous scout→test→queue→deploy loop

**Wall-clock:** ~4 hours (mostly independent final tests + waiting on 4)

---

## Decision Tree for Coordinators

### "Session X is blocked. What now?"

1. **Is it Phase 4 & not Session 4?**
   → Check `PHASES-4-6-MATRIX-ULTRA-CONDENSED.txt` column "IDLE TASK STRATEGY"
   → Assign idle task (test coverage, fixture building, docs)

2. **Is it Phase 5 or later?**
   → No blockers expected. Check why (data issue? test failure?)
   → Assign pair-testing with neighbor session

3. **Is it Session 6 in Phase 6?**
   → Waiting for Session 4 production sign-off?
   → Yes → give Session 4 priority (15-30 min typically)

### "How much longer will Phase 4 take?"

**Question:** What's Session 4's ETA on regression tests?
**Action:** Session 4 is critical path. If >2h remaining, consider having Sessions 1,2,3 pre-stage integration tests while 4 completes bridges.

### "Idle task for Sessions 1,2,3 right now?"

**P4 Stage:** Check `PHASES-4-6-MATRIX-ULTRA-CONDENSED.txt` → P4 IDLE TASK line
- 1-NDI: Help Session 2 WebRTC docs OR Session 5 CLI tests
- 2-WebRTC: Build cross-session test fixtures (IFMessage + SDP mocks)
- 3-H.323: Improve H323-PRODUCTION-RUNBOOK.md

---

## Critical Metrics to Track

| Metric | Target | Owner |
|--------|--------|-------|
| P4 completion time | <8h | Session 4 (blocker) |
| P5 latency baselines | 1-NDI <50ms, 3-H.323 <50ms | Sessions 1, 3 |
| P6 MCU test (12 Guardians) | <200ms join/leave | Session 3 |
| Cost tracking accuracy | Real-time, <5s lag | Session 5 (CLI) |
| Session 6 autonomy gate | Complete when 4 P6 sign-off | Session 4 + 6 |

---

## Files to Reference During Execution

- **Individual Phase Instructions:**
  - `/home/user/infrafabric/INSTRUCTIONS-SESSION-1-PHASE-2.md` (and PHASE-3, etc.)
  - `/home/user/infrafabric/INSTRUCTIONS-AGENT-6-IF-TALENT-PHASES-4-6.md`

- **Session Starters:**
  - `/home/user/infrafabric/docs/SESSION-STARTERS/session-1-ndi-phases-4-6.md`
  - `/home/user/infrafabric/docs/SESSION-STARTERS/session-2-webrtc-swarm.md`

- **This Coordination Matrix:**
  - **Ultra-condensed (fastest):** `PHASES-4-6-MATRIX-ULTRA-CONDENSED.txt`
  - **Operational (detailed):** `PHASES-4-6-COORDINATION-MATRIX.txt`
  - **Full reference:** `PHASES-4-6-CROSS-SESSION-MATRIX.md`

---

## Expected Timeline with Full Parallelism

```
P4: Session 4 critical path ~8h
    └─ Sessions 1,2,3 wait + idle tasks
       Sessions 5,6 support in parallel

P5: All 6 sessions parallel ~6h

P6: All 6 sessions parallel ~4h
    (6 waits on 4 sign-off, ~30min dependency)

Total wall-clock: ~18 hours (8 + 6 + 4)
Total effort: 71 hours distributed across 6 sessions @ $112
```

---

## Handoff Checklist (Phase 4 → Phase 5)

- [ ] Session 4: All regression tests pass (SIP-H.323, SIP-WebRTC, NDI-SIP)
- [ ] Sessions 1,2,3: Integration tests pass; no blockers remaining
- [ ] Session 5: Cost tracking dashboard live
- [ ] Session 6: 24/7 polling loop operational
- [ ] Metrics: Document P4 actual time vs estimated 8h

**Then:** Unlock Phase 5 for all sessions (parallel start)

---

## Coordination Contact Points

**Session 4 (SIP) — Critical Path Owner:**
- Daily ETA on P4 completion
- If delayed >2h: notify Sessions 1,2,3,6 for plan adjustment

**Session 5 (CLI) — Support Layer:**
- Cost tracking live by end of P4
- Alert system operational for P5-6

**Session 6 (Talent) — Autonomy Gate:**
- Ready for Phase 5 independent work
- Waiting for Session 4 P6 sign-off before autonomy deployment

**Coordinator Role:**
- Track P4 blocker (Session 4) daily
- Assign idle tasks when sessions block
- Monitor cost spend (Session 5) against $112 budget
- Gate Session 6 autonomy on Session 4 P6 completion
