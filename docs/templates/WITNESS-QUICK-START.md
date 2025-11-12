# IF.witness Quick Start Guide

**Get witness integration running in 15 minutes**

---

## 1. Generate Signing Key (2 min)

```bash
# Generate Ed25519 key pair
ssh-keygen -t ed25519 -f /tmp/witness-${SESSION_ID}.key -N ""

# Set secure permissions
chmod 600 /tmp/witness-${SESSION_ID}.key
chmod 644 /tmp/witness-${SESSION_ID}.key.pub

# Move to secure location
sudo mv /tmp/witness-${SESSION_ID}.key /etc/infrafabric/keys/
sudo mv /tmp/witness-${SESSION_ID}.key.pub /etc/infrafabric/keys/
```

---

## 2. Initialize Witness Recorder (3 min)

Add to your session's initialization code:

```python
from infrafabric.witness import WitnessRecorder

# In your agent's __init__:
self.witness = WitnessRecorder(
    session_id="session-{N}-{protocol}",  # e.g., "session-2-webrtc"
    key_path="/etc/infrafabric/keys/witness-session-{N}.key"
)
```

---

## 3. Record First Event (2 min)

```python
# Record session initialized event
self.witness.record_event(
    event_type="session_initialized",
    data={
        "session": "session-{N}-{protocol}",
        "protocol": "{PROTOCOL}",  # WebRTC, SIP, H.323, etc.
        "version": "1.0"
    }
)

print("✅ First witness event recorded!")
```

---

## 4. Add Protocol Events (5 min)

Add these calls at key points in your protocol implementation:

```python
# Session started
self.witness.record_event(
    event_type="{protocol}_session_started",
    data={"session_id": session.id, "peer": peer_id}
)

# State changed
self.witness.record_event(
    event_type="{protocol}_state_change",
    data={"session_id": session.id, "from": old_state, "to": new_state}
)

# Error occurred
self.witness.record_event(
    event_type="{protocol}_error",
    data={"session_id": session.id, "error": error_type, "message": str(e)}
)

# Session ended
self.witness.record_event(
    event_type="{protocol}_session_ended",
    data={"session_id": session.id, "duration": duration_seconds}
)
```

---

## 5. Verify Chain (3 min)

Add verification to your health check:

```python
from infrafabric.witness import WitnessVerifier

verifier = WitnessVerifier()

def health_check():
    # Verify last 100 events
    result = verifier.verify_chain(
        chain_id="session-{N}-{protocol}",
        start_event=-100
    )

    if result.valid:
        return {"witness": "ok", "events": result.event_count}
    else:
        return {"witness": "error", "break_point": result.break_point}
```

---

## 6. Test It (5 min total)

### Test 1: Record and Verify (2 min)

```python
# Record 3 events
witness.record_event("test_1", {"data": "first"})
witness.record_event("test_2", {"data": "second"})
witness.record_event("test_3", {"data": "third"})

# Verify chain
result = verifier.verify_chain(chain_id="session-{N}-{protocol}")
assert result.valid, "Chain should be valid"
print(f"✅ Chain valid ({result.event_count} events)")
```

### Test 2: Detect Tampering (3 min)

```python
# Record events
event1 = witness.record_event("test_event", {"value": "original"})
event2 = witness.record_event("test_event", {"value": "next"})

# Tamper with first event (simulated - directly modify storage)
witness.storage.update_event(event1.id, {"value": "tampered"})

# Verification should fail
result = verifier.verify_chain(chain_id="session-{N}-{protocol}")
assert not result.valid, "Chain should be invalid after tampering"
print(f"✅ Tampering detected at event {result.break_point}")
```

---

## Done! 🎉

You now have:
- ✅ Witness recording setup
- ✅ Protocol events recorded
- ✅ Chain verification working
- ✅ Tampering detection tested

---

## Next Steps

1. **Add more event types** - See `WITNESS-INTEGRATION-TEMPLATE.md` for examples
2. **Add monitoring** - Expose Prometheus metrics for witness
3. **Configure retention** - Set up archival to S3 after 30 days
4. **Add to runbook** - Document witness procedures for ops team

---

## Troubleshooting

### "Key not found" error
```bash
# Check key exists and is readable
ls -la /etc/infrafabric/keys/witness-session-{N}.key
# Should show: -rw------- (600 permissions)
```

### "Signature verification failed"
```bash
# Check you're using the right public key
cat /etc/infrafabric/keys/witness-session-{N}.key.pub
```

### "etcd connection refused"
```bash
# Check etcd is running
etcdctl endpoint health
```

---

## Resources

- **Detailed Template:** `docs/templates/WITNESS-INTEGRATION-TEMPLATE.md`
- **FAQ:** `docs/NDI-WITNESS-FAQ.md`
- **API Reference:** `infrafabric/witness.py`
- **Ask for Help:** `#infrafabric-witness` Slack channel

---

**Time to complete:** ~15 minutes
**Difficulty:** Easy
**Support:** Session 1 (NDI) - Ask anytime!
