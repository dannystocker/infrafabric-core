# IF.witness & IF.optimise CLI

Command-line tools for InfraFabric provenance tracking and cost optimization.

## Quick Start

```bash
# Create witness entry
python3 src/cli/if-witness.py log \
  --event "yologuard_scan" \
  --component "IF.yologuard" \
  --trace-id "trace-123" \
  --payload '{"file": "test.py"}' \
  --tokens-in 100 \
  --tokens-out 50 \
  --cost 0.001 \
  --model "claude-haiku-4.5"

# Verify hash chain
python3 src/cli/if-witness.py verify

# View trace
python3 src/cli/if-witness.py trace trace-123

# Check costs
python3 src/cli/if-optimise.py rates
python3 src/cli/if-optimise.py budget --set 100 --period month
```

## Documentation

See [docs/CLI-WITNESS-GUIDE.md](../../docs/CLI-WITNESS-GUIDE.md) for complete documentation.

## Features

### if-witness.py
- ✅ Hash chain verification (SHA-256)
- ✅ Ed25519 cryptographic signatures
- ✅ Trace ID propagation
- ✅ SQLite database storage
- ✅ JSON/CSV export

### if-optimise.py
- ✅ Token usage tracking
- ✅ Cost calculation (GPT-5, Claude, Gemini)
- ✅ Budget management
- ✅ Cost reports and estimates

## Tests

```bash
python3 tests/test_cli_witness.py

# Output: 15 tests, all passing
# - Hash chain verification
# - Signature validation
# - Trace propagation
# - Cost tracking
# - Export formats
```

## Philosophy

Implements IF.ground Principle 8: **Observability without fragility**

Every operation creates a tamper-proof audit entry with:
- **Provenance**: Who, what, when, why
- **Integrity**: Hash chains prevent tampering
- **Authenticity**: Ed25519 signatures prove identity
- **Traceability**: Link related operations across components

## Architecture

```
src/
├── cli/
│   ├── if-witness.py     (~400 lines) - Main CLI
│   └── if-optimise.py    (~300 lines) - Cost tracking
└── witness/
    ├── models.py         - Data models (WitnessEntry, Cost)
    ├── crypto.py         - Ed25519 signatures, hash chains
    └── database.py       - SQLite operations
```

## Integration

Used by Sessions 1-4 for real-time communication provenance:
- Session 1 (NDI): Log frame publishing
- Session 2 (WebRTC): Log SDP offers
- Session 3 (H.323): Log admission control
- Session 4 (SIP): Log ESCALATE calls

This CLI is the **shared audit layer** for all IF components.
