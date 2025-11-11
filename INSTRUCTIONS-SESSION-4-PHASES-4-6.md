# Session 4 Phases 4-6: Integration Hardening → Optimization → Production (ULTRA-CONDENSED)

**Max 25 Lines Total | PRIORITY: UNBLOCK Sessions 1-3 WAITING**

---

## Phase 4: Integration Hardening (FIX BLOCKER)

**IDLE TASK:** None — You're the blocker (Sessions 1-3 waiting)

1. **Fix all SIP-H.323 bridge integration bugs** | `src/communication/sip_h323_gateway.py` | Sonnet | PRIORITY: unblock Session 3
2. **Fix SIP-WebRTC evidence delivery bugs** | `src/communication/sip_webrtc_bridge.py` | Sonnet | PRIORITY: unblock Session 2
3. **Fix NDI stream integration to SIP** | `src/communication/sip_ndi_ingest.py` | Sonnet | PRIORITY: unblock Session 1
4. **Regression tests: All integrations pass** | `tests/integration/test_all_sessions.py` | Sonnet | PRIORITY: unblock Sessions 1,2,3

---

## Phase 5: Optimization

5. **Call setup latency <1s (ESCALATE→Ring)** | `src/communication/sip_proxy.py` | Sonnet | Concurrent call handler
6. **Concurrent call handling (100+ concurrent)** | `src/communication/sip_state_manager.py` | Sonnet | Load test: 50 ESCALATE/sec
7. **IF.witness async logging (non-blocking)** | `src/communication/sip_witness_async.py` | Haiku | Remove latency bottleneck

---

## Phase 6: Production External Expert Test

8. **Real expert SIP call (scheduled validation)** | `tests/test_production_external_expert.py` | Sonnet | HELP: CLI (Session 5) for witness, Talent (Session 6) for routing
9. **Production readiness sign-off** | `PRODUCTION-READINESS.md` | Sonnet | All metrics meet SLA

---

**Timeline:** 8 hours | **Cost:** $15 | **When done:** Unblocks Sessions 1-3 for final integration
