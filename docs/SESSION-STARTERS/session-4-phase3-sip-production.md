# Session 4 Phase 3: SIP Production Deployment (ULTRA-CONDENSED)

**Max 10 Lines:**

1. **Deploy SIP Proxy to Production (Kamailio + TLS)** | `config/kamailio-prod.cfg` | Kamailio 5.7 + OpenSSL (Ed25519 cert pinning)
2. **Configure TLS Certificates & Policy Gate** | `src/communication/sip_tls_config.py` | Python (cryptography lib, IF.guard validation)
3. **External Expert Staging Test (Real Call)** | `tests/test_sip_staging_external.py` | PyTest + real SIP endpoint (sip:expert@external.advisor)
4. **Production Monitoring & Metrics** | `src/communication/sip_monitoring.py` | Prometheus (call latency, success rate, policy rejections)
5. **Runbook: SIP Proxy Emergency Restart** | `docs/SIP-PRODUCTION-RUNBOOK.md` | Bash scripts + systemd service unit
6. **IF.witness Production Audit Trail** | `logs/sip-prod-audit.jsonl` | IF.witness logging (every INVITE/200/REJECT)
7. **Failover to Backup Proxy** | `config/kamailio-backup.cfg` + DNS failover | Hot standby (synchronized call state)
8. **Performance Baseline < 500ms ESCALATE → Ring** | Load test script | 50 concurrent ESCALATE messages
9. **Security: H.323 Bridge TLS Handshake** | `src/communication/sip_h323_tls_bridge.py` | mTLS verification (Session 3 cert pinning)
10. **Smoke Test: SIP → H.323 → Evidence Shared** | Integration test | WebRTC DataChannel evidence delivery (Session 2)

**GO NOW**
