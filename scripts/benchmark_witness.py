#!/usr/bin/env python3
"""
IF.witness Performance Benchmark Script

Quick benchmark for ongoing performance monitoring.
Run this to verify performance remains within targets after code changes.

Usage:
    python scripts/benchmark_witness.py
    python scripts/benchmark_witness.py --quick      # Fast 10-iteration test
    python scripts/benchmark_witness.py --full       # Full 1000-iteration test
"""

import sys
import time
import tempfile
import argparse
import statistics
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.witness.database import WitnessDatabase
from src.witness.models import Cost
from src.witness.crypto import WitnessCrypto


class PerformanceTimer:
    """Context manager for timing code blocks"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.elapsed_ms = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        self.elapsed_ms = (self.end_time - self.start_time) * 1000


def measure_percentile(times, percentile):
    """Calculate percentile from list of times"""
    if not times:
        return 0.0
    sorted_times = sorted(times)
    index = int(len(sorted_times) * percentile / 100)
    return sorted_times[min(index, len(sorted_times) - 1)]


def benchmark_log_latency(num_iterations=100):
    """Benchmark log operation latency"""
    print(f"\n{'='*60}")
    print(f"Benchmarking Log Latency ({num_iterations} iterations)")
    print('='*60)

    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / 'benchmark.db'
    key_path = Path(temp_dir) / 'key.pem'

    crypto = WitnessCrypto(key_path)
    db = WitnessDatabase(db_path, crypto)

    times = []
    for i in range(num_iterations):
        with PerformanceTimer() as timer:
            db.create_entry(
                event='benchmark_event',
                component='IF.benchmark',
                trace_id=f'trace-{i}',
                payload={'iteration': i, 'data': 'benchmark payload'},
                cost=Cost(tokens_in=100, tokens_out=50, cost_usd=0.001, model='benchmark-model')
            )
        times.append(timer.elapsed_ms)

    db.close()

    # Calculate statistics
    avg = statistics.mean(times)
    median = statistics.median(times)
    p95 = measure_percentile(times, 95)
    p99 = measure_percentile(times, 99)

    print(f"\nResults:")
    print(f"  Average:  {avg:.2f}ms")
    print(f"  Median:   {median:.2f}ms")
    print(f"  P95:      {p95:.2f}ms")
    print(f"  P99:      {p99:.2f}ms")
    print(f"  Min:      {min(times):.2f}ms")
    print(f"  Max:      {max(times):.2f}ms")

    # Check against target
    target = 50.0
    if p95 < target:
        print(f"\n✓ PASS: P95 latency {p95:.2f}ms meets <{target}ms target")
        return True
    else:
        print(f"\n✗ FAIL: P95 latency {p95:.2f}ms exceeds {target}ms target")
        return False


def benchmark_batch_insert(num_entries=100):
    """Benchmark batch insert performance"""
    print(f"\n{'='*60}")
    print(f"Benchmarking Batch Insert ({num_entries} entries)")
    print('='*60)

    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / 'benchmark.db'
    key_path = Path(temp_dir) / 'key.pem'

    crypto = WitnessCrypto(key_path)
    db = WitnessDatabase(db_path, crypto)

    entries_data = [
        {
            'event': 'batch_event',
            'component': 'IF.benchmark',
            'trace_id': f'trace-{i}',
            'payload': {'iteration': i},
            'cost': Cost(tokens_in=100, tokens_out=50, cost_usd=0.001, model='benchmark-model')
        }
        for i in range(num_entries)
    ]

    with PerformanceTimer() as timer:
        db.create_entries_batch(entries_data)

    elapsed = timer.elapsed_ms
    per_entry = elapsed / num_entries
    throughput = num_entries / elapsed * 1000

    db.close()

    print(f"\nResults:")
    print(f"  Total time:   {elapsed:.2f}ms")
    print(f"  Per entry:    {per_entry:.2f}ms")
    print(f"  Throughput:   {throughput:.0f} entries/sec")

    # Check against target (should be >5000 entries/sec for large batches)
    # For small batches (<50), use lower threshold due to overhead
    target_throughput = 3000 if num_entries < 50 else 5000
    if throughput > target_throughput:
        print(f"\n✓ PASS: Throughput {throughput:.0f}/s exceeds {target_throughput}/s target")
        return True
    else:
        print(f"\n✗ FAIL: Throughput {throughput:.0f}/s below {target_throughput}/s target")
        return False


def benchmark_report_generation(num_entries=1000, num_traces=100):
    """Benchmark report generation performance"""
    print(f"\n{'='*60}")
    print(f"Benchmarking Report Generation ({num_entries} entries)")
    print('='*60)

    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / 'benchmark.db'
    key_path = Path(temp_dir) / 'key.pem'

    crypto = WitnessCrypto(key_path)
    db = WitnessDatabase(db_path, crypto)

    # Create test data
    print("Creating test data...")
    trace_ids = []
    for i in range(num_entries):
        trace_id = f'trace-{i % num_traces}'
        if trace_id not in trace_ids:
            trace_ids.append(trace_id)

        db.create_entry(
            event=f'event_{i % 10}',
            component=f'IF.component{i % 5}',
            trace_id=trace_id,
            payload={'step': i},
            cost=Cost(
                tokens_in=100 + (i % 50),
                tokens_out=50 + (i % 30),
                cost_usd=0.001 * (i % 10),
                model='benchmark-model'
            )
        )

    # Benchmark trace retrieval
    times = []
    test_traces = trace_ids[:min(20, len(trace_ids))]
    for trace_id in test_traces:
        with PerformanceTimer() as timer:
            trace_info = db.get_trace(trace_id)
        times.append(timer.elapsed_ms)

    db.close()

    avg = statistics.mean(times)
    p95 = measure_percentile(times, 95)

    print(f"\nResults:")
    print(f"  Traces tested: {len(times)}")
    print(f"  Average:       {avg:.2f}ms")
    print(f"  P95:           {p95:.2f}ms")

    # Check against target
    target = 100.0
    if p95 < target:
        print(f"\n✓ PASS: P95 latency {p95:.2f}ms meets <{target}ms target")
        return True
    else:
        print(f"\n✗ FAIL: P95 latency {p95:.2f}ms exceeds {target}ms target")
        return False


def benchmark_verification_scaling():
    """Benchmark verification scaling"""
    print(f"\n{'='*60}")
    print(f"Benchmarking Verification Scaling")
    print('='*60)

    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / 'benchmark.db'
    key_path = Path(temp_dir) / 'key.pem'

    crypto = WitnessCrypto(key_path)

    chain_sizes = [100, 500, 1000]
    results = []

    for size in chain_sizes:
        # Create fresh database
        db_path.unlink(missing_ok=True)
        db = WitnessDatabase(db_path, crypto)

        # Create entries
        for i in range(size):
            db.create_entry(
                event='verify_event',
                component='IF.benchmark',
                trace_id=f'trace-{i}',
                payload={'step': i}
            )

        # Measure verification
        with PerformanceTimer() as timer:
            is_valid, msg, count = db.verify_all()

        elapsed = timer.elapsed_ms
        per_entry = (elapsed * 1000) / size

        results.append({'size': size, 'time_ms': elapsed, 'per_entry_us': per_entry})

        db.close()

    print(f"\nResults:")
    print(f"  {'Size':<10} {'Time':<15} {'Per Entry':<15}")
    print(f"  {'-'*10} {'-'*15} {'-'*15}")
    for r in results:
        print(f"  {r['size']:<10} {r['time_ms']:>10.2f}ms   {r['per_entry_us']:>10.2f}µs")

    # Check variance (should be <50% for linear scaling)
    per_entry_times = [r['per_entry_us'] for r in results]
    variance = statistics.stdev(per_entry_times) / statistics.mean(per_entry_times)

    print(f"\nPer-entry variance: {variance:.2%}")

    if variance < 0.5:
        print(f"✓ PASS: Verification scales linearly (variance < 50%)")
        return True
    else:
        print(f"✗ FAIL: Verification scaling has high variance (>50%)")
        return False


def main():
    parser = argparse.ArgumentParser(description='IF.witness Performance Benchmark')
    parser.add_argument('--quick', action='store_true', help='Quick test (10 iterations)')
    parser.add_argument('--full', action='store_true', help='Full test (1000 iterations)')
    args = parser.parse_args()

    if args.quick:
        iterations = 10
        batch_size = 10
        report_entries = 100
    elif args.full:
        iterations = 1000
        batch_size = 1000
        report_entries = 10000
    else:
        iterations = 100
        batch_size = 100
        report_entries = 1000

    print("\n" + "="*60)
    print("IF.witness Performance Benchmark")
    print("="*60)
    print(f"Mode: {'Quick' if args.quick else 'Full' if args.full else 'Standard'}")

    results = []

    # Run benchmarks
    results.append(('Log Latency', benchmark_log_latency(iterations)))
    results.append(('Batch Insert', benchmark_batch_insert(batch_size)))
    results.append(('Report Generation', benchmark_report_generation(report_entries, report_entries // 10)))
    results.append(('Verification Scaling', benchmark_verification_scaling()))

    # Summary
    print("\n" + "="*60)
    print("Benchmark Summary")
    print("="*60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name:<25} {status}")
        all_passed = all_passed and passed

    print("="*60)

    if all_passed:
        print("\n✓ All benchmarks passed!")
        return 0
    else:
        print("\n✗ Some benchmarks failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
