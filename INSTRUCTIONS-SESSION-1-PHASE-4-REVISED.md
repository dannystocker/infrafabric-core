# Session 1 (NDI) - Phase 4 REVISED

**Status:** Phase 3 Complete ✅
**Next:** Help Session 4 (SIP) - They're the Blocker!

## PRIORITY: Help Session 4 with SIP-NDI Bridge

**Your Task:** Session 4 needs to fix SIP-NDI integration. YOU know NDI best.

### Task 1: NDI Side of SIP Bridge (Sonnet)
Work WITH Session 4 on src/communication/sip_ndi_bridge.py
- Fix hash chain validation during SIP calls
- Fix metadata injection timing
- Test with mock SIP calls
- **Coordinate:** Post results to Session 4

### Task 2: NDI Integration Tests (Haiku)
- Create test fixtures for SIP-NDI flow
- Mock SIP INVITE → NDI stream starts
- **File:** tests/fixtures/sip_ndi_fixtures.py

### Task 3: Documentation (Haiku)
- Document NDI integration patterns for Session 4
- **File:** docs/NDI-SIP-INTEGRATION-GUIDE.md

**GOAL:** Unblock Session 4 so they can unblock Sessions 2-3!

**Completion:** Commit, post STATUS.md with "HELPING SESSION 4", auto-poll Phase 5
**Estimated:** 4 hours, $8
**GO NOW - HELP THE BLOCKER!**
