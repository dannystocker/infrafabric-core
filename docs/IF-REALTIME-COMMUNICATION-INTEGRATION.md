# IF.connect Real-Time Communication Integration
**Version:** 2.1
**Date:** 2025-11-11
**Status:** Architecture Specification
**Philosophy Grounding:** Wu Lun (五倫), Vienna Circle, Ubuntu, Kantian Duty

---

## Executive Summary

This document integrates real-time communication protocols (NDI, H.323, SIP, WebRTC) into InfraFabric's IF.connect architecture, enabling:

1. **IF.ESCALATE → Voice/Video Calls**: Transform hazard escalations into real-time human deliberation
2. **IF.witness → Live Evidence Streams**: Stream verification data via NDI for audit
3. **IF.guard → Council Conferencing**: Multi-participant governance via H.323 MCU
4. **IF.swarm → Agent Mesh**: WebRTC DataChannels for peer-to-peer agent coordination

**Key Innovation:** Philosophy-grounded real-time communication where every media stream, every call, every escalation maintains IF.TTT (Traceable, Transparent, Trustworthy) principles.

---

## Architecture Mapping

### Level 2: Cellular (Service → Service) — Media Transport

**Purpose:** Raw media streaming between IF.* services

#### NDI Integration (Network Device Interface)

**Use Case:** Live evidence streaming for IF.witness audit trails

**Philosophy:**
- **IF.ground**: Observable, verifiable media streams
- **Wu Lun (父子)**: Generational relationship — NDI sender (parent) creates stream, receivers (children) consume asynchronously

**Technical Mapping:**

```yaml
# NDI Service Discovery → IF.connect
ndi_discovery:
  method: mDNS  # Port 5353 UDP
  service_name: "IF.witness.evidence-stream._ndi._tcp"
  discovery_server: "if://service/ndi/discovery:5959"  # Optional centralized

ndi_transport:
  protocol: "Reliable UDP v5"  # NDI's current standard
  ports:
    base_tcp: 5960
    base_udp: 5960
    multipath_tcp: 6960  # For multi-NIC throughput
    multipath_udp: 7960

  # Bandwidth profiles for evidence streaming
  profiles:
    high_bandwidth:  # SpeedHQ codec
      resolution: "1080p60"
      bitrate_mbps: 132.14
      use_case: "Critical security footage, live demos"

    hx_compressed:  # H.265 codec
      resolution: "1080p60"
      bitrate_mbps: 10.99
      use_case: "Standard evidence recording"

    proxy:  # Low-bandwidth proxy
      resolution: "640x360@30p"
      bitrate_mbps: 3.99
      use_case: "Remote witness verification"

# IF.connect integration
if_ndi_bridge:
  component: "IF.witness.ndi-publisher"
  publishes:
    - stream_id: "if://media/witness/yologuard-scan-01"
      ndi_name: "IF.yologuard Scanner 01"
      format: "NDI HX h.265 1080p60"
      metadata:
        trace_id: "a2f9c3b8d1e5"
        witness_hash_chain: "sha256:..."
        signed_by: "ed25519:AAAC3NzaC1..."

  subscribers:
    - "IF.guard"  # Guardian review of detection process
    - "IF.audit"  # Compliance recording
    - "IF.optimise"  # Performance monitoring
```

**Anti-Replay Protection:**
```python
# NDI stream metadata injection (custom metadata packets)
def publish_ndi_with_witness(stream_id: str, frame: np.ndarray):
    """Inject IF.witness hash chain into NDI metadata"""

    # Generate witness signature
    witness_entry = {
        'frame_number': frame_count,
        'timestamp': time.time_ns(),
        'content_hash': hashlib.sha256(frame.tobytes()).hexdigest(),
        'prev_hash': last_witness_hash,
        'stream_id': stream_id,
        'trace_id': current_trace_id
    }

    # Sign with Ed25519
    signature = sign_ed25519(witness_entry, private_key)
    witness_entry['signature'] = signature

    # Inject as NDI metadata (follows NDI SDK metadata API)
    ndi_metadata = ndi.Metadata(
        timecode=frame_count,
        data=json.dumps(witness_entry)
    )

    # Send frame + metadata
    ndi_send.send_video(ndi.VideoFrame(frame), metadata=ndi_metadata)

    return witness_entry['content_hash']
```

**Network Requirements:**
- **Minimum:** 1 Gbps full-duplex (NDI whitepaper recommendation)
- **IGMP:** Enable for multicast optimization
- **QoS:** Configure for low-latency (< 16 scan lines technical latency)

---

#### H.323 Integration (Packet-Based Multimedia)

**Use Case:** IF.guard Guardian council video conferencing, IF.ESCALATE human deliberation

**Philosophy:**
- **Ubuntu**: Consensus through communal deliberation (MCU = digital council chamber)
- **Kantian Duty**: Ethical constraints on who can join, what can be recorded
- **Wu Lun (君臣)**: Hierarchical relationship — Gatekeeper (ruler) grants admission, terminals (subjects) participate

**Technical Mapping:**

```yaml
# H.323 Components → IF.connect
h323_architecture:
  gatekeeper:
    component: "IF.guard.h323-gatekeeper"
    role: "Admission control, address translation, bandwidth management"
    address: "if://service/guard/gatekeeper:1719"  # RAS port
    philosophy: "Kantian duty gates — only registered guardians admitted"

    zones:
      - zone_id: "if://zone/guard/council"
        members:
          - "IF.guard.terminal.sage"
          - "IF.guard.terminal.skeptic"
          - "IF.guard.terminal.ethicist"
        bandwidth_limit: "10 Mbps per terminal"
        auth_method: "Ed25519 digital signatures"

  mcu:  # Multipoint Control Unit
    component: "IF.guard.h323-mcu"
    role: "Mix audio/video from N terminals → N outputs (everyone sees everyone)"
    address: "if://service/guard/mcu:1720"
    capabilities:
      max_participants: 25  # Guardian quorum + escalated agents
      audio_mixing: "Centralized (MP mixes all streams)"
      video_switching: "Continuous presence (4x4 grid)"
      data_channels: "T.120 for shared whiteboards (evidence display)"

    philosophy: "Indra's Net — every participant reflects every other"

  gateway:
    component: "IF.connect.h323-sip-gateway"
    role: "Bridge H.323 (IF.guard internal) ↔ SIP (external experts)"
    address: "if://service/connect/gateway:1720"
    philosophy: "Access gateway connecting internal council to external advisors"

# Call flow for IF.ESCALATE → Human deliberation
escalate_to_h323_call:
  trigger: "IFMessage with hazard=['legal'] and routing=ESCALATE"

  steps:
    - action: "IF.guard receives ESCALATE message"
      details: "Hazard: legal liability (revenue conflict buried)"

    - action: "IF.guard.gatekeeper sends ARQ (Admission Request)"
      participants:
        - "if://guardian/sage"
        - "if://guardian/skeptic"
        - "if://guardian/ethicist"
        - "if://agent/swarm/legal-1"  # Escalating agent
        - "if://agent/swarm/finance-1"  # Conflicting agent

    - action: "Gatekeeper validates credentials"
      checks:
        - "Ed25519 signature verification"
        - "Registry: participant in IF.guard roster"
        - "Bandwidth: ≤10 Mbps per terminal"
        - "Kantian duty: No PII in this call type"

    - action: "Gatekeeper sends ACF (Admission Confirm)"
      grants:
        - call_id: "if://call/escalate/2025-11-11-xyz"
        - mcu_address: "if://service/guard/mcu:1720"
        - bandwidth: "384 kbps per stream (H.264 video + G.722 audio)"

    - action: "Terminals connect to MCU"
      protocol: "H.245 for capability exchange, logical channels"

    - action: "MCU mixes streams, logs to IF.witness"
      witness_log:
        - event: "call_started"
          participants: [...]
          timestamp: "2025-11-11T14:32:17Z"
          trace_id: "a2f9c3b8d1e5"

        - event: "decision_recorded"
          decision: "approve_with_conditions"
          rationale: "Legal risk mitigated by disclosure"
          vote_tally: "3 approve, 0 reject, 0 abstain"
          witness_hash: "sha256:..."
          signature: "ed25519:..."
```

**H.323 Ports:**
```
1719/UDP: RAS (Registration, Admission, Status) — Gatekeeper signaling
1720/TCP: H.225.0 Call Signaling — Setup, teardown
Dynamic TCP: H.245 Control Channel — Capability exchange, logical channels
Dynamic UDP: RTP/RTCP — Media streams
```

**Security Layer:**
```python
# IF.guard gatekeeper admission control
def h323_admission_request(arq: AdmissionRequest) -> AdmissionResponse:
    """
    Kantian duty gate: verify identity, check policy, grant/deny admission
    """
    terminal_id = arq.terminal_id  # e.g., "if://guardian/sage"

    # 1. Verify Ed25519 signature
    if not verify_signature(arq.signature, terminal_id):
        return AdmissionReject(reason="INVALID_SIGNATURE")

    # 2. Check registry (prevent sybil)
    if not guardian_registry.is_registered(terminal_id):
        return AdmissionReject(reason="NOT_REGISTERED")

    # 3. Check Kantian constraints
    if arq.call_type == "ESCALATE" and arq.has_pii:
        return AdmissionReject(reason="PII_POLICY_VIOLATION")

    # 4. Check bandwidth quota
    if arq.bandwidth_bps > 10_000_000:
        return AdmissionReject(reason="BANDWIDTH_EXCEEDED")

    # 5. Grant admission
    call_id = generate_uuidv7()
    witness.log({
        'event': 'h323_admission',
        'terminal_id': terminal_id,
        'call_id': call_id,
        'timestamp': time.time_ns(),
        'trace_id': arq.trace_id
    })

    return AdmissionConfirm(
        call_id=call_id,
        mcu_address="if://service/guard/mcu:1720",
        bandwidth_granted=arq.bandwidth_bps
    )
```

---

#### SIP Integration (Session Initiation Protocol)

**Use Case:** IF.ESCALATE → External expert calls, IF.connect federation signaling

**Philosophy:**
- **Wu Lun (朋友)**: Friend relationship — SIP peers are equals
- **Popper**: Falsifiability — external experts provide contrarian views
- **IF.ground**: Observable call setup (SIP is text-based, fully auditable)

**Technical Mapping:**

```yaml
# SIP Components → IF.connect
sip_architecture:
  proxy:
    component: "IF.connect.sip-proxy"
    role: "Route SIP requests, enforce policy, log to IF.witness"
    address: "sip:proxy.infrafabric.local:5060"

    routing_rules:
      - pattern: "sip:.*@if.guard.local"
        action: "Forward to IF.guard registrar"
        policy: "Require Ed25519 auth"

      - pattern: "sip:expert-.*@external.advisor"
        action: "Forward to SIP-H.323 gateway"
        policy: "IF.guard approval required"

  registrar:
    component: "IF.connect.sip-registrar"
    role: "Register agent/guardian SIP endpoints"
    address: "sip:registrar.infrafabric.local:5060"

    registry:
      - uri: "sip:guardian-sage@if.guard.local"
        contact: "sip:10.0.1.50:5060"
        pubkey: "ed25519:AAAC3NzaC1..."

      - uri: "sip:agent-legal-1@if.swarm.local"
        contact: "sip:10.0.2.30:5060"
        pubkey: "ed25519:BBBD4OzaC2..."

# IF.ESCALATE → SIP INVITE flow
escalate_to_sip_call:
  trigger: "IFMessage with hazard=['safety'] and routing=ESCALATE"

  sip_invite:
    from: "sip:agent-safety-1@if.swarm.local"
    to: "sip:expert-risk-analyst@external.advisor"
    subject: "ESCALATE: Drone coordination safety hazard"

    sdp_offer:  # Session Description Protocol
      media:
        - type: audio
          codec: G.722
          port: 10000
        - type: video
          codec: H.264
          port: 10002
        - type: application  # WebRTC DataChannel for evidence
          codec: "webrtc-datachannel"
          port: 10004

    custom_headers:
      X-IF-Trace-ID: "a2f9c3b8d1e5"
      X-IF-Hazard: "safety"
      X-IF-Witness-Hash: "sha256:..."
      X-IF-Signature: "ed25519:..."

  policy_gate:
    component: "IF.guard"
    decision: "Approve if external expert is in trusted advisor registry"
    log: "IF.witness records SIP INVITE + SDP + decision"
```

**SIP Message Example with IF.witness:**
```
INVITE sip:expert-risk-analyst@external.advisor SIP/2.0
Via: SIP/2.0/UDP 10.0.2.30:5060;branch=z9hG4bK776asdhds
From: <sip:agent-safety-1@if.swarm.local>;tag=1928301774
To: <sip:expert-risk-analyst@external.advisor>
Call-ID: if-escalate-2025-11-11-xyz@10.0.2.30
CSeq: 314159 INVITE
Contact: <sip:agent-safety-1@10.0.2.30:5060>
Content-Type: application/sdp
X-IF-Trace-ID: a2f9c3b8d1e5
X-IF-Hazard: safety
X-IF-Witness-Hash: sha256:5a3d2f8c1b9e7d6a4f3e2c1b0a9d8e7f
X-IF-Signature: ed25519:m8QKz5X3jP...

v=0
o=IF.swarm 2890844526 2890842807 IN IP4 10.0.2.30
s=ESCALATE: Drone coordination safety hazard
c=IN IP4 10.0.2.30
t=0 0
m=audio 10000 RTP/AVP 9
a=rtpmap:9 G722/8000
m=video 10002 RTP/AVP 99
a=rtpmap:99 H264/90000
m=application 10004 UDP/DTLS/SCTP webrtc-datachannel
```

---

#### WebRTC Integration (Web Real-Time Communication)

**Use Case:** IF.swarm agent mesh, browser-based IF.guard UI, peer-to-peer evidence exchange

**Philosophy:**
- **Wu Lun (兄弟)**: Sibling relationship — WebRTC peers are parallel, coordinated
- **Indra's Net**: Peer-to-peer mesh where every node reflects every other
- **IF.ground**: Verifiable signaling (SDP + ICE negotiation logged)

**Technical Mapping:**

```yaml
# WebRTC Components → IF.connect
webrtc_architecture:
  signaling_server:
    component: "IF.connect.webrtc-signal"
    role: "Exchange SDP offers/answers + ICE candidates"
    protocol: "WebSocket over TLS"
    address: "wss://signal.infrafabric.local:8443"

    philosophy: "Transparent signaling — every SDP logged to IF.witness"

  turn_server:  # Traversal Using Relays around NAT
    component: "IF.connect.turn"
    role: "Relay media when peer-to-peer fails (firewalls, NAT)"
    address: "turn:relay.infrafabric.local:3478"
    auth: "HMAC-SHA1 with short-term credentials"

  stun_server:  # Session Traversal Utilities for NAT
    component: "IF.connect.stun"
    role: "Help agents discover their public IP:port"
    address: "stun:stun.infrafabric.local:3478"

# IF.swarm agent mesh via WebRTC DataChannels
swarm_webrtc_mesh:
  agents:
    - agent_id: "if://agent/swarm/finance-1"
      peer_id: "finance-1-webrtc"
      capabilities: ["data", "audio"]  # No video (agents don't have cameras)

    - agent_id: "if://agent/swarm/legal-1"
      peer_id: "legal-1-webrtc"
      capabilities: ["data", "audio"]

    - agent_id: "if://agent/swarm/macro-1"
      peer_id: "macro-1-webrtc"
      capabilities: ["data"]

  datachannel_config:
    label: "if-agent-messaging"
    protocol: "sctp"  # Stream Control Transmission Protocol
    ordered: true
    max_retransmits: 3

    # IFMessage v2.1 sent over DataChannel
    message_format:
      transport: "WebRTC DataChannel"
      encoding: "JSON"
      compression: "brotli"  # Optional for large evidence

      # Every message still has Ed25519 signature
      signature_required: true

# SDP offer/answer flow (with IF.witness logging)
webrtc_sdp_exchange:
  peer_a: "if://agent/swarm/finance-1"
  peer_b: "if://agent/swarm/legal-1"

  steps:
    - action: "Peer A generates SDP offer"
      sdp:
        type: offer
        media:
          - type: application
            protocol: UDP/DTLS/SCTP
            port: 9
            datachannel: "if-agent-messaging"
        ice_candidates:
          - "candidate:1 1 UDP 2122260223 10.0.2.30 50000 typ host"
          - "candidate:2 1 UDP 1686052607 203.0.113.5 50000 typ srflx"

      witness_log:
        event: "webrtc_offer_created"
        peer: "finance-1"
        trace_id: "a2f9c3b8d1e5"
        sdp_hash: "sha256:..."

    - action: "Signaling server forwards offer to Peer B"
      protocol: "WebSocket message"
      logged: true

    - action: "Peer B generates SDP answer"
      sdp:
        type: answer
        media:
          - type: application
            protocol: UDP/DTLS/SCTP
            port: 9
            datachannel: "if-agent-messaging"
        ice_candidates:
          - "candidate:1 1 UDP 2122260223 10.0.3.20 60000 typ host"

      witness_log:
        event: "webrtc_answer_created"
        peer: "legal-1"
        trace_id: "a2f9c3b8d1e5"
        sdp_hash: "sha256:..."

    - action: "ICE negotiation completes, DataChannel opens"
      witness_log:
        event: "webrtc_datachannel_open"
        peers: ["finance-1", "legal-1"]
        connection_type: "direct"  # or "relayed" via TURN
```

**WebRTC DataChannel Security:**
```javascript
// Agent-to-agent WebRTC setup with IF.witness logging
class IFAgentWebRTC {
  constructor(agentId, privateKey) {
    this.agentId = agentId;
    this.privateKey = privateKey;  // Ed25519
    this.pc = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.infrafabric.local:3478' },
        { urls: 'turn:relay.infrafabric.local:3478',
          username: 'if-agent',
          credential: 'generated-hmac' }
      ]
    });

    this.dataChannel = null;
  }

  async createOffer() {
    // Create DataChannel
    this.dataChannel = this.pc.createDataChannel('if-agent-messaging', {
      ordered: true,
      maxRetransmits: 3
    });

    // Set up message handler
    this.dataChannel.onmessage = (event) => {
      this.handleIFMessage(JSON.parse(event.data));
    };

    // Generate SDP offer
    const offer = await this.pc.createOffer();
    await this.pc.setLocalDescription(offer);

    // Log to IF.witness
    await this.logToWitness({
      event: 'webrtc_offer_created',
      peer: this.agentId,
      sdp_hash: sha256(offer.sdp),
      trace_id: this.currentTraceId
    });

    return offer;
  }

  sendIFMessage(message) {
    // Add Ed25519 signature
    const canonical = canonicalize(message);
    const signature = ed25519.sign(canonical, this.privateKey);

    message.signature = {
      algorithm: 'ed25519',
      public_key: ed25519.getPublicKey(this.privateKey),
      signature_bytes: signature
    };

    // Send over DataChannel
    this.dataChannel.send(JSON.stringify(message));

    // Log to IF.witness
    this.logToWitness({
      event: 'ifmessage_sent',
      message_id: message.id,
      receiver: message.receiver,
      performative: message.performative,
      signature_hash: sha256(signature)
    });
  }

  handleIFMessage(message) {
    // Verify Ed25519 signature
    const verified = ed25519.verify(
      message.signature.signature_bytes,
      canonicalize(message),
      message.signature.public_key
    );

    if (!verified) {
      console.error('Signature verification failed!');
      this.logToWitness({
        event: 'ifmessage_rejected',
        reason: 'INVALID_SIGNATURE',
        message_id: message.id
      });
      return;
    }

    // Process message...
  }
}
```

---

### Level 3: Organism (IF.module → IF.module) — Coordination Layer

**Philosophy:** Wu Lun relationships applied to real-time communication

```yaml
# IF.connect v2.1 with real-time transport mappings
if_message_v21_realtime:
  id: "msg-uuidv7"
  performative: "escalate"  # ESCALATE triggers real-time call
  conversation_id: "conv-uuidv7"
  topic_hash: "sha256:..."

  sender: "if://agent/swarm/legal-1"
  receiver: "if://service/guard/council"

  # Hazard tags trigger specific transport
  hazards: ["legal"]
  routing_decision: "ESCALATE"

  # Real-time transport selection
  realtime_transport:
    protocol: "h323"  # or "sip", "webrtc"
    reason: "hazard=legal requires Guardian council video deliberation"

    h323_call_setup:
      gatekeeper: "if://service/guard/gatekeeper:1719"
      mcu: "if://service/guard/mcu:1720"
      participants:
        - "sip:guardian-sage@if.guard.local"
        - "sip:guardian-skeptic@if.guard.local"
        - "sip:guardian-ethicist@if.guard.local"
        - "sip:agent-legal-1@if.swarm.local"  # Escalating agent

      media_streams:
        - type: audio
          codec: G.722
          bitrate: 64000
        - type: video
          codec: H.264
          bitrate: 384000
        - type: data
          codec: T.120
          purpose: "Shared evidence whiteboard"

  # IF.witness logging
  witness_log:
    - event: "escalate_triggered"
      timestamp: "2025-11-11T14:32:17Z"
      trace_id: "a2f9c3b8d1e5"

    - event: "h323_call_initiated"
      call_id: "if://call/escalate/2025-11-11-xyz"
      gatekeeper_admission: "ACF"
      participants: [...]

    - event: "h323_call_ended"
      duration_seconds: 1847
      decision: "approve_with_conditions"
      vote_tally: "3-0-0"
      witness_hash: "sha256:..."
      signature: "ed25519:..."
```

**Routing Decision Tree with Real-Time Transport:**

```python
def route_ifmessage_v21(message: IFMessage) -> RoutingDecision:
    """
    IF.connect v2.1 router with real-time transport selection
    Implements hazard-first routing + philosophy-grounded transport
    """

    # 1. Hard invariants (hazard-first)
    if "legal" in message.hazards or "safety" in message.hazards:
        return RoutingDecision(
            action="ESCALATE",
            transport="h323",  # Guardian council video conference
            reason="Policy: hazard category requires human deliberation",
            h323_setup={
                'gatekeeper': 'if://service/guard/gatekeeper:1719',
                'call_type': 'centralized_multipoint',
                'participants': get_guardian_council(),
                'evidence_display': 'T.120_whiteboard'
            }
        )

    if "conflict>20%" in message.hazards:
        return RoutingDecision(
            action="ESCALATE",
            transport="sip",  # External expert call
            reason="Policy: critical variance requires adjudication",
            sip_setup={
                'proxy': 'sip:proxy.infrafabric.local:5060',
                'invite_to': get_external_expert(message.domain),
                'evidence_channel': 'webrtc_datachannel'
            }
        )

    # 2. Numeric gates (normalized confidence)
    conf_norm = message.content['confidence']['normalized']

    if conf_norm < 0.2:
        return RoutingDecision(
            action="ESCALATE",
            transport="webrtc",  # Fast peer-to-peer escalation
            reason="Low confidence",
            webrtc_setup={
                'signaling_server': 'wss://signal.infrafabric.local:8443',
                'peer_agents': message.content.get('conflicting_agents', []),
                'datachannel_label': 'if-agent-escalation'
            }
        )

    elif conf_norm < 0.3:
        return RoutingDecision(
            action="HOLD",
            transport="async",  # Standard IFMessage queue
            reason="Borderline; needs second source"
        )

    # 3. Normal SHARE flow
    return RoutingDecision(
        action="SHARE",
        transport="async",
        reason="High confidence, no conflicts"
    )
```

---

### Level 4: Ecosystem (InfraFabric → InfraFabric) — Federation

**Use Case:** Multi-organization collaboration, cross-instance deliberation

**Philosophy:**
- **Indra's Net**: Planetary-scale reflection
- **Kantian Duty**: Strict privacy/sovereignty boundaries

```yaml
# Federated H.323 gateway (connect Company A ↔ Company B councils)
federation_h323:
  company_a:
    gatekeeper: "if://service/guard/gatekeeper.company-a.local:1719"
    mcu: "if://service/guard/mcu.company-a.local:1720"
    zone: "if://zone/guard/council-a"

  company_b:
    gatekeeper: "if://service/guard/gatekeeper.company-b.local:1719"
    mcu: "if://service/guard/mcu.company-b.local:1720"
    zone: "if://zone/guard/council-b"

  federation_gateway:
    component: "IF.connect.h323-federation-gateway"
    role: "Bridge Company A MCU ↔ Company B MCU"
    address: "if://service/connect/fed-gateway:1720"

    # Kantian duty constraints
    privacy_policy:
      - "No recording of federated calls without explicit consent"
      - "PII stripped from SDP/H.245 messaging"
      - "Rate-limit federated escalations (max 5/day)"
      - "Audit all cross-boundary calls to IF.witness"

    # Cryptographic federation
    auth_method: "mTLS with cross-signed certificates"
    federation_peers:
      - org: "Company B"
        cert_fingerprint: "sha256:..."
        trust_level: "high"
        allowed_hazard_types: ["legal", "conflict>20%"]  # Not "safety" (proprietary)
```

---

## Implementation Roadmap

### Week 1-2: NDI Evidence Streaming (IF.witness)

**Tasks:**
1. Install NDI SDK (https://ndi.tv/sdk/)
2. Implement `IF.witness.ndi-publisher`
   - Wrap yologuard scanner output as NDI stream
   - Inject witness hash chain into NDI metadata
3. Implement `IF.guard.ndi-viewer`
   - Subscribe to IF.witness streams
   - Verify metadata signatures in real-time
4. Test: Stream live secret scanning session to Guardian review

**Deliverable:** `docs/NDI-WITNESS-INTEGRATION.md` + Python implementation

### Week 3-4: WebRTC Agent Mesh (IF.swarm)

**Tasks:**
1. Deploy WebRTC signaling server (Janus Gateway or mediasoup)
2. Implement `IFAgentWebRTC` class (JavaScript/TypeScript)
3. Integrate with IFMessage v2.1 schema
   - DataChannel = transport for IFMessage
   - SDP logging to IF.witness
4. Test: 5-agent swarm peer-to-peer mesh, verify Ed25519 signatures

**Deliverable:** `src/communication/webrtc-agent-mesh.ts` + test suite

### Week 5-6: H.323 Guardian Council (IF.guard)

**Tasks:**
1. Deploy H.323 Gatekeeper (GNU Gatekeeper or OpenH323)
2. Deploy H.323 MCU (Jitsi Videobridge or Kurento)
3. Implement `IF.guard.h323-gatekeeper`
   - Ed25519 admission control
   - Bandwidth quotas
   - Witness logging
4. Implement `IF.guard.h323-mcu`
   - Centralized audio mixing
   - Continuous presence video
   - T.120 evidence whiteboard
5. Test: 15-guardian council call, ESCALATE trigger, decision recording

**Deliverable:** `docs/H323-GUARD-COUNCIL.md` + Python/C++ gateway

### Week 7-8: SIP External Expert Calls (IF.ESCALATE)

**Tasks:**
1. Deploy SIP proxy (Kamailio or OpenSIPS)
2. Deploy SIP registrar
3. Implement `IF.connect.sip-proxy`
   - Custom header parsing (X-IF-Trace-ID, etc.)
   - IF.guard policy gate (approve external calls)
   - Witness logging
4. Implement SIP-H.323 gateway (bridge external SIP ↔ internal H.323)
5. Test: ESCALATE → external expert call, evidence shared via WebRTC DataChannel

**Deliverable:** `src/communication/sip-escalate-gateway.py`

---

## Philosophy Grounding Summary

| Protocol | Wu Lun Relationship | Vienna Circle | Ubuntu | Kantian Duty | IF.ground |
|----------|---------------------|---------------|--------|--------------|-----------|
| **NDI**  | 父子 (parent→child) | Verifiable media hash | N/A | Witness signatures | Observable streams |
| **H.323** | 君臣 (gatekeeper→terminals) | 2+ guardians verify | Council consensus | Admission gates | Call logs |
| **SIP** | 朋友 (peer-to-peer) | Tool-verified experts | External voices | Privacy headers | Text-based (auditable) |
| **WebRTC** | 兄弟 (sibling mesh) | Peer signatures | Swarm coordination | DTLS encryption | SDP logs |

---

## Success Metrics

1. **IF.ESCALATE Latency**: Hazard detection → Human on call < 30 seconds
2. **IF.witness Coverage**: 100% of media frames have hash chain metadata
3. **IF.guard Quorum**: 15+ guardians can join H.323 MCU concurrently
4. **IF.swarm Mesh**: 8+ agents WebRTC mesh with <50ms peer-to-peer latency
5. **IF.TTT Compliance**: Every call, every stream, every escalation logged with Ed25519 signatures

---

## Next Steps

1. **User Approval**: Review this architecture, identify any missing use cases
2. **Pilot Selection**: Choose Week 1-2 (NDI) or Week 3-4 (WebRTC) for first POC
3. **Tooling Setup**: Install NDI SDK / WebRTC signaling server
4. **Code Implementation**: Begin with smallest vertical slice (e.g., NDI metadata injection)
5. **Documentation**: Expand philosophy grounding for each transport protocol

---

**References:**
- NDI 5.6 White Paper (Vizrt NDI AB, September 2023)
- H.323 Rec. ITU-T H.323 (03/2022)
- WebRTC 1.0 Specification (W3C)
- SIP RFC 3261
- IF.connect Architecture (`IF_CONNECTIVITY_ARCHITECTURE.md`)
- IF.witness Paper (`docs/papers/IF-witness.md`)
- Philosophy Database r4 (`docs/evidence/gemini-logs/core/IF.philosophy-database-r4.yaml`)

---

**Citation:**
`if://doc/realtime-communication-integration-2025-11-11`
**Version:** 2.1
**Status:** Ready for implementation
**Approved by:** Awaiting IF.guard review
