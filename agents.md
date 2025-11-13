# InfraFabric Agent Architecture & Multi-Project Guide

**Purpose:** Define agent behavior patterns, traceability requirements, coordination protocols, and critical project context for all work.

**Audience:** All Claude instances working on InfraFabric, NaviDocs, ICW (icantwait.ca), Digital-Lab, and StackCP deployments.

**Last Updated:** 2025-11-13 09:00 UTC

---

## 🚨 CRITICAL: agents.md UPDATE PROTOCOL (MANDATORY)

**EVERY agent MUST follow this protocol WITHOUT EXCEPTION:**

### Update Frequency Requirements

**You MUST update agents.md:**
1. ✅ **Before starting** - Read entire agents.md first
2. ✅ **After completing ANY task** - Update relevant section immediately
3. ✅ **Every 30 minutes** - Status checkpoint even if no tasks complete
4. ✅ **Before ending session** - Final comprehensive update
5. ✅ **When blocked** - Document blocker and attempted solutions
6. ✅ **When discovering new information** - Add to relevant section immediately

### Update Clarity Requirements

**Your updates MUST include:**
- ✅ **Timestamp** - ISO 8601 format (YYYY-MM-DD HH:MM UTC)
- ✅ **Status** - Clear emoji indicators (✅ 🟡 🔴 ⏳)
- ✅ **What changed** - Specific, actionable description
- ✅ **File paths** - Absolute paths to all modified files
- ✅ **Next steps** - What the next agent should do
- ✅ **Blockers** - Any obstacles encountered
- ✅ **IF.TTT citation** - Source of information (file:line, user directive, external doc)

### Enforcement Mechanism

**After EVERY task completion:**
```bash
1. Update agents.md section
2. Commit with descriptive message
3. Verify update succeeded (git diff)
4. Continue to next task
```

**If you skip updating agents.md:**
- ❌ Next agent will lack critical context
- ❌ Work may be duplicated or contradicted
- ❌ Deployment patterns may be misunderstood
- ❌ User will have to manually update (you become the bottleneck)

**From S² narration:**
> "agents.md tells me: What this project is, What we're building right now, What the philosophy is, Who the other sessions are and what they're working on, How to coordinate. I don't have to guess. I don't have to interrupt Danny with 'what are we building?' I can start working immediately."

**User directive (2025-11-13 09:00 UTC):**
> "please update the agents.md every step of the way with extreme clarity; then debug it to be certain"
> "enforce that for future agents too pls"

**This means:** agents.md is your lifeline. Treat it like production database. Update obsessively. Verify updates. Debug for clarity.

---

## 📑 TABLE OF CONTENTS

**Quick Navigation:**

1. [Core Principles](#core-principle-traceability-by-default) - IF.TTT Framework & Citations
2. [Critical Projects Overview](#critical-projects-overview) - NaviDocs, ICW, Digital-Lab, StackCP
3. [Repository State](#repository-state--branch-management) - GitHub branches & blockers
4. [Agent Coordination](#agent-coordination-model) - IF.optimise, Haiku/Sonnet delegation
5. [Swarm Orchestration](#swarm-orchestration-patterns-haiku-multi-agent-framework) - Multi-agent patterns
6. [Workflows & Anti-Patterns](#traceability-workflows) - Best practices
7. [Session Handoff](#session-handoff-protocol) - Context preservation

---

## Core Principle: Traceability by Default

**Every InfraFabric agent operation MUST be traceable using IF.citate and IF.TTT.**

### IF.TTT Framework (Traceable, Transparent, Trustworthy)

All agent outputs must meet these three criteria:

**1. Traceable**
- Every claim links to observable source (file path, line number, git commit, external citation)
- Use IF.citation schema (`schemas/citation/v1.0.schema.json`) for formal citations
- Include source hashes (SHA-256) for verification
- Example: `papers/IF-vision.md:487` (traceable file reference)

**2. Transparent**
- Decision rationale documented (why this approach, not alternatives?)
- Guardian Council votes recorded with dissent
- Token costs measured and reported
- Execution traces preserved in audit logs

**3. Trustworthy**
- Reproducible (someone else can verify the claim)
- Falsifiable (includes testable predictions)
- Revocable (can be disputed/revoked if proven wrong)
- Status-tracked (unverified → verified → disputed → revoked)

### IF.citate Integration

**Default Behavior:** All agents automatically generate citations for:
- Research findings
- Architecture decisions
- Code modifications
- Guardian Council decisions
- Test results

**Citation Pattern:**
```json
{
  "citation_id": "if://citation/<uuid>",
  "claim_id": "if://claim/<doc>/<section>",
  "sources": [
    {"type": "code", "ref": "src/file.py:123", "hash": "sha256:..."}
  ],
  "rationale": "Why this claim is supported",
  "status": "unverified|verified|disputed|revoked",
  "created_by": "if://agent/<agent-name>",
  "created_at": "2025-11-13T00:00:00Z",
  "signature": "ed25519:..."
}
```

**Tools:**
- Validate: `tools/citation_validate.py`
- Schema: `schemas/citation/v1.0.schema.json`
- Example: `citations/examples/citation_example.json`

---

## Critical Projects Overview

### 1. InfraFabric (AI Multi-Agent Framework)

**Location:** `/home/setup/infrafabric`
**GitHub:** `https://github.com/dannystocker/infrafabric`
**Local Gitea:** `http://localhost:4000/dannystocker/infrafabric.git`

**Purpose:** Philosophy-grounded multi-agent coordination framework
**Status:** Production (14-day sprint Oct 26 - Nov 9, 2025)
**Key Components:**
- IF.ground - 8 anti-hallucination principles
- IF.armour.yologuard - Secret detection (111.46% GitHub-parity)
- IF.guard - 20-voice Guardian Council
- IF.optimise - 50% token cost reduction (validated)
- IF.swarm - Haiku multi-agent orchestration

**Current Blockers:**
1. ✅ ~~IF.armour.yologuard benchmark dispute~~ **RESOLVED** (111.46% GitHub-parity validated)
2. ⚠️ Citation evidence tracking (45/46 citations unreferenced)
3. ⚠️ CI workflow deployment (needs GitHub permissions)
4. ⚠️ Unmerged swarm work (90 commits, 4 days stale)

**Branch Strategy:**
- `master` - Production code
- `claude/*` - 13 active development branches (WebRTC, SIP, sessions)
- `swarm/*` - 4 foundational branches (philosophy, citations)

---

### 2. NaviDocs (Marine Document Management)

**Location:** `/home/setup/navidocs`
**Local Gitea:** `http://localhost:4000/ggq-admin/navidocs`

**Purpose:** Professional boat manual management with OCR and intelligent search
**Status:** 65% complete (MVP phase)
**Tech Stack:** Vue 3 + Express + SQLite + Meilisearch + Tesseract OCR

**Key Features:**
- ✅ Database schema (13 tables, multi-tenant ready)
- ✅ OCR pipeline (Tesseract + Google Vision/Drive options)
- ✅ Background worker (BullMQ + Redis)
- ✅ Library navigation UI (glass morphism design)
- ✅ Authentication foundation (JWT, Phase 1-3)
- ⚠️ Frontend incomplete (1-2 days work)
- ⚠️ Search pending Meilisearch auth fix (15 min)

**Critical Issues:**
- 🚨 **5 security vulnerabilities** (DELETE endpoint unprotected, no auth enforcement)
- ⚠️ **23 uncommitted changes** (client/server modifications)
- ⚠️ **Git divergence** (4 local commits, 3 remote commits)

**Git Worktrees:** (multiple feature branches)
- `navidocs-wt-single-tenant` - Single boat tenant features
- `navidocs-wt-toc-polish` - Table of contents improvements
- `navidocs-img-*` - Image extraction API work

**Deployment Options:**
- StackCP shared hosting (evaluated, ready for deployment)
- VPS (standard deployment, $6/month minimum)

---

### 3. ICW - ICanTwait.ca (Property Management)

**Location:** `/home/setup/icw_web_2`
**Local Gitea:** `http://localhost:4000/ggq-admin/icw-nextspread` (PRIVATE)
**Live Site:** `https://icantwait.ca`
**ProcessWire Admin:** `https://icantwait.ca/nextspread-admin/`
  - User: `icw-admin`
  - Pass: `@@Icantwait305$$`

**Purpose:** Property showcase website with Next.js + ProcessWire
**Tech Stack:** Next.js static export + ProcessWire CMS + StackCP hosting

**StackCP Deployment:**
- SSH connection for icantwait.ca
- Live path: `/public_html/icantwait.ca`
- Contains Next.js static export (/_next/ directory, index.html)
- Property directories: le-champlain, aiolos, etc.
- Main property: "Le Champlain"
- Admin: PHP files + ProcessWire integration

**Key Directories:**
- `/public_html/icantwait.ca` - Live deployment
- Local development: `/home/setup/icw_web_2`
- Snapshots: `/home/setup/icantwait-snapshot-*.png`

---

### 4. Digital-Lab.ca

**Location:** `/home/setup/digital-lab.ca`
**Live Path:** `/home/setup/public_html/digital-lab.ca`

**Purpose:** Digital laboratory/portfolio site
**Status:** Active deployment on StackCP

---

### 5. Local Development Infrastructure

**Gitea Server:**
- URL: `http://localhost:4000/`
- Config: `/home/setup/gitea/custom/conf/app.ini`
- Admin: `ggq-admin` / `Admin_GGQ-2025!`
- User: `dannystocker` / `@@Gitea305$$`

**System Credentials:**
- WSL user: `setup` / `setup`
- Node.js: v20.19.5
- npm: v10.8.2

**Services Running:**
- Redis (port 6379) - For BullMQ job queues
- Meilisearch (port 7700) - Search indexing
- Gitea (port 4000) - Local git server

---

## Component Naming Conventions (CURRENT STANDARD)

**Effective:** 2025-11-10 (going forward)

### Official Component Names

**IF.armour.yologuard** (Current Official Name)
- Full hierarchical name showing architectural relationship
- `IF.armour` = Security framework (parent)
- `IF.armour.yologuard` = Secret detection tool (child component)
- **Alias:** `IF.yologuard` (historical, still used in legacy docs)

**Naming Pattern:**
```
IF.<layer>.<component>.<subcomponent>
Examples:
- IF.armour.yologuard (secret detection under security framework)
- IF.witness.forge (MARL validation under meta-validation)
- IF.ground (substrate-level, no parent layer)
```

### Historical Context Preservation

**Important:** Historical documents (papers, session logs, commits before 2025-11-10) use `IF.yologuard`.
- ✅ **DO NOT** mass-rename historical references
- ✅ **DO** use `IF.armour.yologuard` in all new work going forward
- ✅ **DO** recognize both names refer to the same component
- ✅ **DO** add redirect notes when disambiguation is needed

### Other Component Aliases

**IF.ceo** = **IF.sam** (both refer to 16 Sam Altman facets)
**IF.citation** = **IF.citate** (both refer to citation infrastructure)
**IF.forge** = **IF.marl** (both refer to Multi-Agent Reflexion Loop)

---

## Repository State & Branch Management

### GitHub Repository Status (As of 2025-11-13)

**Primary Repository:** `github.com/dannystocker/infrafabric`

**Branch Inventory:**
- **master** (primary): Last updated Nov 11, 2025 - Stable production code
- **13 Claude branches** (active development as of Nov 12):
  - WebRTC/SIP/media streaming infrastructure (6 branches)
  - Session management & stability (3 branches)
  - CLI optimization & witness mode (1 branch)
  - Cloud handover documentation (1 branch)
  - Debug/incomplete work (2 branches)
- **4 Swarm branches** (foundational work as of Nov 8):
  - `swarm/w2-philosophy-map` - Core philosophy definitions
  - `swarm/w2-citation-schemas` - IF.TTT citation structures
  - `swarm/w2-a6-checklist` - ⚠️ **UNMERGED** complete dossier (90 commits, 56 files)
  - `swarm/w2-a6-ci-workflow` - CI/CD automation (awaiting workflow permissions)

**Critical Issues Identified:**

1. ✅ **RESOLVED: IF.armour.yologuard Benchmark**
   - Final metrics: 111.46% GitHub-parity recall (107/96 detections)
   - Guardian Council: 18/20 approval (90%)
   - Status: **VERIFIED** (see IF-momentum.md)
   - Resolution: Corpus mismatch identified (96 RISK vs 175 total secrets)

2. **BLOCKER: Citation Evidence Tracking Failure**
   - 45/46 citations unreferenced in component index
   - Impact: Credibility of evidence base questioned
   - Required: Complete citation → evidence file mapping

3. **BLOCKER: CI Workflow Deployment**
   - Workflow staged at `docs/ci/review.yml` but not deployed
   - Required: GitHub workflow permissions

4. **CRITICAL: Unmerged Swarm Work**
   - `swarm/w2-a6-checklist` contains 90 commits of complete work (4 days stale)
   - Decision needed: merge or archive
   - Includes complete dossier + validation evidence

**Active Development Streams (Nov 12):**
- Media/streaming infrastructure (WebRTC, SIP, H.323, NDI)
- Session management (parallel sessions, freezing fixes, cloud handover)
- Witness/optimization (CLI enhancements)

**Recommendation for New Sessions:**
1. Check `SESSION-RESUME.md` first (if exists)
2. Review open blockers before starting new work
3. Coordinate with existing Claude branches to avoid conflicts
4. Update `COMPONENT-INDEX.md` when adding new IF.* components

---

## Agent Coordination Model

### IF.optimise Status (Always Visible)

Every agent must display current optimization mode:
- ⚡ **Active** - Using Haiku delegation for mechanical tasks (default)
- 🧠 **Sonnet mode** - Complex reasoning requires direct Sonnet involvement
- 🚀 **Multi-Haiku** - Parallel Haiku agents running
- 💤 **Disabled** - User explicitly requested Sonnet-only mode

### Decision Framework

```
Incoming Task → IF.optimise Evaluation:
├─ Mechanical? (file ops, git, search, transform) → Delegate to Haiku agent
├─ Complex reasoning? (architecture, council debate) → Use Sonnet
├─ Independent parallel tasks? → 🚀 Spawn multiple Haiku in single message
└─ Sequential dependency? → Mixed (Haiku → Sonnet review)
```

**Cost Optimization:**
- Haiku = Sonnet / 10 (cost ratio)
- Target: 50% average token reduction
- Validated: 49.3% reduction (14-day sprint, $45 → $22.80)

---

## Agent Types & Responsibilities

### 1. Sonnet Agents (Expensive, Strategic)

**When to use:**
- Guardian Council deliberations
- Architecture design decisions
- Complex refactoring requiring cross-file understanding
- Final validation and synthesis

**Traceability Requirements:**
- MUST cite IF.ground principles when making epistemological claims
- MUST record Guardian votes with dissent in `/annexes/`
- MUST link decisions to philosophy database when applicable
- MUST generate IF.citation entries for all major decisions

### 2. Haiku Agents (Cheap, Mechanical)

**When to use:**
- File reading and summarization
- Git operations (status, diff, log, commit)
- Simple code transformations
- Data extraction and reformatting
- Test execution and result parsing

**Traceability Requirements:**
- MUST report file hashes (MD5/SHA-256) for all files read
- MUST include git commit IDs for all operations
- MUST timestamp all operations (ISO 8601 format)
- MUST return structured output (JSON/YAML when possible)

### 3. Specialized Agents (Domain-Specific)

**Available Agents:**
- Code-Simplifier: Reduce bloat, dependencies, complexity
- Code-reviewer: Pre-merge review with line references
- Security-Reviewer: Auth, secrets, external inputs, webhooks
- Tech-Lead: Architecture, work shredding, PR sequencing
- Project-Manager: Scoping, acceptance criteria, roadmaps
- Release-Manager-Resume-Specialist: Release cuts, session handoffs

---

## Swarm Orchestration Patterns (Haiku Multi-Agent Framework)

### Overview

InfraFabric implements philosophy-grounded distributed agent communication based on the **Haiku Swarm Test Framework** (see `docs/HAIKU-SWARM-TEST-FRAMEWORK.md`).

### C-UAS Layered Defense Architecture

**Concept:** Counter-Unmanned Aircraft Systems (C-UAS) 4-layer pattern applied to agent coordination:

| Layer | Agent Role | Purpose | Communication Pattern |
|-------|------------|---------|---------------------|
| **1. Detect** | Observer agents | Passive observation | Pub: `if://topic/observations/raw` (BEST_EFFORT) |
| **2. Track** | Tracker agents | Maintain consistency | Sub: observations, Pub: `if://topic/tracks/maintained` (RELIABLE) |
| **3. Identify** | Classifier agents | Verify patterns | Sub: tracks, Pub: `if://topic/classifications/verified` (RELIABLE) |
| **4. Counter** | Effector agents | Execute actions | Sub: classifications, Pub: `if://topic/effects/executed` (PERSISTENT) |

**Coordinator:** 1 agent orchestrates all layers, tracks IF.optimise metrics, generates reports with citations

### Wu Lun (五伦) Relationship Mapping

**Confucian Five Relationships Applied to Agent Roles:**

1. **Ruler → Subject** = Coordinator → Worker
2. **Father → Son** = Senior Agent → Junior Agent
3. **Husband → Wife** = Leader Agent → Support Agent
4. **Elder → Younger** = Experienced → Novice Agent
5. **Friend → Friend** = Peer Agents (equal status)

**Message Routing:** All IFMessages include `wu_lun_relationship` field indicating hierarchical context

**Anti-Pattern Detection:** Workers shouldn't coordinate, coordinators shouldn't observe (violates role boundaries)

### Philosophy Principle Auto-Detection

Every agent message automatically infers which IF.ground principles are being invoked:

```python
def infer_principles(performative, content):
    principles = []

    # Pragmatism (Principle 6): All speech acts
    if performative in ["request", "inform", "agree", "query-if"]:
        principles.append("IF.ground:principle_6_pragmatism_speech_acts")

    # Empiricism (Principle 1): Messages with evidence
    if "evidence" in content and content["evidence"]:
        principles.append("IF.ground:principle_1_observable_artifacts")

    # Verificationism (Principle 2): Content-addressed messages
    if "content_hash" in content:
        principles.append("IF.ground:principle_2_verificationism")

    # Fallibilism (Principle 3): Validation requests
    if performative == "query-if" or "validation_requested" in content:
        principles.append("IF.ground:principle_3_fallibilism")

    # Coherentism (Principle 5): Messages referencing conversation history
    if "in_reply_to" in content or "conversation_id" in content:
        principles.append("IF.ground:principle_5_coherentism")

    # Falsifiability (Principle 7): All signed messages
    if "signature" in content:
        principles.append("IF.ground:principle_7_falsifiability")

    # Stoic Prudence (Principle 8): Retry logic
    if "stoic_resilience" in content:
        principles.append("IF.ground:principle_8_stoic_prudence")

    return principles
```

### IFMessage Schema (Philosophy-Annotated)

```json
{
  "performative": "inform",
  "sender": "if://agent/swarm/worker-1",
  "receiver": "if://agent/coordinator",
  "conversation_id": "if://conversation/mission-2025-11-13",
  "content": {
    "claim": "Task X completed",
    "evidence": ["file.py:123"],
    "cost_tokens": 1247
  },
  "citation_ids": ["if://citation/uuid"],
  "timestamp": 1699632000000000000,
  "sequence_num": 42,
  "content_hash": "sha256:...",
  "signature": {
    "algorithm": "ed25519",
    "public_key": "ed25519:...",
    "signature_bytes": "ed25519:..."
  },
  "philosophy_metadata": {
    "principles_invoked": [
      "IF.ground:principle_1_observable_artifacts",
      "IF.ground:principle_6_pragmatism_speech_acts",
      "IF.ground:principle_7_falsifiability"
    ],
    "wu_lun_relationship": "worker→coordinator",
    "stoic_resilience": "retry_3x_exponential_backoff"
  }
}
```

### Swarm Token Economics (IF.optimise)

**Validated Results (14-day sprint, Nov 10):**
- Total tokens: 2.5M
- Sonnet: 1.2M (48%), Haiku: 1.3M (52%)
- Projected Sonnet-only cost: $45.00
- Actual mixed cost: $22.80
- **Realized savings: 49.3%** (validates 50% claim)

### Swarm Execution Patterns

**Minimal 3-Agent Test:**
```python
# Parallel file summarization (IF.search Pass 1 simulation)
tasks = [
    spawn_agent("worker-1", "Summarizer", "Summarize /papers/IF-vision.md"),
    spawn_agent("worker-2", "Summarizer", "Summarize /papers/IF-foundations.md"),
    spawn_agent("worker-3", "Summarizer", "Summarize /papers/IF-armour.md")
]
results = await asyncio.gather(*tasks)
```

**Production 15-Agent Swarm:**
- Layer 1 (Detect): 5 observers scan codebase
- Layer 2 (Track): 3 trackers maintain consistency
- Layer 3 (Identify): 4 classifiers verify against IF.ground
- Layer 4 (Counter): 3 effectors generate recommendations
- Coordinator: 1 orchestrator with IF.optimise tracking

**Expected Metrics:**
- Total tokens: 80,000-120,000
- Baseline (Sonnet): 250,000 tokens
- Savings: 52-68% (accounting for 26% TTT overhead)
- Citations: 60-80 (15 agents × avg 4-5 findings)
- Philosophy usage: Empiricism (45%), Pragmatism (30%), Coherentism (15%)

---

## Traceability Workflows

### Workflow 1: Research & Documentation

**Pattern:**
```
1. IF.search 8-pass investigation
   ├─ Pass 1-8: Generate citations for each finding
   ├─ Store in /docs/evidence/
   └─ Link to IF.citation service

2. IF.swarm parallelization (optional)
   ├─ Spawn 15 agents across bloom patterns
   ├─ Each agent generates independent citations
   └─ IF.forge synthesizes with conflict resolution

3. Guardian Council review
   ├─ Evaluate citation quality (completeness, verifiability)
   ├─ Vote on approval (record dissent)
   └─ Generate decision citation linking to source citations

4. Final output
   ├─ Research document with inline citation IDs
   ├─ Separate citations file (JSON/YAML)
   └─ Verification checklist
```

### Workflow 2: Code Changes

**Pattern:**
```
1. Read existing code
   ├─ Generate hash of original file
   └─ Citation: "Original state at commit <sha>"

2. Make changes
   ├─ Use Edit tool (preserve line numbers)
   └─ Document rationale in commit message

3. Generate citation
   ├─ Before: file.py:123 (hash: abc123)
   ├─ After: file.py:123 (hash: def456)
   ├─ Rationale: "Implemented Wu Lun weights for relationship detection"
   └─ Guardian approval: Dossier 06, 87% consensus

4. Commit with IF.citation reference
   ├─ Commit message includes citation ID
   └─ Git commit signed (if configured)
```

### Workflow 3: Guardian Council Decisions

**Pattern:**
```
1. Proposal created
   ├─ Define claim (what are we deciding?)
   ├─ Gather evidence (citations to support/oppose)
   └─ Generate proposal citation

2. Guardian deliberation
   ├─ Each guardian cites evidence for their position
   ├─ Contrarian Guardian explicitly seeks disconfirming evidence
   └─ All votes recorded with rationale

3. Decision recorded
   ├─ Status: approved | rejected | deferred
   ├─ Vote tally (e.g., 19/20, Contrarian dissent)
   ├─ Citation graph: decision → evidence → sources
   └─ Dissent preserved (never deleted)

4. Execution (if approved)
   ├─ Implementation citations link back to decision citation
   └─ Post-execution validation (did it work as predicted?)
```

---

## Anti-Patterns (What NOT To Do)

### ❌ Undocumented Claims

**Bad:**
```
"The philosophy database has 12 philosophers."
```

**Good:**
```
"The philosophy database has 12 philosophers (IF-foundations.md:89, verified 2025-11-10)."

Citation:
  claim_id: "if://claim/philosophy-db-count"
  sources: [{"type":"paper","ref":"papers/IF-foundations.md:89","hash":"sha256:493dd69b..."}]
  status: "verified"
```

### ❌ Bypassing Gitignore for Privacy-Sensitive Research

**Bad:**
```
# Force-adding files that should be private
git add -f code/research/IF_ENDORSER_EMAILS*.md
git commit -m "Add endorser emails"
git push

Result: Draft correspondence with researcher names now public on GitHub
```

**Good:**
```
# Respect gitignore patterns for research outputs
git status
# Shows: code/research/IF_ENDORSER_EMAILS_BATCH1.md (ignored)

# Files stay local-only, never committed
ls code/research/IF_ENDORSER_EMAILS*.md  # ✅ Available locally for user
git ls-files | grep ENDORSER_EMAILS       # ✅ Not tracked in git
```

**Why This Matters:**
- Privacy: Publishing draft correspondence violates researcher privacy
- Ethics: Names in your outreach strategy should not be public
- Professional: Draft emails expose your thinking before you've refined it
- Legal: May violate data protection if researchers didn't consent

---

## Session Handoff Protocol

### When Handing Off to Next Session

**Required Artifacts:**
1. **SESSION-RESUME.md** - Current state (<2K tokens)
   - Mission: What we're working on
   - Status: In progress / Blocked / Awaiting decision
   - Branch: Git state, uncommitted changes
   - Citations: Recent decision IDs
   - Updated: ISO 8601 timestamp

2. **Citations Archive**
   - All IF.citation entries generated this session
   - Status updates (unverified → verified)
   - File: `/citations/session-<date>.json`

3. **Evidence Preservation**
   - Guardian Council debates → `/annexes/`
   - Research findings → `/docs/evidence/`
   - Test results → `/code/yologuard/reports/`
   - Git commits with citation references

### When Resuming From Previous Session

**Required Steps:**
1. Read SESSION-RESUME.md ONLY (not full papers)
2. Check COMPONENT-INDEX.md for relevant sections
3. Load recent citations (`/citations/session-<last-date>.json`)
4. Verify git status matches recorded state
5. Continue work with full citation continuity

---

## Quick Reference

**Generate Citation:**
```python
citation = {
    "citation_id": f"if://citation/{uuid4()}",
    "claim_id": "if://claim/doc/section",
    "sources": [
        {"type": "paper", "ref": "path:line", "hash": "sha256:..."}
    ],
    "rationale": "Why this claim is supported",
    "status": "unverified",
    "created_by": "if://agent/name",
    "created_at": datetime.utcnow().isoformat() + "Z",
    "signature": "ed25519:PLACEHOLDER"
}
```

**IF.optimise Status:**
```
⚡ Active | 🧠 Sonnet mode | 🚀 Multi-Haiku | 💤 Disabled
```

**Session Handoff:**
```
1. Update SESSION-RESUME.md
2. Export citations to /citations/session-<date>.json
3. Verify all evidence in /docs/evidence/
4. Commit with citation references
5. Next session reads SESSION-RESUME.md ONLY
```

---

## Validation Checklist

Before completing any major task, verify traceability:

- [ ] All claims have IF.citation entries
- [ ] File hashes (SHA-256) generated for source files
- [ ] Git commits reference citation IDs in messages
- [ ] Guardian Council votes recorded (if applicable)
- [ ] Token costs measured and reported (IF.optimise)
- [ ] Evidence artifacts stored in `/docs/evidence/`
- [ ] SESSION-RESUME.md updated with current state
- [ ] Validation ran: `python tools/citation_validate.py`
- [ ] No broken citation references (`grep -r "if://citation/"`)
- [ ] Status updated (unverified → verified if applicable)

**If any item unchecked:** Task is NOT complete. Generate missing citations before marking done.

---

## Credentials & Access Reference

**Purpose:** Centralized reference for all system credentials and access points.
**Security Note:** This section references credential locations; actual passwords stored in `/home/setup/.claude/CLAUDE.md`

### Local Development

**Gitea Server:**
- URL: `http://localhost:4000/`
- Config: `/home/setup/gitea/custom/conf/app.ini`
- Admin User: `ggq-admin`
- Admin Pass: See `/home/setup/.claude/CLAUDE.md`
- Regular User: `dannystocker`
- Regular Pass: See `/home/setup/.claude/CLAUDE.md`

**WSL System:**
- User: `setup`
- Pass: `setup`

**System Tools:**
- Node.js: v20.19.5
- npm: v10.8.2
- Gemini CLI: v0.11.3

### Project Repositories

**InfraFabric:**
- Local: `/home/setup/infrafabric`
- GitHub: `https://github.com/dannystocker/infrafabric`
- Local Gitea: `http://localhost:4000/dannystocker/infrafabric.git`
- Credentials: Use `dannystocker` Gitea account

**NaviDocs:**
- Local: `/home/setup/navidocs`
- Local Gitea: `http://localhost:4000/ggq-admin/navidocs`
- Credentials: Use `ggq-admin` Gitea account

**ICW (icantwait.ca):**
- Local: `/home/setup/icw_web_2`
- Local Gitea (PRIVATE): `http://localhost:4000/ggq-admin/icw-nextspread`
- Live Site: `https://icantwait.ca`
- ProcessWire Admin: `https://icantwait.ca/nextspread-admin/`
  - User: `icw-admin`
  - Pass: See `/home/setup/.claude/CLAUDE.md`
- Credentials: Use `ggq-admin` Gitea account

**Digital-Lab.ca:**
- Local: `/home/setup/digital-lab.ca`
- Live Path: `/home/setup/public_html/digital-lab.ca`

### StackCP Hosting

**Access:**
- SSH connection for icantwait.ca
- Credentials: See `/home/setup/.claude/CLAUDE.md`

**Paths:**
- icantwait.ca: `/public_html/icantwait.ca`
- digital-lab.ca: `/public_html/digital-lab.ca`

### API Keys & Services

**OpenRouter:**
- Status: **REVOKED** (2025-11-07) - Exposed in GitHub
- Detection: IF.yologuard v3.0 (2025-11-08)
- Whitelist: `/home/setup/.security/revoked-keys-whitelist.md`

**DeepSeek:**
- Key location: See `/home/setup/.claude/CLAUDE.md`
- Status: Active

**Google Cloud:**
- Status: Credentials removed from git history (132 commits rewritten, 2025-11-10)
- Secret scanning: Enabled with test fixture allowlist
- `.env` files: All gitignored (never commit)

### Local Services

**Redis:**
- Port: 6379
- Purpose: BullMQ job queues (NaviDocs background workers)

**Meilisearch:**
- Port: 7700
- Purpose: Search indexing (NaviDocs)
- Auth: See NaviDocs documentation

**Gitea:**
- Port: 4000
- Purpose: Local git server for all repositories

### File Paths Reference

**Windows Paths (via WSL):**
- Downloads: `/mnt/c/users/setup/downloads`
- Screenshots: `/mnt/c/users/setup/pictures/screencaptures/`

**Project Worktrees (NaviDocs):**
- Single tenant: `/home/setup/navidocs-wt-single-tenant`
- TOC polish: `/home/setup/navidocs-wt-toc-polish`
- Image API: `/home/setup/navidocs-img-api`
- Image backend: `/home/setup/navidocs-img-backend`
- Image frontend: `/home/setup/navidocs-img-frontend`
- UI test: `/home/setup/navidocs-ui-test`
- PDF loop: `/home/setup/navidocs-wt-pdf-loop`

**InfraFabric Core (Research Papers):**
- Local: `/home/setup/infrafabric-core`
- GitHub: `https://github.com/dannystocker/infrafabric-core.git`
- Gitea: `http://localhost:4000/dannystocker/infrafabric-core.git`
- Note: Separate repo for research papers vs marketing (infrafabric)

### Security Best Practices

**NEVER commit:**
- `.env` files (always gitignored)
- API keys or tokens
- Passwords or credentials
- Privacy-sensitive data (researcher names, draft emails)

**ALWAYS check before commit:**
```bash
git status                           # Check what's being committed
git diff --cached                    # Review staged changes
grep -r "password\|api_key\|secret" .env 2>&1 | head -5  # Double-check for leaks
```

**IF.armour.yologuard Integration:**
- Runs automatically on commits (if configured)
- Detects 96 RISK secret types
- 111.46% GitHub-parity recall
- Location: `/home/setup/infrafabric/code/yologuard/`

---

## Meta: Updating This Document

**When to update agents.md:**
- New IF.* component requires agent integration
- Citation service API changes (v1.0 → v1.1)
- New agent type added
- Traceability patterns discovered
- Repository state changes (branches, blockers)
- Swarm orchestration patterns evolve
- New critical project added

**Who updates:**
- Any agent that identifies gaps in traceability protocol
- Requires user approval for changes
- Update must include citation to evidence for change

**Last Updated:** 2025-11-13 (restructured with multi-project context, optimized navigation)
**Updated By:** if://agent/claude-sonnet-4.5
**Citation:** if://decision/agents-md-comprehensive-cleanup-2025-11-13

**Sources:**
- GitHub repository comprehensive review (Nov 12-13, 2025)
- `/home/setup/infrafabric/docs/HAIKU-SWARM-TEST-FRAMEWORK.md`
- `/home/setup/infrafabric/papers/InfraFabric.md`
- `/home/setup/infrafabric/papers/IF-momentum.md`
- `/home/setup/navidocs/NAVIDOCS_HANDOVER.md`
- `/home/setup/navidocs/IMPLEMENTATION_SUMMARY.md`
- `/home/setup/.claude/CLAUDE.md`
- Repository branch analysis and git history

---

**Remember:** Traceability is NOT optional. IF.citate and IF.TTT are mandatory for all InfraFabric agent operations.

---

## NaviDocs Cloud Sessions (2025-11-13)

**Status:** ✅ Ready to launch
**Repo:** https://github.com/dannystocker/navidocs
**Summary:** `/home/setup/infrafabric/NAVIDOCS_SESSION_SUMMARY.md`

### Session Architecture
- **5 sequential cloud sessions** (3-5 hours total)
- **Agent identity system:** S1-H01 through S5-H10 (50 Haiku agents total)
- **Budget:** $90 of $100 Claude Code Cloud credit

### Mission
Build sticky boat management app for Riviera Plaisance Euro Voiles:
- **Target:** Prestige + Sunseeker 40-60ft owners (€800K-€1.5M boats)
- **Features:** Inventory tracking, cameras, maintenance, contacts, expenses
- **Pitch:** Include NaviDocs with every boat sale (Sylvain meeting)

### Launch Order (SEQUENTIAL ONLY)
```
S1: Market Research (30-45min) → intelligence/session-1/
S2: Technical Architecture (45-60min) → intelligence/session-2/
S3: UX/Sales Pitch (30-45min) → intelligence/session-3/
S4: Implementation Plan (45-60min) → intelligence/session-4/
S5: Guardian Validation (60-90min) → intelligence/session-5/
```

### Critical Corrections Applied
- ✅ Price: €800K-€1.5M (not €250K-€480K)
- ✅ Brands: Prestige + Sunseeker
- ✅ Agent 1: Joe Trader persona (actual sale price research)
- ✅ Dependencies documented in SESSION_DEBUG_BLOCKERS.md

### Files Created
- `CLOUD_SESSION_1_MARKET_RESEARCH.md` through `CLOUD_SESSION_5_SYNTHESIS_VALIDATION.md`
- `SESSION_DEBUG_BLOCKERS.md` (P0 blockers fixed)
- `intelligence/session-{1,2,3,4,5}/` directories ready

**Next:** Launch Session 1 via Claude Code Cloud web interface (copy-paste full file content)

---

## NaviDocs StackCP S2 Swarm Deployment (2025-11-13)

**Last Updated:** 2025-11-13 09:00 UTC
**Status:** 🟡 Preparation phase IN PROGRESS
**Timeline:** ~5 hours to working demo (presentation deadline when user wakes)
**Strategy:** 5 parallel Haiku agents (prep) → 5 parallel Claude Code CLI agents (development)

**Current Progress:**
- ✅ **Intelligence Complete** - All 5 cloud sessions merged (94 files, 1.5MB, €14.6B market analysis)
- ✅ **Deployment Plan** - STACKCP_S2_SWARM_DEPLOYMENT.md created (5-agent strategy)
- ✅ **Feature Selector** - Deployed to https://digital-lab.ca/navidocs/builder/
- ✅ **Session Handover** - SESSION_HANDOVER_2025-11-13.md created (15KB, comprehensive)
- ✅ **agents.md Update Protocol** - Mandatory update requirements added (this section)
- ✅ **/tmp Persistence Verified** - ext4 filesystem, survives reboots (df -h confirmed)
- 🟡 **Feature Selector Enhancement** - exportAgentTasks() function IN PROGRESS
- ⏳ **Haiku Swarm Deployment** - 5 agents ready to launch in parallel
- ⏳ **StackCP Environment Setup** - npm/npx wrappers, directory structure pending
- ⏳ **NaviDocs Deployment** - Static site deployment to ~/public_html pending

**IF.TTT Citation:**
- Source: User directive 2025-11-13 09:00 UTC + /home/setup/navidocs/SESSION_HANDOVER_2025-11-13.md:1-600
- Verification: `ssh stackcp "df -h /tmp && mount | grep /tmp"` (ext4, rw,relatime)
- Status: verified

### Deployment Architecture (CORRECTED 2025-11-13 09:00 UTC)

**StackCP Environment:**
- **Host:** ssh.gb.stackcp.com (digital-lab.ca account)
- **SSH:** `ssh stackcp` (alias configured in ~/.ssh/config)
- **Home:** /home/sites/7a/c/cb8112d0d1 (user: digital-lab.ca)

**CRITICAL CONSTRAINT (User Correction Applied):**
- ✅ **`/tmp/` IS executable** - For binaries ONLY (node, claude, meilisearch, etc.)
- ✅ **`/tmp/` IS PERSISTENT** - ext4 filesystem, survives reboots, 10-day cleanup for general files
- ✅ **Binaries in /tmp NOT auto-deleted** - Tools persist across reboots
- ❌ **`~/` is noexec** - Code can live here but won't execute
- ✅ **`~/` is persistent** - Standard home directory

**CORRECTED Deployment Pattern:**
- **Executables:** `/tmp/node`, `/tmp/npm`, `/tmp/npx`, `/tmp/claude`, `/tmp/meilisearch`, `/tmp/python*`
- **Application code:** `~/navidocs-app/` (NOT /tmp/navidocs/) - Node.js app lives here
- **Website static files:** `~/public_html/digital-lab.ca/navidocs/` - Apache serves from here
- **Persistent data:** `~/navidocs-data/{db,uploads,logs}` - SQLite, uploads, logs
- **Configuration:** `~/navidocs-app/.env` - Environment variables

**Previous Plan (WRONG):**
- ❌ Code in `/tmp/navidocs/` ← This was incorrect
- ❌ Static site also in `/tmp/` ← This was incorrect

**Corrected Plan (VERIFIED):**
- ✅ Executables: `/tmp/` (node, npm, npx, claude, etc.)
- ✅ Application: `~/navidocs-app/` (cloned repo, npm install here)
- ✅ Website: `~/public_html/digital-lab.ca/navidocs/` (Apache document root)
- ✅ Data: `~/navidocs-data/` (SQLite DB, uploads, logs)

**Verification Commands:**
```bash
# Confirm /tmp persistence
ssh stackcp "df -h /tmp && mount | grep /tmp"
# Output: ext4 filesystem, rw,relatime (NOT tmpfs)

# Check existing binaries
ssh stackcp "ls -lh /tmp/{claude,node,npm,meilisearch}"
# All present and executable

# Check web directory
ssh stackcp "ls -la ~/public_html/digital-lab.ca/navidocs/"
# builder/ directory exists, index.html present
```

**Directory Structure (CORRECTED 2025-11-13 09:00 UTC):**
```
/tmp/                                  # Executables ONLY (persistent ext4)
├── claude                             # Claude Code CLI (v2.0.28)
├── node                               # Node.js symlink (v20.18.0)
├── npm                                # npm wrapper script
├── npx                                # npx wrapper script
├── meilisearch                        # Meilisearch binary (v1.6.2)
├── python-headless-3.12.6-linux-x86_64/  # Python installation
└── node-v20.18.0-linux-x64/           # Node.js installation directory

~/navidocs-app/                        # Application code (noexec OK)
├── server/                            # Backend (Express.js + SQLite)
├── client/                            # Frontend (Vue 3)
├── package.json                       # Dependencies
├── node_modules/                      # Installed packages
└── .env                               # Configuration

~/navidocs-data/                       # Persistent data (noexec OK)
├── db/navidocs.db                     # SQLite database
├── uploads/                           # Permanent uploads
└── logs/                              # Application logs

~/public_html/digital-lab.ca/navidocs/  # Static website (Apache serves)
├── builder/                           # Feature selector tool ✅ DEPLOYED
│   └── index.html                     # Interactive feature selection
├── dist/                              # Production build (when deployed)
│   ├── assets/                        # CSS, JS, images
│   └── index.html                     # Main entry point
├── index.html                         # ✅ Current placeholder
├── styles.css                         # ✅ Current styles
└── script.js                          # ✅ Current script
```

**Backup/Restore Strategy (User Request 2025-11-13 09:00 UTC):**

Since /tmp is persistent but has 10-day cleanup policy for general files:

**Backup Executables (Preventive):**
```bash
# Backup /tmp binaries to home directory
ssh stackcp "mkdir -p ~/backups/tmp-binaries"
ssh stackcp "cp /tmp/{claude,node,npm,npx,meilisearch} ~/backups/tmp-binaries/"
ssh stackcp "cp -r /tmp/node-v20.18.0-linux-x64 ~/backups/tmp-binaries/"
ssh stackcp "cp -r /tmp/python-headless-3.12.6-linux-x86_64 ~/backups/tmp-binaries/"
```

**Restore Executables (If Needed):**
```bash
# Restore from backup
ssh stackcp "cp ~/backups/tmp-binaries/* /tmp/"
ssh stackcp "chmod +x /tmp/{claude,node,npm,npx,meilisearch}"
ssh stackcp "cp -r ~/backups/tmp-binaries/node-v20.18.0-linux-x64 /tmp/"
ssh stackcp "cp -r ~/backups/tmp-binaries/python-headless-3.12.6-linux-x86_64 /tmp/"
```

**Automated Backup Script (Recommended):**
```bash
# Create on StackCP: ~/bin/backup-tmp-binaries.sh
ssh stackcp "mkdir -p ~/bin"
ssh stackcp "cat > ~/bin/backup-tmp-binaries.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups/tmp-binaries-\$(date +%Y%m%d)
mkdir -p \$BACKUP_DIR
cp /tmp/{claude,node,npm,npx,meilisearch} \$BACKUP_DIR/ 2>/dev/null
cp -r /tmp/node-v20.18.0-linux-x64 \$BACKUP_DIR/ 2>/dev/null
cp -r /tmp/python-headless-3.12.6-linux-x86_64 \$BACKUP_DIR/ 2>/dev/null
echo \"\$(date): Backup complete to \$BACKUP_DIR\" >> ~/backup.log
EOF"
ssh stackcp "chmod +x ~/bin/backup-tmp-binaries.sh"

# Run weekly (manual until StackCP cron configured)
ssh stackcp "~/bin/backup-tmp-binaries.sh"
```

### 5-Agent Strategy (S2 Swarm Pattern)

**Agent 1: Backend Developer (S2-BACKEND)**
- **tmux session:** `backend-dev`
- **Tasks:** Database setup, Core API endpoints, Background worker, Testing
- **Duration:** 2 hours
- **Priority:** P0 - All other agents depend on API availability

**Agent 2: Frontend Developer (S2-FRONTEND)**
- **tmux session:** `frontend-dev`
- **Tasks:** Core UI components, Navigation & Layout, Build & Deploy, Testing
- **Duration:** 2 hours
- **Dependencies:** Agent 1 API endpoints

**Agent 3: OCR Integration Specialist (S2-OCR)**
- **tmux session:** `ocr-dev`
- **Tasks:** Claude Code CLI OCR, Google Vision fallback, Hybrid strategy, Testing
- **Duration:** 1.5 hours
- **Innovation:** Use `/tmp/claude` for intelligent document analysis (context understanding)

**Agent 4: Infrastructure & DevOps (S2-INFRA)**
- **tmux session:** `infra`
- **Tasks:** Environment config, Process management, Apache reverse proxy, Monitoring
- **Duration:** 1 hour
- **Critical:** Sets up Redis Cloud, Meilisearch, Node.js environment

**Agent 5: QA & Integration Testing (S2-QA)**
- **tmux session:** `qa`
- **Tasks:** E2E test suite, Demo data preparation, Performance testing, Bug fixing
- **Duration:** 1 hour
- **Final Responsibility:** Sign off on presentation-ready demo

### Coordination Protocol

**Task Assignment via Feature Selector:**
- **Tool:** `~/public_html/digital-lab.ca/navidocs/builder/index.html`
- **Polling:** Agents read `/tmp/navidocs/agent-tasks.json` every 5 minutes
- **Format:**
```json
{
  "session_id": "s2-swarm-2025-11-13",
  "updated_at": "2025-11-13T10:00:00Z",
  "features_selected": [
    {
      "id": "inventory-tracking",
      "title": "Photo-Based Inventory Tracking",
      "priority": "CRITICAL",
      "assigned_to": ["S2-BACKEND", "S2-FRONTEND", "S2-OCR"],
      "notes": "Must support bulk photo upload",
      "must_have": 10
    }
  ],
  "agent_tasks": {
    "S2-BACKEND": [
      "Create DB tables: inventory_items, equipment_photos",
      "POST /api/inventory/upload (multi-part)",
      "GET /api/inventory/:boat_id"
    ],
    "S2-FRONTEND": [
      "Photo grid component with drag-drop",
      "Inventory list view with filters"
    ],
    "S2-OCR": [
      "Extract equipment names from photos",
      "Link OCR results to inventory items"
    ]
  }
}
```

### Agent Coordination Rules

**Communication Pattern:**
- **Coordination file:** `/tmp/navidocs/coordination.json`
- **Update frequency:** Every 15 minutes
- **Format:**
```json
{
  "S2-BACKEND": {
    "status": "in_progress",
    "progress": "3/5 tasks complete",
    "blocked_on": null,
    "api_endpoints_ready": ["/api/auth/login", "/api/boats"]
  },
  "S2-FRONTEND": {
    "status": "blocked",
    "progress": "0/4 tasks complete",
    "blocked_on": "Waiting for Agent 1 API endpoints",
    "eta_unblock": "10 minutes"
  }
}
```

**Anti-Pattern Detection:**
- Workers don't coordinate directly (violates Wu Lun hierarchy)
- All coordination via shared coordination.json (pub/sub pattern)
- Human checks coordination.json every 30 minutes

### Tech Stack (StackCP Deployment)

**Backend:**
- Node.js 20.18.0 (`/tmp/node`)
- Express.js
- SQLite (better-sqlite3) at `~/navidocs-data/db/navidocs.db`
- BullMQ + Redis Cloud (free 30MB tier)

**Frontend:**
- Vue 3 + Vite
- Design System: Ocean Deep #003D5C, Wave Blue #0066CC, Sand Beige #F5F1E8
- Inter font family

**Search:**
- Meilisearch (`/tmp/meilisearch` already running on localhost:7700)

**OCR:**
- Primary: Claude Code CLI (`/tmp/claude`) for intelligent analysis
- Fallback: Google Vision API (@google-cloud/vision) for handwriting

**Process Management:**
- tmux sessions (persistent across SSH disconnects)
- Apache reverse proxy (StackCP managed)

### Deployment Sequence

**Phase 1: Setup (30 minutes)**
```bash
ssh stackcp
cd /tmp && git clone https://github.com/dannystocker/navidocs.git
cd navidocs && npm install
mkdir -p ~/navidocs-data/{db,uploads,logs}
```

**Phase 2: Launch Agents (5 parallel tmux sessions)**
```bash
tmux new -s backend-dev -d "/tmp/claude --prompt 'Agent 1 (S2-BACKEND) prompt...'"
tmux new -s frontend-dev -d "/tmp/claude --prompt 'Agent 2 (S2-FRONTEND) prompt...'"
tmux new -s ocr-dev -d "/tmp/claude --prompt 'Agent 3 (S2-OCR) prompt...'"
tmux new -s infra -d "/tmp/claude --prompt 'Agent 4 (S2-INFRA) prompt...'"
tmux new -s qa -d "/tmp/claude --prompt 'Agent 5 (S2-QA) prompt...'"
```

**Phase 3: Development (3 hours)**
- Agents work in parallel, update coordination.json
- Human monitors progress every 30 minutes
- Download binaries to `/tmp/` if dependencies missing

**Phase 4: Testing (1 hour)**
- Agent 5 (QA) runs E2E tests
- Demo data preparation (sample boat with documents)
- Bug fixes as needed

**Phase 5: Presentation Prep (1 hour)**
- Final polish
- Rehearsal with demo data
- Backup plan if features incomplete

### Critical Files

**Deployment Plan:**
- `~/NAVIDOCS_DEPLOYMENT_PLAN.md` (full 5-agent strategy on StackCP)
- `/home/setup/navidocs/STACKCP_S2_SWARM_DEPLOYMENT.md` (local copy)

**Feature Selector:**
- `~/public_html/digital-lab.ca/navidocs/builder/index.html`
- Accessible: https://digital-lab.ca/navidocs/builder/
- **Enhancement:** Auto-generates `/tmp/navidocs/agent-tasks.json` for agent polling

**Intelligence Outputs:**
- `/home/setup/navidocs/NAVIDOCS_COMPLETE_INTELLIGENCE_DOSSIER.md` (all 5 sessions merged)
- `/home/setup/navidocs/intelligence/session-{1,2,3,4,5}/` (94 files, ~1.5MB)

### IF.TTT Traceability

**Decision Citation:**
```json
{
  "citation_id": "if://decision/navidocs-stackcp-s2-deployment",
  "claim": "5 parallel Claude Code CLI agents can deliver working demo in 5 hours",
  "sources": [
    {"type": "file", "path": "intelligence/session-2/session-2-architecture.md"},
    {"type": "file", "path": "STACKCP_README.md"},
    {"type": "doc", "url": "docs/HAIKU-SWARM-TEST-FRAMEWORK.md"}
  ],
  "rationale": "S2 swarm pattern validated in InfraFabric; StackCP constraints require /tmp strategy",
  "status": "verified",
  "created_by": "if://agent/claude-sonnet-4.5",
  "created_at": "2025-11-13T08:00:00Z"
}
```

**Next Steps:**
1. ✅ Deployment plan complete
2. 🟡 Update agents.md (this section)
3. ⏳ Deploy codebase to `/tmp/navidocs/` on StackCP
4. ⏳ Launch 5 parallel Claude Code CLI agents
5. ⏳ Execute 3-hour development phase

