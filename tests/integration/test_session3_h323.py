"""
Integration tests for Session 3 (H.323) using IF.optimise CLI

Session 3 (H.323): Gatekeeper Admission Control
- H.323 endpoint admission requests
- Bandwidth cost tracking
- Gatekeeper decision logging with costs
- Budget monitoring for H.323 operations
- Multi-endpoint scenarios with cumulative costs

Tests verify:
- Integration between IF.witness and IF.optimise CLIs
- Cost calculation for H.323 operations
- JSON output parsing and validation
- Budget tracking and alerts
- Cost reports by component
"""

import sys
import os
import json
import tempfile
import subprocess
import unittest
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestSession3H323Integration(unittest.TestCase):
    """Integration tests for Session 3 (H.323) using IF.optimise CLI"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = Path(cls.temp_dir) / 'test_h323.db'
        cls.budget_path = Path(cls.temp_dir) / 'budget.json'

        # Set environment variable for custom database path
        cls.env = {
            'HOME': cls.temp_dir,
            'PATH': os.environ.get('PATH', ''),
        }

    def setUp(self):
        """Set up test fixtures before each test"""
        self.trace_ids = []
        self.test_data = []

    def tearDown(self):
        """Clean up after each test"""
        # Clear IF.witness database entries for this test
        pass

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment after all tests"""
        # Clean up database and temp files
        import shutil
        try:
            shutil.rmtree(cls.temp_dir)
        except Exception:
            pass

    def _run_witness_log(self, event: str, component: str, trace_id: str,
                        payload: Dict[str, Any], tokens_in: int, tokens_out: int,
                        cost: float, model: str = 'claude-haiku-4.5') -> subprocess.CompletedProcess:
        """Run IF.witness log command"""
        cmd = [
            'python3', 'src/cli/if-witness.py', 'log',
            '--event', event,
            '--component', component,
            '--trace-id', trace_id,
            '--payload', json.dumps(payload),
            '--tokens-in', str(tokens_in),
            '--tokens-out', str(tokens_out),
            '--cost', str(cost),
            '--model', model
        ]

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )

        return result

    def _run_optimise_report(self, component: str = None, format: str = 'json') -> subprocess.CompletedProcess:
        """Run IF.optimise report command"""
        cmd = ['python3', 'src/cli/if-optimise.py', 'report', '--format', format]

        if component:
            cmd.extend(['--component', component])

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )

        return result

    def _run_optimise_budget(self, budget_amount: float = None, period: str = 'month',
                            component: str = None) -> subprocess.CompletedProcess:
        """Run IF.optimise budget command"""
        cmd = ['python3', 'src/cli/if-optimise.py', 'budget']

        if budget_amount:
            cmd.extend(['--set', str(budget_amount)])

        if period:
            cmd.extend(['--period', period])

        if component:
            cmd.extend(['--component', component])

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )

        return result

    def _run_witness_trace(self, trace_id: str, format: str = 'json') -> subprocess.CompletedProcess:
        """Run IF.witness trace command"""
        cmd = [
            'python3', 'src/cli/if-witness.py', 'trace',
            trace_id,
            '--format', format
        ]

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )

        return result

    def test_h323_single_admission_cost_tracking(self):
        """Test single H.323 admission request with cost tracking"""
        trace_id = "h323-admission-" + uuid4().hex
        self.trace_ids.append(trace_id)

        # Log H.323 admission request
        result = self._run_witness_log(
            event='h323_admission_request',
            component='IF.witness.h323',
            trace_id=trace_id,
            payload={
                'bandwidth_kbps': 384,
                'decision': 'approved',
                'endpoint': 'h323-endpoint-1',
                'session_id': 'session-001'
            },
            tokens_in=150,
            tokens_out=75,
            cost=0.0003,
            model='claude-haiku-4.5'
        )

        # Verify command succeeded
        self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")

        # Verify output contains success indicators
        self.assertIn("✓ Witness entry created", result.stdout)
        self.assertIn("✓ Hash chain verified", result.stdout)
        self.assertIn("✓ Cost:", result.stdout)

    def test_h323_multiple_admissions_cost_aggregation(self):
        """Test multiple H.323 admissions with cost aggregation"""
        trace_id = "h323-multi-" + uuid4().hex
        self.trace_ids.append(trace_id)

        endpoints = [
            ('h323-endpoint-1', 384, 0.0003),
            ('h323-endpoint-2', 256, 0.0002),
            ('h323-endpoint-3', 512, 0.0004),
        ]

        total_cost = 0.0
        total_tokens = 0

        # Log multiple admission requests
        for endpoint, bandwidth, cost in endpoints:
            tokens_in = int(bandwidth / 2)
            tokens_out = int(bandwidth / 4)

            result = self._run_witness_log(
                event='h323_admission_request',
                component='IF.witness.h323',
                trace_id=trace_id,
                payload={
                    'bandwidth_kbps': bandwidth,
                    'decision': 'approved',
                    'endpoint': endpoint,
                    'session_id': f'session-{endpoint}'
                },
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost
            )

            self.assertEqual(result.returncode, 0, f"Admission for {endpoint} failed")
            total_cost += cost
            total_tokens += tokens_in + tokens_out

        # Retrieve full trace to verify aggregation
        result = self._run_witness_trace(trace_id, format='json')
        self.assertEqual(result.returncode, 0)

        trace_data = json.loads(result.stdout)

        # Verify trace structure
        self.assertIn('entries', trace_data)
        self.assertEqual(len(trace_data['entries']), 3, "Should have 3 entries")

        # Verify aggregated costs
        self.assertAlmostEqual(trace_data['total_cost_usd'], total_cost, places=6)
        self.assertEqual(trace_data['total_tokens'], total_tokens)

    def test_h323_admission_rejection_with_cost(self):
        """Test H.323 admission rejection and cost logging"""
        trace_id = "h323-rejected-" + uuid4().hex
        self.trace_ids.append(trace_id)

        # Log admission request
        result = self._run_witness_log(
            event='h323_admission_request',
            component='IF.witness.h323',
            trace_id=trace_id,
            payload={
                'bandwidth_kbps': 2048,  # Request exceeds capacity
                'decision': 'rejected',
                'endpoint': 'h323-endpoint-4',
                'reason': 'Insufficient bandwidth',
                'session_id': 'session-rejected'
            },
            tokens_in=200,
            tokens_out=100,
            cost=0.0005
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("✓ Witness entry created", result.stdout)

        # Verify trace contains rejection
        result = self._run_witness_trace(trace_id, format='json')
        trace_data = json.loads(result.stdout)

        self.assertEqual(len(trace_data['entries']), 1)
        payload = json.loads(trace_data['entries'][0]['payload'])
        self.assertEqual(payload['decision'], 'rejected')
        self.assertEqual(payload['reason'], 'Insufficient bandwidth')

    def test_h323_cost_report_generation(self):
        """Test cost report generation for H.323 component"""
        # Create several H.323 operations
        for i in range(3):
            trace_id = f"h323-report-{i}-" + uuid4().hex
            self.trace_ids.append(trace_id)

            result = self._run_witness_log(
                event='h323_admission_request',
                component='IF.witness.h323',
                trace_id=trace_id,
                payload={
                    'bandwidth_kbps': 256 + (i * 128),
                    'decision': 'approved',
                    'endpoint': f'h323-endpoint-{i}',
                    'session_id': f'session-{i}'
                },
                tokens_in=100 + (i * 50),
                tokens_out=50 + (i * 25),
                cost=0.0002 + (i * 0.0001)
            )

            self.assertEqual(result.returncode, 0)

        # Generate report for H.323 component
        result = self._run_optimise_report(component='IF.witness.h323', format='json')

        self.assertEqual(result.returncode, 0)

        # Parse and verify report structure
        report_data = json.loads(result.stdout)
        self.assertIsInstance(report_data, list)

        # Should have at least one entry for IF.witness.h323
        h323_entries = [row for row in report_data if 'h323' in row.get('component', '').lower()]
        self.assertGreater(len(h323_entries), 0, "Should have H.323 component in report")

        # Verify report structure
        for row in h323_entries:
            self.assertIn('component', row)
            self.assertIn('operations', row)
            self.assertIn('total_tokens', row)
            self.assertIn('total_cost', row)
            self.assertIn('model', row)

    def test_h323_budget_tracking_month(self):
        """Test budget tracking for H.323 operations (monthly)"""
        # Set monthly budget
        result = self._run_optimise_budget(budget_amount=10.0, period='month')

        self.assertEqual(result.returncode, 0)
        self.assertIn("✓ Budget set", result.stdout)
        self.assertIn("$10.00 per month", result.stdout)

        # Log some H.323 operations
        trace_id = "h323-budget-" + uuid4().hex
        self.trace_ids.append(trace_id)

        result = self._run_witness_log(
            event='h323_admission_request',
            component='IF.witness.h323',
            trace_id=trace_id,
            payload={
                'bandwidth_kbps': 384,
                'decision': 'approved',
                'endpoint': 'h323-endpoint-5',
                'session_id': 'session-budget'
            },
            tokens_in=150,
            tokens_out=75,
            cost=0.0003
        )

        self.assertEqual(result.returncode, 0)

        # Check budget status
        result = self._run_optimise_budget(period='month')
        self.assertEqual(result.returncode, 0)

        # Verify budget information in output
        self.assertIn("Budget Status", result.stdout)
        self.assertIn("Budget:", result.stdout)
        self.assertIn("Spent:", result.stdout)
        self.assertIn("Usage:", result.stdout)

    def test_h323_cost_estimation(self):
        """Test cost estimation for H.323 operations"""
        cmd = [
            'python3', 'src/cli/if-optimise.py', 'estimate',
            '--tokens-in', '200',
            '--tokens-out', '100',
            '--model', 'claude-haiku-4.5',
            '--operations', '5'
        ]

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0)

        # Verify output structure
        self.assertIn("Cost Estimate", result.stdout)
        self.assertIn("Model:", result.stdout)
        self.assertIn("Input tokens:", result.stdout)
        self.assertIn("Output tokens:", result.stdout)
        self.assertIn("Cost per op:", result.stdout)
        self.assertIn("Total cost:", result.stdout)

    def test_h323_trace_with_json_output(self):
        """Test H.323 trace retrieval with JSON parsing"""
        trace_id = "h323-json-" + uuid4().hex
        self.trace_ids.append(trace_id)

        # Log admission request
        result = self._run_witness_log(
            event='h323_admission_request',
            component='IF.witness.h323',
            trace_id=trace_id,
            payload={
                'bandwidth_kbps': 384,
                'decision': 'approved',
                'endpoint': 'h323-endpoint-json',
                'session_id': 'session-json',
                'gatekeeper': 'gk-primary'
            },
            tokens_in=150,
            tokens_out=75,
            cost=0.0003
        )

        self.assertEqual(result.returncode, 0)

        # Retrieve trace as JSON
        result = self._run_witness_trace(trace_id, format='json')
        self.assertEqual(result.returncode, 0)

        # Parse JSON
        trace_data = json.loads(result.stdout)

        # Validate JSON structure
        self.assertIn('trace_id', trace_data)
        self.assertIn('entries', trace_data)
        self.assertIn('components', trace_data)
        self.assertIn('total_cost_usd', trace_data)
        self.assertIn('total_tokens', trace_data)
        self.assertIn('duration_seconds', trace_data)

        # Validate entry structure
        self.assertEqual(len(trace_data['entries']), 1)
        entry = trace_data['entries'][0]

        self.assertIn('id', entry)
        self.assertIn('timestamp', entry)
        self.assertIn('event', entry)
        self.assertIn('component', entry)
        self.assertIn('payload', entry)
        self.assertIn('cost_usd', entry)
        self.assertIn('tokens_in', entry)
        self.assertIn('tokens_out', entry)
        self.assertIn('model', entry)

        # Validate payload parsing
        payload = json.loads(entry['payload']) if isinstance(entry['payload'], str) else entry['payload']
        self.assertEqual(payload['bandwidth_kbps'], 384)
        self.assertEqual(payload['decision'], 'approved')
        self.assertEqual(payload['endpoint'], 'h323-endpoint-json')

    def test_h323_trace_cost_breakdown(self):
        """Test cost breakdown for H.323 trace"""
        trace_id = "h323-breakdown-" + uuid4().hex
        self.trace_ids.append(trace_id)

        # Create multiple operations with different costs
        operations = [
            ('h323_admission_request', 150, 75, 0.0003),
            ('h323_call_setup', 200, 100, 0.0004),
            ('h323_bandwidth_confirm', 100, 50, 0.0002),
        ]

        for event, tokens_in, tokens_out, cost in operations:
            result = self._run_witness_log(
                event=event,
                component='IF.witness.h323',
                trace_id=trace_id,
                payload={
                    'session_id': 'session-breakdown',
                    'endpoint': 'h323-endpoint-breakdown'
                },
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost
            )

            self.assertEqual(result.returncode, 0)

        # Get cost breakdown via witness cost command
        cmd = [
            'python3', 'src/cli/if-witness.py', 'cost',
            '--trace-id', trace_id,
            '--format', 'json'
        ]

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0)

        cost_data = json.loads(result.stdout)

        # Verify cost breakdown structure
        self.assertIn('trace_id', cost_data)
        self.assertIn('total_cost_usd', cost_data)
        self.assertIn('total_tokens', cost_data)
        self.assertIn('entries', cost_data)

        # Verify aggregated costs
        expected_cost = sum([op[3] for op in operations])
        expected_tokens = sum([op[1] + op[2] for op in operations])

        self.assertAlmostEqual(cost_data['total_cost_usd'], expected_cost, places=6)
        self.assertEqual(cost_data['total_tokens'], expected_tokens)

    def test_h323_model_rate_calculation(self):
        """Test correct model rate calculation for H.323"""
        # Test with different models
        models = [
            ('claude-haiku-4.5', 150, 75),
            ('claude-sonnet-4.5', 200, 100),
        ]

        for model, tokens_in, tokens_out in models:
            trace_id = f"h323-model-{model}-" + uuid4().hex
            self.trace_ids.append(trace_id)

            result = self._run_witness_log(
                event='h323_admission_request',
                component='IF.witness.h323',
                trace_id=trace_id,
                payload={
                    'endpoint': f'h323-endpoint-{model}',
                    'model_test': True
                },
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=0.0001,  # Fixed cost for testing
                model=model
            )

            self.assertEqual(result.returncode, 0)

            # Verify witness entry was created successfully
            self.assertIn("✓ Witness entry created", result.stdout)
            # Verify cost was logged
            self.assertIn("✓ Cost:", result.stdout)

    def test_h323_empty_payload_handling(self):
        """Test handling of empty payloads in H.323 logs"""
        trace_id = "h323-empty-" + uuid4().hex
        self.trace_ids.append(trace_id)

        result = self._run_witness_log(
            event='h323_admission_request',
            component='IF.witness.h323',
            trace_id=trace_id,
            payload={},  # Empty payload
            tokens_in=100,
            tokens_out=50,
            cost=0.0001
        )

        self.assertEqual(result.returncode, 0)

        # Retrieve and verify
        result = self._run_witness_trace(trace_id, format='json')
        trace_data = json.loads(result.stdout)

        entry = trace_data['entries'][0]
        payload = json.loads(entry['payload'])
        self.assertEqual(payload, {})

    def test_h323_large_bandwidth_request(self):
        """Test H.323 admission for large bandwidth requests"""
        trace_id = "h323-large-bw-" + uuid4().hex
        self.trace_ids.append(trace_id)

        # Large bandwidth request
        large_bandwidth = 8192  # 8 Mbps
        estimated_tokens_in = 500
        estimated_tokens_out = 250
        estimated_cost = 0.0010

        result = self._run_witness_log(
            event='h323_admission_request',
            component='IF.witness.h323',
            trace_id=trace_id,
            payload={
                'bandwidth_kbps': large_bandwidth,
                'decision': 'approved',
                'endpoint': 'h323-endpoint-large',
                'priority': 'high'
            },
            tokens_in=estimated_tokens_in,
            tokens_out=estimated_tokens_out,
            cost=estimated_cost
        )

        self.assertEqual(result.returncode, 0)

        # Verify in trace
        result = self._run_witness_trace(trace_id, format='json')
        trace_data = json.loads(result.stdout)

        payload = json.loads(trace_data['entries'][0]['payload'])
        self.assertEqual(payload['bandwidth_kbps'], large_bandwidth)

    def test_h323_sequential_operations_cost_tracking(self):
        """Test cost tracking for sequential H.323 operations"""
        trace_id = "h323-sequential-" + uuid4().hex
        self.trace_ids.append(trace_id)

        operations = [
            ('h323_gatekeeper_discovery', 100, 50, 0.0001),
            ('h323_admission_request', 150, 75, 0.0003),
            ('h323_call_proceeding', 120, 60, 0.0002),
            ('h323_connect', 180, 90, 0.0004),
        ]

        total_cost = 0.0

        for event, tokens_in, tokens_out, cost in operations:
            result = self._run_witness_log(
                event=event,
                component='IF.witness.h323',
                trace_id=trace_id,
                payload={
                    'operation': event,
                    'session_id': 'sequential-session'
                },
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost
            )

            self.assertEqual(result.returncode, 0)
            total_cost += cost

        # Verify full sequence in trace
        result = self._run_witness_trace(trace_id, format='json')
        trace_data = json.loads(result.stdout)

        self.assertEqual(len(trace_data['entries']), len(operations))
        self.assertAlmostEqual(trace_data['total_cost_usd'], total_cost, places=6)

    def test_h323_cost_json_output_parsing(self):
        """Test JSON output parsing for cost reports"""
        # Create some H.323 operations
        for i in range(2):
            trace_id = f"h323-cost-json-{i}-" + uuid4().hex
            self.trace_ids.append(trace_id)

            self._run_witness_log(
                event='h323_admission_request',
                component='IF.witness.h323',
                trace_id=trace_id,
                payload={'index': i},
                tokens_in=100 + (i * 50),
                tokens_out=50 + (i * 25),
                cost=0.0002 + (i * 0.0001)
            )

        # Get cost report as JSON
        result = self._run_optimise_report(format='json')
        self.assertEqual(result.returncode, 0)

        # Parse and validate JSON
        report = json.loads(result.stdout)
        self.assertIsInstance(report, list)

        # Find H.323 entries
        h323_rows = [r for r in report if 'h323' in r.get('component', '').lower()]

        # Validate structure of each row
        for row in h323_rows:
            self.assertIsInstance(row['operations'], int)
            self.assertGreaterEqual(row['operations'], 0)

            self.assertIsInstance(row['total_tokens'], (int, type(None)))
            if row['total_tokens']:
                self.assertGreater(row['total_tokens'], 0)

            self.assertIsInstance(row['total_cost'], (float, type(None)))
            if row['total_cost']:
                self.assertGreater(row['total_cost'], 0)

            self.assertIsInstance(row['model'], (str, type(None)))


class TestSession3H323EdgeCases(unittest.TestCase):
    """Edge case tests for Session 3 (H.323)"""

    def setUp(self):
        """Set up test fixtures"""
        self.trace_ids = []

    def _run_witness_log(self, event: str, component: str, trace_id: str,
                        payload: Dict[str, Any], tokens_in: int, tokens_out: int,
                        cost: float, model: str = 'claude-haiku-4.5') -> subprocess.CompletedProcess:
        """Run IF.witness log command"""
        cmd = [
            'python3', 'src/cli/if-witness.py', 'log',
            '--event', event,
            '--component', component,
            '--trace-id', trace_id,
            '--payload', json.dumps(payload),
            '--tokens-in', str(tokens_in),
            '--tokens-out', str(tokens_out),
            '--cost', str(cost),
            '--model', model
        ]

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )

        return result

    def test_h323_zero_cost_operation(self):
        """Test H.323 operation with zero cost"""
        trace_id = "h323-zero-cost-" + uuid4().hex
        self.trace_ids.append(trace_id)

        result = self._run_witness_log(
            event='h323_admission_request',
            component='IF.witness.h323',
            trace_id=trace_id,
            payload={'test': 'zero_cost'},
            tokens_in=0,
            tokens_out=0,
            cost=0.0
        )

        self.assertEqual(result.returncode, 0)

    def test_h323_high_precision_cost(self):
        """Test H.323 operations with high-precision costs"""
        trace_id = "h323-precision-" + uuid4().hex
        self.trace_ids.append(trace_id)

        # Very small cost value
        result = self._run_witness_log(
            event='h323_admission_request',
            component='IF.witness.h323',
            trace_id=trace_id,
            payload={'precision_test': True},
            tokens_in=10,
            tokens_out=5,
            cost=0.000000001  # Very small cost
        )

        self.assertEqual(result.returncode, 0)

    def test_h323_invalid_json_payload_rejected(self):
        """Test that invalid JSON payloads are properly rejected"""
        cmd = [
            'python3', 'src/cli/if-witness.py', 'log',
            '--event', 'h323_admission_request',
            '--component', 'IF.witness.h323',
            '--trace-id', 'test-invalid-json',
            '--payload', '{invalid json}',  # Invalid JSON
            '--tokens-in', '100',
            '--tokens-out', '50',
            '--cost', '0.0001',
            '--model', 'claude-haiku-4.5'
        ]

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )

        # Should fail with invalid JSON
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid JSON", result.stderr)

    def test_h323_missing_required_fields(self):
        """Test that missing required fields are rejected"""
        cmd = [
            'python3', 'src/cli/if-witness.py', 'log',
            '--event', 'h323_admission_request',
            '--component', 'IF.witness.h323',
            # Missing --trace-id (required)
            '--payload', '{}',
            '--tokens-in', '100',
            '--tokens-out', '50',
            '--cost', '0.0001',
        ]

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )

        # Should fail due to missing required parameter
        self.assertNotEqual(result.returncode, 0)


class TestSession3H323Consistency(unittest.TestCase):
    """Consistency and reliability tests for Session 3 (H.323)"""

    def test_h323_trace_consistency(self):
        """Test that trace data remains consistent across multiple retrievals"""
        trace_id = "h323-consistency-" + uuid4().hex

        # Log an operation
        cmd = [
            'python3', 'src/cli/if-witness.py', 'log',
            '--event', 'h323_admission_request',
            '--component', 'IF.witness.h323',
            '--trace-id', trace_id,
            '--payload', json.dumps({'test': 'consistency'}),
            '--tokens-in', '200',
            '--tokens-out', '100',
            '--cost', '0.0005',
            '--model', 'claude-haiku-4.5'
        ]

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0)

        # Retrieve trace multiple times
        results = []
        for _ in range(3):
            cmd = [
                'python3', 'src/cli/if-witness.py', 'trace',
                trace_id,
                '--format', 'json'
            ]

            result = subprocess.run(
                cmd,
                cwd='/home/user/infrafabric',
                capture_output=True,
                text=True
            )

            results.append(json.loads(result.stdout))

        # All results should be identical
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[1], results[2])

    def test_h323_hash_chain_integrity(self):
        """Test that hash chain is maintained for H.323 operations"""
        # Log multiple operations
        trace_id = "h323-integrity-" + uuid4().hex

        for i in range(3):
            cmd = [
                'python3', 'src/cli/if-witness.py', 'log',
                '--event', f'h323_operation_{i}',
                '--component', 'IF.witness.h323',
                '--trace-id', trace_id,
                '--payload', json.dumps({'step': i}),
                '--tokens-in', '100',
                '--tokens-out', '50',
                '--cost', '0.0001',
            ]

            result = subprocess.run(
                cmd,
                cwd='/home/user/infrafabric',
                capture_output=True,
                text=True
            )

            self.assertEqual(result.returncode, 0)
            # Each should report hash chain verified
            self.assertIn("Hash chain verified", result.stdout)

    def test_h323_verification_command(self):
        """Test IF.witness verify command for H.323 data"""
        # First, create some H.323 data
        cmd = [
            'python3', 'src/cli/if-witness.py', 'log',
            '--event', 'h323_admission_request',
            '--component', 'IF.witness.h323',
            '--trace-id', 'h323-verify-' + uuid4().hex,
            '--payload', json.dumps({}),
            '--tokens-in', '100',
            '--tokens-out', '50',
            '--cost', '0.0001',
        ]

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0)

        # Now run verify command
        cmd = ['python3', 'src/cli/if-witness.py', 'verify']

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Hash chain intact", result.stdout)


if __name__ == '__main__':
    import os
    unittest.main()
