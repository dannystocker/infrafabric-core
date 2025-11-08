# IF.yologuard Benchmarks (Initial)

This document summarizes current, reproducible numbers and early measurements. Values will evolve with FP/perf harness results and tuning.

## Standard Dataset

- Dataset: `benchmarks/leaky-repo/` (49 files; GT=96 usable secrets)
- Fast benchmark runner: `benchmarks/run_leaky_repo_v3_philosophical_fast_v2.py`
- Results:
  - Detected: 107/96 (111.5%) — component-inclusive (GitHub-aligned)
  - Coverage: 42/42 files
  - Usable-only (GT-style) scorer: 95/96 (98.96%), 0 FP on GT

## Repository Performance Snapshot

- Host repo: `infrafabric` (includes benchmark data; not a clean corpus)
- Tool: `harness/perf_bench.py --root infrafabric`
- Results:
  - files_scanned: 471
  - bytes_scanned: ~13.34 MB
  - detections: 497 (due to embedded benchmark files)
  - duration_sec: ~4.04
  - files_per_sec: ~116.55
  - MB_per_sec: ~3.55

## Public Corpus (Early FP/Perf Survey)

Note: These are public repos used for preliminary signal. They contain tests and examples that may legitimately resemble credentials. Treat detections as “security-relevant” signals, not confirmed FPs. A curated clean corpus is forthcoming.

- Tool: `harness/corpus_eval.py --workdir /tmp/yolo-corpus`
- Repos (shallow clone):
  - psf/requests
  - pallets/flask
- Results:
  - requests
    - files: 120; bytes: ~3.7 MB; detections: 54; duration: ~0.67s; ~178 files/s; ~5.5 MB/s
  - flask
    - files: 229; bytes: ~1.3 MB; detections: 19; duration: ~0.31s; ~730 files/s; ~4.4 MB/s
  - Summary: 349 files; 73 total detections; avg ~454 files/s

## Notes & Next Steps

- Severity thresholds and relationship weights are heuristic defaults, exposed via CLI for tuning.
- We will curate a clean corpus across multiple ecosystems to measure FP rates properly and publish per-repo and aggregate metrics.
- Performance numbers will be repeated with larger repos and streaming reads for large files.
- Head-to-head comparisons with TruffleHog / GitGuardian / GHAS are planned once we establish a shared testbed.

