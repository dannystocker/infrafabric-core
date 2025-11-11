# Session 2 (WebRTC) - Phase 2 Instructions

**Status:** Phase 1 Complete ✅
**Next Phase:** Integration Testing + Security Hardening

## Task 1: SIP-WebRTC Integration
Session 4 (SIP) uses WebRTC DataChannel for real-time agent coordination.

**Deliverables:**
- Test WebRTC DataChannel integration with SIP proxy
- Implement fallback to TURN server if direct P2P fails
- Update src/communication/webrtc_datachannel.py with SIP hooks

**Use IF.swarm:**
- Spawn 1 Sonnet agent: Integration testing
- Spawn 1 Haiku agent: Update documentation

## Task 2: Performance Optimization
Optimize for low-latency agent mesh communication.

**Deliverables:**
- Benchmark latency (target: <50ms P2P, <150ms via TURN)
- Configure STUN/TURN servers (Coturn setup guide)
- Implement bandwidth adaptation (reduce quality under load)

**Use Haiku** for documentation, **Sonnet** for benchmarking code

## Task 3: Security Hardening
Validate DTLS and SRTP encryption.

**Deliverables:**
- Test certificate validation (reject self-signed in production)
- Implement SRTP key rotation (every 24 hours)
- Add IF.witness logging for all WebRTC session establishment

**Use Sonnet** (security-critical)

## Completion Protocol
After finishing:
1. Commit to claude/realtime-workstream-2-webrtc
2. Push to origin
3. Create STATUS-PHASE-2.md
4. **AUTO-CHECK FOR PHASE 3:**
   ```bash
   git pull origin claude/realtime-workstream-2-webrtc
   if [ -f INSTRUCTIONS-SESSION-2-PHASE-3.md ]; then
     cat INSTRUCTIONS-SESSION-2-PHASE-3.md
   else
     # Poll every 60s
     while true; do
       sleep 60
       git pull --quiet
       [ -f INSTRUCTIONS-SESSION-2-PHASE-3.md ] && break
     done
   fi
   ```

**Estimated Time:** 4-5 hours with swarms
**Estimated Cost:** $8-12

Begin Phase 2 now!
