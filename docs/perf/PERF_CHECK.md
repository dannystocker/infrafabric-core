# Manual Performance Check (Local)

Use this guide to get indicative throughput numbers on your machine.

## Quick Run
```
python3 code/yologuard/harness/perf_local.py --root code/yologuard/benchmarks/leaky-repo --json /tmp/perf.json
cat /tmp/perf.json | jq
```

Outputs include files/sec and MB/sec without altering detection thresholds.

Notes:
- This is a local check, not a CI gate.
- For large repos, consider `--max-files` and sample subsets.
