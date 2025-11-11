# IF.witness CLI User Guide

**Version:** 1.0
**Date:** 2025-11-11
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Philosophy](#philosophy)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [CLI Commands](#cli-commands)
6. [Workflow Examples](#workflow-examples)
7. [Integration Guide](#integration-guide)
8. [Troubleshooting](#troubleshooting)

---

## Overview

IF.witness is a provenance and audit trail system for InfraFabric operations. It provides:

- **Provenance tracking**: Every operation logged with who, what, when, why
- **Hash chain integrity**: Tamper-proof audit logs using SHA-256 chains
- **Cryptographic signatures**: Ed25519 signatures prove authenticity
- **Cost tracking**: Token usage and $ costs via IF.optimise integration
- **Trace propagation**: Link related operations across components

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  IF.witness CLI (if-witness.py, if-optimise.py)         │
├─────────────────────────────────────────────────────────┤
│  Witness Database (SQLite + Ed25519 + Hash Chains)     │
├─────────────────────────────────────────────────────────┤
│  Components: IF.yologuard, IF.guard, IF.swarm, etc.    │
└─────────────────────────────────────────────────────────┘
```

---

## Philosophy

IF.witness implements **IF.ground Principle 8: Observability without fragility**.

### Core Principles

1. **Observable Artifacts** (IF.ground Principle 1)
   - Every operation creates a witness entry
   - All entries have cryptographic proof (signatures + hashes)

2. **Tamper-Proof Logging** (SWARM-COMMUNICATION-SECURITY.md)
   - Hash chains prevent retroactive modification
   - Ed25519 signatures prove authenticity
   - Merkle-tree style verification

3. **Warrant Canary Epistemology** (IF.witness paper)
   - Making unknowns explicit through observable absence
   - Dead canary = known compromise (vs unknown state)

4. **IF.TTT Compliance** (Traceable, Transparent, Trustworthy)
   - Traceable: Every message → signature → public key → agent identity
   - Transparent: All entries logged and replayable
   - Trustworthy: Cryptographic verification (not just policy)

---

## Installation

### Prerequisites

```bash
# Python 3.10+
python3 --version

# Install dependencies
pip install click cryptography
```

### Setup

```bash
# Clone repository
git clone https://github.com/dannystocker/infrafabric.git
cd infrafabric

# Add to PATH (optional)
export PATH="$PATH:$(pwd)/src/cli"

# Make executables
chmod +x src/cli/if-witness.py
chmod +x src/cli/if-optimise.py

# Initialize witness database (creates ~/.if-witness/)
./src/cli/if-witness.py verify
```

### Directory Structure

```
~/.if-witness/
├── witness.db          # SQLite database
├── private_key.pem     # Ed25519 private key (600 permissions)
├── public_key.pem      # Ed25519 public key
└── budget.json         # Budget configuration (IF.optimise)
```

---

## Quick Start

### Create Your First Witness Entry

```bash
# Log an operation
./src/cli/if-witness.py log \
  --event "yologuard_scan" \
  --component "IF.yologuard" \
  --trace-id "a2f9c3b8d1e5" \
  --payload '{"file": "test.py", "secrets_found": 3}'

# Output:
# ✓ Witness entry created: wit-abc123
# ✓ Hash chain verified (entry 0 → 1)
# ✓ Signature: ed25519:m8QKz5X3jP...
# ✓ Content hash: 5a3d2f8c1b9e7d...
```

### Verify Hash Chain

```bash
./src/cli/if-witness.py verify

# Output:
# ✓ 1 entries verified
# ✓ Hash chain intact (no tampering)
# ✓ All signatures valid
```

### View a Trace

```bash
./src/cli/if-witness.py trace a2f9c3b8d1e5

# Output:
# Trace: a2f9c3b8d1e5
# Components: IF.yologuard
#
# 1. [14:32:17] IF.yologuard: yologuard_scan
#    Payload: {"file": "test.py", "secrets_found": 3}
#
# Duration: 0.00s
# Total Cost: $0.000000 (0 tokens)
```

---

## CLI Commands

### if-witness.py

#### `log` - Create Witness Entry

Create a new witness entry with hash chain and signature.

```bash
./src/cli/if-witness.py log \
  --event <event_type> \
  --component <component_name> \
  --trace-id <trace_id> \
  --payload <json_payload> \
  [--tokens-in <int>] \
  [--tokens-out <int>] \
  [--cost <float>] \
  [--model <model_name>]
```

**Arguments:**
- `--event`: Event type (e.g., `yologuard_scan`, `guard_decision`)
- `--component`: Component name (e.g., `IF.yologuard`, `IF.guard`)
- `--trace-id`: Trace ID linking related operations
- `--payload`: Event-specific data as JSON string
- `--tokens-in`: Input tokens used (optional, for cost tracking)
- `--tokens-out`: Output tokens used (optional)
- `--cost`: Cost in USD (optional)
- `--model`: Model used (optional, e.g., `claude-sonnet-4.5`)

**Example:**
```bash
./src/cli/if-witness.py log \
  --event "ndi_frame_published" \
  --component "IF.witness.ndi-publisher" \
  --trace-id "session-1-frame-42" \
  --payload '{"frame_number": 42, "content_hash": "5a3d2f8c..."}' \
  --tokens-in 200 \
  --tokens-out 50 \
  --cost 0.0005 \
  --model "claude-haiku-4.5"
```

#### `verify` - Verify Hash Chain

Verify integrity of entire witness chain.

```bash
./src/cli/if-witness.py verify [--db <path>]
```

**Example:**
```bash
./src/cli/if-witness.py verify

# Output:
# ✓ 48 entries verified
# ✓ Hash chain intact (no tampering)
# ✓ All signatures valid
```

#### `trace` - Follow Trace Chain

Retrieve all entries for a specific trace ID.

```bash
./src/cli/if-witness.py trace <trace_id> [--format text|json]
```

**Arguments:**
- `trace_id`: Trace ID to query
- `--format`: Output format (text or json, default: text)

**Example (text format):**
```bash
./src/cli/if-witness.py trace a2f9c3b8d1e5

# Output:
# Trace: a2f9c3b8d1e5 (IF.yologuard scan → IF.guard review)
#
# 1. [14:32:17] IF.yologuard: scan started (file: test.py)
# 2. [14:32:18] IF.yologuard: 3 secrets detected
# 3. [14:32:19] IF.guard: review requested
# 4. [14:32:47] IF.guard: approved (2 guardians voted)
#
# Duration: 30s | Cost: $0.008 (800 tokens)
```

**Example (json format):**
```bash
./src/cli/if-witness.py trace a2f9c3b8d1e5 --format json

# Output: JSON with complete trace data
```

#### `cost` - Show Cost Breakdown

Display token usage and costs.

```bash
./src/cli/if-witness.py cost \
  [--trace-id <trace_id>] \
  [--component <component>] \
  [--start-date <YYYY-MM-DD>] \
  [--end-date <YYYY-MM-DD>] \
  [--format text|json]
```

**Example (by trace):**
```bash
./src/cli/if-witness.py cost --trace-id a2f9c3b8d1e5

# Output:
# Cost Breakdown (trace: a2f9c3b8d1e5)
#
# Component       Tokens    Cost      Model
# IF.yologuard    200       $0.002    Claude Haiku 4.5
# IF.guard        600       $0.006    Gemini 2.5 Pro
# Total           800       $0.008
```

**Example (by component):**
```bash
./src/cli/if-witness.py cost --component IF.yologuard

# Output:
# Cost Breakdown by Component
#
# Component       Operations    Tokens      Cost
# IF.yologuard    142          14,200      $0.036
```

#### `export` - Export Audit Trail

Export witness entries to JSON or CSV.

```bash
./src/cli/if-witness.py export \
  [--format json|csv] \
  [--output <file_path>]
```

**Example (JSON):**
```bash
./src/cli/if-witness.py export --format json --output audit-2025-11-11.json

# Output: ✓ Exported 48 entries to audit-2025-11-11.json
```

**Example (CSV):**
```bash
./src/cli/if-witness.py export --format csv --output audit-2025-11-11.csv

# Output: ✓ Exported 48 entries to audit-2025-11-11.csv
```

---

### if-optimise.py

#### `rates` - Show Model Rates

Display current token pricing for all models.

```bash
./src/cli/if-optimise.py rates [--format text|json]
```

**Example:**
```bash
./src/cli/if-optimise.py rates

# Output:
# Current Model Rates (per token)
#
# Model                     Input           Output
# gpt-5                     $0.00005000     $0.00015000
# claude-sonnet-4.5         $0.00000300     $0.00001500
# claude-haiku-4.5          $0.00000025     $0.00000125
# gemini-2.5-pro            $0.00000100     $0.00000500
```

#### `budget` - Budget Management

Set and monitor budget limits.

```bash
./src/cli/if-optimise.py budget \
  [--set <amount>] \
  [--period day|week|month] \
  [--component <component>]
```

**Example (set budget):**
```bash
./src/cli/if-optimise.py budget --set 100.0 --period month

# Output:
# ✓ Budget set: $100.00 per month
#
# Budget Status (month)
# Period:       2025-11-01 - 2025-11-11
# Budget:       $100.00
# Spent:        $0.462000
# Remaining:    $99.538000
# Usage:        0.46%
```

**Example (check budget):**
```bash
./src/cli/if-optimise.py budget

# Output shows current spending against budget
```

#### `report` - Generate Cost Reports

Generate detailed cost reports with grouping.

```bash
./src/cli/if-optimise.py report \
  [--component <component>] \
  [--start-date <YYYY-MM-DD>] \
  [--end-date <YYYY-MM-DD>] \
  [--group-by component|model|day] \
  [--format text|json]
```

**Example:**
```bash
./src/cli/if-optimise.py report --group-by component

# Output:
# IF.optimise Cost Report
# Group by: component
#
# Component       Operations    Tokens        Cost
# IF.yologuard    142          14,200        $0.036000
# IF.swarm        25           12,500        $0.125000
# IF.guard        10           5,000         $0.050000
# Total           177          31,700        $0.211000
```

#### `estimate` - Estimate Costs

Estimate costs for planned operations.

```bash
./src/cli/if-optimise.py estimate \
  --tokens-in <int> \
  --tokens-out <int> \
  --model <model> \
  [--operations <int>]
```

**Example:**
```bash
./src/cli/if-optimise.py estimate \
  --tokens-in 1000 \
  --tokens-out 500 \
  --model claude-haiku-4.5 \
  --operations 100

# Output:
# Cost Estimate
# Model:          claude-haiku-4.5
# Input tokens:   1,000
# Output tokens:  500
# Total tokens:   1,500
# Cost per op:    $0.000876
# Operations:     100
# Total cost:     $0.087600
```

---

## Workflow Examples

### Example 1: IF.yologuard Secret Detection

```bash
# 1. Start scan (creates trace)
TRACE_ID="scan-$(date +%s)"

./src/cli/if-witness.py log \
  --event "yologuard_scan_started" \
  --component "IF.yologuard" \
  --trace-id "$TRACE_ID" \
  --payload '{"file": "config.yaml", "line_count": 150}'

# 2. Log detection
./src/cli/if-witness.py log \
  --event "secret_detected" \
  --component "IF.yologuard" \
  --trace-id "$TRACE_ID" \
  --payload '{"pattern": "aws_access_key", "line": 42, "severity": "HIGH"}' \
  --tokens-in 200 \
  --tokens-out 50 \
  --cost 0.0005 \
  --model "claude-haiku-4.5"

# 3. Request guardian review
./src/cli/if-witness.py log \
  --event "guard_review_requested" \
  --component "IF.guard" \
  --trace-id "$TRACE_ID" \
  --payload '{"guardians": ["Truth", "Science"], "threshold": 0.75}'

# 4. Log guardian decision
./src/cli/if-witness.py log \
  --event "guard_decision" \
  --component "IF.guard" \
  --trace-id "$TRACE_ID" \
  --payload '{"decision": "approve", "votes": {"Truth": 1.0, "Science": 1.0}}'

# 5. View complete trace
./src/cli/if-witness.py trace "$TRACE_ID"

# 6. Check costs
./src/cli/if-witness.py cost --trace-id "$TRACE_ID"
```

### Example 2: IF.swarm Multi-Agent Consensus

```bash
TRACE_ID="swarm-vote-$(uuidgen)"

# 1. Swarm voting starts
./src/cli/if-witness.py log \
  --event "swarm_vote_started" \
  --component "IF.swarm" \
  --trace-id "$TRACE_ID" \
  --payload '{"question": "Is pattern safe?", "voters": 8}'

# 2. Each agent logs its vote (8 agents)
for i in {1..8}; do
  ./src/cli/if-witness.py log \
    --event "agent_vote" \
    --component "IF.swarm.agent-$i" \
    --trace-id "$TRACE_ID" \
    --payload "{\"vote\": $(shuf -i 0-1 -n 1), \"confidence\": 0.8}" \
    --tokens-in 100 \
    --tokens-out 50 \
    --cost 0.00015 \
    --model "claude-haiku-4.5"
done

# 3. Consensus reached
./src/cli/if-witness.py log \
  --event "swarm_consensus" \
  --component "IF.swarm" \
  --trace-id "$TRACE_ID" \
  --payload '{"consensus": 0.875, "decision": "approve"}'

# 4. View trace
./src/cli/if-witness.py trace "$TRACE_ID"
```

### Example 3: Cost Monitoring

```bash
# Set monthly budget
./src/cli/if-optimise.py budget --set 100 --period month

# Run operations...
# (witness entries with cost data)

# Check budget status
./src/cli/if-optimise.py budget

# Generate weekly report
./src/cli/if-optimise.py report \
  --start-date "2025-11-04" \
  --end-date "2025-11-11" \
  --group-by component

# Estimate upcoming operation
./src/cli/if-optimise.py estimate \
  --tokens-in 5000 \
  --tokens-out 2000 \
  --model claude-sonnet-4.5 \
  --operations 10
```

---

## Integration Guide

### Python Integration

```python
#!/usr/bin/env python3
import sys
import json
import subprocess
from pathlib import Path

# Add witness module to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from witness.database import WitnessDatabase
from witness.models import Cost

# Option 1: Direct Python API
db = WitnessDatabase()

entry = db.create_entry(
    event='custom_operation',
    component='my-component',
    trace_id='trace-123',
    payload={'result': 'success'},
    cost=Cost(tokens_in=100, tokens_out=50, cost_usd=0.001, model='claude-haiku-4.5')
)

print(f"Created entry: {entry.id}")
db.close()

# Option 2: CLI subprocess (for external integration)
def log_witness(event, component, trace_id, payload):
    subprocess.run([
        'python3', 'src/cli/if-witness.py', 'log',
        '--event', event,
        '--component', component,
        '--trace-id', trace_id,
        '--payload', json.dumps(payload)
    ], check=True)

log_witness(
    event='api_call',
    component='IF.api',
    trace_id='api-trace-1',
    payload={'endpoint': '/scan', 'status': 200}
)
```

### Bash Integration

```bash
#!/bin/bash

# Function to log witness entries
log_witness() {
  local event="$1"
  local component="$2"
  local trace_id="$3"
  local payload="$4"

  python3 src/cli/if-witness.py log \
    --event "$event" \
    --component "$component" \
    --trace-id "$trace_id" \
    --payload "$payload"
}

# Usage
TRACE_ID="deploy-$(date +%s)"

log_witness "deployment_started" "IF.deploy" "$TRACE_ID" '{"version": "4.2.0"}'
log_witness "tests_passed" "IF.deploy" "$TRACE_ID" '{"tests": 47, "failures": 0}'
log_witness "deployment_complete" "IF.deploy" "$TRACE_ID" '{"status": "success"}'

# View trace
python3 src/cli/if-witness.py trace "$TRACE_ID"
```

### Session Integration (Sessions 1-4)

```python
# Session 1 (NDI): Log frame publishing
import hashlib

def publish_ndi_frame_with_witness(frame, trace_id):
    # Compute hash
    content_hash = hashlib.sha256(frame.tobytes()).hexdigest()

    # Log to witness
    subprocess.run([
        'python3', 'src/cli/if-witness.py', 'log',
        '--event', 'ndi_frame_published',
        '--component', 'IF.witness.ndi-publisher',
        '--payload', json.dumps({
            'frame_number': frame_count,
            'content_hash': content_hash,
            'stream_id': 'IF.yologuard.01'
        }),
        '--trace-id', trace_id
    ])

    # Publish NDI frame...
```

---

## Troubleshooting

### Issue: Hash Chain Broken

```bash
$ ./src/cli/if-witness.py verify
❌ Verification failed: Entry 5 (wit-xyz): Hash chain broken (prev_hash mismatch)
```

**Cause:** Database corruption or manual modification

**Solution:**
1. Export existing data: `./src/cli/if-witness.py export --format json --output backup.json`
2. Investigate which entry was modified
3. Restore from backup or start fresh

### Issue: Invalid Signature

```bash
❌ Entry 3 (wit-abc): Invalid signature
```

**Cause:** Ed25519 key mismatch or corrupted entry

**Solution:**
1. Check key files: `ls -la ~/.if-witness/*.pem`
2. Verify key permissions: `chmod 600 ~/.if-witness/private_key.pem`
3. If keys are lost, database must be rebuilt

### Issue: Missing Dependencies

```bash
ModuleNotFoundError: No module named 'click'
```

**Solution:**
```bash
pip install click cryptography
```

### Issue: Permission Denied

```bash
PermissionError: [Errno 13] Permission denied: '/home/user/.if-witness/witness.db'
```

**Solution:**
```bash
chmod 644 ~/.if-witness/witness.db
chmod 700 ~/.if-witness/
```

---

## Security Considerations

### Private Key Protection

The Ed25519 private key (`~/.if-witness/private_key.pem`) must be protected:

```bash
# Correct permissions
chmod 600 ~/.if-witness/private_key.pem

# Check permissions
ls -la ~/.if-witness/private_key.pem
# Should show: -rw------- (600)
```

**Never:**
- Commit private keys to git
- Share private keys across machines
- Store in world-readable directories

### Database Security

```bash
# Secure database directory
chmod 700 ~/.if-witness/

# Backup database regularly
cp ~/.if-witness/witness.db ~/backups/witness-$(date +%Y%m%d).db
```

### Audit Log Integrity

The hash chain prevents tampering, but:
1. **Backup regularly**: Use `if-witness export`
2. **Monitor verify output**: Run `if-witness verify` in cron jobs
3. **Alert on failures**: Integration with monitoring systems

---

## Performance

### Database Size

- Average entry: ~1-2 KB (with payload)
- 1M entries: ~1-2 GB database
- SQLite handles billions of rows efficiently

### Query Performance

- `verify`: O(n) - must check all entries
- `trace`: O(log n) - indexed by trace_id
- `cost`: O(log n) - indexed by component/timestamp

### Optimization Tips

```bash
# 1. Vacuum database periodically (reclaim space)
sqlite3 ~/.if-witness/witness.db "VACUUM;"

# 2. Analyze for query optimization
sqlite3 ~/.if-witness/witness.db "ANALYZE;"

# 3. Archive old entries (export + delete)
./src/cli/if-witness.py export --format json --output archive-2024.json
# (then delete old entries manually via SQL)
```

---

## References

- **IF.witness Paper**: `papers/IF-witness.md`
- **SWARM-COMMUNICATION-SECURITY**: `docs/SWARM-COMMUNICATION-SECURITY.md`
- **IF_CONNECTIVITY_ARCHITECTURE**: `IF_CONNECTIVITY_ARCHITECTURE.md`
- **Ed25519 Spec**: RFC 8032 (https://tools.ietf.org/html/rfc8032)
- **SQLite Docs**: https://www.sqlite.org/docs.html

---

**Version:** 1.0
**Last Updated:** 2025-11-11
**Maintainer:** Danny Stocker (danny.stocker@gmail.com)
**License:** See LICENSE-CODE
