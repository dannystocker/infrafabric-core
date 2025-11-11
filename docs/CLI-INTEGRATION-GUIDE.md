# CLI Integration Guide: IF.witness & IF.optimise Across Sessions

**Version:** 1.0
**Date:** 2025-11-11
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture & Flow Diagram](#architecture--flow-diagram)
3. [Session 1: NDI Integration](#session-1-ndi-integration)
4. [Session 2: WebRTC Integration](#session-2-webrtc-integration)
5. [Session 3: H.323 Integration](#session-3-h323-integration)
6. [Session 4: SIP Integration](#session-4-sip-integration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Reference & Links](#reference--links)

---

## Overview

This guide demonstrates how to integrate **IF.witness** (provenance tracking) and **IF.optimise** (cost management) across all four sessions of the InfraFabric system. Each session produces events that should be logged with cryptographic proofs and cost tracking.

### Why Session Integration Matters

- **Traceability**: Link operations across sessions with trace IDs
- **Cost Accountability**: Track token usage and budget across distributed components
- **Audit Compliance**: Maintain tamper-proof logs for security audits
- **Performance Monitoring**: Identify bottlenecks by session and component
- **Cross-Session Validation**: Verify consistency across NDI → WebRTC → H.323 → SIP

### Integration Patterns

```
┌──────────────────────────────────────────────────────────────────┐
│ Witness Entry                                                     │
├──────────────────────────────────────────────────────────────────┤
│ Field          │ Value                                            │
├────────────────┼────────────────────────────────────────────────┤
│ event          │ "session_1_frame_published"                    │
│ component      │ "IF.witness.ndi-publisher"                     │
│ trace-id       │ "session-flow-abc123" (links all sessions)     │
│ payload        │ {frame: 42, stream_id, hash}                   │
│ tokens-in      │ 200 (input tokens)                             │
│ tokens-out     │ 50 (output tokens)                             │
│ cost           │ 0.0005 (USD)                                   │
│ model          │ "claude-haiku-4.5"                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Architecture & Flow Diagram

### High-Level System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   IF.witness + IF.optimise CLI                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Session 1 (NDI)          Session 2 (WebRTC)                    │
│  ┌─────────────────┐      ┌──────────────────┐                  │
│  │ Frame Published │      │ SDP Offer/Answer │                  │
│  │ ↓               │      │ ↓                │                  │
│  │ if-witness log  │      │ if-witness log   │                  │
│  └────────┬────────┘      └────────┬─────────┘                  │
│           │                        │                             │
│  Session 3 (H.323)        Session 4 (SIP)                       │
│  ┌─────────────────┐      ┌──────────────────┐                  │
│  │ Admission Ctrl  │      │ Call Flow Events │                  │
│  │ ↓               │      │ ↓                │                  │
│  │ if-witness log  │      │ if-witness log   │                  │
│  │ if-optimise     │      │ if-optimise      │                  │
│  └────────┬────────┘      └────────┬─────────┘                  │
│           │                        │                             │
│           └────────────┬───────────┘                             │
│                        │                                         │
│                   Witness Database (SQLite)                      │
│                   ├─ Hash Chain (SHA-256)                        │
│                   ├─ Ed25519 Signatures                          │
│                   └─ Cost Tracking                               │
│                                                                  │
│                 if-witness trace <TRACE_ID>                      │
│                 if-optimise report --group-by component         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Trace ID Propagation Across Sessions

```
User Request (Trace: req-2025-11-11-001)
│
├─→ Session 1 (NDI Frame)
│   Event: ndi_frame_published
│   Trace: req-2025-11-11-001
│   Hash: 5a3d2f8c...
│
├─→ Session 2 (WebRTC Setup)
│   Event: sdp_offer_received
│   Trace: req-2025-11-11-001  ← Same trace ID
│   Hash: 7b4e1c9a... (chains from Session 1)
│
├─→ Session 3 (H.323 Admission)
│   Event: admission_request
│   Trace: req-2025-11-11-001
│   Hash: 9c2f5d1e... (chains from Session 2)
│
└─→ Session 4 (SIP Call)
    Event: invite_sent
    Trace: req-2025-11-11-001
    Hash: 8d3a6f2b... (chains from Session 3)

Result: Complete provenance chain across all sessions!
```

---

## Session 1: NDI Integration

### Overview

Session 1 handles **NDI (Network Device Interface) frame publishing**. This is the media acquisition layer where frames are published to a network stream.

### Common NDI Events

| Event Type | Description | Frequency |
|------------|-------------|-----------|
| `ndi_stream_created` | New NDI stream started | Once per session |
| `ndi_frame_published` | Frame added to stream | Per frame (60+ fps) |
| `ndi_stream_metadata` | Stream resolution/codec info | Once per session |
| `ndi_bandwidth_usage` | Network throughput | Per measurement interval |
| `ndi_error` | Frame drop, codec error | As needed |

### Example: Python NDI Frame Publisher

```python
#!/usr/bin/env python3
"""
Session 1 NDI Integration - Log frames with IF.witness
"""

import subprocess
import json
import hashlib
import time
import uuid
from pathlib import Path
from typing import Optional

class NDIWitnessPublisher:
    """
    Publishes NDI frames while logging to IF.witness
    """

    def __init__(self, stream_name: str = "IF.yologuard.01", cli_path: Optional[str] = None):
        """
        Initialize NDI publisher with witness logging

        Args:
            stream_name: NDI stream identifier
            cli_path: Path to if-witness.py (default: src/cli/if-witness.py)
        """
        self.stream_name = stream_name
        self.cli_path = Path(cli_path or "src/cli/if-witness.py").absolute()
        self.trace_id = f"ndi-stream-{uuid.uuid4().hex[:12]}"
        self.frame_count = 0

        # Log stream created event
        self._log_event(
            event="ndi_stream_created",
            payload={
                "stream_name": self.stream_name,
                "stream_id": self.trace_id,
                "timestamp": time.time()
            }
        )

    def _log_event(self, event: str, payload: dict, tokens_in: int = 0,
                   tokens_out: int = 0, cost: float = 0.0, model: str = "claude-haiku-4.5"):
        """
        Log event to IF.witness

        Args:
            event: Event type name
            payload: Event-specific data (dict)
            tokens_in: Input tokens consumed
            tokens_out: Output tokens generated
            cost: Cost in USD
            model: Model used
        """
        cmd = [
            "python3",
            str(self.cli_path),
            "log",
            "--event", event,
            "--component", "IF.witness.ndi-publisher",
            "--trace-id", self.trace_id,
            "--payload", json.dumps(payload)
        ]

        # Add cost tracking if provided
        if tokens_in or tokens_out or cost:
            cmd.extend(["--tokens-in", str(tokens_in)])
            cmd.extend(["--tokens-out", str(tokens_out)])
            cmd.extend(["--cost", str(cost)])
            cmd.extend(["--model", model])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to log {event}: {e.stderr}")
            return False

    def publish_frame(self, frame_data: bytes, frame_number: Optional[int] = None,
                     resolution: str = "1920x1080", fps: int = 60):
        """
        Publish NDI frame with witness logging

        Args:
            frame_data: Raw frame bytes
            frame_number: Frame sequence number (auto-incremented if None)
            resolution: Video resolution
            fps: Frames per second
        """
        if frame_number is None:
            frame_number = self.frame_count
            self.frame_count += 1

        # Compute content hash for frame integrity
        content_hash = hashlib.sha256(frame_data).hexdigest()

        # Log frame publication
        payload = {
            "frame_number": frame_number,
            "content_hash": content_hash,
            "resolution": resolution,
            "fps": fps,
            "size_bytes": len(frame_data),
            "timestamp": time.time()
        }

        # Estimate token usage for frame analysis
        # (In real scenario, this would come from actual processing)
        tokens_in = 50 + (len(frame_data) // 1000)  # ~1 token per KB
        tokens_out = 20
        cost = 0.00001 * (tokens_in + tokens_out)

        success = self._log_event(
            event="ndi_frame_published",
            payload=payload,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=cost
        )

        # Perform frame transmission (actual NDI publishing)
        # ... ndi_send_frame(frame_data) ...

        return {
            "frame_number": frame_number,
            "hash": content_hash,
            "logged": success
        }

    def publish_batch(self, frame_list: list, batch_size: int = 30):
        """
        Publish multiple frames efficiently

        Args:
            frame_list: List of frame data
            batch_size: Frames per batch for cost optimization
        """
        batch_results = []

        for i, frame_data in enumerate(frame_list):
            result = self.publish_frame(frame_data)
            batch_results.append(result)

            # Log batch summary every N frames (reduce witness overhead)
            if (i + 1) % batch_size == 0:
                self._log_event(
                    event="ndi_batch_complete",
                    payload={
                        "batch_number": (i + 1) // batch_size,
                        "frames_processed": i + 1,
                        "first_frame": batch_results[0]["frame_number"],
                        "last_frame": batch_results[-1]["frame_number"]
                    }
                )
                batch_results = []

        return self.trace_id

    def close(self):
        """Log stream closed event"""
        self._log_event(
            event="ndi_stream_closed",
            payload={
                "stream_name": self.stream_name,
                "total_frames": self.frame_count,
                "timestamp": time.time()
            }
        )
```

### Usage Example: Publish 60 Frames

```bash
#!/bin/bash
# Session 1: NDI Frame Publishing with Witness Logging

# Generate sample frames (in real scenario, come from camera/source)
TRACE_ID="session-1-$(date +%s)"

python3 << 'EOF'
import subprocess
import json
import os
import uuid

# Function to log NDI frame
def log_ndi_frame(frame_num, trace_id):
    payload = {
        "frame_number": frame_num,
        "resolution": "1920x1080",
        "fps": 60,
        "codec": "H264"
    }

    subprocess.run([
        "python3", "src/cli/if-witness.py", "log",
        "--event", "ndi_frame_published",
        "--component", "IF.witness.ndi-publisher",
        "--trace-id", trace_id,
        "--payload", json.dumps(payload),
        "--tokens-in", "50",
        "--tokens-out", "20",
        "--cost", "0.000001",
        "--model", "claude-haiku-4.5"
    ], check=True)

# Log stream creation
TRACE_ID = f"session-1-{uuid.uuid4().hex[:12]}"

subprocess.run([
    "python3", "src/cli/if-witness.py", "log",
    "--event", "ndi_stream_created",
    "--component", "IF.witness.ndi-publisher",
    "--trace-id", TRACE_ID,
    "--payload", json.dumps({"stream": "IF.yologuard.01", "fps": 60})
], check=True)

# Log 60 frames (one second of video at 60fps)
for i in range(60):
    log_ndi_frame(i, TRACE_ID)

# Log batch summary
subprocess.run([
    "python3", "src/cli/if-witness.py", "log",
    "--event", "ndi_batch_complete",
    "--component", "IF.witness.ndi-publisher",
    "--trace-id", TRACE_ID,
    "--payload", json.dumps({"frames": 60, "duration_seconds": 1})
], check=True)

print(f"✓ Logged 60 NDI frames (trace: {TRACE_ID})")
EOF
```

### Performance Considerations

**Frame Rate Logging Strategy:**

For high-frequency events (60+ fps), avoid logging every frame individually. Instead:

```python
# ❌ INEFFICIENT: Log every frame
for frame in frames:
    log_witness("ndi_frame_published", frame)  # 60 DB writes/second

# ✅ EFFICIENT: Log in batches
BATCH_SIZE = 30  # Log every 0.5 seconds
for i, frame in enumerate(frames):
    if (i + 1) % BATCH_SIZE == 0:
        log_witness("ndi_batch_complete", {
            "frames": BATCH_SIZE,
            "first_hash": hashes[i - BATCH_SIZE + 1],
            "last_hash": hashes[i]
        })
```

### Key Metrics to Track

```json
{
  "metric": "ndi_frame_published",
  "tokens_per_frame": 70,
  "cost_per_frame": 0.000001,
  "cost_per_second_60fps": 0.00006,
  "monthly_cost_24h_streaming": 86.4
}
```

---

## Session 2: WebRTC Integration

### Overview

Session 2 handles **WebRTC peer connection setup**, including SDP negotiation, ICE candidate gathering, and media stream initialization.

### Common WebRTC Events

| Event Type | Description | When it Happens |
|------------|-------------|-----------------|
| `webrtc_connection_started` | Peer connection created | Once per session |
| `sdp_offer_created` | Local SDP offer generated | Once during setup |
| `sdp_answer_received` | Remote SDP answer received | In response to offer |
| `ice_candidate_gathered` | ICE candidate discovered | Multiple times |
| `ice_connection_state_changed` | Connection state change | Connecting → Connected |
| `media_stream_ready` | Audio/video stream active | When media flows |
| `webrtc_error` | Connection error, timeout | On failure |

### Example: Python WebRTC Integration

```python
#!/usr/bin/env python3
"""
Session 2 WebRTC Integration - Log peer connection with witness
"""

import subprocess
import json
import time
import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

class WebRTCWitnessIntegration:
    """
    WebRTC peer connection with IF.witness logging
    """

    def __init__(self, peer_id: str, cli_path: Optional[str] = None):
        """
        Initialize WebRTC with witness integration

        Args:
            peer_id: Unique identifier for this peer
            cli_path: Path to if-witness.py
        """
        self.peer_id = peer_id
        self.cli_path = Path(cli_path or "src/cli/if-witness.py").absolute()
        self.trace_id = f"webrtc-{peer_id}-{uuid.uuid4().hex[:12]}"
        self.connection_start = time.time()

        self._log_event(
            event="webrtc_connection_started",
            payload={
                "peer_id": self.peer_id,
                "connection_id": self.trace_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    def _log_event(self, event: str, payload: dict, tokens_in: int = 0,
                   tokens_out: int = 0, cost: float = 0.0):
        """Log event to witness database"""
        cmd = [
            "python3",
            str(self.cli_path),
            "log",
            "--event", event,
            "--component", "IF.witness.webrtc",
            "--trace-id", self.trace_id,
            "--payload", json.dumps(payload),
            "--tokens-in", str(tokens_in),
            "--tokens-out", str(tokens_out),
            "--cost", str(cost),
            "--model", "claude-haiku-4.5"
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Witness log failed: {e.stderr}")
            return False

    def log_sdp_offer(self, sdp_offer: str, constraints: dict):
        """
        Log SDP offer creation

        Args:
            sdp_offer: SDP offer string
            constraints: Offered media constraints
        """
        import hashlib

        offer_hash = hashlib.sha256(sdp_offer.encode()).hexdigest()

        self._log_event(
            event="sdp_offer_created",
            payload={
                "peer_id": self.peer_id,
                "offer_hash": offer_hash,
                "constraints": constraints,
                "offer_lines": len(sdp_offer.split('\n')),
                "timestamp": datetime.utcnow().isoformat()
            },
            tokens_in=200,
            tokens_out=100,
            cost=0.0005
        )

    def log_sdp_answer(self, sdp_answer: str):
        """Log SDP answer reception"""
        import hashlib

        answer_hash = hashlib.sha256(sdp_answer.encode()).hexdigest()

        self._log_event(
            event="sdp_answer_received",
            payload={
                "peer_id": self.peer_id,
                "answer_hash": answer_hash,
                "answer_lines": len(sdp_answer.split('\n')),
                "timestamp": datetime.utcnow().isoformat()
            },
            tokens_in=200,
            tokens_out=100,
            cost=0.0005
        )

    def log_ice_candidate(self, candidate: dict, candidate_type: str = "host"):
        """
        Log ICE candidate gathering

        Avoid logging every candidate (too many events).
        Log summary instead.
        """
        # This would typically be batched
        pass

    def log_ice_candidates_summary(self, candidates: list):
        """
        Log summary of all ICE candidates gathered

        Args:
            candidates: List of ICE candidate dicts
        """
        candidate_types = {}
        for cand in candidates:
            ctype = cand.get("type", "unknown")
            candidate_types[ctype] = candidate_types.get(ctype, 0) + 1

        self._log_event(
            event="ice_candidates_gathered",
            payload={
                "peer_id": self.peer_id,
                "total_candidates": len(candidates),
                "candidate_types": candidate_types,
                "gathering_time_ms": int((time.time() - self.connection_start) * 1000),
                "timestamp": datetime.utcnow().isoformat()
            },
            tokens_in=100,
            tokens_out=50,
            cost=0.0002
        )

    def log_connection_state_change(self, old_state: str, new_state: str):
        """Log connection state changes (connecting → connected → etc.)"""
        self._log_event(
            event="ice_connection_state_changed",
            payload={
                "peer_id": self.peer_id,
                "old_state": old_state,
                "new_state": new_state,
                "duration_ms": int((time.time() - self.connection_start) * 1000),
                "timestamp": datetime.utcnow().isoformat()
            },
            tokens_in=50,
            tokens_out=25,
            cost=0.0001
        )

    def log_media_stream_ready(self, audio_enabled: bool, video_enabled: bool,
                              video_resolution: str = "1920x1080"):
        """Log when media stream is ready"""
        self._log_event(
            event="media_stream_ready",
            payload={
                "peer_id": self.peer_id,
                "audio_enabled": audio_enabled,
                "video_enabled": video_enabled,
                "video_resolution": video_resolution,
                "connection_duration_ms": int((time.time() - self.connection_start) * 1000),
                "timestamp": datetime.utcnow().isoformat()
            },
            tokens_in=150,
            tokens_out=75,
            cost=0.0003
        )

    def log_connection_error(self, error_code: str, error_message: str):
        """Log connection errors"""
        self._log_event(
            event="webrtc_error",
            payload={
                "peer_id": self.peer_id,
                "error_code": error_code,
                "error_message": error_message,
                "duration_ms": int((time.time() - self.connection_start) * 1000),
                "timestamp": datetime.utcnow().isoformat()
            },
            tokens_in=50,
            tokens_out=25,
            cost=0.0001
        )

    def close(self):
        """Log connection closed"""
        duration = time.time() - self.connection_start

        self._log_event(
            event="webrtc_connection_closed",
            payload={
                "peer_id": self.peer_id,
                "duration_seconds": duration,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

### Usage Example: Complete WebRTC Setup

```bash
#!/bin/bash
# Session 2: WebRTC Setup with Witness Logging

PEER_ID="caller-123"
TRACE_ID="webrtc-${PEER_ID}-$(date +%s)"

# 1. Log connection started
python3 src/cli/if-witness.py log \
  --event "webrtc_connection_started" \
  --component "IF.witness.webrtc" \
  --trace-id "$TRACE_ID" \
  --payload "{\"peer_id\": \"$PEER_ID\"}" \
  --tokens-in 50 \
  --tokens-out 25 \
  --cost 0.0001

# 2. Log SDP offer (generated by local peer)
python3 src/cli/if-witness.py log \
  --event "sdp_offer_created" \
  --component "IF.witness.webrtc" \
  --trace-id "$TRACE_ID" \
  --payload '{"peer_id": "'$PEER_ID'", "constraints": {"audio": true, "video": true}}' \
  --tokens-in 200 \
  --tokens-out 100 \
  --cost 0.0005

# 3. Log SDP answer (received from remote peer)
python3 src/cli/if-witness.py log \
  --event "sdp_answer_received" \
  --component "IF.witness.webrtc" \
  --trace-id "$TRACE_ID" \
  --payload '{"peer_id": "'$PEER_ID'", "answer_hash": "7b4e1c9a..."}' \
  --tokens-in 200 \
  --tokens-out 100 \
  --cost 0.0005

# 4. Log ICE candidates gathered
python3 src/cli/if-witness.py log \
  --event "ice_candidates_gathered" \
  --component "IF.witness.webrtc" \
  --trace-id "$TRACE_ID" \
  --payload '{"peer_id": "'$PEER_ID'", "total_candidates": 8, "candidate_types": {"host": 3, "srflx": 4, "relay": 1}}' \
  --tokens-in 100 \
  --tokens-out 50 \
  --cost 0.0002

# 5. Log connection state transitions
python3 src/cli/if-witness.py log \
  --event "ice_connection_state_changed" \
  --component "IF.witness.webrtc" \
  --trace-id "$TRACE_ID" \
  --payload '{"peer_id": "'$PEER_ID'", "old_state": "connecting", "new_state": "connected"}' \
  --tokens-in 50 \
  --tokens-out 25 \
  --cost 0.0001

# 6. Log media stream ready
python3 src/cli/if-witness.py log \
  --event "media_stream_ready" \
  --component "IF.witness.webrtc" \
  --trace-id "$TRACE_ID" \
  --payload '{"peer_id": "'$PEER_ID'", "audio": true, "video": true, "resolution": "1920x1080"}' \
  --tokens-in 150 \
  --tokens-out 75 \
  --cost 0.0003

# View complete trace
python3 src/cli/if-witness.py trace "$TRACE_ID"

# View costs
python3 src/cli/if-witness.py cost --trace-id "$TRACE_ID"
```

### Trace ID Linking to Session 1

To link WebRTC setup (Session 2) to NDI frame (Session 1), pass the same trace ID:

```python
# Session 1 logs: ndi_frame_published (trace: session-flow-001)
# Session 2 logs: sdp_offer_created (trace: session-flow-001)
# Both events have SAME trace ID → linked in provenance chain!

trace_id = "session-flow-001"

# Session 1: Publish frame
ndi_publisher.publish_frame(frame_data, trace_id=trace_id)

# Session 2: Setup WebRTC with same trace
webrtc.log_sdp_offer(sdp_offer, trace_id=trace_id)

# Query: All events related to user's request
python3 src/cli/if-witness.py trace session-flow-001
```

---

## Session 3: H.323 Integration

### Overview

Session 3 handles **H.323 protocol operations**, including admission control, bandwidth management, and gatekeepers.

### Common H.323 Events

| Event Type | Description | Context |
|------------|-------------|---------|
| `h323_arq_sent` | Admission Request sent to gatekeeper | Connection init |
| `h323_acf_received` | Admission Confirmation from gatekeeper | Setup allowed |
| `h323_arj_received` | Admission Rejection from gatekeeper | Bandwidth exceeded |
| `h323_bandwidth_requested` | Bandwidth request | Per call setup |
| `h323_bandwidth_granted` | Bandwidth allocated | ACF response |
| `h323_endpoint_registered` | Endpoint registered with gatekeeper | Session start |
| `h323_call_complete` | H.323 call ended | Session cleanup |

### Example: H.323 Cost Tracking Integration

```python
#!/usr/bin/env python3
"""
Session 3 H.323 Integration - Admission control with IF.optimise cost tracking
"""

import subprocess
import json
import time
import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

class H323WitnessOptimiseIntegration:
    """
    H.323 operations with witness logging and cost tracking via IF.optimise
    """

    def __init__(self, endpoint_id: str, gatekeeper_url: str,
                 cli_path: Optional[str] = None, optimise_cli_path: Optional[str] = None):
        """
        Initialize H.323 with cost tracking

        Args:
            endpoint_id: H.323 endpoint identifier
            gatekeeper_url: Gatekeeper address
            cli_path: Path to if-witness.py
            optimise_cli_path: Path to if-optimise.py
        """
        self.endpoint_id = endpoint_id
        self.gatekeeper_url = gatekeeper_url
        self.cli_path = Path(cli_path or "src/cli/if-witness.py").absolute()
        self.optimise_path = Path(optimise_cli_path or "src/cli/if-optimise.py").absolute()
        self.trace_id = f"h323-{endpoint_id}-{uuid.uuid4().hex[:12]}"

    def _log_witness(self, event: str, payload: dict, cost_data: Optional[dict] = None):
        """Log to witness and optionally track cost"""
        cmd = [
            "python3",
            str(self.cli_path),
            "log",
            "--event", event,
            "--component", "IF.witness.h323",
            "--trace-id", self.trace_id,
            "--payload", json.dumps(payload)
        ]

        # Add cost tracking if provided
        if cost_data:
            cmd.extend([
                "--tokens-in", str(cost_data.get("tokens_in", 0)),
                "--tokens-out", str(cost_data.get("tokens_out", 0)),
                "--cost", str(cost_data.get("cost", 0.0)),
                "--model", cost_data.get("model", "claude-haiku-4.5")
            ])

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Witness log failed: {e.stderr}")
            return False

    def request_admission(self, call_id: str, bandwidth_bps: int, duration_minutes: int) -> bool:
        """
        Request admission control (ARQ - Admission Request)

        Args:
            call_id: H.323 call ID
            bandwidth_bps: Required bandwidth in bits per second
            duration_minutes: Expected call duration

        Returns:
            True if admission granted, False otherwise
        """
        # Estimate cost of admission control
        # ARQ processing: ~500 tokens
        tokens_in = 500
        tokens_out = 250
        cost = 0.0003  # Haiku cost

        self._log_witness(
            event="h323_arq_sent",
            payload={
                "endpoint_id": self.endpoint_id,
                "call_id": call_id,
                "bandwidth_bps": bandwidth_bps,
                "bandwidth_kbps": bandwidth_bps / 1000,
                "requested_duration_minutes": duration_minutes,
                "gatekeeper": self.gatekeeper_url,
                "timestamp": datetime.utcnow().isoformat()
            },
            cost_data={
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost": cost,
                "model": "claude-haiku-4.5"
            }
        )

        # Simulate admission control decision
        # (In real scenario, would contact actual gatekeeper)
        admission_granted = True  # Or check against policy

        if admission_granted:
            # Log ACF (Admission Confirmation)
            self._log_witness(
                event="h323_acf_received",
                payload={
                    "endpoint_id": self.endpoint_id,
                    "call_id": call_id,
                    "bandwidth_granted_bps": bandwidth_bps,
                    "duration_minutes": duration_minutes,
                    "timestamp": datetime.utcnow().isoformat()
                },
                cost_data={
                    "tokens_in": 300,
                    "tokens_out": 150,
                    "cost": 0.0002,
                    "model": "claude-haiku-4.5"
                }
            )
        else:
            # Log ARJ (Admission Rejection)
            self._log_witness(
                event="h323_arj_received",
                payload={
                    "endpoint_id": self.endpoint_id,
                    "call_id": call_id,
                    "reason": "bandwidth_unavailable",
                    "available_bandwidth_bps": 1_000_000,
                    "timestamp": datetime.utcnow().isoformat()
                },
                cost_data={
                    "tokens_in": 300,
                    "tokens_out": 150,
                    "cost": 0.0002,
                    "model": "claude-haiku-4.5"
                }
            )

        return admission_granted

    def calculate_session_cost(self, bandwidth_bps: int, duration_minutes: int) -> dict:
        """
        Calculate total cost for H.323 session

        Args:
            bandwidth_bps: Bandwidth in bits per second
            duration_minutes: Call duration in minutes

        Returns:
            Dict with cost breakdown
        """
        # Cost model:
        # - Admission control: $0.0005 per call setup
        # - Bandwidth: $0.001 per Mbps per minute
        # - Gatekeeper keepalives: $0.00001 per minute

        setup_cost = 0.0005
        bandwidth_mbps = bandwidth_bps / 1_000_000
        bandwidth_cost = bandwidth_mbps * 0.001 * duration_minutes
        keepalive_cost = 0.00001 * duration_minutes

        total_cost = setup_cost + bandwidth_cost + keepalive_cost

        return {
            "setup_cost": setup_cost,
            "bandwidth_cost": bandwidth_cost,
            "keepalive_cost": keepalive_cost,
            "total_cost": total_cost,
            "bandwidth_bps": bandwidth_bps,
            "duration_minutes": duration_minutes
        }

    def estimate_monthly_cost(self, avg_bandwidth_bps: int, daily_minutes: int) -> dict:
        """
        Estimate monthly H.323 costs

        Args:
            avg_bandwidth_bps: Average bandwidth per call
            daily_minutes: Total minutes of calls per day

        Returns:
            Monthly cost estimate
        """
        calls_per_day = max(1, daily_minutes // 30)  # Assume 30min avg call
        daily_cost = calls_per_day * self.calculate_session_cost(
            avg_bandwidth_bps, 30
        )["total_cost"]

        monthly_cost = daily_cost * 30

        return {
            "calls_per_day": calls_per_day,
            "daily_cost": daily_cost,
            "monthly_cost": monthly_cost,
            "bandwidth_mbps": avg_bandwidth_bps / 1_000_000
        }

    def close_call(self, call_id: str, duration_minutes: float, bandwidth_bps: int):
        """Log H.323 call completion"""
        cost_info = self.calculate_session_cost(bandwidth_bps, duration_minutes)

        self._log_witness(
            event="h323_call_complete",
            payload={
                "endpoint_id": self.endpoint_id,
                "call_id": call_id,
                "duration_minutes": duration_minutes,
                "bandwidth_bps": bandwidth_bps,
                "total_cost": cost_info["total_cost"],
                "timestamp": datetime.utcnow().isoformat()
            },
            cost_data={
                "tokens_in": 200,
                "tokens_out": 100,
                "cost": 0.0002,
                "model": "claude-haiku-4.5"
            }
        )
```

### Usage: H.323 Session with Cost Tracking

```bash
#!/bin/bash
# Session 3: H.323 Admission Control with Cost Tracking

ENDPOINT_ID="h323-endpoint-001"
CALL_ID="call-2025-11-11-001"
TRACE_ID="h323-${CALL_ID}"

# Set monthly budget for H.323
python3 src/cli/if-optimise.py budget \
  --set 500.0 \
  --period month

# Request admission
python3 src/cli/if-witness.py log \
  --event "h323_arq_sent" \
  --component "IF.witness.h323" \
  --trace-id "$TRACE_ID" \
  --payload "{
    \"endpoint_id\": \"$ENDPOINT_ID\",
    \"call_id\": \"$CALL_ID\",
    \"bandwidth_bps\": 2000000,
    \"duration_minutes\": 60
  }" \
  --tokens-in 500 \
  --tokens-out 250 \
  --cost 0.0003

# Log admission confirmed
python3 src/cli/if-witness.py log \
  --event "h323_acf_received" \
  --component "IF.witness.h323" \
  --trace-id "$TRACE_ID" \
  --payload "{
    \"endpoint_id\": \"$ENDPOINT_ID\",
    \"call_id\": \"$CALL_ID\",
    \"bandwidth_granted_bps\": 2000000
  }" \
  --tokens-in 300 \
  --tokens-out 150 \
  --cost 0.0002

# ... Call is active ...

# Log call completion with cost
python3 src/cli/if-witness.py log \
  --event "h323_call_complete" \
  --component "IF.witness.h323" \
  --trace-id "$TRACE_ID" \
  --payload "{
    \"endpoint_id\": \"$ENDPOINT_ID\",
    \"call_id\": \"$CALL_ID\",
    \"duration_minutes\": 45,
    \"bandwidth_bps\": 2000000,
    \"cost_usd\": 0.0009
  }" \
  --tokens-in 200 \
  --tokens-out 100 \
  --cost 0.0002

# Check H.323 cost breakdown
python3 src/cli/if-optimise.py report --component IF.witness.h323

# Check budget status
python3 src/cli/if-optimise.py budget --period month
```

### Cost Calculation Example

```
H.323 Session Cost Calculation:

Call Setup:
  - Admission Request Processing: $0.0005
  - Bandwidth Allocation: 2 Mbps × $0.001/Mbps/min × 45 min = $0.09
  - Gatekeeper Keepalives: $0.00001/min × 45 min = $0.00045

Total Session Cost: $0.09055

Monthly Projection (3 calls/day × 30 days):
  Setup: $0.0005 × 90 calls = $0.045
  Bandwidth: $0.09 × 90 = $8.10
  Keepalives: $0.00045 × 90 = $0.041

Total Monthly: $8.186
```

---

## Session 4: SIP Integration

### Overview

Session 4 handles **SIP (Session Initiation Protocol) signaling**, including call setup, feature negotiation, and call teardown.

### Common SIP Events

| Event Type | Description | SIP Method |
|------------|-------------|-----------|
| `sip_invite_sent` | Call initiation | INVITE |
| `sip_invite_received` | Incoming call | INVITE |
| `sip_100_trying` | Server received INVITE | 100 Trying |
| `sip_180_ringing` | Remote user alerting | 180 Ringing |
| `sip_200_ok` | Call accepted | 200 OK |
| `sip_ack_sent` | Call confirmed | ACK |
| `sip_bye_sent` | Call termination | BYE |
| `sip_dialog_established` | Call active | After ACK |
| `sip_hash_verified` | Cryptographic verification | Any |

### Example: SIP Call Flow with Hash Verification

```python
#!/usr/bin/env python3
"""
Session 4 SIP Integration - Call flow with hash verification and compliance export
"""

import subprocess
import json
import hashlib
import hmac
import time
import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

class SIPWitnessIntegration:
    """
    SIP call flow with IF.witness logging and cryptographic hash verification
    """

    def __init__(self, local_uri: str, remote_uri: str,
                 cli_path: Optional[str] = None):
        """
        Initialize SIP integration

        Args:
            local_uri: Local SIP URI (e.g., sip:alice@example.com)
            remote_uri: Remote SIP URI (e.g., sip:bob@example.com)
            cli_path: Path to if-witness.py
        """
        self.local_uri = local_uri
        self.remote_uri = remote_uri
        self.cli_path = Path(cli_path or "src/cli/if-witness.py").absolute()
        self.trace_id = f"sip-call-{uuid.uuid4().hex[:12]}"
        self.call_id = None
        self.events = []  # Track all events for final hash

    def _hash_event_data(self, data: str) -> str:
        """Create SHA-256 hash of event data"""
        return hashlib.sha256(data.encode()).hexdigest()

    def _verify_hash_chain(self, previous_hash: str, current_data: str) -> str:
        """
        Create HMAC-SHA256 chain hash

        Each event is signed with previous event's hash,
        creating an unbreakable chain.
        """
        return hmac.new(
            previous_hash.encode(),
            current_data.encode(),
            hashlib.sha256
        ).hexdigest()

    def _log_event(self, event: str, payload: dict, previous_hash: Optional[str] = None,
                   tokens_in: int = 0, tokens_out: int = 0, cost: float = 0.0):
        """Log SIP event to witness"""
        # Create event hash
        event_data = json.dumps(payload, sort_keys=True)
        event_hash = self._hash_event_data(event_data)

        # Create chain hash if not first event
        chain_hash = None
        if previous_hash:
            chain_hash = self._verify_hash_chain(previous_hash, event_data)

        # Add hashes to payload
        payload_with_hash = {
            **payload,
            "event_hash": event_hash,
            "chain_hash": chain_hash
        }

        cmd = [
            "python3",
            str(self.cli_path),
            "log",
            "--event", event,
            "--component", "IF.witness.sip",
            "--trace-id", self.trace_id,
            "--payload", json.dumps(payload_with_hash),
            "--tokens-in", str(tokens_in),
            "--tokens-out", str(tokens_out),
            "--cost", str(cost),
            "--model", "claude-haiku-4.5"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.events.append({
                "event": event,
                "hash": event_hash,
                "chain_hash": chain_hash
            })
            return event_hash
        except subprocess.CalledProcessError as e:
            print(f"❌ Witness log failed: {e.stderr}")
            return None

    def send_invite(self, sdp_offer: str) -> Optional[str]:
        """
        Send SIP INVITE (initiate call)

        Args:
            sdp_offer: SDP offer string

        Returns:
            Hash of this event for chain verification
        """
        self.call_id = f"call-{int(time.time())}"

        previous_hash = self.events[-1]["hash"] if self.events else None

        invite_hash = self._log_event(
            event="sip_invite_sent",
            payload={
                "local_uri": self.local_uri,
                "remote_uri": self.remote_uri,
                "call_id": self.call_id,
                "cseq": 1,
                "sdp_offer_hash": self._hash_event_data(sdp_offer),
                "timestamp": datetime.utcnow().isoformat()
            },
            previous_hash=previous_hash,
            tokens_in=300,
            tokens_out=150,
            cost=0.0005
        )

        return invite_hash

    def receive_100_trying(self) -> Optional[str]:
        """Log 100 Trying response"""
        previous_hash = self.events[-1]["hash"] if self.events else None

        return self._log_event(
            event="sip_100_trying",
            payload={
                "remote_uri": self.remote_uri,
                "call_id": self.call_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            previous_hash=previous_hash,
            tokens_in=100,
            tokens_out=50,
            cost=0.0002
        )

    def receive_180_ringing(self) -> Optional[str]:
        """Log 180 Ringing response"""
        previous_hash = self.events[-1]["hash"] if self.events else None

        return self._log_event(
            event="sip_180_ringing",
            payload={
                "remote_uri": self.remote_uri,
                "call_id": self.call_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            previous_hash=previous_hash,
            tokens_in=100,
            tokens_out=50,
            cost=0.0002
        )

    def receive_200_ok(self, sdp_answer: str) -> Optional[str]:
        """Log 200 OK response (call accepted)"""
        previous_hash = self.events[-1]["hash"] if self.events else None

        return self._log_event(
            event="sip_200_ok",
            payload={
                "remote_uri": self.remote_uri,
                "call_id": self.call_id,
                "sdp_answer_hash": self._hash_event_data(sdp_answer),
                "timestamp": datetime.utcnow().isoformat()
            },
            previous_hash=previous_hash,
            tokens_in=200,
            tokens_out=100,
            cost=0.0003
        )

    def send_ack(self) -> Optional[str]:
        """Log ACK (call confirmed)"""
        previous_hash = self.events[-1]["hash"] if self.events else None

        return self._log_event(
            event="sip_ack_sent",
            payload={
                "remote_uri": self.remote_uri,
                "call_id": self.call_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            previous_hash=previous_hash,
            tokens_in=100,
            tokens_out=50,
            cost=0.0002
        )

    def dialog_established(self, audio_codec: str = "G.711") -> Optional[str]:
        """Log dialog established (call is active)"""
        previous_hash = self.events[-1]["hash"] if self.events else None

        return self._log_event(
            event="sip_dialog_established",
            payload={
                "local_uri": self.local_uri,
                "remote_uri": self.remote_uri,
                "call_id": self.call_id,
                "audio_codec": audio_codec,
                "media_active": True,
                "timestamp": datetime.utcnow().isoformat()
            },
            previous_hash=previous_hash,
            tokens_in=150,
            tokens_out=75,
            cost=0.0003
        )

    def send_bye(self, call_duration_seconds: int) -> Optional[str]:
        """Log BYE (call termination)"""
        previous_hash = self.events[-1]["hash"] if self.events else None

        return self._log_event(
            event="sip_bye_sent",
            payload={
                "remote_uri": self.remote_uri,
                "call_id": self.call_id,
                "duration_seconds": call_duration_seconds,
                "timestamp": datetime.utcnow().isoformat()
            },
            previous_hash=previous_hash,
            tokens_in=100,
            tokens_out=50,
            cost=0.0002
        )

    def export_call_log(self, output_path: Optional[str] = None) -> str:
        """
        Export call log for compliance/audit

        Args:
            output_path: Where to save the export (optional)

        Returns:
            Path to exported file
        """
        export_cmd = [
            "python3",
            str(self.cli_path.parent / "if-witness.py"),
            "export",
            "--trace-id", self.trace_id,
            "--format", "json"
        ]

        if output_path:
            export_cmd.extend(["--output", output_path])

        try:
            result = subprocess.run(export_cmd, capture_output=True, text=True, check=True)
            actual_path = output_path or f"sip-call-{self.call_id}.json"
            print(f"✓ Call log exported to {actual_path}")
            return actual_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Export failed: {e.stderr}")
            return None

    def verify_call_integrity(self) -> bool:
        """Verify entire call log integrity using witness verification"""
        verify_cmd = [
            "python3",
            str(self.cli_path),
            "verify"
        ]

        try:
            result = subprocess.run(verify_cmd, capture_output=True, text=True, check=True)
            print("✓ Call log verified - hash chain intact")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Verification failed: {e.stderr}")
            return False
```

### Usage: Complete SIP Call Flow

```bash
#!/bin/bash
# Session 4: SIP Call Flow with Hash Verification and Export

LOCAL_URI="sip:alice@example.com"
REMOTE_URI="sip:bob@example.com"
TRACE_ID="sip-call-$(date +%s)"

# 1. Send INVITE
python3 src/cli/if-witness.py log \
  --event "sip_invite_sent" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{
    \"local_uri\": \"$LOCAL_URI\",
    \"remote_uri\": \"$REMOTE_URI\",
    \"cseq\": 1
  }" \
  --tokens-in 300 \
  --tokens-out 150 \
  --cost 0.0005

# 2. Receive 100 Trying
python3 src/cli/if-witness.py log \
  --event "sip_100_trying" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{\"remote_uri\": \"$REMOTE_URI\"}" \
  --tokens-in 100 \
  --tokens-out 50 \
  --cost 0.0002

# 3. Receive 180 Ringing
python3 src/cli/if-witness.py log \
  --event "sip_180_ringing" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{\"remote_uri\": \"$REMOTE_URI\"}" \
  --tokens-in 100 \
  --tokens-out 50 \
  --cost 0.0002

# 4. Receive 200 OK
python3 src/cli/if-witness.py log \
  --event "sip_200_ok" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{\"remote_uri\": \"$REMOTE_URI\", \"sdp_answer_hash\": \"9c2f5d1e...\"}" \
  --tokens-in 200 \
  --tokens-out 100 \
  --cost 0.0003

# 5. Send ACK
python3 src/cli/if-witness.py log \
  --event "sip_ack_sent" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{\"remote_uri\": \"$REMOTE_URI\"}" \
  --tokens-in 100 \
  --tokens-out 50 \
  --cost 0.0002

# 6. Dialog established (call active)
python3 src/cli/if-witness.py log \
  --event "sip_dialog_established" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{
    \"local_uri\": \"$LOCAL_URI\",
    \"remote_uri\": \"$REMOTE_URI\",
    \"audio_codec\": \"G.711\",
    \"media_active\": true
  }" \
  --tokens-in 150 \
  --tokens-out 75 \
  --cost 0.0003

# ... Call is active (typically 30 seconds to 1 hour) ...

# 7. Send BYE (call ends)
python3 src/cli/if-witness.py log \
  --event "sip_bye_sent" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{
    \"remote_uri\": \"$REMOTE_URI\",
    \"duration_seconds\": 300
  }" \
  --tokens-in 100 \
  --tokens-out 50 \
  --cost 0.0002

# View complete call trace
python3 src/cli/if-witness.py trace "$TRACE_ID"

# Check call costs
python3 src/cli/if-witness.py cost --trace-id "$TRACE_ID"

# Export call log for compliance
python3 src/cli/if-witness.py export \
  --format json \
  --output "sip-call-${TRACE_ID}.json"

# Verify hash chain integrity
python3 src/cli/if-witness.py verify
```

### SIP Call Flow Diagram

```
Initiator (Alice)              Network              Responder (Bob)
    │                                                     │
    ├─ INVITE ────────────────────────────────────────→ │
    │ (Session 4: sip_invite_sent)                     │
    │                                                     │
    │← ─ ─ ─ ─ 100 Trying ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
    │ (Session 4: sip_100_trying)                      │
    │                                                     │
    │← ─ ─ ─ ─ 180 Ringing ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
    │ (Session 4: sip_180_ringing)                     │
    │                                                     │
    │← ─ ─ ─ ─ 200 OK ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
    │ (Session 4: sip_200_ok)                          │
    │                                                     │
    ├─ ACK ────────────────────────────────────────────→ │
    │ (Session 4: sip_ack_sent)                        │
    │                                                     │
    ├═ MEDIA STREAM (Video/Audio) ════════════════════→ │
    │ (Session 2: media_stream_ready)                  │
    │ (Session 1: ndi_frame_published)                 │
    │                                                     │
    ├─ BYE ────────────────────────────────────────────→ │
    │ (Session 4: sip_bye_sent)                        │
    │                                                     │
    │← ─ ─ ─ ─ 200 OK ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
    │                                                     │

Trace chain: All events have SAME trace_id → Complete provenance!
```

---

## Best Practices

### 1. Trace ID Generation and Propagation

**Generate unique trace IDs:**

```bash
# Timestamp-based (simple)
TRACE_ID="op-$(date +%s)"

# UUID-based (guaranteed unique)
TRACE_ID="op-$(uuidgen)"

# Composite (readable + unique)
TRACE_ID="req-$(date +%Y%m%d)-$(uuidgen | cut -c1-8)"
```

**Propagate across sessions:**

```python
# Session 1
trace_id = "user-request-123"
ndi_publisher.publish_frame(frame, trace_id=trace_id)

# Session 2 - Use same trace_id
webrtc.setup_peer(peer_id, trace_id=trace_id)

# Session 3 - Use same trace_id
h323.request_admission(call_id, trace_id=trace_id)

# Session 4 - Use same trace_id
sip.send_invite(remote_uri, trace_id=trace_id)

# Query: All operations for original user request
if-witness trace user-request-123
```

### 2. Cost Tracking Best Practices

**Track at operation level, not message level:**

```python
# ❌ WRONG: Track every message
for msg in messages:
    log_witness("message_sent", msg, tokens=10, cost=0.00001)

# ✅ CORRECT: Aggregate costs
batch_tokens = sum(estimate_tokens(msg) for msg in messages)
log_witness("batch_complete",
  {"message_count": len(messages)},
  tokens_in=batch_tokens,
  cost=calculate_cost(batch_tokens))
```

**Budget alignment:**

```bash
# Set budget matching expected usage
python3 src/cli/if-optimise.py budget --set 500.0 --period month

# Monitor regularly
python3 src/cli/if-optimise.py budget

# Alert thresholds: 50% → notice, 80% → warning, 100% → error
```

### 3. Error Handling

**Graceful degradation if witness is unavailable:**

```python
def log_safe(event, payload):
    """Log witness entry with error handling"""
    try:
        return log_witness(event, payload)
    except subprocess.TimeoutExpired:
        print(f"⚠️ Witness timeout, continuing without logging")
        return False
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Witness error: {e.stderr}")
        # Still allow operation to continue
        return False

# Use in critical path
if log_safe("operation_started", ...):
    print("✓ Logged to witness")
else:
    print("⚠️ Continuing without witness (network issue?)")
```

### 4. Performance Optimization

**Batch high-frequency events:**

```python
# Frame publishing: 60 fps
# ❌ Log every frame: 60 witness calls/second
# ✅ Log batch every 30 frames (0.5s): 2 witness calls/second

class BatchedLogger:
    def __init__(self, batch_size=30):
        self.batch_size = batch_size
        self.batch = []

    def add(self, event):
        self.batch.append(event)
        if len(self.batch) >= self.batch_size:
            self.flush()

    def flush(self):
        if not self.batch:
            return

        log_witness("batch_complete", {
            "event_count": len(self.batch),
            "events": self.batch
        })
        self.batch = []
```

### 5. Cross-Session Linking

**Link related operations with child trace IDs:**

```
Parent Trace: session-flow-001
├─ Child: ndi-frame-42 (Session 1)
├─ Child: webrtc-peer-123 (Session 2)
├─ Child: h323-call-789 (Session 3)
└─ Child: sip-invite-456 (Session 4)

Query all related:
$ if-witness trace session-flow-001
$ if-optimise report --trace-id session-flow-001
```

---

## Troubleshooting

### Issue: Missing Witness Entries

**Problem:** Operations completed but no witness entries found

**Debug:**

```bash
# 1. Check if-witness.py is executable
ls -la src/cli/if-witness.py

# 2. Test witness directly
python3 src/cli/if-witness.py log \
  --event "test" \
  --component "test" \
  --trace-id "test-$(date +%s)" \
  --payload '{"test": true}'

# 3. Check database exists
ls -la ~/.if-witness/witness.db

# 4. Verify database permissions
chmod 644 ~/.if-witness/witness.db
chmod 700 ~/.if-witness/
```

### Issue: Hash Chain Broken

**Problem:** Verification fails with "Hash chain broken"

**Cause:** Database corruption, manual modification, or lost keys

**Recovery:**

```bash
# 1. Export existing data before recovery
python3 src/cli/if-witness.py export \
  --format json \
  --output witness-backup-$(date +%Y%m%d).json

# 2. If keys are intact, can sometimes repair with:
sqlite3 ~/.if-witness/witness.db "VACUUM;"

# 3. If unrecoverable, start fresh
rm -rf ~/.if-witness/
python3 src/cli/if-witness.py verify  # Reinitialize

# 4. Restore from backup if available
# (Requires reimporting and resigning)
```

### Issue: Slow Witness Logging

**Problem:** Operations blocked waiting for witness

**Analysis:**

```bash
# Check database size
du -sh ~/.if-witness/witness.db

# If > 1GB, optimize:
sqlite3 ~/.if-witness/witness.db "VACUUM;"
sqlite3 ~/.if-witness/witness.db "ANALYZE;"

# Check if-witness.py performance
time python3 src/cli/if-witness.py verify
# Should complete in < 5 seconds for 1M entries
```

**Solution: Batch logging**

```python
# Instead of log 60x per second:
logger = BatchedLogger(batch_size=30)
for frame in frames:
    logger.add(frame)
# Logs 2x per second instead
```

### Issue: Cost Calculation Mismatch

**Problem:** Reported cost doesn't match estimate

**Debug:**

```bash
# 1. Check model rates
python3 src/cli/if-optimise.py rates

# 2. Verify cost data in witness
python3 src/cli/if-witness.py trace <trace_id> --format json | grep -A2 cost

# 3. Calculate manually
# cost = (tokens_in * rate_in) + (tokens_out * rate_out)
# For claude-haiku: (100 * 0.00000025) + (50 * 0.00000125) = 0.0000875

# 4. Compare with reported
python3 src/cli/if-witness.py cost --trace-id <trace_id>
```

### Issue: Budget Exceeded

**Problem:** Received alert that budget is exceeded

**Response:**

```bash
# 1. Check current spending
python3 src/cli/if-optimise.py budget --period month

# 2. View cost breakdown by component
python3 src/cli/if-optimise.py report --group-by component

# 3. Estimate remaining budget
REMAINING=$((500 - 512))  # If budget=$500, spent=$512
if [ $REMAINING -lt 0 ]; then
    echo "❌ Budget exceeded by $$((REMAINING * -1))"
fi

# 4. Options:
# - Increase budget: --set 600.0
# - Reduce operations
# - Optimize tokens (shorter payloads, smaller models)
# - Archive old entries (expensive storage)
```

---

## Reference & Links

### Documentation

- **[CLI-WITNESS-GUIDE.md](./CLI-WITNESS-GUIDE.md)** - Complete IF.witness CLI reference
- **[SWARM-COMMUNICATION-SECURITY.md](./SWARM-COMMUNICATION-SECURITY.md)** - Cryptography and security
- **[IF-URI-SCHEME.md](./IF-URI-SCHEME.md)** - Component URIs and addressing
- **[PHILOSOPHY-TO-TECH-MAPPING.md](./PHILOSOPHY-TO-TECH-MAPPING.md)** - IF.ground principles

### Code References

- `src/cli/if-witness.py` - Witness CLI implementation
- `src/cli/if-optimise.py` - Cost tracking CLI implementation
- `src/witness/database.py` - SQLite database backend
- `src/witness/crypto.py` - Ed25519 signature & hash chain

### External Resources

- **Ed25519 Spec**: [RFC 8032](https://tools.ietf.org/html/rfc8032)
- **SIP Protocol**: [RFC 3261](https://tools.ietf.org/html/rfc3261)
- **H.323 Standard**: [ITU-T H.323](https://www.itu.int/rec/T-REC-H.323/en)
- **WebRTC Spec**: [W3C WebRTC](https://w3c.github.io/webrtc-pc/)
- **NDI Protocol**: [NewTek NDI](https://www.ndi.tv/)

### Model Pricing (as of 2025-11-11)

```
claude-haiku-4.5:
  Input:  $0.25 per 1M tokens
  Output: $1.25 per 1M tokens

claude-sonnet-4.5:
  Input:  $3.00 per 1M tokens
  Output: $15.00 per 1M tokens

gpt-5:
  Input:  $50.00 per 1M tokens
  Output: $150.00 per 1M tokens

gemini-2.5-pro:
  Input:  $1.00 per 1M tokens
  Output: $5.00 per 1M tokens
```

---

## Summary Table

| Session | Component | Events | Typical Costs | Trace ID |
|---------|-----------|--------|---------------|----------|
| 1 (NDI) | IF.witness.ndi-publisher | frame_published, batch_complete | $0.00001/frame, $0.06/sec @60fps | req-001 |
| 2 (WebRTC) | IF.witness.webrtc | sdp_offer, ice_candidates, media_ready | $0.001-0.003 per session | req-001 |
| 3 (H.323) | IF.witness.h323 | arq_sent, acf_received, bandwidth_tracked | $0.001-0.09 per call | req-001 |
| 4 (SIP) | IF.witness.sip | invite_sent, 200_ok, bye_sent | $0.0015 per call | req-001 |

All sessions use **same trace ID** for complete provenance chain across user request.

---

**Version:** 1.0
**Last Updated:** 2025-11-11
**Status:** Production Ready
**Maintainer:** Danny Stocker (danny.stocker@gmail.com)
