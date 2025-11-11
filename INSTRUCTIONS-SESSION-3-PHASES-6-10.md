# Session 3 (H.323) - Phases 6-10

| Phase | Task | File | Model | Notes |
|-------|------|------|-------|-------|
| **6** | Guardian council production test (12 real Guardians) | tests/production/h323_12_guardians.py | Sonnet | Live validation |
| 6 | Production runbook | docs/H323-PRODUCTION-RUNBOOK.md | Haiku | Ops documentation |
| **7** | Guardian scale (50 concurrent) | src/communication/h323_guardian_cluster.py | Sonnet | Quorum-based routing |
| 7 | Standby pool monitor | src/monitoring/h323_idle_monitor.py | Haiku | Health checks |
| **8** | MCU federation (multi-region) | src/communication/h323_mcu_federation.py | Sonnet | Cross-region sync |
| 8 | Federation watcher | src/monitoring/h323_federation_watcher.py | Haiku | Partition detection |
| **9** | E2E encryption + quantum-resistant | src/crypto/h323_crypto_suite.py | Sonnet | Lattice-based KEMs |
| 9 | Key rotation scheduler | src/crypto/h323_key_rotator.py | Haiku | Auto cert updates |
| **10** | AI admission control | src/routing/h323_ai_router.py | Sonnet | Neural net gates |
| 10 | Policy engine | src/routing/h323_policy_engine.py | Haiku | Constraint solver |

**IDLE TASKS:** Help Session 1 (NDI monitoring), Session 5 (CLI export)
**SUPPORT:** Session 4 needs H.323 gateway fixes in Phase 7

**Estimated:** 50 hours, $45 total (Phases 6-10)
