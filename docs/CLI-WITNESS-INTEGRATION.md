# IF.witness Quick Integration Guide

**Concise, action-oriented reference for Sessions 1-4**

---

## 30-Second Start

**Three commands to get logging:**

```bash
# 1. Create trace ID
TRACE_ID="session-$(date +%s)"

# 2. Log your first event
python3 src/cli/if-witness.py log \
  --event "demo_event" \
  --component "IF.witness.demo" \
  --trace-id "$TRACE_ID" \
  --payload '{"status": "active"}'

# 3. View the trace
python3 src/cli/if-witness.py trace "$TRACE_ID"
```

Done. You're logging to witness.

---

## Session 1: NDI Frame Publishing

**What it does:** Logs video frames with content hashes for integrity tracking.

**Key events:** `ndi_stream_created`, `ndi_frame_published`, `ndi_batch_complete`

### Example 1: Publish single frame

```bash
TRACE_ID="ndi-$(date +%s)"

python3 src/cli/if-witness.py log \
  --event "ndi_frame_published" \
  --component "IF.witness.ndi-publisher" \
  --trace-id "$TRACE_ID" \
  --payload '{
    "frame_number": 1,
    "content_hash": "5a3d2f8c...",
    "resolution": "1920x1080",
    "fps": 60
  }' \
  --tokens-in 50 \
  --tokens-out 20 \
  --cost 0.000001
```

### Example 2: Batch frames (30 fps efficient)

```bash
#!/bin/bash
TRACE_ID="ndi-batch-$(date +%s)"

# Log stream start
python3 src/cli/if-witness.py log \
  --event "ndi_stream_created" \
  --component "IF.witness.ndi-publisher" \
  --trace-id "$TRACE_ID" \
  --payload '{"stream": "IF.yologuard.01", "fps": 60}'

# Log batch (instead of 60 individual frames)
python3 src/cli/if-witness.py log \
  --event "ndi_batch_complete" \
  --component "IF.witness.ndi-publisher" \
  --trace-id "$TRACE_ID" \
  --payload '{
    "frames": 30,
    "duration_seconds": 0.5,
    "first_hash": "a1b2c3...",
    "last_hash": "x9y8z7..."
  }' \
  --tokens-in 100 \
  --tokens-out 50 \
  --cost 0.00001

python3 src/cli/if-witness.py trace "$TRACE_ID"
```

**Cost model:** ~$0.00001 per frame or $0.06/second @60fps

---

## Session 2: WebRTC Setup

**What it does:** Logs peer connection setup: SDP offer/answer, ICE candidates, connection states.

**Key events:** `webrtc_connection_started`, `sdp_offer_created`, `sdp_answer_received`, `ice_candidates_gathered`, `media_stream_ready`

### Example 1: Full WebRTC handshake

```bash
PEER_ID="caller-123"
TRACE_ID="webrtc-$PEER_ID-$(date +%s)"

# 1. Connection started
python3 src/cli/if-witness.py log \
  --event "webrtc_connection_started" \
  --component "IF.witness.webrtc" \
  --trace-id "$TRACE_ID" \
  --payload "{\"peer_id\": \"$PEER_ID\"}" \
  --tokens-in 50 --tokens-out 25 --cost 0.0001

# 2. SDP Offer
python3 src/cli/if-witness.py log \
  --event "sdp_offer_created" \
  --component "IF.witness.webrtc" \
  --trace-id "$TRACE_ID" \
  --payload "{\"peer_id\": \"$PEER_ID\", \"constraints\": {\"audio\": true, \"video\": true}}" \
  --tokens-in 200 --tokens-out 100 --cost 0.0005

# 3. SDP Answer
python3 src/cli/if-witness.py log \
  --event "sdp_answer_received" \
  --component "IF.witness.webrtc" \
  --trace-id "$TRACE_ID" \
  --payload "{\"peer_id\": \"$PEER_ID\", \"answer_hash\": \"7b4e1c9a...\"}" \
  --tokens-in 200 --tokens-out 100 --cost 0.0005

# 4. ICE Candidates
python3 src/cli/if-witness.py log \
  --event "ice_candidates_gathered" \
  --component "IF.witness.webrtc" \
  --trace-id "$TRACE_ID" \
  --payload "{\"peer_id\": \"$PEER_ID\", \"total_candidates\": 8, \"candidate_types\": {\"host\": 3, \"srflx\": 4, \"relay\": 1}}" \
  --tokens-in 100 --tokens-out 50 --cost 0.0002

# 5. Connection ready
python3 src/cli/if-witness.py log \
  --event "media_stream_ready" \
  --component "IF.witness.webrtc" \
  --trace-id "$TRACE_ID" \
  --payload "{\"peer_id\": \"$PEER_ID\", \"audio\": true, \"video\": true, \"resolution\": \"1920x1080\"}" \
  --tokens-in 150 --tokens-out 75 --cost 0.0003

python3 src/cli/if-witness.py trace "$TRACE_ID"
```

**Cost model:** $0.001-0.003 per complete WebRTC session

---

## Session 3: H.323 Admission Control

**What it does:** Logs H.323 call setup with bandwidth admission requests and cost tracking.

**Key events:** `h323_arq_sent`, `h323_acf_received`, `h323_call_complete`

### Example 1: Admission request & confirmation

```bash
ENDPOINT_ID="h323-endpoint-001"
CALL_ID="call-$(date +%s)"
TRACE_ID="h323-$CALL_ID"

# Set monthly budget first
python3 src/cli/if-optimise.py budget --set 500.0 --period month

# 1. Request admission (ARQ)
python3 src/cli/if-witness.py log \
  --event "h323_arq_sent" \
  --component "IF.witness.h323" \
  --trace-id "$TRACE_ID" \
  --payload "{
    \"endpoint_id\": \"$ENDPOINT_ID\",
    \"call_id\": \"$CALL_ID\",
    \"bandwidth_bps\": 2000000,
    \"duration_minutes\": 45
  }" \
  --tokens-in 500 --tokens-out 250 --cost 0.0003

# 2. Admission confirmed (ACF)
python3 src/cli/if-witness.py log \
  --event "h323_acf_received" \
  --component "IF.witness.h323" \
  --trace-id "$TRACE_ID" \
  --payload "{
    \"endpoint_id\": \"$ENDPOINT_ID\",
    \"call_id\": \"$CALL_ID\",
    \"bandwidth_granted_bps\": 2000000
  }" \
  --tokens-in 300 --tokens-out 150 --cost 0.0002

# ... Call is active ...

# 3. Call complete with cost
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
  --tokens-in 200 --tokens-out 100 --cost 0.0002

# View breakdown
python3 src/cli/if-optimise.py report --component IF.witness.h323
python3 src/cli/if-witness.py cost --trace-id "$TRACE_ID"
```

**Cost calculation example:**
```
Setup: $0.0005
Bandwidth: 2 Mbps × $0.001/Mbps/min × 45 min = $0.09
Keepalives: $0.00001/min × 45 min = $0.00045
Total: $0.09055
```

---

## Session 4: SIP Call Flow

**What it does:** Logs SIP signaling with call state transitions and hash verification.

**Key events:** `sip_invite_sent`, `sip_100_trying`, `sip_180_ringing`, `sip_200_ok`, `sip_ack_sent`, `sip_dialog_established`, `sip_bye_sent`

### Example 1: Complete SIP call (INVITE → ACK → BYE)

```bash
LOCAL_URI="sip:alice@example.com"
REMOTE_URI="sip:bob@example.com"
TRACE_ID="sip-call-$(date +%s)"

# 1. Send INVITE
python3 src/cli/if-witness.py log \
  --event "sip_invite_sent" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{\"local_uri\": \"$LOCAL_URI\", \"remote_uri\": \"$REMOTE_URI\", \"cseq\": 1}" \
  --tokens-in 300 --tokens-out 150 --cost 0.0005

# 2. Receive 100 Trying
python3 src/cli/if-witness.py log \
  --event "sip_100_trying" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{\"remote_uri\": \"$REMOTE_URI\"}" \
  --tokens-in 100 --tokens-out 50 --cost 0.0002

# 3. Receive 180 Ringing
python3 src/cli/if-witness.py log \
  --event "sip_180_ringing" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{\"remote_uri\": \"$REMOTE_URI\"}" \
  --tokens-in 100 --tokens-out 50 --cost 0.0002

# 4. Receive 200 OK
python3 src/cli/if-witness.py log \
  --event "sip_200_ok" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{\"remote_uri\": \"$REMOTE_URI\", \"sdp_answer_hash\": \"9c2f5d1e...\"}" \
  --tokens-in 200 --tokens-out 100 --cost 0.0003

# 5. Send ACK
python3 src/cli/if-witness.py log \
  --event "sip_ack_sent" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{\"remote_uri\": \"$REMOTE_URI\"}" \
  --tokens-in 100 --tokens-out 50 --cost 0.0002

# 6. Dialog active
python3 src/cli/if-witness.py log \
  --event "sip_dialog_established" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{\"local_uri\": \"$LOCAL_URI\", \"remote_uri\": \"$REMOTE_URI\", \"audio_codec\": \"G.711\", \"media_active\": true}" \
  --tokens-in 150 --tokens-out 75 --cost 0.0003

# ... Call active (30sec - 1 hour) ...

# 7. Send BYE
python3 src/cli/if-witness.py log \
  --event "sip_bye_sent" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" \
  --payload "{\"remote_uri\": \"$REMOTE_URI\", \"duration_seconds\": 300}" \
  --tokens-in 100 --tokens-out 50 --cost 0.0002

# View & export
python3 src/cli/if-witness.py trace "$TRACE_ID"
python3 src/cli/if-witness.py cost --trace-id "$TRACE_ID"
python3 src/cli/if-witness.py export --format json --output "sip-call-${TRACE_ID}.json"
```

**Cost model:** $0.0015 per complete call

---

## Cross-Session Linking

**Link all sessions with single trace ID:**

```bash
# Use same TRACE_ID across all sessions
TRACE_ID="req-$(date +%Y%m%d-%s)"

# Session 1: Publish frame
python3 src/cli/if-witness.py log --event "ndi_frame_published" \
  --component "IF.witness.ndi-publisher" \
  --trace-id "$TRACE_ID" ...

# Session 2: WebRTC setup
python3 src/cli/if-witness.py log --event "sdp_offer_created" \
  --component "IF.witness.webrtc" \
  --trace-id "$TRACE_ID" ...

# Session 3: H.323 admission
python3 src/cli/if-witness.py log --event "h323_arq_sent" \
  --component "IF.witness.h323" \
  --trace-id "$TRACE_ID" ...

# Session 4: SIP call
python3 src/cli/if-witness.py log --event "sip_invite_sent" \
  --component "IF.witness.sip" \
  --trace-id "$TRACE_ID" ...

# Query complete provenance chain
python3 src/cli/if-witness.py trace "$TRACE_ID"

# View all costs across sessions
python3 src/cli/if-optimise.py report --trace-id "$TRACE_ID"
```

---

## Troubleshooting

### 1. "Command not found: if-witness.py"

**Fix:** Use absolute path or check installation
```bash
python3 /home/user/infrafabric/src/cli/if-witness.py log ...
# OR
export PYTHONPATH=/home/user/infrafabric/src:$PYTHONPATH
python3 src/cli/if-witness.py log ...
```

### 2. "Database locked or permission denied"

**Fix:** Check directory permissions
```bash
chmod 700 ~/.if-witness/
chmod 644 ~/.if-witness/witness.db
# Or reset if corrupted
rm -rf ~/.if-witness/
python3 src/cli/if-witness.py verify  # Reinitialize
```

### 3. "Witness logging blocked my operation"

**Fix:** Use background logging with timeout
```bash
# Non-blocking wrapper
timeout 2s python3 src/cli/if-witness.py log ... || echo "⚠️ Timeout, continuing"

# Or batch logs asynchronously
python3 src/cli/if-witness.py log ... &
# Continue immediately
```

### 4. "Cost doesn't match estimate"

**Fix:** Verify token rates and model
```bash
# Check model pricing
python3 src/cli/if-optimise.py rates

# Verify logged tokens
python3 src/cli/if-witness.py trace "$TRACE_ID" --format json | grep tokens

# Manual calculation: cost = (tokens_in × $0.00000025) + (tokens_out × $0.00000125)
```

### 5. "Budget exceeded"

**Fix:** Adjust budget or reduce operations
```bash
# Check current usage
python3 src/cli/if-optimise.py budget --period month

# View by component
python3 src/cli/if-optimise.py report --group-by component

# Increase budget
python3 src/cli/if-optimise.py budget --set 1000.0 --period month

# Or optimize: batch logs, use cheaper model, reduce payload size
```

---

## Quick Reference

| Session | Event | Cost | Use Case |
|---------|-------|------|----------|
| 1 (NDI) | `ndi_frame_published` | $0.000001 | Frame integrity tracking |
| 2 (WebRTC) | `sdp_offer_created` | $0.0005 | Connection negotiation |
| 3 (H.323) | `h323_arq_sent` | $0.0003 | Admission control |
| 4 (SIP) | `sip_invite_sent` | $0.0005 | Call initiation |

**Pro tip:** Use same `TRACE_ID` across all sessions for complete provenance chain.

---

**Full reference:** See [CLI-INTEGRATION-GUIDE.md](./CLI-INTEGRATION-GUIDE.md)
