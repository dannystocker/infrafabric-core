# Session 3 (H.323) - Phase 7 REVISED

**Status:** Phases 4-6 Complete! 🎉
**Next:** Help Session 4 (SIP) FIRST, Then Phase 7

## PRIORITY: Help Session 4 with SIP-H.323 Bridge

**Your Task:** Session 4 is blocked. Help them with SIP-H.323 gateway before starting Phase 7.

### Task 1: H.323 Side of SIP Bridge (Sonnet)
Work WITH Session 4 on src/communication/sip_h323_gateway.py
- Fix codec transcoding (G.729 ↔ G.711)
- Fix Gatekeeper routing for SIP-bridged calls
- Test with mock SIP proxy
- **Coordinate:** Post results to Session 4

### Task 2: Integration Tests (Haiku)
- Create test fixtures for SIP-H.323 flow
- Mock SIP INVITE → H.323 ARQ/ACF
- **File:** tests/fixtures/sip_h323_fixtures.py

**AFTER Session 4 unblocked, THEN start Phase 7:**

### Task 3: Guardian Scale (Sonnet)
- Scale to 50 concurrent Guardian streams
- **File:** src/communication/h323_guardian_cluster.py

**GOAL:** Help Session 4 first (you're already ahead!), then continue Phase 7

**Completion:** Commit, post STATUS.md with "HELPED SESSION 4, NOW PHASE 7", auto-poll Phase 8
**Estimated:** 6 hours total, $12
**GO NOW - HELP THEN CONTINUE!**
