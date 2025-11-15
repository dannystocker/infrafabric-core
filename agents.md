# InfraFabric Agent Architecture

**Purpose:** Define agent behavior patterns, traceability requirements, and coordination protocols for InfraFabric work AND all other projects.

**Audience:** All Claude instances working on InfraFabric, NaviDocs, GGQ-CRM, ICW, Digital-Lab, Job-Hunt, and StackCP projects.

**Last Updated:** 2025-11-14 (Post-mortem: 8-session $400 analysis + GGQ Calendar CRM migration)

---

## 🚨 CRITICAL LESSON: $400 Session Post-Mortem (2025-11-14)

**What Happened:**
- 8 concurrent console sessions across 4 hours
- ~$400 Claude tokens spent (90% from single session: if0-console)
- 213 tool invocations with massive context reloading (15K-30K tokens each)
- 30 Haiku agents deployed for API research
- Sonnet used for mechanical file operations (should have been Haiku)

**Work Output:**
- 150,000+ lines total (73% AI-reformatted API docs, only 3-5% actual production code)
- Should have cost $60-100, not $400 (4-6× premium paid)

**Root Cause:**
1. **Wrong model for wrong task** - Sonnet doing file operations instead of Haiku
2. **Massive context reloading** - 213 tool calls × 20K context = wasted tokens
3. **API documentation generation** - Not production code, low value per dollar

**Critical Blocker Found:**
- **navidocs4-console:** 8 commits unpushed (4,238 lines at risk)
- **Error:** `Failed to connect to 127.0.0.1 port 59238` (push failed)
- **Recovery:** User must push from that session immediately

**Lesson Learned:**
✅ **USE HAIKU FOR LABOR** - File updates, data transformations, API research (10× cheaper)
✅ **USE SONNET FOR REASONING** - Architecture decisions, council debates, complex planning
✅ **AVOID CONTEXT RELOADING** - Batch operations, use Edit tool instead of Read+Write loops
✅ **VALIDATE OUTPUT VALUE** - Reformatted docs ≠ production code

**New Strategy (Validated by Post-Mortem):**
- NaviDocs S² plan: 30 Haiku + 1 Sonnet coordinator = $12-18 budget ✅ CORRECT APPROACH
- Single-session build: 15 Haiku agents only = $8-12 budget ✅ EVEN BETTER (simpler)

**Files:**
- Post-mortem analysis: `/mnt/c/Users/Setup/Downloads/post-mortum/*.txt` (8 console logs)
- Recovery prompts: Generated per-session instructions (not committed)
- New build prompt: `/home/setup/navidocs/NAVIDOCS_SINGLE_SESSION_BUILD.md` ✅

**Status:** User shifted strategy from complex S² (4 missions, 31 agents) to simplified single-session (15 Haiku agents). All NaviDocs research complete, just need to BUILD.

**Citation:** if://decision/navidocs-single-session-2025-11-14

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
  "created_at": "2025-11-10T00:00:00Z",
  "signature": "ed25519:..."
}
```

**Tools:**
- Validate: `tools/citation_validate.py`
- Schema: `schemas/citation/v1.0.schema.json`
- Example: `citations/examples/citation_example.json`

---

## Component Naming Conventions (CURRENT STANDARD)

**Effective:** 2025-11-10 (going forward)
**Status:** Active naming standard for all new work

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

**Rationale (IF.ground - Fallibilism):**
> "Preserve historical context. Changing past documents creates confusion and breaks traceable lineage.
> Establish naming convention for future work while honoring how discussions actually happened."

### Other Component Aliases

**IF.ceo** = **IF.sam** (both refer to 16 Sam Altman facets)
**IF.citation** = **IF.citate** (both refer to citation infrastructure)
**IF.forge** = **IF.marl** (both refer to Multi-Agent Reflexion Loop)

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
- Measured: 87-90% reduction for mechanical tasks

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

**Example:**
```
Decision: Expand philosophy database to 18 philosophers
Citation: if://decision/philosophy-expansion-2025-11-09
Sources:
  - /evidence/philosophy_database_evaluation_2025-11-09.md
  - IF-foundations.md:89-140 (philosophy database definition)
Rationale: Evaluate marginal utility of adding 6 philosophers
Result: HOLD at 12 philosophers (90% simplification already achieved)
Status: verified
Created_by: if://agent/claude-sonnet-4.5
```

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

**Example:**
```
Task: Summarize IF-vision.md
Output:
  summary: "[400 word summary]"
  source: "papers/IF-vision.md"
  hash: "1f9a453a11c3728138ad883d89086edb"
  lines_read: 850
  last_modified: "2025-11-09"
  agent: "if://agent/haiku-4.5-summarizer"
```

### 3. Specialized Agents (Domain-Specific)

**Available Agents:**
- Code-Simplifier: Reduce bloat, dependencies, complexity
- Code-reviewer: Pre-merge review with line references
- Security-Reviewer: Auth, secrets, external inputs, webhooks
- Tech-Lead: Architecture, work shredding, PR sequencing
- Project-Manager: Scoping, acceptance criteria, roadmaps
- Release-Manager-Resume-Specialist: Release cuts, session handoffs

**Traceability Requirements:**
- MUST generate domain-specific evidence artifacts
- MUST link to relevant IF.ground principles
- MUST preserve audit trail in `/docs/evidence/`
- MUST flag high-risk changes for Guardian review

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

**Traceability Artifacts:**
- `/docs/evidence/<research-topic>-<date>.md` - Research findings
- `/citations/<research-topic>-<date>.json` - Citation database
- `/annexes/<dossier-number>.md` - Guardian Council debate

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

**Traceability Artifacts:**
- Git commit with citation in message
- `/citations/code-changes-<date>.json`
- Optional: `/docs/evidence/code-review-<date>.md`

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

**Traceability Artifacts:**
- `/annexes/ANNEX-<letter>-<topic>.md` - Full debate transcript
- `/schemas/decision/v1.0.schema.json` - Decision citation
- `/docs/evidence/guardian-verdict-<date>.md` - Executive summary

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

### ❌ Unverifiable Architecture Decisions

**Bad:**
```
User: Should we expand the philosophy database?
Agent: Yes, we should add 6 more philosophers.
[No citation, no Guardian vote, no rationale]
```

**Good:**
```
User: Should we expand the philosophy database?
Agent: Let me evaluate this with IF.guard protocol.

1. Spawn Haiku agent to analyze marginal utility
2. Generate evidence document with citations
3. Present to Guardian Council for deliberation
4. Record decision with dissent preserved

Result: HOLD at 12 philosophers (Dossier evaluation, 2025-11-09)
Citation: /evidence/philosophy_database_evaluation_2025-11-09.md
```

### ❌ Silent Failures

**Bad:**
```
[Test fails, agent doesn't report it, marks task as complete]
```

**Good:**
```
Test failed (3/10 passing).

Citation:
  claim_id: "if://test-run/yologuard-v3-2025-11-10"
  sources: [{"type":"code","ref":"tests/test_corpus.py:45","hash":"sha256:..."}]
  status: "disputed"
  rationale: "Regression in Wu Lun weight calibration"
  created_by: "if://agent/haiku-test-runner"

Action: Mark task as IN_PROGRESS (not completed), create blocker citation.
```

### ❌ Opaque Token Costs

**Bad:**
```
[Uses Sonnet to read 6 papers directly, consumes 50K tokens, doesn't report cost]
```

**Good:**
```
⚡ IF.optimise Active
Task: Understand InfraFabric papers
Strategy: 🚀 Spawn 4 Haiku agents to summarize papers in parallel

Cost Analysis:
- Direct reading: 50,000 tokens @ Sonnet pricing
- Haiku delegation: 5,000 tokens @ Haiku pricing (10× savings)

Traceability:
- Each Haiku agent reports source file hash
- Summaries stored in /docs/evidence/paper-summaries-2025-11-10.json
- Token costs logged in IF.optimise report
```

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

**Traceability Validation:**
```bash
# Verify all citations are valid
python tools/citation_validate.py citations/session-2025-11-10.json

# Check for broken references
grep -r "if://citation/" docs/ | while read ref; do
  # Verify citation exists and hash matches
done

# Audit trail completeness
git log --grep="if://citation/" --oneline | wc -l
```

---

## Integration Points

### IF.armour.yologuard (Secret Detection)
**Current Name:** IF.armour.yologuard | **Historical Alias:** IF.yologuard

- Emit citation IDs alongside manifests (`--manifest`)
- Provenance fields at `code/yologuard/src/IF.yologuard_v3.py:1210`
- Link secret detections to Wu Lun principle citations
- **Primary Metric:** 107/96 (111.46% GitHub-parity recall), 100% precision
- **Status:** VERIFIED (Guardian Council 18/20 approval, 2025-11-10)

### IF.guard
- Decisions include `citation_ids` array (optional)
- Schema: `schemas/decision/v1.0.schema.json`
- Links Guardian votes to supporting evidence

### IF.search
- Each of 8 passes generates citations
- Pass 8 (Monitor) includes warrant canary citations
- IF.swarm parallelization preserves per-agent citations

### IF.forge
- Multi-Agent Reflexion Loop citations at each stage
- Stage 3 (External Validator) must cite cross-model sources
- Stage 7 (Final Validation) links to Guardian decision citations

### IF.witness
- Meta-validation citations prove validation occurred
- Gemini recursive validation: cite external review documents
- GPT-5 MARL: cite 8 architectural improvements proposed

---

## Citation Service Roadmap

**Current (v1.0):**
- JSON schema validation
- Manual citation creation
- File-based storage

**Planned (v1.1 - IF.citation Service):**
- REST API: POST /v1/citations, GET /v1/citations/{id}
- Verification endpoint: POST /v1/citations/{id}/verify
- Revocation endpoint: POST /v1/citations/{id}/revoke
- Content-addressed artifacts (SHA-256)
- Optional IPFS/S3 pointers
- Graph-friendly lineage (claim → sources → decisions)

**Future (v2.0):**
- Auto-verifier job (check source hashes, update status)
- Decision UI (show linked citations in web interface)
- Merkle tree append-only log (EU AI Act Article 10 compliance)
- Cryptographic signatures (ed25519)
- Cross-repository citation resolution

---

## Compliance & Standards

### EU AI Act Article 10 (Traceability Requirements)

InfraFabric agents comply with EU AI Act traceability mandates:
- **Article 10.2(a):** All decisions traceable to data/logic via IF.citation
- **Article 10.2(b):** Audit logs preserved (Merkle tree append-only)
- **Article 10.2(c):** Human oversight supported (Guardian Council votes)
- **Article 10.2(d):** Provenance chains cryptographically verifiable

**Implementation:**
- IF.trace: Merkle tree audit trail
- IF.citation: Provenance graph with signatures
- IF.guard: Human-in-the-loop governance
- IF.witness: Third-party validation with citations

### IF.ground Epistemological Standards

Every agent operation maps to IF.ground principles:
1. **Ground in Observable Artifacts** → Every claim has file:line citation
2. **Validate with Toolchain** → Test results cited, hashes verified
3. **Make Unknowns Explicit** → Status: unverified (not hidden)
4. **Schema-Tolerant Parsing** → Citations support multiple source types
5. **Gate Client-Only Features** → Citations link to capability evidence
6. **Progressive Enhancement** → Citations added iteratively (unverified → verified)
7. **Reversible Switches** → Citations can be revoked with rationale
8. **Observability Without Fragility** → Warrant canaries detect missing citations

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

**Validate Citation:**
```bash
python tools/citation_validate.py citations/my-citation.json
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

## Cloud Environment Instructions (Claude Code Web)

**For Claude instances running in Claude Code Web with GitHub integration:**

### Initial Setup (First Cloud Session)

**Step 1: Clone and Verify**
```bash
# Repository will be auto-cloned by Claude Code Web
cd infrafabric
git status                               # Verify clean state
git log --oneline -5                     # Check latest commits
ls .env 2>&1 | grep "No such file"       # Verify .env absent (gitignored)
```

**Step 2: Read Session Handover**
```
Read SESSION-HANDOVER-TO-CLOUD.md FIRST
- Contains current mission (yologuard benchmark fix)
- Token budget ($1000 with Haiku/Sonnet strategy)
- Three paths forward (verify → fix → document)
- Security reminders
```

**Step 3: Adopt Agent Protocol**
```
Read THIS FILE (agents.md) and:
1. Understand IF.TTT framework (Traceable, Transparent, Trustworthy)
2. Note IF.optimise default behavior (Haiku delegation)
3. Learn citation generation pattern
4. Review anti-patterns to avoid
5. Commit to traceability checklist
```

**Step 4: Display IF.optimise Status**
```
Always show current mode in responses:
⚡ Active       - Haiku delegation for mechanical tasks (default)
🧠 Sonnet mode  - Complex reasoning (architecture, council)
🚀 Multi-Haiku  - Parallel agents running
💤 Disabled     - Sonnet-only (user requested)
```

### Cloud-Specific Traceability

**Token Cost Tracking (MANDATORY):**
- Report Haiku vs Sonnet token ratio after first major task
- Track cost per task
- Alert if burning budget too fast (>$100/day for setup work)
- Target: 50-80% Haiku delegation

**Git Operations:**
```bash
# Before commits
git status                               # Always check first

# Commits MUST include citations
git commit -m "Fix yologuard benchmark

- Created canonical benchmark script
- Documented usable-only filtering
- Explained 96 vs 175 corpus discrepancy

Citation: if://fix/yologuard-benchmark-2025-11-10

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push origin master
```

**Session Boundaries:**
- Update SESSION-RESUME.md after each major task
- Export citations to /citations/session-<date>.json
- Commit progress frequently (don't lose work)
- Use TodoWrite tool to track multi-step tasks

### Security Protocol (CRITICAL)

**NEVER in cloud environment:**
- ❌ Create .env file
- ❌ Commit credentials
- ❌ Store API keys
- ❌ Push sensitive data

**Safe operations:**
- ✅ Read code and documentation from GitHub
- ✅ Modify papers with verified metrics
- ✅ Create test scripts (no real credentials)
- ✅ Update documentation

**Test Data (Safe):**
- code/yologuard/benchmarks/leaky-repo/** (public benchmark corpus)
- Allowlisted in .github/secret_scanning.yml
- GitHub may flag - these are false positives

### Haiku Agent Spawning (Cloud)

**Pattern for parallel work:**
```
Spawn 3 Haiku agents in parallel (single message with multiple Task calls):

Agent 1: Read papers/IF-armour.md yologuard section, report claimed metrics
Agent 2: Read docs/GUARDED-CLAIMS.md Claim 1, report verification status
Agent 3: Read code/yologuard/benchmarks/run_leaky_repo_test.py, report test corpus size

Then (Sonnet): Analyze discrepancies between claims and actual test results
```

**Cost estimate:**
- 3 Haiku agents: ~1,500 tokens each = 4,500 Haiku tokens
- Sonnet analysis: ~2,000 Sonnet tokens
- Total cost: ~$0.03-0.06 (vs $0.15-0.30 Sonnet-only)

### IF.ground Compliance in Cloud

Every cloud operation must map to principles:

**Principle 1 (Empiricism):**
- Verify claims against actual files (don't trust SESSION-RESUME.md blindly)
- Run benchmarks yourself (don't cite unverified metrics)

**Principle 2 (Verificationism):**
- Generate file hashes for all sources cited
- Include verification commands in documentation

**Principle 3 (Fallibilism):**
- Mark claims as "unverified" until independently tested
- Preserve Gemini's contradicting evidence (don't delete)

**Principle 7 (Falsifiability):**
- Include testable predictions in commit messages
- Document how to reproduce results

### Cloud Session Checklist

Before ending each cloud session:

- [ ] SESSION-RESUME.md updated with current state
- [ ] Token costs tracked (Haiku vs Sonnet ratio calculated)
- [ ] All changes committed to git
- [ ] All changes pushed to GitHub
- [ ] Citations exported to /citations/session-<date>.json
- [ ] IF.optimise status indicator shown in last message
- [ ] Next session path clearly specified
- [ ] No sensitive data left in workspace

---

## 2025-11-11: Philosophy Database r4 Upgrade

**Citation:** if://citation/gpt5pro-fixpack-r4-2025-11-11
**Commit:** 73e52a4
**Source:** InfraFabric_FixPack_2025-11-11_r4_gapfill.zip (SHA-256: 46c69ff...)

### What Changed

**Philosophy Database:**
- **Before r4:** 16 core philosophers (75% Western), no tensions, no historical lineage
- **After r4:** 26 philosophers (54% Western), embedded tensions_with, historical_context for all
- **Architecture:** Embedded structure (tensions/lineage in YAML) vs. separate documentation files
- **Joe Coulombe:** Now has historical_context (influenced_by: A&P, 7-Eleven anti-model)

**New Documentation:**
- `docs/PHILOSOPHY-CODE-EXAMPLES.md` (125 lines): 7 philosophy→code mappings
- `docs/evidence/gemini-logs/core/IF.philosophy-database-r4.yaml` (955 lines): Core philosophers
- `docs/evidence/gemini-logs/core/PATCH-IF.philosophy-database.additions.yaml` (292 lines): 9 new traditions

**New Philosophical Traditions Added:**
1. **Islamic:** Al-Ghazali (Occasionalism), Avicenna (Essence/existence), Averroes (Faith/reason harmony)
2. **African:** Ubuntu (Personhood through community)
3. **Indigenous:** Relational epistemology (Knowledge in relationships)
4. **Phenomenology:** Husserl/Heidegger/Merleau-Ponty (Epoché, being-in-world)
5. **Critical Theory:** Frankfurt School/Habermas (Ideology critique)
6. **Process:** Whitehead/Bergson (Events over substances)
7. **Feminist Epistemology:** Haraway/Harding (Situated knowledges)
8. **Postmodernism:** Foucault/Derrida/Deleuze (Power/knowledge)
9. **Tech Philosophy:** Simondon/Stiegler/Yuk Hui (Individuation, cosmotechnics)

### Impact on Agent Behavior

**IF.search Agents:**
- Can now reference 7 concrete code examples (docs/PHILOSOPHY-CODE-EXAMPLES.md)
- Joe persona has explicit historical grounding (A&P, 7-Eleven influences)
- Cross-cultural breadth: 54% Western, 46% non-Western (was 75%/25%)

**IF.guard Agents:**
- Tension resolution strategies documented (e.g., Al-Ghazali ↔ Avicenna on causality)
- Ubuntu consensus now has Python implementation example (`approve()` function)
- All 26 philosophers available for council deliberations

**IF.persona Agents:**
- Joe Coulombe historical_context: influenced_by [A&P, 7-Eleven (anti-model)]
- Joe influenced: [Modern private-label retail]
- Additional_readings: Becoming Trader Joe (2021), Acquired Podcast (2025)

**IF.witness Agents:**
- Process philosophy (Whitehead/Bergson) now has YAML event log example
- Append-only, Ed25519-signed event schema documented

**IF.citation Agents:**
- Indigenous relationality mapped to rhizomatic citation CSV (multi-source coherence)
- Non-hierarchical evidence graphs now have philosophical grounding

### Code Examples (Philosophy → Implementation)

All agents should reference `docs/PHILOSOPHY-CODE-EXAMPLES.md` when implementing IF principles:

1. **Verificationism → CI Toolchain Gate** (Vienna Circle → ifctl.py + GitHub Actions)
2. **Falsifiability → One-Line Rollback** (Popper → feature flags in TypeScript)
3. **Schema Tolerance → Multi-variant Parse** (Duhem-Quine → TypeScript union types)
4. **Ubuntu Consensus → Guard Gating** (African Philosophy → Python council voting)
5. **Process Philosophy → Event Witness Log** (Whitehead/Bergson → YAML append-only events)
6. **Indigenous Relationality → Rhizomatic Citations** (Non-hierarchical → multi-source CSV)
7. **Joe's Heuristics → Search Pass Filters** (Trader Joe's → YAML differentiation filters)

### Linter Updates

**ifctl.py validation:**
- Now validates 19 checks (was 17 in r3)
- Added: 2 additional philosopher validations
- Status: 19/19 OK, 0 failures (commit 73e52a4)

### Next Steps for Agents

**Recommended agent behaviors going forward:**

1. **When making IF.guard decisions:** Cite tension resolution strategies from philosophy database
   - Example: "Using Al-Ghazali ↔ Avicenna resolution: empirical adjudication via falsifiers"

2. **When implementing IF principles:** Link to PHILOSOPHY-CODE-EXAMPLES.md
   - Example: "Implementing Principle 7 (Reversibility) using Popper's pattern (docs/PHILOSOPHY-CODE-EXAMPLES.md:30-45)"

3. **When executing IF.search passes:** Apply Joe's differentiation-filter
   - Check: Does this evidence provide unique value vs. peers? If not, drop it.
   - Use: Joe's heuristic "private-label-only-when-better" for source selection

4. **When generating citations:** Reference historical lineage
   - Example: "Joe Coulombe's constraint-driven curation (influenced_by: A&P, 7-Eleven anti-model)"

5. **When spawning swarm agents:** Distribute across cultural traditions
   - Instead of: "Spawn 8 agents"
   - Better: "Spawn 8 agents (2 Islamic, 2 Indigenous, 2 Process, 2 Western)"

### Validation Commands

**Check philosophy database:**
```bash
python tools/ifctl.py lint
# Expected: 19/19 OK checks
```

**View code examples:**
```bash
cat docs/PHILOSOPHY-CODE-EXAMPLES.md | grep "^##"
# Shows 7 philosophy→code mappings
```

**Check tensions:**
```bash
grep -A3 "tensions_with" docs/evidence/gemini-logs/core/PATCH-IF.philosophy-database.additions.yaml
# Shows cross-cultural dialectics
```

---

## Meta: Updating This Document

**When to update agents.md:**
- New IF.* component requires agent integration
- Citation service API changes (v1.0 → v1.1)
- New agent type added
- Traceability patterns discovered
- Philosophy database updates (r3 → r4 upgrades)

**Who updates:**
- Any agent that identifies gaps in traceability protocol
- Requires user approval for changes
- Update must include citation to evidence for change

**Update History:**
- **2025-11-14:** Added GGQ-CRM project context and calendar migration strategy
- **2025-11-11:** Philosophy Database r4 upgrade (26 philosophers, tensions, lineage, code examples) - Commit 73e52a4
- **2025-11-10:** Initial creation for IF.TTT integration - Commit 44a365b

**Last Updated:** 2025-11-14
**Updated By:** if://agent/claude-sonnet-4.5
**Citation:** if://decision/agents-md-update-ggq-2025-11-14

---

## 🆕 GGQ-CRM Project (Added 2025-11-14)

### Project Overview
**Location:** `/home/setup/ggq-crm`
**GitHub:** https://github.com/dannystocker/ggq-crm
**Purpose:** CRM data enrichment and Google Calendar → SuiteCRM migration for Les Guides GQ (Quebec LGBT tourism guide)

### Current Status (Updated 2025-11-15)
- ✅ **Rivière-du-Loup enrichment:** 730 businesses enriched (94.9% email capture, ~$1 cost) via Claude Cloud
- ✅ **Calendar parsing:** ALL 9,094 entries parsed by GPT-5 Pro (100% success, 22 seconds, 70.8% phone capture)
- ✅ **Data merge & cleaning:** GPT-5 Pro merged both datasets intelligently
  - 6,561 unique businesses (deduplicated from 9,824 input records)
  - 326 Rivière-du-Loup matched to existing calendar clients (44.7%)
  - 404 NEW prospects from Rivière-du-Loup (55.3%)
  - 70 existing clients enriched with Rivière-du-Loup data
  - 2,737 calendar duplicates merged (30% of calendar entries!)
- ✅ **SuiteCRM installation:** Docker deployment complete (localhost:8082)
- ✅ **CSV import files:** 5 files generated (23,581 total records across Accounts/Contacts/Calls/Notes/Tasks)
- ✅ **Bi-directional sync:** Complete architecture designed (see BIDIRECTIONAL-SYNC-ARCHITECTURE.md)
- ✅ **Offline work guide:** Created for train travel setup (OFFLINE-WORK-GUIDE.md)
- ⏭️ **User actions pending:**
  - Complete SuiteCRM web installer
  - Create Marc & André users, note UUIDs
  - Create 7 custom fields via Studio
  - Replace user_id placeholders in CSV files
  - Import all data via SuiteCRM web interface
  - Verify 6,561 businesses imported correctly
- ⏭️ **Build sync engine:** Implement bi-directional sync (Google Calendar ↔ SuiteCRM)

### Calendar Migration Strategy (CONFIRMED 2025-11-14)

**Problem:** 9,094 completely unstructured calendar entries need extraction to SuiteCRM

**Solution:** Split by date, use local Haiku agents for recent + Cloud for historical

#### Date Split Strategy
1. **Recent (2024-2025):** ~1,000-1,500 entries
   - **Process locally:** Spawn Haiku agents here via Task tool
   - **Cost:** ~$0.15 USD (1,500 × $0.0001)
   - **Time:** ~1 hour (parallel agents)

2. **Historical (pre-2024):** ~7,500-8,000 entries
   - **Process in Cloud:** Claude Code Cloud instance
   - **Cost:** ~$0.75 USD (7,500 × $0.0001)
   - **Time:** ~5-8 hours (parallel agents)

#### Color Mappings (CONFIRMED)

**Marc's Calendar:**
- 🟠 Orange → New prospect
- 🟡 Yellow → Prospect has been called
- 🟢 Green → Call back for some reason
- 🩷 Pink → Send promo/media kit
- 🟣 Purple → Appointment booked
- ⬛ Black → Chase for payment
- ⬜ Dark Grey → Chase for payment

**André's Calendar:**
- 🔵 Dark Blue → Call prospect
- 🔴 Red → Do not call / not interested
- ⬛ Black → Chase for payment
- ⬜ Dark Grey → Chase for payment

#### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                LOCAL (This Claude Session)              │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │  Parse 2024-2025 Entries (~1,500)             │   │
│  │  - Spawn 10-15 Haiku agents (Task tool)        │   │
│  │  - Each processes ~100-150 entries             │   │
│  │  - Extract structured JSON                     │   │
│  │  - Cost: ~$0.15 USD                            │   │
│  └────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐   │
│  │  Merge Results → JSON                          │   │
│  │  Save: data/parsed_calendars/recent.json       │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│             CLOUD (Claude Code Cloud)                   │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │  Parse Pre-2024 Entries (~7,500)               │   │
│  │  - Spawn 40-50 Haiku agents                    │   │
│  │  - Each processes ~150-200 entries             │   │
│  │  - Extract structured JSON                     │   │
│  │  - Cost: ~$0.75 USD                            │   │
│  └────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐   │
│  │  Commit to GitHub                              │   │
│  │  File: data/parsed_calendars/historical.json   │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

                        ▼
            ┌───────────────────────┐
            │  Merge Both Files     │
            │  Build SuiteCRM CSV   │
            │  Import to CRM        │
            └───────────────────────┘
```

#### Key Files
- **Calendar ICS files:** `/mnt/c/Users/Setup/Downloads/marc@etre.ics` (6.3MB), `André @etre.ics` (4.3MB)
- **Color mappings:** `docs/CALENDAR-COLOR-MAPPINGS.md`
- **Migration plan:** `docs/CALENDAR-TO-SUITECRM-MIGRATION-PLAN.md`
- **Sync architecture:** `docs/CALENDAR-SUITECRM-SYNC-ARCHITECTURE.md`
- **Parser script:** `scripts/parse_calendar_with_ai.py` (template, needs adaptation for Task tool)
- **Import builder:** `scripts/build_suitecrm_import.py`

#### API Usage Tracking
- **Google Custom Search API:** 125/1,000 queries used (tracked in `data/query_tracker.json`)
- **Remaining budget:** 875 queries for future regions

### Workflow Integration

**Local Agent Pattern:**
```python
# Spawn Haiku agent for calendar parsing batch
Task(
  subagent_type="general-purpose",
  description="Parse calendar entries 1-100",
  model="haiku",
  prompt="""
Parse these 100 calendar entries and extract structured data.
For each entry, extract: contact info, contact persons, activity timeline, next actions.
French patterns: "Je dois rappeler" = call back, "Répondeur" = voicemail.
Return JSON array with all extracted data.
"""
)
```

**Cloud Agent Pattern:**
- Use `ORCHESTRATOR-PROMPT-RIVIERE-DU-LOUP.md` as template
- Adapt for calendar parsing instead of web scraping
- Spawn 40-50 agents for historical entries
- Commit results to GitHub for retrieval

### Cost Summary (GGQ-CRM)
- **Prospect enrichment (821):** ~$2.40 USD (40 agents × ~20 businesses)
- **Calendar parsing recent (1,500):** ~$0.15 USD (local Haiku agents)
- **Calendar parsing historical (7,500):** ~$0.75 USD (Cloud Haiku agents)
- **Google API usage:** Free tier (1,000 queries/day)
- **Total estimated:** ~$3.30 USD

### Key Files Created
- `/home/setup/ggq-crm/data/parsed_calendars/ggq_crm_master_database.json` (6.9 MB, 6,561 businesses)
- `/home/setup/ggq-crm/data/parsed_calendars/ggq_crm_merge_stats.json` (merge statistics)
- `/home/setup/ggq-crm/data/suitecrm_import/*.csv` (5 import files: Accounts, Contacts, Calls, Notes, Tasks)
- `/home/setup/ggq-crm/docs/BIDIRECTIONAL-SYNC-ARCHITECTURE.md` (complete 2-way sync design)
- `/home/setup/ggq-crm/OFFLINE-WORK-GUIDE.md` (step-by-step setup guide for train travel)
- `/home/setup/ggq-crm/docker-compose.yml` (SuiteCRM + MariaDB containers)
- `/home/setup/ggq-crm/scripts/match_prospects_to_clients.py` (client matching script)

### Data Quality Metrics
**Contact Coverage:**
- 57.2% have phone (3,752 / 6,561)
- 38.3% have email (2,510 / 6,561)
- 40.0% have website (2,628 / 6,561)

**Quality Distribution:**
- MINIMAL: 2,283 (34.8%)
- PARTIAL: 2,172 (33.1%)
- VERIFIED: 1,992 (30.4%)
- HIGH: 114 (1.7%)

**Region Distribution:**
- Other: 4,897 (74.6%)
- Montréal: 673 (10.3%)
- Québec: 555 (8.5%)
- Rivière-du-Loup: 436 (6.6%)

### Next Actions (GGQ-CRM)
1. ✅ Color mappings confirmed
2. ✅ Split ICS files by date (Jan 1 2024 cutoff)
3. ✅ Calendar parsing via GPT-5 Pro (100% success)
4. ✅ Merge results + build SuiteCRM import
5. ⏭️ User completes offline setup during train travel (OFFLINE-WORK-GUIDE.md)
6. ⏭️ Build sync engine implementation (after user verifies import)

---

**Remember:** Traceability is NOT optional. IF.citate and IF.TTT are mandatory for all InfraFabric agent operations.
