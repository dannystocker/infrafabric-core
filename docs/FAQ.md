# FAQ (Beginners)

## It found too many things in docs/examples!
Use `--profile ci` on source dirs only (e.g., `src/`, `app/`, `lib/`). Reserve `--profile forensics` for audits.

## What do the "relationship" messages mean?
They indicate nearby items (e.g., username and password in the same file). Higher scores usually mean higher severity.

## Why is PQ experimental?
Post-quantum checks are early heuristics. They are informational only and should not block releases.

## How do I get a simple output?
Use `--beginner-mode` or `--simple-output --format json-simple`.

## Where are governance decisions stored?
See governance/examples/decision_example.json and the runbook in governance/DECISION_DISSENT_RUNBOOK.md.
