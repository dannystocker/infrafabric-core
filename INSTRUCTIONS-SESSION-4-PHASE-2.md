# Session 4 (SIP) - Phase 2 Instructions

**Status:** Phase 1 Complete ✅
**Next Phase:** End-to-End Integration + Security + Monitoring

## Task 1: Full Integration Test
Test the complete call flow: External expert (SIP) → Guardian council (H.323) → Agent mesh (WebRTC) → Evidence stream (NDI)

**Deliverables:**
- End-to-end test script: `tests/test_full_sip_escalate_flow.py`
- Test scenario:
  1. External expert initiates SIP call (IF.ESCALATE)
  2. SIP proxy validates IF.guard policy
  3. H.323 gateway bridges to Guardian council MCU
  4. WebRTC agent mesh shares real-time context
  5. NDI stream provides evidence video to Guardians
- Success criteria: <2s call setup, <100ms audio latency, all IF.witness logs present

**Use IF.swarm:**
- Spawn 1 Sonnet agent: Integration test implementation
- Spawn 2 Haiku agents: Test fixtures, documentation

## Task 2: Production Security Hardening
Harden SIP proxy for production deployment.

**Deliverables:**
- Enable TLS (SIP over TLS, port 5061)
- Implement digest authentication (reject unauthenticated INVITE)
- Rate limiting (max 10 calls/minute per external expert)
- IP allowlist (only approved expert organizations)
- Update config/kamailio.cfg with security settings

**Use Sonnet** (security-critical)

## Task 3: Monitoring and Observability
Full observability for IF.guard compliance audits.

**Deliverables:**
- Grafana dashboard: Active SIP calls, call duration, error rates, latency
- IF.witness integration: Log every SIP INVITE/ACK/BYE with trace_id
- Prometheus metrics export: `sip_calls_total`, `sip_call_duration_seconds`, `sip_errors_total`
- Alert rules: >5 failed calls in 5 minutes → notify IF.guard

**Use Haiku** for dashboards/config, **Sonnet** for IF.witness integration

## Completion Protocol
After finishing:
1. Commit to claude/realtime-workstream-4-sip
2. Push to origin
3. Create STATUS-PHASE-2.md
4. **AUTO-CHECK FOR PHASE 3:**
   ```bash
   git pull origin claude/realtime-workstream-4-sip
   [ -f INSTRUCTIONS-SESSION-4-PHASE-3.md ] && cat INSTRUCTIONS-SESSION-4-PHASE-3.md || while true; do sleep 60; git pull --quiet; [ -f INSTRUCTIONS-SESSION-4-PHASE-3.md ] && break; done
   ```

**Estimated Time:** 6-8 hours with swarms
**Estimated Cost:** $12-18

Begin Phase 2 integration!
