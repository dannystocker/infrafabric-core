# IF.yologuard v3.1 – Guardian Handoff

## Summary

This handoff requests Guardian approval to publish IF.yologuard v3.1 updates and acknowledge new evaluation scaffolding:

- Aligns benchmark to SecretRedactorV3 with position-aware deduplication
- Implements Confucian 兄弟 (metadata-sibling) relationship
- Adds CLI with JSON + SARIF outputs, severity mapping, and stats mode
- Introduces scan modes: `--mode usable|component|both` and tunable thresholds `--error-threshold/--warn-threshold`
- Adds falsifier checks and GitHub CI workflow with SARIF upload
- Adds FP/Performance harness (clean‑corpus FP estimator, perf benchmark, corpus evaluator)
 - Adds experimental cross‑file linking tool: `tools/cross_file_scan.py` (adds crossfile-sibling relations)

## Evidence

- Benchmark: `code/yologuard/benchmarks/run_leaky_repo_v3_philosophical_fast_v2.py`
  - Result: 107/96 detections (111.5%), 42/42 coverage
- Scorer (usable-only GT): 95/96 (98.96%), 0 FP
- CLI: `code/yologuard/src/IF.yologuard_v3.py`
  - `--json`, `--sarif`, `--out`, `--mode usable|component|both`, `--error-threshold`, `--warn-threshold`, `--stats`
- CI: `.github/workflows/yologuard-ci.yml` (gates on ≥95 detections)
- Falsifier tests: `code/yologuard/tests/test_falsifiers.py`
- Harness: `code/yologuard/harness/README.md`, `fp_eval.py`, `perf_bench.py`, `corpus_eval.py`
- Cross-file tool: `code/yologuard/tools/cross_file_scan.py`
- Benchmarks & Comparison: `code/yologuard/docs/BENCHMARKS.md`, `code/yologuard/docs/COMPARISON.md`

### Initial Harness Readouts (Repeatable)
- Perf (host repo snapshot): ~116 files/sec, ~3.55 MB/sec (includes benchmark data)
- Public corpus (requests+flask): 349 files, 73 detections total; ~454 files/sec (tests/examples may contribute)

## Risks

- Overreach increasing FP on novel repos
- Severity thresholds may require tuning across environments
- Component vs usable philosophy differences can cause confusion
 - Single‑file relationship scope; cross‑file linking is not yet implemented

## Safeguards

- Redaction guaranteed; no raw secrets logged
- Falsifier suite blocks common near-misses
- CI gate with SARIF upload to code scanning
- Classification and relationship confidence included in outputs
 - Heuristics are explicitly tunable via CLI thresholds; calibration to follow FP/perf data

## Roadmap Commitments (Post‑Approval)
- Publish FP rates using curated clean corpus across multiple ecosystems
- Publish large‑repo performance metrics and add streaming for very large files
- Implement cross‑file relationship linking (env/config interpolation and usage)
- Expand competitor comparisons with measured head‑to‑head results

## Governance Note
- IF.ceo (not IF.sam) is the correct name for the executive strategic spectrum referenced in council docs.

## How to Run the Debate

```bash
python3 infrafabric/code/yologuard/integration/guardian_handoff.py
# Output: integration/guardian_handoff_result.json
```
