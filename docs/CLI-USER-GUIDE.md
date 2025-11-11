# IF.witness CLI User Guide

Welcome! This guide will help you get started with the IF.witness suite of tools for provenance tracking, cost monitoring, and audit trails. Whether you're a DevOps engineer, data scientist, compliance officer, or product manager, you'll find practical examples to solve real problems.

---

## Table of Contents

1. [Quick Start (5 Minutes)](#quick-start-5-minutes)
2. [Installation & Setup](#installation--setup)
3. [Core Concepts](#core-concepts)
4. [CLI Tools Overview](#cli-tools-overview)
5. [Common Workflows](#common-workflows)
6. [Command Reference](#command-reference)
7. [Practical Examples](#practical-examples)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [FAQ](#faq)

---

## Quick Start (5 Minutes)

Get your first witness log and cost report running in under 5 minutes.

### Step 1: Install

```bash
pip install if-tools
```

Verify installation:
```bash
if-witness --help
if-optimise --help
```

You should see command help text. If not, check the [Installation & Setup](#installation--setup) section.

### Step 2: Log Your First Operation

Let's create a witness entry for an AI operation:

```bash
if-witness log \
  --event "llm_inference" \
  --component "chatbot.inference" \
  --trace-id "chat-session-001" \
  --payload '{"user": "alice", "query": "explain bitcoin"}' \
  --tokens-in 150 \
  --tokens-out 300 \
  --cost 0.001234 \
  --model "claude-sonnet-4.5"
```

You should see output like:
```
✓ Witness entry created: 3fa2b8c1-9d4e-4a2b-b9c3...
✓ Hash chain verified (entry 0 → 1)
✓ Signature: ed25519:a1b2c3d4e5f6g7h8...
✓ Cost: $0.001234 (450 tokens)
```

Congratulations! You've created your first witness entry.

### Step 3: View Your First Cost Report

```bash
if-witness cost --trace-id "chat-session-001"
```

Output:
```
Cost Breakdown (trace: chat-session-001)

Component                  Tokens     Cost         Model
------------------------------------------------------------------------
chatbot.inference          450        $0.001234    claude-sonnet-4.5
------------------------------------------------------------------------
Total                      450        $0.001234
```

### Step 4: Verify It Worked

```bash
if-witness verify
```

Output:
```
✓ 1 entries verified
✓ Hash chain intact (no tampering)
✓ All signatures valid
```

**Congratulations!** You've successfully:
- Created a witness entry ✓
- Logged costs ✓
- Verified integrity ✓

Now let's dive deeper into what you can do.

---

## Installation & Setup

### Requirements

- Python 3.8 or higher
- pip (Python package manager)
- ~100 MB disk space for database (grows with usage)

Check your Python version:
```bash
python3 --version
```

### Installation

Install the IF.tools package:

```bash
pip install if-tools
```

Upgrade to the latest version:
```bash
pip install --upgrade if-tools
```

### Configuration

The IF.witness tools store data in `~/.if-witness/` by default:

```
~/.if-witness/
  ├── witness.db         # Main database (auto-created)
  ├── budget.json        # Budget settings (optional)
  └── .if-witness.log    # Log file (auto-created)
```

#### Custom Database Location

By default, the database goes to `~/.if-witness/witness.db`. To use a custom location:

```bash
if-witness --db /path/to/custom/witness.db log \
  --event "test" \
  --component "test" \
  --trace-id "test-001" \
  --payload '{}'
```

Or set an environment variable:
```bash
export IF_WITNESS_DB="/opt/if-witness/db/witness.db"
if-witness log --event "test" ...
```

### Verification

Verify your installation:

```bash
# Check if-witness
if-witness verify

# Check if-optimise rates
if-optimise rates

# Check cost-monitor
if-cost-monitor status
```

If you see command help or output, you're good to go!

---

## Core Concepts

Before using the tools, understand these key ideas.

### What is Witness Logging?

Witness logging creates an **immutable, cryptographically-signed audit trail** of operations. Think of it like a tamper-proof logbook where you record:

- **Who** did it (component name)
- **What** happened (event type)
- **When** it happened (timestamp)
- **Why** it happened (trace ID linking related operations)
- **How much** it cost (tokens, $)

Example audit trail for a chatbot:
```
1. [10:05:00] chatbot.input: user_message
2. [10:05:01] llm.inference: api_call (450 tokens, $0.001)
3. [10:05:02] chatbot.output: response_sent
```

### Why Hash Chains Matter

A **hash chain** prevents tampering. Each entry references the previous entry's hash:

```
Entry 1                    Entry 2                    Entry 3
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ payload: "start" │      │ payload: "op"    │      │ payload: "end"   │
│ hash: a1b2c3...  │      │ prev_hash: a1... │      │ prev_hash: d4... │
│ prev_hash: null  │ ---> │ hash: d4e5f6...  │ ---> │ hash: g7h8i9...  │
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

If someone tries to change Entry 2's data, the hash changes, and Entry 3's `prev_hash` no longer matches. The chain is broken, and tampering is detected.

**Every operation is signed with Ed25519 cryptography**, so you can prove who created each entry.

### What are Trace IDs?

A **trace ID** links related operations together. Use it to track a complete flow:

```
Trace ID: "video-processing-job-42"

Entry 1: download_video          (trace-id: video-processing-job-42)
Entry 2: extract_frames          (trace-id: video-processing-job-42)
Entry 3: run_llm_analysis        (trace-id: video-processing-job-42)
Entry 4: upload_results          (trace-id: video-processing-job-42)
```

You can then query all entries for a trace:
```bash
if-witness trace video-processing-job-42
```

Good trace ID formats:
- `chat-session-${uuid}`
- `batch-job-${date}-${id}`
- `video-processing-${filename}-${timestamp}`
- `experiment-${name}-${run-number}`

### Cost Tracking Basics

The tools track **three cost dimensions**:

1. **Per-operation cost**: How much did one operation cost?
   - Input tokens × input rate + output tokens × output rate

2. **Per-component cost**: How much did a component spend?
   - Sum of all operations in that component

3. **Per-trace cost**: How much did a complete workflow cost?
   - Sum of all operations in that trace

Example:
```
Trace: "llm-experiment-001"
├─ claude-sonnet inference: 1M tokens → $0.025
├─ gpt-5 summary: 500K tokens → $0.040
├─ claude-haiku formatting: 200K tokens → $0.0001
└─ Total: $0.0651 for the whole experiment
```

---

## CLI Tools Overview

The IF.witness suite includes six command-line tools:

### 1. `if-witness` - Provenance Tracking

**What it does**: Logs operations, tracks costs, verifies integrity, exports audit trails.

**Key commands**:
- `log` - Create a new witness entry
- `verify` - Check hash chain integrity
- `trace` - View all entries in a trace
- `cost` - Show cost breakdowns
- `export` - Export to JSON, CSV, or PDF

**Use when**: You need to record what happened, prove it wasn't tampered with, or audit costs.

### 2. `if-optimise` - Cost Management

**What it does**: Shows pricing, tracks budgets, generates cost reports, estimates operation costs.

**Key commands**:
- `rates` - Display current model pricing
- `budget` - Set and monitor budget limits
- `report` - Generate detailed cost reports
- `estimate` - Calculate cost for hypothetical operations

**Use when**: You want to control spending, understand cost trends, or plan budget allocation.

### 3. `if-cost-tracker` - Quick Logging (Helper)

**What it does**: Simplified cost logging without the full witness machinery.

**Use when**: You just need to log a cost quickly without cryptographic overhead.

### 4. `if-budget-alerts` - Monitoring (Helper)

**What it does**: Watches costs and sends alerts when thresholds are crossed.

**Use when**: You want notifications when spending exceeds limits.

### 5. `if-alert-launcher` - Quick Checks (Helper)

**What it does**: One-time cost checks and alerts.

**Use when**: You want a quick cost sanity check before running an expensive operation.

### 6. `if-cost-monitor` - Autonomous Monitoring

**What it does**: Background daemon that continuously monitors costs and triggers alerts.

**Key commands**:
- `start` - Begin continuous monitoring
- `status` - Check current monitoring status

**Use when**: You want always-on cost surveillance across multiple sessions.

---

## Common Workflows

Real-world scenarios and how to solve them with IF.witness.

### Workflow 1: Logging an AI Operation

You run an LLM API call and want to record it with costs:

```bash
# Run your operation (outside of if-witness)
response=$(curl -s https://api.anthropic.com/v1/messages -H "...")

# Extract usage from response
tokens_in=450
tokens_out=280
cost_usd=0.001234

# Log it with if-witness
if-witness log \
  --event "api_call" \
  --component "llm.inference" \
  --trace-id "experiment-001-run-1" \
  --payload "{\"model\": \"claude-sonnet-4.5\", \"status\": \"success\"}" \
  --tokens-in $tokens_in \
  --tokens-out $tokens_out \
  --cost $cost_usd \
  --model "claude-sonnet-4.5"
```

### Workflow 2: Tracking Costs for a Project

Track all costs for a multi-week project:

```bash
# Day 1: Initial exploration
if-witness log \
  --event "exploration" \
  --component "research.exploration" \
  --trace-id "project-neuralnet-2024" \
  --payload '{"phase": "data_prep"}' \
  --cost 5.23 --model "claude-sonnet-4.5" \
  --tokens-in 50000 --tokens-out 30000

# Day 2: Model training
if-witness log \
  --event "training" \
  --component "research.training" \
  --trace-id "project-neuralnet-2024" \
  --payload '{"phase": "model_training", "iterations": 100}' \
  --cost 12.45 --model "claude-sonnet-4.5" \
  --tokens-in 150000 --tokens-out 80000

# Day 3: Evaluation
if-witness log \
  --event "evaluation" \
  --component "research.evaluation" \
  --trace-id "project-neuralnet-2024" \
  --payload '{"phase": "results_analysis"}' \
  --cost 3.12 --model "claude-haiku-4.5" \
  --tokens-in 20000 --tokens-out 15000

# View complete project costs
if-witness trace project-neuralnet-2024

# Export for stakeholders
if-witness export --format pdf --output project-neuralnet-2024.pdf
```

### Workflow 3: Setting Up Budget Alerts

Monitor spending and get notified when approaching limits:

```bash
# Set monthly budget of $500
if-optimise budget --set 500.00 --period month

# Check current status (shows %used, remaining, etc.)
if-optimise budget

# For daily monitoring, start the cost monitor daemon
if-cost-monitor start \
  --budget-daily 10.00 \
  --budget-weekly 50.00 \
  --budget-monthly 500.00

# In another terminal, check status
if-cost-monitor status
```

### Workflow 4: Generating Compliance Reports

Export audit trail for quarterly review or audits:

```bash
# Export Q4 data as PDF compliance report
if-witness export \
  --format pdf \
  --date-range "2024-10-01:2024-12-31" \
  --output Q4-2024-compliance-report.pdf

# Or as CSV for spreadsheet analysis
if-witness export \
  --format csv \
  --date-range "2024-10-01:2024-12-31" \
  --output Q4-2024-witness-log.csv

# Include verification results
if-witness verify
```

### Workflow 5: Cross-Session Tracing

Track operations across multiple days/weeks using the same trace ID:

```bash
# Monday: Start trace
if-witness log \
  --event "job_start" \
  --component "batch.scheduler" \
  --trace-id "weekly-sync-2024-11-11" \
  --payload '{"status": "started"}'

# Tuesday-Friday: Continue same trace
for day in tue wed thu fri; do
  if-witness log \
    --event "daily_sync" \
    --component "sync.worker" \
    --trace-id "weekly-sync-2024-11-11" \
    --payload "{\"day\": \"$day\"}" \
    --cost 0.50 --tokens-in 5000 --tokens-out 3000
done

# Friday: View entire week
if-witness trace weekly-sync-2024-11-11

# Analyze weekly costs
if-witness cost --trace-id "weekly-sync-2024-11-11"
```

---

## Command Reference

Complete reference for all IF.witness commands.

### if-witness Commands

#### `if-witness log`

Create a new witness entry.

```bash
if-witness log \
  --event EVENT_NAME \
  --component COMPONENT_NAME \
  --trace-id TRACE_ID \
  --payload JSON_STRING \
  [--tokens-in INT] \
  [--tokens-out INT] \
  [--cost FLOAT] \
  [--model MODEL_NAME] \
  [--db PATH]
```

**Required options**:
- `--event`: Event type (e.g., `llm_call`, `data_processing`, `api_request`)
- `--component`: Component name (e.g., `chatbot.inference`, `data-pipeline.stage-1`)
- `--trace-id`: Links related operations (e.g., `experiment-001`)
- `--payload`: JSON payload with event details

**Optional options**:
- `--tokens-in`: Input tokens used (for LLM operations)
- `--tokens-out`: Output tokens used (for LLM operations)
- `--cost`: USD cost of operation
- `--model`: Model name used (e.g., `claude-sonnet-4.5`, `gpt-5`)
- `--db`: Custom database path

#### `if-witness verify`

Check that the hash chain is intact and not tampered with.

```bash
if-witness verify [--db PATH]
```

Output tells you:
- Number of entries verified
- Whether hash chain is intact
- Whether all signatures are valid

#### `if-witness trace`

View all entries for a specific trace ID.

```bash
if-witness trace TRACE_ID \
  [--format (text|json)] \
  [--db PATH]
```

**Formats**:
- `text`: Human-readable timeline (default)
- `json`: Structured JSON output

Example output (text):
```
Trace: chat-session-2024-11-11-001

1. [10:05:12] chatbot.input: message_received
   Payload: {"user": "alice"}

2. [10:05:13] llm.inference: api_call
   Cost: $0.001234 (450 tokens, claude-sonnet-4.5)

3. [10:05:14] chatbot.output: response_sent

Duration: 2.15s
Total Cost: $0.001234 (450 tokens)
```

#### `if-witness cost`

Show cost breakdowns by component or trace.

```bash
# For a specific trace
if-witness cost --trace-id TRACE_ID [--format (text|json)] [--db PATH]

# By component (all traces)
if-witness cost \
  [--component COMPONENT_NAME] \
  [--start-date YYYY-MM-DD] \
  [--end-date YYYY-MM-DD] \
  [--format (text|json)] \
  [--db PATH]
```

Example output:
```
Component                  Tokens     Cost         Model
------------------------------------------------------------------------
llm.inference              1250       $0.003121    claude-sonnet-4.5
data.processing            4500       $0.000650    claude-haiku-4.5
api.calls                  2100       $0.002450    gpt-5
------------------------------------------------------------------------
Total                      7850       $0.006221
```

#### `if-witness export`

Export audit trail in multiple formats.

```bash
if-witness export \
  --format (json|csv|pdf) \
  [--output FILE_PATH] \
  [--date-range YYYY-MM-DD:YYYY-MM-DD] \
  [--db PATH]
```

**Formats**:
- `json`: Complete JSON dump (can be large)
- `csv`: Excel/spreadsheet compatible
- `pdf`: Compliance report with verification results

### if-optimise Commands

#### `if-optimise rates`

Show current pricing for all supported models.

```bash
if-optimise rates [--format (text|json)]
```

Example output:
```
Current Model Rates (per token)

Model                    Input              Output
-------------------------------------------------------
gpt-5                    $0.00005000        $0.00015000
claude-sonnet-4.5        $0.00000300        $0.00001500
claude-haiku-4.5         $0.00000025        $0.00000125
gemini-2.5-pro           $0.00000100        $0.00000500
```

#### `if-optimise budget`

Set and monitor budget limits.

```bash
# Set budget
if-optimise budget --set AMOUNT --period (day|week|month) [--component COMPONENT] [--db PATH]

# Check current budget status
if-optimise budget [--period (day|week|month)] [--db PATH]
```

Example output:
```
Budget Status (month)
----------------------------------------
Period:       2024-11-01 - 2024-11-11
Budget:       $500.00
Spent:        $123.45
Remaining:    $376.55
Usage:        24.69%
Operations:   245
Total tokens: 45,600

⚡ NOTICE: 24.69% of budget used
Projected month total: $367.50
```

#### `if-optimise report`

Generate detailed cost reports.

```bash
if-optimise report \
  [--component COMPONENT_NAME] \
  [--start-date YYYY-MM-DD] \
  [--end-date YYYY-MM-DD] \
  [--group-by (component|model|day)] \
  [--format (text|json)] \
  [--db PATH]
```

#### `if-optimise estimate`

Estimate cost for hypothetical operations.

```bash
if-optimise estimate \
  --tokens-in INPUT_COUNT \
  --tokens-out OUTPUT_COUNT \
  --model MODEL_NAME \
  [--operations COUNT]
```

Example:
```bash
if-optimise estimate --tokens-in 1000000 --tokens-out 1000000 --model claude-sonnet-4.5

Output:
Cost Estimate
----------------------------------------
Model:          claude-sonnet-4.5
Input tokens:   1,000,000
Output tokens:  1,000,000
Total tokens:   2,000,000
Cost per op:    $0.018000
```

### if-cost-monitor Commands

#### `if-cost-monitor start`

Begin autonomous cost monitoring.

```bash
if-cost-monitor start \
  [--db PATH] \
  [--budget-daily AMOUNT] \
  [--budget-weekly AMOUNT] \
  [--budget-monthly AMOUNT] \
  [--budget-total AMOUNT] \
  [--check-interval SECONDS]
```

Runs in foreground. Press Ctrl+C to stop. Monitors continuously and prints alerts when thresholds are crossed.

#### `if-cost-monitor status`

Check current monitoring status.

```bash
if-cost-monitor status [--db PATH] [--format (table|json)]
```

Example output:
```
Budget Status:
------------------------------------------------------------------------
daily                  15.2% $1.52 / $10.00 OK
weekly                 28.5% $14.25 / $50.00 OK
monthly                12.3% $61.50 / $500.00 OK
total                  8.9% $44.50 / $500.00 OK

Recent Alerts:
------------------------------------------------------------------------
[WARNING] Daily budget 'daily' at 50.0% ($5.00 of $10.00)
[WARNING] Weekly budget 'weekly' at 75.0% ($37.50 of $50.00)
```

---

## Practical Examples

Real-world scenarios with complete, copy-paste ready examples.

### Example 1: Tracking LLM Costs for a Chatbot

Track and analyze costs for a production chatbot over one day:

```bash
#!/bin/bash
# Track chatbot costs for 2024-11-11

TRACE_ID="chatbot-2024-11-11"
DB_PATH="$HOME/.if-witness/chatbot.db"

# Morning: First wave of requests (8 AM)
if-witness log --db $DB_PATH \
  --event "batch_inference" \
  --component "chatbot.llm" \
  --trace-id $TRACE_ID \
  --payload '{"batch": "morning", "requests": 150}' \
  --tokens-in 75000 --tokens-out 45000 \
  --cost 0.225 --model "claude-sonnet-4.5"

# Noon: Peak traffic (12 PM)
if-witness log --db $DB_PATH \
  --event "batch_inference" \
  --component "chatbot.llm" \
  --trace-id $TRACE_ID \
  --payload '{"batch": "noon", "requests": 450}' \
  --tokens-in 225000 --tokens-out 135000 \
  --cost 0.675 --model "claude-sonnet-4.5"

# Evening: Second wave (6 PM)
if-witness log --db $DB_PATH \
  --event "batch_inference" \
  --component "chatbot.llm" \
  --trace-id $TRACE_ID \
  --payload '{"batch": "evening", "requests": 200}' \
  --tokens-in 100000 --tokens-out 60000 \
  --cost 0.300 --model "claude-sonnet-4.5"

# View daily report
echo "=== Daily Chatbot Costs ==="
if-witness trace $TRACE_ID --db $DB_PATH

# Export for stakeholders
if-witness export --db $DB_PATH \
  --format pdf \
  --date-range "2024-11-11:2024-11-11" \
  --output "chatbot-daily-report-2024-11-11.pdf"

# Check budget status
if-optimise budget --period day --db $DB_PATH
```

### Example 2: Audit Trail for Video Processing Pipeline

Multi-stage pipeline with cost tracking at each stage:

```bash
#!/bin/bash
# Complete video processing pipeline with audit trail

TRACE_ID="video-proc-$(date +%s)"
OUTPUT_FILE="video_processing_audit.log"

# Stage 1: Download video
if-witness log \
  --event "download_video" \
  --component "pipeline.download" \
  --trace-id $TRACE_ID \
  --payload '{"source": "s3://bucket/video.mp4", "size_mb": 250}' \
  --cost 0.002 > "$OUTPUT_FILE"

# Stage 2: Extract frames (CPU-based, no LLM cost)
if-witness log \
  --event "extract_frames" \
  --component "pipeline.extraction" \
  --trace-id $TRACE_ID \
  --payload '{"fps": 30, "total_frames": 7200}' \
  --cost 0.010 >> "$OUTPUT_FILE"

# Stage 3: Run LLM analysis on each frame
if-witness log \
  --event "llm_analysis" \
  --component "pipeline.llm" \
  --trace-id $TRACE_ID \
  --payload '{"frames_analyzed": 7200, "batch_size": 100}' \
  --tokens-in 720000 --tokens-out 360000 \
  --cost 2.160 --model "claude-sonnet-4.5" >> "$OUTPUT_FILE"

# Stage 4: Upload results
if-witness log \
  --event "upload_results" \
  --component "pipeline.upload" \
  --trace-id $TRACE_ID \
  --payload '{"destination": "s3://bucket/results/", "files": 100}' \
  --cost 0.015 >> "$OUTPUT_FILE"

# Generate audit report
echo "=== Processing Pipeline Audit ==="
if-witness trace $TRACE_ID

# Export for compliance
if-witness export --format json --output "video_pipeline_${TRACE_ID}.json"

# Show total cost
if-witness cost --trace-id $TRACE_ID | tail -5
```

### Example 3: Multi-Session Cost Monitoring

Monitor costs across multiple concurrent LLM experiments:

```bash
#!/bin/bash
# Start monitoring with strict budgets

# Set per-experiment budget ($50 per experiment)
if-optimise budget --set 50.00 --period day

# Start continuous monitoring in background
if-cost-monitor start \
  --budget-daily 50.00 \
  --budget-weekly 250.00 \
  --budget-monthly 1000.00 \
  --check-interval 30 &

MONITOR_PID=$!

# Run experiments
EXPERIMENTS=("bert-tuning" "gpt-classification" "t5-summarization")

for exp in "${EXPERIMENTS[@]}"; do
  echo "Starting experiment: $exp"

  # Run 5 iterations
  for iter in {1..5}; do
    if-witness log \
      --event "experiment_iteration" \
      --component "ml.${exp}" \
      --trace-id "${exp}-run-001" \
      --payload "{\"iteration\": $iter}" \
      --tokens-in 50000 --tokens-out 30000 \
      --cost 0.150 --model "claude-sonnet-4.5"

    # Check budget after each iteration
    BUDGET_STATUS=$(if-optimise budget --period day 2>&1 | grep "Usage:")
    echo "[$exp] Iteration $iter complete. $BUDGET_STATUS"
  done
done

# Stop monitoring
kill $MONITOR_PID
wait $MONITOR_PID 2>/dev/null

# Final report
echo "=== Experiment Cost Summary ==="
for exp in "${EXPERIMENTS[@]}"; do
  echo "Experiment: $exp"
  if-witness cost --component "ml.${exp}"
done
```

### Example 4: Compliance Export for Quarterly Review

Prepare audit trail and cost data for compliance review:

```bash
#!/bin/bash
# Q4 2024 Compliance Report

QUARTER_START="2024-10-01"
QUARTER_END="2024-12-31"

echo "Generating Q4 2024 Compliance Report..."

# Export witness log (PDF with verification)
if-witness export \
  --format pdf \
  --date-range "${QUARTER_START}:${QUARTER_END}" \
  --output "Q4-2024-witness-log.pdf"

# Export cost data (CSV for analysis)
if-witness export \
  --format csv \
  --date-range "${QUARTER_START}:${QUARTER_END}" \
  --output "Q4-2024-costs.csv"

# Verify hash chain (adds verification report)
VERIFY_RESULT=$(if-witness verify)
echo "$VERIFY_RESULT" > "Q4-2024-verification.txt"

# Generate detailed cost report
if-optimise report \
  --start-date $QUARTER_START \
  --end-date $QUARTER_END \
  --format json > "Q4-2024-detailed-costs.json"

# Compliance summary
cat > "Q4-2024-COMPLIANCE-SUMMARY.txt" << EOF
Q4 2024 Compliance Report
Generated: $(date)

Hash Chain Verification:
$(if-witness verify)

Cost Summary:
$(if-optimise report --start-date $QUARTER_START --end-date $QUARTER_END)

Exported Files:
- Q4-2024-witness-log.pdf (complete audit trail)
- Q4-2024-costs.csv (cost data for spreadsheets)
- Q4-2024-detailed-costs.json (detailed breakdown)
- Q4-2024-verification.txt (hash chain verification)
EOF

echo "✓ Compliance report generated"
ls -lh Q4-2024*
```

---

## Troubleshooting

Common problems and solutions.

### "❌ Database file not found"

**Problem**: You get an error saying the database doesn't exist.

**Solution**: The database is automatically created on first use. Make sure you have write permissions to `~/.if-witness/`:

```bash
mkdir -p ~/.if-witness
chmod 755 ~/.if-witness

# Try again
if-witness verify
```

### "❌ Permission denied"

**Problem**: You get permission errors when trying to use IF.witness.

**Solution**: Check directory permissions:

```bash
# Fix ownership
chmod 700 ~/.if-witness
chmod 600 ~/.if-witness/witness.db

# Or use a custom database location you own
if-witness --db /tmp/test.db log \
  --event "test" --component "test" \
  --trace-id "test-001" --payload '{}'
```

### "❌ Invalid JSON payload"

**Problem**: Error: "Invalid JSON payload"

**Solution**: Make sure your `--payload` is valid JSON:

```bash
# Wrong: unquoted strings
if-witness log --payload '{user: alice}'

# Right: quoted strings
if-witness log --payload '{"user": "alice"}'

# Tip: Use single quotes to avoid shell escaping
if-witness log --payload '{"key": "value", "count": 42}'
```

### "❌ No entries found for trace_id"

**Problem**: You try to view a trace but it doesn't exist.

**Solution**: Make sure the trace ID is spelled correctly and the entries were logged with that ID:

```bash
# List all traces (via custom database query)
# For now, verify the entry was created:
if-witness verify  # Should show total entry count

# Log an entry with your trace ID
if-witness log \
  --event "test" \
  --component "test" \
  --trace-id "my-trace-001" \
  --payload '{"test": true}'

# Now this should work
if-witness trace my-trace-001
```

### "❌ Hash chain verification failed"

**Problem**: Verification fails with "Hash chain integrity error".

**Possible causes**: Database corruption or tampering detected.

**Solution**:
1. Do NOT modify the database directly
2. Check if the database file is corrupted:
   ```bash
   sqlite3 ~/.if-witness/witness.db "SELECT COUNT(*) FROM witness_entries;"
   ```
3. If severely corrupted, back up and start fresh:
   ```bash
   cp ~/.if-witness/witness.db ~/.if-witness/witness.db.backup
   rm ~/.if-witness/witness.db
   if-witness verify  # Creates new database
   ```

### Cost Not Showing in Reports

**Problem**: You logged costs but they don't appear in reports.

**Solution**:
1. Verify the entry was created:
   ```bash
   if-witness verify
   ```
   Should show entry count > 0

2. Check you're using the correct trace ID:
   ```bash
   if-witness trace your-trace-id
   ```

3. If using custom database path, make sure you're querying the same DB:
   ```bash
   if-witness --db /path/to/db.db cost
   ```

### Monitor Not Sending Alerts

**Problem**: Cost monitor is running but not alerting.

**Solution**:
1. Check monitor status:
   ```bash
   if-cost-monitor status
   ```

2. Verify budgets are configured:
   ```bash
   if-optimise budget --period day
   ```

3. Check if spending actually exceeds thresholds:
   ```bash
   # If spent < 50% of budget, no alerts will trigger
   if-witness cost
   ```

4. Manually test at 90% threshold:
   ```bash
   if-optimise budget --set 0.10  # Set very small budget
   # Log operation costing $0.09
   # Should trigger warning
   ```

---

## Best Practices

Recommendations for effective use of IF.witness.

### When to Use Which Tool

```
Scenario                          → Tool
─────────────────────────────────────────────────────
Log a single operation            → if-witness log
Check if data is tampered with    → if-witness verify
View complete workflow            → if-witness trace
Analyze costs by component        → if-witness cost
Prepare audit for compliance      → if-witness export
Know current model pricing        → if-optimise rates
Set spending limits               → if-optimise budget
Review detailed costs             → if-optimise report
Estimate operation cost           → if-optimise estimate
Always-on cost monitoring         → if-cost-monitor start
```

### Trace ID Conventions

Use consistent, meaningful trace IDs:

**Good**:
- `chat-session-${uuid}` - Unique session IDs
- `batch-job-${date}-${id}` - Batch processes
- `experiment-${name}-${run}` - ML experiments
- `user-${user_id}-${timestamp}` - User workflows

**Avoid**:
- `test` - Too generic
- `op1`, `op2` - Not descriptive
- Random strings - Hard to query

**Examples**:
```bash
# Bad
if-witness log --trace-id "test" ...

# Good
if-witness log --trace-id "experiment-neural-net-01" ...
if-witness log --trace-id "chat-session-$(uuidgen)" ...
if-witness log --trace-id "batch-sync-$(date +%Y-%m-%d)-001" ...
```

### Cost Tracking Strategy

1. **Always log costs** when available:
   ```bash
   # If you know the cost, include it
   if-witness log \
     --tokens-in 1000 --tokens-out 500 \
     --cost 0.0015 --model "claude-sonnet-4.5"
   ```

2. **Use consistent models**:
   ```bash
   # Good: specify model
   --model "claude-sonnet-4.5"

   # Bad: vague or missing
   --model "claude"
   ```

3. **Group related operations** with same trace ID:
   ```bash
   # All parts of one workflow
   if-witness log --trace-id "workflow-42" ...
   if-witness log --trace-id "workflow-42" ...
   if-witness log --trace-id "workflow-42" ...

   # Now easy to analyze: if-witness trace workflow-42
   ```

4. **Set budgets before running expensive operations**:
   ```bash
   if-optimise budget --set 100.00 --period day
   # Then run operations
   # Monitor with: if-optimise budget
   ```

### Security Considerations

1. **Protect your database**:
   ```bash
   chmod 600 ~/.if-witness/witness.db
   chmod 700 ~/.if-witness/
   ```

2. **Don't log sensitive data** in payloads:
   ```bash
   # Bad: includes API key in payload
   --payload '{"api_key": "sk-...", "result": "ok"}'

   # Good: log only necessary metadata
   --payload '{"endpoint": "messages", "status": "success"}'
   ```

3. **Keep payloads minimal**:
   ```bash
   # Instead of entire response, log key metrics
   --payload '{"status": "success", "duration_ms": 245}'
   ```

4. **Verify regularly**:
   ```bash
   # Weekly verification
   if-witness verify
   ```

---

## FAQ

Top 10 questions we hear.

### Q1: How much disk space does IF.witness use?

**A**: The database grows based on volume:
- Empty database: ~100 KB
- 1000 entries: ~500 KB
- 100,000 entries: ~50 MB
- 1,000,000 entries: ~500 MB

The hash chain adds minimal overhead. Most growth is from payload data.

### Q2: Can I migrate to a different database?

**A**: Yes! Just copy the database file:
```bash
cp ~/.if-witness/witness.db /new/location/witness.db
if-witness --db /new/location/witness.db verify
```

Or export to portable formats:
```bash
# JSON is portable
if-witness export --format json --output backup.json

# CSV is spreadsheet-compatible
if-witness export --format csv --output backup.csv
```

### Q3: How do I delete entries?

**A**: **Don't**. IF.witness is append-only by design. Deleting breaks the hash chain.

Instead:
- Export to a new database after a cutoff date
- Start fresh database for new fiscal year
- Archive old data separately

### Q4: Can multiple users share one database?

**A**: Not recommended. Each user should have their own `~/.if-witness/` directory.

If you must share, use file-level permissions:
```bash
chmod 660 ~/.if-witness/witness.db  # Both users can read/write
chmod 770 ~/.if-witness/            # Both can access directory
```

But separate databases are better:
```bash
export IF_WITNESS_DB="/shared/logs/team-witness.db"
```

### Q5: What happens if I lose the database file?

**A**: All witness entries are lost. There's no recovery.

**Prevention**:
- Regular backups: `cp ~/.if-witness/witness.db ~/backups/$(date).db`
- Or export regularly: `if-witness export --format json > backup.json`

### Q6: How accurate is cost tracking?

**A**: As accurate as the input data.

You provide:
- `tokens-in`: Count from LLM API response
- `tokens-out`: Count from LLM API response
- `cost`: Either calculated manually or from API

IF.witness just records what you give it. Verify costs against your API bills.

### Q7: Can I query the database directly?

**A**: Yes, it's SQLite:

```bash
sqlite3 ~/.if-witness/witness.db

# List all entries
SELECT timestamp, component, event, cost_usd FROM witness_entries LIMIT 10;

# Total cost by component
SELECT component, SUM(cost_usd) FROM witness_entries GROUP BY component;

# Most expensive traces
SELECT trace_id, SUM(cost_usd) as total FROM witness_entries
GROUP BY trace_id ORDER BY total DESC LIMIT 5;
```

But use the CLI for most tasks—it's easier and safer.

### Q8: How does the hash chain actually work?

**A**: Each entry includes:
- `prev_hash`: Hash of the previous entry
- `content_hash`: Hash of this entry's content
- `signature`: Ed25519 signature (proves authenticity)

To verify:
1. Recalculate `content_hash` from entry data
2. Compare to stored `content_hash` (detects tampering)
3. Check that previous entry's `content_hash` matches this entry's `prev_hash`
4. Verify signature (proves who created it)

If any step fails, tampering is detected.

### Q9: What model rates are used for cost estimation?

**A**: Check `if-optimise rates` to see current rates:

```bash
if-optimise rates
```

Rates are hardcoded and updated with releases. Actual costs depend on your API pricing—verify against your bills.

### Q10: Can I automate logging?

**A**: Yes! Write scripts that call `if-witness log`:

```bash
#!/bin/bash
# Log every LLM call automatically

log_llm_call() {
  local model=$1
  local tokens_in=$2
  local tokens_out=$3
  local cost=$4

  if-witness log \
    --event "llm_call" \
    --component "app.llm" \
    --trace-id "$(cat /tmp/trace_id)" \
    --payload "{\"model\": \"$model\"}" \
    --tokens-in $tokens_in \
    --tokens-out $tokens_out \
    --cost $cost \
    --model "$model"
}

# Use in your application
log_llm_call "claude-sonnet-4.5" 450 280 0.001234
```

Or integrate into CI/CD:
```yaml
# .github/workflows/track-costs.yml
- name: Log operation cost
  run: |
    if-witness log \
      --event "ci_job" \
      --component "ci.build" \
      --trace-id "${{ github.run_id }}" \
      --payload '{"job": "${{ github.job }}"}' \
      --cost ${{ env.ESTIMATED_COST }}
```

---

## Getting Help

- **Command help**: `if-witness --help`, `if-optimise --help`, `if-cost-monitor --help`
- **Specific command help**: `if-witness log --help`
- **Issues**: Report bugs on GitHub
- **Questions**: Check this guide and the FAQ first

---

## Summary

You now know:
- How to install and configure IF.witness ✓
- Core concepts: witness logging, hash chains, trace IDs ✓
- All available CLI tools and commands ✓
- Real-world workflows and examples ✓
- How to troubleshoot problems ✓
- Best practices for production use ✓

Ready to start? Try the [Quick Start](#quick-start-5-minutes) now!
