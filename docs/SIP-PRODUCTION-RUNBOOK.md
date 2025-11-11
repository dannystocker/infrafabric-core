# SIP ESCALATE Production Operations Runbook

**Status:** Session 4 Phase 3 - Production Runbook
**Last Updated:** 2025-11-11
**Author:** InfraFabric Operations Team
**Audience:** On-Call Engineers, DevOps, SREs

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Service Overview](#service-overview)
3. [Common Operations](#common-operations)
4. [Health Checks](#health-checks)
5. [Alert Response Procedures](#alert-response-procedures)
6. [Emergency Procedures](#emergency-procedures)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Monitoring Dashboards](#monitoring-dashboards)
9. [Escalation Procedures](#escalation-procedures)
10. [Maintenance Windows](#maintenance-windows)

---

## Quick Reference

### Emergency Contacts

| Role | Name | Phone | Email | Slack |
|------|------|-------|-------|-------|
| **On-Call Lead** | [See Pagerduty] | +1-555-0100 | oncall@infrafabric.io | #on-call |
| **SIP Expert** | Engineering Team | +1-555-0101 | sip-team@infrafabric.io | #sip-escalate |
| **Security Team** | Security Lead | +1-555-0102 | security@infrafabric.io | #security-incident |
| **IF.guard Admin** | Policy Team | +1-555-0103 | ifguard@infrafabric.io | #if-guard |

### Key URLs

| Service | URL | Port | Protocol |
|---------|-----|------|----------|
| **Kamailio SIP Proxy** | kamailio.infrafabric.local | 5060 (5061 TLS) | UDP/TCP/TLS |
| **Prometheus** | prometheus.infrafabric.io:9090 | 9090 | HTTP |
| **Grafana** | grafana.infrafabric.io | 3000 | HTTP |
| **Kamailio Logs** | `/var/log/kamailio/kamailio.log` | N/A | File |
| **IF.witness Logs** | `/var/log/infrafabric/sip_witness.log` | N/A | File |
| **Alert Dashboard** | https://alertmanager.infrafabric.io | 9093 | HTTP |

### Critical Thresholds

| Metric | Threshold | Severity | Action |
|--------|-----------|----------|--------|
| **Call Failure Rate** | >10% failures | WARNING | Investigate logs, check policy |
| **Excessive Failures** | >5 in 5 minutes | CRITICAL | Immediate escalation |
| **Call Duration** | >1 hour | WARNING | Check for stuck calls |
| **Latency (p95)** | >10 seconds | WARNING | Check H.323 bridge, network |
| **Policy Rejection Rate** | >50% | CRITICAL | Audit IF.guard policy |
| **Active Calls** | >100 concurrent | WARNING | Monitor capacity, scale if needed |
| **Proxy Down** | Not responding for 2+ min | CRITICAL | Restart Kamailio immediately |
| **5xx Errors** | >3 in 5 minutes | CRITICAL | Check Kamailio logs for errors |

### Quick Action Commands

```bash
# Check service status
systemctl status kamailio

# View recent logs
tail -f /var/log/kamailio/kamailio.log

# View security events
tail -f /var/log/infrafabric/sip_witness.log | grep SECURITY_EVENT

# Restart service
sudo systemctl restart kamailio

# Check active connections
kamctl fifo get_statistics dialog

# Monitor in real-time
watch -n 1 'curl -s http://prometheus.infrafabric.io:9090/api/v1/query?query=sip_active_calls | jq'
```

---

## Service Overview

### What is IF.ESCALATE?

IF.ESCALATE is InfraFabric's external expert escalation system. It enables the Guardian Council to bring trusted external experts into critical decision-making via SIP-based voice calls when hazardous situations are detected.

**Key Scenarios:**
- **Safety Review**: Escalate to safety experts when hazardous decisions emerge
- **Ethics Challenge**: Engage ethics experts when bias is detected
- **Security Audit**: Consult security specialists for privacy concerns
- **Alignment Verification**: Contact alignment experts when drift is suspected

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    External Expert Domain                        │
│         (Safety, Ethics, Security Experts)                       │
│              SIP 5060 (UDP/TCP) or 5061 (TLS)                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
      ┌──────────────────────────────┐
      │  Kamailio SIP Proxy          │
      │  ├─ TLS 5061 (Production)     │
      │  ├─ IF.guard Policy Gate      │
      │  ├─ IF.witness Audit Logging  │
      │  └─ Security Layers (7 total) │
      └──────────────┬─────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌─────────────┐      ┌──────────────┐
    │ H.323 MCU   │      │ WebRTC Agent │
    │ (Session 3) │      │ (Session 2)  │
    │             │      │              │
    │ Guardian    │      │ Evidence     │
    │ Council     │      │ Sharing      │
    └─────────────┘      └──────────────┘
```

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| **Kamailio SIP Proxy** | `config/kamailio-production.cfg` | SIP signaling & routing |
| **SIPEscalateProxy** | `src/communication/sip_proxy.py` | Orchestration & escalation flow |
| **IF.guard Policy Gate** | `src/communication/sip_proxy.py` | Policy decisions & expert approval |
| **SIPtoH323Bridge** | `src/communication/sip_h323_gateway.py` | Protocol bridging (SIP ↔ H.323) |
| **IF.witness Logger** | `src/communication/sip_proxy.py` | Comprehensive audit trail |
| **SecurityManager** | `src/communication/sip_security.py` | Multi-layer security validation |

### Key Dependencies

- **Kamailio 5.7+**: SIP signaling server
- **Python 3.9+**: SIP proxy orchestration
- **H.323 Gatekeeper** (Session 3): Guardian council bridging
- **WebRTC Agent Mesh** (Session 2): Evidence sharing
- **Prometheus**: Metrics collection
- **Grafana**: Dashboard visualization

---

## Common Operations

### Starting the Service

**Option 1: Using systemctl (Recommended)**

```bash
# Start Kamailio
sudo systemctl start kamailio

# Enable on boot
sudo systemctl enable kamailio

# Verify status
sudo systemctl status kamailio
```

**Option 2: Using Docker Compose (If containerized)**

```bash
# Navigate to docker directory
cd /home/user/infrafabric

# Start all services
docker-compose up -d kamailio

# View logs
docker-compose logs -f kamailio
```

**Option 3: Manual Kamailio Start**

```bash
# Start with debug logging
sudo kamailio -f /etc/kamailio/kamailio.cfg -D

# Or daemon mode
sudo kamailio -f /etc/kamailio/kamailio.cfg -d -P /var/run/kamailio.pid
```

### Stopping the Service

**Graceful Shutdown (Recommended)**

```bash
# Stop gracefully - allows existing calls to complete
sudo systemctl stop kamailio

# Verify stopped
sudo systemctl status kamailio
```

**Forced Shutdown**

```bash
# Force kill if graceful shutdown fails
sudo pkill -9 kamailio

# Verify no processes remain
ps aux | grep kamailio
```

### Restarting the Service

**Standard Restart**

```bash
# Restart Kamailio (calls will be interrupted)
sudo systemctl restart kamailio

# Watch for startup messages
tail -f /var/log/kamailio/kamailio.log
```

**Zero-Downtime Restart** (If supported)

```bash
# Check if Kamailio has hot-reload
kamctl reload
```

### Checking Service Status

```bash
# systemctl status
sudo systemctl status kamailio

# Process check
ps aux | grep kamailio | grep -v grep

# Port listening check
netstat -tlnp | grep 5060
netstat -tlnp | grep 5061

# Kamailio diagnostic info
kamailio -v

# Active connections
kamctl fifo get_statistics dialog

# Request statistics
kamctl fifo get_statistics sip_requests
```

### Viewing Logs

```bash
# Kamailio main log (all SIP events)
tail -f /var/log/kamailio/kamailio.log

# Filter by IF.witness events
tail -f /var/log/kamailio/kamailio.log | grep "IF.witness"

# Filter by IF.guard events
tail -f /var/log/kamailio/kamailio.log | grep "IF.guard"

# IF.witness audit trail (JSON format)
tail -f /var/log/infrafabric/sip_witness.log

# Parse witness events by type
cat /var/log/infrafabric/sip_witness.log | jq '.event_type' | sort | uniq -c

# Search for specific trace ID
grep "trace_id.*abc123" /var/log/infrafabric/sip_witness.log

# Security events only
grep "SECURITY_EVENT" /var/log/infrafabric/sip_witness.log | jq .
```

---

## Health Checks

### Health Endpoint Check

```bash
# If health endpoint is exposed
curl http://kamailio.infrafabric.local:8080/health

# Expected response
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "active_calls": 5,
  "registered_contacts": 42
}
```

### Prometheus Metrics Endpoint

```bash
# Query active calls metric
curl http://prometheus.infrafabric.io:9090/api/v1/query?query=sip_active_calls

# Query call failure rate
curl http://prometheus.infrafabric.io:9090/api/v1/query?query='rate(sip_calls_total{result="failed"}[5m])'

# Query policy decisions
curl http://prometheus.infrafabric.io:9090/api/v1/query?query=sip_policy_decisions_total
```

### Active Call Count Check

```bash
# Using Kamailio fifo interface
kamctl fifo get_statistics dialog
# Look for "dialog:active_dialogs" value

# Using Prometheus
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=sip_active_calls' | jq '.data.result[0].value[1]'

# Using top-like monitoring
watch -n 2 'kamctl fifo get_statistics dialog'
```

### Grafana Dashboard Check

1. **Navigate to Grafana**: https://grafana.infrafabric.io
2. **Select Dashboard**: "SIP Escalate - Production"
3. **Key Panels to Check**:
   - **Top Left**: Active Calls (should be 0-100 normally)
   - **Top Right**: Call Success Rate (target >95%)
   - **Bottom Left**: Policy Approval Rate (track rejected calls)
   - **Bottom Right**: System Load & Resources
   - **Alerts Panel**: Any firing alerts (red icons)

### Custom Health Check Script

```bash
#!/bin/bash
# /usr/local/bin/sip-health-check.sh

echo "=== SIP Service Health Check ==="
echo ""

# 1. Service status
echo "1. Service Status:"
systemctl is-active kamailio && echo "   ✓ Kamailio running" || echo "   ✗ Kamailio DOWN"

# 2. Port listening
echo "2. Ports Listening:"
netstat -tlnp 2>/dev/null | grep kamailio | grep -q 5060 && echo "   ✓ Port 5060 listening" || echo "   ✗ Port 5060 not listening"
netstat -tlnp 2>/dev/null | grep kamailio | grep -q 5061 && echo "   ✓ Port 5061 (TLS) listening" || echo "   ✗ Port 5061 not listening"

# 3. Active calls
echo "3. Active Calls:"
CALLS=$(kamctl fifo get_statistics dialog 2>/dev/null | grep "active_dialogs" | awk '{print $NF}')
echo "   Active: $CALLS"
[[ $CALLS -lt 100 ]] && echo "   ✓ Within normal range" || echo "   ⚠ High call volume"

# 4. Recent errors
echo "4. Recent Errors (last 5 minutes):"
ERRORS=$(tail -300 /var/log/kamailio/kamailio.log | grep -c "ERROR\|CRITICAL")
echo "   Error count: $ERRORS"
[[ $ERRORS -eq 0 ]] && echo "   ✓ No errors" || echo "   ⚠ Errors detected"

# 5. Disk space for logs
echo "5. Log Directory Space:"
USAGE=$(df /var/log/infrafabric | tail -1 | awk '{print $5}')
echo "   Usage: $USAGE"
[[ ${USAGE%\%} -lt 80 ]] && echo "   ✓ Healthy" || echo "   ⚠ High disk usage"

echo ""
echo "=== Health Check Complete ==="
```

**Run health check:**
```bash
bash /usr/local/bin/sip-health-check.sh
```

---

## Alert Response Procedures

### Alert 1: SIPCallFailureRate (>10% failure rate, WARNING)

**Symptoms:**
- Escalation calls intermittently failing
- Expert calls not connecting
- Call success rate dropping

**Impact:**
- External experts cannot connect to Guardian Council
- Safety/ethics review decisions delayed
- Potential audit trail gaps

**Detection:**
```
Alert fires when: (failure_rate > 10%) AND (failures exist) for 5+ minutes
Prometheus query: rate(sip_calls_total{result="failed"}[5m]) / (rate(...success...) + rate(...failed...)) > 0.1
```

**Investigation Steps:**

1. **Check recent logs**:
```bash
tail -100 /var/log/kamailio/kamailio.log | grep -E "FAILED|ERROR|INVITE"
grep "SECURITY_EVENT\|POLICY" /var/log/infrafabric/sip_witness.log | tail -20 | jq .
```

2. **Verify expert availability**:
```bash
# Check if experts are registered
kamctl fifo ul_show_contact expert-safety external.advisor
kamctl fifo ul_show_contact expert-ethics external.advisor
kamctl fifo ul_show_contact expert-security external.advisor

# Test SIP connectivity to expert
sip-options sip:expert-safety@external.advisor
```

3. **Check IF.guard policy**:
```bash
# Review recent policy rejections
grep "POLICY_REJECTED" /var/log/infrafabric/sip_witness.log | tail -10 | jq '.details'
```

4. **Monitor H.323 bridge**:
```bash
# Check H.323 gateway connectivity
grep "BRIDGE_FAILED\|bridge_external_call" /var/log/infrafabric/sip_witness.log | tail -5
```

**Remediation:**

| Cause | Action |
|-------|--------|
| **Expert unavailable** | Contact external expert org, verify SIP registration |
| **Network issue** | Check firewall, DNS resolution, routing to expert |
| **IF.guard rejecting** | Review policy settings, check expert specialization match |
| **H.323 bridge down** | Restart H.323 gateway, check Session 3 status |
| **Kamailio overloaded** | Check resource usage, consider scaling |

**Recovery:**
```bash
# If experts are registered and accessible:
# 1. Restart Kamailio
sudo systemctl restart kamailio

# 2. Verify recovery
sleep 30
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=rate(sip_calls_total{result="failed"}[5m])' | jq
```

---

### Alert 2: SIPExcessiveCallFailures (>5 in 5 minutes, CRITICAL)

**Symptoms:**
- Multiple expert calls failing
- Escalations repeatedly failing
- Cannot reach any external expert

**Impact:**
- Critical safety/ethics decisions cannot be escalated
- Guardian Council unable to consult experts
- Service degradation

**Action: IMMEDIATE ESCALATION REQUIRED**

**Investigation & Remediation:**

```bash
# 1. Get detailed failure information
grep "BRIDGE_TERMINATED\|POLICY_REJECTED\|ERROR" /var/log/infrafabric/sip_witness.log | tail -20

# 2. Check if external network is reachable
ping external.advisor  # Should work
nslookup external.advisor  # DNS should resolve

# 3. Check firewall rules
sudo iptables -L -n | grep 5060
sudo iptables -L -n | grep 5061

# 4. Check Kamailio status
sudo systemctl status kamailio
ps aux | grep kamailio | grep -v grep

# 5. If Kamailio is stuck, restart
sudo systemctl restart kamailio

# 6. Monitor recovery
watch -n 2 'curl -s http://prometheus.infrafabric.io:9090/api/v1/query?query=increase(sip_calls_total{result="failed"}[5m]) | jq ".data.result[0].value[1]"'

# 7. If still failing, escalate to SIP team
```

**Escalation Path:**
1. Page on-call SIP engineer
2. Notify IF.guard admin team
3. Check if external network is experiencing issues
4. Consider failover to backup expert endpoints

---

### Alert 3: SIPCallDurationAnomaly (>1 hour call, WARNING)

**Symptoms:**
- One or more calls lasting unusually long (>60 minutes)
- Possible resource leak
- Potential stuck call

**Impact:**
- Resource exhaustion (RTP ports, memory)
- May prevent new escalations

**Investigation:**

```bash
# Find long-running calls
grep "BRIDGE_ESTABLISHED" /var/log/infrafabric/sip_witness.log | \
  jq 'select(.details.duration_seconds > 3600) | {call_id: .details.sip_call_id, duration: .details.duration_seconds}'

# Get current active calls with duration
kamctl fifo get_statistics dialog | grep duration
```

**Remediation:**

```bash
# 1. Identify stuck call ID
STUCK_CALL_ID="sip-call-xxxxx"

# 2. Terminate the call (via API or manual)
# Contact the active expert to end call voluntarily

# 3. If expert unresponsive, force terminate
# This requires implementation in SIPEscalateProxy:
curl -X POST http://localhost:8000/api/calls/$STUCK_CALL_ID/terminate

# 4. Verify call terminated
grep "$STUCK_CALL_ID" /var/log/infrafabric/sip_witness.log | tail -5
```

---

### Alert 4: SIPHighLatency (p95 >10 seconds, WARNING)

**Symptoms:**
- Slow call connections
- Audio delay between expert and council
- Expert taking 10+ seconds to answer

**Impact:**
- Poor user experience
- Potential for miscommunication
- May indicate network congestion

**Investigation:**

```bash
# Check latency distribution
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=histogram_quantile(0.95,rate(sip_call_duration_seconds_bucket[5m]))' | jq

# Check H.323 gateway latency
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=h323_bridge_latency_p95' | jq

# Check network latency to experts
for expert in expert-safety expert-ethics expert-security; do
  echo "Latency to $expert:"
  ping -c 3 ${expert}.external.advisor | tail -1
done

# Check Kamailio processing latency
grep "sip_method_duration" /var/log/infrafabric/sip_witness.log | jq '.details.duration_ms' | sort -n | tail -5
```

**Remediation:**

| Cause | Action |
|-------|--------|
| **Network congestion** | Check QoS, network utilization, consider traffic shaping |
| **H.323 bridge slow** | Check H.323 gateway load, consider scaling |
| **Expert slow to answer** | Contact expert org about SIP phone responsiveness |
| **Kamailio overloaded** | Check CPU/memory, consider scaling proxy |

---

### Alert 5: IFGuardHighRejectionRate (>50% rejected, CRITICAL)

**Symptoms:**
- Most escalation requests being rejected
- Calls failing at policy stage
- Unable to reach any expert

**Impact:**
- Cannot escalate critical decisions
- Service essentially non-functional

**Action: IMMEDIATE INVESTIGATION REQUIRED**

**Investigation:**

```bash
# Check what policies are rejecting
grep "POLICY_REJECTED" /var/log/infrafabric/sip_witness.log | tail -20 | jq '.details.reason'

# Check IF.guard registry
# Login to IF.guard admin console at: https://ifguard.infrafabric.io/admin
# Or query directly:
python3 -c "
from src.communication.sip_proxy import IFGuardPolicy
policy = IFGuardPolicy()
for expert_id, info in policy.approved_experts.items():
    print(f'{expert_id}: {info}')
"

# Check signature validation failures
grep "signature.*invalid\|verification.*failed" /var/log/infrafabric/sip_witness.log | wc -l
```

**Common Causes & Fixes:**

1. **Expert not in registry**:
```python
# Add missing expert to IFGuardPolicy.approved_experts
# File: src/communication/sip_proxy.py (lines 62-143)
# Restart Kamailio after modification
sudo systemctl restart kamailio
```

2. **Specialization mismatch** (expert certified for "safety" but request is "ethics"):
```bash
# Check what hazard types the request contains
grep "X-IF-Hazard\|hazards" /var/log/kamailio/kamailio.log | tail -10
# Match against expert specialization
```

3. **Signature validation failing**:
```bash
# Check if Ed25519 signatures are properly formatted
grep "X-IF-Signature" /var/log/kamailio/kamailio.log | head -1
# Verify signature format: base64-encoded
```

**Recovery:**
```bash
# Temporarily disable signature verification (emergency only)
# Edit: src/communication/sip_proxy.py
# Change: if not approval["approved"]:
#     to: if EMERGENCY_MODE and hazard in approved_experts:

# After fix, notify IF.guard team
```

---

### Alert 6: IFGuardHighEvaluationLatency (p99 >1 second, WARNING)

**Symptoms:**
- Policy evaluation taking too long
- Delays in expert call setup
- Kamailio Python integration slow

**Impact:**
- Longer escalation time (30-100ms becomes 1s+)
- User-facing latency increase
- Possible call timeouts

**Investigation:**

```bash
# Check IF.guard evaluation times
grep "policy_eval_duration" /var/log/infrafabric/sip_witness.log | jq '.details.eval_duration_ms' | sort -rn | head -10

# Check if registry queries are slow
# Monitor: src/communication/sip_proxy.py line 118: if_guard.approve_external_call()

# Check Python process CPU/memory
ps aux | grep python | grep sip_proxy
top -p $(pgrep -f sip_proxy)
```

**Remediation:**

```bash
# 1. Check for slow DNS queries
grep "DNS\|nslookup\|getaddrinfo" /var/log/kamailio/kamailio.log

# 2. Optimize IF.guard registry (cache expert lookups)
# File: src/communication/sip_proxy.py
# Add caching: from functools import lru_cache

# 3. Restart with optimization
sudo systemctl restart kamailio

# 4. Verify improvement
watch -n 2 'grep "policy_eval_duration" /var/log/infrafabric/sip_witness.log | tail -1 | jq ".details.eval_duration_ms"'
```

---

### Alert 7: SIPErrorRateElevated (>5% errors, WARNING)

**Symptoms:**
- Increasing 4xx/5xx SIP responses
- Protocol errors in call setup
- Possible Kamailio configuration issue

**Impact:**
- Some escalations failing
- Degraded service

**Investigation:**

```bash
# Get error breakdown by status code
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=increase(sip_errors_total[5m])' | jq '.data.result[] | {status_code: .metric.status_code, count: .value[1]}'

# Check Kamailio error logs
grep -E "40[0-9]|41[0-9]|50[0-9]|51[0-9]" /var/log/kamailio/kamailio.log | tail -20

# Common errors
# 400 Bad Request: Missing IF headers (X-IF-Trace-ID, X-IF-Hazard)
# 403 Forbidden: IP not allowlisted, auth failed
# 404 Not Found: Expert URI invalid
# 408 Request Timeout: Expert not responding
# 500 Server Error: Kamailio internal error
```

**Remediation:**
| Error | Fix |
|-------|-----|
| **400** | Ensure client sends X-IF-Trace-ID and X-IF-Hazard headers |
| **403** | Verify IP allowlist, check authentication, verify IF.guard policy |
| **404** | Verify expert SIP URI is correct and registered |
| **408** | Check expert availability, increase timeout if needed |
| **500** | Check Kamailio logs for internal errors, restart if needed |

---

### Alert 8: SIPActiveCallsHigh (>100 concurrent, WARNING)

**Symptoms:**
- High number of simultaneous escalation calls
- System approaching capacity
- Potential for new calls to fail

**Impact:**
- Risk of service degradation
- May start rejecting new calls

**Investigation:**

```bash
# Get exact call count
kamctl fifo get_statistics dialog | grep active_dialogs

# List all active calls
kamctl fifo dp_list

# Check if calls are stuck (should be <10 minutes typical)
grep "BRIDGE_ESTABLISHED\|STATE_CHANGE" /var/log/infrafabric/sip_witness.log | tail -50 | jq '.details | {call_id, duration_seconds}'
```

**Remediation:**

```bash
# 1. Check if calls are completing normally
OLDEST_CALL_AGE=$(grep "BRIDGE_ESTABLISHED" /var/log/infrafabric/sip_witness.log | tail -1 | jq '.timestamp' | date -f - +%s)
NOW=$(date +%s)
AGE=$((NOW - OLDEST_CALL_AGE))
echo "Oldest active call age: $AGE seconds"

# 2. If calls are stuck, terminate them
# (implement in SIPEscalateProxy or via administrative interface)

# 3. Monitor and scale if needed
watch -n 5 'kamctl fifo get_statistics dialog | grep active'

# 4. If persistent, scale Kamailio horizontally (add more proxy instances)
```

---

### Alert 9: SIPProxyDown (proxy not responding for 2+ minutes, CRITICAL)

**Symptoms:**
- No SIP responses from proxy
- All escalation attempts failing
- Service completely unavailable

**Impact:**
- ALL escalations failing
- Service DOWN

**Action: IMMEDIATE RESTART REQUIRED**

**Emergency Recovery:**

```bash
# 1. Check if process is running
ps aux | grep kamailio | grep -v grep

# 2. Attempt graceful restart
sudo systemctl restart kamailio

# 3. Wait for startup
sleep 10

# 4. Verify status
sudo systemctl status kamailio

# 5. Test connectivity
echo "Testing SIP connectivity..."
timeout 5 bash -c 'cat < /dev/null > /dev/tcp/127.0.0.1/5060' && echo "✓ Port 5060 responsive" || echo "✗ Port 5060 not responding"

# 6. If restart fails, check for errors
journalctl -u kamailio -n 50 --no-pager

# 7. If kernel crash suspected
dmesg | tail -20
```

**If Restart Fails:**

```bash
# Check configuration
sudo kamailio -c -f /etc/kamailio/kamailio.cfg

# If config error, fallback to backup config
cp /etc/kamailio/kamailio.cfg /etc/kamailio/kamailio.cfg.broken
cp /etc/kamailio/kamailio.cfg.backup /etc/kamailio/kamailio.cfg
sudo systemctl restart kamailio

# Contact SIP team immediately
# Page: #on-call in Slack
```

---

### Alert 10: SIPServerErrors (5xx responses >3 in 5 minutes, CRITICAL)

**Symptoms:**
- Server errors (500, 502, 503, etc.)
- Kamailio internal failures
- Python integration failures

**Impact:**
- Some/all escalations failing

**Immediate Actions:**

```bash
# 1. Get detailed error information
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=increase(sip_errors_total{status_code=~"5.."}[5m])' | jq

# 2. Check Kamailio error logs
tail -50 /var/log/kamailio/kamailio.log | grep -E "ERROR|CRITICAL|error"

# 3. Check Python integration logs
grep -i "python\|error\|traceback" /var/log/kamailio/kamailio.log | tail -20

# 4. Check system resources
free -h  # Memory
df -h    # Disk
top -bn1 | head -20  # CPU

# 5. Restart Kamailio if resources OK
sudo systemctl restart kamailio

# 6. Verify fix
sleep 10
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=sip_errors_total{status_code=~"5.."}' | jq
```

---

### Alert 11: SIPMethodLatencyHigh (specific SIP method >5 seconds, WARNING)

**Symptoms:**
- Specific SIP method (e.g., INVITE) is slow
- Other methods may be normal
- Protocol-level latency issue

**Investigation:**

```bash
# Check which method is slow
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=histogram_quantile(0.95,rate(sip_method_duration_seconds_bucket[5m]))' | jq '.data.result[] | {method: .metric.method, latency: .value[1]}'

# Check Kamailio timing for that method
grep "method.*latency\|duration" /var/log/kamailio/kamailio.log | grep "INVITE" | tail -20

# Common slow methods:
# - INVITE: Initial call setup (may involve policy checks, bridge creation)
# - BYE: Call termination
# - ACK: Final acknowledgment
```

**Remediation:**

| Method | Likely Cause | Fix |
|--------|--------------|-----|
| **INVITE** | Policy evaluation, H.323 bridge setup slow | Optimize IF.guard, check H.323 gateway |
| **BYE** | Bridge teardown slow | Check bridge termination logic |
| **ACK** | SIP dialog establishment slow | Check network latency, Kamailio config |

---

### Alert 12: PolicyDecisionRateAnomalous (very low decision rate, WARNING)

**Symptoms:**
- Very few policy decisions being made
- No recent scalations
- Possible system idle or stalled

**Impact:**
- May indicate system not functioning
- Or simply no escalations needed (informational)

**Investigation:**

```bash
# Check if system is actually receiving escalation requests
grep "INVITE\|handle_escalate" /var/log/kamailio/kamailio.log | wc -l

# Check policy decision events
grep "POLICY_APPROVED\|POLICY_REJECTED" /var/log/infrafabric/sip_witness.log | wc -l

# Check last escalation attempt
grep "POLICY_\|BRIDGE_" /var/log/infrafabric/sip_witness.log | tail -1

# If no recent activity, this may be informational (no escalations needed)
# Verify system is operational with health check
systemctl status kamailio
```

**Action:**
- If services running normally and alerts are recent, alert is likely informational (no escalations triggered)
- If services down, use emergency procedures above
- No action typically needed for this alert

---

## Emergency Procedures

### Scenario 1: Service Down (Proxy not responding)

**Goal:** Restore service to operational state
**Time Target:** <2 minutes

```bash
# STEP 1: Verify problem (10 seconds)
echo "1. Checking service status..."
systemctl status kamailio
curl http://localhost:5060 2>&1 | head -3

# STEP 2: Attempt graceful restart (30 seconds)
echo "2. Attempting graceful restart..."
sudo systemctl restart kamailio
sleep 10

# STEP 3: Verify recovery (20 seconds)
echo "3. Verifying recovery..."
systemctl status kamailio | grep "active (running)"
curl http://prometheus.infrafabric.io:9090/api/v1/query?query=up{job=\"sip-escalate-proxy\"} | grep -o '"value":\[\s*1'

# STEP 4: If restart failed, diagnose (5 minutes)
if [ $? -ne 0 ]; then
  echo "4. Restart failed. Diagnosing..."
  sudo journalctl -u kamailio -n 50
  echo "5. Attempting configuration validation..."
  sudo kamailio -c -f /etc/kamailio/kamailio.cfg
  echo "6. Escalate to SIP team if validation fails"
  echo "   Slack: #on-call, @sip-team"
fi

# STEP 5: Verification tests (30 seconds)
echo "5. Running verification tests..."
# Test SIP on port 5060
timeout 2 bash -c 'cat < /dev/null > /dev/tcp/127.0.0.1/5060' && echo "✓ SIP (5060) responsive"
# Test TLS on port 5061
timeout 2 bash -c 'cat < /dev/null > /dev/tcp/127.0.0.1/5061' && echo "✓ SIP TLS (5061) responsive"
# Test Prometheus metrics
curl -s http://prometheus.infrafabric.io:9090/api/v1/query?query=sip_active_calls | jq '.data.result[0].value[1]' && echo "✓ Metrics available"

echo ""
echo "✓ Recovery complete. Service should be operational."
```

### Scenario 2: High Latency / Performance Issue

**Goal:** Identify and resolve performance bottleneck
**Time Target:** 10-15 minutes

```bash
# STEP 1: Identify bottleneck
echo "1. Identifying performance bottleneck..."

# Check call latency
echo "  - Call latency (p95):"
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=histogram_quantile(0.95,rate(sip_call_duration_seconds_bucket[5m]))' | jq '.data.result[0].value[1]'

# Check policy evaluation latency
echo "  - Policy eval latency (p99):"
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=histogram_quantile(0.99,rate(sip_policy_eval_duration_seconds_bucket[5m]))' | jq '.data.result[0].value[1]'

# Check H.323 bridge latency
echo "  - H.323 bridge latency:"
grep "bridge_latency\|transcoding" /var/log/infrafabric/sip_witness.log | tail -5 | jq '.details.latency_ms'

# STEP 2: Check system resources
echo ""
echo "2. Checking system resources..."
free -h | head -2
df -h | grep -E "/$|/var"
top -bn1 | head -20

# STEP 3: Identify and resolve based on bottleneck

# If H.323 bridge latency high:
if [ $(curl -s '...' | jq '.value' | cut -d. -f1) -gt 5 ]; then
  echo "3a. H.323 bridge slow - options:"
  echo "   - Check H.323 gatekeeper status (Session 3)"
  echo "   - Review bridge transcoding load"
  echo "   - Consider load balancing"
fi

# If policy eval latency high:
if [ $(curl -s '...' | jq '.value' | cut -d. -f1) -gt 1 ]; then
  echo "3b. Policy evaluation slow - options:"
  echo "   - Check expert registry size"
  echo "   - Review signature validation"
  echo "   - Consider caching expert lookups"
  echo "   - Implement: @lru_cache for approved_experts lookup"
fi

# If high CPU utilization:
if [ $(top -bn1 | grep "Cpu" | awk '{print $2}' | cut -d% -f1) -gt 80 ]; then
  echo "3c. High CPU utilization - options:"
  echo "   - Scale Kamailio horizontally (add more proxy instances)"
  echo "   - Reduce policy evaluation complexity"
  echo "   - Implement rate limiting to shed load"
fi

# If high memory utilization:
if [ $(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}') -gt 80 ]; then
  echo "3d. High memory utilization - options:"
  echo "   - Check for memory leaks in Python integration"
  echo "   - Restart Kamailio (graceful drain first)"
  echo "   - Reduce call history retention"
fi

echo ""
echo "Recovery: Apply remediation above and monitor metrics"
```

### Scenario 3: Security Breach or Suspected Attack

**Goal:** Containment and forensics
**Time Target:** <5 minutes for lockdown

```bash
# STEP 1: LOCKDOWN (immediate)
echo "1. LOCKING DOWN SERVICE..."

# Block all external access except known experts
sudo iptables -I INPUT -p tcp --dport 5060 -j DROP
sudo iptables -I INPUT -p udp --dport 5060 -j DROP
sudo iptables -I INPUT -p tcp --dport 5061 -j DROP

# Allow only approved expert IPs
for IP in 203.0.113.0/24 198.51.100.0/24 192.0.2.0/24; do
  sudo iptables -I INPUT -s $IP -p tcp --dport 5061 -j ACCEPT
  sudo iptables -I INPUT -s $IP -p udp --dport 5060 -j ACCEPT
done

echo "✓ Firewall locked down. Only approved IPs can connect."

# STEP 2: COLLECT EVIDENCE
echo ""
echo "2. Collecting evidence for forensics..."

# Capture all logs
sudo tar -czf /tmp/sip-incident-logs-$(date +%s).tar.gz \
  /var/log/kamailio/ \
  /var/log/infrafabric/sip_witness.log \
  /etc/kamailio/

# Capture Prometheus data for last 24 hours
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query_range?query=increase(sip_errors_total[5m])&start='"$(date -u -d '24 hours ago' +%s)"'&end='"$(date +%s)"'&step=60' > /tmp/sip-errors-24h.json

echo "✓ Evidence captured to /tmp/"

# STEP 3: NOTIFY SECURITY TEAM
echo ""
echo "3. NOTIFYING SECURITY TEAM..."
echo ""
echo "URGENT: Potential security incident detected"
echo "Incident logs: /tmp/sip-incident-logs-*.tar.gz"
echo "Contact:"
echo "  - Slack: #security-incident @security-lead"
echo "  - Phone: +1-555-0102"
echo "  - Email: security@infrafabric.io"

# STEP 4: FORENSIC ANALYSIS (preliminary)
echo ""
echo "4. Preliminary forensic analysis..."

# Check for suspicious patterns
echo "  - Failed authentication attempts:"
grep "AUTH_FAILED\|401" /var/log/kamailio/kamailio.log | wc -l

echo "  - IP allowlist violations:"
grep "IP_NOT_ALLOWLISTED\|403" /var/log/kamailio/kamailio.log | wc -l

echo "  - Unusual expert IDs:"
grep "expert_id" /var/log/infrafabric/sip_witness.log | jq '.details.expert_id' | sort | uniq -c | sort -rn | head -10

echo "  - Suspicious source IPs:"
grep "source_ip" /var/log/infrafabric/sip_witness.log | jq '.source_ip' | sort | uniq -c | sort -rn | head -10

# STEP 5: MAINTAIN SERVICE
echo ""
echo "5. Service status during incident..."
systemctl status kamailio
echo ""
echo "✓ Service is operational under security lockdown."
echo "  IF.guard policy will automatically block unauthorized calls."
echo "  Authorized experts can still connect via TLS + digest auth."
```

### Scenario 4: Rate Limit Exceeded (Possible DoS)

**Goal:** Identify attack source and mitigate
**Time Target:** 5 minutes

```bash
# STEP 1: CONFIRM DoS ATTACK
echo "1. Confirming DoS attack..."

ERRORS=$(grep -c "RATE_LIMIT_EXCEEDED\|429" /var/log/kamailio/kamailio.log | tail -100)
echo "  Rate limit violations in last 100 log lines: $ERRORS"

if [ $ERRORS -gt 10 ]; then
  echo "  ✓ Confirmed: Possible DoS attack"
else
  echo "  ✗ Not confirmed: May be legitimate high load"
fi

# STEP 2: IDENTIFY ATTACK SOURCE
echo ""
echo "2. Identifying attack source..."

# Get top source IPs hitting rate limit
echo "  Top source IPs:"
grep "RATE_LIMIT_EXCEEDED" /var/log/kamailio/kamailio.log | \
  grep -oE "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" | \
  sort | uniq -c | sort -rn | head -5

# Get top experts being targeted
echo "  Top targeted experts:"
grep "RATE_LIMIT_EXCEEDED" /var/log/kamailio/kamailio.log | \
  grep -oE "expert-[a-z]+@external.advisor" | \
  sort | uniq -c | sort -rn | head -5

# STEP 3: APPLY MITIGATIONS
echo ""
echo "3. Applying mitigations..."

# Tighten IP allowlist (only approved expert IPs)
echo "  - Tightening IP allowlist (temporary)"
sudo iptables -I INPUT -p tcp --dport 5060 -j DROP
sudo iptables -I INPUT -p udp --dport 5060 -j DROP
echo "  ✓ Blocked all unapproved SIP traffic"

# Reduce rate limit threshold temporarily
echo "  - Reducing rate limit threshold (emergency)"
# Modify in /etc/kamailio/kamailio.cfg:
#   modparam("pike", "sampling_time_unit", 10)  # Tighter window
# Then restart Kamailio
echo "  ✓ Rate limiting configured"

# STEP 4: MONITOR ATTACK
echo ""
echo "4. Monitoring attack status..."
watch -n 2 'grep -c "RATE_LIMIT_EXCEEDED" /var/log/kamailio/kamailio.log | tail -50'

# STEP 5: ESCALATE
echo ""
echo "5. Escalation..."
echo "  Notify: #security-incident @security-lead"
echo "  Source IP(s) detected: [see above]"
echo "  Consider: Blocking at infrastructure level (WAF, DDoS mitigation)"
```

---

## Troubleshooting Guide

### Problem: Call Setup Fails (INVITE Rejected)

**Error Message:** `400 Bad Request` or `403 Forbidden`

**Investigation:**

```bash
# 1. Check error logs
tail -50 /var/log/kamailio/kamailio.log | grep -E "400|403|INVITE"

# 2. Check for missing IF headers
grep "X-IF-Trace-ID\|X-IF-Hazard" /var/log/kamailio/kamailio.log | tail -5

# 3. Check IF.guard policy
grep "POLICY_REJECTED" /var/log/infrafabric/sip_witness.log | jq '.details.reason' | tail -5

# 4. Check IP allowlist
grep "IP_NOT_ALLOWLISTED" /var/log/kamailio/kamailio.log | tail -5
```

**Solutions:**

| Error | Cause | Fix |
|-------|-------|-----|
| **400 Bad Request** | Missing X-IF-Trace-ID or X-IF-Hazard | Ensure client sends required headers |
| **403 Forbidden** | IP not allowlisted | Add source IP to address table in Kamailio DB |
| **403 Forbidden** | Expert not in IF.guard registry | Add expert to approved_experts in sip_proxy.py |
| **403 Forbidden** | Specialization mismatch | Verify expert specialization matches hazard type |
| **401 Unauthorized** | Authentication failed | Check credentials, verify nonce validity |

---

### Problem: No Audio Between Expert and Council

**Error Message:** No error, but audio not flowing

**Investigation:**

```bash
# 1. Check if bridge was created
grep "BRIDGE_ESTABLISHED" /var/log/infrafabric/sip_witness.log | tail -3 | jq '.details'

# 2. Check media transcoding
grep "MediaTranscoder\|transcode" /var/log/kamailio/kamailio.log | tail -10

# 3. Check RTP port availability
netstat -tlnp | grep "10[0-9][0-9][0-9]"

# 4. Check H.323 bridge audio status
grep "h323_media\|audio_channel" /var/log/infrafabric/sip_witness.log | tail -5
```

**Solutions:**

```bash
# 1. Verify codec compatibility
# SIP: Should be G.711-ulaw (8000 Hz)
# H.323: Should be G.711 (8000 Hz)
grep "codec\|audio_format" /var/log/infrafabric/sip_witness.log | tail -10

# 2. Check RTP port conflicts
# Verify each bridge has unique RTP port
kamctl fifo get_statistics dialog | grep rtp_port

# 3. Check network routing between expert and gateway
ping -c 3 expert-safety.external.advisor
ping -c 3 h323-gateway.infrafabric.local

# 4. Review bridge creation logs
grep -A 20 "BRIDGE_ESTABLISHED" /var/log/infrafabric/sip_witness.log | tail -1 | jq '.'
```

---

### Problem: Expert Not Registered

**Error Message:** `404 Not Found`

**Investigation:**

```bash
# 1. Check if expert is registered in Kamailio
kamctl fipi ul_show_contact expert-safety external.advisor

# 2. Check expert SIP URI
grep "expert-safety\|sip:" /var/log/kamailio/kamailio.log | tail -10

# 3. Check expert network connectivity
ping expert-safety.external.advisor
nslookup expert-safety.external.advisor
```

**Solutions:**

```bash
# 1. Contact external expert organization
echo "Expert may not be online. Contact:"
echo "  Safety Expert Org: support@safety-experts.io"
echo "  Or ask expert to register their SIP phone"

# 2. Verify expert SIP URI is correct
echo "Check expert URI in IFGuardPolicy.approved_experts"
grep "expert-safety@" /home/user/infrafabric/src/communication/sip_proxy.py

# 3. Check if expert org network is reachable
# May be firewall/NAT issue on expert side
```

---

### Problem: High Latency in Calls

**Error Message:** Slow call setup or audio delay

**Investigation:**

```bash
# 1. Identify where latency occurs
echo "1. Call setup latency:"
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=sip_call_duration_seconds' | jq '.data.result[0].value[1]'

echo "2. Policy eval latency:"
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=sip_policy_eval_duration_seconds' | jq '.data.result[0].value[1]'

echo "3. H.323 bridge latency:"
grep "bridge_established\|h323_latency" /var/log/infrafabric/sip_witness.log | jq '.details.latency_ms' | tail -5

echo "4. Network latency to expert:"
ping -c 5 expert-safety.external.advisor | grep "avg"

echo "5. Kamailio processing latency:"
grep "sip_method_duration" /var/log/kamailio/kamailio.log | tail -5 | jq '.duration_ms'
```

**Solutions:**

| Component | High Latency | Fix |
|-----------|--------------|-----|
| **Policy eval** | >1000ms | Cache expert lookups, optimize signature verification |
| **H.323 bridge** | >2000ms | Check H.323 gateway load, verify network routing |
| **Network** | High ping | Check ISP, DNS resolution, BGP routing |
| **Kamailio** | CPU high | Scale horizontally, reduce logging verbosity |

---

### Problem: Policy Evaluation Errors

**Error Message:** IF.guard rejections increasing

**Investigation:**

```bash
# 1. Check what's being rejected
grep "POLICY_REJECTED" /var/log/infrafabric/sip_witness.log | jq '.details.reason' | sort | uniq -c | sort -rn

# 2. Analyze rejection patterns
grep "POLICY_REJECTED" /var/log/infrafabric/sip_witness.log | jq '.details | {expert_id, hazard, reason}' | tail -20

# 3. Check for configuration issues
python3 << 'EOF'
from src.communication.sip_proxy import IFGuardPolicy
policy = IFGuardPolicy()
print("Registered experts:")
for expert_id, info in policy.approved_experts.items():
    print(f"  {expert_id}: {info['specialization']}")
EOF

# 4. Verify specialized expert-to-hazard mapping
grep "get_expert_for_hazard" /home/user/infrafabric/src/communication/sip_proxy.py
```

**Solutions:**

| Rejection | Cause | Fix |
|-----------|-------|-----|
| **Expert not in registry** | Expert missing | Add to approved_experts dict |
| **Specialization mismatch** | Expert not qualified | Verify expert specialization covers hazard |
| **Signature invalid** | Invalid Ed25519 signature | Check signature format, verify key |
| **Multiple failures** | Configuration corrupt | Review IF.guard policy, restart Kamailio |

---

### Problem: IF.witness Logs Not Generated

**Error Message:** No audit trail created

**Investigation:**

```bash
# 1. Check log file exists
ls -la /var/log/infrafabric/sip_witness.log

# 2. Check permissions
stat /var/log/infrafabric/sip_witness.log | grep -E "Access:|Uid"

# 3. Check if Kamailio can write
sudo -u kamailio touch /var/log/infrafabric/test.txt && echo "✓ Write OK" || echo "✗ Permission denied"

# 4. Check for Python errors in Kamailio logs
grep "Python\|error\|traceback" /var/log/kamailio/kamailio.log | tail -20
```

**Solutions:**

```bash
# 1. Create log directory with proper permissions
sudo mkdir -p /var/log/infrafabric
sudo chown kamailio:kamailio /var/log/infrafabric
sudo chmod 750 /var/log/infrafabric

# 2. Verify IFWitnessLogger initialization
grep "IFWitnessLogger" /home/user/infrafabric/src/communication/sip_proxy.py | head -3

# 3. Restart Kamailio
sudo systemctl restart kamailio

# 4. Verify logging works
# Trigger a test escalation and check for events
grep "BRIDGE_ESTABLISHED" /var/log/infrafabric/sip_witness.log | tail -1
```

---

### Problem: Kamailio Module Not Loading

**Error Message:** `app_python3.so not found` or Python initialization fails

**Investigation:**

```bash
# 1. Check module installation
ls -la /usr/lib/kamailio/modules/app_python3.so

# 2. Check for dependencies
ldd /usr/lib/kamailio/modules/app_python3.so | grep -E "not found|error"

# 3. Check Python availability
python3 --version
which python3

# 4. Check Kamailio config for module load
grep "app_python3" /etc/kamailio/kamailio.cfg
```

**Solutions:**

```bash
# 1. Install Python3 module for Kamailio
sudo apt-get install kamailio-python3-modules

# 2. Verify installation
dpkg -l | grep kamailio-python3

# 3. Update Kamailio config to load module
# In /etc/kamailio/kamailio.cfg:
# loadmodule "app_python3.so"
# modparam("app_python3", "load", "/home/user/infrafabric/src/communication/sip_proxy.py")

# 4. Test configuration
sudo kamailio -c -f /etc/kamailio/kamailio.cfg

# 5. Restart
sudo systemctl restart kamailio
```

---

## Monitoring Dashboards

### Grafana Dashboard: "SIP Escalate - Production"

**URL:** https://grafana.infrafabric.io/d/sip-escalate-prod

**Key Panels:**

1. **Top Left: Active Calls**
   - Shows current number of escalation calls in progress
   - Normal range: 0-50 (warning >100, critical >150)
   - Drill down to see individual calls

2. **Top Right: Call Success Rate**
   - Percentage of successful escalations
   - Target: >95%
   - Warning: <90%, Critical: <80%

3. **Bottom Left: Policy Approvals vs Rejections**
   - Stacked bar chart showing approved/rejected escalations
   - Investigate if rejection rate >50%

4. **Bottom Right: System Resource Usage**
   - CPU, memory, disk utilization
   - Alert if CPU >80%, memory >85%, disk >90%

5. **Additional Panels:**
   - **Call Duration Distribution**: p50/p95/p99 latency
   - **Expert Availability**: Which experts online/offline
   - **Geographic Map**: Expert location distribution
   - **Error Rate by Type**: 4xx/5xx breakdown

### Prometheus Queries for Manual Monitoring

```bash
# Get current active calls
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=sip_active_calls' | jq

# Get call success rate (last 5 minutes)
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=rate(sip_calls_total{result="success"}[5m])' | jq

# Get failure rate
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=rate(sip_calls_total{result="failed"}[5m])' | jq

# Get policy rejection rate
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=rate(sip_policy_decisions_total{result="rejected"}[5m])' | jq

# Get call latency (p95)
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=histogram_quantile(0.95,rate(sip_call_duration_seconds_bucket[5m]))' | jq

# Get error rate
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query?query=rate(sip_errors_total[5m])' | jq
```

### Alert Rules Monitoring

**URL:** https://alertmanager.infrafabric.io

**Active Alerts Dashboard:**
- Shows all firing alerts
- Red = Critical, Orange = Warning
- Click alert to see details and runbook link

**Alert History:**
- View past alerts and resolutions
- Track mean time to recovery (MTTR)
- Identify recurring issues

---

## Escalation Procedures

### Escalation Matrix

```
┌─────────────────────────────────────────┐
│         SIP Service Escalation            │
├─────────────────────────────────────────┤
│ Level 1 (10 minutes): On-Call Engineer   │
│  - Standard troubleshooting              │
│  - Restart services                      │
│  - Check logs/dashboards                 │
├─────────────────────────────────────────┤
│ Level 2 (5 minutes): SIP Team Lead       │
│  - Complex routing issues                │
│  - Configuration problems                │
│  - Performance tuning                    │
├─────────────────────────────────────────┤
│ Level 3 (2 minutes): Security Team       │
│  - Security incidents                    │
│  - Policy violations                     │
│  - Rate limit attacks                    │
├─────────────────────────────────────────┤
│ Level 4 (Immediate): VP Engineering      │
│  - Service complete outage               │
│  - Data breach suspected                 │
│  - Critical audit failure                │
└─────────────────────────────────────────┘
```

### When to Escalate

**Level 1 → Level 2** (After 10 minutes of investigation without resolution)
- Unable to restart service
- Persistent high error rates
- Policy configuration issues not obvious

**Level 2 → Level 3** (If security aspect identified)
- Unusual IP patterns (possible attack)
- Authorization violations
- Rate limit abuse
- Signature validation failures

**Level 3 → Level 4** (If not resolved in 5 minutes)
- Complete service outage persisting
- Data breach confirmed
- Compliance violation detected

### Escalation Process

```bash
#!/bin/bash
# Escalation script

SEVERITY=$1  # "warning" | "critical" | "emergency"
DESCRIPTION=$2
CONTEXT=$3

case $SEVERITY in
  warning)
    # Alert on-call engineer in Slack
    curl -X POST -H 'Content-type: application/json' \
      --data "{
        \"text\": \":warning: SIP Alert\",
        \"blocks\": [{
          \"type\": \"section\",
          \"text\": {
            \"type\": \"mrkdwn\",
            \"text\": \"*$DESCRIPTION*\n$CONTEXT\"
          }
        }]
      }" \
      $SLACK_WEBHOOK_WARNING
    ;;

  critical)
    # Page SIP team lead
    curl -X POST \
      --data "integration_key=$PAGERDUTY_KEY&severity=critical&description=$DESCRIPTION" \
      https://events.pagerduty.com/v2/enqueue

    # Notify Slack
    curl -X POST -H 'Content-type: application/json' \
      --data "{
        \"text\": \":rotating_light: CRITICAL SIP Alert - @sip-lead\",
        \"blocks\": [{
          \"type\": \"section\",
          \"text\": {
            \"type\": \"mrkdwn\",
            \"text\": \"*$DESCRIPTION*\n$CONTEXT\n\nSee runbook: https://infrafabric.io/docs/runbook/sip-production\"
          }
        }]
      }" \
      $SLACK_WEBHOOK_CRITICAL
    ;;

  emergency)
    # Page VP Engineering + all teams
    # Execute emergency procedure
    # Notify all stakeholders
    echo "EMERGENCY ESCALATION IN PROGRESS"
    # ... implementation ...
    ;;
esac
```

---

## Maintenance Windows

### TLS Certificate Renewal (Every 90 Days)

**Procedure:**

```bash
# 1. Generate new certificate (30 days before expiry)
echo "1. Generating new TLS certificate..."
openssl req -new -x509 -days 365 -nodes \
  -out /etc/kamailio/tls/server-new.pem \
  -keyout /etc/kamailio/tls/server-key-new.pem

# 2. Backup current certificate
echo "2. Backing up current certificate..."
cp /etc/kamailio/tls/server.pem /etc/kamailio/tls/server-$(date +%Y%m%d).pem.bak

# 3. Schedule maintenance window (low-traffic time)
echo "3. Scheduling maintenance window..."
# E.g., Saturday 02:00 UTC
MAINTENANCE_TIME="$(date -d 'next saturday 02:00' '+%Y-%m-%d %H:%M')"
echo "   Maintenance window: $MAINTENANCE_TIME"

# 4. Notify users
echo "4. Notifying users of maintenance..."
# Send notification to #if-escalate-operations

# 5. At maintenance time: Replace certificate
echo "5. (During maintenance) Replacing certificate..."
cp /etc/kamailio/tls/server-new.pem /etc/kamailio/tls/server.pem
chown kamailio:kamailio /etc/kamailio/tls/server.pem
chmod 600 /etc/kamailio/tls/server.pem

# 6. Reload Kamailio (graceful)
echo "6. Reloading Kamailio with new certificate..."
sudo systemctl reload kamailio

# 7. Verify new certificate
echo "7. Verifying new certificate..."
openssl x509 -in /etc/kamailio/tls/server.pem -noout -dates

# 8. Monitor for errors
echo "8. Monitoring for errors (5 minutes)..."
tail -f /var/log/kamailio/kamailio.log | grep -E "ERROR|tls|cert" &
MONITOR_PID=$!
sleep 300
kill $MONITOR_PID

echo "✓ Certificate renewal complete"
```

### Log Rotation

**Configuration:** `/etc/logrotate.d/kamailio`

```
/var/log/kamailio/kamailio.log {
  daily
  rotate 14
  compress
  delaycompress
  postrotate
    /usr/lib/kamailio/utils/sip_trace_reload.sh 2>/dev/null || true
  endscript
}

/var/log/infrafabric/sip_witness.log {
  daily
  rotate 30
  compress
  delaycompress
  size 100M
}
```

**Manual Rotation:**

```bash
sudo logrotate -f /etc/logrotate.d/kamailio
```

### Database Cleanup (Monthly)

**Purpose:** Remove old audit trail entries to manage storage

```bash
# 1. Backup current database
echo "1. Backing up IF.witness database..."
mysqldump -u kamailio -p infrafabric_sip_witness > /backup/sip_witness_$(date +%Y%m%d).sql

# 2. Archive old entries
echo "2. Archiving entries older than 90 days..."
mysql -u kamailio -p infrafabric << EOF
-- Archive old entries to separate table
CREATE TABLE IF NOT EXISTS sip_witness_archive LIKE sip_witness;
INSERT INTO sip_witness_archive
  SELECT * FROM sip_witness
  WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- Delete archived entries from main table
DELETE FROM sip_witness
  WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- Optimize table
OPTIMIZE TABLE sip_witness;
OPTIMIZE TABLE sip_witness_archive;
EOF

echo "✓ Database cleanup complete"
```

### Performance Tuning (Quarterly)

**Objective:** Optimize based on utilization patterns

```bash
# 1. Analyze Prometheus metrics over past 3 months
echo "1. Analyzing performance metrics..."
curl -s 'http://prometheus.infrafabric.io:9090/api/v1/query_range?query=sip_active_calls&start=...&end=...&step=3600' > perf_analysis.json

# 2. Review bottlenecks
echo "2. Top slowdowns in past quarter:"
grep "method_duration\|policy_eval_duration\|bridge_duration" perf_analysis.json | jq '.data.result[].value[1]' | sort -rn | head -10

# 3. Adjust Kamailio parameters if needed
# Examples:
#   - Increase max dialogs if reaching capacity
#   - Reduce timer values if latency high
#   - Tune buffer sizes for memory efficiency

# 4. Test changes in staging first
echo "3. Testing performance tuning in staging environment..."

# 5. Apply to production during maintenance window
echo "4. Applying tuning parameters..."
# Modify /etc/kamailio/kamailio.cfg:
#   modparam("tm", "fr_timer", 5000)
#   modparam("dialog", "max_dialogs", 500000)
#   modparam("htable", "htable", "call_stats=>size=100;")

# 6. Restart and monitor
sudo systemctl restart kamailio
sleep 60
./sip-health-check.sh
```

---

## Decision Trees for Common Scenarios

### Decision Tree 1: Service Not Responding

```
Start: Is Kamailio responding?
├─ No → [CRITICAL PATH]
│   └─ Restart Kamailio
│       ├─ Success? → Monitor recovery (5 min)
│       └─ Failed? → Check error logs
│           ├─ Config error? → Fix config, restart
│           ├─ Resource issue? → Free resources, restart
│           └─ Unknown error? → Escalate to Level 2
│
└─ Yes → Responds to queries?
    ├─ No → Firewall issue?
    │   ├─ Yes → Review iptables, allow 5060/5061
    │   └─ No → Check network interface
    │
    └─ Yes → Check service functionality
        └─ → Run health check script
```

### Decision Tree 2: Call Failures Increasing

```
Start: Failure rate > 10%?
├─ Yes → Are experts registered?
│   ├─ No → Contact expert orgs
│   └─ Yes → Check IF.guard policy
│       ├─ Many rejections? → Review policy config
│       │   └─ Expert missing? → Add to registry
│       │   └─ Specialization mismatch? → Update mapping
│       └─ Few rejections? → Check H.323 bridge
│           └─ Bridge down? → Restart Session 3
│
└─ No → Monitor trend
    └─ Increasing? → Investigate network
    └─ Stable? → No action needed
```

### Decision Tree 3: High Latency Complaints

```
Start: Are calls timing out?
├─ Yes → Increase Kamailio timers
│   ├─ INVITE timeout? → modparam("tm", "fr_inv_timer", 60000)
│   └─ Other timeout? → Review [tm] module params
│
└─ No → Where is latency?
    ├─ Call setup slow (>10s)? → Check policy eval
    │   └─ Policy eval slow? → Cache expert lookups
    ├─ Audio delay (>2s)? → Check H.323 transcoding
    │   └─ Transcoder slow? → Review codec settings
    └─ Expert not answering? → Contact expert org
```

---

## Quick Reference Commands

```bash
# Service Control
systemctl start kamailio          # Start service
systemctl stop kamailio           # Stop service
systemctl restart kamailio        # Restart service
systemctl status kamailio         # Check status

# Logs
tail -f /var/log/kamailio/kamailio.log           # Main log
tail -f /var/log/infrafabric/sip_witness.log     # Audit log
grep "ERROR" /var/log/kamailio/kamailio.log      # Find errors

# Monitoring
kamctl fifo get_statistics dialog    # Active dialogs
kamctl fifo get_statistics sip_requests  # SIP stats
kamctl fifo ul_show_contact expert-* *  # Registered contacts

# Prometheus Queries
curl 'http://prometheus:9090/api/v1/query?query=sip_active_calls'
curl 'http://prometheus:9090/api/v1/query?query=rate(sip_calls_total[5m])'

# Testing
kamailio -c -f /etc/kamailio/kamailio.cfg  # Config validation
sip-options sip:expert@external.advisor     # Connectivity test

# Emergency
sudo pkill -9 kamailio      # Force kill (last resort)
sudo iptables -L -n         # View firewall rules
df -h                        # Check disk space
free -h                      # Check memory
```

---

## Document Information

**Version:** 1.0
**Status:** Production Ready
**Last Updated:** 2025-11-11
**Next Review:** 2025-12-11
**Author:** InfraFabric Operations Team

**Distribution:** Internal Use Only
**License:** SPDX-License-Identifier: MIT

---

**Questions or Issues?** Contact:
- **Slack:** #sip-escalate-operations
- **Email:** sip-ops@infrafabric.io
- **PagerDuty:** On-Call SIP Engineer
