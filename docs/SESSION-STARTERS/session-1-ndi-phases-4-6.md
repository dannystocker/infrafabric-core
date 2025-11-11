# Session 1: NDI Witness — Phases 4-6

**Continuation after Phase 3 (Core Implementation)**

---

## Phase 4: Integration Hardening

| Task | File | Model | Blocked? |
|------|------|-------|----------|
| Fix hash chain edge cases | src/communication/ndi_witness_publisher.py | Sonnet 4.5 | IF Session 4 (SIP) blocks: help Session 2 (WebRTC docs) |
| Debug NDI metadata injection bugs | src/communication/ndi_guardian_viewer.py | Sonnet 4.5 | Same: assist Session 5 (CLI tests) |
| Resolve Session 4 SIP integration issues | tests/test_ndi_witness.py | Sonnet 4.5 | **IDLE TASK:** Improve test coverage for Sessions 2, 3, 5 |

---

## Phase 5: Optimization

| Task | File | Model | Notes |
|------|------|-------|-------|
| Reduce bandwidth: compress NDI metadata packets | src/communication/ndi_witness_publisher.py | Sonnet 4.5 | Profile frame sizes first |
| Latency tuning: optimize hash chain verification | src/communication/ndi_guardian_viewer.py | Sonnet 4.5 | Target <50ms overlay render |
| Benchmark witness signature verification | tests/test_ndi_witness.py | Sonnet 4.5 | Ed25519 crypto overhead measurement |

---

## Phase 6: Autonomous Monitoring

| Task | File | Model | Notes |
|------|------|-------|-------|
| Implement 24/7 health checks | src/communication/ndi_health_monitor.py | Sonnet 4.5 | Stream uptime tracking |
| Create alerting for hash chain breaks | src/communication/ndi_witness_publisher.py | Sonnet 4.5 | Log to IF.witness event system |
| Dashboard: stream status & witness integrity | docs/NDI-WITNESS-INTEGRATION.md | Sonnet 4.5 | Update case study with metrics |

---

**Total Lines (this doc): 24**
