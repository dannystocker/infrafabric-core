# Session 3 (H.323) - Phases 4-6: Hardening → Production

**Status:** Phase 3 Complete ✅
**Phases:** 4-6 of 6 (Final push)

## Phase 4: Integration Hardening
| Task | File | Model | Blocking? |
|------|------|-------|-----------|
| Fix SIP gateway codec transcoding (G.729 ↔ G.711 bugs) | src/communication/h323_sip_gateway.py | Haiku | **BLOCKED** waiting Session 4: help Session 1 w/ NDI monitoring codec validation |
| Enforce IF.guard policy on bridged SIP calls | src/communication/h323_policy_enforce.py | Sonnet | — |
| Integration test (SIP→H.323 calls, mixed codec streams) | tests/test_sip_h323_integration.py | Haiku | **BLOCKED** waiting Session 4: help Session 5 w/ CLI export SIP logs |

**IDLE TASK:** Improve docs/H323-PRODUCTION-RUNBOOK.md (add codec troubleshooting section)

## Phase 5: Optimization
| Task | File | Model | Notes |
|------|------|-------|-------|
| Reduce H.323 latency (<50ms, jitter <10ms) | src/communication/h323_gatekeeper_tuning.py | Sonnet | Gatekeeper buffer tuning, RAS message batching |
| Codec efficiency (prefer VP8 over H.264 where possible) | src/communication/codec_selector.py | Haiku | Bandwidth analysis, MCU codec negotiation |
| Performance baseline (8-12 concurrent Guardians) | tests/test_h323_perf_baseline.py | Haiku | Latency, jitter, packet loss metrics |

**IDLE TASK:** Document codec tradeoffs in docs/H323-CODEC-SELECTION.md

## Phase 6: Guardian Council Production Test
| Task | File | Model | Deliverable |
|------|------|-------|-------------|
| Live test: 12 real Guardians MCU conference | tests/test_h323_production_12guardian.py | Sonnet | Load test, failover, incident response |
| Production handoff (deploy, monitor, rollback) | docs/H323-PRODUCTION-DEPLOY.md | Sonnet | Runbook complete |

**CRITICAL SUCCESS:**
✅ SIP-H.323 gateway stable (no codec drops)
✅ 12 Guardians join/leave smoothly (<200ms)
✅ Latency <50ms sustained over 30min conference
✅ Failover <5s, zero call loss
✅ Production runbook (deploy, troubleshoot, rollback)

**Estimated:** 8-10 hours | **Cost:** $15-20
