# InfraFabric Test Fixtures

This directory contains mock data for testing IF components and inter-session communication.

---

## Available Fixtures

### **webrtc_ifmessages.py** (Session 2 - WebRTC)

**Purpose:** Test WebRTC DataChannel integration, SDP negotiation, ICE candidates, and error scenarios.

**Contents:**
- **2 SDP messages:** Offer + Answer for WebRTC session establishment
- **3 ICE candidates:** Host, Server-Reflexive (STUN), Relay (TURN)
- **3 State transitions:** Connecting → Connected → Failed
- **3 DataChannel messages:** Open, Data, Close
- **3 Error scenarios:** Invalid SDP, DTLS failure, ICE timeout
- **1 Metrics report:** Performance statistics

**Usage:**
```python
from tests.fixtures.webrtc_ifmessages import (
    WEBRTC_SDP_OFFER_MESSAGE,
    WEBRTC_ICE_CANDIDATE_HOST,
    ALL_WEBRTC_MESSAGES
)

def test_webrtc_offer_processing():
    message = WEBRTC_SDP_OFFER_MESSAGE
    result = process_sdp_offer(message)
    assert result['status'] == 'success'

def test_all_webrtc_messages():
    for message in ALL_WEBRTC_MESSAGES:
        assert validate_ifmessage_structure(message)
```

**Test Scenarios Covered:**

| Scenario | Fixture | Purpose |
|----------|---------|---------|
| **Happy path: P2P connection** | SDP offer/answer + host ICE | Test direct peer-to-peer |
| **STUN fallback** | srflx ICE candidate | Test NAT traversal with STUN |
| **TURN fallback** | relay ICE candidate | Test TURN server relay |
| **Connection failure** | WEBRTC_STATE_FAILED | Test error handling |
| **Invalid SDP** | WEBRTC_ERROR_INVALID_SDP | Test input validation |
| **Security failure** | WEBRTC_ERROR_DTLS_FAILURE | Test certificate validation |
| **Timeout handling** | WEBRTC_ERROR_TIMEOUT | Test timeout recovery |
| **DataChannel communication** | DATACHANNEL_OPEN/MESSAGE/CLOSE | Test agent coordination |
| **Performance monitoring** | WEBRTC_METRICS_REPORT | Test latency/bandwidth tracking |

**Helper Functions:**
- `validate_ifmessage_structure(message)` - Check message conforms to schema
- `create_webrtc_message(type, source, dest, payload)` - Factory for custom messages
- `generate_message_id()` - Generate unique message IDs
- `current_timestamp()` - ISO 8601 timestamp

---

## Adding New Fixtures

### Guidelines

1. **Follow IFMessage schema:** `schemas/ifmessage/v1.0.schema.json`
2. **Include realistic data:** Use actual SDP/ICE formats, not placeholders
3. **Cover edge cases:** Normal operation + error scenarios
4. **Add validation:** Self-test in `if __name__ == "__main__"`
5. **Document usage:** Add to this README with example

### Template

```python
#!/usr/bin/env python3
"""
[Component] IFMessage Test Fixtures

Provides mock IFMessage data for testing [component] functionality.

Reference: schemas/ifmessage/v1.0.schema.json
"""

from typing import Dict, List

# Example fixture
COMPONENT_MESSAGE: Dict = {
    "id": "msg-component-001",
    "timestamp": "2025-11-12T17:00:00Z",
    "level": 2,
    "source": "session-X-component",
    "destination": "IF.witness",
    "traceId": "trace-component-001",
    "version": "1.0",
    "payload": {
        "type": "event_type",
        "data": "..."
    }
}

# Validation
if __name__ == "__main__":
    from webrtc_ifmessages import validate_ifmessage_structure
    assert validate_ifmessage_structure(COMPONENT_MESSAGE)
    print("✅ Fixture valid")
```

---

## Test Structure

```
tests/
├── fixtures/
│   ├── README.md (this file)
│   ├── webrtc_ifmessages.py (Session 2 - WebRTC)
│   ├── ndi_ifmessages.py (future: Session 1 - NDI)
│   ├── sip_ifmessages.py (future: Session 4 - SIP)
│   └── coordinator_ifmessages.py (future: Session 5 - IF.coordinator)
├── integration/
│   └── test_coordinator.py (uses fixtures)
└── unit/
    └── test_webrtc_datachannel.py (uses fixtures)
```

---

## Running Fixture Tests

**Validate all fixtures:**
```bash
python3 tests/fixtures/webrtc_ifmessages.py
# Output: ✅ All 15 test fixtures valid
```

**Use in pytest:**
```python
import pytest
from tests.fixtures.webrtc_ifmessages import ALL_WEBRTC_MESSAGES

@pytest.mark.parametrize("message", ALL_WEBRTC_MESSAGES)
def test_ifmessage_schema_compliance(message):
    """Test all WebRTC fixtures conform to IFMessage schema"""
    validate_ifmessage_schema(message)
```

---

## Reference

**IFMessage Schema:** `schemas/ifmessage/v1.0.schema.json`

**Required fields:**
- `id` (string) - Unique message ID
- `timestamp` (ISO 8601 string) - Message creation time
- `level` (1 or 2) - Connectivity level (1=function→function, 2=module→module)
- `source` (string) - Emitter component/agent
- `destination` (string) - Receiver component/agent
- `payload` (object) - Message-specific data

**Optional fields:**
- `traceId` (string) - Trace correlation ID
- `version` (string) - Message contract version

---

**Last Updated:** 2025-11-12 (F1.3 - Session 1 contribution)
