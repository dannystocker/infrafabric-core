# IF.yologuard v3.1.1 — Update Brief for External Reviewers

Date: 2025‑11‑08
Repo: infrafabric (branch: master)

## What Changed Since Your Last Review

This brief summarizes focused changes landed for v3.1.1 and the new forensics profile (IEF) + TTT additions. All prior benchmark claims remain reproducible.

### Quality/Safety
- .gitignore added (filters `__pycache__/`, `*.pyc`, `.venv*`, `.venv_tools/`, `code/yologuard/reports/`, benchmark artifacts)
- Threshold/file‑cap constants (no magic numbers)
- Optional regex timeout via `regex` module (20ms per pattern); safe fallback to stdlib `re`
- Binary sniff pre‑check (skip likely binary files before text parsing)

### TTT (Traceability • Trust • Transparency)
- Per‑detection provenance (repo commit, file sha256, scan timestamp)
- Rationale array (pattern, classification, relations, relation_score, thresholds, two_source flag)
- Run manifest flag: `--manifest <file>` (records config/inputs/results and quantum summary)

### IEF (Immuno‑Epistemic Forensics) – v1
- `--forensics` profile/mode (or `--profile forensics`)
- Danger signals: `encoded_blob_in_text`, `honeypot_marker`
- Structure checks: JWT structure validity, PEM block presence (sandbox‑only; no exfiltration)
- Indra graph output: `--graph-out indra.json` (nodes: file/antigen; edges: contains/relation/danger)

### Quantum Readiness (PQ) – v1 (Experimental)
- `--pq-report <file>` produces a quantum exposure summary; `--sbom <path>` best‑effort hints
- `pqRisk` per detection (algorithms/protocols, QES score/drivers)
- Manifest includes repo‑level PQ summary

### Audience Profiles
- `--profile ci|ops|audit|research|forensics` (ci=usable‑only PR gate; forensics=full context)

## Reproducible Artifacts (Fresh)

Run set 1 (bench/verify/perf): `code/yologuard/reports/20251108T020047Z/`
- `bench_fast.json` / `.sarif` — 107/96 detections; coverage 42/42 (component‑inclusive)
- `verify.log` — PASS (≥95)
- `perf_infrafabric.json` — ~116 files/sec; ~3.55 MB/sec (host repo snapshot)

Run set 2 (head‑to‑head corpus): `code/yologuard/reports/20251108T020506Z/`
- `head2head.md` — IF vs Gitleaks (TruffleHog default showed 0 in this corpus); IF surfaces more context‑relevant signals

## How to Re‑Run Quickly

```bash
cd infrafabric
# CI/PR gate (low noise)
python3 code/yologuard/src/IF.yologuard_v3.py \
  --scan code/yologuard/benchmarks/leaky-repo \
  --profile ci \
  --sarif results.sarif \
  --manifest run.manifest \
  --stats

# Forensics profile (context + graph + manifest + PQ)
python3 code/yologuard/src/IF.yologuard_v3.py \
  --scan code/yologuard/benchmarks/leaky-repo \
  --profile forensics \
  --json ief.json \
  --sarif ief.sarif \
  --graph-out indra.json \
  --manifest ief.manifest \
  --pq-report pq.json \
  --stats

# Fast benchmark (component‑inclusive reference)
code/yologuard/verification/verify.sh
```

## Notes for Reviewers
- TTT: Designed for auditability (provenance + rationale + manifest)
- IEF: Adds investigative context (danger signals, structure checks, graph); no network calls
- PQ: Marked experimental in README; early heuristics now captured in manifest/PQ report
- Profiles: Use `ci` for PR gates; `forensics` for weekly audits; thresholds/file caps are configurable

## Recommended Review Focus
1) Does TTT satisfy traceability requirements for CI/GRC?
2) Do IEF signals (danger/structure/graph) improve triage without adding noise?
3) Are `ci` and `forensics` profiles appropriate defaults for PRs vs weekly audits?
4) Are PQ disclaimers and outputs appropriately labeled and useful at this stage?

Thank you for the re‑review.
