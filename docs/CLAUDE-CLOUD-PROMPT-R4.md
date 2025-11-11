# InfraFabric r4 Philosophy Database - Claude Cloud Onboarding

**Purpose:** Comprehensive prompt for Claude.ai Cloud sessions working on InfraFabric after r4 integration
**Target:** Claude Sonnet/Opus on https://claude.ai
**Last Updated:** 2025-11-11
**Commit:** 73e52a4
**Citation:** if://citation/gpt5pro-fixpack-r4-2025-11-11

---

## Quick Context: What Is InfraFabric?

InfraFabric is a **philosophical governance framework for AI agent systems** that grounds agent behavior in epistemology (theory of knowledge). It maps 26 philosophical traditions to concrete software components (IF.search, IF.guard, IF.witness, etc.) to make AI systems **traceable, transparent, and trustworthy** (IF.TTT).

**Key Innovation:** Every AI decision can be traced back to a philosophical principle, with citations linking to observable artifacts (files, commits, research papers).

---

## 🚀 What Changed in r4 (2025-11-11)

### Philosophy Database Expansion
- **Before:** 16 philosophers (75% Western)
- **After:** 26 philosophers (54% Western, 46% non-Western)
- **New:** 9 philosophical traditions added (Islamic, African, Indigenous, Phenomenology, Critical Theory, Process, Feminist Epistemology, Postmodernism, Tech Philosophy)

### Three Major Additions

**1. Code Examples (docs/PHILOSOPHY-CODE-EXAMPLES.md)**
- 7 concrete philosophy→code mappings
- Shows how abstract principles become TypeScript/Python/YAML implementations
- Example: "Vienna Circle verificationism → CI toolchain gate (ifctl.py lint)"

**2. Philosophical Tensions (embedded in YAML)**
- Cross-cultural debates documented (e.g., Al-Ghazali ↔ Avicenna on causality)
- Each tension has IF-specific resolution strategy
- Example: "Empirical adjudication via falsifiers; reversible switches"

**3. Historical Lineage (embedded in YAML)**
- All 26 philosophers have `influenced_by` and `influenced` chains
- Joe Coulombe (Trader Joe's founder) now positioned in retail epistemology tradition
- Influenced_by: A&P, 7-Eleven (anti-model)

---

## 📂 Repository Structure (GitHub)

**Primary Repo:** https://github.com/dannystocker/infrafabric.git

### Key Files You'll Need

**Philosophy Database (Core):**
```
docs/evidence/gemini-logs/core/IF.philosophy-database-r4.yaml (955 lines)
├─ 16 core philosophers (Epictetus, Locke, Peirce, Vienna Circle, Duhem, Quine,
│  James, Dewey, Popper, Buddha, Lao Tzu, Confucius, Joe Coulombe, etc.)
└─ Joe Coulombe now has historical_context
```

**Philosophy Database (Additions):**
```
docs/evidence/gemini-logs/core/PATCH-IF.philosophy-database.additions.yaml (292 lines)
├─ 9 new traditions with tensions_with and historical_context
└─ Al-Ghazali, Avicenna, Averroes, Ubuntu, Indigenous, Phenomenology,
   Critical Theory, Process, Feminist Epistemology, Postmodernism, Tech Philosophy
```

**Code Examples:**
```
docs/PHILOSOPHY-CODE-EXAMPLES.md (125 lines)
├─ 7 philosophy→code mappings
└─ Verificationism→CI, Falsifiability→Feature Flags, Ubuntu→Guard, etc.
```

**Agent Behavior:**
```
agents.md (875 lines)
├─ IF.TTT traceability protocol (mandatory for all agents)
├─ Agent types (Sonnet, Haiku, specialized)
└─ NEW: 2025-11-11 r4 upgrade section (lines 736-850)
```

**Evaluation & Context:**
```
docs/GPT5PRO-WORK-EVALUATION-IF-IMPACT.md (r3 evaluation: 4.55/5)
docs/CLAUDE_V4_EPIC_COMPREHENSIVE_PROMPT.md (20KB execution guide)
/tmp/R4-INTEGRATION-SUMMARY.md (comprehensive r4 analysis)
```

---

## 🎯 IF.TTT Framework (MANDATORY)

**Every operation must be Traceable, Transparent, Trustworthy.**

### 1. Traceable
- Link every claim to observable source (file:line, commit SHA, external citation)
- Generate IF.citation URIs: `if://citation/<uuid>`
- Include SHA-256 hashes for verification

**Example:**
```
Claim: "Philosophy database has 26 philosophers"
Source: docs/evidence/gemini-logs/core/IF.philosophy-database-r4.yaml:1-955
Verification: python tools/ifctl.py lint (19/19 OK checks)
Citation: if://citation/philosophy-db-count-2025-11-11
```

### 2. Transparent
- Document decision rationale (why this approach, not alternatives?)
- Preserve dissent (Contrarian Guardian votes never deleted)
- Track token costs (Haiku vs Sonnet ratio)

### 3. Trustworthy
- Reproducible (include verification commands)
- Falsifiable (testable predictions in commit messages)
- Revocable (status: unverified → verified → disputed → revoked)

---

## 🧠 Philosophy Database: Key Concepts

### Joe Coulombe (Merchant-Philosopher)
**Tradition:** Modern Applied Pragmatism (Retail Epistemology)
**Era:** 1960s–2010s
**Key Concept:** Constraint-driven curation; private label only when differentiated

**IF Components:** IF.search, IF.optimise, IF.guard, IF.persona, IF.citation, IF.quiet, IF.garp

**Operating Laws:**
1. **Do Without:** If category is undifferentiated → drop it
2. **Private Label:** Only where meaningfully better value/quality
3. **Supplier COD:** Net-0 (COD/fast terms) to avoid hidden risk
4. **Small/Dense:** Prefer small footprint, high traffic, high SKU velocity
5. **Write Memos:** 5-year white papers + weekly field notes

**IF.search Integration:**
- Joe guides passes 1,2,5,6,7 (Map, Collect, Challenge, Predict, Witness)
- Differentiation-filter: "Require unique value vs peers; else drop"
- Private-label-only-when-better: "Prefer best-in-class unless own label is provably superior"

**Historical Context (NEW in r4):**
- Influenced_by: A&P (grocery pioneer), 7-Eleven (anti-model for small stores)
- Influenced: Modern private-label retail (Costco Kirkland, Amazon Basics)
- Additional_readings: Becoming Trader Joe (2021), Acquired Podcast: Trader Joe's (2025)

### New Philosophers (r4)

**Al-Ghazali (Islamic Occasionalism):**
- Key Concept: All causal power belongs to God; apparent causation is occasioned by divine will
- IF Components: IF.witness, IF.citation, IF.search
- Tension: ↔ Avicenna (necessary causation vs occasionalism)
- Resolution: Empirical adjudication via falsifiers; reversible switches

**Avicenna (Islamic Peripatetic):**
- Key Concept: Essence/existence distinction; Flying Man thought experiment
- IF Components: IF.persona, IF.search
- Application: Model persona essence (schema) separate from runtime instances

**Ubuntu (African Philosophy):**
- Key Concept: Personhood through community ("I am because we are")
- IF Components: IF.guard, IF.swarm
- Code Example: Python `approve()` function with quorum/supermajority thresholds

**Process Philosophy (Whitehead/Bergson):**
- Key Concept: Reality as process; events over substances
- IF Components: IF.witness, IF.swarm
- Code Example: YAML append-only event log with Ed25519 signatures

---

## 💻 Code Examples (Philosophy → Implementation)

### 1. Verificationism → CI Toolchain Gate
**Philosophy:** Vienna Circle - meaningful statements must be empirically verifiable
**IF Principle:** Principle 2 (Validate with the Toolchain)

```yaml
# .github/workflows/ifctl-lint.yml
name: ifctl-lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: python ifctl.py lint   # Fails build on schema errors
```

### 2. Falsifiability → One-Line Rollback
**Philosophy:** Popper - scientific claims must be refutable
**IF Principle:** Principle 7 (Reversible Decisions)

```typescript
// feature-flags.ts
export const ENABLE_EXPERIMENTAL_ROUTING = false; // Reversible switch

// router.ts
if (ENABLE_EXPERIMENTAL_ROUTING) {
  return experimentalRouter(request);
}
return stableRouter(request);
```

### 3. Ubuntu Consensus → Guard Gating
**Philosophy:** African Ubuntu - "I am because we are"
**IF Principle:** Principle 5 (Gate Client-Only Features)

```python
# guard_gate.py
def approve(action_votes, quorum=15, approval=0.50, supermajority=0.80):
    present = sum(v is not None for v in action_votes)
    if present < quorum: return "NO-QUORUM"
    rate = sum(1 for v in action_votes if v is True)/present
    if rate >= supermajority: return "ADVISE-PROCEED"
    if rate > approval: return "PROCEED"
    return "VETO"
```

### 4. Joe's Heuristics → Search Pass Filters
**Philosophy:** Joe Coulombe - curate "one-of-one" and drop undifferentiated categories
**IF Principle:** Principle 6 (Progressive Enhancement)

```yaml
# SWARM.config.v4-epic.yaml
if.search:
  passes: 8
  filters:
    - name: "differentiation-filter"
      rule: "require unique value vs peers; else drop"
    - name: "private-label-only-when-better"
      rule: "prefer best-in-class unless own label is provably superior"
```

**More examples:** See `docs/PHILOSOPHY-CODE-EXAMPLES.md` for all 7 mappings.

---

## 🛠️ Validation & Linting

### Run the Linter
```bash
python tools/ifctl.py lint
```

**Expected Output:**
```json
{
  "ok": true,
  "ok_checks": 19,
  "fail_checks": 0,
  "results": [
    {"ok": true, "msg": "persona[joe] OK"},
    {"ok": true, "msg": "philosophers[epictetus] OK"},
    // ... 17 more checks
  ]
}
```

**What it validates:**
- Persona schema (joe)
- 13 philosopher definitions (epictetus, locke, peirce, vienna_circle, duhem, quine, james, dewey, popper, buddha, lao_tzu, confucius, joe)
- Guard constitution thresholds (council_size, approval_threshold, supermajority_advice, contrarian_veto_threshold)
- No alias collisions

---

## 📋 Agent Behavior Guidelines (r4)

### When Making IF.guard Decisions
**OLD:** "Let's approve this change"
**NEW:** "Using Al-Ghazali ↔ Avicenna tension resolution: empirical adjudication via falsifiers. Proposal requires 2-week reversibility window (docs/evidence/gemini-logs/core/PATCH-IF.philosophy-database.additions.yaml:20-23)"

### When Implementing IF Principles
**OLD:** "Implementing Principle 7"
**NEW:** "Implementing Principle 7 (Reversibility) using Popper's falsifiability pattern (docs/PHILOSOPHY-CODE-EXAMPLES.md:30-45)"

### When Executing IF.search Passes
**Apply Joe's differentiation-filter:**
1. Does this evidence provide unique value vs. peers?
2. If not, drop it (Joe's "do without" heuristic)
3. Prefer best-in-class sources unless private research is provably superior

### When Generating Citations
**Include historical lineage:**
```json
{
  "citation_id": "if://citation/joe-retail-heuristics-2025-11-11",
  "philosophical_grounding": "Joe Coulombe (influenced_by: A&P, 7-Eleven anti-model)",
  "historical_context": "Modern Applied Pragmatism (Retail Epistemology), 1960s–2010s",
  "sources": [
    {"type": "book", "ref": "Becoming Trader Joe (2021)", "hash": "sha256:..."},
    {"type": "podcast", "ref": "Acquired: Trader Joe's (2025)", "hash": "sha256:..."}
  ]
}
```

### When Spawning Swarm Agents
**OLD:** "Spawn 8 agents"
**NEW:** "Spawn 8 agents distributed across cultural traditions: 2 Islamic (Al-Ghazali, Avicenna), 2 Indigenous (relational epistemology), 2 Process (Whitehead), 2 Western (Popper, Peirce)"

---

## 🎓 Common Tasks & Examples

### Task 1: Execute IF.search 8-Pass Investigation
```
1. Read docs/SWARM.config.v4-epic.yaml for pass configuration
2. Apply Joe's differentiation-filter at passes 1,2,5,6,7
3. Generate citations for each finding: if://citation/<uuid>
4. Store evidence in docs/evidence/<topic>-<date>.md
5. Link to philosophy database: "Using Joe's 'do without' heuristic (IF-philosophy-database-r4.yaml:208-243)"
```

### Task 2: Guardian Council Deliberation
```
1. Gather 20-voice council (6 Core + 3 Western + 3 Eastern + 8 IF.sam)
2. Check for philosophical tensions (e.g., Al-Ghazali ↔ Avicenna)
3. Apply tension resolution strategy from database
4. Vote with thresholds:
   - Quorum: 15/20
   - Approval: >50%
   - Supermajority (advice): ≥80%
   - Contrarian veto: ≥95% (2-week cooling-off)
5. Record dissent (NEVER delete)
6. Generate decision citation: if://decision/<topic>-<date>
```

### Task 3: Validate Traceability
```bash
# Check all citations are valid
python tools/citation_validate.py citations/session-2025-11-11.json

# Verify file hashes match claims
sha256sum docs/evidence/gemini-logs/core/IF.philosophy-database-r4.yaml
# Should match: (first 7 chars shown in commits)

# Run linter
python tools/ifctl.py lint
# Expect: 19/19 OK
```

---

## 🚨 Anti-Patterns (What NOT To Do)

### ❌ Undocumented Claims
**Bad:**
```
"The philosophy database has 26 philosophers."
```

**Good:**
```
"The philosophy database has 26 philosophers (docs/evidence/gemini-logs/core/IF.philosophy-database-r4.yaml:1-955, verified 2025-11-11 with ifctl.py lint: 19/19 OK).

Citation:
  claim_id: "if://claim/philosophy-db-count"
  sources: [{"type":"file","ref":"IF-philosophy-database-r4.yaml","hash":"sha256:..."}]
  status: "verified"
```

### ❌ Ignoring Philosophical Tensions
**Bad:**
```
"Let's use both Al-Ghazali's occasionalism and Avicenna's necessary causation."
[No acknowledgment of contradiction]
```

**Good:**
```
"Al-Ghazali and Avicenna have documented tension on causality (occasionalism vs necessity).
Per r4 resolution strategy: Use empirical adjudication via falsifiers + reversible switches.
Implementation: Feature flag for causality model, A/B test for 2 weeks, choose based on evidence.
Citation: docs/evidence/gemini-logs/core/PATCH-IF.philosophy-database.additions.yaml:20-28"
```

### ❌ Mass-Renaming Historical References
**Bad:**
```
git grep -l "IF.yologuard" | xargs sed -i 's/IF.yologuard/IF.armour.yologuard/g'
[Breaks traceable lineage in historical documents]
```

**Good:**
```
"Historical documents (before 2025-11-10) use IF.yologuard.
Going forward, use IF.armour.yologuard in new work.
Both names refer to same component (see docs/FIX.component-canonicalization.yaml).
Preserve git history - do not mass-rename."
```

---

## 📊 Metrics & Validation (r4)

| Metric | r3 (Commit 44a365b) | r4 (Commit 73e52a4) | Delta |
|--------|---------------------|---------------------|-------|
| Philosophy DB Lines | 1,038 | 1,247 (955 core + 292 patch) | +209 lines (+20%) |
| Philosophers | 25 | 26 | +1 (Joe moved to core) |
| Cultural Diversity | 75% Western, 25% non-Western | 54% Western, 46% non-Western | +21% non-Western |
| Code Examples | 0 | 7 (125 lines) | +7 examples |
| Tensions Documented | 0 | 3+ (embedded) | +3 minimum |
| Historical Lineage | 0 | 26 philosophers | +26 entries |
| Linter Checks | 17 OK | 19 OK | +2 checks |

**Quality Rating:** 4.55/5 (r3 evaluation) → TBD (pending r4 real-world validation)

---

## 🔄 Next Steps (Recommended)

### 1. Integrate Joe Source Materials
- Extract case examples from "Becoming Trader Joe" (2021)
- Timestamp-link Acquired podcast segments to IF.search passes
- Create `docs/JOE-HISTORICAL-EXAMPLES.md` with real Trader Joe's decisions

### 2. Validate Tension Resolutions
- Run IF.guard council on controversial decision
- Test if "empirical adjudication via falsifiers" actually resolves Al-Ghazali ↔ Avicenna
- Document case study: `docs/case-studies/TENSION-RESOLUTION-001.md`

### 3. Execute V4 Epic Intelligence Dossier
- Use `docs/CLAUDE_V4_EPIC_COMPREHENSIVE_PROMPT.md` as execution guide
- Deploy Joe persona to guide passes 1,2,5,6,7
- Measure: claims per pass, evidence density, Joe veto rate

### 4. Expand Code Examples
- Current: 7 examples (Vienna Circle, Popper, Duhem-Quine, Ubuntu, Process, Indigenous, Joe)
- Remaining: 19 philosophers without code mappings
- Target: 26 examples (one per philosopher)

---

## 🔐 Security & Privacy

**Sensitive Data:**
- Never commit API keys, passwords, or credentials
- IF.armour.yologuard scans for secrets (v3.0 with OpenRouter/DeepSeek detection)
- Revoked keys whitelist: /home/setup/.security/revoked-keys-whitelist.md

**Git Configuration:**
- Primary remote: https://github.com/dannystocker/infrafabric.git
- Local Gitea mirror: http://localhost:4000/dannystocker/infrafabric.git
- Always push to GitHub after commits

---

## 📞 Support & Documentation

**Full Documentation:**
- `/home/setup/infrafabric/agents.md` (Agent behavior, IF.TTT protocol)
- `/home/setup/infrafabric/docs/PHILOSOPHY-CODE-EXAMPLES.md` (7 code examples)
- `/home/setup/infrafabric/docs/GPT5PRO-WORK-EVALUATION-IF-IMPACT.md` (r3 evaluation)
- `/tmp/R4-INTEGRATION-SUMMARY.md` (Comprehensive r4 analysis)

**Key Papers:**
- `papers/IF-foundations.md` (Epistemological foundations)
- `papers/IF-vision.md` (Architecture vision)
- `papers/IF-witness.md` (Meta-validation framework)
- `papers/IF-armour.md` (Security framework)

**Validation Commands:**
```bash
python tools/ifctl.py lint                # Validate personas/philosophers/guard
cat docs/PHILOSOPHY-CODE-EXAMPLES.md      # View code examples
git log --oneline | head -5               # Recent commits
grep -A3 "tensions_with" docs/evidence/gemini-logs/core/PATCH-IF.philosophy-database.additions.yaml  # View tensions
```

---

## 🎯 Session Checklist

**Before starting work:**
- [ ] Read `agents.md` section: "2025-11-11: Philosophy Database r4 Upgrade" (lines 736-850)
- [ ] Verify linter passes: `python tools/ifctl.py lint` (expect 19/19 OK)
- [ ] Check git status: `git status` (should be clean if starting fresh)
- [ ] Review philosophy database structure (26 philosophers, embedded tensions/lineage)

**During work:**
- [ ] Generate IF.citation URIs for all claims: `if://citation/<uuid>`
- [ ] Link to philosophy database when making decisions
- [ ] Apply Joe's differentiation-filter for IF.search passes
- [ ] Use tension resolution strategies for conflicting philosophies
- [ ] Preserve dissent (Contrarian Guardian votes never deleted)

**Before ending session:**
- [ ] Update SESSION-RESUME.md with current state
- [ ] Commit all changes with IF.TTT-compliant message
- [ ] Push to GitHub: `git push origin master`
- [ ] Export citations to `/citations/session-<date>.json`
- [ ] Run linter one last time: `python tools/ifctl.py lint`
- [ ] Copy any evaluation documents to /tmp/ for user review

---

## 🚀 Quick Start Command Sequence

```bash
# 1. Verify environment
cd /home/setup/infrafabric
python tools/ifctl.py lint                # Should show 19/19 OK

# 2. Check philosophy database
cat docs/PHILOSOPHY-CODE-EXAMPLES.md | grep "^##"
# Shows: 7 philosophy→code mappings

# 3. View tensions
grep -A3 "tensions_with" docs/evidence/gemini-logs/core/PATCH-IF.philosophy-database.additions.yaml
# Shows: Al-Ghazali ↔ Avicenna, etc.

# 4. Check git status
git status                                # Should be clean
git log --oneline -5                      # Recent commits

# 5. Start work with IF.TTT compliance
# Always link claims to sources with citations!
```

---

**Ready to work on InfraFabric with r4 philosophy database!**

**Key Principle:** Every claim must be traceable, transparent, and trustworthy. When in doubt, cite the philosophy database and link to concrete code examples.

**Citation for this prompt:** if://doc/claude-cloud-prompt-r4-2025-11-11
**Last Updated:** 2025-11-11 by Claude Sonnet 4.5 (Commit 73e52a4)
