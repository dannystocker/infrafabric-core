# Session 1 (NDI) - Phases 6-10

| Phase | Task | File | Model | Notes |
|-------|------|------|-------|-------|
| **6** | Autonomous monitoring (24/7 health checks) | src/monitoring/ndi_health.py | Sonnet | Auto-alert on stream failures |
| 6 | Hash chain integrity alerts | src/monitoring/witness_alerts.py | Haiku | Real-time validation |
| **7** | Production hardening (1000 concurrent streams) | src/communication/ndi_scale.py | Sonnet | Stress test + optimize |
| 7 | NDI metadata compression | src/communication/ndi_compress.py | Haiku | Reduce bandwidth 40% |
| **8** | Multi-region (US/EU/APAC) | deploy/regions/*.yml | Sonnet | Geographic distribution |
| 8 | GDPR compliance per region | docs/NDI-COMPLIANCE.md | Haiku | Legal coordination |
| **9** | 4K HDR support | src/communication/ndi_4k_hdr.py | Sonnet | High-res witness streams |
| 9 | AI frame analysis (detect anomalies) | src/ai/frame_analyzer.py | Sonnet | ML-based validation |
| **10** | Auto-scaling (demand-based) | deploy/autoscale.yml | Sonnet | K8s HPA |
| 10 | Self-healing (auto-restart failed streams) | src/ops/self_heal.py | Haiku | Full autonomy ✓ |

**IDLE TASKS:** Help Session 2 (WebRTC docs), Session 5 (CLI tests)
**SUPPORT:** Session 4 needs NDI integration fixes in Phases 7-8

**Estimated:** 40 hours, $35 total (Phases 6-10)
