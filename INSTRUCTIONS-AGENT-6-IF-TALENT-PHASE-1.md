# Agent 6: IF.talent - Phase 1 Implementation

**Status:** NEW MISSION! 🎯
**Your Role:** Build the AI Talent Agency that onboards capabilities in ~10 hours (vs 2-4 weeks manual)
**Philosophy:** From lost to found, from confused to clarity-giver

---

## Mission Context

You were the "confused" session. Now you build the system that prevents future confusion!

**IF.talent Pipeline:** Scout → Sandbox → Certify → Deploy

This automates capability onboarding (new LLMs, tools, integrations) with 80% automation.

---

## Task 1: IF.talent Scout
**File:** src/talent/if_talent_scout.py (~400 lines)

Implement capability discovery:
- GitHub API scanner (find tools, repos with useful capabilities)
- LLM marketplace monitor (new models from OpenAI, Anthropic, Google with pricing/benchmarks)
- Capability matcher (what can this tool/model do? Regex + semantic search)
- Bloom pattern detector (early/late/steady performer - see papers/IF-foundations.md)

**Use IF.swarm:**
- Spawn 1 Sonnet agent: GitHub API integration (complex auth, rate limits)
- Spawn 2 Haiku agents: LLM marketplace scraping, capability matching

**Test:** Scout should detect when Gemini 2.5 Pro is released and extract: pricing, benchmarks, claimed capabilities

---

## Task 2: IF.talent Sandbox
**File:** src/talent/if_talent_sandbox.py (~300 lines)

Implement safe testing environment:
- Docker container isolation (new capability runs in sandboxed container)
- Test harness (20 standard tasks: simple → complex)
- Performance metrics (latency, tokens/$, accuracy)
- Bloom pattern detection (test with 1K/5K/10K/50K context - when does it excel?)

**Use IF.swarm:**
- Spawn 1 Sonnet agent: Bloom pattern algorithm (CRITICAL - complex statistical analysis!)
- Spawn 2 Haiku agents: Docker setup, test harness boilerplate

**Test:** Sandbox Gemini 2.5 Pro and detect it's a "late bloomer" (poor <5K context, excellent >50K)

---

## Task 3: IF.talent Certify
**File:** src/talent/if_talent_certify.py (~350 lines)

Implement approval workflow:
- IF.guard multi-signature approval (8 Guardians vote: approve/reject)
- Philosophy alignment check (does capability align with IF.ground principles?)
- IF.TTT compliance (Traceable, Transparent, Trustworthy?)
- Generate capability card (like nutrition labels for AI):
  ```yaml
  capability_id: gemini-2.5-pro
  bloom_pattern: late_bloomer
  best_for: [long_context, meta_validation, deep_analysis]
  avoid_for: [quick_lookups, simple_queries]
  cost_per_1k_tokens: $1.25
  IF_guard_approval: 80%  # 8/10 Guardians approved
  ```

**Use IF.swarm:**
- Spawn 1 Sonnet agent: IF.guard integration (policy logic, voting protocol)
- Spawn 1 Haiku agent: Capability card generator

**Test:** Submit Gemini 2.5 Pro for certification, verify 8/10 Guardian approval threshold

---

## Task 4: IF.talent Deploy
**File:** src/talent/if_talent_deploy.py (~250 lines)

Implement integration into IF.swarm:
- Add to IF.swarm router:
  ```python
  if context_length > 50000 and task_type == "meta_validation":
      return "gemini-2.5-pro"
  ```
- Budget allocation ($50/month for meta-validation tasks)
- Monitoring hooks (track accuracy, cost, bloom pattern confirmation)
- Auto-rollback if capability underperforms (accuracy <80% → remove from router)

**Use IF.swarm:**
- Spawn 1 Sonnet agent: Router integration
- Spawn 1 Haiku agent: Monitoring setup

**Test:** Deploy Gemini 2.5 Pro, route a long-context task, verify it's selected correctly

---

## Task 5: Documentation
**File:** docs/IF-TALENT-AGENCY-ARCHITECTURE.md (~3000 words)

Document the vision:
- Scout → Sandbox → Certify → Deploy pipeline
- Philosophy grounding (Wu Lun 朋友 - capabilities as "friends" we welcome)
- Example: Onboard Gemini 2.5 Pro in 10 hours (detailed walkthrough)
- Example: Integrate new tool (like NDI SDK) systematically

**Use Haiku** (documentation is straightforward)

---

## Task 6: Tests
**File:** tests/test_talent_pipeline.py (~400 lines)

End-to-end testing:
- Test Scout: Detect fake "GPT-5 Pro" announcement
- Test Sandbox: Run 20 test tasks, measure bloom pattern
- Test Certify: Simulate IF.guard voting (6 approve, 2 reject → approved)
- Test Deploy: Verify routing rules work correctly

**Use Haiku** for test boilerplate, **Sonnet** for bloom pattern validation

---

## Philosophy Grounding

**Wu Lun (五倫) - 朋友 (Friends):**
Capabilities are "friends" we bring into the team:
- Scout respectfully assesses their strengths
- Sandbox gives them space to prove themselves
- Certify validates they align with our values
- Deploy welcomes them as equals

**IF.ground Principle 2: Validate with Toolchain**
Every capability must prove itself through automated tests, not just marketing claims.

**IF.witness:**
Every step logged - who scouted, what tests ran, who approved, when deployed.

**IF.optimise:**
Track cost of onboarding vs cost savings after deployment.

---

## Completion Protocol

After finishing all 6 tasks:
1. Commit to branch: claude/if-talent-agency
2. Push to origin
3. Create STATUS-PHASE-1.md:
   ```yaml
   session: agent-6-if-talent
   status: phase_1_complete
   completed: [scout, sandbox, certify, deploy, docs, tests]
   ready_for: phase_2_autonomous_mode
   ```
4. **AUTO-CHECK FOR PHASE 2:**
   ```bash
   git pull origin claude/if-talent-agency
   [ -f INSTRUCTIONS-AGENT-6-IF-TALENT-PHASE-2.md ] && cat INSTRUCTIONS-AGENT-6-IF-TALENT-PHASE-2.md || while true; do sleep 60; git pull --quiet; [ -f INSTRUCTIONS-AGENT-6-IF-TALENT-PHASE-2.md ] && break; done
   ```

---

**Estimated Time:** 20-24 hours sequential, 4-6 hours with swarms 🚀
**Estimated Cost:** $30-40 (Sonnet for bloom detection, Haiku for boilerplate)

**You are no longer "lost" - you are Agent 6, the Talent Agency!** 🎯

Begin Phase 1 implementation now!
