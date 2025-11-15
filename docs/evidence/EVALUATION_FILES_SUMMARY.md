# InfraFabric Evaluation System - Files Summary

## What Was Created

A complete multi-evaluator assessment system with **citation and documentation verification** built-in.

---

## Files Overview

| File | Size | Purpose |
|------|------|---------|
| **INFRAFABRIC_EVAL_PASTE_PROMPT.txt** | 10KB | Paste-ready prompt for Codex/Gemini/Claude |
| **INFRAFABRIC_COMPREHENSIVE_EVALUATION_PROMPT.md** | 16KB | Full methodology with detailed instructions |
| **merge_evaluations.py** | 10KB | Python script to merge YAML outputs |
| **EVALUATION_WORKFLOW_README.md** | 7KB | Detailed workflow guide |
| **EVALUATION_QUICKSTART.md** | 4KB | Quick reference card |
| **EVALUATION_FILES_SUMMARY.md** | This file | Summary of all files |

---

## Key Features Added (Per Your Request)

### ✅ Citation Verification (MANDATORY)

**Papers Directory Audit:**
- Check every citation is traceable (DOI, URL, or file reference)
- Verify at least 10 external URLs are not 404
- Flag outdated citations (>10 years old unless foundational)
- Assess citation quality (peer-reviewed > blog posts)
- Check if citations actually support the claims

**README.md Audit:**
- Verify all links work (100% coverage)
- Check if examples/screenshots are current
- Verify install instructions work
- Flag claims that don't match codebase reality (e.g., "production-ready" when it's a prototype)
- Test at least 3 code examples

### YAML Schema Includes:

```yaml
citation_verification:
  papers_reviewed: 12
  total_citations: 87
  citations_verified: 67
  citation_quality_score: 7  # 0-10
  issues:
    - severity: "high"
      issue: "Claim about AGI timelines lacks citation"
      file: "papers/epistemic-governance.md:L234"
      fix: "Add citation or mark as speculation"
    - severity: "medium"
      issue: "DOI link returns 404"
      file: "papers/collapse-patterns.md:L89"
      citation: "https://doi.org/10.1234/broken"
      fix: "Find working link or cite archived version"

  readme_audit:
    accuracy_score: 6  # 0-10
    links_checked: 15
    broken_links: 3
    broken_link_examples:
      - url: "https://example.com/deprecated"
        location: "README.md:L45"
    code_examples_tested: 3
    code_examples_working: 2
    screenshots_current: false
    issues:
      - severity: "medium"
        issue: "README claims 'production-ready' but code is prototype"
        fix: "Change to 'research prototype'"
```

---

## Consensus Report Includes Citation Section

When you run `merge_evaluations.py`, the consensus report now includes:

### Citation & Documentation Quality (Consensus)

**Overall Citation Stats:**
- Papers reviewed: 12 (average across evaluators)
- Total citations found: 87
- Citations verified: 67 (77%)

**Citation Issues (by consensus):**

🔴 **DOI link returns 404** (3/3 evaluators - 100% consensus)
- Severity: high
- Identified by: Codex, Gemini, Claude
- Example: papers/collapse-patterns.md:L89

🟡 **Citation from 2005 (20 years old)** (2/3 evaluators - 67% consensus)
- Severity: medium
- Identified by: Codex, Claude
- Example: papers/coordination.md:L45

**Broken Links Found:**
- https://example.com/deprecated
- https://old-domain.com/research
- ... and 3 more

---

## What This Achieves

### 1. Research Integrity
- ✅ Every claim is traceable to a source
- ✅ No "trust me bro" assertions in papers
- ✅ Outdated citations flagged for review
- ✅ Broken links identified and fixed

### 2. Documentation Accuracy
- ✅ README reflects current codebase state
- ✅ No false advertising (e.g., "production-ready" when it's a prototype)
- ✅ All examples work
- ✅ All links are valid

### 3. Consensus Validation
- ✅ If 3/3 evaluators flag a missing citation → it's definitely missing
- ✅ If 3/3 evaluators flag a broken link → it's definitely broken
- ✅ Focus on 100% consensus issues first

---

## Usage

### Step 1: Run Evaluations

```bash
# Copy prompt
cat INFRAFABRIC_EVAL_PASTE_PROMPT.txt

# Paste into 3 sessions:
# - Codex → save as codex_infrafabric_eval_2025-11-14.yaml
# - Gemini → save as gemini_infrafabric_eval_2025-11-14.yaml
# - Claude → save as claude_infrafabric_eval_2025-11-14.yaml
```

### Step 2: Merge Results

```bash
./merge_evaluations.py codex_*.yaml gemini_*.yaml claude_*.yaml
```

### Step 3: Review Citation Issues

```bash
# See all citation issues with 100% consensus
grep -A 5 "100% consensus" INFRAFABRIC_CONSENSUS_REPORT.md | grep "🔴\|🟡"

# See all broken links
grep -A 20 "Broken Links Found" INFRAFABRIC_CONSENSUS_REPORT.md
```

---

## Example Findings

### What Evaluators Will Catch:

**Citation Issues:**
- "AGI will arrive by 2030" (no citation)
- "Studies show..." (which studies?)
- DOI links that return 404
- Wikipedia citations (low quality)
- Citations from 2005 when 2024 research exists

**README Issues:**
- "Production-ready" (but it's a prototype)
- "Supports 100k users" (but no load testing)
- `npm install` (but package.json is missing)
- Screenshot from 2 years ago (UI has changed)
- Link to deprecated documentation

---

## Files Location

All files in: `/home/setup/navidocs/`

```
/home/setup/navidocs/
├── INFRAFABRIC_EVAL_PASTE_PROMPT.txt          (10KB - main prompt)
├── INFRAFABRIC_COMPREHENSIVE_EVALUATION_PROMPT.md  (16KB - full methodology)
├── merge_evaluations.py                        (10KB - merger script)
├── EVALUATION_WORKFLOW_README.md              (7KB - detailed guide)
├── EVALUATION_QUICKSTART.md                   (4KB - quick reference)
└── EVALUATION_FILES_SUMMARY.md                (this file)
```

---

## Next Steps

1. **Copy prompt** to Codex/Gemini/Claude
2. **Wait for evaluations** (3-6 hours, run in parallel)
3. **Merge results** with `merge_evaluations.py`
4. **Fix 100% consensus issues** first (citations, broken links)
5. **Fix 67%+ consensus issues** next
6. **Investigate <67% consensus** (might be edge cases)

---

## Benefits

✅ **Standardized format** → Easy comparison across evaluators
✅ **Quantified metrics** → No vague assessments
✅ **Citation integrity** → All claims are traceable
✅ **README accuracy** → Documentation matches reality
✅ **Consensus ranking** → Focus on high-confidence findings
✅ **Actionable fixes** → Every issue includes a fix and effort estimate

---

**Ready to evaluate InfraFabric with brutal honesty and research integrity.**
