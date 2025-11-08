# RFC: Philosophy Tags in Messages and Decisions (v0.1)

Goal: Allow optional `principles` annotations so modules can declare which philosophical principles influenced outputs.

## Proposal
- IFMessage extension (non-breaking): `meta.principles: ["wulun", "popper", ...]`
- Decision JSON extension: `principles: ["popper", "kant"]`

## Benefits
- Traceability: reviewers see which principles guided decisions
- Analytics: measure principle application over time

## Backwards Compatibility
- Optional fields; schema v1.0 remains valid; introduce v1.1 when enforced

## Next Steps
- Define `schemas/philosophy/taxonomy.json` (provided)
- Add examples and doc references
- Pilot annotations in governance examples and IFMessage samples
