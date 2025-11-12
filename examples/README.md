# InfraFabric Examples

This directory contains working examples demonstrating key InfraFabric concepts and components.

## Examples

### IF.witness Hash Chain

**File:** `if-witness-coordination-hash-chain.py`

**Purpose:** Demonstrates how IF.witness tracks Phase 0 coordination operations with cryptographic hash chains for traceability and tamper-detection.

**What It Shows:**
- Task claim event tracking (IF.coordinator)
- Task execution lifecycle events
- Hash chain verification
- Tampering detection
- Ed25519 signature verification

**Run:**
```bash
python3 examples/if-witness-coordination-hash-chain.py
```

**Output:** Demonstrates 5 coordination events with full hash chain verification and tampering detection.

**Key Concepts:**
- **Hash Chain:** Each event links to previous event via cryptographic hash
- **Ed25519 Signatures:** All events signed for authenticity
- **Tamper Detection:** Any modification to past events breaks the chain
- **IF.TTT Compliance:** Full traceability, transparency, and trustworthiness

**Related Docs:**
- `docs/components/IF.WITNESS.md` (when available)
- `docs/SWARM-OF-SWARMS-ARCHITECTURE.md` - Section "IF.TTT Compliance at Scale"
- `docs/ONBOARDING.md` - Section 7 "Security, Compliance, and Never Do List"

---

## Running Examples

All examples are self-contained and require only Python 3.8+:

```bash
# Run all examples
for example in examples/*.py; do
    echo "Running $example..."
    python3 "$example"
    echo ""
done
```

---

## Contributing Examples

When adding new examples:

1. **Self-contained:** Example should run without external dependencies
2. **Documented:** Include docstring explaining purpose and concepts
3. **Tested:** Verify example runs successfully
4. **Educational:** Focus on teaching key concepts, not production code
5. **IF.TTT compliant:** Demonstrate traceability and provenance

**Example template:**
```python
#!/usr/bin/env python3
"""
Example Title

Purpose: What this example demonstrates

Key Concepts:
- Concept 1
- Concept 2

Reference: Link to related documentation
"""

# Example code here

if __name__ == "__main__":
    demo_function()
```

---

## Examples Roadmap

Future examples to add:

- [ ] **IF.coordinator atomic CAS operations** - Demonstrate race-free task claiming
- [ ] **IF.governor capability matching** - Show smart resource allocation
- [ ] **IF.chassis WASM sandboxing** - Demonstrate isolated execution
- [ ] **Multi-session coordination** - Show cross-session help protocol
- [ ] **Cost tracking with IF.optimise** - Budget enforcement example
- [ ] **Reputation system** - SLO-based reputation scoring

---

**Questions?** See `docs/ONBOARDING.md` for getting started guide.
