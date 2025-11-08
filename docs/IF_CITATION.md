# IF.citation (v1)

IF.citation formalizes evidence for claims in IF.TTT. It defines a JSON schema, examples, and where to attach citations in IF.yologuard and IF.guard.

## Schema
- File: `schemas/citation/v1.0.schema.json`
- Validate with `tools/citation_validate.py`

## Example
- File: `citations/examples/citation_example.json`

## Integration Points
- IF.yologuard: when writing a manifest (`--manifest`), include a `citation_id` for assertions where possible. See `code/yologuard/src/IF.yologuard_v3.py:1210` for provenance fields.
- IF.guard: decisions may include `citation_ids` (optional) linking to citations that support or dispute claims. See `schemas/decision/v1.0.schema.json`.

## Roadmap
- REST service for storing/verifying citations
- Auto-verifier job to check source hashes and update status
- Decision UI to show linked citations

