# Session 1 (NDI) - Phase 4

**Status:** Phase 3 Complete ✅
**Next:** Integration Hardening

## Task 1: SIP-NDI Bridge Fixes (Sonnet)
Session 4 (SIP) integration - fix bugs from Phase 3
- Hash chain edge cases
- NDI metadata injection timing
- **File:** src/communication/ndi_sip_bridge.py

## Task 2: Test Coverage (Haiku)
- Improve test coverage to 95%+
- Add edge case tests
- **File:** tests/test_ndi_witness_complete.py

## Task 3: Performance Benchmarks (Sonnet)
- Verify hash chain validation <50ms
- Benchmark Ed25519 crypto overhead
- **File:** tests/performance/ndi_benchmarks.py

**BLOCKED ON:** Session 4 (SIP) Phase 4 completion
**IDLE:** If blocked, help Session 2 (WebRTC docs) or Session 5 (CLI tests)

**Completion:** Commit, STATUS-PHASE-4.md, auto-poll Phase 5
**Estimated:** 5 hours, $8
**GO NOW**
