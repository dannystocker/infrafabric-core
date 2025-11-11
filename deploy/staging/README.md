# IF.swarm WebRTC Staging Deployment

This directory contains staging deployment configuration for IF.swarm WebRTC infrastructure.

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Generate TURN auth secret
echo "TURN_AUTH_SECRET=$(openssl rand -base64 32)" >> .env

# Set your external IP (or use auto-detect)
echo "EXTERNAL_IP=YOUR_PUBLIC_IP" >> .env
```

### 2. Configure TURN Credentials

Edit `coturn.conf` and add user credentials:

```bash
# Add to coturn.conf under "Authentication" section:
user=ifswarm_staging:YOUR_SECURE_PASSWORD
```

Or use the static auth secret already configured in `.env`.

### 3. Deploy Stack

**Basic (TURN + Signaling + Redis):**

```bash
docker-compose up -d
```

**With Load Balancer:**

```bash
docker-compose --profile loadbalancer up -d
```

**With Monitoring:**

```bash
docker-compose --profile monitoring up -d
```

**Full Stack:**

```bash
docker-compose --profile loadbalancer --profile monitoring up -d
```

### 4. Verify Deployment

```bash
# Check services
docker-compose ps

# Check logs
docker-compose logs -f signaling
docker-compose logs -f turn

# Test signaling server
curl http://localhost:8443
```

## Files in This Directory

| File | Description |
|------|-------------|
| `docker-compose.yml` | Complete stack definition |
| `coturn.conf` | TURN server configuration |
| `.env.example` | Environment variables template |
| `nginx-signaling.conf` | Nginx load balancer config (generated) |
| `ecosystem.config.js` | PM2 process manager config (generated) |
| `ifswarm-signaling.service` | systemd service file (generated) |

## Architecture

```
Client Agents
     ↓ WSS
Nginx (optional)
     ↓
Signaling Server (1-5 instances)
     ↓
Redis (state)
     ↓ (fallback)
TURN Server
```

## Services

### Signaling Server
- **Port:** 8443 (WSS)
- **Purpose:** SDP/ICE exchange coordination
- **Logs:** `docker logs ifswarm-signaling-staging`

### TURN Server
- **Ports:**
  - 3478 (UDP/TCP) - STUN/TURN
  - 5349 (TCP) - TLS
  - 49152-65535 (UDP) - relay
- **Purpose:** WebRTC relay fallback
- **Logs:** `docker logs ifswarm-turn-staging`

### Redis
- **Port:** 6379 (internal)
- **Purpose:** Signaling server state
- **Logs:** `docker logs ifswarm-redis-staging`

### Nginx (optional)
- **Ports:** 80, 443
- **Purpose:** Load balancer + SSL termination
- **Logs:** `docker logs ifswarm-nginx-staging`

## Monitoring

Access Grafana: http://localhost:3000

**Default credentials:** admin / admin (change in `.env`)

## Firewall Configuration

Required ports:

```bash
sudo ufw allow 3478/tcp
sudo ufw allow 3478/udp
sudo ufw allow 5349/tcp
sudo ufw allow 8443/tcp
sudo ufw allow 49152:65535/udp
```

## Troubleshooting

### TURN not accessible

```bash
# Check firewall
sudo ufw status

# Test connectivity
nc -zv YOUR_IP 3478

# Check logs
docker logs ifswarm-turn-staging
```

### Signaling connection issues

```bash
# Check if running
docker ps | grep signaling

# Check logs
docker logs -f ifswarm-signaling-staging

# Test WebSocket
wscat -c ws://localhost:8443
```

### Redis connection errors

```bash
# Check Redis
docker exec ifswarm-redis-staging redis-cli ping
# Should return: PONG

# Check connection from signaling
docker exec ifswarm-signaling-staging nc -zv redis 6379
```

## Scaling

Scale signaling server instances:

```bash
# Using Docker Compose scale (not supported with container_name)
# Instead, use PM2 or multiple compose files

# Or deploy with PM2 (see deployment guide)
```

## Security Checklist

- [ ] Change default TURN credentials
- [ ] Generate strong TURN_AUTH_SECRET
- [ ] Configure TLS certificates
- [ ] Enable Redis authentication
- [ ] Configure firewall rules
- [ ] Disable verbose logging in production
- [ ] Set Grafana admin password

## Production Migration

Before deploying to production:

1. Review [WEBRTC-DEPLOYMENT.md](../../docs/WEBRTC-DEPLOYMENT.md)
2. Complete security checklist above
3. Configure TLS certificates (Let's Encrypt)
4. Update `.env` with production values
5. Test deployment in staging first
6. Set up monitoring and alerting
7. Document runbooks

## Support

For detailed documentation, see:
- [WEBRTC-DEPLOYMENT.md](../../docs/WEBRTC-DEPLOYMENT.md)
- [WEBRTC-SWARM-MESH.md](../../docs/WEBRTC-SWARM-MESH.md)
- [SECURITY_HARDENING.md](../../SECURITY_HARDENING.md)

For issues:
- Check IF.witness logs
- Review troubleshooting section
- Open GitHub issue with logs
