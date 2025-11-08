# External Reviewer Sync — Claude Sonnet 4.5 (2025‑11‑08)

This document captures Claude’s verification of v3.1.1 and the agreed adjustments to the 7‑day plan.

## Verification Summary
- Commits: 53bf0b6 (v3.1.1 fixes), bb09ca0 (docs) present on `master` (origin/HEAD)
- Benchmark: 107/96 detections (111.5%), 42/42 coverage — reproduced, no regressions
- Forensics end‑to‑end: JSON, SARIF, graph, manifest, PQ all generated successfully
- Detected counts: 107 total (99 usable, 8 components)
- Minor: datetime.utcnow() deprecation noted → fixed to timezone‑aware UTC in v3.1.1+1

## Adjusted 7‑Day Plan (Claude’s Priority Reorder)
1) Days 1–3 — FP corpus + precision metrics (CRITICAL)
   - Curate 50+ clean OSS repos (Apache/LF/CNCF)
   - Run `harness/fp_eval.py` and `harness/head2head.py`
   - Deliverable: `reports/FP_CORPUS_RESULTS.md` (precision, FP rate) + JSON/MD

2) Day 4 — Tests + CI (ESSENTIAL)
   - pytest integration tests (empty/binary/large/unicode, perf budget)
   - GitHub Action: lint → tests → benchmark gate (>=107/96, falsifiers pass)

3) Days 5–6 — Minimal modular split (FOUNDATIONAL)
   - Extract `patterns.py` (78 variants) and `wulun.py` (relationship logic)
   - Verify benchmarks (107/96, 42/42) after each extraction

4) Day 7 — FLEX (choose by momentum)
   - Cross‑file relations v1 (env→config→usage triangles) OR
   - IF.armour.learner MVP (scrape 5 CVEs → synthesize + validate patterns)

## Minor Fix Applied
- Replaced `datetime.utcnow()` with `datetime.now(datetime.UTC)` and preserved `Z` suffix
  - File: `code/yologuard/src/IF.yologuard_v3.py`

## Next Check‑In
- End of Day 3: deliver FP corpus results and head‑to‑head comparison artifacts under `code/yologuard/reports/`.

## Handy Commands
- Benchmark: `python3 code/yologuard/benchmarks/run_leaky_repo_v3_philosophical_fast_v2.py`
- Forensics: `python3 code/yologuard/src/IF.yologuard_v3.py --scan code/yologuard/benchmarks/leaky-repo --profile forensics --json ief.json --sarif ief.sarif --graph-out indra.json --manifest ief.manifest --pq-report pq.json --stats`
- Head‑to‑head: `python3 code/yologuard/harness/head2head.py --config code/yologuard/harness/corpus_config.json --workdir /tmp/yolo-corpus --json code/yologuard/reports/<ts>/head2head.json --md code/yologuard/reports/<ts>/head2head.md`
