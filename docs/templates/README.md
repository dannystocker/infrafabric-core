# InfraFabric Documentation Templates

**Reusable templates for all sessions**

This directory contains copy-and-customize templates to accelerate documentation and integration work across all 7 sessions.

---

## Available Templates

### 1. Witness Integration

| Template | Description | Time to Complete | Audience |
|----------|-------------|------------------|----------|
| **WITNESS-QUICK-START.md** | Get witness running in 15 minutes | 15 min | Developers |
| **WITNESS-INTEGRATION-TEMPLATE.md** | Complete witness integration guide | 2-3 hours | Tech Leads |

**When to use:**
- You need to integrate IF.witness into your protocol (WebRTC, SIP, H.323, etc.)
- You want to add cryptographic audit trails to your session
- You need tamper detection for coordination events

**How to use:**
1. Copy template to your session's docs: `docs/{PROTOCOL}-WITNESS-INTEGRATION.md`
2. Replace placeholders: `{PROTOCOL}`, `{SESSION_NAME}`, `{session-id}`
3. Fill in protocol-specific event types and schemas
4. Add code snippets for your protocol's integration points
5. Test using the provided test templates

**Example:** Session 2 (WebRTC) would create `docs/WEBRTC-WITNESS-INTEGRATION.md` with event types like `webrtc_peer_connected`, `webrtc_ice_candidate_added`, etc.

---

## Future Templates (Coming Soon)

### Coordination

- **COORDINATOR-CLIENT-TEMPLATE.md** - How to integrate IF.coordinator into your session
- **TASK-CLAIMING-TEMPLATE.md** - Standard patterns for claiming and releasing tasks

### Testing

- **INTEGRATION-TEST-TEMPLATE.md** - Structure for Phase 0 integration tests
- **PROTOCOL-MOCK-TEMPLATE.md** - Creating mock protocol implementations

### Documentation

- **COMPONENT-DOC-TEMPLATE.md** - Standard structure for component documentation
- **RUNBOOK-TEMPLATE.md** - Production runbook entries for your session

### Monitoring

- **METRICS-TEMPLATE.md** - Prometheus metrics to expose from your session
- **ALERTS-TEMPLATE.md** - Standard alerting rules for session health

---

## Contributing Templates

Have a useful pattern that other sessions could use? Create a template!

### Template Checklist

- [ ] **Reusable** - Works for multiple sessions with minimal changes
- [ ] **Placeholders** - Uses `{PLACEHOLDERS}` for session-specific values
- [ ] **Complete** - Includes code, config, tests, and documentation
- [ ] **Tested** - Actually used by at least one session
- [ ] **Maintained** - Includes version number and last-updated date

### Template Structure

```markdown
# {Component} {Purpose} Template

**Copy this template for {use case}**

**Session:** {SESSION_NAME}
**Component:** {COMPONENT}
**Last Updated:** {DATE}

---

## Overview
{What this template helps you do}

---

## Checklist
- [ ] Step 1
- [ ] Step 2
...

---

## Code Examples
{Copy-paste code snippets}

---

## Testing
{How to test your implementation}

---

## Acceptance Criteria
{What "done" looks like}
```

---

## Template Usage Stats

| Template | Used By | Downloads | Last Updated |
|----------|---------|-----------|--------------|
| WITNESS-QUICK-START | Session 1 (NDI) | 1 | 2025-11-12 |
| WITNESS-INTEGRATION-TEMPLATE | Session 1 (NDI) | 1 | 2025-11-12 |

---

## Getting Help

- **Slack:** `#infrafabric-templates` channel
- **GitHub Issues:** Tag with `component:templates`
- **Session 1 (NDI):** Created witness templates - ask for help customizing

---

**Directory Status:** ✅ Active
**Maintained By:** All sessions (contribute!)
**Review Cadence:** Monthly
