# Session 3 (H.323) - Phase 2 Instructions

**Status:** Phase 1 Complete ✅
**Next Phase:** Integration + Redundancy + Load Testing

## Task 1: SIP-H.323 Gateway Integration
Session 4 (SIP) needs to bridge external expert calls into Guardian council H.323 conferences.

**Deliverables:**
- Implement H.323-SIP gateway in src/communication/h323_sip_gateway.py
- Test codec transcoding (H.323 G.729 ↔ SIP G.711)
- Validate IF.guard policy enforcement on bridged calls

**Use IF.swarm:**
- Spawn 1 Sonnet agent: Gateway implementation (complex codec handling)
- Spawn 1 Haiku agent: Test suite

## Task 2: Gatekeeper Redundancy
Ensure IF.guard council calls don't fail if primary Gatekeeper crashes.

**Deliverables:**
- Configure secondary Gatekeeper (hot standby)
- Implement health check monitoring (Prometheus + Grafana)
- Test failover (kill primary, verify secondary takeover <5s)

**Use Sonnet** (critical availability requirement)

## Task 3: Load Testing
Simulate IF.guard council meeting with 8-12 concurrent Guardian video streams.

**Deliverables:**
- Load test script (8-12 simulated H.323 endpoints)
- Measure: Bandwidth usage, latency, packet loss, jitter
- Document maximum supported Guardians (target: 15 concurrent)

**Use Haiku** for scripts, **Sonnet** for performance analysis

## Completion Protocol
After finishing:
1. Commit to claude/realtime-workstream-3-h323
2. Push to origin
3. Create STATUS-PHASE-2.md
4. **AUTO-CHECK FOR PHASE 3:**
   ```bash
   git pull origin claude/realtime-workstream-3-h323
   [ -f INSTRUCTIONS-SESSION-3-PHASE-3.md ] && cat INSTRUCTIONS-SESSION-3-PHASE-3.md || while true; do sleep 60; git pull --quiet; [ -f INSTRUCTIONS-SESSION-3-PHASE-3.md ] && break; done
   ```

**Estimated Time:** 5-6 hours with swarms
**Estimated Cost:** $10-15

Begin Phase 2!
