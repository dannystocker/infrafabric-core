# H.323 Guardian Council - Production Runbook

**Component**: IF.guard Real-Time Conferencing
**Version**: 1.1 (Phase 0 Integration Update)
**Last Updated**: 2025-11-12
**Audience**: Operations, SRE, DevOps

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Summary](#architecture-summary)
3. [Phase 0 Integration (IF.coordinator, IF.governor, IF.chassis)](#phase-0-integration-ifcoordinator-ifgovernor-ifchassis)
4. [Deployment Procedures](#deployment-procedures)
5. [Monitoring & Observability](#monitoring--observability)
6. [Incident Response](#incident-response)
7. [Troubleshooting Guide](#troubleshooting-guide)
   - [Common Issues](#common-issues)
   - [Codec Troubleshooting](#codec-troubleshooting)
   - [Phase 0 Component Troubleshooting](#phase-0-component-troubleshooting)
8. [Rollback Procedures](#rollback-procedures)
9. [Maintenance Windows](#maintenance-windows)

---

## Overview

This runbook provides operational procedures for the H.323 Guardian Council conferencing system. The system enables secure, traceable real-time communication for InfraFabric's governance body.

### Key Components

- **H.323 Gatekeeper (Primary)**: Admission control (port 1719)
- **H.323 Gatekeeper (Secondary)**: Hot standby (port 1720)
- **MCU**: Multipoint Control Unit for audio/video mixing
- **SIP Gateway**: External expert bridge
- **Health Monitoring**: Prometheus + Grafana
- **IF.witness**: Audit logging

### SLA Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Uptime** | 99.9% | Monthly |
| **Failover Time** | <5 seconds | Per incident |
| **Latency** | <150ms | P95 |
| **Packet Loss** | <1% | Average |
| **Call Success Rate** | >99% | Per admission request |

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│  8-15 Guardian H.323 Terminals                              │
│  (Ed25519 signed admission requests)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ ARQ (Admission Request)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  H.323 Gatekeeper HA Cluster                                │
│  ┌──────────────┐              ┌──────────────┐             │
│  │  PRIMARY     │◄────────────►│  SECONDARY   │             │
│  │  Port 1719   │  Heartbeat   │  Port 1720   │             │
│  │  (Active)    │  (2 sec)     │  (Standby)   │             │
│  └──────┬───────┘              └──────┬───────┘             │
│         │                              │                     │
│         └──────────┬───────────────────┘                     │
│                    │                                         │
│              Health Monitor                                  │
│         (TCP + process checks)                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ ACF/ARJ
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  MCU (Jitsi Videobridge / Kurento)                          │
│  - Audio mixing (centralized)                               │
│  - Video layout (4x4 grid)                                  │
│  - Max 25 guardians                                         │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ Metrics
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  Observability Stack                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Prometheus  │  │   Grafana    │  │  IF.witness  │      │
│  │  (Metrics)   │  │  (Dashboards)│  │  (Audit)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 0 Integration (IF.coordinator, IF.governor, IF.chassis)

**Status**: Phase 0 in progress (components under development)
**Integration Target**: H.323 Guardian Council will integrate with S² coordination infrastructure

### IF.coordinator Integration

The H.323 Guardian Council will integrate with IF.coordinator for real-time task distribution and coordination.

**Current State** (git polling - 30,000ms latency):
- Guardians poll git every 30 seconds for new tasks
- High latency prevents real-time consensus
- No atomic task claiming (race conditions possible)

**Future State** (IF.coordinator - <10ms latency):
- Event-driven task distribution via etcd/NATS
- Atomic Compare-And-Swap (CAS) for task claiming
- Real-time blocker detection and help coordination

**Integration Points**:

1. **Guardian Registration**:
   ```python
   # Register guardian as swarm with capabilities
   from infrafabric.coordinator import IFCoordinator

   coordinator = IFCoordinator(event_bus)
   await coordinator.register_swarm(
       swarm_id='guardian-council',
       capabilities=[
           'governance:voting',
           'governance:quality-assessment',
           'integration:h323',
           'docs:technical-writing'
       ]
   )
   ```

2. **Real-Time Task Distribution**:
   ```python
   # Coordinator pushes tasks to guardians (<10ms)
   await coordinator.push_task_to_swarm('guardian-council', {
       'id': 'task-123',
       'type': 'quality_assessment',
       'target': 'session-2-webrtc',
       'priority': 'high'
   })
   ```

3. **Blocker Detection**:
   ```python
   # Guardian detects blocker, escalates immediately
   if blocker_detected:
       await coordinator.detect_blocker('guardian-council', {
           'type': 'consensus_needed',
           'issue': 'quality_threshold_violation',
           'target': 'session-4-sip',
           'votes_needed': 8
       })
   ```

**H.323 Specific Coordination**:
- Guardian votes coordinated via IF.coordinator
- MCU capacity managed via real-time events
- Failover coordination between primary/secondary gatekeeper

**Migration Notes**:
- See `docs/MIGRATION-GIT-TO-ETCD.md` (when available)
- Gradual rollout: Run git polling + IF.coordinator in parallel initially
- Cutover when <10ms latency verified in production

---

### IF.governor Integration

Resource allocation and capability matching for Guardian Council operations.

**Capability Profile** (Guardian Council):
```yaml
swarm_id: guardian-council
capabilities:
  - governance:voting
  - governance:quality-assessment
  - governance:tie-breaking
  - integration:h323
  - integration:mcu
  - docs:technical-writing
cost_per_hour: 15.0  # Sonnet model
reputation_score: 0.98  # High reputation (production-proven)
current_budget_remaining: 100.0
model: sonnet
```

**Resource Management**:

1. **Budget Tracking**:
   ```python
   # Track H.323 operation costs
   from infrafabric.governor import IFGovernor

   governor.track_cost(
       swarm_id='guardian-council',
       operation='guardian_vote',
       cost=0.05  # ~$0.05 per vote
   )

   governor.track_cost(
       swarm_id='guardian-council',
       operation='quality_assessment',
       cost=0.15  # ~$0.15 per assessment
   )
   ```

2. **Capability Matching for Help Requests**:
   ```python
   # When H.323 guardian needs help
   qualified_swarms = governor.find_qualified_swarm(
       required_capabilities=['integration:h323', 'docs:technical-writing'],
       max_cost=5.0
   )
   # Returns: session-3-h323 (70%+ match)
   ```

3. **Circuit Breaker Protection**:
   ```python
   # Prevent cost spirals from runaway operations
   if guardian_council_budget_exhausted:
       governor._trip_circuit_breaker(
           swarm_id='guardian-council',
           reason='budget_exhausted'
       )
       # → Escalate to human for approval
   ```

**Policy Enforcement**:
- Max 3 swarms per blocked guardian (GANG_UP_ON_BLOCKER)
- Max $10 per help request
- 70% capability match required
- Circuit breaker trips at budget exhaustion

**H.323 Specific Policies**:
- Guardian votes: max 8 guardians per vote (quorum requirement)
- MCU capacity: 25 guardians max (hard limit)
- Quality assessments: require 70%+ h323 capability match

---

### IF.chassis Integration

**Security Note**: H.323 Guardian Council currently runs in trusted environment.
Phase 0 will introduce WASM sandboxing for untrusted swarm modules.

**Current Deployment** (trusted execution):
- Guardian terminals run as Python processes
- Direct system access (network sockets, filesystem)
- Credentials stored in environment variables
- No resource isolation

**Future Deployment** (IF.chassis WASM sandbox):
- Guardian modules compiled to WASM
- Resource limits enforced (CPU, memory, network)
- Scoped credentials (no access to other swarm secrets)
- SLO tracking and reputation scoring

**WASM Compilation** (future):
```bash
# Compile guardian module to WASM
rustc --target wasm32-wasi \
    src/communication/h323_guardian_module.rs \
    -o guardian_module.wasm

# Load into IF.chassis
from infrafabric.chassis import IFChassis

chassis = IFChassis()
chassis.load_swarm('guardian-council', 'guardian_module.wasm', {
    'max_cpu_percent': 50,
    'max_memory_mb': 512,
    'max_network_bandwidth_mbps': 10
})
```

**Resource Limits** (future SLO targets):
```yaml
guardian_council:
  max_cpu_percent: 50  # 50% of 1 core
  max_memory_mb: 512  # 512 MB RAM
  max_network_bandwidth_mbps: 10  # 10 Mbps (sufficient for H.323)
  max_concurrent_sessions: 25  # MCU capacity
  slo_response_time_ms: 150  # p95 latency target
```

**Security Boundaries**:
- Guardian modules cannot access other swarm credentials
- Guardian modules cannot modify IF.coordinator state directly
- Guardian modules cannot bypass IF.governor budget limits
- Credential scoping: guardians receive only H.323 gatekeeper API keys

**H.323 Specific Security**:
- Ed25519 private keys scoped to guardian identity
- MCU credentials scoped to guardian-council swarm
- SIP gateway credentials scoped (if external experts joining)
- IF.witness audit logs immutable (append-only)

**Migration Strategy**:
1. Phase 0: Document security boundaries (this section)
2. Phase 1: Refactor guardian code for WASM compatibility
3. Phase 2: Test guardian-module.wasm in IF.chassis sandbox
4. Phase 3: Gradual rollout (trusted → sandboxed execution)
5. Phase 4: All swarms running in IF.chassis WASM isolation

---

## Deployment Procedures

### Prerequisites

**System Requirements**:
- Ubuntu 22.04+ or similar Linux distribution
- Python 3.9+
- 4+ CPU cores
- 8+ GB RAM
- 100+ GB disk space
- Network: Static IPs for gatekeeper cluster

**Dependencies**:
```bash
# System packages
sudo apt-get update
sudo apt-get install -y \
    python3.9 python3-pip \
    gstreamer1.0-tools gstreamer1.0-plugins-good \
    prometheus grafana \
    gnugk  # Optional: GNU Gatekeeper

# Python dependencies
pip3 install cryptography pyyaml asyncio
```

### Step 1: Clone Repository

```bash
git clone https://github.com/dannystocker/infrafabric.git
cd infrafabric
git checkout claude/h323-guardian-council-011CV2ntGfBNNQYpqiJxaS8B
```

### Step 2: Configure Guardian Registry

```bash
# Generate Ed25519 keypairs for guardians
python3 -c "
from src.communication.h323_gatekeeper import generate_test_keypair
for i in range(8):
    priv, pub = generate_test_keypair()
    print(f'Guardian {i+1} Public Key: {pub}')
"

# Edit registry
nano config/guardian-registry.yaml
# Add guardian public keys generated above
```

### Step 3: Deploy Gatekeeper Cluster

```bash
# Validate deployment
python3 scripts/deploy_gatekeeper_ha.py --validate

# Start primary gatekeeper
python3 src/communication/h323_gatekeeper.py &
GATEKEEPER_PRIMARY_PID=$!
echo $GATEKEEPER_PRIMARY_PID > /var/run/gatekeeper_primary.pid

# Start secondary gatekeeper (port 1720)
python3 src/communication/h323_gatekeeper.py --port 1720 &
GATEKEEPER_SECONDARY_PID=$!
echo $GATEKEEPER_SECONDARY_PID > /var/run/gatekeeper_secondary.pid

# Start HA manager
python3 -c "
import asyncio
from src.communication.h323_gatekeeper_ha import GatekeeperHAManager
ha_manager = GatekeeperHAManager()
asyncio.run(ha_manager.start())
" &
HA_MANAGER_PID=$!
echo $HA_MANAGER_PID > /var/run/ha_manager.pid
```

### Step 4: Deploy MCU

```bash
# Generate MCU config
python3 -c "
from src.communication.h323_mcu_config import MCUConfigManager
from pathlib import Path
mcu = MCUConfigManager(mcu_type='jitsi')
mcu.generate_jitsi_config(Path('config/jitsi-videobridge.json'))
"

# Start Jitsi Videobridge
jvb --config config/jitsi-videobridge.json &
MCU_PID=$!
echo $MCU_PID > /var/run/mcu.pid
```

### Step 5: Configure Monitoring

```bash
# Import Grafana dashboard
curl -X POST http://localhost:3000/api/dashboards/db \
    -H "Content-Type: application/json" \
    -d @config/grafana_gatekeeper_ha.json

# Verify Prometheus scraping
curl http://localhost:9090/api/v1/targets | jq .
```

### Step 6: Smoke Test

```bash
# Run production 8-guardian test
python3 tests/test_h323_production_8guardian.py

# Expected output: ✅ PASS - Production Ready
```

---

## Monitoring & Observability

### Prometheus Metrics

**Endpoint**: `http://localhost:9090/metrics`

**Key Metrics**:
- `h323_gatekeeper_up{instance, role}` - Gatekeeper health (1=healthy, 0=down)
- `h323_gatekeeper_active_sessions{instance}` - Active guardian sessions
- `h323_gatekeeper_total_admissions{instance}` - Total admission requests
- `h323_gatekeeper_failover_total` - Failover event count
- `h323_gatekeeper_failover_duration_seconds` - Last failover duration

**Alert Rules** (`/etc/prometheus/rules/h323_alerts.yml`):
```yaml
groups:
  - name: h323_gatekeeper
    rules:
      - alert: GatekeeperDown
        expr: h323_gatekeeper_up == 0
        for: 1m
        annotations:
          summary: "Gatekeeper {{ $labels.instance }} is down"

      - alert: FailoverTooSlow
        expr: h323_gatekeeper_failover_duration_seconds > 5
        annotations:
          summary: "Failover took {{ $value }}s (>5s SLA)"

      - alert: HighCPU
        expr: h323_mcu_cpu_percent > 80
        for: 5m
        annotations:
          summary: "MCU CPU at {{ $value }}%"
```

### Grafana Dashboards

**Dashboard**: `config/grafana_gatekeeper_ha.json`

**Panels**:
1. **Gatekeeper Health** - Real-time up/down status
2. **Active Sessions** - Guardian count over time
3. **Failover Events** - Timeline of failover incidents
4. **Latency P95** - 95th percentile latency

**Access**: `http://localhost:3000/dashboards`

### IF.witness Audit Logs

**Location**: `/home/user/infrafabric/logs/`

**Log Files**:
- `h323_witness/h323_ras_YYYYMMDD.jsonl` - Admission requests (ARQ/ACF/ARJ)
- `gateway/gateway_YYYYMMDD.jsonl` - SIP-H.323 bridge events
- `ha/failover_YYYYMMDD.jsonl` - Failover events

**Query Example**:
```bash
# Count admission requests today
grep '"msg_type": "ARQ"' logs/h323_witness/h323_ras_$(date +%Y%m%d).jsonl | wc -l

# Find admission rejections
grep '"msg_type": "ARJ"' logs/h323_witness/h323_ras_$(date +%Y%m%d).jsonl | jq .
```

### Phase 0 Metrics (IF.coordinator, IF.governor, IF.chassis)

**Note**: These metrics available once Phase 0 components deployed.

#### IF.coordinator Metrics

**Key Metrics**:
- `if_coordinator_up{instance}` - Coordinator health (1=healthy, 0=down)
- `if_coordinator_push_latency_ms_p95{swarm}` - Task push latency (target: <10ms)
- `if_coordinator_claim_latency_ms_p95{swarm}` - Task claim latency (target: <10ms)
- `if_coordinator_tasks_pushed_total{swarm}` - Total tasks pushed counter
- `if_coordinator_tasks_claimed_total{swarm}` - Total tasks claimed counter
- `if_coordinator_blocker_detected_total{swarm}` - Blocker detection counter
- `if_coordinator_event_bus_connected{instance}` - Event bus connection status

**Alert Rules** (add to `/etc/prometheus/rules/phase0_alerts.yml`):
```yaml
groups:
  - name: if_coordinator
    rules:
      - alert: CoordinatorDown
        expr: if_coordinator_up == 0
        for: 1m
        annotations:
          summary: "IF.coordinator down - task distribution halted"

      - alert: CoordinatorLatencyHigh
        expr: if_coordinator_push_latency_ms_p95 > 10
        for: 5m
        annotations:
          summary: "IF.coordinator latency {{ $value }}ms exceeds 10ms target"

      - alert: EventBusDisconnected
        expr: if_coordinator_event_bus_connected == 0
        for: 30s
        annotations:
          summary: "IF.coordinator lost connection to event bus (etcd/NATS)"
```

#### IF.governor Metrics

**Key Metrics**:
- `if_governor_swarm_budget_remaining{swarm}` - Remaining budget per swarm
- `if_governor_swarm_reputation{swarm}` - Reputation score (0.0-1.0)
- `if_governor_circuit_breaker_state{swarm}` - Circuit breaker state (0=open, 1=closed)
- `if_governor_capability_match_score{swarm, task}` - Last capability match score
- `if_governor_cost_tracked_total{swarm}` - Total cost tracked per swarm
- `if_governor_help_requests_total{swarm}` - Gang-up-on-blocker requests
- `if_governor_policy_violations_total{swarm, policy}` - Policy violation counter

**Alert Rules**:
```yaml
groups:
  - name: if_governor
    rules:
      - alert: SwarmBudgetLow
        expr: if_governor_swarm_budget_remaining{swarm="guardian-council"} < 10
        annotations:
          summary: "Guardian council budget low: ${{ $value }} remaining"

      - alert: CircuitBreakerTripped
        expr: if_governor_circuit_breaker_state == 0
        for: 1m
        annotations:
          summary: "Circuit breaker tripped for {{ $labels.swarm }}"

      - alert: ReputationScoreLow
        expr: if_governor_swarm_reputation{swarm="guardian-council"} < 0.8
        for: 1h
        annotations:
          summary: "Guardian council reputation dropped to {{ $value }}"
```

#### IF.chassis Metrics

**Key Metrics**:
- `if_chassis_swarm_cpu_percent{swarm}` - CPU usage per swarm
- `if_chassis_swarm_memory_mb{swarm}` - Memory usage per swarm
- `if_chassis_swarm_network_mbps{swarm}` - Network bandwidth per swarm
- `if_chassis_slo_violations_total{swarm, metric}` - SLO violation counter
- `if_chassis_wasm_load_errors_total{swarm}` - WASM module load failures
- `if_chassis_credential_access_denied_total{swarm}` - Credential scoping violations
- `if_chassis_swarm_response_time_ms_p95{swarm}` - Swarm response latency

**Alert Rules**:
```yaml
groups:
  - name: if_chassis
    rules:
      - alert: SwarmResourceLimitExceeded
        expr: if_chassis_swarm_cpu_percent{swarm="guardian-council"} > 50
        for: 5m
        annotations:
          summary: "Guardian council CPU at {{ $value }}% (limit: 50%)"

      - alert: WasmLoadFailure
        expr: increase(if_chassis_wasm_load_errors_total[5m]) > 0
        annotations:
          summary: "WASM module failed to load for {{ $labels.swarm }}"

      - alert: SLOViolation
        expr: increase(if_chassis_slo_violations_total{swarm="guardian-council"}[1h]) > 5
        annotations:
          summary: "Guardian council SLO violated {{ $value }} times in last hour"
```

#### Updated Grafana Dashboard

**New Panels for Phase 0**:
1. **Coordinator Latency** - Real-time push/claim latency (target: <10ms line)
2. **Swarm Budgets** - Budget remaining for all swarms (guardian-council highlighted)
3. **Circuit Breaker Status** - Visual indicator (green=closed, red=tripped)
4. **Resource Usage** - CPU/memory per swarm (IF.chassis)
5. **SLO Compliance** - Percentage of operations meeting SLO targets
6. **Event Bus Health** - etcd/NATS connection status

**Query Examples**:
```bash
# Check IF.coordinator latency
curl -s "http://localhost:9090/api/v1/query?query=if_coordinator_push_latency_ms_p95" | jq .

# Check guardian council budget
curl -s "http://localhost:9090/api/v1/query?query=if_governor_swarm_budget_remaining{swarm='guardian-council'}" | jq .

# Check IF.chassis resource usage
curl -s "http://localhost:9090/api/v1/query?query=if_chassis_swarm_cpu_percent{swarm='guardian-council'}" | jq .
```

---

## Incident Response

### Incident Classification

| Severity | Description | Response Time | Example |
|----------|-------------|---------------|---------|
| **P0 - Critical** | Complete outage | <15 minutes | Both gatekeepers down |
| **P1 - High** | Degraded service | <1 hour | Primary down, secondary active |
| **P2 - Medium** | Minor issues | <4 hours | High latency (>200ms) |
| **P3 - Low** | Non-urgent | <24 hours | Single guardian admission failure |

### P0 - Critical: Both Gatekeepers Down

**Symptoms**:
- `h323_gatekeeper_up` = 0 for both instances
- No guardian admissions succeeding
- Prometheus alert: `GatekeeperDown`

**Response**:
1. **Assess Impact** (1 minute)
   ```bash
   curl http://localhost:9090/api/v1/query?query=h323_gatekeeper_up
   ```

2. **Check Process Status** (1 minute)
   ```bash
   ps aux | grep -E '(h323_gatekeeper|gnugk)'
   netstat -tulpn | grep -E '(1719|1720)'
   ```

3. **Restart Primary** (2 minutes)
   ```bash
   sudo systemctl restart h323-gatekeeper-primary
   # Or manual: python3 src/communication/h323_gatekeeper.py &
   ```

4. **Verify Recovery** (1 minute)
   ```bash
   python3 tests/test_h323_production_8guardian.py
   ```

5. **Notify Stakeholders** (5 minutes)
   - Slack: #if-guard-ops
   - Email: guardians@infrafabric.org

**Post-Incident**:
- Review IF.witness logs for root cause
- Update runbook if new failure mode discovered

### P1 - High: Primary Gatekeeper Failure

**Symptoms**:
- `h323_gatekeeper_up{role="primary"}` = 0
- Secondary promoted to primary
- Prometheus alert: `FailoverTriggered`

**Response**:
1. **Verify Failover** (1 minute)
   ```bash
   curl http://localhost:9090/api/v1/query?query=h323_gatekeeper_failover_total
   # Should show recent failover
   ```

2. **Check Failover Duration** (1 minute)
   ```bash
   curl http://localhost:9090/api/v1/query?query=h323_gatekeeper_failover_duration_seconds
   # Should be <5 seconds
   ```

3. **Diagnose Primary** (5 minutes)
   ```bash
   journalctl -u h323-gatekeeper-primary -n 100 --no-pager
   tail -n 50 logs/h323_witness/h323_ras_$(date +%Y%m%d).jsonl
   ```

4. **Restore Primary** (10 minutes)
   - Fix root cause
   - Restart primary
   - Wait for health checks to confirm healthy
   - HA manager will restore primary/secondary roles

**Success Criteria**:
- ✅ Failover completed <5 seconds
- ✅ Zero call drops during failover
- ✅ Primary restored and healthy

### P2 - Medium: High Latency

**Symptoms**:
- Average latency >150ms
- Guardian complaints about audio delay
- Prometheus alert: `HighLatency`

**Response**:
1. **Measure Latency** (2 minutes)
   ```bash
   python3 tests/load_test_h323_council.py --guardians 8
   # Check avg_latency_ms in output
   ```

2. **Check Network** (5 minutes)
   ```bash
   ping -c 10 <mcu-ip>
   traceroute <mcu-ip>
   ```

3. **Check MCU Load** (2 minutes)
   ```bash
   curl http://localhost:9090/api/v1/query?query=h323_mcu_cpu_percent
   # Should be <80%
   ```

4. **Mitigation**:
   - If MCU overloaded: Reduce guardian count or upgrade hardware
   - If network issue: Work with network team
   - If bandwidth saturation: Reduce video quality (2 Mbps → 1 Mbps)

---

## Troubleshooting Guide

### Common Issues

#### Issue: "Gatekeeper not responding on port 1719"

**Diagnosis**:
```bash
nc -zv localhost 1719
# Connection refused = not running
# Connection succeeded = running
```

**Solution**:
```bash
# Check if process running
ps aux | grep h323_gatekeeper

# If not running, start it
python3 src/communication/h323_gatekeeper.py &

# If port occupied, find and kill process
sudo lsof -i :1719
sudo kill -9 <PID>
```

#### Issue: "Guardian admission rejected (INVALID_SIGNATURE)"

**Diagnosis**:
```bash
# Check IF.witness logs for ARJ events
grep INVALID_SIGNATURE logs/h323_witness/*.jsonl | tail -n 10
```

**Solution**:
- Verify guardian public key in `config/guardian-registry.yaml`
- Ensure guardian terminal using correct private key
- Check Ed25519 signature generation code

#### Issue: "MCU at capacity (25 guardians)"

**Diagnosis**:
```bash
curl http://localhost:9090/api/v1/query?query=h323_mcu_active_participants
```

**Solution**:
- Wait for guardians to leave
- Deploy second MCU (cascading configuration)
- Reject new admissions with `CAPACITY_EXCEEDED`

#### Issue: "Failover taking >5 seconds"

**Diagnosis**:
```bash
grep GATEKEEPER_FAILOVER logs/ha/failover_*.jsonl | jq .failover_duration_sec
```

**Solution**:
- Check health check interval (should be 2 seconds)
- Verify network latency between primary/secondary
- Review failover logic in `h323_gatekeeper_ha.py`

---

## Codec Troubleshooting

### Codec Negotiation Failures

#### Issue: "Codec negotiation failed (SIP-H.323)"

**Symptoms**:
- SIP calls fail to bridge to H.323
- Error logs show "No common codec"
- Audio drops or no audio

**Diagnosis**:
```bash
# Check gateway logs for codec mismatches
grep "codec_negotiation_failed" logs/gateway/gateway_*.jsonl | tail -n 10

# Check SIP caller's codec preferences
grep "SIP INVITE" logs/gateway/*.log | grep "m=audio"
```

**Common Codec Compatibility**:
| SIP Codec | H.323 Codec | Transcoding Needed? | Bandwidth |
|-----------|-------------|---------------------|-----------|
| G.711     | G.711       | No                  | 64 kbps   |
| G.711     | G.729       | Yes                 | 64→8 kbps |
| G.729     | G.711       | Yes                 | 8→64 kbps |
| Opus      | G.711       | Yes                 | Variable  |
| VP8       | H.264       | Yes (video)         | Variable  |

**Solution**:
1. **Check Codec Whitelist** (`src/communication/h323_policy_enforce.py:192`):
   ```python
   ALLOWED_CODECS = ['G.711', 'G.729', 'VP8', 'Opus']
   ```
   - If SIP caller using non-whitelisted codec, add to whitelist
   - Or configure SIP client to use whitelisted codec

2. **Verify GStreamer Transcoding Pipeline**:
   ```bash
   # Test G.711 → G.729 transcoding
   gst-launch-1.0 -v \
     udpsrc port=20000 caps="application/x-rtp,media=audio,encoding-name=PCMU" ! \
     rtppcmudepay ! mulawdec ! \
     avenc_g729 ! rtpg729pay ! \
     udpsink host=localhost port=20002

   # Check for errors in output
   ```

3. **Check MCU Codec Support**:
   ```bash
   # For Jitsi MCU
   grep "supported codecs" /var/log/jitsi/jvb.log

   # For Kurento MCU
   kurento-media-server --list-codecs
   ```

4. **Fallback to Safe Codec**:
   - Configure SIP gateway to always use G.711 (universally supported)
   - In `h323_sip_gateway.py`, set default codec to G.711:
     ```python
     DEFAULT_CODEC = "G.711"  # Fallback codec
     ```

#### Issue: "Audio quality degraded after transcoding"

**Symptoms**:
- Audio sounds compressed or "tinny"
- Guardian complaints about poor audio quality
- Packet loss >5% in transcoded calls

**Diagnosis**:
```bash
# Check transcoding CPU usage
ps aux | grep gst-launch | awk '{print $3}'  # Should be <50% per stream

# Check transcoding latency
grep "transcoding_latency_ms" logs/gateway/gateway_*.jsonl | jq .transcoding_latency_ms
# Should be <20ms

# Check packet loss
grep "packet_loss" logs/gateway/gateway_*.jsonl | jq .packet_loss_percent
```

**Root Causes & Solutions**:

1. **CPU Overload** (transcoding >5 concurrent streams):
   ```bash
   # Check number of active transcoding processes
   ps aux | grep gst-launch | wc -l

   # Solution: Limit concurrent transcoded calls
   # In h323_sip_gateway.py, add max transcoding limit:
   MAX_CONCURRENT_TRANSCODING = 5
   ```

2. **Codec Bitrate Mismatch**:
   - G.711 (64 kbps) → G.729 (8 kbps) = significant quality loss
   - **Solution**: Prefer G.711 for high-quality calls
   - Use G.729 only for bandwidth-constrained scenarios

3. **Jitter Buffer Underrun**:
   ```bash
   # Check jitter buffer statistics
   grep "jitter_buffer" logs/gateway/*.log

   # Solution: Increase jitter buffer size
   # In h323_sip_gateway.py:
   JITTER_BUFFER_SIZE_MS = 150  # Increase from 50ms to 150ms
   ```

4. **Network Packet Loss**:
   ```bash
   # Test network quality between SIP gateway and H.323 MCU
   iperf3 -c <mcu-ip> -u -b 2M -t 30

   # Solution: Enable FEC (Forward Error Correction)
   # Or reduce number of concurrent calls
   ```

#### Issue: "Video codec mismatch (VP8 vs H.264)"

**Symptoms**:
- Video not displaying for some guardians
- Error: "Unsupported video codec"
- CPU usage high (>80%) during video calls

**Diagnosis**:
```bash
# Check video codec negotiation
grep "video_codec" logs/gateway/gateway_*.jsonl | jq .codec

# Check MCU video codec support
# For Jitsi
curl http://localhost:8080/colibri/stats | jq .videochannels[].codec

# For Kurento
grep "VideoCodec" /var/log/kurento/*.log
```

**Solution**:

1. **Prefer VP8 over H.264**:
   - VP8 is royalty-free, better browser support
   - H.264 requires licensing, but better hardware acceleration
   - **Recommendation**: Use VP8 for Guardian Council (browser-based guardians)

   In `src/communication/codec_selector.py` (Phase 5):
   ```python
   VIDEO_CODEC_PREFERENCE = ["VP8", "H.264", "VP9"]
   ```

2. **Disable Video for Audio-Only Calls**:
   ```bash
   # If audio quality > video quality, disable video
   # In h323_sip_gateway.py:
   AUDIO_ONLY_MODE = True  # Force audio-only for low-bandwidth
   ```

3. **Hardware Acceleration** (if available):
   ```bash
   # Check for GPU support
   vainfo  # Intel GPU
   nvidia-smi  # NVIDIA GPU

   # Configure GStreamer to use hardware encoding
   # In h323_sip_gateway.py:
   USE_HARDWARE_ENCODING = True  # Use vaapih264enc or nvh264enc
   ```

#### Issue: "SIP caller rejected due to codec policy"

**Symptoms**:
- SIP call rejected with `CODEC_NOT_ALLOWED`
- Error in logs: "PolicyViolationType.CODEC_NOT_ALLOWED"

**Diagnosis**:
```bash
# Check policy enforcement logs
grep "CODEC_NOT_ALLOWED" logs/gateway/sip_policy_*.jsonl | jq .
```

**Solution**:
1. **Update Codec Whitelist** (`src/communication/h323_policy_enforce.py:192`):
   ```python
   # Add caller's codec to whitelist
   ALLOWED_CODECS = ['G.711', 'G.729', 'VP8', 'Opus', 'AMR']  # Added AMR
   ```

2. **Notify SIP Caller**:
   - Send SIP 488 Not Acceptable Here response
   - Include supported codecs in SIP response headers:
     ```
     Accept: application/sdp
     Supported-Codecs: G.711,G.729,VP8,Opus
     ```

3. **Configure SIP Client**:
   - Ask caller to reconfigure SIP client to use G.711 or G.729
   - Provide codec configuration instructions for common clients:
     - Zoiper: Settings → Accounts → Advanced → Codecs
     - Linphone: Preferences → Audio codecs
     - Jitsi: Advanced → Audio → Audio codecs

### Codec Performance Tuning

#### Best Practices for Codec Selection

**For Audio Calls**:
- **Low Bandwidth** (<1 Mbps): Use G.729 (8 kbps)
- **Standard Quality** (1-2 Mbps): Use G.711 (64 kbps)
- **High Quality** (>2 Mbps): Use Opus (64-128 kbps, adaptive)

**For Video Calls**:
- **Browser-Based Guardians**: Use VP8 (better WebRTC support)
- **Hardware-Accelerated Endpoints**: Use H.264 (better performance)
- **Bandwidth-Constrained**: Use VP8 with low bitrate (500 kbps)

**Transcoding Decision Matrix**:
```
SIP Codec → H.323 Codec:
  G.711 → G.711: Pass-through (0ms latency, 0% CPU)
  G.711 → G.729: Transcode (15ms latency, 30% CPU)
  G.729 → G.711: Transcode (15ms latency, 25% CPU)
  Opus  → G.711: Transcode (20ms latency, 40% CPU)
  VP8   → H.264: Transcode (50ms latency, 70% CPU)
```

**Recommendation**: Minimize transcoding by standardizing on G.711 + VP8 for all participants.

---

## Phase 0 Component Troubleshooting

**Note**: These sections apply once Phase 0 components (IF.coordinator, IF.governor, IF.chassis) are deployed.

### IF.coordinator Issues

#### Issue: "Task push latency >10ms"

**Diagnosis**:
```bash
# Check IF.coordinator latency metrics
curl http://localhost:9090/api/v1/query?query=if_coordinator_push_latency_ms_p95

# Check etcd/NATS connection status
etcdctl endpoint health
# OR
nats-server --healthz
```

**Solution**:
- Check network latency between coordinator and event bus
- Verify etcd/NATS not overloaded
- Check for resource contention (CPU, disk I/O)
- Review coordinator logs for errors:
  ```bash
  grep ERROR logs/coordinator/*.jsonl | tail -n 20
  ```

#### Issue: "Task claim race condition detected"

**Diagnosis**:
```bash
# Check IF.witness logs for duplicate claims
grep "task_claimed" logs/coordinator/*.jsonl | jq '.task_id' | sort | uniq -d
```

**Solution**:
- Verify CAS (Compare-And-Swap) operations working correctly
- Check etcd transaction isolation
- Review coordinator CAS implementation in `infrafabric/coordinator.py:claim_task()`

#### Issue: "Blocker notification not received"

**Diagnosis**:
```bash
# Check pub/sub subscription status
etcdctl watch /tasks/broadcast/guardian-council --prefix

# Check coordinator event logs
grep "detect_blocker" logs/coordinator/*.jsonl | tail -n 10
```

**Solution**:
- Verify guardian council subscribed to correct channel
- Check event bus connectivity
- Review coordinator push implementation

---

### IF.governor Issues

#### Issue: "Budget tracking incorrect"

**Diagnosis**:
```bash
# Check budget status
if governor budget-report

# Check cost tracking in IF.witness
grep "cost_tracked" logs/governor/*.jsonl | jq '{swarm: .swarm_id, cost: .cost, remaining: .remaining_budget}'
```

**Solution**:
- Verify cost tracking calls in guardian code
- Check for missing `track_cost()` calls
- Review IF.optimise integration for cost calculation accuracy

#### Issue: "Circuit breaker tripped unexpectedly"

**Diagnosis**:
```bash
# Check circuit breaker events
grep "circuit_breaker_tripped" logs/governor/*.jsonl | jq '{swarm: .swarm_id, reason: .reason}'

# Check budget history
if governor budget-history guardian-council --last 24h
```

**Solution**:
- Review budget exhaustion or failure threshold
- Check for cost spiral (runaway operations)
- Manually reset circuit breaker if appropriate:
  ```bash
  if governor reset-circuit-breaker guardian-council --new-budget 100.0
  ```
- Investigate root cause of budget exhaustion/failures

#### Issue: "Capability matching returning wrong swarm"

**Diagnosis**:
```bash
# Check swarm capability profiles
if governor list-swarms --capabilities

# Test capability matching manually
python3 -c "
from infrafabric.governor import IFGovernor
from infrafabric.schemas.capability import Capability

gov = IFGovernor(...)
result = gov.find_qualified_swarm(
    required_capabilities=[Capability.INTEGRATION_H323],
    max_cost=5.0
)
print(f'Matched swarm: {result}')
"
```

**Solution**:
- Verify swarm profiles registered correctly
- Check capability overlap scoring (Jaccard similarity)
- Review 70% match threshold (adjust if needed)
- Verify cost and reputation factors in scoring

---

### IF.chassis Issues

#### Issue: "WASM module failed to load"

**Diagnosis**:
```bash
# Check WASM runtime logs
grep "WASM" logs/chassis/*.jsonl | tail -n 20

# Validate WASM module
wasmtime validate guardian_module.wasm
```

**Solution**:
- Ensure WASM compiled for wasm32-wasi target
- Check service contract matches module exports
- Verify wasmtime runtime version compatibility
- Review compilation errors:
  ```bash
  rustc --target wasm32-wasi src/communication/h323_guardian_module.rs 2>&1 | grep error
  ```

#### Issue: "Resource limit exceeded (CPU/memory)"

**Diagnosis**:
```bash
# Check resource usage
if chassis resource-usage guardian-council

# Check SLO violations
grep "resource_limit_exceeded" logs/chassis/*.jsonl | jq '{swarm: .swarm_id, resource: .resource_type, limit: .limit, actual: .actual}'
```

**Solution**:
- Review resource limits for guardian-council
- Adjust limits if legitimate usage increase:
  ```yaml
  # config/chassis/guardian-council.yaml
  max_cpu_percent: 70  # Increase from 50%
  max_memory_mb: 1024  # Increase from 512MB
  ```
- Investigate resource leak if usage unexpected
- Check for infinite loops or memory leaks in guardian module

#### Issue: "Scoped credentials not working"

**Diagnosis**:
```bash
# Check credential scoping configuration
if chassis list-credentials guardian-council

# Check IF.witness logs for credential access attempts
grep "credential_access" logs/chassis/*.jsonl | jq '{swarm: .swarm_id, credential: .credential_key, allowed: .allowed}'
```

**Solution**:
- Verify credential scoping rules in IF.chassis config
- Check guardian module requesting correct credential scope
- Review security boundary violations:
  ```bash
  grep "security_violation" logs/chassis/*.jsonl
  ```

#### Issue: "SLO reputation score dropping"

**Diagnosis**:
```bash
# Check reputation history
if chassis reputation-history guardian-council --last 7d

# Check SLO violations
grep "slo_violation" logs/chassis/*.jsonl | jq '{swarm: .swarm_id, metric: .metric, target: .target, actual: .actual}'
```

**Solution**:
- Identify which SLO metric violated (response time, availability, error rate)
- Review guardian performance bottlenecks
- Check for external dependencies causing slowdowns
- Investigate H.323 network latency issues

---

### H.323 + Phase 0 Integration Issues

#### Issue: "Guardian vote coordination slow (>10ms)"

**Diagnosis**:
```bash
# Check end-to-end latency from vote request to vote recorded
grep "guardian_vote" logs/coordinator/*.jsonl logs/h323_witness/*.jsonl | \
  jq -s 'group_by(.vote_id) | map({vote_id: .[0].vote_id, latency_ms: (.[1].timestamp - .[0].timestamp) * 1000})'
```

**Solution**:
- Verify IF.coordinator running and healthy
- Check event bus latency (should be <5ms)
- Review guardian H.323 network performance
- Check if git polling still enabled (should be disabled after migration)

#### Issue: "MCU capacity not updating in IF.governor"

**Diagnosis**:
```bash
# Check MCU metrics in Prometheus
curl http://localhost:9090/api/v1/query?query=h323_mcu_active_participants

# Check IF.governor receiving capacity updates
grep "mcu_capacity" logs/governor/*.jsonl | tail -n 10
```

**Solution**:
- Verify MCU sending metrics to IF.governor
- Check metric collection interval (should be <1 minute)
- Review IF.governor policy enforcement for MCU capacity

---

## Rollback Procedures

### Scenario: Phase 3 Deployment Fails

**Rollback to Phase 2**:
```bash
# Stop all Phase 3 services
sudo systemctl stop h323-gatekeeper-primary
sudo systemctl stop h323-gatekeeper-secondary
sudo systemctl stop h323-mcu

# Checkout Phase 2 commit
git checkout b5e1f40  # Phase 1+2 commit

# Restart Phase 2 services
python3 src/communication/h323_gatekeeper.py &
python3 src/communication/h323_mcu_config.py &

# Verify
python3 tests/test_h323_admission.py
```

### Scenario: Configuration Error

**Rollback Config**:
```bash
# Restore previous guardian registry
cp config/guardian-registry.yaml.bak config/guardian-registry.yaml

# Restart gatekeeper to reload config
sudo systemctl restart h323-gatekeeper-primary
```

---

## Maintenance Windows

### Planned Maintenance Procedure

**Frequency**: Monthly
**Duration**: 2 hours
**Notification**: 1 week advance

**Steps**:
1. **Notify Guardians** (T-1 week)
   - Email: guardians@infrafabric.org
   - Slack: #if-guard-council
   - Subject: "Maintenance Window: H.323 System Upgrade"

2. **Prepare** (T-1 day)
   - Backup configs: `tar -czf configs_backup.tar.gz config/`
   - Backup logs: `tar -czf logs_backup.tar.gz logs/`
   - Test rollback procedure

3. **Execute Maintenance** (T-0)
   - Switch to secondary gatekeeper
   - Upgrade primary
   - Test primary
   - Switch back to primary
   - Upgrade secondary

4. **Validate** (T+15min)
   - Run production test: `python3 tests/test_h323_production_8guardian.py`
   - Check all metrics
   - Confirm zero issues

5. **Close** (T+2h)
   - Send completion email
   - Update maintenance log

---

## Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| **On-Call Engineer** | oncall@infrafabric.org | 24/7 |
| **Tech Lead** | danny.stocker@gmail.com | Business hours |
| **Guardian Council** | guardians@infrafabric.org | Business hours |

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-11 | 1.0 | Initial production runbook | InfraFabric S3 |

---

**Document Owner**: InfraFabric Operations Team
**Review Cycle**: Quarterly
**Next Review**: 2026-02-11
