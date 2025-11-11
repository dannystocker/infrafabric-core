"""
Integration tests for Session 4 (SIP) using IF.witness CLI

Tests:
- SIP ESCALATE call logging via CLI
- Complete SIP call flow: INVITE → ESCALATE → ACK
- Hash chain verification after each operation
- Export of SIP call records (JSON and CSV)
- Cost tracking for SIP operations

Philosophy: IF.ground Principle 8 - Observability without fragility
Every SIP operation logged with provenance (who, what, when, why)
"""

import sys
import json
import tempfile
import subprocess
import unittest
from pathlib import Path
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.witness.database import WitnessDatabase
from src.witness.crypto import WitnessCrypto


class TestSIPEscalateLogging(unittest.TestCase):
    """Test SIP ESCALATE call logging"""

    def setUp(self):
        """Create temporary database for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_sip.db'
        self.key_path = Path(self.temp_dir) / 'test_key.pem'

        self.crypto = WitnessCrypto(self.key_path)
        self.db = WitnessDatabase(self.db_path, self.crypto)

        # Set database path for CLI
        self.db_arg = f"--db={self.db_path}"

    def tearDown(self):
        """Clean up database"""
        self.db.close()

    def test_sip_escalate_witness_logging(self):
        """Test logging SIP ESCALATE call via CLI"""
        trace_id = "sip-call-" + uuid4().hex

        # Log ESCALATE request
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'priority': 'high',
                'reason': 'emergency',
                'call_id': 'call-' + uuid4().hex
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0, f"CLI error: {result.stderr.decode()}")

        # Verify output
        output = result.stdout.decode()
        self.assertIn("Witness entry created", output)
        self.assertIn("Hash chain verified", output)
        self.assertIn("ed25519:", output)

    def test_sip_escalate_with_cost_tracking(self):
        """Test logging SIP ESCALATE with cost information"""
        trace_id = "sip-escalate-cost-" + uuid4().hex

        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'priority': 'critical',
                'reason': 'system_failure'
            }),
            '--tokens-in', '150',
            '--tokens-out', '200',
            '--cost', '0.0035',
            '--model', 'claude-haiku-4.5'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0, f"CLI error: {result.stderr.decode()}")

        output = result.stdout.decode()
        self.assertIn("Witness entry created", output)
        self.assertIn("0.0035", output)
        self.assertIn("350 tokens", output)

    def test_sip_multiple_escalates_same_trace(self):
        """Test logging multiple ESCALATE calls with same trace ID"""
        trace_id = "sip-multi-escalate-" + uuid4().hex

        # Log first escalate
        result1 = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'attempt': 1,
                'priority': 'high'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result1.returncode, 0)

        # Log second escalate with same trace
        result2 = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'charlie@example.com',
                'attempt': 2,
                'priority': 'critical'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result2.returncode, 0)


class TestSIPCallFlow(unittest.TestCase):
    """Test complete SIP call flow: INVITE → ESCALATE → ACK"""

    def setUp(self):
        """Create temporary database for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_sip_flow.db'
        self.key_path = Path(self.temp_dir) / 'test_key.pem'

        self.crypto = WitnessCrypto(self.key_path)
        self.db = WitnessDatabase(self.db_path, self.crypto)

        self.db_arg = f"--db={self.db_path}"
        self.trace_id = "sip-flow-" + uuid4().hex

    def tearDown(self):
        """Clean up database"""
        self.db.close()

    def test_sip_call_flow_invite_escalate_ack(self):
        """Test complete SIP call flow with INVITE, ESCALATE, and ACK"""

        # Step 1: Log INVITE
        result_invite = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_invite',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'method': 'INVITE',
                'call_id': 'call-' + uuid4().hex,
                'cseq': 1,
                'via': 'SIP/2.0/UDP 192.168.1.100'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result_invite.returncode, 0,
                        f"INVITE failed: {result_invite.stderr.decode()}")
        self.assertIn("Witness entry created", result_invite.stdout.decode())

        # Step 2: Log ESCALATE
        result_escalate = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'method': 'ESCALATE',
                'priority': 'high',
                'reason': 'network_quality',
                'call_id': 'call-' + uuid4().hex,
                'cseq': 2,
                'previous_state': 'ringing'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result_escalate.returncode, 0,
                        f"ESCALATE failed: {result_escalate.stderr.decode()}")
        self.assertIn("Witness entry created", result_escalate.stdout.decode())

        # Step 3: Log ACK
        result_ack = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_ack',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'bob@example.com',
                'to': 'alice@example.com',
                'method': 'ACK',
                'priority': 'high',
                'state': 'established',
                'call_id': 'call-' + uuid4().hex,
                'cseq': 2
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result_ack.returncode, 0,
                        f"ACK failed: {result_ack.stderr.decode()}")
        self.assertIn("Witness entry created", result_ack.stdout.decode())

    def test_sip_call_flow_with_hash_chain_verification(self):
        """Test that hash chain is verified after each SIP operation"""

        # Log INVITE
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_invite',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'method': 'INVITE',
                'via': 'SIP/2.0/UDP 192.168.1.100'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Verify after INVITE
        verify_result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'verify'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(verify_result.returncode, 0)
        output = verify_result.stdout.decode()
        self.assertIn("1 entries verified", output)
        self.assertIn("Hash chain intact", output)

        # Log ESCALATE
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'priority': 'high',
                'reason': 'quality'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Verify after ESCALATE
        verify_result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'verify'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(verify_result.returncode, 0)
        output = verify_result.stdout.decode()
        self.assertIn("2 entries verified", output)
        self.assertIn("Hash chain intact", output)

        # Log ACK
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_ack',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'bob@example.com',
                'to': 'alice@example.com',
                'state': 'established'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Verify after ACK
        verify_result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'verify'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(verify_result.returncode, 0)
        output = verify_result.stdout.decode()
        self.assertIn("3 entries verified", output)
        self.assertIn("Hash chain intact", output)


class TestSIPHashChainVerification(unittest.TestCase):
    """Test hash chain verification for SIP call logs"""

    def setUp(self):
        """Create temporary database for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_sip_verify.db'
        self.key_path = Path(self.temp_dir) / 'test_key.pem'

        self.crypto = WitnessCrypto(self.key_path)
        self.db = WitnessDatabase(self.db_path, self.crypto)

        self.db_arg = f"--db={self.db_path}"
        self.trace_id = "sip-verify-" + uuid4().hex

    def tearDown(self):
        """Clean up database"""
        self.db.close()

    def test_sip_verify_call_log_empty(self):
        """Test verification of empty call log"""
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'verify'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode()
        self.assertIn("verified", output.lower())

    def test_sip_verify_call_log_single_entry(self):
        """Test verification of single SIP call log entry"""
        # Log single ESCALATE call
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'priority': 'high'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Verify
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'verify'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode()
        self.assertIn("1 entries verified", output)
        self.assertIn("Hash chain intact", output)

    def test_sip_verify_call_log_multiple_entries(self):
        """Test verification of multiple SIP call log entries"""
        # Log multiple ESCALATE calls
        for i in range(5):
            subprocess.run([
                'python3', 'src/cli/if-witness.py',
                self.db_arg,
                'log',
                '--event', 'sip_escalate',
                '--component', 'IF.witness.sip',
                '--trace-id', self.trace_id,
                '--payload', json.dumps({
                    'from': 'user' + str(i) + '@example.com',
                    'to': 'user' + str((i+1) % 5) + '@example.com',
                    'priority': 'high' if i % 2 == 0 else 'critical',
                    'attempt': i + 1
                })
            ], capture_output=True, cwd='/home/user/infrafabric')

        # Verify
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'verify'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode()
        self.assertIn("5 entries verified", output)
        self.assertIn("Hash chain intact", output)
        self.assertIn("All signatures valid", output)

    def test_sip_verify_provides_hash_details(self):
        """Test that verify command provides detailed hash information"""
        # Log SIP entry
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'priority': 'high'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Verify
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'verify'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode()
        self.assertIn("✓", output)  # Success indicator
        self.assertIn("verified", output.lower())


class TestSIPTraceRetrieval(unittest.TestCase):
    """Test trace retrieval for SIP calls"""

    def setUp(self):
        """Create temporary database for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_sip_trace.db'
        self.key_path = Path(self.temp_dir) / 'test_key.pem'

        self.crypto = WitnessCrypto(self.key_path)
        self.db = WitnessDatabase(self.db_path, self.crypto)

        self.db_arg = f"--db={self.db_path}"
        self.trace_id = "sip-trace-" + uuid4().hex

    def tearDown(self):
        """Clean up database"""
        self.db.close()

    def test_sip_trace_single_escalate(self):
        """Test trace retrieval for single SIP ESCALATE"""
        # Log ESCALATE
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'priority': 'high'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Trace
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'trace', self.trace_id
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode()
        self.assertIn(self.trace_id, output)
        self.assertIn("sip_escalate", output)
        self.assertIn("IF.witness.sip", output)

    def test_sip_trace_call_flow(self):
        """Test trace retrieval for complete SIP call flow"""
        # Log INVITE
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_invite',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'method': 'INVITE'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Log ESCALATE
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'priority': 'high'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Log ACK
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_ack',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'bob@example.com',
                'to': 'alice@example.com',
                'state': 'established'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Trace
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'trace', self.trace_id
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode()
        self.assertIn(self.trace_id, output)
        self.assertIn("sip_invite", output)
        self.assertIn("sip_escalate", output)
        self.assertIn("sip_ack", output)

    def test_sip_trace_json_format(self):
        """Test trace retrieval in JSON format"""
        # Log ESCALATE
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'priority': 'high'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Trace in JSON format
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'trace', self.trace_id,
            '--format', 'json'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode()

        # Parse JSON
        trace_data = json.loads(output)
        self.assertEqual(trace_data['trace_id'], self.trace_id)
        self.assertEqual(len(trace_data['entries']), 1)
        self.assertEqual(trace_data['entries'][0]['event'], 'sip_escalate')


class TestSIPExport(unittest.TestCase):
    """Test export of SIP call records"""

    def setUp(self):
        """Create temporary database for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_sip_export.db'
        self.key_path = Path(self.temp_dir) / 'test_key.pem'

        self.crypto = WitnessCrypto(self.key_path)
        self.db = WitnessDatabase(self.db_path, self.crypto)

        self.db_arg = f"--db={self.db_path}"
        self.trace_id = "sip-export-" + uuid4().hex

    def tearDown(self):
        """Clean up database"""
        self.db.close()

    def test_sip_export_json_empty(self):
        """Test JSON export of empty SIP log"""
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'export',
            '--format', 'json'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode()

        # Parse JSON
        data = json.loads(output)
        self.assertEqual(len(data), 0)

    def test_sip_export_json_single_entry(self):
        """Test JSON export of single SIP entry"""
        # Log ESCALATE
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'priority': 'high',
                'call_id': 'call-123'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Export
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'export',
            '--format', 'json'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode()

        # Parse JSON
        data = json.loads(output)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['event'], 'sip_escalate')
        self.assertEqual(data[0]['component'], 'IF.witness.sip')
        self.assertEqual(data[0]['trace_id'], self.trace_id)
        self.assertIn('content_hash', data[0])
        self.assertIn('signature', data[0])

    def test_sip_export_json_multiple_entries(self):
        """Test JSON export of multiple SIP entries"""
        # Log INVITE, ESCALATE, ACK
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_invite',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'priority': 'high'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_ack',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'bob@example.com',
                'to': 'alice@example.com'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Export
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'export',
            '--format', 'json'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode()

        # Parse JSON
        data = json.loads(output)
        self.assertEqual(len(data), 3)

        # Verify order
        self.assertEqual(data[0]['event'], 'sip_invite')
        self.assertEqual(data[1]['event'], 'sip_escalate')
        self.assertEqual(data[2]['event'], 'sip_ack')

    def test_sip_export_json_to_file(self):
        """Test JSON export to file"""
        # Log ESCALATE
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'priority': 'high'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Export to file
        export_file = Path(self.temp_dir) / 'export.json'
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'export',
            '--format', 'json',
            '--output', str(export_file)
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        self.assertTrue(export_file.exists())

        # Verify file content
        data = json.loads(export_file.read_text())
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['event'], 'sip_escalate')

    def test_sip_export_csv_single_entry(self):
        """Test CSV export of single SIP entry"""
        # Log ESCALATE with cost
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'priority': 'high'
            }),
            '--tokens-in', '100',
            '--tokens-out', '50',
            '--cost', '0.0015',
            '--model', 'claude-haiku-4.5'
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Export
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'export',
            '--format', 'csv'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode()

        # Verify CSV content
        lines = output.strip().split('\n')
        self.assertEqual(len(lines), 2)  # Header + 1 entry

        # Header should contain expected fields
        header = lines[0]
        self.assertIn('id', header)
        self.assertIn('event', header)
        self.assertIn('component', header)
        self.assertIn('cost_usd', header)

    def test_sip_export_csv_to_file(self):
        """Test CSV export to file"""
        # Log ESCALATE
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'from': 'alice@example.com',
                'to': 'bob@example.com',
                'priority': 'high'
            })
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Export to file
        export_file = Path(self.temp_dir) / 'export.csv'
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'export',
            '--format', 'csv',
            '--output', str(export_file)
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        self.assertTrue(export_file.exists())

        # Verify file content
        content = export_file.read_text()
        lines = content.strip().split('\n')
        self.assertEqual(len(lines), 2)  # Header + 1 entry
        self.assertIn('sip_escalate', content)


class TestSIPCostTracking(unittest.TestCase):
    """Test cost tracking for SIP operations"""

    def setUp(self):
        """Create temporary database for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_sip_cost.db'
        self.key_path = Path(self.temp_dir) / 'test_key.pem'

        self.crypto = WitnessCrypto(self.key_path)
        self.db = WitnessDatabase(self.db_path, self.crypto)

        self.db_arg = f"--db={self.db_path}"
        self.trace_id = "sip-cost-" + uuid4().hex

    def tearDown(self):
        """Clean up database"""
        self.db.close()

    def test_sip_cost_breakdown_single_trace(self):
        """Test cost breakdown for a single SIP trace"""
        # Log INVITE with cost
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_invite',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({'from': 'alice@example.com'}),
            '--tokens-in', '100',
            '--tokens-out', '50',
            '--cost', '0.001',
            '--model', 'claude-haiku-4.5'
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Log ESCALATE with cost
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({'from': 'alice@example.com', 'priority': 'high'}),
            '--tokens-in', '150',
            '--tokens-out', '200',
            '--cost', '0.0035',
            '--model', 'claude-haiku-4.5'
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Get cost breakdown
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'cost',
            '--trace-id', self.trace_id
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode()

        # Verify cost information
        self.assertIn(self.trace_id, output)
        self.assertIn("IF.witness.sip", output)
        self.assertIn("0.0045", output)  # Total: 0.001 + 0.0035
        self.assertIn("500", output)  # Total tokens: 100+50+150+200

    def test_sip_cost_breakdown_json_format(self):
        """Test cost breakdown in JSON format"""
        # Log ESCALATE with cost
        subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'log',
            '--event', 'sip_escalate',
            '--component', 'IF.witness.sip',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({'from': 'alice@example.com'}),
            '--tokens-in', '200',
            '--tokens-out', '100',
            '--cost', '0.009',
            '--model', 'claude-sonnet-4.5'
        ], capture_output=True, cwd='/home/user/infrafabric')

        # Get cost breakdown in JSON
        result = subprocess.run([
            'python3', 'src/cli/if-witness.py',
            self.db_arg,
            'cost',
            '--trace-id', self.trace_id,
            '--format', 'json'
        ], capture_output=True, cwd='/home/user/infrafabric')

        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode()

        # Parse JSON
        cost_data = json.loads(output)
        self.assertEqual(cost_data['trace_id'], self.trace_id)
        self.assertAlmostEqual(cost_data['total_cost_usd'], 0.009, places=4)
        self.assertEqual(cost_data['total_tokens'], 300)


if __name__ == '__main__':
    unittest.main()
