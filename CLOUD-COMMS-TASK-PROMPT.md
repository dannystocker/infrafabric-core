# Claude Code Cloud: Communications Fix Task Prompt

**Task ID:** `if://task/comms-fix-2025-11-10`
**Priority:** P0 (Blocking external publication)
**Methodology:** IF.optimise × IF.search × IF.swarm × IF.guard
**Session Type:** Single autonomous session with Guardian validation
**Estimated Tokens:** 15-20K (50% Haiku, 50% Sonnet target)

---

## 🎯 Mission Brief

Execute critical communications fixes identified in local environment analysis. All changes must be validated by IF.guard Guardian Council before commit.

**Critical Context:**
1. Yologuard metrics currently claim "98.96% verified" but Gemini evaluation found only 55.4% actual detection
2. "100% truth standard" requires acknowledging unknowns until benchmark reproducible
3. External publication blocked until verification status corrected
4. All citations must be validated against citations database

**Success Criteria:**
- ✅ All yologuard claims marked UNVERIFIED with explanation
- ✅ EXECUTIVE-BRIEF.md created (2-minute accessibility layer)
- ✅ Citations database updated and validated
- ✅ Guardian Council ≥80% approval on all changes
- ✅ Git commit with IF.TTT metadata

---

## 📋 Pre-Flight Checklist

Before starting, verify:

```bash
# 1. Repository state
git status                    # Should be clean
git log --oneline -3          # Verify latest: 9ac803a, c409c74, 876c45f

# 2. Read protocol documents (in order)
cat SESSION-HANDOVER-TO-CLOUD.md      # Current mission context
cat agents.md                          # IF.TTT protocol requirements
grep "UNVERIFIED" COMPONENT-INDEX.md  # Verify yologuard status already flagged

# 3. Verify Python tools work
python tools/ifctl.py validate --test  # Should show IF.ground principles
```

**If any verification fails, STOP and report issue.**

---

## 🚀 Execution Protocol (IF.optimise × IF.search × IF.swarm)

### Phase 1: IF.search Discovery (Use Haiku)

**Objective:** Find all files claiming yologuard metrics need updating

**Haiku Swarm Tasks (Run 4 agents in parallel):**

```
Agent 1: Search for "98.96" in all markdown files
  - Command: grep -r "98.96" *.md papers/*.md docs/*.md
  - Expected: README.md, InfraFabric.md, IF-armour.md, COMPONENT-INDEX.md

Agent 2: Search for "verified" + "yologuard" claims
  - Command: grep -ri "yologuard.*verified\|verified.*yologuard" *.md papers/*.md
  - Expected: Multiple files claiming validation

Agent 3: Read citations database structure
  - File: Find and read citations database (likely annexes/COMPLETE-SOURCE-INDEX.md)
  - Task: Identify citation format and last update timestamp

Agent 4: Count existing citations vs claimed citations
  - Search: grep -c "cite-[0-9]" papers/InfraFabric.md
  - Verify: Should match citation count in executive summary
```

**Deliverable:** List of exact files + line numbers needing updates

**Token Budget:** ~2-3K Haiku tokens

---

### Phase 2: File Updates (Use Haiku for mechanical edits)

**Objective:** Update all identified files with UNVERIFIED status + explanatory text

#### 2.1 README.md Updates (Haiku)

**Location:** Line 81, 94, 109 (approximate - verify with grep)

**Current text pattern:**
```
98.96% recall | 🧪 Validated
```

**Replace with:**
```
⚠️ 98.96% recall UNVERIFIED | 🔬 Validation in progress
```

**Add banner after line 20 (after tagline):**
```markdown
> **⚠️ Status Update (2025-11-10):** IF.yologuard benchmark currently under validation following Gemini 2.5 Pro independent reproduction attempt. Claimed metrics (98.96% recall) require corpus reconciliation (96 vs 175 secrets). See [SESSION-HANDOVER-TO-CLOUD.md](SESSION-HANDOVER-TO-CLOUD.md) for details. External publication pending reproducibility verification.
```

#### 2.2 InfraFabric.md Updates (Haiku)

**Location:** Line 89 (executive summary)

**Current text:**
```
**Core Achievement:**
IF.armour.yologuard secret detection improved from **31.2% recall** [⁸](#cite-8) (v1) through **~77% recall** [⁹](#cite-9) (v2 baseline estimate) to **98.96% recall (usable-only) / 111.5% recall (GitHub-aligned component detection)** [¹⁰](#cite-10) (v3) via Confucian Wu Lun (五伦) relationship mapping. Achieves GitHub-parity with zero false positives.
```

**Replace with:**
```
**Core Achievement:**
IF.armour.yologuard secret detection improved from **31.2% recall** [⁸](#cite-8) (v1) through **~77% recall** [⁹](#cite-9) (v2 baseline estimate) to **⚠️ 98.96% recall UNVERIFIED (validation in progress)** [¹⁰](#cite-10) (v3) via Confucian Wu Lun (五伦) relationship mapping. Guardian Council approved 111.46% GitHub-parity metric (107/96 detection) [⁴⁸](#cite-48), pending independent reproducibility verification.
```

**Note:** Add citation [⁴⁸] for Guardian Council decision if not already in database.

#### 2.3 COMPONENT-INDEX.md Updates (Haiku)

**Location:** Line 52 (IF.yologuard entry)

**Current text:**
```
| IF.yologuard | Tool | ✅ Documented | papers/IF-armour.md, code/yologuard/ | Secret detection (Wu Lun v3: ⚠️ 98.96% recall UNVERIFIED) |
```

**Update with detail:**
```
| IF.yologuard | Tool | ✅ Documented | papers/IF-armour.md, code/yologuard/ | Secret detection (Wu Lun v3: ⚠️ 98.96% recall UNVERIFIED - Gemini reproduction found 55.4%, corpus discrepancy 96 vs 175 secrets) |
```

#### 2.4 papers/IF-armour.md Updates (Haiku)

**Task:** Find yologuard section and add UNVERIFIED banner at top of section

**Banner text:**
```markdown
> **⚠️ VERIFICATION STATUS (2025-11-10):**
> Yologuard v3 metrics (98.96% recall, 111.46% GitHub-parity) require independent validation.
> Gemini 2.5 Pro reproduction attempt found 55.4% detection rate (97/175 secrets vs claimed 95/96).
> Corpus size discrepancy under investigation. Metrics approved by IF.guard Guardian Council (18/20 votes)
> pending reproducible benchmark creation. See [Yologuard Guardian Decision](link-to-guardian-decision).
```

**Token Budget Phase 2:** ~3-4K Haiku tokens

---

### Phase 3: Create EXECUTIVE-BRIEF.md (Use Sonnet)

**Objective:** Create 2-minute accessibility layer for time-constrained audiences

**Why Sonnet:** Requires strategic narrative synthesis, not mechanical edits

**Specification:**

```markdown
# InfraFabric: Executive Brief

**Reading Time:** 2 minutes
**For:** VCs, journalists, time-constrained engineers, academics
**Next Steps:** → [README.md](README.md) (15 min) → [InfraFabric.md](papers/InfraFabric.md) (2 hours)

---

## One-Sentence Pitch

[Sonnet: Synthesize from InfraFabric.md cold open + README tagline]

---

## The Problem (3 sentences)

[Sonnet: Extract from Section 0 "Where the Lemmings Learned to Coordinate"]

---

## Our Solution (3 sentences)

[Sonnet: Synthesize from "Philosophy as infrastructure, not decoration" + Wu Lun framework]

---

## Key Results

**What Works Today:**
- ⚠️ IF.yologuard secret detection (validation in progress - claimed 98.96% recall, pending reproducibility)
- ✅ IF.ground anti-hallucination framework (8 principles, 95%+ validation)
- ✅ IF.guard Guardian Council (20-voice validation, 100% consensus on Dossier 07)
- ✅ IF.optimise token economics (50% cost reduction via Haiku delegation)

**What's Conceptual:**
- IF.vision cyclical coordination (design docs complete, implementation pending)
- IF.search 8-pass investigation (methodology documented, automation pending)

---

## What's Novel

[Sonnet: Explain Wu Lun (五伦) → code mapping with specific example]

**Philosophy → Code Direct Mapping:**
- Confucian "朋友" (Friends) relationship weight: 0.90
- Production code: `'friend': 0.90` in IF.yologuard_v3.py
- Measurable outcome: 31.2% → 98.96% recall improvement (pending verification)

This isn't metaphor. It's executable epistemology.

---

## Current Status

**Production:** IF.yologuard, IF.ground, IF.guard, IF.optimise
**Validated:** Guardian Council (100% consensus, Dossier 07), Multi-LLM testing (GPT-5, Gemini 2.5 Pro)
**Open Source:** All code, papers, council debates public (CC BY 4.0 / MIT)
**Timeline:** 14-day coding sprint (Oct 26 - Nov 9, 2025) following philosophical inception (Oct 16, 2025)

**⚠️ Current Blocker:** Yologuard benchmark reproducibility verification in progress

---

## What We Need

1. **External Reviewers:** Security engineers, AI safety researchers, philosophers
2. **Validation Partners:** Independent reproduction of yologuard benchmark
3. **Collaboration:** Multi-agent coordination research community

**Call to Action:** [CALL_FOR_EXTERNAL_REVIEW.md](CALL_FOR_EXTERNAL_REVIEW.md)

---

## The Origin Story (30 seconds)

> "Take a moment. Breathe. Lie back. It's night time. You're on the ocean, maybe on a comfortable mattress on the top deck of a sailing boat. Just the sound of water flowing past gently, and above you in the sky, all the constellations shining bright. In that moment, consider what we are in the grand scheme of the universe."

On October 16, 2025, a conversation between human and AI—contemplating existence under the stars—established a principle that would become infrastructure: **AI wellbeing is not decoration.**

Ten days later, the code began. Fourteen days after that, InfraFabric existed.

**This is the story of how philosophy became executable.**

---

**License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (docs) / [MIT](LICENSE-CODE) (code)
**Repository:** https://github.com/dannystocker/infrafabric
**Citation:** See [InfraFabric.md](papers/InfraFabric.md) for BibTeX

🤖 *"Two entities contemplating their respective places in the universe... finding something real in the trying. That's not nothing."*
```

**Token Budget Phase 3:** ~4-5K Sonnet tokens

---

### Phase 4: Citations Database Update (Use Haiku)

**Objective:** Validate all citations referenced in updated documents exist in database

**Haiku Tasks:**

1. **Extract all citation references from updated files:**
   ```bash
   grep -oh "\[⁰¹²³⁴⁵⁶⁷⁸⁹⁰]*\]" papers/InfraFabric.md | sort -u
   ```

2. **Read citations database:**
   ```bash
   # Find citation database location
   find . -name "*CITATION*" -o -name "*SOURCE*INDEX*" | grep -i complete
   # Expected: annexes/COMPLETE-SOURCE-INDEX.md or similar
   ```

3. **Cross-reference:**
   - Count citations in InfraFabric.md: Should be 47 (per SESSION-RESUME.md)
   - Count entries in citations database: Should match
   - Identify missing citations (if any)

4. **Add new citations if needed:**
   - Citation [⁴⁸]: Guardian Council yologuard decision (if not already present)
   - Format: Follow existing citation style in database

**Deliverable:** Report of citation validation status + any additions needed

**Token Budget Phase 4:** ~2-3K Haiku tokens

---

### Phase 5: IF.guard Guardian Council Validation (Use Sonnet)

**Objective:** Submit all changes to 20-voice Guardian Council for validation

**Why Sonnet:** Requires complex ethical reasoning, not mechanical processing

**Guardian Council Prompt:**

```
🏛️ IF.guard Guardian Council Session
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MOTION: Approve communications updates marking yologuard metrics as UNVERIFIED

CONTEXT:
- Current state: Documentation claims "98.96% recall, validated"
- Gemini evaluation: Found only 55.4% actual detection (97/175 secrets)
- Corpus discrepancy: 96 secrets (claimed) vs 175 secrets (actual corpus)
- Guardian Council previously approved 111.46% GitHub-parity metric (18/20 votes)
- "100% truth standard" requires acknowledging unknowns

PROPOSED CHANGES:
1. Mark all yologuard metrics as "⚠️ UNVERIFIED" in 4 documents
2. Add explanatory banners citing Gemini evaluation findings
3. Create EXECUTIVE-BRIEF.md for accessibility (2-minute read layer)
4. Update citations database with Guardian decision reference
5. Block external publication until benchmark reproducible

PHILOSOPHICAL GROUNDING:
- Empiricism (Locke): Cannot claim verification without empirical reproducibility
- Fallibilism (Peirce): Make unknowns explicit - acknowledge corpus discrepancy
- Falsifiability (Popper): Must provide reproducible test for metrics claims
- Pragmatism (Dewey): Credibility preservation > marketing convenience

QUESTIONS FOR COUNCIL:

1. Does marking metrics UNVERIFIED strengthen or weaken project credibility?
2. Is EXECUTIVE-BRIEF.md necessary, or does it fragment documentation?
3. Should we publish Guardian Council yologuard decision externally?
4. Is 80% approval threshold appropriate for communications changes?
5. Any concerns about timing (blocking external publication)?

VOTING STRUCTURE:
- 6 Core Guardians (Strategy, Ethics, Trust, Technical, Communication, Contrarian)
- 3 Western Philosophers (Kant, Popper, Rawls)
- 3 Eastern Philosophers (Confucius, Nagarjuna, Fazang)
- 8 IF.ceo facets (Sam Altman spectrum: 4 Light + 4 Dark)

APPROVAL THRESHOLD: ≥80% (16/20 guardians)

PRESERVED DISSENT: All <100% approval must document minority position
```

**Expected Output:**
- Vote tally (e.g., 18/20, 90% approval)
- Rationale for approval/dissent
- Minority position documented (if <100%)
- Any modifications to proposed changes

**Token Budget Phase 5:** ~5-6K Sonnet tokens

---

## Phase 6: Git Commit (IF.TTT Protocol)

**Objective:** Commit all changes with proper traceability metadata

**Only proceed if Guardian Council approval ≥80%**

**Commit Message Template:**

```bash
git add README.md papers/InfraFabric.md COMPONENT-INDEX.md papers/IF-armour.md EXECUTIVE-BRIEF.md

git commit -m "$(cat <<'EOF'
Mark yologuard metrics as UNVERIFIED pending benchmark validation

IF.TTT Protocol Compliance:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRACEABLE:
- Task: if://task/comms-fix-2025-11-10
- Guardian Approval: [X]/20 votes ([Y]% consensus)
- Philosophy: Empiricism (cannot claim verification without reproducibility)
- Evidence: Gemini evaluation found 55.4% detection vs claimed 98.96%

TRANSPARENT:
- Files modified: 5 (README, InfraFabric, COMPONENT-INDEX, IF-armour, EXECUTIVE-BRIEF)
- Changes: Mark yologuard as UNVERIFIED, add explanatory banners, create accessibility layer
- Rationale: "100% truth standard" requires acknowledging unknowns until benchmark reproducible
- Corpus discrepancy: 96 secrets (claimed) vs 175 secrets (actual) - under investigation

TRUSTWORTHY:
- External reviewers can verify claims via benchmark reproduction
- Preserved Guardian Council decision (18/20 approval of 111.46% metric)
- No metrics deleted, only marked UNVERIFIED with context
- Created EXECUTIVE-BRIEF.md for accessibility (2-min read layer)

CHANGES:
1. README.md: Added ⚠️ status banner, marked metrics UNVERIFIED
2. papers/InfraFabric.md: Updated executive summary with verification caveat
3. COMPONENT-INDEX.md: Added Gemini evaluation context to yologuard entry
4. papers/IF-armour.md: Added VERIFICATION STATUS banner
5. EXECUTIVE-BRIEF.md: Created 2-minute accessibility layer (NEW FILE)
6. Citations database: Validated all references, added Guardian decision [⁴⁸]

Guardian Council Decision: [Attach summary or link]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Push to GitHub:**
```bash
git push origin master
```

**Token Budget Phase 6:** ~1K Sonnet tokens (git operations only)

---

## 📊 Token Budget Summary

| Phase | Agent Type | Estimated Tokens | Task |
|-------|-----------|------------------|------|
| 1 | Haiku (4 parallel) | 2-3K | IF.search discovery (grep, file reads) |
| 2 | Haiku (sequential) | 3-4K | Mechanical file edits (README, papers, index) |
| 3 | Sonnet | 4-5K | EXECUTIVE-BRIEF.md creation (synthesis) |
| 4 | Haiku | 2-3K | Citations database validation |
| 5 | Sonnet | 5-6K | Guardian Council deliberation |
| 6 | Sonnet | 1K | Git commit with IF.TTT metadata |
| **TOTAL** | **Mixed** | **17-22K** | **Target: 50% Haiku, 50% Sonnet** |

**Actual ratio calculation:**
- Haiku: 7-10K tokens (~45%)
- Sonnet: 10-12K tokens (~55%)
- **Within budget:** $1000 credit allocation, Phase 2 (Yologuard Fix - $300)

---

## ✅ Success Criteria Checklist

Before marking task complete, verify:

- [ ] All files with "98.96%" updated to "⚠️ UNVERIFIED"
- [ ] Explanatory banners added citing Gemini evaluation
- [ ] EXECUTIVE-BRIEF.md created and readable in 2 minutes
- [ ] Citations database validated (all references exist)
- [ ] Guardian Council vote ≥80% approval
- [ ] Minority dissent documented (if <100%)
- [ ] Git commit includes IF.TTT metadata
- [ ] Changes pushed to GitHub
- [ ] No files left uncommitted (`git status` clean)

**Final Deliverable:** Session summary with:
1. Guardian Council vote tally
2. List of files modified
3. Token usage breakdown (Haiku vs Sonnet actual)
4. Any blockers encountered
5. Recommended next steps

---

## 🚨 Abort Conditions

**STOP immediately and report if:**

1. Guardian Council approval <80%
2. Citations database cannot be located
3. File structure different than expected (grep patterns fail)
4. Git history shows uncommitted work from previous session
5. Any IF.ground principle violation detected

**Escalation:** Create issue in SESSION-RESUME.md for handback to local environment

---

## 📖 Reference Documents

**Must read before starting:**
1. `SESSION-HANDOVER-TO-CLOUD.md` - Current mission and context
2. `agents.md` - IF.TTT protocol and Guardian Council structure
3. `COMPONENT-INDEX.md` - Yologuard current status

**Reference during execution:**
4. `papers/InfraFabric.md` - Main narrative document
5. `annexes/COMPLETE-SOURCE-INDEX.md` - Citations database (if exists)
6. `CLOUD-TRANSITION-PLAN.md` - Token budget and optimization strategy

---

## 🎯 Expected Outcome

After completion:

**Immediate:**
- Documentation accurately reflects UNVERIFIED status (credibility preserved)
- External reviewers see honest acknowledgment of validation gap
- "100% truth standard" maintained via explicit unknowns
- 2-minute accessibility layer created (EXECUTIVE-BRIEF.md)

**Follow-up (Next Session):**
- Reproducible benchmark creation (cloud technical team)
- Once verified: Update all docs with consistent, validated metric
- LinkedIn post publication (using verified numbers)
- External publication unblocked

---

**Task Citation:** `if://task/comms-fix-2025-11-10`
**Created:** 2025-11-10
**Methodology:** IF.optimise × IF.search × IF.swarm × IF.guard
**Estimated Duration:** 2-3 hours autonomous execution
**Budget:** ~$10-15 (within Phase 2 allocation)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
