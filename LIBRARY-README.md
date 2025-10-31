# InfraFabric Library

**Infrastructure-Level Weighted Coordination**

A Python library implementing weighted coordination mechanisms for multi-agent systems, governance frameworks, and self-improving infrastructure.

## Philosophy

> "The same coordination mechanism that builds the system governs the system"

InfraFabric applies **weighted coordination** (0.0 → 2.0 adaptive weighting) across multiple domains:
- **Agent coordination**: Multi-agent systems with adaptive influence
- **Governance**: Pluridisciplinary oversight with weighted debate
- **Self-documentation**: Manifests with complete provenance
- **Meta-learning**: Late bloomer discovery and self-improvement

## Quick Start

### IF Guardians: Weighted Governance Debate

```python
from infrafabric.guardians import debate_proposal

proposal = {
    'title': 'Persona Agent Pilot',
    'description': 'Use AI to personalize outreach drafts',
    'risks': ['Privacy violation', 'Impersonation'],
    'safeguards': ['Public data only', 'Human review mandatory']
}

result = debate_proposal(proposal, proposal_type='ethical')
print(f"Decision: {result.decision}")  # CONDITIONAL
print(f"Safeguards: {len(result.required_safeguards)}")  # 8
```

## Library Structure

```
infrafabric/
  ├── __init__.py          # Core exports
  ├── guardians.py         # IF Guardians (weighted debate)
  ├── coordination.py      # Weighted agent coordination
  └── manifests.py         # Self-documenting provenance

examples/
  └── guardian_debate_example.py

guardians/
  └── IF-GUARDIANS-CHARTER.md  # Complete governance charter
```

## Testing

```bash
# Run guardian example
python examples/guardian_debate_example.py

# Run batch test
cd marketing/page-zero
python test_batch_simple.py
```

## Documentation

See `IF-GUARDIANS-CHARTER.md` for complete governance framework.

## Status

**Phase 1 Complete:** ✅ Core library, IF Guardians, weighted coordination
**Phase 2 In Progress:** Batch discovery, persona agents, validation

---

**InfraFabric Research | October 2025**
