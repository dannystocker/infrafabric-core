# WebRTC Deployment Guide for IF.swarm

**Purpose:** Deploy TURN server and Signaling server infrastructure for WebRTC-based IF.swarm agent mesh communication in staging and production environments.

**Philosophy Grounding:**
- **IF.ground:** Reproducible, infrastructure-as-code deployment
- **IF.witness:** All deployment events logged and traceable
- **IF.TTT:** Transparent deployment process with documented steps

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Quick Start (Docker Compose)](#quick-start-docker-compose)
5. [Manual Deployment](#manual-deployment)
   - [TURN Server (Coturn)](#turn-server-coturn)
   - [Signaling Server](#signaling-server)
   - [Load Balancer (Nginx)](#load-balancer-nginx)
6. [Configuration](#configuration)
7. [Verification](#verification)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)
10. [Production Checklist](#production-checklist)

---

## Overview

The IF.swarm WebRTC infrastructure consists of:

1. **TURN Server (Coturn):** Relay server for NAT traversal when direct P2P connection fails
2. **Signaling Server (WebSocket):** Coordinates SDP/ICE exchange between agents
3. **Redis:** State management for multi-instance signaling servers
4. **Nginx (optional):** Load balancer for signaling servers
5. **Monitoring (optional):** Prometheus + Grafana for metrics

**Deployment Flow:**
```
Agent 1 ←→ Signaling Server ←→ Agent 2
   ↓                              ↓
   └───────→ TURN Server ←───────┘
   (fallback if P2P fails)
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 IF.swarm Clients                    │
│           (Agents with WebRTC mesh)                 │
└─────────────────────────────────────────────────────┘
                      ↓ WSS (443)
┌─────────────────────────────────────────────────────┐
│            Nginx Load Balancer (optional)           │
│         - SSL termination                           │
│         - WebSocket proxying                        │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│        Signaling Server (Node.js + WebSocket)       │
│         - Instances: 1-5 (auto-scaling)             │
│         - Process Manager: PM2 / systemd / Docker   │
│         - State: Redis                              │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│                 Redis (State)                       │
│         - Connected agents registry                 │
│         - Session state                             │
└─────────────────────────────────────────────────────┘

                      ↓ (WebRTC fallback)
┌─────────────────────────────────────────────────────┐
│            TURN Server (Coturn)                     │
│         - UDP/TCP 3478 (STUN/TURN)                  │
│         - TCP 5349 (TLS)                            │
│         - UDP 49152-65535 (relay ports)             │
└─────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required Software

- **Docker** >= 20.10 (recommended)
- **Docker Compose** >= 2.0
- **Node.js** >= 18.x (if running outside Docker)
- **npm** >= 9.x

### Optional Software

- **PM2** (for process management): `npm install -g pm2`
- **Nginx** (for load balancing)
- **Redis** (if not using Docker)

### System Requirements

**Staging:**
- 2 CPU cores
- 4 GB RAM
- 20 GB disk space
- Public IP address (for TURN)

**Production:**
- 4+ CPU cores
- 8+ GB RAM
- 50+ GB disk space
- Public IP address with static allocation
- TLS certificates (Let's Encrypt recommended)

### Network Requirements

**Firewall Rules:**

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Signaling | 8443 | TCP | WebSocket (WSS) |
| Nginx (optional) | 80, 443 | TCP | HTTP/HTTPS |
| TURN | 3478 | UDP/TCP | STUN/TURN |
| TURN TLS | 5349 | TCP | TURN over TLS |
| TURN Relay | 49152-65535 | UDP | Media relay |
| Redis | 6379 | TCP | Internal only |

**DNS Records (Production):**
- `signaling.yourdomain.com` → Signaling server IP
- `turn.yourdomain.com` → TURN server IP

---

## Quick Start (Docker Compose)

The fastest way to deploy the complete stack:

### 1. Clone Repository

```bash
cd /home/user/infrafabric
```

### 2. Configure Environment

Create `.env` file:

```bash
cat > deploy/staging/.env << EOF
# External IP for TURN server (auto-detect or set manually)
EXTERNAL_IP=auto-detect

# TURN authentication secret (generate with: openssl rand -base64 32)
TURN_AUTH_SECRET=$(openssl rand -base64 32)

# Redis URL
REDIS_URL=redis://redis:6379

# IF.witness logger URL (optional)
WITNESS_LOGGER_URL=http://witness:9000

# TLS certificates (for production)
TLS_CERT_PATH=/path/to/cert.pem
TLS_KEY_PATH=/path/to/key.pem

# Grafana password (for monitoring)
GRAFANA_PASSWORD=your_secure_password
EOF
```

### 3. Update TURN Configuration

Edit `deploy/staging/coturn.conf` and add credentials:

```bash
# Add to coturn.conf:
user=ifswarm_user:YOUR_SECURE_PASSWORD
```

Or use static auth secret (already configured in .env).

### 4. Deploy Stack

**Basic deployment (TURN + Signaling + Redis):**

```bash
cd deploy/staging
docker-compose up -d
```

**With load balancer:**

```bash
docker-compose --profile loadbalancer up -d
```

**With monitoring:**

```bash
docker-compose --profile monitoring up -d
```

**Full stack:**

```bash
docker-compose --profile loadbalancer --profile monitoring up -d
```

### 5. Verify Deployment

```bash
# Check all services are running
docker-compose ps

# Check logs
docker-compose logs -f signaling
docker-compose logs -f turn

# Test signaling server
curl http://localhost:8443

# Test TURN server (requires stun client)
# Use: https://webrtc.github.io/samples/src/content/peerconnection/trickle-ice/
```

---

## Manual Deployment

For more control or non-Docker environments.

### TURN Server (Coturn)

#### Option 1: Docker

```bash
# Generate configuration
cd /home/user/infrafabric
npm run build
node dist/ops/turn-staging.js

# Or deploy manually
docker run -d \
  --name ifswarm-turn-staging \
  --network host \
  --restart unless-stopped \
  -v $(pwd)/deploy/staging/coturn.conf:/etc/coturn/turnserver.conf:ro \
  -v /var/log/coturn:/var/log/coturn \
  coturn/coturn:latest \
  -c /etc/coturn/turnserver.conf
```

#### Option 2: System Package

```bash
# Install Coturn
sudo apt-get update
sudo apt-get install coturn

# Enable Coturn
sudo systemctl enable coturn

# Copy configuration
sudo cp deploy/staging/coturn.conf /etc/turnserver.conf

# Update TURN credentials
sudo nano /etc/turnserver.conf
# Add: user=username:password

# Start service
sudo systemctl start coturn
sudo systemctl status coturn
```

#### Option 3: TypeScript Deployment Script

```bash
# Build project
npm run build

# Run deployment script
export EXTERNAL_IP=YOUR_PUBLIC_IP
export TURN_AUTH_SECRET=$(openssl rand -base64 32)
node dist/ops/turn-staging.js
```

### Signaling Server

#### Option 1: PM2 (Recommended)

```bash
# Install PM2
npm install -g pm2

# Build project
npm run build

# Deploy with PM2
npm run build
node dist/ops/signaling-staging.js

# Or manually
pm2 start dist/communication/webrtc-signaling-server.js \
  --name ifswarm-signaling-staging \
  -i max \
  --env PORT=8443 \
  --env HOST=0.0.0.0 \
  --env REDIS_URL=redis://localhost:6379

# Save PM2 configuration
pm2 save

# Setup PM2 startup script
pm2 startup
```

#### Option 2: systemd

```bash
# Generate systemd service file
node dist/ops/signaling-staging.js

# Copy service file
sudo cp deploy/staging/ifswarm-signaling.service /etc/systemd/system/ifswarm-signaling@.service

# Reload systemd
sudo systemctl daemon-reload

# Start instances (e.g., 2 instances)
sudo systemctl start ifswarm-signaling@1.service
sudo systemctl start ifswarm-signaling@2.service

# Enable on boot
sudo systemctl enable ifswarm-signaling@1.service
sudo systemctl enable ifswarm-signaling@2.service

# Check status
sudo systemctl status ifswarm-signaling@*.service
```

#### Option 3: Docker

```bash
# Build image
docker build -t ifswarm-signaling:staging .

# Run container
docker run -d \
  --name ifswarm-signaling-staging \
  --restart unless-stopped \
  -p 8443:8443 \
  --env-file deploy/staging/.env.signaling \
  ifswarm-signaling:staging
```

### Load Balancer (Nginx)

#### Setup Nginx

```bash
# Install Nginx
sudo apt-get install nginx

# Generate nginx configuration
node dist/ops/signaling-staging.js

# Copy configuration
sudo cp deploy/staging/nginx-signaling.conf /etc/nginx/sites-available/ifswarm-signaling

# Enable site
sudo ln -s /etc/nginx/sites-available/ifswarm-signaling /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

#### SSL/TLS Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d signaling.yourdomain.com

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

---

## Configuration

### TURN Server Configuration

**Key settings in `deploy/staging/coturn.conf`:**

```ini
# Network
listening-port=3478
tls-listening-port=5349
min-port=49152
max-port=65535
external-ip=YOUR_PUBLIC_IP

# Authentication
realm=ifswarm.staging
lt-cred-mech
user=username:password

# Security
fingerprint
no-tlsv1
no-tlsv1_1

# Logging
verbose
log-file=/var/log/coturn/turn.log
```

**Generate credentials:**

```bash
# Random username/password
echo "user=ifswarm_$(openssl rand -hex 4):$(openssl rand -base64 32)"

# Or use static auth secret
echo "static-auth-secret=$(openssl rand -base64 32)"
```

### Signaling Server Configuration

**Environment variables:**

```bash
# Port and host
PORT=8443
HOST=0.0.0.0

# Redis for state sharing
REDIS_URL=redis://localhost:6379

# IF.witness integration
WITNESS_LOGGER_URL=http://witness:9000

# TLS certificates
TLS_CERT_PATH=/path/to/cert.pem
TLS_KEY_PATH=/path/to/key.pem
```

### Client Configuration

**Update agent configuration to use deployed servers:**

```typescript
import { IFAgentWebRTC } from './communication/webrtc-agent-mesh';

const agent = new IFAgentWebRTC({
  agentId: 'agent-1',
  signalingServerUrl: 'wss://signaling.yourdomain.com',
  stunServers: ['stun:stun.l.google.com:19302'],
  turnServers: [{
    urls: 'turn:turn.yourdomain.com:3478',
    username: 'your_username',
    credential: 'your_password'
  }],
  turnFallbackTimeout: 5000
});
```

---

## Verification

### 1. Check Services Status

**Docker Compose:**

```bash
cd deploy/staging
docker-compose ps
```

**PM2:**

```bash
pm2 list
pm2 logs ifswarm-signaling-staging
```

**systemd:**

```bash
sudo systemctl status coturn
sudo systemctl status ifswarm-signaling@1.service
```

### 2. Test Signaling Server

```bash
# WebSocket connection test
wscat -c ws://localhost:8443

# Send test message
{"type":"register","agent_id":"test-agent"}

# Expected response
{"type":"registered","agent_id":"test-agent","connected_agents":[]}
```

### 3. Test TURN Server

Use online TURN tester: https://webrtc.github.io/samples/src/content/peerconnection/trickle-ice/

**Settings:**
- STUN/TURN URI: `turn:YOUR_IP:3478`
- Username: `your_username`
- Password: `your_password`

**Expected result:** "relay" candidates appear

### 4. Integration Test

Run agent mesh test:

```bash
npm test -- tests/webrtc-agent-mesh.test.ts
```

---

## Monitoring

### Logs

**TURN Server:**

```bash
# Docker
docker logs -f ifswarm-turn-staging

# System
sudo tail -f /var/log/coturn/turn.log
```

**Signaling Server:**

```bash
# Docker
docker logs -f ifswarm-signaling-staging

# PM2
pm2 logs ifswarm-signaling-staging

# systemd
sudo journalctl -u ifswarm-signaling@1.service -f
```

### Metrics (Prometheus + Grafana)

1. **Access Grafana:** http://localhost:3000 (admin/admin)

2. **Add Prometheus data source:**
   - URL: `http://prometheus:9090`

3. **Import WebRTC dashboard** (create custom dashboard)

**Key metrics to monitor:**
- Active signaling connections
- TURN relay sessions
- Bandwidth usage
- Connection success rate
- Latency (RTT)

### IF.witness Integration

All deployment and operational events are logged to IF.witness:

- `turn_deployment_started`
- `turn_deployment_completed`
- `signaling_deployment_started`
- `signaling_deployment_completed`
- `turn_health_check_failed`
- `signaling_health_check_failed`
- `turn_auto_restarted`

Query IF.witness for deployment audit trail and debugging.

---

## Troubleshooting

### TURN Server Issues

**Problem:** TURN server not accessible

```bash
# Check firewall
sudo ufw status
sudo ufw allow 3478/tcp
sudo ufw allow 3478/udp
sudo ufw allow 5349/tcp
sudo ufw allow 49152:65535/udp

# Check external IP
curl ifconfig.me
# Update coturn.conf with correct external-ip

# Test connectivity
nc -zv YOUR_IP 3478
```

**Problem:** Authentication failures

```bash
# Verify credentials in coturn.conf
grep "user=" /etc/coturn/turnserver.conf

# Check logs for auth errors
sudo tail -f /var/log/coturn/turn.log | grep "401"
```

### Signaling Server Issues

**Problem:** WebSocket connection refused

```bash
# Check if server is running
netstat -tulpn | grep 8443

# Check logs
docker logs ifswarm-signaling-staging

# Test locally
wscat -c ws://localhost:8443
```

**Problem:** Multiple instances not sharing state

```bash
# Verify Redis connectivity
redis-cli ping
# Should return: PONG

# Check signaling server Redis connection
docker logs ifswarm-signaling-staging | grep Redis
```

### Network Issues

**Problem:** P2P connection fails, TURN fallback not working

```bash
# Enable verbose logging in client
const agent = new IFAgentWebRTC({
  ...,
  turnFallbackTimeout: 5000,
  witnessLogger: (event) => console.log(event)
});

# Check for these events:
# - ice_candidate_sent (should include "relay" type)
# - turn_fallback_initiated
# - turn_connection_detected
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `EADDRINUSE` | Port already in use | Change port or kill existing process |
| `ECONNREFUSED` | Service not running | Start service and check status |
| `401 Unauthorized` | Invalid TURN credentials | Update credentials in coturn.conf |
| `Certificate error` | Missing/invalid TLS cert | Generate cert or disable TLS for testing |
| `Redis connection failed` | Redis not running | Start Redis: `docker-compose up redis` |

---

## Production Checklist

Before deploying to production:

### Security

- [ ] Generate strong TURN credentials (32+ character passwords)
- [ ] Configure TLS certificates (Let's Encrypt)
- [ ] Enable firewall rules (allow only necessary ports)
- [ ] Disable verbose logging in TURN and signaling
- [ ] Use static auth secret instead of long-term credentials
- [ ] Enable Redis authentication
- [ ] Configure Nginx rate limiting
- [ ] Set up VPN or IP whitelisting for admin access

### Scalability

- [ ] Enable auto-scaling for signaling server (PM2 cluster mode)
- [ ] Configure load balancer (Nginx or cloud LB)
- [ ] Set up Redis cluster for high availability
- [ ] Configure TURN server capacity limits
- [ ] Plan for horizontal scaling (multiple TURN servers)

### Monitoring

- [ ] Set up Prometheus + Grafana dashboards
- [ ] Configure IF.witness logging
- [ ] Set up alerting (PagerDuty, Slack, email)
- [ ] Monitor bandwidth usage
- [ ] Track connection success rates
- [ ] Monitor certificate expiration

### Reliability

- [ ] Enable auto-restart for all services
- [ ] Set up health checks
- [ ] Configure automated backups (Redis, logs)
- [ ] Test failover scenarios
- [ ] Document runbooks for common incidents
- [ ] Set up log rotation

### Compliance

- [ ] Log all relay sessions (IF.witness)
- [ ] Configure log retention policies
- [ ] Document data flow for auditing
- [ ] Ensure GDPR/compliance requirements met

---

## Additional Resources

- **Coturn Documentation:** https://github.com/coturn/coturn/wiki
- **WebRTC Samples:** https://webrtc.github.io/samples/
- **TURN Tester:** https://webrtc.github.io/samples/src/content/peerconnection/trickle-ice/
- **IF.swarm WebRTC Architecture:** [WEBRTC-SWARM-MESH.md](./WEBRTC-SWARM-MESH.md)
- **Security Hardening:** [SECURITY_HARDENING.md](../SECURITY_HARDENING.md)

---

## Support

For issues or questions:

1. Check IF.witness logs for deployment events
2. Review troubleshooting section above
3. Open GitHub issue with logs and configuration
4. Contact IF.swarm team

---

**IF.philosophy alignment:**
- **IF.ground:** All deployment steps are reproducible via Docker Compose or scripts
- **IF.witness:** All deployment events logged with timestamps and metadata
- **IF.TTT:** Complete transparency in deployment process, configuration, and operations

**Session 2 Deliverable:** Staging deployment infrastructure ready for Session 4 testing
