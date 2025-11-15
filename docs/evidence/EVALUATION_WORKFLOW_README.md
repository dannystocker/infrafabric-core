# InfraFabric Multi-Evaluator Workflow

This directory contains prompts and tools for evaluating InfraFabric using multiple AI evaluators (Codex, Gemini, Claude) and automatically merging their feedback.

## Files

### 1. Prompts
- **`INFRAFABRIC_COMPREHENSIVE_EVALUATION_PROMPT.md`** - Full evaluation framework (7.5KB)
- **`INFRAFABRIC_EVAL_PASTE_PROMPT.txt`** - Concise paste-ready version (3.4KB)

### 2. Tools
- **`merge_evaluations.py`** - Python script to compare and merge YAML outputs

## Workflow

### Step 1: Run Evaluations in Parallel

Copy the paste-ready prompt and run in 3 separate sessions:

**Session A: Codex**
```bash
# Copy prompt
cat INFRAFABRIC_EVAL_PASTE_PROMPT.txt

# Paste into Codex session
# Save output as: codex_infrafabric_eval_2025-11-14.yaml
```

**Session B: Gemini**
```bash
# Copy prompt
cat INFRAFABRIC_EVAL_PASTE_PROMPT.txt

# Paste into Gemini session
# Save output as: gemini_infrafabric_eval_2025-11-14.yaml
```

**Session C: Claude Code**
```bash
# Copy prompt
cat INFRAFABRIC_EVAL_PASTE_PROMPT.txt

# Paste into Claude Code session
# Save output as: claude_infrafabric_eval_2025-11-14.yaml
```

### Step 2: Merge Results

Once you have all 3 YAML files:

```bash
./merge_evaluations.py codex_*.yaml gemini_*.yaml claude_*.yaml
```

This generates: **`INFRAFABRIC_CONSENSUS_REPORT.md`**

## What the Merger Does

The `merge_evaluations.py` script:

1. **Score Consensus**
   - Averages scores across evaluators (overall, conceptual, technical, etc.)
   - Calculates variance and identifies outliers
   - Shows individual scores for comparison

2. **IF.* Component Status**
   - Merges component assessments (implemented/partial/vaporware)
   - Shows consensus level (e.g., "3/3 evaluators agree")
   - Averages completeness percentages for implemented components

3. **Critical Issues (P0/P1/P2)**
   - Aggregates issues across evaluators
   - Ranks by consensus (how many evaluators identified it)
   - Merges effort estimates

4. **Buyer Persona Analysis**
   - Averages fit scores and willingness-to-pay
   - Identifies consensus on target markets
   - Ranks by aggregate fit score

## Example Output Structure

```markdown
# InfraFabric Evaluation Consensus Report

**Evaluators:** Codex, Gemini, Claude
**Generated:** 2025-11-14

## Score Consensus

### overall_score
- **Average:** 6.5/10
- **Variance:** 0.25
- **Individual scores:**
  - Codex: 6.0
  - Gemini: 7.0
  - Claude: 6.5
- **Outliers:** None

## IF.* Component Status (Consensus)

### IMPLEMENTED

**IF.guard** (3/3 evaluators agree - 100% consensus)
- Evaluators: Codex, Gemini, Claude
- Average completeness: 73%

**IF.citate** (3/3 evaluators agree - 100% consensus)
- Evaluators: Codex, Gemini, Claude
- Average completeness: 58%

### PARTIAL

**IF.sam** (3/3 evaluators agree - 100% consensus)
- Evaluators: Codex, Gemini, Claude

**IF.optimize** (2/3 evaluators agree - 67% consensus)
- Evaluators: Codex, Claude

### VAPORWARE

**IF.swarm** (2/3 evaluators agree - 67% consensus)
- Evaluators: Gemini, Claude

## P0 Blockers (Consensus)

**API keys exposed in documentation** (3/3 evaluators - 100% consensus)
- Identified by: Codex, Gemini, Claude
- Effort estimates: 1 hour, 30 minutes

**No authentication system** (3/3 evaluators - 100% consensus)
- Identified by: Codex, Gemini, Claude
- Effort estimates: 3-5 days, 1 week

## Buyer Persona Consensus

**Academic AI Safety Researchers**
- Avg Fit Score: 7.7/10
- Avg Willingness to Pay: 3.3/10
- Identified by: Codex, Gemini, Claude

**Enterprise AI Governance Teams**
- Avg Fit Score: 6.0/10
- Avg Willingness to Pay: 7.0/10
- Identified by: Codex, Gemini, Claude
```

## Benefits of This Approach

### 1. Consensus Validation
- **100% consensus** = High-confidence finding (all evaluators agree)
- **67% consensus** = Worth investigating (2/3 agree)
- **33% consensus** = Possible blind spot or edge case (1/3 unique finding)

### 2. Outlier Detection
- Identifies when one evaluator is significantly different from others
- Helps spot biases or unique insights

### 3. Easy Comparison
- YAML format makes `diff` and `grep` trivial
- Programmatic filtering: `yq '.gaps_and_issues.p0_blockers' codex_eval.yaml`

### 4. Aggregated Metrics
- Average scores reduce individual evaluator bias
- Variance shows agreement level

### 5. Actionable Prioritization
- Issues ranked by consensus (how many evaluators flagged it)
- Effort estimates from multiple perspectives

## Advanced Usage

### Filter by Consensus Level

Show only issues with 100% consensus:
```bash
python3 -c "
import yaml
with open('INFRAFABRIC_CONSENSUS_REPORT.md') as f:
    content = f.read()
    for line in content.split('\n'):
        if '100% consensus' in line:
            print(line)
"
```

### Extract P0 Blockers Only

```bash
grep -A 3 "P0 Blockers" INFRAFABRIC_CONSENSUS_REPORT.md
```

### Compare Individual Scores

```bash
for file in *_eval.yaml; do
    echo "=== $file ==="
    yq '.executive_summary.overall_score' "$file"
done
```

## Tips

1. **Run evaluations in parallel** - All 3 can run simultaneously
2. **Use exact YAML schema** - Don't modify the structure
3. **Save raw outputs** - Keep individual evaluations for reference
4. **Version control consensus reports** - Track how assessments evolve over time
5. **Focus on 100% consensus items first** - These are highest-confidence findings

## Next Steps After Consensus Report

1. **P0 Blockers with 100% consensus** → Fix immediately
2. **IF.* components with 100% "vaporware" consensus** → Remove from docs or implement
3. **Buyer personas with highest avg fit + WTP** → Focus GTM strategy
4. **Issues with <67% consensus** → Investigate (might be edge cases or evaluator blind spots)

## Troubleshooting

**Issue:** YAML parse error
- **Fix:** Ensure evaluators used exact schema (no custom fields at top level)

**Issue:** Missing scores
- **Fix:** Check all evaluators filled in all sections (use schema as checklist)

**Issue:** Consensus report empty
- **Fix:** Verify YAML files are in current directory and named correctly

## Example Session

```bash
# 1. Start evaluations (paste prompt into 3 sessions)
cat INFRAFABRIC_EVAL_PASTE_PROMPT.txt

# 2. Wait for all 3 to complete (1-2 hours each)

# 3. Download YAML outputs to current directory
# codex_infrafabric_eval_2025-11-14.yaml
# gemini_infrafabric_eval_2025-11-14.yaml
# claude_infrafabric_eval_2025-11-14.yaml

# 4. Merge
./merge_evaluations.py *.yaml

# 5. Review consensus
cat INFRAFABRIC_CONSENSUS_REPORT.md

# 6. Act on high-consensus findings
grep -A 3 "100% consensus" INFRAFABRIC_CONSENSUS_REPORT.md
```

---

**Ready to evaluate InfraFabric with brutal honesty and scientific rigor.**
