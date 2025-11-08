# IF.yologuard Harness

Utilities for evaluating false-positive rates and performance on your own codebases.

## False Positive Evaluation (Assumes Clean Corpus)

```bash
python3 fp_eval.py --root /path/to/clean/repos --json fp_report.json
```

Notes:
- This treats all detections as false positives (assumes repos are clean).
- Use `--exclude` to skip vendor/build/cache directories.
- Output includes detections per 1k files and per MB.

## Performance Benchmark

```bash
python3 perf_bench.py --root /path/to/large/repo --json perf_report.json
```

Reports:
- Files scanned, bytes scanned
- Detections count
- Duration and throughput (files/sec, MB/sec)

