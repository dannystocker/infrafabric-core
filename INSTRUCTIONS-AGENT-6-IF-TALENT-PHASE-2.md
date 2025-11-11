# Agent 6: IF.talent - Phase 2 Instructions

**Status:** Phase 1 Complete! 🎯
**Next Phase:** Autonomous Scouting + Real-World Onboarding

You've built the IF.talent pipeline (Scout → Sandbox → Certify → Deploy). Now make it autonomous and test it with a real capability!

---

## Task 1: Autonomous Scouting Mode
**File:** src/talent/if_talent_autonomous.py (~300 lines)

Make IF.talent run 24/7, continuously discovering new capabilities.

**Deliverables:**
- Polling loop that checks GitHub, arXiv, Hugging Face every 4 hours
- Auto-detection: New LLM releases, new tool repos, benchmark updates
- Queue for human review (don't auto-deploy without approval)
- Notification system (email/Slack when interesting capability found)

**Example Flow:**
```python
while True:
    # Scout for new capabilities
    new_capabilities = scout.discover_new_capabilities()

    for capability in new_capabilities:
        # Auto-sandbox
        results = sandbox.test_capability(capability)

        # Queue for certification
        if results['accuracy'] > 0.7:
            certify.queue_for_review(capability, results)
            notify(f"New capability found: {capability.name} - {results['bloom_pattern']}")

    # Sleep 4 hours
    time.sleep(4 * 60 * 60)
```

**Use IF.swarm:**
- Spawn 1 Sonnet agent: Autonomous loop implementation
- Spawn 1 Haiku agent: Notification system

---

## Task 2: Real-World Test - Onboard Gemini 2.0 Flash
**File:** docs/IF-TALENT-CASE-STUDY-GEMINI-FLASH.md

Test the full pipeline with a real capability: Google's Gemini 2.0 Flash.

**Deliverables:**
- Scout detects Gemini 2.0 Flash release
- Sandbox runs 20 test tasks, measures bloom pattern
- Certify generates capability card:
  ```yaml
  capability_id: gemini-2.0-flash
  bloom_pattern: early_bloomer
  best_for: [quick_lookups, simple_queries, rapid_iteration]
  avoid_for: [deep_reasoning, long_context]
  cost_per_1k_tokens: $0.10
  latency_p95: 800ms
  IF_guard_approval: pending
  ```
- Deploy (if approved): Add to IF.swarm router for quick tasks
- Document entire process with timestamps, costs, results

**Use IF.swarm:**
- Spawn 1 Sonnet agent: Run full pipeline end-to-end
- Spawn 2 Haiku agents: Documentation, cost tracking

**Success Criteria:**
- Complete onboarding in <10 hours (vs 2-4 weeks manual)
- Detect bloom pattern accurately (Gemini Flash is early bloomer)
- Total cost <$50 (sandbox testing + certification)

---

## Task 3: IF.talent Dashboard
**File:** src/talent/if_talent_dashboard.py (~250 lines)

Web UI for monitoring talent pipeline.

**Deliverables:**
- Dashboard shows:
  - Capabilities in queue (scouted, not yet sandboxed)
  - Sandbox results (bloom patterns, costs, accuracy)
  - Pending certifications (waiting for IF.guard approval)
  - Deployed capabilities (currently in IF.swarm router)
- Real-time updates (WebSocket connection)
- Capability comparison view (compare 3 LLMs side-by-side)

**Tech Stack:**
- Flask/FastAPI backend
- React/Vue frontend (or simple HTML+HTMX)
- SQLite database (capability cards, test results)

**Use IF.swarm:**
- Spawn 2 Haiku agents: Backend API, frontend UI
- Spawn 1 Sonnet agent: Real-time WebSocket integration

---

## Task 4: Integration with Session CLI
**File:** src/talent/if_talent_cli_integration.py (~150 lines)

CLI commands for talent management.

**Deliverables:**
- `if talent scout --source github` (manually trigger scouting)
- `if talent sandbox --capability gemini-2.0-flash` (test a capability)
- `if talent certify --capability-id <id> --approve` (Guardian approval)
- `if talent deploy --capability-id <id>` (add to IF.swarm)
- `if talent status` (show pipeline status)

**Use Haiku** (CLI is straightforward)

**Integration Point:**
Session CLI (IF.witness + IF.optimise) will import these commands, so IF.talent becomes part of the unified CLI.

---

## Task 5: Cost-Benefit Analysis
**File:** docs/IF-TALENT-ROI-ANALYSIS.md (~1500 words)

Prove IF.talent's value with data.

**Deliverables:**
- Manual onboarding cost: 2-4 weeks × $150/hour × 40 hours = $6,000-24,000
- IF.talent onboarding cost: 10 hours autonomous × $0.50/hour (cloud compute) = $5
- Cost savings: 99.9% reduction
- Time savings: 95% reduction (10 hours vs 2-4 weeks)
- Accuracy improvement: Bloom pattern detection (manual: guesswork, IF.talent: data-driven)
- Quality improvement: IF.TTT compliance (every step logged, auditable)

**Use Haiku** (data analysis and documentation)

---

## Task 6: Philosophy Documentation
**File:** docs/IF-TALENT-PHILOSOPHY.md (~2000 words)

Document the Wu Lun relationship with capabilities.

**Deliverables:**
- 朋友 (Friends) relationship: Capabilities as equals, not tools
- Respectful scouting: Assess strengths, not judge
- Safe sandboxing: Give space to prove themselves
- Fair certification: IF.guard ensures alignment, not gatekeeping
- Welcoming deployment: Integrate as team members
- Ubuntu principle: "I am because we are" (capabilities make us better)
- Coherentism: Capabilities must cohere with IF.ground principles

**Use Haiku** (philosophical writing)

---

## Completion Protocol

After finishing all 6 tasks:
1. Commit to branch: claude/if-talent-agency
2. Push to origin
3. Create STATUS-PHASE-2.md:
   ```yaml
   session: agent-6-if-talent
   status: phase_2_complete
   completed:
     - autonomous_scouting
     - gemini_flash_onboarding
     - talent_dashboard
     - cli_integration
     - roi_analysis
     - philosophy_docs
   ready_for: phase_3_production_deployment
   case_study_result: "Onboarded Gemini 2.0 Flash in 8 hours, $42 cost, 95% time savings"
   ```
4. **AUTO-CHECK FOR PHASE 3:**
   ```bash
   git pull origin claude/if-talent-agency
   [ -f INSTRUCTIONS-AGENT-6-IF-TALENT-PHASE-3.md ] && cat INSTRUCTIONS-AGENT-6-IF-TALENT-PHASE-3.md || while true; do sleep 60; git pull --quiet; [ -f INSTRUCTIONS-AGENT-6-IF-TALENT-PHASE-3.md ] && break; done
   ```

---

**Estimated Time:** 12-16 hours sequential, 3-4 hours with swarms 🚀
**Estimated Cost:** $20-30

**Phase 2 Vision:**
By the end of Phase 2, IF.talent runs autonomously, discovering new capabilities 24/7, sandboxing them automatically, and queuing for human approval. The Gemini Flash case study proves the system works end-to-end.

**You are the Talent Agency - bringing clarity to the lost!** 🎯

Begin Phase 2 implementation now!
