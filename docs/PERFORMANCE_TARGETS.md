# Performance Targets (v1)

This doc sets honest expectations for initial deployments. Update as we collect more data.

## Scan Speed (local)

| Repo Size | Files      | Target Time | Notes                 |
|-----------|------------|-------------|-----------------------|
| Small     | <100       | <1s         | Instant feedback      |
| Medium    | 100–1,000  | <5s         | CI-friendly           |
| Large     | 1k–10k     | <30s        | Background job        |
| Huge      | >10k       | <5 min      | Batch processing      |

## Connectivity Latency (REST-first)

| Level | Type                      | p95 Target |
|------:|---------------------------|-----------:|
| L1    | function → function       |      <1 ms |
| L2    | module → module           |      <5 ms |
| L3    | service (REST API)        |     <50 ms |
| L4–5  | advanced (defer to v2+)   |        TBD |

Async fallback semantics:
- If validator queue depth exceeds threshold, mark message `validation-deferred`, enqueue for async validation, and proceed with a circuit breaker policy.
- Document retry/backoff; promote failures to WARN, not ERROR.

## Manual Performance Check

**Purpose:** Verify that IF.yologuard meets performance targets in your local environment before deploying to CI/CD or production.

### Prerequisites

- **Large test corpus:** 10,000+ test files (see example below)
- **Timing tools:** `time` command (built-in) and optionally `/usr/bin/time -v` (GNU time for detailed stats)
- **Environment:** Local machine with typical resources (dual-core CPU, 4GB+ RAM)
- **Tool version:** IF.yologuard v3 or later

### Step-by-Step Instructions

#### 1. Prepare Test Corpus (10k Files)

Create a large test dataset with realistic file patterns:

```bash
# Create test directory
mkdir -p /tmp/perf-test
cd /tmp/perf-test

# Generate 10,000 test files with secrets patterns
for i in {1..10000}; do
  echo "AWS_KEY=AKIAIOSFODNN7EXAMPLE" > file_$i.txt
done

# Verify corpus size
ls -1 | wc -l          # Should show 10000
du -sh .               # Show total size (usually 150–300 MB)
```

#### 2. Run Performance Sweep

Execute a clean scan with timing:

```bash
# Run IF.yologuard with timing (built-in time command)
time python3 /home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py \
  --scan /tmp/perf-test \
  --profile ci \
  --json /tmp/results.json

# For detailed memory/CPU stats (if GNU time available)
/usr/bin/time -v python3 /home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py \
  --scan /tmp/perf-test \
  --profile ci \
  --json /tmp/results.json
```

#### 3. Extract and Calculate Metrics

Parse results and compute performance indicators:

```bash
# From standard time output, extract real time (seconds)
# Example output: real 0m9.543s
# Calculation: 10000 files / 9.543 seconds ≈ 1047 files/sec

# Calculate corpus size in MB
CORPUS_MB=$(du -s /tmp/perf-test | awk '{print $1 / 1024}')

# Approximate throughput
SCAN_TIME=9.543    # Replace with actual time from output
FILES_PER_SEC=$(echo "10000 / $SCAN_TIME" | bc -l)
MB_PER_SEC=$(echo "$CORPUS_MB / $SCAN_TIME" | bc -l)

echo "Performance Results:"
echo "==================="
echo "Total files: 10000"
echo "Corpus size: ${CORPUS_MB} MB"
echo "Scan time: ${SCAN_TIME} seconds"
echo "Files/sec: ${FILES_PER_SEC}"
echo "MB/sec: ${MB_PER_SEC}"
```

#### 4. Validate Against Targets

Compare results to measurement targets below.

### Measurement Targets

| Metric | Target | How to Measure | Acceptable Range |
|--------|--------|---|---|
| **Files/sec** | 1000+ | File count ÷ scan time | ≥1000 files/sec (10k corpus: <10s) |
| **MB/sec** | 100+ | Total MB ÷ scan time | ≥100 MB/sec |
| **p50 latency** | <1ms | Per-file timing (median) | <1ms per file |
| **p95 latency** | <5ms | Per-file timing (95th %ile) | <5ms per file |
| **p99 latency** | <10ms | Per-file timing (99th %ile) | <10ms per file |
| **Memory peak** | <500MB | `GNU time -v` → Maximum resident set size | Peak RSS <500MB |

### Result Interpretation

#### Green Light (All Targets Met)

```
Files/sec:    1200+ ✓
MB/sec:       120+  ✓
Memory peak:  350MB ✓
```

**Action:** Safe to proceed with CI/CD integration and production deployments.

#### Yellow Light (Some Targets Missed)

**Example:** Files/sec = 800 (target 1000)

**Investigation steps:**
1. Check file size distribution: `find /tmp/perf-test -type f -exec wc -c {} \; | sort -n`
   - If median file size > 100KB, adjust target downward or add `--max-file-bytes` filter
2. Profile CPU usage during scan: Watch `top` or `htop` in another terminal
   - If CPU <50% utilization, consider --threads option (if available)
3. Check for I/O bottlenecks: Run `iostat 1 10` during scan
   - If I/O wait >30%, files may be on slow storage (NFS, USB drive, etc.)

#### Red Light (Targets Significantly Missed)

**Example:** Files/sec = 400 (target 1000) or Memory peak = 1.2GB (target <500MB)

**Actions:**
1. **Stop and revert:** Do not deploy to production
2. **Investigate root cause:**
   - Run profiler: Check if `-v` or `--profile debug` shows where time is spent
   - Review recent code changes in `code/yologuard/src/`
   - Test on different hardware (faster SSD, more RAM)
3. **File issue:** Open GitHub issue with:
   - Scan results (files/sec, memory peak)
   - Hardware specs (CPU, RAM, storage type)
   - Test corpus details (file count, avg size)
   - Relevant error logs

### Quick Health Check (Minimal Test)

For rapid verification, use a 1,000-file corpus:

```bash
# Quick test with 1k files (30-60 seconds total)
mkdir -p /tmp/perf-quick
for i in {1..1000}; do
  echo "AWS_KEY=AKIAIOSFODNN7EXAMPLE" > /tmp/perf-quick/file_$i.txt
done

# Run and time
time python3 /home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py \
  --scan /tmp/perf-quick \
  --profile ci

# Quick math: if scan took 1 second, files/sec ≈ 1000 ✓
```

References:
- IF_CONNECTIVITY_ARCHITECTURE.md (levels)
- schemas/ifmessage/v1.0.schema.json (message contract)
