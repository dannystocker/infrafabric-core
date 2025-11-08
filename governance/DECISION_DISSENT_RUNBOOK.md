# Decision Dissent Runbook (IF.guard)

Purpose: Turn decision artifacts into operational governance.

1) Create decision JSON (v1.0)
- Required fields: id, timestamp (UTC), submitter, decision (APPROVE/REJECT/CONDITIONAL)
- Optional: dissent[] (names/roles), notes (rationale, conditions)

2) Dissent handling
- If dissent[] non-empty → escalate to review team within 24h
- Review outcome appended to notes with date + reviewer
- If decision flips, create follow-up decision JSON linking prior id

3) Archival
- Store artifacts under governance/decisions/<yyyy-mm>/<id>.json
- Index includes: id, decision, dissent_count, submitter, timestamp

4) Feedback loop
- Monthly: compute dissent rate; feed into risk priors for future decisions
- Dissent taxonomy: policy, performance, ethics, scope

5) CI enforcement (release PRs)
- Validate decision JSON v1.0 schema
- Require no unresolved dissent for release tag

References
- schemas/decision/v1.0.schema.json
- governance/examples/decision_example.json
