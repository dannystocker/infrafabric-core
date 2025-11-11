# RFC: Communication Layer Integration (Swarp v4* + WebRTC/SIP/H.323)

**Status:** DRAFT
**Created:** 2025-11-11
**Authors:** GPT-5 Pro (Swarp v4*), GPT-5 Pro (WebRTC/SIP/H.323), Gemini 2.5 Pro (Review), Claude (Integration)
**Supersedes:** None
**Implements:** Message security hardening + Real-time transport

---

## Executive Summary

This RFC proposes integrating **two complementary communication enhancements** into InfraFabric:

1. **Swarp v4* Message Hardening** (MESSAGE LAYER)
   - Enhanced IFMessage schema v2.1 with anti-replay, hazard tags, scoping
   - Cross-swarm relation agent for evidence mapping
   - Fixes critical v2 ESCALATE bug (confidence thresholds burying critical issues)

2. **WebRTC/SIP/H.323 Transport Integration** (TRANSPORT LAYER)
   - Real-time peer-to-peer communication for agents
   - Transforms ESCALATE into actionable voice/video calls
   - Live evidence streaming during deliberations

**Key Principle**: These are NOT competing proposals—they solve different layers of the same problem.

---

## Problem Statement

### Current Gaps

**Gap 1: Message Layer Vulnerabilities** (Swarp v4* addresses)
- ❌ Confidence manipulation to avoid escalation triggers
- ❌ Conversation ID collisions across parallel workflows
- ❌ False conflicts from scope ambiguity
- ❌ Critical issues (legal/safety) buried by numeric confidence gates
- ❌ No systematic evidence mapping across swarms (Finance ↔ Legal ↔ Markets)

**Gap 2: Transport Layer Limitations** (WebRTC/SIP/H.323 addresses)
- ❌ ESCALATE is abstract performative with no action path
- ❌ No real-time human-in-the-loop capability
- ❌ Evidence streaming is async-only (no live fact-checking during calls)
- ❌ Multipoint deliberation uses ad-hoc topologies (not enterprise-grade)
- ❌ No NAT traversal for browser-based agent UIs

---

## Proposed Solution Architecture

### Layer Stack

```
┌─────────────────────────────────────────────────────────┐
│ IF.guard / IF.witness (Governance)                      │
│ - Audits hazard tags, replays signed conversations      │
├─────────────────────────────────────────────────────────┤
│ APPLICATION LAYER                                        │
│ - FIPA performatives: request, inform, ESCALATE         │
│ - Cross-swarm relation agent (rhizomatic citations)     │
├─────────────────────────────────────────────────────────┤
│ MESSAGE LAYER (Swarp v4* Schema v2.1) ★ NEW             │
│ - IFMessage: nonce, ttl, scope, hazard tags, topic_hash │
│ - Policy-first routing (hazard → ESCALATE, not just %)  │
│ - Ed25519 signatures, content-addressed citations       │
├─────────────────────────────────────────────────────────┤
│ SESSION LAYER (SIP/H.323 Signaling) ★ NEW               │
│ - SIP: REGISTER, INVITE, BYE (session lifecycle)        │
│ - H.323 Gatekeeper: Admission control, quotas           │
│ - IF.guard gates: Pre-session policy enforcement        │
├─────────────────────────────────────────────────────────┤
│ TRANSPORT LAYER (WebRTC DataChannels) ★ NEW             │
│ - Peer-to-peer agent messaging (NAT traversal)          │
│ - Live evidence streaming (DataChannel + media)         │
│ - DTLS-SRTP encryption (end-to-end security)            │
├─────────────────────────────────────────────────────────┤
│ EXISTING: DDS/RTPS (service mesh) │ REST/gRPC (APIs)    │
│ - Level 2 (Cellular) connectivity from IF.connect       │
└─────────────────────────────────────────────────────────┘
```

---

## Component 1: Swarp v4* Message Hardening

### 1.1 Enhanced IFMessage Schema v2.1

**Additions to existing schema** (from SWARM-COMMUNICATION-SECURITY.md):

```yaml
# IFMessage v2.1 (Swarp v4* enhancements)
performative: "inform"
sender: "if://agent/swarm/legal-1@1.2.0"
receiver: ["if://agent/swarm/financial/*"]
conversation_id: "if://conversation/epic-2025-11-10-xyz"
topic: "if://topic/mission/legal/findings"

# EXISTING FIELDS (from v2.0)
content:
  claim: "Epic Games settled antitrust lawsuit for $520M"
  evidence: ["SEC-10K-2023:pg14", "Reuters:2025-09-17"]
citation_ids: ["cit:9f2b3a1e", "cit:4d8a7c2d"]
timestamp: "2025-11-10T14:32:17.234Z"
sequence_num: 42
trace_id: "a2f9c3b8d1e5"

# ★ NEW FIELDS (v2.1 Swarp hardening)
nonce: "7a8f3d2e1c9b"  # 96-bit random (anti-replay beyond sequence)
ttl: 300  # seconds (message expires after 5 minutes)
scope:  # Prevents false conflicts
  mission_id: "epic-intelligence-v4"
  workflow: "legal-findings-pass-3"
  domain: "legal"
topic_hash: "sha256:1a2b3c..."  # Conversation ID collision detection

hazard:  # ★ CRITICAL: Policy-driven escalation
  type: "legal"  # OR "safety", "conflict", "ethical"
  severity: "high"  # low/medium/high
  auto_escalate: true  # Forces ESCALATE regardless of confidence
  rationale: "Potential liability exposure >$100M"

# EXISTING: Signature (from v2.0)
signature:
  algorithm: "ed25519"
  public_key: "ed25519:AAAC3NzaC1lZDI1NTE5AAAAIOMq..."
  signature_bytes: "ed25519:m8QKz5X3jP..."
  signed_fields: [..., "nonce", "ttl", "scope", "topic_hash", "hazard"]
```

### 1.2 Critical Bug Fix: ESCALATE Logic Reordering

**Problem (v2):** Confidence gates bury critical issues

```python
# ❌ BROKEN (v2): HOLD catches critical issues before ESCALATE
if confidence < 0.3:
    return "HOLD"  # Catches 0.2 confidences (legal hazards hidden!)
if confidence < 0.2:
    return "ESCALATE"  # Never reached for 0.2-0.3 range
```

**Solution (v3/Swarp v4*):** Hazard-first routing

```python
# ✅ FIXED (v4*): Check hazards BEFORE confidence gates
if message.get("hazard", {}).get("auto_escalate"):
    return "ESCALATE"  # Legal/safety hazards bypass confidence

if confidence < 0.2:
    return "ESCALATE"  # Critical uncertainty
if confidence < 0.3:
    return "HOLD"  # Medium uncertainty
if confidence >= 0.7:
    return "SHARE"  # High confidence
```

### 1.3 Cross-Swarm Relation Agent

**Purpose:** Map evidence across specialized swarms (Finance ↔ Legal ↔ Markets ↔ Macro)

**Implementation**:

```python
class CrossSwarmRelationAgent:
    """
    Rhizomatic citation mapping across domain swarms
    Implements: Vienna Circle verificationism, Popperian falsifiability, Ubuntu consensus
    """

    def __init__(self, swarms: List[str]):
        self.swarms = swarms  # ["finance", "legal", "markets", "macro"]
        self.citation_graph = nx.MultiDiGraph()  # Citation network

    def map_evidence(self, claim_id: str) -> Dict[str, List[str]]:
        """
        For a claim, find all supporting/contradicting evidence across swarms
        Returns: {swarm_domain: [citation_ids]}
        """
        evidence_map = {}

        for swarm in self.swarms:
            # Query swarm's citation store
            citations = self.query_swarm_citations(swarm, claim_id)

            # Verify each citation (multi-source requirement)
            verified = [
                c for c in citations
                if self.verify_citation_sources(c) >= 2  # Vienna Circle: 2+ sources
            ]

            if verified:
                evidence_map[swarm] = verified

        return evidence_map

    def detect_conflicts(self, claim_id: str) -> Optional[Dict]:
        """
        Find contradictions across swarms (Popperian falsifiability)
        Returns: {type: "contradiction", swarms: [...], severity: "high"}
        """
        evidence_map = self.map_evidence(claim_id)

        # Check for conflicting confidence scores
        confidences = {}
        for swarm, citations in evidence_map.items():
            confidences[swarm] = self.aggregate_confidence(citations)

        # Flag if variance > 20% (indicates disagreement)
        if max(confidences.values()) - min(confidences.values()) > 0.2:
            return {
                "type": "conflict",
                "claim_id": claim_id,
                "swarms": list(confidences.keys()),
                "confidences": confidences,
                "severity": "high",
                "action": "ESCALATE"  # Force human review
            }

        return None

    def verify_citation_sources(self, citation_id: str) -> int:
        """Count independent sources for citation (Vienna Circle)"""
        citation = self.citation_store.get(citation_id)
        return len(citation.get("sources", []))
```

---

## Component 2: WebRTC/SIP/H.323 Transport Integration

### 2.1 Architecture Overview

**Three-lane design:**

1. **Signaling Plane**: SIP proxies + H.323 gatekeepers (session management)
2. **Media Plane**: WebRTC (audio/video/DataChannels for IF frames)
3. **IF Substrate**: IF.guard gates admission, IF.witness logs artifacts

### 2.2 Identity and Admission Control

**SIP REGISTER → IF.guard Gate:**

```python
class IFSIPProxy:
    """SIP proxy with IF.guard admission control"""

    def handle_register(self, sip_request: SIPRequest):
        """
        SIP REGISTER → IF.guard check → Accept/Reject
        """
        agent_id = sip_request.from_uri  # sip:legal-1@infrafabric.local

        # Query IF.guard: Is this agent authorized?
        guard_decision = self.if_guard.check_admission(
            agent_id=agent_id,
            resource="rtc_session",
            context={
                "sip_user_agent": sip_request.headers["User-Agent"],
                "ip_address": sip_request.source_ip
            }
        )

        if guard_decision["decision"] == "approve":
            # Generate SIP credentials
            credentials = self.generate_sip_credentials(agent_id)
            return SIPResponse(200, "OK", credentials=credentials)
        else:
            # Reject registration
            return SIPResponse(403, "Forbidden", reason=guard_decision["rationale"])
```

**H.323 RAS (Registration, Admission, Status):**

```python
class IFH323Gatekeeper:
    """H.323 gatekeeper with enterprise admission control"""

    def handle_admission_request(self, arq: AdmissionRequest):
        """
        H.323 ARQ → IF.guard check → Accept/Reject
        Enforces quotas, usage limits, concurrent session caps
        """
        agent_id = arq.endpoint_identifier

        # Check IF.guard policy
        guard_decision = self.if_guard.check_admission(
            agent_id=agent_id,
            resource="h323_conference",
            context={
                "bandwidth_requested": arq.bandwidth,
                "call_type": arq.call_type,  # audio-only, video, data
                "destination": arq.destination_info
            }
        )

        if guard_decision["decision"] == "approve":
            # Allocate bandwidth, assign MCU if multipoint
            return AdmissionConfirm(
                call_id=arq.call_id,
                bandwidth=arq.bandwidth,
                mcu_address="mcu.infrafabric.local" if arq.multipoint else None
            )
        else:
            # Reject admission
            return AdmissionReject(
                reason=guard_decision["rationale"],
                alternate_gatekeeper=None
            )
```

### 2.3 ESCALATE → WebRTC Call Flow

**Scenario:** Legal agent finds $520M settlement uncertainty → ESCALATE → Calls human expert

```python
class IFEscalateHandler:
    """Transforms ESCALATE performative into WebRTC call"""

    def handle_escalate(self, message: IFMessage):
        """
        ESCALATE message → SIP INVITE → WebRTC offer → Human answers
        """
        # Extract escalation context
        claim = message.content["claim"]
        confidence = message.content.get("confidence", 0.0)
        hazard = message.get("hazard", {})

        # Determine escalation target (human expert)
        expert = self.route_escalation(
            domain=message.scope["domain"],  # "legal"
            hazard_type=hazard.get("type"),  # "legal"
            severity=hazard.get("severity")  # "high"
        )  # Returns: sip:legal-expert@infrafabric.local

        # Create SIP INVITE with SDP offer (WebRTC)
        sdp_offer = self.create_webrtc_offer(
            audio=True,
            video=True,
            data_channel=True  # For live evidence streaming
        )

        sip_invite = SIPRequest(
            method="INVITE",
            request_uri=expert,
            from_uri=f"sip:{message.sender}",
            to_uri=expert,
            sdp=sdp_offer,
            headers={
                "Subject": f"ESCALATE: {claim}",
                "X-IF-Confidence": str(confidence),
                "X-IF-Hazard-Type": hazard.get("type"),
                "X-IF-Trace-ID": message.trace_id
            }
        )

        # Send INVITE via SIP proxy
        response = self.sip_proxy.send(sip_invite)

        if response.status_code == 200:  # Expert answered
            # Establish WebRTC peer connection
            sdp_answer = response.sdp
            peer_connection = self.establish_webrtc(sdp_offer, sdp_answer)

            # Stream live evidence via DataChannel
            data_channel = peer_connection.create_data_channel("evidence")
            self.stream_citations(data_channel, message.citation_ids)

            # Log session to IF.witness
            self.if_witness.log_escalation(
                message_id=message.trace_id,
                expert=expert,
                session_id=peer_connection.session_id,
                timestamp=datetime.utcnow()
            )

            return {"status": "connected", "session_id": peer_connection.session_id}
        else:
            # Expert unavailable → Fallback to async escalation
            return {"status": "failed", "reason": response.reason_phrase}

    def stream_citations(self, data_channel, citation_ids: List[str]):
        """Stream citations to human expert in real-time"""
        for cit_id in citation_ids:
            citation = self.citation_store.get(cit_id)

            # Send via DataChannel (JSON)
            data_channel.send(json.dumps({
                "type": "citation",
                "citation_id": cit_id,
                "claim": citation["claim_id"],
                "sources": citation["sources"],
                "rationale": citation["rationale"],
                "confidence": citation.get("confidence")
            }))
```

### 2.4 Multipoint Deliberation (IF.guard Council)

**Use Case:** 15-agent IF.guard council deliberates via video conference

```python
class IFMultipointConference:
    """H.323 MCU for IF.guard council video deliberations"""

    def create_council_conference(self, proposal_id: str, guardians: List[str]):
        """
        Create multipoint video conference for Guardian council
        Uses H.323 MCU (Multipoint Control Unit)
        """
        # Request MCU resources from gatekeeper
        arq = AdmissionRequest(
            endpoint_identifier="if-guard-coordinator",
            call_type="video",
            bandwidth=2048,  # kbps (2 Mbps for 15 participants)
            multipoint=True,
            max_participants=15
        )

        acf = self.gatekeeper.handle_admission_request(arq)

        if isinstance(acf, AdmissionConfirm):
            # Create conference on MCU
            conference = MCUConference(
                conference_id=proposal_id,
                mcu_address=acf.mcu_address,
                max_participants=15,
                recording_enabled=True,  # IF.witness requirement
                layout="voice-activated"  # Active speaker highlighted
            )

            # Invite each Guardian via SIP
            for guardian in guardians:
                sip_invite = SIPRequest(
                    method="INVITE",
                    request_uri=f"sip:{guardian}@infrafabric.local",
                    from_uri="sip:if-guard@infrafabric.local",
                    sdp=conference.get_sdp_offer(),
                    headers={
                        "Subject": f"Council Vote: {proposal_id}",
                        "X-IF-Proposal-ID": proposal_id,
                        "X-IF-Conference-ID": conference.conference_id
                    }
                )

                self.sip_proxy.send(sip_invite)

            # Stream proposal evidence to all participants via DataChannel
            self.stream_proposal_to_conference(conference, proposal_id)

            return conference
        else:
            raise AdmissionError(acf.reason)

    def stream_proposal_to_conference(self, conference: MCUConference, proposal_id: str):
        """Stream proposal + evidence to all conference participants"""
        proposal = self.if_guard.get_proposal(proposal_id)

        # Broadcast via MCU data channel
        conference.broadcast_data({
            "type": "proposal",
            "proposal_id": proposal_id,
            "title": proposal["title"],
            "description": proposal["description"],
            "evidence": proposal["evidence"],
            "risks": proposal["risks"],
            "benefits": proposal["benefits"]
        })
```

---

## Implementation Plan

### Phase 1: Swarp v4* Message Hardening (Weeks 1-3)

**Week 1: Schema Enhancement**
- [ ] Add v2.1 fields to IFMessage schema (nonce, ttl, scope, topic_hash, hazard)
- [ ] Update message signing to include new fields
- [ ] Create schema validator with v2.1 support
- [ ] Backfill existing messages with default values

**Week 2: Policy-First Routing**
- [ ] Implement hazard-based ESCALATE logic
- [ ] Refactor confidence gating (reorder ESCALATE before HOLD)
- [ ] Add unit tests for ESCALATE bug fix
- [ ] Create hazard tag taxonomy (legal, safety, conflict, ethical)

**Week 3: Cross-Swarm Relation Agent**
- [ ] Implement CrossSwarmRelationAgent class
- [ ] Build citation graph (NetworkX)
- [ ] Add conflict detection (>20% variance → ESCALATE)
- [ ] Integrate with existing IF.citation service

### Phase 2: WebRTC/SIP/H.323 Transport (Weeks 4-8)

**Week 4: SIP Proxy + IF.guard Integration**
- [ ] Deploy Kamailio/OpenSIPS SIP proxy
- [ ] Implement IF.guard admission hooks (REGISTER/INVITE)
- [ ] Generate SIP credentials for agents
- [ ] Test SIP REGISTER → IF.guard → Accept/Reject flow

**Week 5: WebRTC Peer Connections**
- [ ] Integrate aiortc (Python WebRTC library)
- [ ] Implement STUN/TURN servers (NAT traversal)
- [ ] Create WebRTC offer/answer handlers
- [ ] Add DataChannel support for IF frames

**Week 6: ESCALATE → Call Flow**
- [ ] Implement IFEscalateHandler
- [ ] Map ESCALATE → SIP INVITE
- [ ] Route escalations to human experts
- [ ] Stream citations via DataChannel
- [ ] Log sessions to IF.witness

**Week 7: H.323 Gatekeeper + MCU**
- [ ] Deploy H.323 gatekeeper (GNU Gatekeeper or Cisco)
- [ ] Implement admission control (quotas, bandwidth)
- [ ] Configure MCU for multipoint conferences
- [ ] Test IF.guard council video deliberations

**Week 8: Integration + Testing**
- [ ] End-to-end test: Message → ESCALATE → WebRTC call → Human response
- [ ] Load test: 15-agent council conference
- [ ] Security audit: DTLS-SRTP, SIP TLS
- [ ] Documentation: RFC, runbooks, diagrams

### Phase 3: Production Rollout (Weeks 9-10)

**Week 9: Staging Deployment**
- [ ] Deploy SIP proxy, H.323 gatekeeper, TURN servers
- [ ] Enable v2.1 schema in staging swarm
- [ ] Test with V4 Epic Intelligence Dossier workflow
- [ ] Monitor hazard escalations, call success rate

**Week 10: Production Deployment**
- [ ] Enable v2.1 schema in production
- [ ] Activate WebRTC/SIP/H.323 transport
- [ ] Migrate existing workflows to hazard-first routing
- [ ] Document lessons learned

---

## Security Considerations

### Message Layer (Swarp v4*)

**Threat Model:**
- ✅ Confidence manipulation → Mitigated by hazard tags (bypass confidence gates)
- ✅ Scope collisions → Mitigated by scope metadata + topic_hash
- ✅ False conflicts → Mitigated by cross-swarm relation agent
- ✅ Replay attacks → Mitigated by nonce + ttl + existing sequence numbers

**New Attack Surfaces:**
- ⚠️ Hazard tag abuse (agents spam "legal" to force escalations)
  - **Mitigation**: IF.guard audits hazard frequency, penalizes abuse
- ⚠️ Nonce collision (birthday paradox with 96-bit nonces)
  - **Mitigation**: 2^96 nonces = 10^28, collision risk negligible

### Transport Layer (WebRTC/SIP/H.323)

**Threat Model:**
- ✅ Eavesdropping → Mitigated by DTLS-SRTP (WebRTC), TLS (SIP)
- ✅ MITM → Mitigated by certificate pinning, IF.guard credential validation
- ✅ DoS (SIP flooding) → Mitigated by H.323 admission control, rate limiting
- ✅ Unauthorized access → Mitigated by IF.guard gates on REGISTER/INVITE

**New Attack Surfaces:**
- ⚠️ WebRTC ICE candidate poisoning (malicious STUN servers)
  - **Mitigation**: Whitelist STUN/TURN servers, validate via HMAC
- ⚠️ SIP INVITE replay (reuse old INVITE to initiate calls)
  - **Mitigation**: SIP nonces, timestamp validation (same as IFMessage)

---

## Performance Impact

### Message Layer Overhead

**Swarp v4* additions:**
- Nonce generation: ~0.1 ms (random.getrandbits(96))
- Scope + hazard serialization: ~0.2 ms (JSON)
- Topic hash: ~1 ms (SHA-256)
- **Total: ~1.3 ms per message** (negligible compared to AI inference ~500ms)

### Transport Layer Overhead

**WebRTC/SIP/H.323:**
- SIP REGISTER: ~50 ms (round-trip to proxy)
- WebRTC ICE negotiation: ~200-500 ms (NAT traversal)
- DataChannel latency: ~10-50 ms (peer-to-peer, after connection)
- H.323 admission: ~100 ms (gatekeeper round-trip)

**Acceptable for:**
- ESCALATE calls (human-in-loop, ~1-2 sec acceptable)
- Council conferences (setup time <5 sec acceptable)

**NOT acceptable for:**
- High-frequency agent messaging (use existing DDS/gRPC)
- Low-latency CRDT updates (use existing CRDT layer)

---

## Testing Strategy

### Unit Tests

**Message Layer:**
- [ ] Test nonce uniqueness (1M messages, no collisions)
- [ ] Test TTL expiration (reject messages >300s old)
- [ ] Test hazard-first routing (hazard bypasses confidence gates)
- [ ] Test scope isolation (parallel workflows don't conflict)

**Transport Layer:**
- [ ] Test SIP REGISTER → IF.guard → Accept
- [ ] Test SIP REGISTER → IF.guard → Reject (unauthorized agent)
- [ ] Test WebRTC offer/answer (SDP negotiation)
- [ ] Test DataChannel message delivery

### Integration Tests

- [ ] Full flow: Legal agent finds issue → hazard tag → ESCALATE → SIP INVITE → WebRTC call → Human responds
- [ ] Cross-swarm: Finance cites $520M → Legal contradicts $500M → Conflict detected → Relation agent escalates
- [ ] Multipoint: 15 Guardians join H.323 conference → Deliberate on proposal → Vote recorded

### Load Tests

- [ ] 100 concurrent SIP registrations (test admission control)
- [ ] 50 concurrent WebRTC peer connections (test TURN server)
- [ ] 15-participant H.323 conference (test MCU capacity)

---

## Rollback Plan

**If issues arise during rollout:**

1. **Message Layer (Swarp v4*):**
   - Revert schema to v2.0 (remove nonce, ttl, scope, hazard)
   - Revert ESCALATE logic to v2 (confidence-first, accepts bug)
   - Disable cross-swarm relation agent

2. **Transport Layer (WebRTC/SIP/H.323):**
   - Disable SIP proxy (fall back to DDS/gRPC)
   - Disable WebRTC (ESCALATE becomes async-only)
   - Disable H.323 gatekeeper (council uses existing video tools)

**Rollback triggers:**
- Security incident (credential leak, DoS attack)
- Performance degradation (>10% latency increase)
- Data integrity issue (message corruption, citation tampering)

---

## Success Metrics

### Message Layer (Swarp v4*)

- **Hazard detection rate**: >90% of legal/safety issues flagged
- **False positive rate**: <5% of hazard tags are spurious
- **Conflict detection**: >95% of cross-swarm contradictions caught
- **ESCALATE bug fix**: 0% critical issues buried by HOLD gate

### Transport Layer (WebRTC/SIP/H.323)

- **Call success rate**: >95% of ESCALATE → SIP INVITE → Answered
- **Connection latency**: <2 seconds (ICE negotiation + connection)
- **Audio/video quality**: >90% sessions rated "good" by humans
- **Multipoint capacity**: 15+ participants with <200ms audio lag

---

## Future Enhancements

### Phase 4: Advanced Features (Post-Launch)

1. **Recording + Transcription**:
   - Record all ESCALATE calls (IF.witness audit)
   - Transcribe audio → Citations (Whisper API)
   - Link human responses to evidence graph

2. **Sentiment Analysis**:
   - Analyze human expert tone during calls (concern, confidence)
   - Adjust agent confidence calibration based on expert reactions

3. **Screen Sharing**:
   - Agents share visualizations (charts, evidence tables) during calls
   - Use WebRTC video track for screen sharing

4. **Federation**:
   - Cross-organization ESCALATE calls (Company A agent → Company B expert)
   - SIP trunking, H.323 gatekeeper federation

---

## Conclusion

This RFC proposes a **two-layer enhancement** to InfraFabric communication:

1. **Swarp v4* (Message Layer)**: Hardens schema, fixes ESCALATE bug, adds cross-swarm evidence mapping
2. **WebRTC/SIP/H.323 (Transport Layer)**: Enables real-time human-in-loop, live evidence streaming

**Both are required** to achieve production-grade agent communication. Implementing **Swarp v4* first** (Weeks 1-3) provides immediate security benefits, then **WebRTC/SIP/H.323** (Weeks 4-8) unlocks real-time capabilities.

**Estimated Timeline**: 10 weeks (3 weeks schema + 5 weeks transport + 2 weeks rollout)

**Risk**: Low (both layers are additive, rollback plan in place)

**Recommendation**: **APPROVE** for implementation

---

**RFC Status**: DRAFT → Review → Approve → Implement
**Next Steps**: Review with user, refine timeline, assign implementation teams

**Citation**:
```json
{
  "citation_id": "if://citation/rfc-comm-layer-2025-11-11",
  "claim_id": "if://claim/swarp-v4-webrtc-integration",
  "sources": [
    {"type": "proposal", "ref": "media-standard-integration-sip-webtrc-h232.txt", "hash": "sha256:PENDING"},
    {"type": "proposal", "ref": "swarp-update.txt", "hash": "sha256:PENDING"},
    {"type": "review", "ref": "the gemini review.txt", "hash": "sha256:PENDING"}
  ],
  "rationale": "RFC integrating Swarp v4* message hardening and WebRTC/SIP/H.323 transport for production-ready agent communication",
  "status": "draft",
  "created_by": "if://agent/claude-sonnet-4.5",
  "created_at": "2025-11-11T12:00:00Z"
}
```
