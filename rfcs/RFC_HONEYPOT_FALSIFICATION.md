# RFC: Honeypot Falsification Protocol (v0.1)

Status: Draft
Authors: IF.armour working group
Motivation: Break the circular dependency between IF.armour (learner) and IF.witness (falsification oracle) by specifying a falsifier interface and protocol.

## Scope
- Inputs: challenge descriptors (synthetic honey tokens, repo injection points, expected behaviors)
- Outputs: falsification verdicts (valid/invalid), confidence, rationale, evidence links
- Non-goals: training loop details, MARL specifics, reward shaping (handled by learner)

## Interface (JSON Schema outline)
- id (string)
- timestamp (date-time)
- challenge.type (enum: token, config, media)
- environment (enum: local, CI)
- observations[] (strings, redacted)
- verdict (enum: VALID, INVALID, INCONCLUSIVE)
- confidence (0..1)
- evidence[] (path:line or section references)

## Protocol
1) Seed N challenges with tagged honey markers (no exfiltration)
2) Observe repo/tool responses; record observations
3) Produce falsifier verdicts with evidence (evidence-binding required)
4) Feed verdicts to learner as reward signals

## Safety
- No network calls; no live credential validation; redact outputs

## Next Steps
- Define JSON Schema in `schemas/falsifier/v1.0.schema.json`
- Add minimal falsifier runner stub under `tools/falsifier/`
- Connect to IF.armour.honeypot MVP in v2
