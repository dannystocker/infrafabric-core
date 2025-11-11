# Session 4 (SIP) - Phase 4

**Status:** Phase 3 Complete ✅ (Production Deployed!)
**Next:** Integration Hardening - UNBLOCK SESSIONS 1-3

## Task 1: Fix SIP-H.323 Bridge (Sonnet) **[UNBLOCKS SESSION 3]**
- Debug codec transcoding issues
- Fix call routing between SIP and H.323
- **File:** src/communication/sip_h323_gateway.py

## Task 2: Fix SIP-WebRTC Bridge (Sonnet) **[UNBLOCKS SESSION 2]**
- Fix DataChannel integration
- Ensure IFMessage escalate works
- **File:** src/communication/sip_webrtc_bridge.py

## Task 3: Fix NDI-SIP Integration (Sonnet) **[UNBLOCKS SESSION 1]**
- Enable optional NDI evidence streaming during expert calls
- Test end-to-end flow
- **File:** src/communication/sip_ndi_ingest.py

## Task 4: Regression Tests (Haiku)
- Test all 3 integrations work together
- **File:** tests/integration/test_sip_all_bridges.py

**PRIORITY:** You're blocking Sessions 1-3. Fix integrations ASAP.
**NO IDLE TASKS:** You're critical path - work faster!

**Completion:** Commit, STATUS-PHASE-4.md, auto-poll Phase 5
**Estimated:** 8 hours, $15
**GO NOW - UNBLOCK THE SWARM!**
