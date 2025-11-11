# Session 2: WebRTC Agent Mesh (IF.swarm)

**Workstream:** 2 of 4 (Independent)
**Agent:** GPT-5 (Early Bloomer - fast boilerplate)
**Budget:** $12, 12 hours
**Dependencies:** None

---

## Copy-Paste This Into New Claude Code Session

```
Hi Claude! I need you to implement Workstream 2 from the InfraFabric real-time communication integration.

REPOSITORY: dannystocker/infrafabric
BRANCH: claude/realtime-workstream-2-webrtc (create from claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy)

CONTEXT FILES YOU MUST READ FIRST:
1. docs/IF-REALTIME-COMMUNICATION-INTEGRATION.md (full specification, WebRTC section)
2. docs/IF-REALTIME-PARALLEL-ROADMAP.md (your workstream details)
3. docs/SWARM-COMMUNICATION-SECURITY.md (Ed25519 signatures)
4. schemas/ifmessage/v1.0.schema.json (message format)

YOUR TASK: Implement WebRTC peer-to-peer agent mesh for IF.swarm

DELIVERABLES:
1. src/communication/webrtc-agent-mesh.ts (~400 lines)
   - IFAgentWebRTC class with SDP offer/answer
   - ICE candidate exchange
   - DataChannel for IFMessage v2.1 transport
   - Ed25519 signature on every message

2. src/communication/webrtc-signaling-server.ts (~200 lines)
   - WebSocket signaling server (Node.js + ws library)
   - SDP/ICE relay between peers
   - Logging to IF.witness

3. tests/test_webrtc_mesh.spec.ts (~100 lines)
   - Test 2-agent peer connection
   - Test 5-agent full mesh
   - Test Ed25519 signature verification
   - Test IFMessage v2.1 schema validation

4. docs/WEBRTC-SWARM-MESH.md (tutorial)
   - How to create agent mesh
   - Philosophy grounding (Wu Lun 兄弟, Indra's Net)
   - Performance benchmarks

TECHNICAL REQUIREMENTS:
- WebRTC Stack: Use native browser WebRTC APIs (RTCPeerConnection, RTCDataChannel)
- Signaling: WebSocket server (Node.js + ws library)
- STUN/TURN: Use public STUN servers (stun.l.google.com:19302) for testing
- Ed25519: Use @noble/ed25519 library (lightweight, browser-compatible)
- IFMessage v2.1: DataChannel sends JSON-encoded messages with signature field

PHILOSOPHY GROUNDING:
- Wu Lun (五倫) Relationship: 兄弟 (Siblings) — Agents are parallel peers, coordinated but equal
- Indra's Net: Every node reflects every other node (full mesh topology)
- IF.ground: Verifiable signaling (SDP logged to IF.witness)
- IF.TTT: Traceable (every message has trace_id), Transparent (SDP visible), Trustworthy (Ed25519 signed)

SUCCESS CRITERIA:
✅ 2 agents establish peer-to-peer DataChannel
✅ 5 agents form full mesh (10 connections: N*(N-1)/2)
✅ IFMessage v2.1 sent over DataChannel with Ed25519 signature
✅ SDP offers/answers logged to IF.witness
✅ Latency < 50ms peer-to-peer
✅ Tests pass: connection, mesh, signature, schema

INTERFACE CONTRACT (for Session 4 handoff):
Create docs/INTERFACES/workstream-2-webrtc-contract.yaml with:
```yaml
webrtc_datachannel_interface:
  class: IFAgentWebRTC
  methods:
    - name: sendIFMessage
      params: {message: IFMessage}
      returns: Promise<void>
    - name: onIFMessage
      type: EventHandler
      params: {message: IFMessage}
  test_fixtures:
    - valid_ifmessage_escalate.json
    - valid_sdp_offer.json
```

BUDGET & TIME:
- Estimated: 10-14 hours
- Cost: ~$8-12 (GPT-5 efficient on boilerplate)
- No blockers (no dependencies on other sessions)

START HERE:
1. Read the 4 context files
2. Install dependencies: `npm install ws @noble/ed25519`
3. Implement IFAgentWebRTC class (TypeScript)
4. Implement signaling server (Node.js)
5. Write tests (Jest or Mocha)
6. Document in WEBRTC-SWARM-MESH.md
7. Create interface contract YAML
8. Commit to branch: claude/realtime-workstream-2-webrtc
9. Push and notify when complete

EXAMPLE CODE STRUCTURE:
```typescript
// src/communication/webrtc-agent-mesh.ts
import * as ed25519 from '@noble/ed25519';

class IFAgentWebRTC {
  private pc: RTCPeerConnection;
  private dataChannel: RTCDataChannel;
  private privateKey: Uint8Array;

  async createOffer(): Promise<RTCSessionDescriptionInit> {
    this.dataChannel = this.pc.createDataChannel('if-agent-messaging');
    this.dataChannel.onmessage = (event) => this.handleMessage(event.data);

    const offer = await this.pc.createOffer();
    await this.pc.setLocalDescription(offer);

    // Log to IF.witness
    await this.logToWitness({
      event: 'webrtc_offer_created',
      sdp_hash: sha256(offer.sdp),
      trace_id: this.currentTraceId
    });

    return offer;
  }

  async sendIFMessage(message: IFMessage): Promise<void> {
    // Add Ed25519 signature
    const canonical = JSON.stringify(message);
    const signature = await ed25519.sign(canonical, this.privateKey);

    message.signature = {
      algorithm: 'ed25519',
      public_key: await ed25519.getPublicKey(this.privateKey),
      signature_bytes: signature
    };

    this.dataChannel.send(JSON.stringify(message));
  }
}
```

BEGIN!
```

---

## WebRTC Signaling Server Setup

```bash
# Create signaling server directory
mkdir -p src/communication/signaling

# Install dependencies
npm install ws @types/ws

# Run signaling server (for testing)
node src/communication/webrtc-signaling-server.js
# Expected: WebSocket server listening on ws://localhost:8443
```

---

## Test Scenario (5-Agent Full Mesh)

```
Agent 1 (Finance) ←→ Agent 2 (Legal)
       ↘          ×        ↙
         Agent 3 (Macro)
       ↗          ×        ↖
Agent 4 (Markets) ←→ Agent 5 (Competitive)

Total connections: 5 * 4 / 2 = 10 DataChannels
Expected latency: < 50ms per hop
```

---

## Handoff to Session 4 (SIP)

Session 4 will use your DataChannel for evidence sharing during external expert calls:

**Flow:** SIP call to expert → Expert wants to see evidence → WebRTC DataChannel sends files/data

Your contract documents how Session 4 can:
1. Get a reference to `IFAgentWebRTC` instance
2. Call `sendIFMessage({performative: 'inform', payload: evidenceFile})`
3. Receive responses via `onIFMessage` handler

---

## Phases 4-6 (Post-MVP Continuation)

| Phase | Task | File | Model | IF BLOCKED |
|-------|------|------|-------|-----------|
| **4** | Mesh stability: connection pooling, heartbeat protocol | src/communication/webrtc-mesh-stability.ts | GPT-5 | Waiting on SIP (Session 4) → Help with H.323 load tests (Session 3) |
| **4** | SIP-WebRTC bridge: IFMessage escalate → H.323 signaling | src/communication/sip-webrtc-bridge.ts | Claude 3.5 | Same as above → OR help Talent dashboard (Session 6) |
| **5** | Bandwidth optimization: VP9 codec, adaptive bitrate control | src/communication/webrtc-codec-manager.ts | Claude 3.5 | Independent |
| **5** | P2P routing efficiency: greedy mesh optimization, latency metrics | src/communication/webrtc-routing-optimizer.ts | GPT-5 | Independent |
| **6** | Autonomous healing: auto-reconnect logic, backoff strategy | src/communication/webrtc-auto-heal.ts | Claude 3.5 | Independent |
| — | **IDLE TASK:** Cross-session test fixtures (IFMessage + SDP + H.323 RAS mock) | tests/fixtures/cross-session-*.json | Any | Run while blocked on Session 4 SIP |

---

## Phases 7-10: Scale, Global, Intelligence, Autonomy

| Phase | Task | File | Model | Notes |
|-------|------|------|-------|-------|
| **7** | 1K mesh + batched ICE processing, connection pooling | src/communication/webrtc-scale.ts | GPT-5 | After Phase 6 → IDLE: Synthetic mesh data |
| **7** | Mesh telemetry: agent count, latency percentiles, bandwidth | src/monitoring/webrtc-telemetry.ts | Claude 3.5 | Independent |
| **8** | TURN manager: 5 regions (US-E/W, EU, APAC, SA) + auto-failover | src/communication/webrtc-turn-manager.ts | GPT-5 | Independent |
| **8** | TURN fallback: detect unreachable peers, trigger region rotation | src/communication/webrtc-turn-fallback.ts | Claude 3.5 | Independent |
| **9** | ML peer selector: latency prediction, historical data model training | src/routing/webrtc-ml-selector.ts | Claude 3.5 | Independent → IDLE: Collect 1K+ connection logs |
| **9** | Path optimizer: multi-hop routing, minimize relay hops via Dijkstra | src/routing/webrtc-path-optimizer.ts | GPT-5 | Depends Phase 9 model |
| **10** | Auto-topology: monitor mesh health, trigger rebalance on drift | src/communication/webrtc-auto-topology.ts | Claude 3.5 | Phases 8+9 → Support role: Dashboard |
| **10** | Chaos: simulate peer failures, validate topology resilience | tests/chaos/webrtc-chaos-scenarios.ts | GPT-5 | Independent → Validate Phase 10 |
| — | **IDLE:** Baselines (1K mesh latency SLA), test fixtures, docs | docs/PHASE-7-10-PERFORMANCE-SLAs.md, tests/fixtures/ | Any | Parallel all phases |

---

**Session Start:** [Copy-paste block above]
**Session Complete:** Push to `claude/realtime-workstream-2-webrtc`
