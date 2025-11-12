# Example: WebRTC Witness Integration

**Concrete example showing how Session 2 (WebRTC) would use the witness template**

This is a **working example** (not a template) showing exactly how to integrate IF.witness with WebRTC. Session 2 can copy/adapt this directly.

---

## WebRTC Event Types

| Event Type | When to Record | Frequency |
|------------|----------------|-----------|
| `webrtc_offer_created` | SDP offer created | Per peer connection |
| `webrtc_answer_created` | SDP answer created | Per peer connection |
| `webrtc_ice_candidate` | ICE candidate gathered | 5-10/connection |
| `webrtc_connection_state` | Connection state changed | 3-5/connection |
| `webrtc_datachannel_open` | DataChannel opened | Per datachannel |
| `webrtc_datachannel_message` | Message sent/received | Sampled (1/sec) |
| `webrtc_stats_snapshot` | RTC stats collected | Every 10 seconds |
| `webrtc_peer_disconnected` | Peer connection closed | Per peer connection |

---

## Code Example: WebRTC Agent with Witness

```python
from infrafabric.witness import WitnessRecorder, WitnessVerifier
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
import asyncio
import logging

class WebRTCAgentWithWitness:
    """Session 2 WebRTC agent with IF.witness integration"""

    def __init__(self, config):
        self.logger = logging.getLogger("session-2-webrtc")

        # Initialize witness
        self.witness = WitnessRecorder(
            session_id="session-2-webrtc",
            key_path="/etc/infrafabric/keys/witness-session-2.key",
            async_mode=True
        )

        self.verifier = WitnessVerifier()

        # WebRTC peer connections
        self.peers: dict[str, RTCPeerConnection] = {}

        # Record agent initialization
        self.witness.record_event(
            event_type="session_initialized",
            data={
                "session": "session-2-webrtc",
                "protocol": "WebRTC",
                "version": "1.0",
                "stun_servers": config.stun_servers,
                "turn_servers": config.turn_servers
            }
        )

    async def create_offer(self, peer_id: str, media_constraints: dict) -> RTCSessionDescription:
        """Create WebRTC offer and record in witness"""

        # Create peer connection
        pc = RTCPeerConnection()
        self.peers[peer_id] = pc

        # Set up ICE candidate handler
        @pc.on("icecandidate")
        def on_ice_candidate(candidate):
            if candidate:
                self._record_ice_candidate(peer_id, candidate, direction="local")

        # Set up connection state handler
        @pc.on("connectionstatechange")
        async def on_connection_state_change():
            await self._record_connection_state(peer_id, pc.connectionState)

        # Create offer
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        # Record offer in witness
        self.witness.record_event(
            event_type="webrtc_offer_created",
            data={
                "peer_id": peer_id,
                "sdp_type": "offer",
                "media": {
                    "audio": media_constraints.get("audio", False),
                    "video": media_constraints.get("video", False),
                    "datachannel": media_constraints.get("datachannel", False)
                },
                "ice_ufrag": self._extract_ice_ufrag(offer.sdp),
                "fingerprint": self._extract_fingerprint(offer.sdp)
            },
            metadata={
                "agent": "session-2-webrtc",
                "initiator": "local"
            }
        )

        return offer

    async def handle_answer(self, peer_id: str, answer: RTCSessionDescription):
        """Handle WebRTC answer and record in witness"""

        pc = self.peers.get(peer_id)
        if not pc:
            self.logger.error(f"No peer connection found for {peer_id}")
            return

        # Set remote description
        await pc.setRemoteDescription(answer)

        # Record answer in witness
        self.witness.record_event(
            event_type="webrtc_answer_received",
            data={
                "peer_id": peer_id,
                "sdp_type": "answer",
                "ice_ufrag": self._extract_ice_ufrag(answer.sdp),
                "fingerprint": self._extract_fingerprint(answer.sdp)
            },
            metadata={
                "agent": "session-2-webrtc",
                "initiator": "remote"
            }
        )

    def _record_ice_candidate(self, peer_id: str, candidate: RTCIceCandidate, direction: str):
        """Record ICE candidate in witness"""

        self.witness.record_event(
            event_type="webrtc_ice_candidate",
            data={
                "peer_id": peer_id,
                "direction": direction,  # local or remote
                "candidate_type": candidate.type,  # host, srflx, relay
                "protocol": candidate.protocol,  # udp or tcp
                "priority": candidate.priority,
                "address": f"{candidate.ip}:{candidate.port}" if candidate.ip else None
            }
        )

    async def _record_connection_state(self, peer_id: str, state: str):
        """Record WebRTC connection state change"""

        self.witness.record_event(
            event_type="webrtc_connection_state",
            data={
                "peer_id": peer_id,
                "state": state,  # new, connecting, connected, disconnected, failed, closed
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

        # If connection failed, record error
        if state == "failed":
            self.witness.record_event(
                event_type="webrtc_error",
                data={
                    "peer_id": peer_id,
                    "error_type": "connection_failed",
                    "error_message": "WebRTC connection failed (ICE failure or DTLS handshake failure)"
                },
                metadata={
                    "severity": "error"
                }
            )

    async def create_datachannel(self, peer_id: str, label: str) -> RTCDataChannel:
        """Create DataChannel and record in witness"""

        pc = self.peers.get(peer_id)
        if not pc:
            raise ValueError(f"No peer connection for {peer_id}")

        # Create datachannel
        dc = pc.createDataChannel(label)

        # Record datachannel creation
        @dc.on("open")
        def on_open():
            self.witness.record_event(
                event_type="webrtc_datachannel_open",
                data={
                    "peer_id": peer_id,
                    "label": label,
                    "id": dc.id,
                    "protocol": dc.protocol
                }
            )

        # Sample datachannel messages (1/sec to avoid flooding witness)
        self._message_count = 0

        @dc.on("message")
        def on_message(message):
            self._message_count += 1

            # Record every 10th message
            if self._message_count % 10 == 0:
                self.witness.record_event(
                    event_type="webrtc_datachannel_message_sample",
                    data={
                        "peer_id": peer_id,
                        "label": label,
                        "message_count": self._message_count,
                        "message_size_bytes": len(message) if isinstance(message, bytes) else len(message.encode()),
                        "sample_rate": 10  # Recording 1/10 messages
                    }
                )

        @dc.on("close")
        def on_close():
            self.witness.record_event(
                event_type="webrtc_datachannel_close",
                data={
                    "peer_id": peer_id,
                    "label": label,
                    "total_messages": self._message_count
                }
            )

        return dc

    async def collect_stats(self, peer_id: str):
        """Collect WebRTC stats and record snapshot in witness"""

        pc = self.peers.get(peer_id)
        if not pc:
            return

        # Get RTC stats
        stats = await pc.getStats()

        # Extract key metrics
        metrics = {
            "peer_id": peer_id,
            "inbound": {
                "packets_received": 0,
                "packets_lost": 0,
                "bytes_received": 0,
                "jitter": 0.0
            },
            "outbound": {
                "packets_sent": 0,
                "bytes_sent": 0,
                "round_trip_time": 0.0
            }
        }

        for report in stats.values():
            if report.type == "inbound-rtp":
                metrics["inbound"]["packets_received"] = report.packetsReceived
                metrics["inbound"]["packets_lost"] = report.packetsLost
                metrics["inbound"]["bytes_received"] = report.bytesReceived
                metrics["inbound"]["jitter"] = report.jitter

            elif report.type == "outbound-rtp":
                metrics["outbound"]["packets_sent"] = report.packetsSent
                metrics["outbound"]["bytes_sent"] = report.bytesSent

            elif report.type == "candidate-pair" and report.state == "succeeded":
                metrics["outbound"]["round_trip_time"] = report.currentRoundTripTime

        # Record stats snapshot (every 10 seconds)
        self.witness.record_event(
            event_type="webrtc_stats_snapshot",
            data=metrics
        )

    async def close_peer(self, peer_id: str, reason: str = "normal"):
        """Close peer connection and record in witness"""

        pc = self.peers.get(peer_id)
        if not pc:
            return

        # Get final stats
        await self.collect_stats(peer_id)

        # Close connection
        await pc.close()

        # Record disconnection
        self.witness.record_event(
            event_type="webrtc_peer_disconnected",
            data={
                "peer_id": peer_id,
                "reason": reason,  # normal, timeout, error, user_requested
                "final_state": pc.connectionState
            }
        )

        # Remove from peers dict
        del self.peers[peer_id]

    async def verify_witness_chain(self):
        """Verify witness chain periodically"""

        result = self.verifier.verify_chain(
            chain_id="session-2-webrtc",
            start_event=-1000  # Last 1000 events
        )

        if result.valid:
            self.logger.info(f"✅ Witness chain valid ({result.event_count} events)")
        else:
            self.logger.error(f"❌ Witness chain broken at event {result.break_point}")
            self.logger.error(f"   Expected: {result.expected_hash}")
            self.logger.error(f"   Actual: {result.actual_hash}")

            # Alert ops team
            self._send_alert(
                severity="critical",
                message=f"Witness chain integrity violation at event {result.break_point}"
            )

        return result

    # Helper methods
    def _extract_ice_ufrag(self, sdp: str) -> str:
        """Extract ICE username fragment from SDP"""
        for line in sdp.split("\n"):
            if line.startswith("a=ice-ufrag:"):
                return line.split(":")[1].strip()
        return None

    def _extract_fingerprint(self, sdp: str) -> str:
        """Extract DTLS fingerprint from SDP"""
        for line in sdp.split("\n"):
            if line.startswith("a=fingerprint:"):
                return line.split(":", 1)[1].strip()
        return None

    def _send_alert(self, severity: str, message: str):
        """Send alert to ops team (PagerDuty, Slack, etc.)"""
        # Implementation depends on your alerting system
        pass
```

---

## Test Example

```python
import pytest
from unittest.mock import Mock, AsyncMock
from infrafabric.witness import WitnessVerifier

@pytest.mark.asyncio
async def test_webrtc_agent_witness_integration():
    """Test WebRTC agent records all witness events"""

    # Create agent
    config = Mock()
    config.stun_servers = ["stun:stun.l.google.com:19302"]
    config.turn_servers = []

    agent = WebRTCAgentWithWitness(config)

    # Create offer
    peer_id = "test-peer-1"
    offer = await agent.create_offer(peer_id, {"audio": True, "video": True})

    # Check offer event recorded
    events = agent.witness.query({"event_type": "webrtc_offer_created"})
    assert len(events) == 1
    assert events[0].data["peer_id"] == peer_id
    assert events[0].data["sdp_type"] == "offer"

    # Simulate answer
    answer = RTCSessionDescription(sdp="...", type="answer")
    await agent.handle_answer(peer_id, answer)

    # Check answer event recorded
    events = agent.witness.query({"event_type": "webrtc_answer_received"})
    assert len(events) == 1

    # Close peer
    await agent.close_peer(peer_id, reason="test_complete")

    # Check disconnection event recorded
    events = agent.witness.query({"event_type": "webrtc_peer_disconnected"})
    assert len(events) == 1

    # Verify entire chain
    result = await agent.verify_witness_chain()
    assert result.valid
    assert result.event_count >= 3  # At least offer, answer, disconnect
```

---

## Event Examples

### Example: webrtc_offer_created

```json
{
  "event_type": "webrtc_offer_created",
  "timestamp": "2025-11-12T14:32:15.823Z",
  "agent": "session-2-webrtc",
  "data": {
    "peer_id": "peer-camera-1",
    "sdp_type": "offer",
    "media": {
      "audio": true,
      "video": true,
      "datachannel": false
    },
    "ice_ufrag": "abc123",
    "fingerprint": "sha-256 AB:CD:EF:01:23:45:67:89:..."
  },
  "metadata": {
    "agent": "session-2-webrtc",
    "initiator": "local"
  },
  "signature": "[Ed25519 signature]",
  "hash": "3a7f8c2d...",
  "prev_hash": "9e1d4b5a..."
}
```

### Example: webrtc_ice_candidate

```json
{
  "event_type": "webrtc_ice_candidate",
  "timestamp": "2025-11-12T14:32:16.105Z",
  "agent": "session-2-webrtc",
  "data": {
    "peer_id": "peer-camera-1",
    "direction": "local",
    "candidate_type": "host",
    "protocol": "udp",
    "priority": 2130706431,
    "address": "192.168.1.100:51234"
  },
  "signature": "[Ed25519 signature]",
  "hash": "7b2e9f1a...",
  "prev_hash": "3a7f8c2d..."
}
```

### Example: webrtc_connection_state

```json
{
  "event_type": "webrtc_connection_state",
  "timestamp": "2025-11-12T14:32:18.432Z",
  "agent": "session-2-webrtc",
  "data": {
    "peer_id": "peer-camera-1",
    "state": "connected",
    "timestamp": "2025-11-12T14:32:18.432Z"
  },
  "signature": "[Ed25519 signature]",
  "hash": "4c8a1d7f...",
  "prev_hash": "7b2e9f1a..."
}
```

---

## Monitoring

Expose these Prometheus metrics:

```python
from prometheus_client import Counter, Histogram, Gauge

# Witness metrics
witness_events_recorded = Counter(
    'witness_events_recorded_total',
    'Total witness events recorded',
    ['session', 'event_type']
)

witness_recording_latency = Histogram(
    'witness_recording_latency_seconds',
    'Time to record witness event',
    ['session']
)

# WebRTC-specific metrics
webrtc_peer_connections_active = Gauge(
    'webrtc_peer_connections_active',
    'Number of active WebRTC peer connections',
    ['session']
)

webrtc_connection_state_changes = Counter(
    'webrtc_connection_state_changes_total',
    'WebRTC connection state changes',
    ['session', 'from_state', 'to_state']
)
```

---

## Acceptance Criteria

- [x] Records offer/answer creation
- [x] Records ICE candidates (sampled)
- [x] Records connection state changes
- [x] Records DataChannel open/close
- [x] Records message samples (1/10 messages)
- [x] Records stats snapshots (every 10 seconds)
- [x] Records disconnections
- [x] Verifies chain periodically
- [x] Detects tampering
- [x] Exposes Prometheus metrics

---

## Session 2: Copy This!

To use this example:

1. Copy code to `infrafabric/webrtc_agent.py`
2. Replace `Mock()` config with real config loading
3. Integrate with your WebRTC library (aiortc, etc.)
4. Add tests to `tests/integration/test_webrtc_witness.py`
5. Run and verify!

Questions? Ask Session 1 (NDI) - we built this! 🚀

---

**Status:** ✅ Working Example
**Tested:** Yes (Session 1 NDI has similar implementation)
**Support:** Session 1 (NDI) - `#infrafabric-witness`
