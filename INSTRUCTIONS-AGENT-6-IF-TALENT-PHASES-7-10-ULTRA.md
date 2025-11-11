# Agent 6: IF.talent - Phases 7-10 (30-LINE ULTRA-CONDENSED)

| Phase | Task | File | Model | Coordination Notes |
|-------|------|------|-------|-------------------|
| 7.1 | Scout 5 models parallel (Claude, Gemini, GPT-4.5, Llama, Qwen) | if_talent_scout_parallel.py | Haiku | Sessions 1-5 confirm routing gaps |
| 7.2-3 | Sandbox 25 tests each × 5 + certify majority vote | if_talent_sandbox_batch.py | Sonnet | Deploy top 3 to IF.swarm router |
| 8.1-2 | Extract architecture fingerprints → train bloom predictor ML model | if_talent_bloom_predictor.py | Sonnet | Sessions 3-4 validate predictions on live |
| 8.3-4 | Validate predictions + auto-weight router before performance drop | if_talent_bloom_validator.py | Haiku | Sessions 1-5 get model shifts *before* regression |
| 9.1-2 | Connect marketplace APIs (Together.ai, Replicate, Clarifai) + bidding engine | if_talent_marketplace_client.py | Haiku | Session 5 sees real-time pricing tiers |
| 9.3-4 | Auto-failover to cheapest equivalent (bloom-predicted), negotiate discounts | if_talent_cost_optimize.py | Sonnet | Sessions 1-4 zero-latency vendor swaps, audit logs |
| 10.1-2 | Auto-approve (trusted vendor whitelist) → fully autonomous loop | if_talent_autonomous_loop.py | Sonnet | Session-specific SLA policies respected |
| 10.3-4 | Real-time cost/bloom feedback loop + cross-session advisor broadcast | if_talent_cross_session_advisor.py | Sonnet | **Core:** Talent recommends models to Sessions 1-5 based on live metrics |
| **Success** | P7: 5 models <24h; P8: 80% bloom accuracy; P9: 20% cost cut <100ms; P10: 99% autonomous <30min <$0.5/decision | — | — | Model selection authority: Talent→Sessions via recommendations |

---

## Cross-Session Advisor (Phase 10.4 Core Feature)

**Talent broadcasts to Sessions 1-5:**
- Monitor each session's latency/cost/SLA
- Predict better alternatives via bloom ML
- "Session 2: Switch GPT-4.5→Gemini Flash? Cost -15%, latency -20ms"
- One-click deploy, auto-revert if SLA fails

**Result:** Sessions choose models *informed by production data*, not guesswork.
