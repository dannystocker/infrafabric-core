# Implementation Guide: Communication Layer Integration

**Status:** READY FOR IMPLEMENTATION
**Timeline:** 10 weeks (3 weeks schema + 5 weeks transport + 2 weeks rollout)
**Difficulty:** Medium-High
**Prerequisites:** Python 3.9+, Node 18+ (for WebRTC), SIP server, H.323 gatekeeper

---

## Quick Start (Schema Hardening Only - Week 1)

### Step 1: Install Dependencies

```bash
cd /home/user/infrafabric

# Python dependencies
pip install cryptography networkx jsonschema

# Validate schema
python -m jsonschema -i examples/message_v21_example.json schemas/ifmessage/v2.1.schema.json
```

### Step 2: Update Existing Agents to Use v2.1 Schema

```python
from src.communication.ifmessage_v21 import IFMessage, Performative, Scope, Domain, Hazard, HazardType, HazardSeverity

# Create message with hazard tag
msg = IFMessage(
    performative=Performative.INFORM,
    sender="if://agent/swarm/legal-1@1.2.0",
    receiver=["if://agent/swarm/financial/*"],
    conversation_id="if://conversation/epic-xyz",
    content={
        "claim": "Epic settled for $520M",
        "confidence": 0.25  # LOW
    },
    citation_ids=["if://citation/abc"],
    timestamp="2025-11-10T14:32:17.234Z",
    sequence_num=42,
    scope=Scope(
        mission_id="epic-v4",
        workflow="legal-findings-pass-3",
        domain=Domain.LEGAL
    ),
    hazard=Hazard(
        type=HazardType.LEGAL,
        severity=HazardSeverity.HIGH,
        auto_escalate=True,  # CRITICAL: Forces ESCALATE despite low confidence
        rationale="Potential liability exposure >$100M"
    )
)

# Route based on confidence + hazard
decision = msg.route_decision(confidence=0.25)
print(decision)  # "ESCALATE" (hazard overrides low confidence)
```

### Step 3: Integrate Cross-Swarm Relation Agent

```python
from src.communication.cross_swarm_relation import CrossSwarmRelationAgent, Citation

# Initialize with citation store
citation_store = {...}  # Load from IF.citation service
agent = CrossSwarmRelationAgent(
    swarms=["legal", "finance", "markets", "macro"],
    citation_store=citation_store
)

# Map evidence across swarms
evidence_map = agent.map_evidence("if://claim/epic-settlement")
print(evidence_map)
# {"legal": ["cit:abc"], "finance": ["cit:def"], "markets": [], "macro": []}

# Detect conflicts
conflict = agent.detect_conflicts("if://claim/epic-settlement")
if conflict:
    print(f"CONFLICT: {conflict.rationale}")
    print(f"Action: {conflict.action}")  # "ESCALATE"

# Get consensus
consensus = agent.get_cross_swarm_consensus("if://claim/epic-settlement")
print(f"Consensus: {consensus['consensus_confidence']:.2%}")
print(f"Status: {consensus['status']}")  # "consensus", "disputed", "partial"
```

---

## Full Integration (Schema + WebRTC - Weeks 1-8)

### Phase 1: Schema Hardening (Weeks 1-3)

#### Week 1: Schema Enhancement

**Tasks:**
- [x] Create v2.1 schema (`schemas/ifmessage/v2.1.schema.json`)
- [x] Implement Python classes (`src/communication/ifmessage_v21.py`)
- [ ] Update existing IFMessage instances to v2.1
- [ ] Add schema validation to message handlers
- [ ] Create migration script (v2.0 → v2.1)

**Migration Script Example:**

```python
# tools/migrate_messages_v21.py

from src.communication.ifmessage_v21 import IFMessage, Scope, Domain
import json

def migrate_message_v20_to_v21(old_msg: dict) -> dict:
    """Migrate v2.0 message to v2.1"""
    # Add new required fields
    old_msg["nonce"] = IFMessage.generate_nonce()
    old_msg["ttl"] = 300  # 5 minutes default

    # Add scope (extract from existing fields)
    old_msg["scope"] = {
        "mission_id": extract_mission_id(old_msg),
        "workflow": extract_workflow(old_msg),
        "domain": guess_domain(old_msg["sender"]),
        "priority": "medium"
    }

    # Add topic_hash
    old_msg["topic_hash"] = hash_conversation_id(old_msg["conversation_id"])

    # Hazard is optional, don't add if not present
    old_msg["hazard"] = None

    return old_msg

# Run migration
messages = load_messages_from_db()
for msg in messages:
    migrated = migrate_message_v20_to_v21(msg)
    save_message_to_db(migrated)
```

#### Week 2: Policy-First Routing

**Tasks:**
- [ ] Refactor confidence gating logic (all agents)
- [ ] Implement hazard-based ESCALATE (priority over confidence)
- [ ] Add unit tests for ESCALATE bug fix
- [ ] Create hazard tag taxonomy documentation

**Update Routing Logic:**

```python
# Before (v2 - BROKEN):
def route_message(confidence: float) -> str:
    if confidence < 0.3:
        return "HOLD"  # BUG: Catches 0.2-0.3 range (legal hazards buried!)
    if confidence < 0.2:
        return "ESCALATE"  # Never reached
    if confidence >= 0.7:
        return "SHARE"
    return "HOLD"

# After (v2.1 - FIXED):
def route_message(message: IFMessage, confidence: float) -> str:
    # 1. Check hazards FIRST (critical fix)
    if message.hazard and message.hazard.auto_escalate:
        return "ESCALATE"

    # 2. Check confidence thresholds (reordered)
    if confidence < 0.2:
        return "ESCALATE"
    if confidence < 0.3:
        return "HOLD"
    if confidence >= 0.7:
        return "SHARE"
    return "HOLD"
```

**Unit Tests:**

```python
# tests/test_routing_v21.py

def test_hazard_overrides_confidence():
    """Test that hazard auto_escalate bypasses confidence gates"""
    msg = create_message_with_hazard(
        confidence=0.25,  # Would normally be HOLD
        hazard_auto_escalate=True
    )

    decision = msg.route_decision(confidence=0.25)
    assert decision == "ESCALATE", "Hazard should force ESCALATE"


def test_escalate_before_hold():
    """Test that ESCALATE logic runs before HOLD (bug fix)"""
    msg = create_message_without_hazard()

    decision = msg.route_decision(confidence=0.2)
    assert decision == "ESCALATE", "0.2 confidence should ESCALATE"

    decision = msg.route_decision(confidence=0.25)
    assert decision == "HOLD", "0.25 confidence should HOLD"
```

#### Week 3: Cross-Swarm Relation Agent

**Tasks:**
- [x] Implement CrossSwarmRelationAgent class
- [ ] Integrate with IF.citation service
- [ ] Add conflict detection to swarm workflows
- [ ] Create visualization of citation graph (NetworkX → Graphviz)

**Integration Example:**

```python
# agents/swarm_coordinator.py

class SwarmCoordinator:
    def __init__(self, swarms: List[str]):
        self.swarms = swarms
        self.relation_agent = CrossSwarmRelationAgent(
            swarms=swarms,
            citation_store=load_citation_store()
        )

    def coordinate_claim_validation(self, claim_id: str):
        """Coordinate multi-swarm validation of a claim"""
        # 1. Map evidence across swarms
        evidence_map = self.relation_agent.map_evidence(claim_id)

        # 2. Check for conflicts
        conflict = self.relation_agent.detect_conflicts(claim_id)
        if conflict:
            # ESCALATE if high-severity conflict
            if conflict.severity in ["high", "critical"]:
                self.escalate_to_human(conflict)
                return

        # 3. Get consensus
        consensus = self.relation_agent.get_cross_swarm_consensus(claim_id)

        # 4. Route based on consensus status
        if consensus["status"] == "consensus":
            self.publish_claim(claim_id, confidence=consensus["consensus_confidence"])
        elif consensus["status"] == "disputed":
            self.escalate_to_human(consensus)
        else:  # partial
            self.request_more_evidence(claim_id, consensus["participating_swarms"])
```

---

### Phase 2: WebRTC/SIP/H.323 Transport (Weeks 4-8)

#### Week 4: SIP Proxy Setup

**Prerequisites:**
- SIP server (Kamailio recommended, or OpenSIPS)
- TLS certificates for SIPS
- IF.guard API endpoint

**Installation:**

```bash
# Ubuntu/Debian
sudo apt install kamailio kamailio-tls-modules

# Configure Kamailio
sudo cp config/communication/kamailio.cfg /etc/kamailio/
sudo systemctl restart kamailio

# Test SIP REGISTER
sip-cli register sip:legal-1@infrafabric.local --password=test123
```

**IF.guard Integration:**

```python
# src/communication/sip_proxy_hooks.py

import sipvicious  # or pysip

class IFSIPProxy:
    def __init__(self, if_guard_api_url: str):
        self.if_guard_api = if_guard_api_url

    def handle_register(self, sip_request):
        """SIP REGISTER → IF.guard admission check"""
        agent_id = extract_agent_id(sip_request.from_uri)

        # Query IF.guard
        response = requests.post(
            f"{self.if_guard_api}/check_admission",
            json={
                "agent_id": agent_id,
                "resource": "rtc_session",
                "context": {
                    "user_agent": sip_request.headers["User-Agent"],
                    "ip": sip_request.source_ip
                }
            }
        )

        guard_decision = response.json()

        if guard_decision["decision"] == "approve":
            # Generate SIP credentials
            return sip_response_200_ok(
                credentials=generate_sip_credentials(agent_id)
            )
        else:
            # Reject
            return sip_response_403_forbidden(
                reason=guard_decision["rationale"]
            )
```

#### Week 5: WebRTC Peer Connections

**Install WebRTC Library:**

```bash
pip install aiortc aiohttp
```

**Create WebRTC Handler:**

```python
# src/communication/webrtc_handler.py

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCDataChannel
import asyncio

class IFWebRTCHandler:
    def __init__(self):
        self.peer_connections = {}

    async def create_offer(self, agent_id: str) -> dict:
        """Create WebRTC offer for agent"""
        pc = RTCPeerConnection()
        self.peer_connections[agent_id] = pc

        # Add data channel for IF messages
        data_channel = pc.createDataChannel("if-messages")
        self.setup_data_channel_handlers(data_channel)

        # Create SDP offer
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        return {
            "type": offer.type,
            "sdp": pc.localDescription.sdp
        }

    async def handle_answer(self, agent_id: str, answer_sdp: dict):
        """Handle WebRTC answer from peer"""
        pc = self.peer_connections.get(agent_id)
        if not pc:
            raise ValueError(f"No peer connection for {agent_id}")

        answer = RTCSessionDescription(
            sdp=answer_sdp["sdp"],
            type=answer_sdp["type"]
        )
        await pc.setRemoteDescription(answer)

    def setup_data_channel_handlers(self, channel: RTCDataChannel):
        """Setup handlers for data channel messages"""
        @channel.on("message")
        def on_message(message):
            # Parse IF message
            if_message = IFMessage.from_json(message)
            self.route_if_message(if_message)

        @channel.on("open")
        def on_open():
            print(f"Data channel {channel.label} opened")

        @channel.on("close")
        def on_close():
            print(f"Data channel {channel.label} closed")
```

#### Week 6: ESCALATE → Call Flow

**Implement Escalate Handler:**

```python
# src/communication/escalate_handler.py

from src.communication.webrtc_handler import IFWebRTCHandler
from src.communication.sip_proxy_hooks import IFSIPProxy

class IFEscalateHandler:
    def __init__(self, sip_proxy: IFSIPProxy, webrtc: IFWebRTCHandler):
        self.sip_proxy = sip_proxy
        self.webrtc = webrtc

    async def handle_escalate(self, message: IFMessage):
        """Transform ESCALATE message into WebRTC call"""
        # 1. Determine escalation target (human expert)
        expert = self.route_escalation(
            domain=message.scope.domain,
            hazard_type=message.hazard.type if message.hazard else None
        )

        # 2. Create WebRTC offer
        offer = await self.webrtc.create_offer(message.sender)

        # 3. Send SIP INVITE with WebRTC SDP
        sip_invite = create_sip_invite(
            from_uri=f"sip:{message.sender}",
            to_uri=expert,
            sdp=offer,
            headers={
                "Subject": f"ESCALATE: {message.content.get('claim', 'Unknown')}",
                "X-IF-Trace-ID": message.trace_id,
                "X-IF-Hazard-Type": message.hazard.type.value if message.hazard else "none"
            }
        )

        response = await self.sip_proxy.send(sip_invite)

        if response.status_code == 200:  # Expert answered
            # 4. Complete WebRTC connection
            await self.webrtc.handle_answer(message.sender, response.sdp)

            # 5. Stream citations via data channel
            await self.stream_citations(message.sender, message.citation_ids)

            return {"status": "connected", "expert": expert}
        else:
            return {"status": "failed", "reason": response.reason_phrase}

    def route_escalation(self, domain: Domain, hazard_type: Optional[HazardType]) -> str:
        """Route ESCALATE to appropriate human expert"""
        # Simple routing logic (enhance as needed)
        if hazard_type == HazardType.LEGAL:
            return "sip:legal-expert@infrafabric.local"
        elif domain == Domain.FINANCE:
            return "sip:finance-expert@infrafabric.local"
        else:
            return "sip:general-expert@infrafabric.local"
```

**Test ESCALATE Flow:**

```python
# tests/test_escalate_flow.py

async def test_escalate_to_webrtc_call():
    """Test full flow: ESCALATE message → SIP INVITE → WebRTC call"""
    # 1. Create ESCALATE message with hazard
    msg = IFMessage(
        performative=Performative.ESCALATE,
        sender="if://agent/swarm/legal-1",
        receiver=["if://agent/human/expert"],
        conversation_id="if://conversation/test-escalate",
        content={"claim": "Test escalation", "confidence": 0.2},
        timestamp=datetime.utcnow().isoformat() + "Z",
        sequence_num=1,
        scope=Scope(mission_id="test", workflow="test", domain=Domain.LEGAL),
        hazard=Hazard(
            type=HazardType.LEGAL,
            severity=HazardSeverity.HIGH,
            auto_escalate=True,
            rationale="Test hazard"
        )
    )

    # 2. Handle ESCALATE
    handler = IFEscalateHandler(sip_proxy, webrtc)
    result = await handler.handle_escalate(msg)

    # 3. Verify call initiated
    assert result["status"] == "connected"
    assert "legal-expert" in result["expert"]
```

#### Weeks 7-8: H.323 + Integration Testing

See RFC document for full details.

---

## Testing Strategy

### Unit Tests

```bash
# Run all communication layer tests
pytest tests/communication/ -v

# Specific test suites
pytest tests/communication/test_ifmessage_v21.py  # Schema tests
pytest tests/communication/test_cross_swarm.py   # Relation agent tests
pytest tests/communication/test_escalate.py      # WebRTC escalate tests
```

### Integration Tests

```bash
# End-to-end test: Message → ESCALATE → Call
pytest tests/integration/test_e2e_escalate.py

# Cross-swarm conflict detection
pytest tests/integration/test_cross_swarm_conflicts.py
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All unit tests passing (100% coverage for new code)
- [ ] Integration tests passing
- [ ] Security audit completed (signatures, encryption)
- [ ] Performance benchmarks met (<1.3ms message overhead)
- [ ] Documentation updated (API docs, runbooks)

### Staging Deployment

- [ ] Deploy SIP proxy, TURN servers
- [ ] Enable v2.1 schema in staging swarm
- [ ] Test ESCALATE flow with mock human expert
- [ ] Monitor hazard escalation rate, call success rate

### Production Deployment

- [ ] Gradual rollout (10% → 50% → 100% traffic)
- [ ] Monitor metrics (latency, escalation rate, conflicts detected)
- [ ] Have rollback plan ready (revert to v2.0 schema)

---

## Troubleshooting

### Issue: Messages rejected with "nonce collision"
**Solution:** Increase nonce size from 96-bit to 128-bit, or check for clock skew

### Issue: ESCALATE calls not connecting
**Solution:** Check TURN server logs, verify NAT traversal, test SIP REGISTER

### Issue: Cross-swarm conflicts not detected
**Solution:** Verify citation graph is built correctly, check confidence calculation

---

## Next Steps

1. **Review this guide** with implementation team
2. **Assign owners** for each phase (schema, SIP, WebRTC, H.323)
3. **Start Week 1** (schema enhancement)
4. **Weekly check-ins** to track progress

**Questions?** Open an issue at `github.com/dannystocker/infrafabric/issues`

---

**Citation:**
```json
{
  "citation_id": "if://citation/impl-guide-comm-2025-11-11",
  "claim_id": "if://claim/communication-layer-implementation",
  "sources": [
    {"type": "rfc", "ref": "docs/RFC-COMMUNICATION-LAYER-INTEGRATION.md"},
    {"type": "code", "ref": "src/communication/ifmessage_v21.py"},
    {"type": "code", "ref": "src/communication/cross_swarm_relation.py"}
  ],
  "rationale": "Practical implementation guide for communication layer integration",
  "status": "verified",
  "created_by": "if://agent/claude-sonnet-4.5",
  "created_at": "2025-11-11T12:30:00Z"
}
```
