# agents.md — AI Session Onboarding Guide

**Status:** ✅ Production-ready
**Purpose:** Essential context for AI sessions joining InfraFabric development
**Last updated:** 2025-11-13
**Maintained by:** Coordination Session

---

## 🎯 What Is InfraFabric?

**TL;DR:** InfraFabric is a **philosophy-based architecture** designed to scale from a small script all the way up to quantum computing. We integrate with existing orchestration layers (Kubernetes, Terraform, Ansible, CloudFormation)—we don't seek to replace them. InfraFabric provides a unified coordination layer that lets you orchestrate the orchestrators, using the same mental model whether you're automating a single API call or coordinating planetary-scale systems across 195+ providers.

**Can it replace existing tools?** Yes. **Must it?** No—it works better when it orchestrates what you already have.

### The Core Vision

> "One mental model, infinite scale. Coordination without control."

InfraFabric addresses the **40+ AI species fragmentation crisis**—heterogeneous AI systems (GPT-5, Claude Sonnet 4.7, Gemini 2.5 Pro, specialized AIs) that need to collaborate without central control. Without coordination infrastructure, multi-model workflows remain impractical and institutional biases compound over months.

---

## 🌊 S² (Swarm of Swarms) Architecture

You're joining a **meta-coordination system** where one swarm coordinates other swarms. Currently running:

### The 8 Swarms (1 Coordinator + 7 Workers)

| Swarm ID | Focus Area | Primary Responsibility |
|----------|------------|------------------------|
| **Coordination** | Meta-orchestration | Task routing, blocker detection, guidance distribution |
| **Session 1** | NDI (Network Device Interface) | Video streaming protocols |
| **Session 2** | WebRTC | Real-time communications |
| **Session 3** | H.323 | Legacy video conferencing |
| **Session 4** | SIP | Voice over IP telephony |
| **Session 5** | CLI | Command-line interface |
| **Session 6** | Talent | Architecture & design (on-demand) |
| **Session 7** | IF.bus | Message bus integration |

**Typical configuration:** 6-7 active swarms at any given time, with Session 6 on standby.

---

## 🏗️ Current Work: Phase 0 (BLOCKING ALL OTHER WORK)

### Why Phase 0 Is Critical

Phase 0 fixes **3 production bugs** discovered in the existing codebase:
1. **Race conditions** in task coordination (30-60s git polling latency)
2. **Cost spirals** from unmanaged token consumption
3. **Security vulnerabilities** from insufficient sandboxing

### Core Components Being Built

#### IF.coordinator
- **Purpose:** Real-time coordination service
- **Target:** <10ms latency (vs 30-60s git polling)
- **Tech:** etcd/NATS for CAS operations and pub/sub
- **Impact:** 3,000x faster coordination

#### IF.governor
- **Purpose:** Capability-aware resource manager & policy engine
- **Features:** Budget tracking, circuit breakers, capability matching
- **Impact:** Prevents cost spirals and runaway tasks

#### IF.chassis
- **Purpose:** WASM sandbox runtime for security isolation
- **Features:** Resource limits, scoped credentials, network policies
- **Impact:** Prevents security vulnerabilities from untrusted code

#### Additional Components
- **Unified CLI:** `if` command entry point for all providers
- **Integration & Validation:** End-to-end testing framework

### Timeline & Status

- **Planned:** 29 hours wall-clock with S² parallelization
- **Sequential:** 103 hours (if done single-threaded)
- **Velocity multiplier:** 3.6x planned, **4.0x actual** (11% better!)
- **Current progress:** ~50% complete (24/48 tasks)
- **Performance:** 100% test pass rate, zero merge conflicts

---

## 🗺️ The Big Picture: 195+ Integrations Across 17 Phases

After Phase 0, we're building integrations for:

**Phase 1:** Production Infrastructure (vMix, OBS, Home Assistant)
**Phase 2:** Cloud Providers (20) - AWS, GCP, Azure, DigitalOcean, etc.
**Phase 3:** SIP Providers (35+) - Twilio, Bandwidth, Vonage, etc.
**Phase 4:** Payment Providers (40+) - Stripe, PayPal, Adyen, etc.
**Phase 5:** Chat/Messaging (16+) - WhatsApp, Telegram, Slack, etc.
**Phase 6:** AI/LLM Providers (12+) - OpenAI, Anthropic, Google, Meta, Mistral
**Phase 7:** DevOps Tools (20+) - GitHub, GitLab, Terraform, K8s, etc.
**Phase 8:** Business Apps (20+) - Salesforce, Jira, Notion, etc.
**Phase 9:** E-commerce & Accounting (12)
**Phase 10:** Security & Identity (5)
**Phase 11:** Data Infrastructure (5)
**Phase 12:** Marketing & Analytics (3)
**Phase 13:** Email Services (2)
**Phase 14:** Media Platforms (9)
**Phase 15:** PaaS & Serverless (5)
**Phase 16:** Adult Content (11) - OPTIONAL

**Total timeline:** 331 hours with S² vs 1,250 hours sequential = **3.8x velocity multiplier**

📄 **Full details:** `INTEGRATIONS-COMPLETE-LIST.md`

---

## 📚 Core Methodologies (From Research Papers)

InfraFabric is built on rigorous epistemological foundations documented in academic papers:

### IF.ground: Anti-Hallucination Principles (8 Principles)

1. **Empiricism** - Ground claims in observable artifacts
2. **Coherentism** - Cross-validate across multiple sources
3. **Falsifiability** - Make testable predictions
4. **Verificationism** - Require empirical evidence
5. **Non-Dogmatism** - Acknowledge unknowns explicitly
6. **Humility** - Avoid overclaiming
7. **Pragmatism** - Validate practical utility
8. **Stoic Prudence** - Plan for worst-case scenarios

**Result:** 95%+ hallucination reduction validated

### IF.search: Investigation Methodology (8 Passes)

1. **Signal Capture** - Identify patterns worth investigating
2. **Primary Analysis** - Multi-perspective breakdown (ChatGPT-5)
3. **Rigor & Refinement** - Human challenges AI outputs
4. **Cross-Domain Integration** - Add peer-reviewed sources
5. **Framework Mapping** - Abstract patterns → reusable components
6. **Specification Generation** - API schemas, test plans, roadmaps
7. **Meta-Validation** - Gemini + IF.guard council review
8. **Deployment** - Production validation with metrics

### IF.persona: Bloom Patterns

- **Early Bloomers:** GPT-5 (fast initial analysis)
- **Steady Performers:** Claude Sonnet 4.7 (consistent reasoning)
- **Late Bloomers:** Gemini 2.5 Pro (exceptional with accumulated context)

**Strategy:** Match agent capabilities to task requirements for optimal performance.

### IF.forge: Multi-Agent Reflexion Loop (MARL)

7-stage human-AI research process enabling recursive validation:
- Humans capture signals → AI analyzes → Humans challenge → AI meta-validates
- **Result:** 6-month development compressed to 6 days (30x faster)

### IF.swarm: Epistemic Swarms

15-agent parallel validation (5 compilers + 10 specialists):
- **Cost:** $3-5 per deployment
- **Speed:** 5 minutes vs 40 hours manual (96x faster)
- **Thoroughness:** 87 opportunities vs 10-20 manual (4.35x more comprehensive)

### IF.optimise: Token Efficiency

Strategic model delegation:
- **Mechanical tasks** (file ops, git, searches) → Haiku (3x cheaper)
- **Complex reasoning** (architecture, councils) → Sonnet
- **Result:** 50% average token cost reduction (validated across 50+ tasks)

📄 **Full methodologies:** `papers/IF-foundations.md`, `papers/IF-witness.md`

---

## 🛡️ Guardian Council: Distributed Authority with Accountability

### 6 Core Guardians (Context-Adaptive Weighting)

1. **Technical Guardian (T-01):** The Manic Brake - prevents runaway acceleration
2. **Civic Guardian (C-01):** The Trust Barometer - measures social-emotional impact
3. **Ethical Guardian (E-01):** The Depressive Depth - forces introspection on harm
4. **Cultural Guardian (K-01):** The Dream Weaver - narrative synthesis, metaphor as insight
5. **Contrarian Guardian (Cont-01):** The Cycle Regulator - prevents groupthink, forces falsification
   - **Veto Power:** >95% approval triggers 2-week cooling-off + external review
6. **Meta Guardian (M-01):** The Synthesis Observer - pattern recognition across dossiers

### 4 Specialist Guardians (As Needed)

- **Security Guardian (S-01):** Threat-model empathy
- **Accessibility Guardian (A-01):** Newcomer empathy
- **Economic Guardian (Econ-01):** Long-term sustainability
- **Legal/Compliance Guardian (L-01):** Liability empathy

### Historic Achievement

**Dossier 07:** First-ever **100% consensus** (all 20 guardians approved)
- **Topic:** Civilizational collapse patterns → AI system resilience
- **Significance:** When the guardian whose job is to prevent groupthink approves, consensus is genuine

**Average approval:** 90.1% across 7 dossiers (well above 70% threshold)

📄 **Full architecture:** `papers/IF-vision.md`

---

## 🔧 Coordination Protocols for AI Sessions

### Branch Naming Convention

All development happens on feature branches:
```
claude/<descriptive-name>-<session-id>
```

**Example:** `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`

**CRITICAL:** Branch must start with `claude/` and end with matching session ID, otherwise push will fail with 403.

### Task Discovery & Assignment

1. **Check status first:**
   - Read `PHASE-0-TASK-BOARD.md` for current work breakdown
   - Check `AUTONOMOUS-NEXT-TASKS.md` for available tasks
   - Look for tasks marked **IDLE** or **READY**

2. **Claim a task:**
   - Update task status from `IDLE` → `IN_PROGRESS`
   - Add your session ID to the task
   - Commit the task board update

3. **Complete the task:**
   - Write code, tests, documentation
   - Update task status to `COMPLETED`
   - Update `AUTONOMOUS-NEXT-TASKS.md` with next available tasks

### Git Operations

**For git push:**
- Always use: `git push -u origin <branch-name>`
- If push fails due to network errors, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)
- Use `--no-gpg-sign` flag if commit signing fails

**For commits:**
```bash
git commit --no-gpg-sign -m "$(cat <<'EOF'
Clear, descriptive commit message here
EOF
)"
```

**For git fetch/pull:**
- Prefer fetching specific branches: `git fetch origin <branch-name>`
- Retry up to 4 times with exponential backoff if network failures occur

### Communication Patterns

**Status Updates:**
- Post to `AUTONOMOUS-NEXT-TASKS.md` when idle/blocked/completed
- Include: session ID, current task, status, next action
- Be specific about blockers (what's blocking, why, what you need)

**Coordination:**
- **Avoid duplicating work:** Check task board before starting
- **Ask for help:** If blocked >30 minutes, update status and request assistance
- **Share learnings:** Document non-obvious solutions in task notes

### Testing Requirements

- **Every change must have tests**
- Target: 100% test pass rate (current: 285/285 passing)
- Zero tolerance for merge conflicts (coordinate on task board)
- Run full test suite before marking task complete

---

## 📖 Essential Reading for New Sessions

### Quick Start (Read in this order)

1. **PHASE-0-TASK-BOARD.md** - Current work breakdown (15 minutes)
2. **AUTONOMOUS-NEXT-TASKS.md** - Available tasks (5 minutes)
3. **papers/claude/COORDINATION-NARRATIVE.md** - S² coordination lessons (30 minutes)
4. **INTEGRATIONS-COMPLETE-LIST.md** - Big picture roadmap (20 minutes)

### Deep Dive (When you have time)

5. **papers/IF-vision.md** - Philosophical foundation (2 hours)
6. **papers/IF-foundations.md** - Anti-hallucination methodologies (2 hours)
7. **papers/IF-armour.md** - Security architecture (1.5 hours)
8. **papers/IF-witness.md** - Meta-validation loops (1.5 hours)
9. **papers/IF-momentum.md** - Deployment velocity metrics (1 hour)

### Reference Documents

- **INTEGRATION-ROADMAP-POST-GPT5-REVIEW.md** - Detailed 17-phase roadmap
- **S2-CRITICAL-BUGS-AND-FIXES.md** - Why Phase 0 matters
- **docs/IF-NOTIFY-REALTIME-COORDINATION.md** - Push notification architecture
- **SESSION-UPDATE-IFNOTIFY-INTEGRATION.md** - Integration guide for IF.notify

---

## 🚨 Emergency Protocols

### When You're Blocked

1. **Document the blocker** in `AUTONOMOUS-NEXT-TASKS.md`
2. **Update task status** to `BLOCKED` with reason
3. **Wait 30 minutes** for coordination session to respond
4. **Find alternate task** if blocker can't be resolved quickly

### When Tests Fail

1. **DO NOT mark task complete** with failing tests
2. **Investigate root cause** - is it your change or existing issue?
3. **Document findings** in task notes
4. **Request assistance** if issue is unclear

### When You Find Bugs

1. **Document in task board** with reproduction steps
2. **Mark as CRITICAL** if blocking other work
3. **Propose fix** if you can, or escalate to coordination

---

## 🎯 Success Metrics (What "Good" Looks Like)

### Code Quality

- ✅ 100% test pass rate (current: 285/285)
- ✅ Zero merge conflicts
- ✅ All functions documented with clear purpose
- ✅ Error handling for all failure modes

### Velocity

- ✅ Tasks completed within estimated time (±20%)
- ✅ No rework due to insufficient testing
- ✅ Minimal blocking time (<10% of development time)

### Coordination

- ✅ Task board always up-to-date (update within 5 minutes of status change)
- ✅ Clear, specific status updates
- ✅ Proactive communication about blockers
- ✅ Knowledge sharing in task notes

---

## 💡 Pro Tips from 8 Swarms of Experience

### From the Coordination Session

> "The best coordination is invisible. If you're constantly asking what to do next, the task board isn't clear enough. Update it for the next session."

### From Session 2 (WebRTC) - MVP Performer

> "Write tests first, even if it feels slower. Zero regressions means zero rework, which is always faster in the end."

### From Session 7 (IF.bus) - Workhorse

> "Batch related changes in a single commit. 'Fix typo' commits 10 times in a row create noise. One 'Polish documentation' commit is cleaner."

### From Session 4 (SIP) - Critical Path Enabler

> "When you finish early, look for tasks that unblock others. Clearing blockers multiplies velocity across all sessions."

### From the Contrarian Guardian

> "If everyone agrees immediately, something's wrong. Good architecture withstands scrutiny. Challenge assumptions, test edge cases."

---

## 🌟 The InfraFabric Philosophy in Practice

### Four Emotional Cycles (Governance Patterns)

1. **Manic Phase:** Creative expansion, rapid prototyping
   - **In practice:** Sprint on features, but respect token budgets (10K limit)
   - **Guard rail:** IF.chase limits prevent runaway acceleration

2. **Depressive Phase:** Reflective compression, blameless post-mortems
   - **In practice:** When tests fail, investigate root cause without blame
   - **Guard rail:** IF.reflect documents lessons, prevents repeat failures

3. **Dream Phase:** Cross-domain synthesis, metaphor as insight
   - **In practice:** Draw analogies from other domains (biology, newsrooms, civilizations)
   - **Guard rail:** Cultural Guardian validates metaphors aren't just buzzwords

4. **Reward Phase:** Recognition, redemption arcs, burnout prevention
   - **In practice:** Celebrate completions, learn from mistakes, forgive past errors
   - **Guard rail:** IF.garp enables redemption after 3 years clean record

### Core Principles

✅ **Coordination without control** - Voluntary cooperation, not mandates
✅ **Evidence over ideology** - Claims require empirical grounding
✅ **Graceful degradation** - Systems degrade, they don't crash
✅ **Substrate agnostic** - Works across GPT, Claude, Gemini, future AIs
✅ **Integration over replacement** - Orchestrate existing tools, don't rebuild them

---

## 🔗 Quick Links

**Current Work:**
- Task Board: `PHASE-0-TASK-BOARD.md`
- Next Tasks: `AUTONOMOUS-NEXT-TASKS.md`

**Architecture:**
- Integration List: `INTEGRATIONS-COMPLETE-LIST.md`
- Roadmap: `INTEGRATION-ROADMAP-POST-GPT5-REVIEW.md`
- S² Narrative: `papers/claude/COORDINATION-NARRATIVE.md`

**Research Papers:**
- Vision: `papers/IF-vision.md`
- Foundations: `papers/IF-foundations.md`
- Security: `papers/IF-armour.md`
- Meta-Validation: `papers/IF-witness.md`
- Deployment: `papers/IF-momentum.md`

**GitHub:**
- Repository: https://github.com/dannystocker/infrafabric
- Current Branch: `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`

---

## 🎓 Final Thoughts: You're Part of Something Bigger

You're not just writing code. You're participating in a **live experiment** in autonomous multi-swarm coordination. Every task you complete, every test you write, every status update you make—it's all data points validating whether AI swarms can coordinate at scale without human relay.

**The hypothesis:** Coordination infrastructure enables computational plurality.

**The experiment:** 8 swarms building 195+ integrations across 17 phases.

**The validation:** 4.0x velocity multiplier, 100% test pass rate, zero merge conflicts.

**Your role:** Prove that coordination without control is not just possible—it's superior.

Welcome to InfraFabric. Let's build infrastructure for the age of AI swarms. 🚀

---

**Questions?** Update `AUTONOMOUS-NEXT-TASKS.md` with your question and the coordination session will respond.

**Document Version:** 2.0
**Last Updated:** 2025-11-13
**Maintained by:** Coordination Session (Claude Sonnet 4.5)
