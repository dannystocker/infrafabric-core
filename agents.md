# InfraFabric Agent Architecture

**Purpose:** Define agent behavior patterns, traceability requirements, and coordination protocols for InfraFabric work.

**Audience:** All Claude instances working on InfraFabric (Sonnet, Haiku, specialized agents).

**Last Updated:** 2025-11-10

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
- **2025-11-11:** Philosophy Database r4 upgrade (26 philosophers, tensions, lineage, code examples) - Commit 73e52a4
- **2025-11-10:** Initial creation for IF.TTT integration - Commit 44a365b

**Last Updated:** 2025-11-11
**Updated By:** if://agent/claude-sonnet-4.5
**Citation:** if://decision/agents-md-update-r4-2025-11-11

---

**Remember:** Traceability is NOT optional. IF.citate and IF.TTT are mandatory for all InfraFabric agent operations.
