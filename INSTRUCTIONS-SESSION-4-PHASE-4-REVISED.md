# Session 4 (SIP) - Phase 4 REVISED

**Status:** Phase 3 Complete ✅
**Next:** Integration Hardening - ACCEPT HELP FROM ALL SESSIONS!

## YOU'RE THE BLOCKER - BUT EVERYONE IS HELPING YOU!

**Sessions 1-3 are helping with YOUR integration work:**
- Session 1 (NDI): Fixing NDI side of SIP-NDI bridge
- Session 2 (WebRTC): Fixing WebRTC side of SIP-WebRTC bridge
- Session 3 (H.323): Fixing H.323 side of SIP-H.323 bridge

**YOUR Job:** Coordinate + integrate their work

### Task 1: SIP Proxy Core (Sonnet)
Focus on the SIP proxy side of all 3 bridges:
- SIP INVITE routing logic
- SIP headers (X-IF-Trace-ID, X-IF-Hazard)
- SIP session management
- **Files:** src/communication/sip_proxy_core.py

### Task 2: Integration Coordinator (Sonnet)
Pull together work from Sessions 1-3:
- Integrate NDI bridge (from Session 1)
- Integrate WebRTC bridge (from Session 2)
- Integrate H.323 bridge (from Session 3)
- **File:** src/communication/sip_integration_coordinator.py

### Task 3: End-to-End Test (Haiku)
Test all 3 bridges work together:
- SIP call → all 3 protocols activated
- **File:** tests/integration/test_sip_all_bridges_e2e.py

### Task 4: Coordination (Critical!)
- Monitor STATUS.md from Sessions 1-3
- Review their PRs/commits
- Provide feedback/guidance
- **Communication:** Essential!

**YOU'RE NOT ALONE - THE SWARM IS HELPING YOU!**

**Completion:** Commit, STATUS-PHASE-4.md, auto-poll Phase 5
**Estimated:** 6 hours (down from 8 with help!), $12
**GO NOW - COORDINATE THE SWARM!**
