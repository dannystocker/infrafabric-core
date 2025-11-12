# Phase 0 Production Operations Runbook

**Version:** 1.0
**Status:** Production-Ready
**Components:** IF.coordinator, IF.governor, IF.chassis
**Last Updated:** 2025-11-12

---

## Table of Contents

1. [Overview](#overview)
2. [Deployment Procedures](#deployment-procedures)
3. [Monitoring Setup](#monitoring-setup)
4. [Incident Response](#incident-response)
5. [Backup & Restore](#backup--restore)
6. [Performance Tuning](#performance-tuning)
7. [Security Checklist](#security-checklist)
8. [Appendix](#appendix)

---

## Overview

### What is Phase 0?

Phase 0 introduces **production-ready coordination infrastructure** for Swarm of Swarms (S²) architecture:

- **IF.coordinator:** Real-time task coordination (replaces git polling)
- **IF.governor:** Capability-aware resource management
- **IF.chassis:** WASM sandbox runtime for secure agent execution

### Purpose of This Runbook

This document provides **operational procedures** for deploying, monitoring, and maintaining Phase 0 components in production.

**Target Audience:**
- Site Reliability Engineers (SRE)
- DevOps Engineers
- On-Call Engineers
- System Administrators

**Scope:**
- Production deployment (3+ environments: dev, staging, prod)
- 24/7 operations and monitoring
- Incident response and troubleshooting
- Performance optimization
- Security compliance

---

## Deployment Procedures

### Pre-Deployment Checklist

**Before deploying Phase 0 to production:**

- [ ] **Testing Complete:**
  - [ ] All unit tests passing (100% coverage Phase 0 code)
  - [ ] Integration tests passing (P0.1.5, P0.2.6, P0.3.6)
  - [ ] Load tests passing (10,000+ concurrent sessions)
  - [ ] Security audit complete (no critical/high findings)

- [ ] **Infrastructure Ready:**
  - [ ] etcd cluster deployed (3+ nodes for HA)
  - [ ] NATS cluster deployed (3+ nodes for HA)
  - [ ] Prometheus deployed for monitoring
  - [ ] Grafana deployed for dashboards

- [ ] **Documentation Updated:**
  - [ ] IF.coordinator configuration reviewed
  - [ ] Migration guide reviewed (if migrating from git polling)
  - [ ] On-call roster updated
  - [ ] Incident response procedures reviewed

- [ ] **Approvals Obtained:**
  - [ ] Architecture team signoff (@arch-team)
  - [ ] Security team signoff (@security-team)
  - [ ] Change advisory board (CAB) approval

---

### Deployment Architecture

**Production Topology:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer                             │
│                  (Session Ingress)                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    ┌───▼────┐    ┌───▼────┐    ┌───▼────┐
    │Session │    │Session │    │Session │
    │Agent 1 │    │Agent 2 │    │Agent N │
    └───┬────┘    └───┬────┘    └───┬────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    ┌───▼────────┐ ┌──▼─────────┐ ┌──▼──────────┐
    │IF.coordinator│ │IF.governor │ │IF.chassis   │
    │   (API)     │ │   (API)    │ │  (Runtime)  │
    └───┬────────┘ └──┬─────────┘ └──┬──────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    ┌───▼────┐    ┌───▼────┐    ┌───▼────┐
    │etcd-1  │    │etcd-2  │    │etcd-3  │
    │(leader)│    │(follow)│    │(follow)│
    └────────┘    └────────┘    └────────┘
```

**Components:**
- **3x etcd nodes:** High availability coordination backend
- **3x NATS nodes:** High throughput message bus
- **IF.coordinator:** Stateless (can scale horizontally)
- **IF.governor:** Stateless (can scale horizontally)
- **IF.chassis:** Per-session runtime (isolated)

---

### Step 1: Deploy etcd Cluster (Production)

**Requirements:**
- 3 nodes minimum for quorum (5 for large scale)
- SSD storage (etcd is disk I/O sensitive)
- Low-latency network (<5ms between nodes)
- TLS certificates for authentication

**Deployment (Docker Compose):**

```yaml
# docker-compose.etcd.yml
version: '3.8'

services:
  etcd-1:
    image: quay.io/coreos/etcd:v3.5.10
    container_name: etcd-1
    hostname: etcd-1
    environment:
      - ETCD_NAME=etcd-1
      - ETCD_INITIAL_ADVERTISE_PEER_URLS=https://etcd-1:2380
      - ETCD_LISTEN_PEER_URLS=https://0.0.0.0:2380
      - ETCD_LISTEN_CLIENT_URLS=https://0.0.0.0:2379
      - ETCD_ADVERTISE_CLIENT_URLS=https://etcd-1:2379
      - ETCD_INITIAL_CLUSTER_TOKEN=if-prod-cluster
      - ETCD_INITIAL_CLUSTER=etcd-1=https://etcd-1:2380,etcd-2=https://etcd-2:2380,etcd-3=https://etcd-3:2380
      - ETCD_INITIAL_CLUSTER_STATE=new
      # TLS
      - ETCD_CLIENT_CERT_AUTH=true
      - ETCD_TRUSTED_CA_FILE=/certs/ca.crt
      - ETCD_CERT_FILE=/certs/etcd-1.crt
      - ETCD_KEY_FILE=/certs/etcd-1.key
      - ETCD_PEER_CLIENT_CERT_AUTH=true
      - ETCD_PEER_TRUSTED_CA_FILE=/certs/ca.crt
      - ETCD_PEER_CERT_FILE=/certs/etcd-1-peer.crt
      - ETCD_PEER_KEY_FILE=/certs/etcd-1-peer.key
    volumes:
      - etcd-1-data:/etcd-data
      - ./certs:/certs:ro
    networks:
      - if-prod-net
    ports:
      - "2379:2379"
      - "2380:2380"

  etcd-2:
    image: quay.io/coreos/etcd:v3.5.10
    container_name: etcd-2
    hostname: etcd-2
    environment:
      - ETCD_NAME=etcd-2
      - ETCD_INITIAL_ADVERTISE_PEER_URLS=https://etcd-2:2380
      - ETCD_LISTEN_PEER_URLS=https://0.0.0.0:2380
      - ETCD_LISTEN_CLIENT_URLS=https://0.0.0.0:2379
      - ETCD_ADVERTISE_CLIENT_URLS=https://etcd-2:2379
      - ETCD_INITIAL_CLUSTER_TOKEN=if-prod-cluster
      - ETCD_INITIAL_CLUSTER=etcd-1=https://etcd-1:2380,etcd-2=https://etcd-2:2380,etcd-3=https://etcd-3:2380
      - ETCD_INITIAL_CLUSTER_STATE=new
      # TLS
      - ETCD_CLIENT_CERT_AUTH=true
      - ETCD_TRUSTED_CA_FILE=/certs/ca.crt
      - ETCD_CERT_FILE=/certs/etcd-2.crt
      - ETCD_KEY_FILE=/certs/etcd-2.key
      - ETCD_PEER_CLIENT_CERT_AUTH=true
      - ETCD_PEER_TRUSTED_CA_FILE=/certs/ca.crt
      - ETCD_PEER_CERT_FILE=/certs/etcd-2-peer.crt
      - ETCD_PEER_KEY_FILE=/certs/etcd-2-peer.key
    volumes:
      - etcd-2-data:/etcd-data
      - ./certs:/certs:ro
    networks:
      - if-prod-net
    ports:
      - "2381:2379"
      - "2382:2380"

  etcd-3:
    image: quay.io/coreos/etcd:v3.5.10
    container_name: etcd-3
    hostname: etcd-3
    environment:
      - ETCD_NAME=etcd-3
      - ETCD_INITIAL_ADVERTISE_PEER_URLS=https://etcd-3:2380
      - ETCD_LISTEN_PEER_URLS=https://0.0.0.0:2380
      - ETCD_LISTEN_CLIENT_URLS=https://0.0.0.0:2379
      - ETCD_ADVERTISE_CLIENT_URLS=https://etcd-3:2379
      - ETCD_INITIAL_CLUSTER_TOKEN=if-prod-cluster
      - ETCD_INITIAL_CLUSTER=etcd-1=https://etcd-1:2380,etcd-2=https://etcd-2:2380,etcd-3=https://etcd-3:2380
      - ETCD_INITIAL_CLUSTER_STATE=new
      # TLS
      - ETCD_CLIENT_CERT_AUTH=true
      - ETCD_TRUSTED_CA_FILE=/certs/ca.crt
      - ETCD_CERT_FILE=/certs/etcd-3.crt
      - ETCD_KEY_FILE=/certs/etcd-3.key
      - ETCD_PEER_CLIENT_CERT_AUTH=true
      - ETCD_PEER_TRUSTED_CA_FILE=/certs/ca.crt
      - ETCD_PEER_CERT_FILE=/certs/etcd-3-peer.crt
      - ETCD_PEER_KEY_FILE=/certs/etcd-3-peer.key
    volumes:
      - etcd-3-data:/etcd-data
      - ./certs:/certs:ro
    networks:
      - if-prod-net
    ports:
      - "2383:2379"
      - "2384:2380"

volumes:
  etcd-1-data:
  etcd-2-data:
  etcd-3-data:

networks:
  if-prod-net:
    driver: bridge
```

**Deploy:**

```bash
# Start cluster
docker-compose -f docker-compose.etcd.yml up -d

# Verify cluster health
docker exec etcd-1 etcdctl \
  --endpoints=https://etcd-1:2379,https://etcd-2:2379,https://etcd-3:2379 \
  --cacert=/certs/ca.crt \
  --cert=/certs/client.crt \
  --key=/certs/client.key \
  endpoint health

# Expected output:
# https://etcd-1:2379 is healthy: successfully committed proposal
# https://etcd-2:2379 is healthy: successfully committed proposal
# https://etcd-3:2379 is healthy: successfully committed proposal
```

**Verification:**

```bash
# Check cluster membership
docker exec etcd-1 etcdctl \
  --endpoints=https://etcd-1:2379 \
  --cacert=/certs/ca.crt \
  --cert=/certs/client.crt \
  --key=/certs/client.key \
  member list

# Test read/write
docker exec etcd-1 etcdctl \
  --endpoints=https://etcd-1:2379 \
  --cacert=/certs/ca.crt \
  --cert=/certs/client.crt \
  --key=/certs/client.key \
  put test "hello production"

docker exec etcd-1 etcdctl \
  --endpoints=https://etcd-1:2379 \
  --cacert=/certs/ca.crt \
  --cert=/certs/client.crt \
  --key=/certs/client.key \
  get test
# Expected: test
#           hello production
```

---

### Step 2: Deploy IF.coordinator

**Requirements:**
- Python 3.9+
- `etcd3` library
- Configuration file with etcd endpoints
- TLS certificates

**Configuration (`config/coordinator.production.yaml`):**

```yaml
coordinator:
  backend: etcd

  etcd:
    endpoints:
      - https://etcd-1.prod.infrafabric.io:2379
      - https://etcd-2.prod.infrafabric.io:2379
      - https://etcd-3.prod.infrafabric.io:2379

    timeout_seconds: 5

    # TLS (required in production)
    ca_cert: /etc/infrafabric/certs/ca.crt
    cert_file: /etc/infrafabric/certs/coordinator-client.crt
    key_file: /etc/infrafabric/certs/coordinator-client.key

  # Task TTL (auto-expire stale claims)
  task_claim_ttl_seconds: 300  # 5 minutes

  # Metrics
  metrics:
    enabled: true
    port: 9090
    path: /metrics

  # Logging
  logging:
    level: INFO  # DEBUG for troubleshooting
    format: json
    output: /var/log/infrafabric/coordinator.log
```

**Systemd Service (`/etc/systemd/system/if-coordinator.service`):**

```ini
[Unit]
Description=IF.coordinator Service
Documentation=https://github.com/infrafabric/infrafabric/blob/main/docs/components/IF.COORDINATOR.md
After=network.target etcd.service
Requires=etcd.service

[Service]
Type=simple
User=infrafabric
Group=infrafabric
WorkingDirectory=/opt/infrafabric

# Environment
Environment="COORDINATOR_CONFIG=/etc/infrafabric/coordinator.production.yaml"
Environment="PYTHONUNBUFFERED=1"

# Start command
ExecStart=/opt/infrafabric/venv/bin/python -m infrafabric.coordinator \
  --config ${COORDINATOR_CONFIG}

# Restart policy
Restart=always
RestartSec=10

# Resource limits
LimitNOFILE=65536
MemoryLimit=2G

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/infrafabric

[Install]
WantedBy=multi-user.target
```

**Deploy:**

```bash
# Install service
sudo cp if-coordinator.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable if-coordinator
sudo systemctl start if-coordinator

# Check status
sudo systemctl status if-coordinator

# Check logs
sudo journalctl -u if-coordinator -f
```

**Verification:**

```bash
# Test coordinator API
curl -k https://localhost:8080/health
# Expected: {"status": "healthy", "etcd": "connected"}

# Test metrics endpoint
curl -k https://localhost:9090/metrics | grep if_coordinator
# Expected: Various if_coordinator_* metrics
```

---

### Step 3: Deploy IF.governor

**Configuration (`config/governor.production.yaml`):**

```yaml
governor:
  coordinator:
    # Connect to IF.coordinator
    url: https://coordinator.prod.infrafabric.io:8080
    timeout_seconds: 5

  # Budget enforcement
  budget:
    enabled: true
    default_session_budget: 40.00  # USD
    cost_tracking_interval: 60  # seconds

  # Capability matching
  capabilities:
    enabled: true
    min_match_score: 0.7  # 70% capability match required

  # Circuit breakers
  circuit_breaker:
    enabled: true
    failure_threshold: 5  # failures before open
    reset_timeout: 60  # seconds

  # Metrics
  metrics:
    enabled: true
    port: 9091

  logging:
    level: INFO
    format: json
    output: /var/log/infrafabric/governor.log
```

**Systemd Service:** Similar to IF.coordinator (adjust paths/ports)

---

### Step 4: Deploy IF.chassis

**Configuration (`config/chassis.production.yaml`):**

```yaml
chassis:
  # WASM runtime
  runtime:
    engine: wasmtime  # or wasmer
    max_memory_mb: 512
    max_cpu_percent: 50
    max_execution_time_seconds: 300

  # Scoped credentials
  credentials:
    vault_addr: https://vault.prod.infrafabric.io:8200
    vault_token_path: /etc/infrafabric/vault-token

  # SLO tracking
  slo:
    target_latency_p95_ms: 10
    target_availability_percent: 99.9

  # Metrics
  metrics:
    enabled: true
    port: 9092

  logging:
    level: INFO
    format: json
    output: /var/log/infrafabric/chassis.log
```

**Systemd Service:** Similar to IF.coordinator

---

### Step 5: Deploy Monitoring Stack

**Prometheus Configuration (`prometheus.yml`):**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # IF.coordinator
  - job_name: 'if-coordinator'
    static_configs:
      - targets: ['coordinator-1:9090', 'coordinator-2:9090', 'coordinator-3:9090']
    metrics_path: '/metrics'
    scheme: https
    tls_config:
      ca_file: /etc/prometheus/certs/ca.crt
      cert_file: /etc/prometheus/certs/prometheus.crt
      key_file: /etc/prometheus/certs/prometheus.key

  # IF.governor
  - job_name: 'if-governor'
    static_configs:
      - targets: ['governor-1:9091', 'governor-2:9091', 'governor-3:9091']

  # IF.chassis
  - job_name: 'if-chassis'
    static_configs:
      - targets: ['chassis-1:9092', 'chassis-2:9092']

  # etcd
  - job_name: 'etcd'
    static_configs:
      - targets: ['etcd-1:2379', 'etcd-2:2379', 'etcd-3:2379']
    metrics_path: '/metrics'
```

**Deploy Prometheus:**

```bash
docker run -d \
  --name prometheus \
  -p 9093:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml:ro \
  -v $(pwd)/certs:/etc/prometheus/certs:ro \
  prom/prometheus:latest

# Verify
curl http://localhost:9093/api/v1/targets
```

---

### Step 6: Deploy Grafana Dashboards

**Import Pre-Built Dashboard:**

1. Navigate to Grafana UI: `https://grafana.prod.infrafabric.io`
2. Go to Dashboards → Import
3. Upload `dashboards/phase-0-overview.json`

**Key Panels:**
- IF.coordinator claim latency (p50, p95, p99)
- IF.governor budget utilization
- IF.chassis sandbox count
- etcd cluster health
- Session agent count

---

### Step 7: Initialize Production Data

**Seed Task Board:**

```bash
# Initialize Phase 0 tasks in etcd
python3 <<EOF
from infrafabric.event_bus import EventBus
import yaml

# Connect to production etcd
bus = EventBus('etcd', {
    'endpoints': [
        'https://etcd-1.prod.infrafabric.io:2379',
        'https://etcd-2.prod.infrafabric.io:2379',
        'https://etcd-3.prod.infrafabric.io:2379'
    ],
    'ca_cert': '/etc/infrafabric/certs/ca.crt',
    'cert_file': '/etc/infrafabric/certs/client.crt',
    'key_file': '/etc/infrafabric/certs/client.key'
})

assert bus.connect(), "Failed to connect to etcd"

# Load tasks from task board
with open('docs/PHASE-0-TASK-BOARD.md', 'r') as f:
    task_board = f.read()

# Parse and initialize tasks (customize parsing logic)
# ... (task initialization logic) ...

print("✅ Task board initialized")
EOF
```

---

### Deployment Validation

**Smoke Tests:**

```bash
# Test 1: Task claim
python3 -c "
from infrafabric.coordinator import Coordinator
from infrafabric.event_bus import EventBus

bus = EventBus('etcd', {...})  # production config
bus.connect()
coordinator = Coordinator(bus)

# Claim test task
assert coordinator.claim_task('TEST-001', 'validation-session')
print('✅ Task claim working')
"

# Test 2: Real-time events
python3 -c "
# Subscribe to task updates
coordinator.subscribe_task_updates(lambda e: print(f'Event: {e}'))
# Trigger event by claiming task
coordinator.claim_task('TEST-002', 'validation-session')
# Should see event printed
"

# Test 3: Latency benchmark
python3 -c "
import time
latencies = []
for i in range(100):
    start = time.time()
    coordinator.claim_task(f'TEST-{i}', 'bench-session')
    latencies.append((time.time() - start) * 1000)

p95 = sorted(latencies)[94]
assert p95 < 10, f'p95 latency {p95:.2f}ms exceeds target'
print(f'✅ Latency test passed: p95={p95:.2f}ms')
"
```

---

## Monitoring Setup

### Key Metrics

#### IF.coordinator Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `if_coordinator_claim_latency_p95` | Histogram | Task claim latency (p95) | >10ms |
| `if_coordinator_claim_success_rate` | Gauge | % successful claims | <99% |
| `if_coordinator_active_tasks` | Gauge | Currently claimed tasks | >10,000 |
| `if_coordinator_event_bus_health` | Gauge | etcd connection status | 0 (disconnected) |
| `if_coordinator_cas_failures` | Counter | CAS operation failures | >100/min |

#### IF.governor Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `if_governor_budget_utilization` | Gauge | % of budget used | >90% |
| `if_governor_capability_match_score` | Histogram | Capability match quality | <0.7 |
| `if_governor_circuit_breaker_open` | Gauge | Circuit breaker status | 1 (open) |
| `if_governor_cost_overhead_percent` | Gauge | Coordination overhead | >10% |

#### IF.chassis Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `if_chassis_sandbox_count` | Gauge | Active WASM sandboxes | >1,000 |
| `if_chassis_memory_usage_mb` | Gauge | Total memory used | >80% |
| `if_chassis_sandbox_escapes` | Counter | Security violations | >0 |
| `if_chassis_slo_violations` | Counter | SLO breaches | >10/hour |

#### etcd Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `etcd_server_has_leader` | Gauge | Cluster has leader | 0 (no leader) |
| `etcd_disk_backend_commit_duration_seconds_bucket` | Histogram | Disk write latency | >100ms (p99) |
| `etcd_network_peer_round_trip_time_seconds` | Histogram | Network latency | >50ms |

---

### Alerting Rules

**Prometheus Alerts (`alerts.yml`):**

```yaml
groups:
  - name: phase0_critical
    interval: 30s
    rules:
      # IF.coordinator alerts
      - alert: CoordinatorHighLatency
        expr: if_coordinator_claim_latency_p95 > 10
        for: 5m
        labels:
          severity: critical
          component: if-coordinator
        annotations:
          summary: "IF.coordinator claim latency exceeds 10ms"
          description: "p95 latency is {{ $value }}ms (target: <10ms)"

      - alert: CoordinatorLowSuccessRate
        expr: if_coordinator_claim_success_rate < 0.99
        for: 5m
        labels:
          severity: critical
          component: if-coordinator
        annotations:
          summary: "IF.coordinator success rate below 99%"
          description: "Success rate is {{ $value | humanizePercentage }}"

      - alert: CoordinatorEtcdDisconnected
        expr: if_coordinator_event_bus_health == 0
        for: 1m
        labels:
          severity: critical
          component: if-coordinator
        annotations:
          summary: "IF.coordinator lost connection to etcd"
          description: "Event bus health check failing"

      # IF.governor alerts
      - alert: GovernorBudgetExhausted
        expr: if_governor_budget_utilization > 0.95
        for: 5m
        labels:
          severity: warning
          component: if-governor
        annotations:
          summary: "IF.governor budget >95% utilized"
          description: "Budget utilization: {{ $value | humanizePercentage }}"

      - alert: GovernorCircuitBreakerOpen
        expr: if_governor_circuit_breaker_open == 1
        for: 1m
        labels:
          severity: warning
          component: if-governor
        annotations:
          summary: "IF.governor circuit breaker open"
          description: "Circuit breaker tripped - too many failures"

      # IF.chassis alerts
      - alert: ChassisSandboxEscape
        expr: rate(if_chassis_sandbox_escapes[5m]) > 0
        for: 1m
        labels:
          severity: critical
          component: if-chassis
          security: high
        annotations:
          summary: "IF.chassis sandbox escape detected"
          description: "SECURITY: Sandbox containment violated"

      - alert: ChassisMemoryHigh
        expr: if_chassis_memory_usage_mb / if_chassis_memory_limit_mb > 0.8
        for: 5m
        labels:
          severity: warning
          component: if-chassis
        annotations:
          summary: "IF.chassis memory usage >80%"
          description: "Memory: {{ $value | humanizePercentage }}"

      # etcd alerts
      - alert: EtcdNoLeader
        expr: etcd_server_has_leader == 0
        for: 1m
        labels:
          severity: critical
          component: etcd
        annotations:
          summary: "etcd cluster has no leader"
          description: "Cluster election in progress or quorum lost"

      - alert: EtcdHighDiskLatency
        expr: histogram_quantile(0.99, rate(etcd_disk_backend_commit_duration_seconds_bucket[5m])) > 0.1
        for: 5m
        labels:
          severity: warning
          component: etcd
        annotations:
          summary: "etcd disk latency high (p99 >100ms)"
          description: "Disk performance degraded"
```

**AlertManager Configuration:**

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  receiver: 'default'
  group_by: ['alertname', 'component']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

  routes:
    # Critical alerts: page immediately
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true

    # Security alerts: notify security team
    - match:
        security: high
      receiver: 'security-team'
      continue: true

    # Warnings: Slack only
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'default'
    slack_configs:
      - api_url: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
        channel: '#infra-alerts'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: YOUR_PAGERDUTY_KEY
        description: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'

  - name: 'security-team'
    email_configs:
      - to: 'security@infrafabric.io'
        from: 'alertmanager@infrafabric.io'
        smarthost: 'smtp.infrafabric.io:587'
```

---

### Dashboards

**Grafana Dashboard JSON** (key panels):

```json
{
  "dashboard": {
    "title": "Phase 0 - Production Overview",
    "panels": [
      {
        "title": "IF.coordinator Claim Latency",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(if_coordinator_claim_latency_bucket[5m]))",
          "legendFormat": "p95"
        }],
        "yaxes": [{
          "format": "ms",
          "label": "Latency"
        }]
      },
      {
        "title": "Active Sessions",
        "targets": [{
          "expr": "if_coordinator_active_sessions",
          "legendFormat": "Sessions"
        }]
      },
      {
        "title": "etcd Cluster Health",
        "targets": [{
          "expr": "etcd_server_has_leader",
          "legendFormat": "Has Leader"
        }]
      }
    ]
  }
}
```

---

## Incident Response

### Incident Severity Levels

| Severity | Definition | Response Time | Example |
|----------|-----------|---------------|---------|
| **P1 (Critical)** | Complete service outage | 15 min | etcd cluster down, all sessions blocked |
| **P2 (High)** | Significant degradation | 30 min | High latency (>100ms), 50% sessions affected |
| **P3 (Medium)** | Partial impact | 1 hour | Single component degraded, workaround available |
| **P4 (Low)** | Minimal impact | 4 hours | Non-critical feature issue |

---

### Incident Response Procedures

#### P1: Complete Outage

**Symptoms:**
- IF.coordinator unreachable
- etcd cluster down (no leader)
- All session agents failing to claim tasks

**Immediate Actions (15 minutes):**

1. **Acknowledge incident**
   ```bash
   # Post in #infra-incidents
   "@here P1 incident: Phase 0 complete outage. Investigating."
   ```

2. **Check etcd cluster**
   ```bash
   # Check etcd health
   docker exec etcd-1 etcdctl endpoint health --cluster

   # If no leader, check logs
   docker logs etcd-1 --tail 100
   docker logs etcd-2 --tail 100
   docker logs etcd-3 --tail 100
   ```

3. **Identify failed node(s)**
   ```bash
   # Check which nodes responding
   curl -k https://etcd-1:2379/health
   curl -k https://etcd-2:2379/health
   curl -k https://etcd-3:2379/health
   ```

4. **Restore quorum if <2 nodes healthy**
   ```bash
   # Restart failed node(s)
   docker restart etcd-2

   # Or: Force new cluster (LAST RESORT - data loss risk)
   # Only if 2+ nodes permanently lost
   docker exec etcd-1 etcdctl member list
   # Remove dead members
   docker exec etcd-1 etcdctl member remove <member-id>
   ```

5. **Verify recovery**
   ```bash
   # Test coordinator connectivity
   python3 -c "
   from infrafabric.coordinator import Coordinator
   from infrafabric.event_bus import EventBus

   bus = EventBus('etcd', {...})
   assert bus.connect(), 'Still cannot connect'
   print('✅ Connectivity restored')
   "
   ```

**Mitigation (60 minutes):**
- If etcd unrecoverable: Restore from backup (see Backup & Restore section)
- If partial cluster: Add new member to replace failed node
- Document timeline in incident report

---

#### P2: High Latency

**Symptoms:**
- Task claim latency >100ms (10x normal)
- Session agents timing out
- Alert: `CoordinatorHighLatency`

**Diagnosis:**

```bash
# Check etcd disk latency
docker exec etcd-1 etcdctl check perf

# Check network latency between nodes
for node in etcd-1 etcd-2 etcd-3; do
  docker exec $node ping -c 5 etcd-1
done

# Check IF.coordinator resource usage
docker stats if-coordinator

# Check active task count
curl -k https://coordinator:8080/metrics | grep if_coordinator_active_tasks
```

**Common Causes & Fixes:**

1. **Disk I/O saturation**
   ```bash
   # Check disk usage
   iostat -x 1 10

   # If >80% busy: Add SSD or scale etcd horizontally
   ```

2. **Network congestion**
   ```bash
   # Check network throughput
   iftop -i eth0

   # If saturated: Upgrade network or move nodes closer
   ```

3. **Too many concurrent sessions**
   ```bash
   # Check session count
   curl -k https://coordinator:8080/metrics | grep if_coordinator_active_sessions

   # If >10,000: Scale IF.coordinator horizontally (add more instances)
   ```

---

#### P3: Single Component Degraded

**Symptoms:**
- IF.governor circuit breaker open
- Some sessions failing capability matching
- Alert: `GovernorCircuitBreakerOpen`

**Diagnosis:**

```bash
# Check IF.governor logs
sudo journalctl -u if-governor -n 100

# Check which capability causing failures
curl -k https://governor:9091/metrics | grep if_governor_capability_match_failures_total
```

**Mitigation:**
- Circuit breaker will auto-reset after timeout (60s default)
- If persistent: Check IF.governor configuration
- Temporary workaround: Lower capability match threshold

---

### Escalation Path

**Level 1: On-Call Engineer (0-15 min)**
- Initial response and diagnosis
- Execute runbook procedures
- Escalate to Level 2 if unresolved in 15 min

**Level 2: Senior SRE (15-30 min)**
- Complex troubleshooting
- Authorization for risky procedures (force new cluster, etc.)
- Escalate to Level 3 if unresolved in 30 min

**Level 3: Engineering Leadership (30+ min)**
- Major architectural decisions
- Customer communication
- Post-incident review ownership

**Contacts:**
- On-Call Rotation: See [ONCALL-ROSTER.md](ONCALL-ROSTER.md)
- PagerDuty: +1-XXX-XXX-XXXX
- Slack: #infra-incidents (urgent) #infra-alerts (routine)

---

### Post-Incident Review

**Template:**

```markdown
# Post-Incident Review: [Incident Title]

**Date:** YYYY-MM-DD
**Duration:** X hours Y minutes
**Severity:** P1 / P2 / P3 / P4
**Affected Components:** IF.coordinator / IF.governor / IF.chassis / etcd
**Incident Commander:** @username

## Timeline

- HH:MM - Detection: Alert fired / User report
- HH:MM - Response: On-call acknowledged
- HH:MM - Diagnosis: Identified root cause
- HH:MM - Mitigation: Applied fix
- HH:MM - Resolution: Service restored
- HH:MM - Monitoring: Confirmed stability

## Impact

- **Users Affected:** X sessions / Y% of traffic
- **Degradation:** Task claim latency increased to X ms
- **Revenue Impact:** $X (if applicable)

## Root Cause

[Detailed explanation of what caused the incident]

## Contributing Factors

- Factor 1
- Factor 2

## Resolution

[What was done to resolve the incident]

## Preventive Actions

| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| Add monitoring for X | @sre-team | 2025-11-20 | Pending |
| Increase etcd disk IOPS | @infra-team | 2025-11-15 | Complete |
| Update runbook with new procedure | @doc-team | 2025-11-13 | Complete |

## Lessons Learned

### What Went Well

- Quick detection (alert fired within 1 min)
- Clear runbook procedures followed

### What Could Be Improved

- Backup restoration took longer than expected
- Need better monitoring for X

## Follow-Up

- RCA Document: [Link to full analysis]
- Related Issues: #123, #456
```

**Review Meeting:**
- Schedule within 48 hours of incident
- Attendees: Incident Commander, SRE team, affected service owners
- Focus: Blameless culture, system improvements

---

## Backup & Restore

### Backup Strategy

**RPO (Recovery Point Objective):** 5 minutes
**RTO (Recovery Time Objective):** 15 minutes

**Backup Schedule:**
- **Continuous:** etcd snapshots every 5 minutes
- **Daily:** Full etcd backup at 02:00 UTC
- **Weekly:** Offsite backup to S3 (Sunday 02:00 UTC)

---

### etcd Snapshot Backup

**Automated Backup Script (`/opt/infrafabric/scripts/etcd-backup.sh`):**

```bash
#!/bin/bash
# etcd-backup.sh - Automated etcd snapshot backup

set -euo pipefail

# Configuration
ETCD_ENDPOINTS="https://etcd-1:2379,https://etcd-2:2379,https://etcd-3:2379"
BACKUP_DIR="/var/backups/etcd"
RETENTION_DAYS=7
S3_BUCKET="s3://infrafabric-backups/etcd"

# Certificates
CA_CERT="/etc/infrafabric/certs/ca.crt"
CLIENT_CERT="/etc/infrafabric/certs/backup-client.crt"
CLIENT_KEY="/etc/infrafabric/certs/backup-client.key"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate backup filename with timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/etcd-snapshot-$TIMESTAMP.db"

# Create snapshot
echo "Creating etcd snapshot: $BACKUP_FILE"
etcdctl \
  --endpoints="$ETCD_ENDPOINTS" \
  --cacert="$CA_CERT" \
  --cert="$CLIENT_CERT" \
  --key="$CLIENT_KEY" \
  snapshot save "$BACKUP_FILE"

# Verify snapshot
echo "Verifying snapshot..."
etcdctl snapshot status "$BACKUP_FILE" --write-out=table

# Compress backup
echo "Compressing backup..."
gzip "$BACKUP_FILE"
BACKUP_FILE="$BACKUP_FILE.gz"

# Upload to S3
echo "Uploading to S3..."
aws s3 cp "$BACKUP_FILE" "$S3_BUCKET/$(basename $BACKUP_FILE)"

# Clean up old local backups
echo "Cleaning up old backups (retention: $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "etcd-snapshot-*.db.gz" -mtime +$RETENTION_DAYS -delete

echo "✅ Backup complete: $BACKUP_FILE"
```

**Cron Job:**

```bash
# /etc/cron.d/etcd-backup
*/5 * * * * infrafabric /opt/infrafabric/scripts/etcd-backup.sh >> /var/log/infrafabric/etcd-backup.log 2>&1
```

---

### Restore from Backup

**Scenario:** Complete etcd cluster loss, need to restore from backup

**Procedure:**

1. **Stop all etcd nodes**
   ```bash
   docker stop etcd-1 etcd-2 etcd-3
   ```

2. **Download latest backup from S3**
   ```bash
   aws s3 cp s3://infrafabric-backups/etcd/etcd-snapshot-20251112-140000.db.gz /tmp/
   gunzip /tmp/etcd-snapshot-20251112-140000.db.gz
   ```

3. **Restore snapshot to each node**
   ```bash
   # Node 1
   docker run --rm \
     -v /tmp:/backup \
     -v etcd-1-data:/etcd-data \
     quay.io/coreos/etcd:v3.5.10 \
     etcdctl snapshot restore /backup/etcd-snapshot-20251112-140000.db \
       --name etcd-1 \
       --initial-cluster etcd-1=https://etcd-1:2380,etcd-2=https://etcd-2:2380,etcd-3=https://etcd-3:2380 \
       --initial-cluster-token if-prod-cluster-restored \
       --initial-advertise-peer-urls https://etcd-1:2380 \
       --data-dir /etcd-data

   # Repeat for nodes 2 and 3 (adjust --name and --initial-advertise-peer-urls)
   ```

4. **Start etcd cluster with restored data**
   ```bash
   # Update docker-compose to use restored token
   sed -i 's/ETCD_INITIAL_CLUSTER_TOKEN=.*/ETCD_INITIAL_CLUSTER_TOKEN=if-prod-cluster-restored/' docker-compose.etcd.yml

   # Start cluster
   docker-compose -f docker-compose.etcd.yml up -d
   ```

5. **Verify cluster health**
   ```bash
   docker exec etcd-1 etcdctl endpoint health --cluster
   docker exec etcd-1 etcdctl member list
   ```

6. **Verify data integrity**
   ```bash
   # Check task count
   docker exec etcd-1 etcdctl get --prefix tasks/ --count-only
   # Compare with expected count
   ```

7. **Resume operations**
   ```bash
   # Restart IF.coordinator, IF.governor, IF.chassis
   sudo systemctl restart if-coordinator
   sudo systemctl restart if-governor
   sudo systemctl restart if-chassis
   ```

**Estimated Recovery Time:** 15-20 minutes

---

### Disaster Recovery Testing

**Quarterly DR Drill:**

1. **Schedule maintenance window** (e.g., Sunday 02:00-04:00 UTC)
2. **Simulate complete cluster failure**
   ```bash
   docker stop etcd-1 etcd-2 etcd-3
   docker volume rm etcd-1-data etcd-2-data etcd-3-data
   ```
3. **Execute restore procedure** (documented above)
4. **Validate restoration**
   - All tasks present in etcd
   - Session agents can connect
   - Task claims functioning
5. **Document results**
   - Actual RTO achieved
   - Issues encountered
   - Runbook improvements

---

## Performance Tuning

### etcd Performance Optimization

#### Disk I/O Tuning

**Problem:** High disk latency (>100ms p99)

**Solutions:**

1. **Use SSD/NVMe storage**
   ```bash
   # Check current disk type
   lsblk -d -o name,rota
   # rota=1: HDD (slow), rota=0: SSD (fast)

   # If HDD: Migrate to SSD
   ```

2. **Increase disk IOPS (AWS EBS example)**
   ```bash
   # Upgrade EBS volume to io2 (higher IOPS)
   aws ec2 modify-volume \
     --volume-id vol-xxxxx \
     --volume-type io2 \
     --iops 10000
   ```

3. **Tune filesystem**
   ```bash
   # Mount options for etcd data volume
   # /etc/fstab
   /dev/sdb1  /var/lib/etcd  ext4  defaults,noatime,nodiratime  0 2
   ```

---

#### Network Latency Tuning

**Problem:** High network latency between etcd nodes (>10ms)

**Solutions:**

1. **Co-locate etcd nodes in same datacenter**
   - Target: <2ms inter-node latency
   - Use placement groups (AWS) or affinity rules (K8s)

2. **Increase heartbeat interval** (for high-latency networks only)
   ```bash
   # etcd configuration
   --heartbeat-interval=200  # Default: 100ms
   --election-timeout=2000   # Default: 1000ms
   ```

3. **Monitor network metrics**
   ```bash
   # Check etcd peer round-trip time
   curl -k https://etcd-1:2379/metrics | grep etcd_network_peer_round_trip_time_seconds
   ```

---

### IF.coordinator Performance Optimization

#### Horizontal Scaling

**Problem:** Single IF.coordinator instance overloaded (>1,000 sessions)

**Solution:** Deploy multiple IF.coordinator instances behind load balancer

```yaml
# docker-compose.coordinator-scaled.yml
version: '3.8'

services:
  coordinator-1:
    image: infrafabric/coordinator:latest
    environment:
      - COORDINATOR_CONFIG=/config/coordinator.yaml
    volumes:
      - ./config:/config:ro

  coordinator-2:
    image: infrafabric/coordinator:latest
    environment:
      - COORDINATOR_CONFIG=/config/coordinator.yaml
    volumes:
      - ./config:/config:ro

  coordinator-3:
    image: infrafabric/coordinator:latest
    environment:
      - COORDINATOR_CONFIG=/config/coordinator.yaml
    volumes:
      - ./config:/config:ro

  load-balancer:
    image: nginx:latest
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - coordinator-1
      - coordinator-2
      - coordinator-3
```

**NGINX Configuration:**

```nginx
# nginx.conf
upstream coordinator_backend {
    least_conn;  # Route to least-loaded instance
    server coordinator-1:8080;
    server coordinator-2:8080;
    server coordinator-3:8080;
}

server {
    listen 80;

    location / {
        proxy_pass http://coordinator_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

#### Connection Pooling

**Problem:** Too many etcd connections from IF.coordinator

**Solution:** Configure connection pooling

```yaml
# config/coordinator.yaml
coordinator:
  etcd:
    pool_size: 10  # Max concurrent connections
    pool_recycle: 300  # Recycle connections every 5 min
```

---

### IF.governor Performance Optimization

#### Capability Matching Cache

**Problem:** Slow capability matching (re-computing every request)

**Solution:** Cache capability scores

```yaml
# config/governor.yaml
governor:
  capabilities:
    cache_enabled: true
    cache_ttl_seconds: 300  # 5 minutes
    cache_max_entries: 10000
```

---

### IF.chassis Performance Optimization

#### WASM Runtime Tuning

**Problem:** High sandbox startup latency

**Solutions:**

1. **Pre-compile WASM modules**
   ```bash
   # Pre-compile frequently used modules
   wasmtime compile agent.wasm -o agent.cwasm
   ```

2. **Increase resource limits** (if sandboxes resource-starved)
   ```yaml
   # config/chassis.yaml
   chassis:
     runtime:
       max_memory_mb: 1024  # Increase from 512
       max_cpu_percent: 75   # Increase from 50
   ```

3. **Pool sandbox instances** (reuse instead of create/destroy)
   ```yaml
   chassis:
     sandbox_pool:
       enabled: true
       min_size: 10  # Pre-create 10 sandboxes
       max_size: 100
   ```

---

## Security Checklist

### Pre-Production Security Audit

**Before launching Phase 0 to production, verify:**

- [ ] **Authentication & Authorization**
  - [ ] TLS enabled for all etcd connections
  - [ ] Client certificates configured for IF.coordinator, IF.governor
  - [ ] No default/weak passwords
  - [ ] Service accounts have minimum required permissions

- [ ] **Network Security**
  - [ ] Firewall rules limit etcd access to known IPs
  - [ ] Private network for inter-component communication
  - [ ] Public endpoints behind WAF/DDoS protection

- [ ] **Data Security**
  - [ ] Encryption at rest enabled for etcd
  - [ ] Encryption in transit (TLS 1.3) for all connections
  - [ ] Secrets stored in Vault (not config files)
  - [ ] Backup encryption enabled

- [ ] **WASM Sandbox Security**
  - [ ] IF.chassis sandboxes have resource limits
  - [ ] Scoped credentials (no full API keys in sandboxes)
  - [ ] File system access restricted
  - [ ] Network access limited to allowed endpoints

- [ ] **Logging & Auditing**
  - [ ] All API calls logged with user context
  - [ ] Audit logs immutable (append-only)
  - [ ] Logs retained for 90 days minimum
  - [ ] Security events forwarded to SIEM

- [ ] **Vulnerability Management**
  - [ ] Dependencies scanned for CVEs (Snyk/Dependabot)
  - [ ] Container images scanned (Trivy/Clair)
  - [ ] Regular security updates applied

---

### Ongoing Security Operations

**Weekly:**
- [ ] Review access logs for anomalies
- [ ] Check for new CVEs in dependencies
- [ ] Rotate service account credentials

**Monthly:**
- [ ] Penetration testing (internal team or external vendor)
- [ ] Security patch updates
- [ ] Review firewall rules for stale entries

**Quarterly:**
- [ ] Full security audit
- [ ] Disaster recovery drill
- [ ] Access control review (least privilege)

---

### Security Incident Response

**If security breach detected:**

1. **Contain** (immediately)
   - Isolate affected systems
   - Revoke compromised credentials
   - Block malicious IP addresses

2. **Investigate** (1-2 hours)
   - Review audit logs
   - Identify scope of breach
   - Document timeline

3. **Remediate** (2-4 hours)
   - Patch vulnerabilities
   - Restore from clean backup if needed
   - Reset all credentials

4. **Notify** (as required)
   - Internal stakeholders
   - Customers (if PII exposed)
   - Regulatory bodies (if required)

5. **Post-Incident Review** (within 48 hours)
   - Root cause analysis
   - Preventive actions
   - Update security policies

---

## Appendix

### Quick Reference Commands

```bash
# etcd health check
docker exec etcd-1 etcdctl endpoint health --cluster

# IF.coordinator logs
sudo journalctl -u if-coordinator -f

# Task claim test
python3 -m infrafabric.tools.test_claim --task TEST-001

# Metrics query (Prometheus)
curl http://prometheus:9090/api/v1/query?query=if_coordinator_claim_latency_p95

# Backup now
/opt/infrafabric/scripts/etcd-backup.sh

# Restore from backup
/opt/infrafabric/scripts/etcd-restore.sh /path/to/snapshot.db
```

---

### Troubleshooting Quick Reference

| Symptom | Possible Cause | Quick Fix |
|---------|----------------|-----------|
| High latency | Disk I/O slow | Check `iostat`, upgrade to SSD |
| Connection refused | Service down | `systemctl restart if-coordinator` |
| etcd no leader | Quorum lost | Check logs, restart failed node |
| Circuit breaker open | Too many failures | Check IF.governor logs, will auto-reset |
| Sandbox escape | WASM vulnerability | Patch IF.chassis, review security audit |

---

### Related Documentation

- [IF.COORDINATOR.md](components/IF.COORDINATOR.md) - Component documentation
- [IF.GOVERNOR.md](components/IF.GOVERNOR.md) - Governor documentation
- [IF.CHASSIS.md](components/IF.CHASSIS.md) - Chassis documentation
- [MIGRATION-GIT-TO-ETCD.md](MIGRATION-GIT-TO-ETCD.md) - Migration guide
- [ONCALL-ROSTER.md](ONCALL-ROSTER.md) - On-call contacts

---

### Glossary

- **CAS:** Compare-And-Swap (atomic operation)
- **etcd:** Distributed key-value store
- **HA:** High Availability
- **NATS:** Message bus
- **p95:** 95th percentile
- **Quorum:** Majority of nodes (2 out of 3)
- **RTO:** Recovery Time Objective
- **RPO:** Recovery Point Objective
- **SLO:** Service Level Objective
- **WASM:** WebAssembly

---

**Last Updated:** 2025-11-12 (Phase 0)
**Maintained By:** Session 1 (NDI) - Documentation Specialist
**Status:** Production-Ready Operations Runbook
**Version:** 1.0
