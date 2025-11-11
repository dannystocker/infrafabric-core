# Phases 4-6: Cross-Session Coordination Matrix

## PHASE 4: Integration Hardening (8-10h)

| Session | Main Tasks | Dependencies | IDLE Task When Blocked |
|---------|-----------|--------------|----------------------|
| **1-NDI** | Fix hash chain edge cases; debug metadata injection; resolve SIP integration | BLOCKED by 4 | Help Session 2 WebRTC docs + Session 5 CLI tests |
| **2-WebRTC** | Mesh stability/connection pooling; SIP-WebRTC bridge | BLOCKED by 4 | Build cross-session test fixtures (IFMessage + SDP mocks) |
| **3-H.323** | Fix SIP gateway codec transcoding (G.729↔G.711); enforce IF.guard policy; integration tests | BLOCKED by 4 | Improve H323-PRODUCTION-RUNBOOK.md (codec troubleshooting) |
| **4-SIP** | **CRITICAL BLOCKER:** Fix SIP-H.323 bridge; SIP-WebRTC bridge; NDI-SIP ingest; regression tests all | None (unblock 1,2,3,6) | None — you're critical path. Keep shipping. |
| **5-CLI** | Witness integration; cost tracking; real-time dashboard; spawn helpers | SUPPORT 1,2,3,4 | Pre-build test fixtures for Phase 5 |
| **6-Talent** | 24/7 polling loop; GitHub/arXiv/HF API scan; auto-queue to sandbox | SUPPORT 4 | Build IF.swarm routing improvements + help Session 4 routing logic |

**Notes:** Session 4 unblocks Sessions 1,2,3 → Phase 5. Session 5 (CLI) + Session 6 (Talent) run in parallel, unblocking is not their role.

---

## PHASE 5: Optimization (6-8h)

| Session | Main Tasks | Blockers | IDLE Task |
|---------|-----------|----------|-----------|
| **1-NDI** | Compress NDI metadata packets; optimize hash chain verification (<50ms overlay); benchmark Ed25519 overhead | None (independent post-P4) | Document codec tradeoffs in NDI-OPTIMIZATION.md |
| **2-WebRTC** | VP9 codec + adaptive bitrate; P2P routing greedy mesh optimization; latency metrics | None (independent) | Help Session 3 with H.323 perf baseline testing |
| **3-H.323** | Reduce latency (<50ms, jitter <10ms); codec efficiency (VP8 over H.264); perf baseline (8-12 Guardians) | None (independent) | Help Session 5 optimize CLI SQLite WAL patterns |
| **4-SIP** | Call setup latency <1s; concurrent handling (100+ calls, 50 ESCALATE/sec); async IF.witness logging | None (independent) | — |
| **5-CLI** | Profiling + benchmarks (Sonnet); SQLite WAL; connection pooling; fast spawn; fixtures | SUPPORT 1,2,3,4 | Pre-load perf fixtures for Phase 6 |
| **6-Talent** | Scout 2nd model release; sandbox 25 tests; certify & deploy to IF.swarm | None (independent) | Dashboard improvements + documentation |

**Notes:** Phase 5 is fully parallel. No critical blockers. Sessions can help each other with optimization patterns.

---

## PHASE 6: Final Production + Autonomous Mode (4-6h)

| Session | Main Tasks | Dependencies | Critical Success |
|---------|-----------|--------------|------------------|
| **1-NDI** | 24/7 health checks; alerting for hash chain breaks; dashboard (stream status + witness integrity) | None (ready post-P5) | Uptime tracking + event logging to IF.witness |
| **2-WebRTC** | Autonomous healing (auto-reconnect, backoff strategy) | None (ready post-P5) | Seamless failover, zero message loss |
| **3-H.323** | Live test: 12 real Guardians MCU; production handoff + runbook | None (ready post-P5) | <200ms join/leave; <50ms sustained latency; <5s failover |
| **4-SIP** | Real expert SIP call (scheduled validation); production readiness sign-off | None (gates 6) | All SLA metrics met + runbook complete |
| **5-CLI** | Cost monitor agent; budget alerts (>80%); multi-session cost view; alert spawn | SUPPORT 1,2,3,4,6 | Real-time cost tracking + 10min auto-reports |
| **6-Talent** | **FULL AUTONOMY:** Auto-approval workflow; deploy to IF.swarm (zero human touch until queue) | UNBLOCK by 4 (external expert calls) | Scout → Test → Queue → Deploy without human |

**Notes:** Sessions 1,2,3 are independent in P6. Session 4 gates Session 6's autonomy. Session 5 (CLI) is support for all.

---

## Critical Path & Escalation

**Who Blocks Whom:**
1. **Session 4 (SIP)** = critical path for Phases 4 → unblocks 1,2,3
2. **Session 6 (Talent)** waits on Phase 4 completion for external expert routing
3. **Session 5 (CLI)** = support layer for all; no blocking dependencies

**When Blocked (Parallel Work):**
- **P4:** 1,2,3 help each other's tests; 6 builds routing improvements for 4
- **P5:** All independent; pair-test with neighboring sessions (e.g., 1↔2, 3↔4)
- **P6:** 4 gates 6's autonomy; others finish independently; 5 monitors cost

**Success Criteria (P4-6 Complete):**
✅ All bridges stable (SIP-H.323, SIP-WebRTC, NDI-SIP)
✅ 12 Guardian MCU live test pass
✅ <50ms latency sustained, <5s failover
✅ Talent autonomy operational (scout→sandbox→deploy loop)
✅ Real-time cost monitoring active
✅ Production runbooks signed off

---

## Session Effort & Cost Summary

| Phase | 1-NDI | 2-WebRTC | 3-H.323 | 4-SIP | 5-CLI | 6-Talent | Total |
|-------|-------|----------|---------|-------|-------|----------|-------|
| **P4** | 6h $8 | 4h $6 | 5h $7 | 8h $15 | 4h $5 | 3h $5 | 30h $46 |
| **P5** | 5h $8 | 4h $6 | 4h $6 | 5h $10 | 4h $5 | 3h $5 | 25h $40 |
| **P6** | 3h $5 | 2h $3 | 3h $5 | 2h $3 | 2h $2 | 4h $8 | 16h $26 |
| **Total** | 14h $21 | 10h $15 | 12h $18 | 15h $28 | 10h $12 | 10h $18 | **71h $112** |

**Max parallel:** 6 sessions × ~8h = ~8 hours wall clock (P4), then ~6h (P5), then ~4h (P6) = ~18h total with parallelism
