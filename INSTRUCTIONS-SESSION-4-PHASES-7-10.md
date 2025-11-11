# Session 4 Phases 7-10: Global Scale, Advanced Features, AI Routing (ULTRA-CONDENSED)

**Max 30 Lines Total | PRIORITY: Critical path for Sessions 5-6 integration**

---

## Phase 7: Production Hardening (1000 concurrent expert calls)

| Phase | Task | File | Model | Coordination notes |
|-------|------|------|-------|-------------------|
| 7 | **PRIORITY: Connection pooling & load balancing** | `src/communication/sip_connection_pool.py` | Sonnet | Unblock Phase 8 multi-region routing |
| 7 | Circuit breaker (graceful degradation on overload) | `src/communication/sip_circuit_breaker.py` | Haiku | Prevent cascade failures |
| 7 | Resource monitoring & auto-scaling thresholds | `src/communication/sip_metrics.py` | Haiku | Prometheus alerts |
| 7 | Chaos testing (kill 10% of calls, verify recovery) | `tests/chaos/test_concurrent_failures.py` | Haiku | Load test: 1000 concurrent ESCALATE |

---

## Phase 8: Global SIP Proxy Network (Multi-region)

| Phase | Task | File | Model | Coordination notes |
|-------|------|------|-------|-------------------|
| 8 | **PRIORITY: Geo-routing logic (latency-optimal path)** | `src/communication/sip_geo_router.py` | Sonnet | Unblock Phase 9 advanced features |
| 8 | Deploy regional SIP proxies (US, EU, APAC) | `config/kamailio-regional.cfg` | Haiku | GeoIP routing, DNS SRV records |
| 8 | Cross-region call failover & state sync | `src/communication/sip_region_sync.py` | Sonnet | Redis cluster for call state |

---

## Phase 9: Advanced Features (Video calls, screen sharing, E2E encryption)

| Phase | Task | File | Model | Coordination notes |
|-------|------|------|-------|-------------------|
| 9 | **PRIORITY: WebRTC video call bridge** | `src/communication/sip_webrtc_video.py` | Sonnet | Unblock Session 2 video evidence |
| 9 | Screen sharing via VP8 simulcast | `src/communication/sip_screenshare.py` | Haiku | SRTP encryption |
| 9 | E2E encryption (Double Ratchet protocol) | `src/communication/sip_e2e_encryption.py` | Sonnet | ZRTP key exchange |
| 9 | Test: Video + E2E + evidence delivery | `tests/integration/test_video_e2e.py` | Haiku | Expert-to-verdict encrypted chain |

---

## Phase 10: AI-Powered Expert Routing (Auto-match to problems)

| Phase | Task | File | Model | Coordination notes |
|-------|------|------|-------|-------------------|
| 10 | **PRIORITY: Expert skill matching ML model** | `src/routing/expert_skill_matcher.py` | Sonnet | Unblock Session 6 talent allocation |
| 10 | Problem classification (NLP: extract domain/severity) | `src/routing/problem_classifier.py` | Sonnet | Session 4 → Route to best expert |
| 10 | Dynamic routing (skill match + availability) | `src/routing/dynamic_expert_router.py` | Haiku | ESCALATE → Ring optimal expert |
| 10 | A/B test: Manual vs AI routing (accuracy) | `tests/routing/test_ai_routing.py` | Haiku | Success rate, expert satisfaction |

---

**Timeline:** 24 hours (Phase 7-8), 16 hours (Phase 9), 12 hours (Phase 10) | **Cost:** $45 | **Unblocks:** Sessions 5-6 production deployment
