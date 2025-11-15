# InfraFabric Evaluation - Quick Start

## TL;DR

**Goal:** Get brutal, comparable feedback from 3 AI evaluators (Codex, Gemini, Claude) on InfraFabric

**Time:** 3-6 hours (evaluations run in parallel)

**Output:** Consensus report showing what all evaluators agree on

---

## 3-Step Process

### Step 1: Copy Prompt (5 seconds)

```bash
cat /home/setup/navidocs/INFRAFABRIC_EVAL_PASTE_PROMPT.txt
```

### Step 2: Paste into 3 Sessions (3-6 hours total, run in parallel)

1. **Codex session** → Save output as `codex_infrafabric_eval_2025-11-14.yaml`
2. **Gemini session** → Save output as `gemini_infrafabric_eval_2025-11-14.yaml`
3. **Claude Code session** → Save output as `claude_infrafabric_eval_2025-11-14.yaml`

### Step 3: Merge Results (10 seconds)

```bash
cd /home/setup/navidocs
./merge_evaluations.py codex_*.yaml gemini_*.yaml claude_*.yaml
```

**Output:** `INFRAFABRIC_CONSENSUS_REPORT.md`

---

## What You'll Get

### 1. Score Consensus
```yaml
overall_score: 6.5/10 (average across 3 evaluators)
variance: 0.25 (low variance = high agreement)
```

### 2. IF.* Component Status
```
IF.guard: ✅ Implemented (3/3 agree, 73% complete)
IF.citate: ✅ Implemented (3/3 agree, 58% complete)
IF.sam: 🟡 Partial (3/3 agree - has design, no code)
IF.swarm: ❌ Vaporware (2/3 agree - mentioned but no spec)
```

### 3. Critical Issues (Ranked by Consensus)
```
P0: API keys exposed (3/3 evaluators - 100% consensus) - 1 hour fix
P0: No authentication (3/3 evaluators - 100% consensus) - 3-5 days
P1: IF.sam not implemented (3/3 evaluators - 100% consensus) - 1-2 weeks
```

### 4. Buyer Persona Fit
```
1. Academic AI Safety: Fit 7.7/10, WTP 3.3/10 (loves it, won't pay)
2. Enterprise Governance: Fit 6.0/10, WTP 7.0/10 (will pay if production-ready)
```

---

## Why This Works

✅ **YAML format** → Easy to diff, merge, filter programmatically
✅ **Mandatory schema** → All evaluators use same structure
✅ **Quantified scores** → No vague assessments, everything is 0-10 or percentage
✅ **Consensus ranking** → Focus on what all evaluators agree on first
✅ **File citations** → Every finding links to `file:line` for traceability

---

## Files Reference

| File | Size | Purpose |
|------|------|---------|
| `INFRAFABRIC_EVAL_PASTE_PROMPT.txt` | 9.4KB | Paste this into Codex/Gemini/Claude |
| `INFRAFABRIC_COMPREHENSIVE_EVALUATION_PROMPT.md` | 15KB | Full methodology (reference) |
| `merge_evaluations.py` | 8.9KB | Merges YAML outputs |
| `EVALUATION_WORKFLOW_README.md` | 6.6KB | Detailed workflow guide |
| `EVALUATION_QUICKSTART.md` | This file | Quick reference |

---

## Expected Timeline

| Phase | Duration | Parallelizable? |
|-------|----------|-----------------|
| Start 3 evaluation sessions | 1 minute | Yes |
| Wait for evaluations to complete | 3-6 hours | Yes (all 3 run simultaneously) |
| Download YAML files | 2 minutes | No |
| Run merger | 10 seconds | No |
| Review consensus report | 15-30 minutes | No |
| **Total elapsed time** | **3-6 hours** | (mostly waiting) |

---

## Troubleshooting

**Q: Evaluator isn't following YAML format**
```bash
# Show them the schema again (it's in the prompt)
grep -A 100 "YAML Schema:" INFRAFABRIC_EVAL_PASTE_PROMPT.txt
```

**Q: Merger script fails**
```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('codex_eval.yaml'))"

# Install PyYAML if needed
pip install pyyaml
```

**Q: Want to see just P0 blockers**
```bash
grep -A 5 "P0 Blockers" INFRAFABRIC_CONSENSUS_REPORT.md
```

---

## What to Do with Results

### Priority 1: 100% Consensus P0 Blockers
- **Everyone agrees these are critical**
- Fix immediately before anything else

### Priority 2: IF.* Components (Vaporware → Implemented)
- Components all 3 evaluators flagged as vaporware = remove from docs or build
- Components all 3 flagged as partial = finish implementation

### Priority 3: Market Focus
- Buyer persona with highest `fit_score * willingness_to_pay` = your target customer
- Ignore personas with high fit but low WTP (interesting but won't make money)

### Priority 4: Documentation Cleanup
- Issues with 100% consensus on docs = definitely fix
- Issues with <67% consensus = might be evaluator bias, investigate

---

## Next Session Prompt

After you have the consensus report, create a debug session:

```markdown
# InfraFabric Debug Session

Based on consensus evaluation from Codex, Gemini, and Claude (2025-11-14):

**P0 Blockers (100% consensus):**
1. API keys exposed in docs (1 hour fix)
2. No authentication system (3-5 days)

**IF.* Components to implement:**
1. IF.sam (design exists, no code - 1-2 weeks)
2. [...]

Please implement fixes in priority order, starting with P0s.
```

---

## Key Insight

**Focus on 100% consensus findings first.**

If all 3 evaluators (different architectures, different training data, different biases) independently flag the same issue → it's real and important.

---

**Ready to get brutally honest feedback. Copy the prompt and run 3 evaluations in parallel.**
