# IF.connect Real-Time Communication — Quick Reference

**Version:** 2.1
**Date:** 2025-11-11
**Full Spec:** [IF-REALTIME-COMMUNICATION-INTEGRATION.md](IF-REALTIME-COMMUNICATION-INTEGRATION.md)

---

## One-Page Overview

### Protocol → Use Case Mapping

| Protocol | Primary Use | IF Component | Philosophy | Ports |
|----------|------------|--------------|------------|-------|
| **NDI** | Evidence streaming | IF.witness | IF.ground (observable) | 5353 UDP, 5960+ TCP/UDP |
| **H.323** | Guardian council calls | IF.guard | Ubuntu (consensus), Kant (gates) | 1719 RAS, 1720 H.225 |
| **SIP** | External expert calls | IF.ESCALATE | Popper (falsification) | 5060 TCP/UDP |
| **WebRTC** | Agent peer-to-peer mesh | IF.swarm | Indra's Net (reflection) | Dynamic (ICE) |

---

## IF.ESCALATE Flow (Hazard → Real-Time Call)

```
IFMessage v2.1 {hazard: ["legal"]}
  ↓
IF.connect router (hazard-first routing)
  ↓
H.323 Gatekeeper (Kantian admission control)
  ↓
H.323 MCU (Guardian council video conference)
  ↓
IF.witness logs decision (Ed25519 signature)
```

**Latency Target:** Hazard detection → Human on call < 30 seconds

---

## IF.witness Integration (Every Stream Signed)

### NDI Metadata Injection

```python
# Every NDI frame carries witness hash chain
witness_entry = {
    'frame_number': N,
    'content_hash': sha256(frame),
    'prev_hash': last_hash,
    'trace_id': current_trace,
    'signature': ed25519_sign(...)
}
ndi_send.send_video(frame, metadata=witness_entry)
```

### H.323 Call Logging

```yaml
witness_log:
  - event: h323_call_started
    call_id: "if://call/escalate/..."
    participants: [guardian-sage, guardian-skeptic, ...]
    trace_id: "a2f9c3b8d1e5"
  - event: h323_decision_recorded
    decision: "approve_with_conditions"
    witness_hash: "sha256:..."
    signature: "ed25519:..."
```

### WebRTC SDP Logging

```javascript
await logToWitness({
  event: 'webrtc_offer_created',
  peer: agentId,
  sdp_hash: sha256(offer.sdp),
  trace_id: currentTraceId,
  signature: ed25519.sign(...)
});
```

---

## Wu Lun (五倫) Relationships

| Relationship | Protocol Example | Meaning |
|--------------|------------------|---------|
| **父子** (Parent-Child) | NDI sender → receivers | Generational, asynchronous |
| **君臣** (Ruler-Subject) | H.323 Gatekeeper → terminals | Hierarchical admission |
| **朋友** (Friends) | SIP peers | Equal partners |
| **兄弟** (Siblings) | WebRTC agent mesh | Parallel coordination |
| **夫婦** (Complementary) | SIP proxy ↔ registrar | Manager-managed |

---

## Kantian Duty Gates (Policy Enforcement)

```python
# H.323 Gatekeeper admission control
def admit_terminal(request):
    # 1. Verify Ed25519 signature
    if not verify_signature(request): return REJECT

    # 2. Check registry (no sybil)
    if not is_registered(request.terminal_id): return REJECT

    # 3. Kantian constraints
    if request.has_pii and call_type == "ESCALATE":
        return REJECT  # PII policy violation

    # 4. Bandwidth quota
    if request.bandwidth_bps > MAX_BW: return REJECT

    # 5. Log to IF.witness
    witness.log({...})

    return ADMIT
```

---

## IF.TTT Compliance Summary

| Principle | Implementation |
|-----------|----------------|
| **Traceable** | Every message has trace_id, every frame has hash chain |
| **Transparent** | SIP is text-based (fully auditable), SDP logged to witness |
| **Trustworthy** | Ed25519 signatures on IFMessage, NDI metadata, WebRTC offers |

---

## Implementation Weeks

| Week | Task | Protocol | Deliverable |
|------|------|----------|-------------|
| 1-2 | NDI evidence streaming | NDI | `IF.witness.ndi-publisher` (Python) |
| 3-4 | Agent WebRTC mesh | WebRTC | `IFAgentWebRTC` class (TypeScript) |
| 5-6 | Guardian H.323 council | H.323 | `IF.guard.h323-gatekeeper` (Python/C++) |
| 7-8 | SIP external experts | SIP | `IF.connect.sip-proxy` (Kamailio config) |

---

## Philosophy Grounding

### Vienna Circle → NDI Discovery

**Principle:** Verificationism — 2+ independent sources

**Implementation:** NDI multicast discovery (mDNS) + optional centralized Discovery Service
- **Primary:** mDNS on 5353 UDP (peer discovery)
- **Secondary:** Discovery Server on 5959 TCP (centralized registry)
- **Verification:** Both methods must agree on stream availability

### Ubuntu → H.323 MCU

**Principle:** Communal synthesis via deliberation

**Implementation:** Centralized Multipoint Conference
- **Audio Mixing:** All Guardian voices → single mixed stream → all participants hear all
- **Video Grid:** Continuous presence (everyone sees everyone)
- **Evidence Display:** T.120 whiteboard shared across council

### Popper → SIP Contrarian Views

**Principle:** Falsifiability via external challenge

**Implementation:** SIP gateway to external advisors
- **ESCALATE** triggers SIP INVITE to expert-risk-analyst@external.advisor
- **Contrarian input** via SIP call → WebRTC DataChannel evidence sharing
- **IF.guard logs** external dissent, prevents groupthink

### Indra's Net → WebRTC Mesh

**Principle:** Every node reflects every other node

**Implementation:** Peer-to-peer DataChannels
- **Full mesh topology:** N agents = N(N-1)/2 connections
- **Message reflection:** Every IFMessage has `reflects` field linking to parent message
- **Swarm coordination:** Finance.Agent ↔ Legal.Agent ↔ Macro.Agent peer exchanges

---

## Quick Diagnostics

### Check NDI Stream Health

```bash
# List available NDI sources
ndiscan

# Verify metadata in stream
ndi-metadata-viewer --source "IF.yologuard Scanner 01"
# Expected: witness_entry JSON with signature field
```

### Check H.323 Gatekeeper Registrations

```bash
# Query gatekeeper for registered terminals
gnugk -s status
# Expected: guardian-sage, guardian-skeptic, guardian-ethicist
```

### Check SIP Proxy Logs

```bash
# View recent SIP INVITE messages
tail -f /var/log/kamailio/kamailio.log | grep "INVITE.*ESCALATE"
# Expected: X-IF-Trace-ID, X-IF-Hazard headers present
```

### Check WebRTC DataChannel Health

```javascript
// In browser console
dataChannel.readyState  // Expected: "open"
dataChannel.bufferedAmount  // Expected: < 100KB (low latency)
```

---

## Success Metrics (Production Readiness)

- ✅ **IF.ESCALATE Latency:** < 30 seconds (hazard → human on call)
- ✅ **IF.witness Coverage:** 100% of NDI frames have hash chain
- ✅ **IF.guard Quorum:** 15+ guardians concurrent H.323 call
- ✅ **IF.swarm Mesh:** 8+ agents WebRTC < 50ms peer latency
- ✅ **IF.TTT:** 100% of calls/streams have Ed25519 signatures

---

## References

- **Full Spec:** [IF-REALTIME-COMMUNICATION-INTEGRATION.md](IF-REALTIME-COMMUNICATION-INTEGRATION.md)
- **IF.connect Architecture:** [IF_CONNECTIVITY_ARCHITECTURE.md](../IF_CONNECTIVITY_ARCHITECTURE.md)
- **IF.witness Paper:** [../papers/IF-witness.md](../papers/IF-witness.md)
- **Philosophy Database:** [../docs/evidence/gemini-logs/core/IF.philosophy-database-r4.yaml](../docs/evidence/gemini-logs/core/IF.philosophy-database-r4.yaml)

---

**Citation:** `if://doc/realtime-comms-quick-ref-2025-11-11`
**Status:** Production-ready specification
**Next Step:** Select Week 1-2 (NDI) or Week 3-4 (WebRTC) for pilot implementation
