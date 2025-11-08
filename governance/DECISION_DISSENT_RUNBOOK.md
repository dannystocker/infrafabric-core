# Decision Dissent Runbook (IF.guard)

Purpose: Turn decision artifacts into operational governance.

1) Create decision JSON (v1.0)
- Required fields: id, timestamp (UTC), submitter, decision (APPROVE/REJECT/CONDITIONAL)
- Optional: dissent[] (names/roles), notes (rationale, conditions)

2) Dissent handling
- If dissent[] non-empty → escalate to review team within 24h
- Review outcome appended to notes with date + reviewer
- If decision flips, create follow-up decision JSON linking prior id

## Dissent Escalation Outcomes

| Scenario | Dissent Level | Outcome | Timeline | Next Steps |
|----------|---------------|---------|----------|------------|
| Consensus reached | 0% dissent | Decision approved | Immediate | Implement immediately |
| Minor dissent | <20% dissent | Approved with notes | 1-2 days | Document concerns, proceed |
| Moderate dissent | 20-40% dissent | Extended review | 1 week | Revision cycle, address concerns |
| Major dissent | 40-60% dissent | Decision paused | 2 weeks | Mediation, find compromise |
| Blocking dissent | >60% dissent | Escalate to council | 1 month | External review, governance decision |

**Examples:**

- **Consensus (0%):** All guardians agree → Immediate approval
- **Minor (<20%):** 1 dissent out of 6 guardians → Note concern, proceed
- **Moderate (20-40%):** 2 dissenters → Revision required, address specific objections
- **Major (40-60%):** 3+ dissenters → Pause, fundamental disagreement
- **Blocking (>60%):** Majority dissent → Requires governance council intervention

See practical example: docs/EXAMPLES/05_governance_simple.sh

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
