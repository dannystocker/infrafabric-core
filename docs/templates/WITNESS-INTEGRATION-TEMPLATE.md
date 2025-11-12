# IF.witness Integration Template

**Copy this template for your session's witness integration documentation**

**Session:** {SESSION_NAME} (e.g., Session 2 - WebRTC)
**Protocol:** {PROTOCOL} (e.g., WebRTC, SIP, H.323, etc.)
**Last Updated:** {DATE}

---

## Overview

### What Events Should We Record?

For **{PROTOCOL}** integration, we record the following event types:

| Event Type | Frequency | Priority | Example |
|------------|-----------|----------|---------|
| `{protocol}_session_started` | Per session | High | WebRTC peer connection established |
| `{protocol}_state_change` | 0.1-1/sec | High | Connection state: connecting → connected |
| `{protocol}_error` | On error | Critical | DTLS handshake failure |
| `{protocol}_quality_change` | 0.1-1/sec | Medium | Bitrate adjusted 5Mbps → 2Mbps |
| `{protocol}_session_ended` | Per session | High | Peer connection closed |

**Rule:** Record **decision points** and **state changes**, not per-packet/per-frame data.

---

## Integration Checklist

Use this checklist to track your witness integration:

### Phase 1: Setup (15 min)
- [ ] Initialize `WitnessRecorder` in session startup
- [ ] Load signing keys from config (`/etc/infrafabric/keys/witness-{session}.key`)
- [ ] Verify key permissions (readable by session only)
- [ ] Test basic event recording with `witness.record_event()`

### Phase 2: Event Definition (20 min)
- [ ] Define {PROTOCOL}-specific event types (see table above)
- [ ] Create event data schemas (what fields to include)
- [ ] Document event semantics (what each event means)
- [ ] Add examples to this document

### Phase 3: Integration Points (30 min)
- [ ] Identify where in code to record events
- [ ] Add `witness.record_event()` calls at integration points
- [ ] Include relevant context (session ID, protocol state, error details)
- [ ] Test event recording in development environment

### Phase 4: Verification (15 min)
- [ ] Implement chain verification (periodic or on-demand)
- [ ] Add verification to health checks
- [ ] Test tampering detection
- [ ] Document verification procedures

### Phase 5: Production Readiness (20 min)
- [ ] Configure key storage (etcd, filesystem, HSM)
- [ ] Set up monitoring (event rate, verification status)
- [ ] Document operational procedures
- [ ] Add runbook entries for witness failures

---

## Code Examples

### 1. Initialize Witness Recorder

Add this to your session's initialization code:

```python
from infrafabric.witness import WitnessRecorder

class {Session}Agent:
    def __init__(self, config):
        # Initialize witness recorder
        self.witness = WitnessRecorder(
            session_id="{session-id}",  # e.g., "session-2-webrtc"
            key_path=config.witness.key_path,  # e.g., "/etc/infrafabric/keys/witness.key"
            async_mode=True  # Use async for better performance
        )

        # Verify witness is working
        self.witness.record_event(
            event_type="session_initialized",
            data={
                "session": "{session-id}",
                "protocol": "{PROTOCOL}",
                "version": "1.0"
            }
        )
```

### 2. Record Protocol Session Start

```python
def start_{protocol}_session(self, session_params):
    """Start {PROTOCOL} session and record in witness"""

    # Start your protocol session
    session = self.{protocol}_engine.create_session(session_params)

    # Record in witness
    self.witness.record_event(
        event_type="{protocol}_session_started",
        data={
            "session_id": session.id,
            # Add protocol-specific fields:
            # For WebRTC: {"peer_id": ..., "sdp_type": "offer"}
            # For SIP: {"call_id": ..., "from_uri": ..., "to_uri": ...}
            # For H.323: {"conference_id": ..., "terminal_id": ...}
            "config": {
                # Include relevant config (codecs, quality, etc.)
            }
        },
        metadata={
            "agent": "{session-id}",
            "initiator": "user|system|other_session"
        }
    )

    return session
```

### 3. Record State Changes

```python
def on_{protocol}_state_change(self, session_id, old_state, new_state, reason=None):
    """Record protocol state change in witness"""

    self.witness.record_event(
        event_type="{protocol}_state_change",
        data={
            "session_id": session_id,
            "from_state": old_state,
            "to_state": new_state,
            "reason": reason  # e.g., "timeout", "user_hangup", "network_error"
        },
        metadata={
            "agent": "{session-id}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
```

### 4. Record Errors

```python
def on_{protocol}_error(self, session_id, error_type, error_details):
    """Record protocol error in witness"""

    self.witness.record_event(
        event_type="{protocol}_error",
        data={
            "session_id": session_id,
            "error_type": error_type,  # e.g., "connection_timeout", "codec_negotiation_failed"
            "error_code": error_details.code,
            "error_message": error_details.message,
            "recovery_action": error_details.recovery  # What you did to recover
        },
        metadata={
            "agent": "{session-id}",
            "severity": "error|critical|warning"
        }
    )
```

### 5. Record Session End

```python
def end_{protocol}_session(self, session_id, reason="normal"):
    """End {PROTOCOL} session and record in witness"""

    # Get session stats before closing
    stats = self.{protocol}_engine.get_session_stats(session_id)

    # Record in witness
    self.witness.record_event(
        event_type="{protocol}_session_ended",
        data={
            "session_id": session_id,
            "reason": reason,  # "normal", "timeout", "error", "user_requested"
            "duration_seconds": stats.duration,
            # Add protocol-specific stats:
            # For WebRTC: {"packets_sent": ..., "packets_lost": ...}
            # For SIP: {"call_duration": ..., "final_response": ...}
            # For H.323: {"conference_duration": ..., "participant_count": ...}
        }
    )

    # Close session
    self.{protocol}_engine.close_session(session_id)
```

### 6. Verify Chain Periodically

```python
from infrafabric.witness import WitnessVerifier

class {Session}Agent:
    def __init__(self, config):
        self.witness = WitnessRecorder(...)
        self.verifier = WitnessVerifier()

        # Start periodic verification (every 5 minutes)
        self.start_periodic_verification()

    def start_periodic_verification(self):
        """Verify witness chain every 5 minutes"""

        async def verify_loop():
            while True:
                try:
                    result = self.verifier.verify_chain(
                        chain_id="{session-id}",
                        start_event=-1000,  # Last 1000 events
                        end_event=None
                    )

                    if result.valid:
                        self.logger.info(f"✅ Witness chain valid ({result.event_count} events)")
                    else:
                        self.logger.error(f"❌ Witness chain broken at event {result.break_point}")
                        # Alert ops team
                        self.alert_manager.send_alert(
                            severity="critical",
                            message=f"Witness chain integrity violation at event {result.break_point}"
                        )

                except Exception as e:
                    self.logger.error(f"Witness verification failed: {e}")

                await asyncio.sleep(300)  # 5 minutes

        asyncio.create_task(verify_loop())
```

---

## Event Schemas

Define your {PROTOCOL}-specific event data schemas here.

### Event: `{protocol}_session_started`

```json
{
  "event_type": "{protocol}_session_started",
  "timestamp": "2025-11-12T14:32:15.823Z",
  "agent": "{session-id}",
  "data": {
    "session_id": "unique-session-id",
    // Add protocol-specific fields
  },
  "metadata": {
    "initiator": "user|system|other_session",
    "trace_id": "distributed-trace-id"
  },
  "signature": "[Ed25519 signature]",
  "hash": "[SHA-256 hash]",
  "prev_hash": "[Previous event hash]"
}
```

**Fields:**
- `session_id` (string, required): Unique identifier for this {PROTOCOL} session
- {Add protocol-specific fields here}

### Event: `{protocol}_state_change`

```json
{
  "event_type": "{protocol}_state_change",
  "data": {
    "session_id": "unique-session-id",
    "from_state": "previous_state",
    "to_state": "new_state",
    "reason": "why_state_changed"
  }
}
```

**Valid States for {PROTOCOL}:**
- {List valid states, e.g., for WebRTC: "new", "connecting", "connected", "disconnected", "failed", "closed"}

### Event: `{protocol}_error`

```json
{
  "event_type": "{protocol}_error",
  "data": {
    "session_id": "unique-session-id",
    "error_type": "error_category",
    "error_code": "protocol_specific_code",
    "error_message": "human_readable_message",
    "recovery_action": "what_was_done_to_recover"
  },
  "metadata": {
    "severity": "warning|error|critical"
  }
}
```

**Common Error Types for {PROTOCOL}:**
- {List common errors, e.g., for WebRTC: "ice_connection_failed", "dtls_handshake_failed", "datachannel_error"}

### Event: `{protocol}_session_ended`

```json
{
  "event_type": "{protocol}_session_ended",
  "data": {
    "session_id": "unique-session-id",
    "reason": "normal|timeout|error|user_requested",
    "duration_seconds": 3600,
    // Add protocol-specific stats
  }
}
```

---

## Testing

### Unit Tests

Create unit tests to verify witness integration:

```python
import pytest
from infrafabric.witness import WitnessRecorder, WitnessVerifier

class Test{Protocol}WitnessIntegration:

    def setup_method(self):
        self.witness = WitnessRecorder(
            session_id="{session-id}-test",
            key_path="/tmp/test-witness.key"
        )
        self.verifier = WitnessVerifier()

    def test_record_{protocol}_session_lifecycle(self):
        """Test recording complete {PROTOCOL} session lifecycle"""

        # Start session
        event1 = self.witness.record_event(
            event_type="{protocol}_session_started",
            data={"session_id": "test-session-1"}
        )
        assert event1.hash is not None

        # State change
        event2 = self.witness.record_event(
            event_type="{protocol}_state_change",
            data={
                "session_id": "test-session-1",
                "from_state": "connecting",
                "to_state": "connected"
            }
        )
        assert event2.prev_hash == event1.hash

        # End session
        event3 = self.witness.record_event(
            event_type="{protocol}_session_ended",
            data={"session_id": "test-session-1", "reason": "normal"}
        )
        assert event3.prev_hash == event2.hash

        # Verify chain
        result = self.verifier.verify_chain(chain_id="{session-id}-test")
        assert result.valid
        assert result.event_count == 3

    def test_detect_tampering(self):
        """Test that tampering is detected"""

        # Record events
        event1 = self.witness.record_event("{protocol}_session_started", {"session_id": "test"})
        event2 = self.witness.record_event("{protocol}_session_ended", {"session_id": "test"})

        # Tamper with event1 data
        self.witness.storage.update_event(event1.id, {"session_id": "tampered"})

        # Verification should fail
        result = self.verifier.verify_chain(chain_id="{session-id}-test")
        assert not result.valid
        assert result.break_point == event1.id
```

### Integration Tests

Test witness integration with your {PROTOCOL} engine:

```python
class Test{Protocol}EngineWithWitness:

    def test_full_{protocol}_flow_with_witness(self):
        """Test complete {PROTOCOL} flow records all witness events"""

        agent = {Session}Agent(config)

        # Start session
        session = agent.start_{protocol}_session(params)

        # Verify session_started event was recorded
        events = agent.witness.query({"event_type": "{protocol}_session_started"})
        assert len(events) == 1
        assert events[0].data["session_id"] == session.id

        # Simulate state change
        agent.on_{protocol}_state_change(session.id, "connecting", "connected")

        # Verify state_change event was recorded
        events = agent.witness.query({"event_type": "{protocol}_state_change"})
        assert len(events) == 1

        # End session
        agent.end_{protocol}_session(session.id)

        # Verify session_ended event was recorded
        events = agent.witness.query({"event_type": "{protocol}_session_ended"})
        assert len(events) == 1

        # Verify entire chain
        result = agent.verifier.verify_chain(chain_id="{session-id}")
        assert result.valid
        assert result.event_count >= 3  # At least start, state_change, end
```

---

## Operational Procedures

### Monitoring

Add these Prometheus metrics to your session:

```python
from prometheus_client import Counter, Histogram

# Witness event recording metrics
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

# Witness verification metrics
witness_verification_failures = Counter(
    'witness_verification_failures_total',
    'Total witness chain verification failures',
    ['session']
)

# Use in code
def record_event_with_metrics(self, event_type, data):
    start_time = time.time()

    event = self.witness.record_event(event_type, data)

    latency = time.time() - start_time
    witness_events_recorded.labels(session="{session-id}", event_type=event_type).inc()
    witness_recording_latency.labels(session="{session-id}").observe(latency)

    return event
```

### Alerting Rules

Add these Prometheus alert rules:

```yaml
groups:
  - name: {session}_witness
    rules:
      - alert: {Session}WitnessRecordingFailed
        expr: rate(witness_events_recorded_total{{session="{session-id}"}}[5m]) == 0
        for: 5m
        labels:
          severity: warning
          component: witness
        annotations:
          summary: "{Session} witness not recording events"
          description: "No witness events recorded for {session-id} in last 5 minutes"

      - alert: {Session}WitnessChainBroken
        expr: witness_verification_failures_total{{session="{session-id}"}} > 0
        labels:
          severity: critical
          component: witness
        annotations:
          summary: "{Session} witness chain integrity violation"
          description: "Witness chain verification failed for {session-id}"

      - alert: {Session}WitnessHighLatency
        expr: histogram_quantile(0.95, witness_recording_latency_seconds{{session="{session-id}"}}) > 0.01
        for: 5m
        labels:
          severity: warning
          component: witness
        annotations:
          summary: "{Session} witness recording latency high"
          description: "p95 witness recording latency >10ms for {session-id}"
```

### Runbook Entries

#### Runbook: Witness Not Recording Events

**Symptoms:** Alert `{Session}WitnessRecordingFailed` firing

**Investigation:**
1. Check if witness is enabled in config:
   ```bash
   grep "witness.enabled" /etc/infrafabric/config/{session}.yaml
   ```

2. Check witness logs for errors:
   ```bash
   journalctl -u infrafabric-{session} | grep "witness"
   ```

3. Test event recording manually:
   ```python
   from infrafabric.witness import WitnessRecorder
   witness = WitnessRecorder(session_id="{session-id}", key_path="/etc/infrafabric/keys/witness.key")
   witness.record_event("test_event", {"test": "data"})
   ```

**Resolution:**
- If config disabled: Enable witness and restart service
- If key missing: Restore key from backup or generate new key (requires key rotation)
- If etcd unavailable: Check etcd cluster health

#### Runbook: Witness Chain Broken

**Symptoms:** Alert `{Session}WitnessChainBroken` firing

**Investigation:**
1. Get chain verification details:
   ```python
   from infrafabric.witness import WitnessVerifier
   verifier = WitnessVerifier()
   result = verifier.verify_chain(chain_id="{session-id}")
   print(f"Break point: {result.break_point}")
   print(f"Expected hash: {result.expected_hash}")
   print(f"Actual hash: {result.actual_hash}")
   ```

2. Check event details at break point:
   ```python
   event = witness.get_event(event_id=result.break_point)
   print(json.dumps(event.data, indent=2))
   ```

3. Check if event was modified:
   ```bash
   # Check etcd audit logs
   etcdctl get /infrafabric/witness/{session-id}/events/{event-id} --print-value-only
   ```

**Resolution:**
- If tampering detected: Escalate to security team, investigate access logs
- If storage corruption: Restore from backup, verify restored chain
- If hash algorithm mismatch: Check witness library version (possible version skew)

---

## Configuration

Add witness configuration to your session's config file:

```yaml
# /etc/infrafabric/config/{session}.yaml

witness:
  enabled: true

  # Key storage
  key_storage: etcd  # etcd, filesystem, hsm, kms
  key_path: /infrafabric/keys/witness/{session-id}

  # Recording options
  async_mode: true  # Use async recording for better performance
  batch_size: 100  # Batch events before writing to storage
  flush_interval_ms: 100  # Flush batch every 100ms

  # Storage backend
  storage:
    backend: etcd
    etcd:
      endpoints:
        - https://etcd-1:2379
        - https://etcd-2:2379
        - https://etcd-3:2379
      timeout_seconds: 5
      ca_cert: /etc/infrafabric/certs/ca.crt
      cert_file: /etc/infrafabric/certs/{session}-client.crt
      key_file: /etc/infrafabric/certs/{session}-client.key

  # Verification options
  verification:
    enabled: true
    interval_seconds: 300  # Verify every 5 minutes
    lookback_events: 1000  # Verify last 1000 events

  # Retention
  retention:
    retention_days: 90  # Keep 3 months
    archive_after_days: 30  # Archive to S3 after 30 days
    archive_backend: s3
    s3:
      bucket: infrafabric-witness-archive
      region: us-east-1
      prefix: {session-id}/
```

---

## Acceptance Criteria

Check off when complete:

### Functional Requirements
- [ ] Witness records all {PROTOCOL} session lifecycle events (start, state changes, end)
- [ ] Witness records all {PROTOCOL} errors with context
- [ ] Events include sufficient context for audit/debugging
- [ ] Hash chain verification passes for all recorded events
- [ ] Tampering is detected within 1 verification cycle

### Performance Requirements
- [ ] Event recording latency <5ms (p95)
- [ ] Event recording throughput >500 events/sec
- [ ] Verification latency <500ms for 1000 events
- [ ] Witness overhead <1% of CPU usage

### Operational Requirements
- [ ] Monitoring metrics exposed (recording rate, latency, verification status)
- [ ] Alerts configured for recording failures and chain breaks
- [ ] Runbook entries added for common witness issues
- [ ] Configuration documented and tested

### Security Requirements
- [ ] Signing keys stored securely (not in version control)
- [ ] Key permissions restricted (readable by session only)
- [ ] Witness events don't contain sensitive data (passwords, PII)
- [ ] Key rotation procedure documented and tested

---

## Resources

- **IF.witness API Reference:** See `infrafabric/witness.py`
- **NDI Witness FAQ:** See `docs/NDI-WITNESS-FAQ.md`
- **Hash Chain Example:** See `examples/witness-hash-chain-demo.py`
- **Phase 0 Performance:** See `docs/PHASE-0-PERFORMANCE.md`

---

## Questions & Support

- **Slack:** `#infrafabric-witness` channel
- **GitHub Issues:** Tag with `component:witness`
- **Session 1 (NDI):** Primary witness implementation - ask for help/code review

---

**Template Version:** 1.0
**Last Updated:** 2025-11-12
**Maintained By:** Session 1 (NDI)
**Next Review:** 2025-12-12
