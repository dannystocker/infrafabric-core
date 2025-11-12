# Session Parallel: IF.witness CLI + IF.optimise Integration

**Workstream:** Independent (Can run alongside Sessions 1-4)
**Agent:** Claude Sonnet 4.5 OR GPT-5 (Either works)
**Budget:** $15-20, 12-16 hours
**Dependencies:** None (standalone CLI enhancement)

---

## Copy-Paste This Into New Claude Code Session

```
Hi Claude! I need you to enhance the IF.witness CLI with IF.optimise cost tracking.

REPOSITORY: dannystocker/infrafabric
BRANCH: claude/cli-witness-optimise (create from claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy)

CONTEXT: This session is PARALLEL to the real-time communication work.
You're building CLI tools that work independently and will integrate later.

CONTEXT FILES YOU MUST READ FIRST:
1. papers/IF-witness.md (witness philosophy)
2. docs/SWARM-COMMUNICATION-SECURITY.md (Ed25519 signatures)
3. IF_CONNECTIVITY_ARCHITECTURE.md (IF.connect overview)

YOUR TASK: Build IF.witness CLI with provenance, tracing, and cost tracking

DELIVERABLES:
1. src/cli/if-witness.py (~400 lines)
   CLI commands:
   - `if witness log` — Create new witness entry
   - `if witness verify` — Verify hash chain integrity
   - `if witness trace <trace_id>` — Follow full trace chain
   - `if witness cost <trace_id>` — Show token/$ costs (IF.optimise)
   - `if witness export` — Export audit trail (JSON/CSV)

2. src/cli/if-optimise.py (~300 lines)
   Cost tracking:
   - Track tokens per operation
   - Track $ cost per model (GPT/Claude/Gemini rates)
   - Budget alerts ("80% of $100 budget used")
   - Cost attribution by component (IF.yologuard, IF.guard, etc.)

3. docs/CLI-WITNESS-GUIDE.md (user guide)
   - How to use each command
   - Philosophy grounding (IF.ground observability)
   - Example workflows

4. tests/test_cli_witness.py (unit tests)
   - Test hash chain verification
   - Test trace_id propagation
   - Test cost calculation
   - Test export formats

TECHNICAL REQUIREMENTS:
- Language: Python 3.10+
- CLI Framework: Click OR Typer (modern, type-safe)
- Witness Store: SQLite database (simple, embedded)
- Ed25519: cryptography library
- Cost Rates: Hardcode current rates (GPT-5: $0.05/1M tokens, etc.)

PHILOSOPHY GROUNDING:
- IF.witness: Every operation logged with provenance (who, what, when, why)
- IF.ground Principle 8: Observability without fragility
- IF.optimise: Cost-aware operations, budget constraints
- IF.TTT: Traceable (hash chain), Transparent (export), Trustworthy (Ed25519)

WITNESS ENTRY SCHEMA:
```python
@dataclass
class WitnessEntry:
    id: str  # UUID
    timestamp: datetime
    event: str  # "yologuard_scan", "guard_decision", etc.
    component: str  # "IF.yologuard", "IF.guard", etc.
    trace_id: str  # Links related operations
    payload: Dict[str, Any]  # Event-specific data
    prev_hash: str  # Hash of previous entry (chain)
    content_hash: str  # Hash of this entry
    signature: str  # Ed25519 signature
    cost: Optional[Cost]  # Token count, $ amount, model
```

SUCCESS CRITERIA:
✅ `if witness log` creates entry with hash chain
✅ `if witness verify` validates entire chain (no tampering)
✅ `if witness trace <id>` shows full operation path
✅ `if witness cost <id>` shows token + $ breakdown
✅ Hash chain integrity: prev_hash → content_hash → next
✅ Ed25519 signatures verify
✅ Export to JSON + CSV works
✅ Tests pass: logging, verification, tracing, costing

EXAMPLE CLI USAGE:
```bash
# Create witness entry
if witness log \
  --event "yologuard_scan" \
  --component "IF.yologuard" \
  --payload '{"file": "test.py", "secrets_found": 3}' \
  --trace-id "a2f9c3b8d1e5"

# Output:
# ✓ Witness entry created: wit-abc123
# ✓ Hash chain verified (entry 47 → 48)
# ✓ Signature: ed25519:m8QKz5X3jP...

# Verify hash chain
if witness verify

# Output:
# ✓ 48 entries verified
# ✓ Hash chain intact (no tampering)
# ✓ All signatures valid

# Trace operation
if witness trace a2f9c3b8d1e5

# Output:
# Trace: a2f9c3b8d1e5 (IF.yologuard scan → IF.guard review)
#
# 1. [14:32:17] IF.yologuard: scan started (file: test.py)
# 2. [14:32:18] IF.yologuard: 3 secrets detected
# 3. [14:32:19] IF.guard: review requested
# 4. [14:32:47] IF.guard: approved (2 guardians voted)
#
# Duration: 30s | Cost: $0.008 (800 tokens)

# Show cost breakdown
if witness cost a2f9c3b8d1e5

# Output:
# Cost Breakdown (trace: a2f9c3b8d1e5)
#
# Component       Tokens    Cost      Model
# IF.yologuard    200       $0.002    Claude Haiku 4.5
# IF.guard        600       $0.006    Gemini 2.5 Pro
# Total           800       $0.008
#
# Budget: $0.008 / $100.00 (0.01% used)

# Export audit trail
if witness export --format json --output audit-2025-11-11.json
# Output: ✓ Exported 48 entries to audit-2025-11-11.json
```

COST TRACKING (IF.optimise):
```python
# Hardcode current model rates (as of 2025-11-11)
MODEL_RATES = {
    'gpt-5': {'input': 0.00005, 'output': 0.00015},  # per token
    'claude-sonnet-4.5': {'input': 0.000003, 'output': 0.000015},
    'claude-haiku-4.5': {'input': 0.00000025, 'output': 0.00000125},
    'gemini-2.5-pro': {'input': 0.000001, 'output': 0.000005},
}

def calculate_cost(tokens_in: int, tokens_out: int, model: str) -> float:
    rates = MODEL_RATES.get(model, {'input': 0, 'output': 0})
    return (tokens_in * rates['input']) + (tokens_out * rates['output'])
```

BUDGET & TIME:
- Estimated: 12-16 hours
- Cost: ~$15-20
- No blockers (fully independent)

START HERE:
1. Read context files (IF-witness.md most important)
2. Install: `pip install click cryptography`
3. Create SQLite schema (witness_entries table)
4. Implement `if witness log` (core command)
5. Implement hash chain verification
6. Implement `if witness verify`
7. Implement `if witness trace`
8. Implement `if witness cost` (IF.optimise)
9. Write tests
10. Document in CLI-WITNESS-GUIDE.md
11. Commit to claude/cli-witness-optimise

INTEGRATION WITH OTHER SESSIONS:
- Session 1 (NDI): Will call `if witness log` when publishing frames
- Session 2 (WebRTC): Will call `if witness log` for SDP offers
- Session 3 (H.323): Will call `if witness log` for admission control
- Session 4 (SIP): Will call `if witness log` for ESCALATE calls

Your CLI is the **shared audit layer** they all use!

BEGIN!
```

---

## Phase 0: Coordination Protocol (Complete This First!)

**BEFORE implementing, complete Phase 0 coordination:**

### 1. Branch Polling
```bash
# Check current branch status
git status
git branch -a

# Poll for other workstream branches (for awareness - no dependencies)
git fetch --all
git branch -r | grep "claude/realtime-workstream-\|claude/cli-witness"

# Expected branches (eventually):
# - claude/cli-witness-optimise (YOU)
# - claude/realtime-workstream-1-ndi (will use your CLI)
# - claude/realtime-workstream-2-webrtc (will use your CLI)
# - claude/realtime-workstream-3-h323 (will use your CLI)
# - claude/realtime-workstream-4-sip (will use your CLI)
```

### 2. STATUS Reporting Requirements
Create STATUS file on your branch:
```bash
# Create STATUS.md on your branch
cat > STATUS.md <<EOF
# Session Parallel: IF.witness CLI + IF.optimise
**Agent:** Claude Sonnet 4.5 OR GPT-5
**Branch:** claude/cli-witness-optimise
**Status:** PHASE_0_COORDINATION

## Phase 0 Checklist
- [ ] Branch created from base
- [ ] Context files read
- [ ] Dependencies checked (NONE - fully independent)
- [ ] SQLite schema designed
- [ ] Ready to begin implementation

## Current Phase: 0 (Coordination)
**Started:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Blockers:** None
**Next:** Phase 1 (CLI Implementation)
**Note:** This CLI will be used by ALL other workstreams (1-4)

## Milestones
- [ ] Phase 0: Coordination complete
- [ ] Phase 1: if-witness.py CLI commands implemented
- [ ] Phase 2: if-optimise.py cost tracking implemented
- [ ] Phase 3: SQLite database schema created
- [ ] Phase 4: Tests passing (logging, verification, tracing, costing)
- [ ] Phase 5: Documentation complete
- [ ] HANDOFF: CLI ready for integration by Sessions 1-4
EOF

git add STATUS.md
git commit -m "Phase 0: Initialize CLI witness status tracking"
```

### 3. Filler Task Strategy
**Parallel CLI session has NO dependencies** - proceed directly to implementation after Phase 0!

This session is FULLY INDEPENDENT and can run in parallel with Sessions 1-4.

However, if you encounter blockers during implementation:
- Research Click/Typer CLI framework best practices
- Design additional cost attribution reports
- Create export format specifications (JSON/CSV/HTML)
- Document hash chain verification algorithms
- Write performance benchmarks for SQLite queries

### 4. Milestone Reporting
Update STATUS.md after each milestone:
```bash
# After completing each phase, update STATUS.md
sed -i 's/Status:** PHASE_0/Status:** PHASE_1_CLI_IMPLEMENTATION/' STATUS.md
sed -i 's/- \[ \] Phase 0/- [x] Phase 0/' STATUS.md

git add STATUS.md
git commit -m "Milestone: Phase 0 complete, beginning CLI implementation"
```

**IMPORTANT:** Notify other sessions when CLI is ready:
```bash
# After CLI is functional
echo "ALL SESSIONS UNBLOCKED: IF.witness CLI ready for integration" >> STATUS.md
git add STATUS.md
git commit -m "HANDOFF: CLI available for Sessions 1-4"
```

### 5. Phase 0 Completion Checklist
Before moving to implementation:
- ✅ Branch created: `claude/cli-witness-optimise`
- ✅ STATUS.md created and committed
- ✅ All 3 context files read
- ✅ Dependencies verified (NONE - fully independent)
- ✅ SQLite schema designed
- ✅ CLI command structure planned
- ✅ Development plan confirmed
- ✅ Ready to implement

**Phase 0 Complete? Proceed to "SQLite Schema" below and begin implementation!**

---

## SQLite Schema

```sql
-- Database: witness.db
CREATE TABLE witness_entries (
    id TEXT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    event TEXT NOT NULL,
    component TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    payload JSON NOT NULL,
    prev_hash TEXT,
    content_hash TEXT NOT NULL,
    signature TEXT NOT NULL,

    -- Cost tracking (IF.optimise)
    tokens_in INTEGER,
    tokens_out INTEGER,
    cost_usd REAL,
    model TEXT,

    -- Indexes
    INDEX idx_trace_id (trace_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_component (component)
);

-- Verify chain integrity
SELECT
    prev_hash = LAG(content_hash) OVER (ORDER BY timestamp)
FROM witness_entries;
-- All rows should be TRUE
```

---

## Hash Chain Verification Algorithm

```python
def verify_hash_chain(entries: List[WitnessEntry]) -> bool:
    """Verify hash chain integrity"""
    for i in range(1, len(entries)):
        prev_entry = entries[i-1]
        curr_entry = entries[i]

        # Check: curr.prev_hash == prev.content_hash
        if curr_entry.prev_hash != prev_entry.content_hash:
            print(f"❌ Chain broken at entry {i}")
            print(f"   Expected prev_hash: {prev_entry.content_hash}")
            print(f"   Actual prev_hash:   {curr_entry.prev_hash}")
            return False

        # Check: curr.content_hash == hash(curr payload)
        computed_hash = sha256(canonical(curr_entry))
        if curr_entry.content_hash != computed_hash:
            print(f"❌ Content hash mismatch at entry {i}")
            return False

    print(f"✓ {len(entries)} entries verified (chain intact)")
    return True
```

---

## Cost Attribution Report (IF.optimise)

```
$ if witness cost --component IF.yologuard --period 2025-11-01..2025-11-11

IF.optimise Cost Report
Period: 2025-11-01 to 2025-11-11
Component: IF.yologuard

Daily Breakdown:
Date         Operations    Tokens      Cost       Model
2025-11-01   142          14,200      $0.036     Claude Haiku 4.5
2025-11-02   198          19,800      $0.050     Claude Haiku 4.5
2025-11-03   156          15,600      $0.039     Claude Haiku 4.5
...
2025-11-11   201          20,100      $0.050     Claude Haiku 4.5

Total:       1,847        184,700     $0.462

Budget Status: $0.46 / $100.00 (0.46% used)
Projected Monthly: $1.39 (well under budget)
```

---

## Integration Example (From Session 1)

```python
# Session 1 (NDI) will use your CLI like this:
import subprocess

def publish_ndi_frame_with_witness(frame: np.ndarray):
    # Compute hash
    content_hash = hashlib.sha256(frame.tobytes()).hexdigest()

    # Log to IF.witness via CLI
    subprocess.run([
        'if', 'witness', 'log',
        '--event', 'ndi_frame_published',
        '--component', 'IF.witness.ndi-publisher',
        '--payload', json.dumps({
            'frame_number': frame_count,
            'content_hash': content_hash,
            'stream_id': 'IF.yologuard.01'
        }),
        '--trace-id', current_trace_id
    ])

    # Publish NDI frame...
```

---

**Session Start:** [Copy-paste block above into fresh session]
**Session Complete:** Push to `claude/cli-witness-optimise`

**Parallelization Note:** This session runs INDEPENDENTLY of Sessions 1-4.
You can start this immediately without waiting!
