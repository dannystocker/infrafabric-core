#!/usr/bin/env python3
"""
WebRTC IFMessage Test Fixtures for Session 2

Provides mock IFMessage data for testing WebRTC DataChannel integration,
SDP offer/answer negotiation, ICE candidates, and error scenarios.

Usage:
    from tests.fixtures.webrtc_ifmessages import *

    # Use in tests
    test_message = WEBRTC_SDP_OFFER_MESSAGE
    assert validate_ifmessage(test_message)

Reference: schemas/ifmessage/v1.0.schema.json
"""

from datetime import datetime, timezone
from typing import Dict, List
import uuid

# =============================================================================
# Helper Functions
# =============================================================================

def generate_message_id() -> str:
    """Generate unique message ID"""
    return f"msg-{uuid.uuid4()}"


def current_timestamp() -> str:
    """Generate ISO 8601 timestamp"""
    return datetime.now(timezone.utc).isoformat()


# =============================================================================
# SDP Offer/Answer Messages
# =============================================================================

WEBRTC_SDP_OFFER_MESSAGE: Dict = {
    "id": "msg-webrtc-offer-001",
    "timestamp": "2025-11-12T17:00:00Z",
    "level": 2,  # module→module
    "source": "session-2-webrtc-agent",
    "destination": "session-4-sip-proxy",
    "traceId": "trace-webrtc-session-001",
    "version": "1.0",
    "payload": {
        "type": "sdp_offer",
        "sdp": {
            "type": "offer",
            "sdp": """v=0
o=- 4611731400430051336 2 IN IP4 127.0.0.1
s=-
t=0 0
a=group:BUNDLE 0
a=extmap-allow-mixed
a=msid-semantic: WMS
m=application 9 UDP/DTLS/SCTP webrtc-datachannel
c=IN IP4 0.0.0.0
a=ice-ufrag:abcd
a=ice-pwd:abcdefghijklmnopqrstuvwx
a=ice-options:trickle
a=fingerprint:sha-256 AB:CD:EF:01:23:45:67:89:AB:CD:EF:01:23:45:67:89:AB:CD:EF:01:23:45:67:89:AB:CD:EF:01:23:45:67:89
a=setup:actpass
a=mid:0
a=sctp-port:5000
a=max-message-size:262144"""
        },
        "session_id": "webrtc-session-001",
        "agent_id": "session-2-webrtc-agent",
        "capabilities": ["datachannel", "sctp", "dtls"]
    }
}

WEBRTC_SDP_ANSWER_MESSAGE: Dict = {
    "id": "msg-webrtc-answer-001",
    "timestamp": "2025-11-12T17:00:05Z",
    "level": 2,
    "source": "session-4-sip-proxy",
    "destination": "session-2-webrtc-agent",
    "traceId": "trace-webrtc-session-001",
    "version": "1.0",
    "payload": {
        "type": "sdp_answer",
        "sdp": {
            "type": "answer",
            "sdp": """v=0
o=- 4611731400430051337 2 IN IP4 127.0.0.1
s=-
t=0 0
a=group:BUNDLE 0
a=extmap-allow-mixed
a=msid-semantic: WMS
m=application 9 UDP/DTLS/SCTP webrtc-datachannel
c=IN IP4 192.168.1.100
a=ice-ufrag:efgh
a=ice-pwd:zyxwvutsrqponmlkjihgfedcba
a=ice-options:trickle
a=fingerprint:sha-256 98:76:54:32:10:FE:DC:BA:98:76:54:32:10:FE:DC:BA:98:76:54:32:10:FE:DC:BA:98:76:54:32:10:FE:DC:BA
a=setup:active
a=mid:0
a=sctp-port:5000
a=max-message-size:262144"""
        },
        "session_id": "webrtc-session-001",
        "agent_id": "session-4-sip-proxy",
        "capabilities": ["datachannel", "sctp", "dtls"]
    }
}

# =============================================================================
# ICE Candidate Messages
# =============================================================================

WEBRTC_ICE_CANDIDATE_HOST: Dict = {
    "id": "msg-ice-host-001",
    "timestamp": "2025-11-12T17:00:02Z",
    "level": 2,
    "source": "session-2-webrtc-agent",
    "destination": "session-4-sip-proxy",
    "traceId": "trace-webrtc-session-001",
    "version": "1.0",
    "payload": {
        "type": "ice_candidate",
        "candidate": {
            "candidate": "candidate:1 1 UDP 2130706431 192.168.1.50 54321 typ host",
            "sdpMid": "0",
            "sdpMLineIndex": 0,
            "usernameFragment": "abcd"
        },
        "session_id": "webrtc-session-001"
    }
}

WEBRTC_ICE_CANDIDATE_SRFLX: Dict = {
    "id": "msg-ice-srflx-001",
    "timestamp": "2025-11-12T17:00:03Z",
    "level": 2,
    "source": "session-2-webrtc-agent",
    "destination": "session-4-sip-proxy",
    "traceId": "trace-webrtc-session-001",
    "version": "1.0",
    "payload": {
        "type": "ice_candidate",
        "candidate": {
            "candidate": "candidate:2 1 UDP 1694498815 203.0.113.50 54321 typ srflx raddr 192.168.1.50 rport 54321",
            "sdpMid": "0",
            "sdpMLineIndex": 0,
            "usernameFragment": "abcd"
        },
        "session_id": "webrtc-session-001",
        "stun_server": "stun:stun.infrafabric.io:3478"
    }
}

WEBRTC_ICE_CANDIDATE_RELAY: Dict = {
    "id": "msg-ice-relay-001",
    "timestamp": "2025-11-12T17:00:04Z",
    "level": 2,
    "source": "session-2-webrtc-agent",
    "destination": "session-4-sip-proxy",
    "traceId": "trace-webrtc-session-001",
    "version": "1.0",
    "payload": {
        "type": "ice_candidate",
        "candidate": {
            "candidate": "candidate:3 1 UDP 16777215 203.0.113.100 49152 typ relay raddr 203.0.113.50 rport 54321",
            "sdpMid": "0",
            "sdpMLineIndex": 0,
            "usernameFragment": "abcd"
        },
        "session_id": "webrtc-session-001",
        "turn_server": "turn:turn.infrafabric.io:3478",
        "turn_protocol": "udp"
    }
}

# =============================================================================
# WebRTC State Transition Messages
# =============================================================================

WEBRTC_STATE_CONNECTING: Dict = {
    "id": "msg-state-connecting-001",
    "timestamp": "2025-11-12T17:00:06Z",
    "level": 2,
    "source": "session-2-webrtc-agent",
    "destination": "IF.witness",
    "traceId": "trace-webrtc-session-001",
    "version": "1.0",
    "payload": {
        "type": "state_transition",
        "session_id": "webrtc-session-001",
        "previous_state": "new",
        "current_state": "connecting",
        "ice_connection_state": "checking",
        "ice_gathering_state": "gathering",
        "signaling_state": "have-remote-offer"
    }
}

WEBRTC_STATE_CONNECTED: Dict = {
    "id": "msg-state-connected-001",
    "timestamp": "2025-11-12T17:00:10Z",
    "level": 2,
    "source": "session-2-webrtc-agent",
    "destination": "IF.witness",
    "traceId": "trace-webrtc-session-001",
    "version": "1.0",
    "payload": {
        "type": "state_transition",
        "session_id": "webrtc-session-001",
        "previous_state": "connecting",
        "current_state": "connected",
        "ice_connection_state": "connected",
        "ice_gathering_state": "complete",
        "signaling_state": "stable",
        "selected_candidate_pair": {
            "local": "candidate:2 1 UDP 1694498815 203.0.113.50 54321 typ srflx",
            "remote": "candidate:1 1 UDP 2130706431 192.168.1.100 43210 typ host"
        },
        "latency_ms": 45,
        "bandwidth_estimate_kbps": 5000
    }
}

WEBRTC_STATE_FAILED: Dict = {
    "id": "msg-state-failed-001",
    "timestamp": "2025-11-12T17:00:30Z",
    "level": 2,
    "source": "session-2-webrtc-agent",
    "destination": "IF.witness",
    "traceId": "trace-webrtc-session-002",
    "version": "1.0",
    "payload": {
        "type": "state_transition",
        "session_id": "webrtc-session-002",
        "previous_state": "connecting",
        "current_state": "failed",
        "ice_connection_state": "failed",
        "ice_gathering_state": "complete",
        "signaling_state": "stable",
        "error_code": "ice_failure",
        "error_message": "All ICE candidates failed (no TURN server available)",
        "attempted_candidates": 5,
        "failed_candidates": 5
    }
}

# =============================================================================
# DataChannel Messages
# =============================================================================

WEBRTC_DATACHANNEL_OPEN: Dict = {
    "id": "msg-datachannel-open-001",
    "timestamp": "2025-11-12T17:00:11Z",
    "level": 1,  # function→function
    "source": "session-2-webrtc-agent",
    "destination": "IF.coordinator",
    "traceId": "trace-webrtc-session-001",
    "version": "1.0",
    "payload": {
        "type": "datachannel_open",
        "session_id": "webrtc-session-001",
        "channel_id": 0,
        "channel_label": "agent-coordination",
        "protocol": "sctp",
        "ordered": True,
        "max_packet_life_time": None,
        "max_retransmits": 0,
        "negotiated": False
    }
}

WEBRTC_DATACHANNEL_MESSAGE: Dict = {
    "id": "msg-datachannel-data-001",
    "timestamp": "2025-11-12T17:00:12Z",
    "level": 1,
    "source": "session-2-webrtc-agent",
    "destination": "session-4-sip-proxy",
    "traceId": "trace-webrtc-session-001",
    "version": "1.0",
    "payload": {
        "type": "datachannel_message",
        "session_id": "webrtc-session-001",
        "channel_id": 0,
        "channel_label": "agent-coordination",
        "data": {
            "message_type": "task_claim",
            "task_id": "P0.1.1",
            "agent_id": "session-2-webrtc-agent",
            "timestamp": "2025-11-12T17:00:12Z"
        },
        "size_bytes": 128
    }
}

WEBRTC_DATACHANNEL_CLOSE: Dict = {
    "id": "msg-datachannel-close-001",
    "timestamp": "2025-11-12T17:05:00Z",
    "level": 1,
    "source": "session-2-webrtc-agent",
    "destination": "IF.witness",
    "traceId": "trace-webrtc-session-001",
    "version": "1.0",
    "payload": {
        "type": "datachannel_close",
        "session_id": "webrtc-session-001",
        "channel_id": 0,
        "channel_label": "agent-coordination",
        "reason": "session_complete",
        "messages_sent": 42,
        "messages_received": 38,
        "bytes_sent": 8192,
        "bytes_received": 7340,
        "duration_seconds": 289
    }
}

# =============================================================================
# Error Scenarios
# =============================================================================

WEBRTC_ERROR_INVALID_SDP: Dict = {
    "id": "msg-error-invalid-sdp-001",
    "timestamp": "2025-11-12T17:00:01Z",
    "level": 2,
    "source": "session-2-webrtc-agent",
    "destination": "IF.witness",
    "traceId": "trace-webrtc-error-001",
    "version": "1.0",
    "payload": {
        "type": "error",
        "error_code": "invalid_sdp",
        "error_message": "SDP offer missing required 'm=application' line",
        "session_id": "webrtc-session-error-001",
        "sdp_snippet": "v=0\no=- 12345 2 IN IP4 127.0.0.1\ns=-\nt=0 0",
        "severity": "error",
        "recoverable": False
    }
}

WEBRTC_ERROR_DTLS_FAILURE: Dict = {
    "id": "msg-error-dtls-001",
    "timestamp": "2025-11-12T17:00:08Z",
    "level": 2,
    "source": "session-2-webrtc-agent",
    "destination": "IF.witness",
    "traceId": "trace-webrtc-error-002",
    "version": "1.0",
    "payload": {
        "type": "error",
        "error_code": "dtls_handshake_failure",
        "error_message": "DTLS handshake failed: certificate verification error",
        "session_id": "webrtc-session-error-002",
        "certificate_fingerprint": "sha-256 XX:XX:XX:XX:XX:XX...",
        "remote_fingerprint": "sha-256 YY:YY:YY:YY:YY:YY...",
        "severity": "critical",
        "recoverable": False,
        "security_implication": "Possible MITM attack or certificate mismatch"
    }
}

WEBRTC_ERROR_TIMEOUT: Dict = {
    "id": "msg-error-timeout-001",
    "timestamp": "2025-11-12T17:01:00Z",
    "level": 2,
    "source": "session-2-webrtc-agent",
    "destination": "IF.witness",
    "traceId": "trace-webrtc-error-003",
    "version": "1.0",
    "payload": {
        "type": "error",
        "error_code": "ice_timeout",
        "error_message": "ICE connection timeout after 60 seconds (no candidates succeeded)",
        "session_id": "webrtc-session-error-003",
        "attempted_candidates": 8,
        "host_candidates": 2,
        "srflx_candidates": 3,
        "relay_candidates": 3,
        "severity": "error",
        "recoverable": True,
        "recommended_action": "Retry with TURN server fallback"
    }
}

# =============================================================================
# Performance/Metrics Messages
# =============================================================================

WEBRTC_METRICS_REPORT: Dict = {
    "id": "msg-metrics-001",
    "timestamp": "2025-11-12T17:05:00Z",
    "level": 2,
    "source": "session-2-webrtc-agent",
    "destination": "IF.witness",
    "traceId": "trace-webrtc-session-001",
    "version": "1.0",
    "payload": {
        "type": "metrics_report",
        "session_id": "webrtc-session-001",
        "duration_seconds": 300,
        "statistics": {
            "latency_p50_ms": 42,
            "latency_p95_ms": 67,
            "latency_p99_ms": 89,
            "packets_sent": 4521,
            "packets_received": 4498,
            "packets_lost": 23,
            "packet_loss_rate": 0.0051,
            "bytes_sent": 921600,
            "bytes_received": 895400,
            "bandwidth_estimate_kbps": 4800,
            "jitter_ms": 5.3
        },
        "connection_quality": "excellent"
    }
}

# =============================================================================
# Test Collections
# =============================================================================

ALL_SDP_MESSAGES: List[Dict] = [
    WEBRTC_SDP_OFFER_MESSAGE,
    WEBRTC_SDP_ANSWER_MESSAGE
]

ALL_ICE_MESSAGES: List[Dict] = [
    WEBRTC_ICE_CANDIDATE_HOST,
    WEBRTC_ICE_CANDIDATE_SRFLX,
    WEBRTC_ICE_CANDIDATE_RELAY
]

ALL_STATE_MESSAGES: List[Dict] = [
    WEBRTC_STATE_CONNECTING,
    WEBRTC_STATE_CONNECTED,
    WEBRTC_STATE_FAILED
]

ALL_DATACHANNEL_MESSAGES: List[Dict] = [
    WEBRTC_DATACHANNEL_OPEN,
    WEBRTC_DATACHANNEL_MESSAGE,
    WEBRTC_DATACHANNEL_CLOSE
]

ALL_ERROR_MESSAGES: List[Dict] = [
    WEBRTC_ERROR_INVALID_SDP,
    WEBRTC_ERROR_DTLS_FAILURE,
    WEBRTC_ERROR_TIMEOUT
]

ALL_WEBRTC_MESSAGES: List[Dict] = (
    ALL_SDP_MESSAGES +
    ALL_ICE_MESSAGES +
    ALL_STATE_MESSAGES +
    ALL_DATACHANNEL_MESSAGES +
    ALL_ERROR_MESSAGES +
    [WEBRTC_METRICS_REPORT]
)

# =============================================================================
# Test Helpers
# =============================================================================

def validate_ifmessage_structure(message: Dict) -> bool:
    """
    Validate IFMessage conforms to v1.0 schema

    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["id", "timestamp", "level", "source", "destination", "payload"]

    for field in required_fields:
        if field not in message:
            return False

    if message["level"] not in [1, 2]:
        return False

    if not isinstance(message["payload"], dict):
        return False

    return True


def create_webrtc_message(
    message_type: str,
    source: str,
    destination: str,
    payload: Dict,
    trace_id: str = None
) -> Dict:
    """
    Factory function to create WebRTC IFMessage

    Args:
        message_type: Type of message (sdp_offer, ice_candidate, etc.)
        source: Source agent/component
        destination: Destination agent/component
        payload: Message payload data
        trace_id: Optional trace correlation ID

    Returns:
        Dict: Valid IFMessage
    """
    return {
        "id": generate_message_id(),
        "timestamp": current_timestamp(),
        "level": 2,
        "source": source,
        "destination": destination,
        "traceId": trace_id or f"trace-{uuid.uuid4()}",
        "version": "1.0",
        "payload": {
            "type": message_type,
            **payload
        }
    }


if __name__ == "__main__":
    # Self-test: validate all fixtures
    print("WebRTC IFMessage Test Fixtures - Validation")
    print("=" * 60)

    all_valid = True
    for i, message in enumerate(ALL_WEBRTC_MESSAGES, 1):
        valid = validate_ifmessage_structure(message)
        status = "✅" if valid else "❌"
        print(f"{status} Message {i}/{len(ALL_WEBRTC_MESSAGES)}: {message['id']}")

        if not valid:
            all_valid = False
            print(f"   ERROR: Invalid structure")

    print("=" * 60)
    if all_valid:
        print(f"✅ All {len(ALL_WEBRTC_MESSAGES)} test fixtures valid")
    else:
        print("❌ Some fixtures invalid - check structure")

    print(f"\nCollections available:")
    print(f"  - ALL_SDP_MESSAGES: {len(ALL_SDP_MESSAGES)} messages")
    print(f"  - ALL_ICE_MESSAGES: {len(ALL_ICE_MESSAGES)} messages")
    print(f"  - ALL_STATE_MESSAGES: {len(ALL_STATE_MESSAGES)} messages")
    print(f"  - ALL_DATACHANNEL_MESSAGES: {len(ALL_DATACHANNEL_MESSAGES)} messages")
    print(f"  - ALL_ERROR_MESSAGES: {len(ALL_ERROR_MESSAGES)} messages")
    print(f"  - WEBRTC_METRICS_REPORT: 1 message")
