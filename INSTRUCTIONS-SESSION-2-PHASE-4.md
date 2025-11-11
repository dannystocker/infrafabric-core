# Session 2 (WebRTC) - Phase 4

**Status:** Phases 2-3 Complete ✅
**Next:** Integration Hardening

## Task 1: SIP-WebRTC Integration Fixes (Sonnet)
Session 4 (SIP) needs WebRTC bridge fixes
- Debug connection issues from Phase 3 testing
- Fix DataChannel message routing
- **File:** src/communication/webrtc_sip_bridge.py

## Task 2: Mesh Stability (Sonnet)
- Connection pooling, heartbeat protocol
- Auto-reconnect with exponential backoff
- **File:** src/communication/webrtc_mesh_stability.py

## Task 3: Integration Tests (Haiku)
- Test with Session 4 (SIP proxy)
- Test with Session 1 (NDI streaming)
- **File:** tests/integration/test_webrtc_cross_session.py

**PRIORITY:** Unblock Session 1 (NDI needs WebRTC mesh)
**IDLE:** If blocked, help Session 3 (H.323 load tests)

**Completion:** Commit, STATUS-PHASE-4.md, auto-poll Phase 5
**Estimated:** 6 hours, $12
**GO NOW**
