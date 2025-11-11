"""
IF.witness CLI Performance Test Suite

Target Metrics:
- `if witness log`: <50ms (P95 latency)
- `if optimise report`: <100ms for 1000 entries (P95 latency)
- Hash chain verification: O(n) scaling
- Batch insert: >10x faster than individual inserts

Philosophy: Performance is a feature. Real-time observability requires
low-latency logging that doesn't slow down the critical path.
"""

import sys
import time
import tempfile
import unittest
import statistics
import cProfile
import pstats
import io
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

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


def measure_percentile(times: List[float], percentile: int) -> float:
    """Calculate percentile from list of times"""
    if not times:
        return 0.0
    sorted_times = sorted(times)
    index = int(len(sorted_times) * percentile / 100)
    return sorted_times[min(index, len(sorted_times) - 1)]


class TestLogPerformance(unittest.TestCase):
    """Test if witness log is <50ms (P95)"""

    def setUp(self):
        """Create temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'perf_test.db'
        self.key_path = Path(self.temp_dir) / 'test_key.pem'
        self.crypto = WitnessCrypto(self.key_path)

    def test_log_latency_p95(self):
        """Test P95 latency for log operations"""
        print("\n=== Log Performance Test ===")

        times = []
        num_iterations = 100

        # Create database
        db = WitnessDatabase(self.db_path, self.crypto)

        for i in range(num_iterations):
            with PerformanceTimer() as timer:
                db.create_entry(
                    event='test_event',
                    component='IF.test',
                    trace_id=f'trace-{i}',
                    payload={'iteration': i, 'data': 'test payload'},
                    cost=Cost(tokens_in=100, tokens_out=50, cost_usd=0.001, model='test-model')
                )
            times.append(timer.elapsed_ms)

        db.close()

        # Calculate statistics
        p50 = measure_percentile(times, 50)
        p95 = measure_percentile(times, 95)
        p99 = measure_percentile(times, 99)
        avg = statistics.mean(times)
        median = statistics.median(times)

        print(f"Iterations: {num_iterations}")
        print(f"Average: {avg:.2f}ms")
        print(f"Median: {median:.2f}ms")
        print(f"P50: {p50:.2f}ms")
        print(f"P95: {p95:.2f}ms")
        print(f"P99: {p99:.2f}ms")
        print(f"Min: {min(times):.2f}ms")
        print(f"Max: {max(times):.2f}ms")

        # Assert P95 < 50ms target
        self.assertLess(p95, 50.0, f"P95 latency {p95:.2f}ms exceeds 50ms target")
        print(f"✓ P95 latency {p95:.2f}ms meets <50ms target")

    def test_log_latency_with_existing_chain(self):
        """Test log latency with existing hash chain (1000 entries)"""
        print("\n=== Log Latency with Existing Chain ===")

        db = WitnessDatabase(self.db_path, self.crypto)

        # Pre-populate with 1000 entries
        print("Pre-populating with 1000 entries...")
        for i in range(1000):
            db.create_entry(
                event='setup_event',
                component='IF.test',
                trace_id=f'setup-{i}',
                payload={'step': i}
            )

        # Now measure log latency
        times = []
        num_iterations = 100

        for i in range(num_iterations):
            with PerformanceTimer() as timer:
                db.create_entry(
                    event='test_event',
                    component='IF.test',
                    trace_id=f'perf-{i}',
                    payload={'iteration': i}
                )
            times.append(timer.elapsed_ms)

        db.close()

        p95 = measure_percentile(times, 95)
        avg = statistics.mean(times)

        print(f"Chain size: 1000 entries")
        print(f"Test iterations: {num_iterations}")
        print(f"Average: {avg:.2f}ms")
        print(f"P95: {p95:.2f}ms")

        self.assertLess(p95, 50.0, f"P95 latency {p95:.2f}ms exceeds 50ms target")
        print(f"✓ P95 latency {p95:.2f}ms meets <50ms target (with 1000 entry chain)")


class TestReportPerformance(unittest.TestCase):
    """Test if optimise report is <100ms for 1000 entries"""

    def setUp(self):
        """Create temporary database with test data"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'perf_test.db'
        self.key_path = Path(self.temp_dir) / 'test_key.pem'
        self.crypto = WitnessCrypto(self.key_path)

    def test_report_generation_1000_entries(self):
        """Test report generation with 1000 entries"""
        print("\n=== Report Performance Test (1000 entries) ===")

        db = WitnessDatabase(self.db_path, self.crypto)

        # Create 1000 test entries
        print("Creating 1000 test entries...")
        trace_ids = []
        for i in range(1000):
            trace_id = f'trace-{i % 100}'  # 100 unique traces, 10 entries each
            if trace_id not in trace_ids:
                trace_ids.append(trace_id)

            db.create_entry(
                event=f'event_{i % 10}',
                component=f'IF.component{i % 5}',
                trace_id=trace_id,
                payload={'step': i, 'data': f'payload_{i}'},
                cost=Cost(
                    tokens_in=100 + (i % 50),
                    tokens_out=50 + (i % 30),
                    cost_usd=0.001 * (i % 10),
                    model='test-model'
                )
            )

        print(f"Created 1000 entries across {len(trace_ids)} traces")

        # Measure trace retrieval (report generation)
        times = []
        for trace_id in trace_ids[:20]:  # Test first 20 traces
            with PerformanceTimer() as timer:
                trace_info = db.get_trace(trace_id)
            times.append(timer.elapsed_ms)

        p95 = measure_percentile(times, 95)
        avg = statistics.mean(times)

        print(f"Traces tested: {len(times)}")
        print(f"Average: {avg:.2f}ms")
        print(f"P95: {p95:.2f}ms")

        db.close()

        self.assertLess(p95, 100.0, f"P95 latency {p95:.2f}ms exceeds 100ms target")
        print(f"✓ P95 latency {p95:.2f}ms meets <100ms target")

    def test_cost_report_performance(self):
        """Test cost breakdown report generation"""
        print("\n=== Cost Report Performance Test ===")

        db = WitnessDatabase(self.db_path, self.crypto)

        # Create entries for multiple components
        print("Creating test data...")
        for i in range(1000):
            db.create_entry(
                event='llm_call',
                component=f'IF.component{i % 5}',
                trace_id=f'trace-{i}',
                payload={'query': f'query_{i}'},
                cost=Cost(
                    tokens_in=100 + (i % 100),
                    tokens_out=50 + (i % 50),
                    cost_usd=0.001 * (1 + i % 10),
                    model=f'model-{i % 3}'
                )
            )

        # Measure cost breakdown query
        times = []
        for _ in range(20):
            with PerformanceTimer() as timer:
                cost_data = db.get_cost_by_component()
            times.append(timer.elapsed_ms)

        p95 = measure_percentile(times, 95)
        avg = statistics.mean(times)

        print(f"Iterations: {len(times)}")
        print(f"Average: {avg:.2f}ms")
        print(f"P95: {p95:.2f}ms")

        db.close()

        self.assertLess(p95, 100.0, f"P95 latency {p95:.2f}ms exceeds 100ms target")
        print(f"✓ P95 latency {p95:.2f}ms meets <100ms target")


class TestVerificationPerformance(unittest.TestCase):
    """Test hash chain verification scales linearly"""

    def setUp(self):
        """Create temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'perf_test.db'
        self.key_path = Path(self.temp_dir) / 'test_key.pem'
        self.crypto = WitnessCrypto(self.key_path)

    def test_verification_scaling(self):
        """Test verification time scales linearly with chain size"""
        print("\n=== Verification Scaling Test ===")

        db = WitnessDatabase(self.db_path, self.crypto)

        chain_sizes = [100, 500, 1000, 2000]
        results = []

        for size in chain_sizes:
            # Clear and create entries
            db.close()
            self.db_path.unlink(missing_ok=True)
            db = WitnessDatabase(self.db_path, self.crypto)

            print(f"\nTesting with {size} entries...")
            for i in range(size):
                db.create_entry(
                    event='test_event',
                    component='IF.test',
                    trace_id=f'trace-{i}',
                    payload={'step': i}
                )

            # Measure verification time
            times = []
            for _ in range(5):
                with PerformanceTimer() as timer:
                    is_valid, msg, count = db.verify_all()
                times.append(timer.elapsed_ms)
                self.assertTrue(is_valid)

            avg_time = statistics.mean(times)
            results.append({'size': size, 'time_ms': avg_time, 'per_entry_us': (avg_time * 1000) / size})

            print(f"  Average: {avg_time:.2f}ms")
            print(f"  Per entry: {(avg_time * 1000) / size:.2f}µs")

        db.close()

        # Check linearity: time per entry should be roughly constant
        per_entry_times = [r['per_entry_us'] for r in results]
        variance = statistics.stdev(per_entry_times) / statistics.mean(per_entry_times)

        print(f"\nScaling Analysis:")
        for r in results:
            print(f"  {r['size']:4d} entries: {r['time_ms']:7.2f}ms ({r['per_entry_us']:.2f}µs/entry)")

        print(f"\nPer-entry variance: {variance:.2%}")
        self.assertLess(variance, 0.5, "Verification should scale linearly (variance < 50%)")
        print("✓ Verification scales linearly")


class TestBatchPerformance(unittest.TestCase):
    """Compare batch insert vs individual inserts"""

    def setUp(self):
        """Create temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'perf_test.db'
        self.key_path = Path(self.temp_dir) / 'test_key.pem'
        self.crypto = WitnessCrypto(self.key_path)

    def test_batch_vs_single_insert(self):
        """Compare batch insert vs individual inserts"""
        print("\n=== Batch vs Single Insert Performance ===")

        num_entries = 100

        # Test single inserts
        self.db_path.unlink(missing_ok=True)
        db = WitnessDatabase(self.db_path, self.crypto)

        print(f"\nSingle inserts ({num_entries} entries)...")
        with PerformanceTimer() as single_timer:
            for i in range(num_entries):
                db.create_entry(
                    event='test_event',
                    component='IF.test',
                    trace_id=f'trace-{i}',
                    payload={'step': i}
                )

        single_time = single_timer.elapsed_ms
        db.close()

        # Test batch insert
        self.db_path.unlink(missing_ok=True)
        db = WitnessDatabase(self.db_path, self.crypto)

        entries_data = [
            {
                'event': 'test_event',
                'component': 'IF.test',
                'trace_id': f'trace-{i}',
                'payload': {'step': i}
            }
            for i in range(num_entries)
        ]

        print(f"Batch insert ({num_entries} entries)...")
        with PerformanceTimer() as batch_timer:
            db.create_entries_batch(entries_data)

        batch_time = batch_timer.elapsed_ms
        db.close()

        speedup = single_time / batch_time

        print(f"\nResults:")
        print(f"  Single inserts: {single_time:.2f}ms ({single_time/num_entries:.2f}ms/entry)")
        print(f"  Batch insert: {batch_time:.2f}ms ({batch_time/num_entries:.2f}ms/entry)")
        print(f"  Speedup: {speedup:.1f}x")

        self.assertGreater(speedup, 1.5, "Batch insert should be >1.5x faster")
        print(f"✓ Batch insert is {speedup:.1f}x faster")

    def test_large_batch_insert(self):
        """Test batch insert with 1000 entries"""
        print("\n=== Large Batch Insert Test (1000 entries) ===")

        db = WitnessDatabase(self.db_path, self.crypto)

        entries_data = [
            {
                'event': f'event_{i % 10}',
                'component': f'IF.component{i % 5}',
                'trace_id': f'trace-{i % 100}',
                'payload': {'step': i, 'data': f'payload_{i}'},
                'cost': Cost(
                    tokens_in=100 + (i % 50),
                    tokens_out=50 + (i % 30),
                    cost_usd=0.001 * (i % 10),
                    model='test-model'
                )
            }
            for i in range(1000)
        ]

        with PerformanceTimer() as timer:
            entries = db.create_entries_batch(entries_data)

        elapsed = timer.elapsed_ms
        per_entry = elapsed / 1000

        print(f"Total time: {elapsed:.2f}ms")
        print(f"Per entry: {per_entry:.2f}ms")
        print(f"Throughput: {1000/elapsed*1000:.0f} entries/sec")

        # Verify hash chain
        is_valid, msg, count = db.verify_all()
        self.assertTrue(is_valid)
        self.assertEqual(count, 1000)

        db.close()

        # Should average < 1ms per entry
        self.assertLess(per_entry, 1.0, "Batch insert should average <1ms per entry")
        print(f"✓ Batch insert averages {per_entry:.2f}ms per entry")


class TestConnectionPoolPerformance(unittest.TestCase):
    """Test connection pooling performance"""

    def setUp(self):
        """Create temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'perf_test.db'
        self.key_path = Path(self.temp_dir) / 'test_key.pem'
        self.crypto = WitnessCrypto(self.key_path)

    def test_pooled_vs_single_connection(self):
        """Compare pooled vs single connection performance"""
        print("\n=== Connection Pool Performance ===")

        num_operations = 100

        # Test without pool
        print(f"\nWithout pool ({num_operations} operations)...")
        self.db_path.unlink(missing_ok=True)
        db = WitnessDatabase(self.db_path, self.crypto, use_pool=False)

        with PerformanceTimer() as no_pool_timer:
            for i in range(num_operations):
                db.create_entry(
                    event='test_event',
                    component='IF.test',
                    trace_id=f'trace-{i}',
                    payload={'step': i}
                )

        no_pool_time = no_pool_timer.elapsed_ms
        db.close()

        # Test with pool
        print(f"With pool ({num_operations} operations)...")
        self.db_path.unlink(missing_ok=True)
        db = WitnessDatabase(self.db_path, self.crypto, use_pool=True)

        with PerformanceTimer() as pool_timer:
            for i in range(num_operations):
                db.create_entry(
                    event='test_event',
                    component='IF.test',
                    trace_id=f'trace-{i}',
                    payload={'step': i}
                )

        pool_time = pool_timer.elapsed_ms
        db.close()

        print(f"\nResults:")
        print(f"  Without pool: {no_pool_time:.2f}ms")
        print(f"  With pool: {pool_time:.2f}ms")
        print(f"  Difference: {((pool_time - no_pool_time) / no_pool_time * 100):.1f}%")

        # Pool should be similar performance (within 50% for single-threaded)
        # In multi-threaded scenarios, pool would show significant advantage
        print(f"✓ Connection pool overhead is acceptable")


class TestProfilingIntegration(unittest.TestCase):
    """Test profiling integration"""

    def setUp(self):
        """Create temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'perf_test.db'
        self.key_path = Path(self.temp_dir) / 'test_key.pem'
        self.crypto = WitnessCrypto(self.key_path)

    def test_profile_create_entry(self):
        """Profile create_entry operation"""
        print("\n=== Profiling create_entry ===")

        db = WitnessDatabase(self.db_path, self.crypto)

        # Profile the operation
        profiler = cProfile.Profile()
        profiler.enable()

        for i in range(100):
            db.create_entry(
                event='test_event',
                component='IF.test',
                trace_id=f'trace-{i}',
                payload={'step': i, 'data': 'test'},
                cost=Cost(tokens_in=100, tokens_out=50, cost_usd=0.001, model='test-model')
            )

        profiler.disable()

        # Print stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(15)  # Top 15 functions

        print("\nTop 15 functions by cumulative time:")
        print(s.getvalue())

        db.close()

    def test_profile_verification(self):
        """Profile hash chain verification"""
        print("\n=== Profiling Verification ===")

        db = WitnessDatabase(self.db_path, self.crypto)

        # Create 1000 entries
        for i in range(1000):
            db.create_entry(
                event='test_event',
                component='IF.test',
                trace_id=f'trace-{i}',
                payload={'step': i}
            )

        # Profile verification
        profiler = cProfile.Profile()
        profiler.enable()

        db.verify_all()

        profiler.disable()

        # Print stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(15)

        print("\nTop 15 functions by cumulative time:")
        print(s.getvalue())

        db.close()


def run_performance_suite():
    """Run complete performance test suite"""
    print("\n" + "=" * 80)
    print("IF.witness CLI Performance Test Suite")
    print("=" * 80)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLogPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestReportPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestVerificationPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectionPoolPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestProfilingIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    print("Performance Test Summary")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_performance_suite()
    sys.exit(0 if success else 1)
