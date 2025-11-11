"""
Integration tests for Session 2 (WebRTC) using IF.witness CLI

Tests WebRTC SDP offer/answer handshake with complete trace tracking.
Philosophy: IF.ground Principle 8 - Observability without fragility.
Every operation logged with provenance and hash chain integrity.

Tests:
- WebRTC SDP offer logging with witness trace
- WebRTC SDP answer logging with same trace_id
- ICE candidate logging and tracking
- Complete handshake flow (offer → answer → candidates)
- Trace retrieval showing full operation sequence
- Hash chain verification across distributed operations
"""

import sys
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.witness.database import WitnessDatabase
from src.witness.crypto import WitnessCrypto


class TestSession2WebRTC(unittest.TestCase):
    """Integration tests for WebRTC Session 2 using IF.witness CLI"""

    @classmethod
    def setUpClass(cls):
        """Set up test database and CLI environment"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = Path(cls.temp_dir) / 'test_witness.db'
        cls.key_path = Path(cls.temp_dir) / 'test_key.pem'

        # Initialize database and crypto
        WitnessCrypto(cls.key_path)
        cls.db = WitnessDatabase(cls.db_path)

        # Set environment variable for CLI database path
        import os
        os.environ['WITNESS_DB'] = str(cls.db_path)

    @classmethod
    def tearDownClass(cls):
        """Clean up database and temporary files"""
        cls.db.close()
        import shutil
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def _run_cli_log(self, event, component, trace_id, payload):
        """
        Run IF.witness log command via subprocess.

        Args:
            event: Event type (e.g., 'webrtc_sdp_offer')
            component: Component name (e.g., 'IF.witness.webrtc')
            trace_id: Trace ID linking related operations
            payload: Event payload as dict (will be JSON encoded)

        Returns:
            CompletedProcess result object
        """
        db_path = str(Path(__file__).parent.parent.parent / 'tests' / 'integration' / '.witness.db')
        cmd = [
            'python3', str(Path(__file__).parent.parent.parent / 'src' / 'cli' / 'if-witness.py'),
            '--db', db_path,
            'log',
            '--event', event,
            '--component', component,
            '--trace-id', trace_id,
            '--payload', json.dumps(payload)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        return result

    def _run_cli_trace(self, trace_id, output_format='text'):
        """
        Run IF.witness trace command via subprocess.

        Args:
            trace_id: Trace ID to retrieve
            output_format: 'text' or 'json'

        Returns:
            CompletedProcess result object
        """
        db_path = str(Path(__file__).parent.parent.parent / 'tests' / 'integration' / '.witness.db')
        cmd = [
            'python3', str(Path(__file__).parent.parent.parent / 'src' / 'cli' / 'if-witness.py'),
            '--db', db_path,
            'trace',
            trace_id,
            '--format', output_format
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        return result

    def _run_cli_verify(self):
        """
        Run IF.witness verify command via subprocess.

        Returns:
            CompletedProcess result object
        """
        db_path = str(Path(__file__).parent.parent.parent / 'tests' / 'integration' / '.witness.db')
        cmd = [
            'python3', str(Path(__file__).parent.parent.parent / 'src' / 'cli' / 'if-witness.py'),
            '--db', db_path,
            'verify'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        return result

    def setUp(self):
        """Create fresh database for each test"""
        self.test_db_path = Path(Path(__file__).parent.parent.parent / 'tests' / 'integration' / '.witness.db')
        # Remove old test database if it exists
        if self.test_db_path.exists():
            self.test_db_path.unlink()
        # Create fresh database
        self.db = WitnessDatabase(self.test_db_path)
        self.db.close()

    def tearDown(self):
        """Clean up test database"""
        if self.test_db_path.exists():
            self.test_db_path.unlink()
        # Also clean up parent directory if empty
        parent_dir = self.test_db_path.parent
        try:
            if parent_dir.exists() and parent_dir.name == 'integration':
                # Keep the directory, just clean the db file
                pass
        except:
            pass

    def test_webrtc_sdp_offer_witness(self):
        """Test WebRTC SDP offer logging with witness trace"""
        trace_id = "webrtc-session-" + uuid4().hex

        # Log SDP offer
        result = self._run_cli_log(
            event='webrtc_sdp_offer',
            component='IF.witness.webrtc',
            trace_id=trace_id,
            payload={
                'session_id': 'session-abc123',
                'offer_type': 'video',
                'ice_candidates': 5,
                'codec': 'vp8'
            }
        )

        # Verify CLI succeeded
        self.assertEqual(result.returncode, 0, f"CLI failed: {result.stderr}")
        self.assertIn('Witness entry created', result.stdout)
        self.assertIn('Hash chain verified', result.stdout)

    def test_webrtc_sdp_answer_witness(self):
        """Test WebRTC SDP answer logging with witness trace"""
        trace_id = "webrtc-session-" + uuid4().hex

        # Log SDP answer
        result = self._run_cli_log(
            event='webrtc_sdp_answer',
            component='IF.witness.webrtc',
            trace_id=trace_id,
            payload={
                'session_id': 'session-xyz789',
                'answer_type': 'video',
                'ice_candidates': 3,
                'codec': 'vp8'
            }
        )

        # Verify CLI succeeded
        self.assertEqual(result.returncode, 0, f"CLI failed: {result.stderr}")
        self.assertIn('Witness entry created', result.stdout)

    def test_webrtc_ice_candidate_witness(self):
        """Test WebRTC ICE candidate logging"""
        trace_id = "webrtc-session-" + uuid4().hex

        # Log ICE candidate
        result = self._run_cli_log(
            event='webrtc_ice_candidate',
            component='IF.witness.webrtc',
            trace_id=trace_id,
            payload={
                'session_id': 'session-def456',
                'candidate': 'candidate:12345 1 udp 2122260223 192.168.1.100 54321 typ host',
                'candidate_type': 'host',
                'foundation': '12345'
            }
        )

        # Verify CLI succeeded
        self.assertEqual(result.returncode, 0, f"CLI failed: {result.stderr}")
        self.assertIn('Witness entry created', result.stdout)

    def test_webrtc_complete_handshake_flow(self):
        """Test complete WebRTC handshake flow (offer → answer → candidates)"""
        trace_id = "webrtc-handshake-" + uuid4().hex
        session_id = "session-" + uuid4().hex

        # Step 1: Log SDP offer
        result_offer = self._run_cli_log(
            event='webrtc_sdp_offer',
            component='IF.witness.webrtc',
            trace_id=trace_id,
            payload={
                'session_id': session_id,
                'offer_type': 'video',
                'ice_candidates': 5,
                'codec': 'vp8',
                'video_resolution': '1920x1080'
            }
        )
        self.assertEqual(result_offer.returncode, 0, f"Offer failed: {result_offer.stderr}")

        # Step 2: Log SDP answer with same trace_id
        result_answer = self._run_cli_log(
            event='webrtc_sdp_answer',
            component='IF.witness.webrtc',
            trace_id=trace_id,
            payload={
                'session_id': session_id,
                'answer_type': 'video',
                'ice_candidates': 4,
                'codec': 'vp8',
                'video_resolution': '1920x1080'
            }
        )
        self.assertEqual(result_answer.returncode, 0, f"Answer failed: {result_answer.stderr}")

        # Step 3: Log ICE candidates
        for i in range(3):
            result_ice = self._run_cli_log(
                event='webrtc_ice_candidate',
                component='IF.witness.webrtc',
                trace_id=trace_id,
                payload={
                    'session_id': session_id,
                    'candidate': f'candidate:{i} 1 udp 2122260223 192.168.1.{100+i} {54321+i} typ host',
                    'candidate_type': 'host',
                    'foundation': str(i),
                    'sequence': i
                }
            )
            self.assertEqual(result_ice.returncode, 0, f"ICE candidate {i} failed: {result_ice.stderr}")

        # Step 4: Verify hash chain
        result_verify = self._run_cli_verify()
        self.assertEqual(result_verify.returncode, 0, f"Verify failed: {result_verify.stderr}")
        self.assertIn('entries verified', result_verify.stdout.lower())

    def test_trace_retrieval_offer_answer_chain(self):
        """Test trace retrieval showing offer → answer chain"""
        trace_id = "webrtc-trace-" + uuid4().hex

        # Log offer
        self._run_cli_log(
            event='webrtc_sdp_offer',
            component='IF.witness.webrtc',
            trace_id=trace_id,
            payload={
                'session_id': 'trace-session-1',
                'offer_type': 'video',
                'ice_candidates': 5
            }
        )

        # Log answer
        self._run_cli_log(
            event='webrtc_sdp_answer',
            component='IF.witness.webrtc',
            trace_id=trace_id,
            payload={
                'session_id': 'trace-session-1',
                'answer_type': 'video',
                'ice_candidates': 5
            }
        )

        # Retrieve trace in text format
        result_text = self._run_cli_trace(trace_id, output_format='text')
        self.assertEqual(result_text.returncode, 0, f"Trace failed: {result_text.stderr}")
        self.assertIn(trace_id, result_text.stdout)
        self.assertIn('webrtc_sdp_offer', result_text.stdout)
        self.assertIn('webrtc_sdp_answer', result_text.stdout)

        # Verify order: offer should come before answer
        offer_index = result_text.stdout.find('webrtc_sdp_offer')
        answer_index = result_text.stdout.find('webrtc_sdp_answer')
        self.assertLess(offer_index, answer_index, "Offer should appear before answer in trace")

    def test_trace_retrieval_json_format(self):
        """Test trace retrieval in JSON format"""
        trace_id = "webrtc-json-" + uuid4().hex

        # Log multiple events
        self._run_cli_log(
            event='webrtc_sdp_offer',
            component='IF.witness.webrtc',
            trace_id=trace_id,
            payload={'session_id': 'json-test', 'offer_type': 'audio'}
        )

        self._run_cli_log(
            event='webrtc_ice_candidate',
            component='IF.witness.webrtc',
            trace_id=trace_id,
            payload={'session_id': 'json-test', 'candidate_type': 'host'}
        )

        # Retrieve trace in JSON format
        result = self._run_cli_trace(trace_id, output_format='json')
        self.assertEqual(result.returncode, 0, f"JSON trace failed: {result.stderr}")

        # Parse JSON
        trace_data = json.loads(result.stdout)
        self.assertEqual(trace_data['trace_id'], trace_id)
        self.assertIn('entries', trace_data)
        self.assertGreater(len(trace_data['entries']), 0)
        self.assertIn('IF.witness.webrtc', trace_data['components'])

    def test_trace_shows_all_steps_in_order(self):
        """Test trace shows all WebRTC handshake steps in correct order"""
        trace_id = "webrtc-order-" + uuid4().hex

        # Log events in specific order
        events = [
            ('webrtc_session_start', {'session_id': 'order-test', 'initiator': True}),
            ('webrtc_sdp_offer', {'session_id': 'order-test', 'offer_type': 'video'}),
            ('webrtc_sdp_answer', {'session_id': 'order-test', 'answer_type': 'video'}),
            ('webrtc_ice_candidate', {'session_id': 'order-test', 'candidate_type': 'host'}),
            ('webrtc_connection_established', {'session_id': 'order-test', 'state': 'connected'})
        ]

        for event_type, payload in events:
            result = self._run_cli_log(
                event=event_type,
                component='IF.witness.webrtc',
                trace_id=trace_id,
                payload=payload
            )
            self.assertEqual(result.returncode, 0, f"Event {event_type} failed: {result.stderr}")

        # Retrieve trace in JSON
        result = self._run_cli_trace(trace_id, output_format='json')
        self.assertEqual(result.returncode, 0)

        trace_data = json.loads(result.stdout)
        returned_events = [entry['event'] for entry in trace_data['entries']]

        # Verify all events are present
        for event_type, _ in events:
            self.assertIn(event_type, returned_events, f"Missing event: {event_type}")

        # Verify order is preserved
        expected_order = [e[0] for e in events]
        self.assertEqual(returned_events, expected_order, "Event order not preserved")

    def test_multiple_parallel_webrtc_traces(self):
        """Test multiple parallel WebRTC sessions tracked independently"""
        trace_ids = ["webrtc-parallel-1-" + uuid4().hex, "webrtc-parallel-2-" + uuid4().hex]

        # Log events for two different sessions
        for trace_id in trace_ids:
            # Each session logs offer and answer
            self._run_cli_log(
                event='webrtc_sdp_offer',
                component='IF.witness.webrtc',
                trace_id=trace_id,
                payload={'session_id': f'session-{trace_id[:8]}', 'offer_type': 'video'}
            )

            self._run_cli_log(
                event='webrtc_sdp_answer',
                component='IF.witness.webrtc',
                trace_id=trace_id,
                payload={'session_id': f'session-{trace_id[:8]}', 'answer_type': 'video'}
            )

        # Retrieve each trace independently
        for trace_id in trace_ids:
            result = self._run_cli_trace(trace_id, output_format='json')
            self.assertEqual(result.returncode, 0)

            trace_data = json.loads(result.stdout)
            self.assertEqual(trace_data['trace_id'], trace_id)
            self.assertEqual(len(trace_data['entries']), 2)  # offer + answer

    def test_webrtc_with_cost_tracking(self):
        """Test WebRTC operations with cost tracking (token usage, cost)"""
        trace_id = "webrtc-cost-" + uuid4().hex

        # Log SDP offer with cost information
        db_path = str(Path(__file__).parent.parent.parent / 'tests' / 'integration' / '.witness.db')
        cmd = [
            'python3', str(Path(__file__).parent.parent.parent / 'src' / 'cli' / 'if-witness.py'),
            '--db', db_path,
            'log',
            '--event', 'webrtc_sdp_offer',
            '--component', 'IF.witness.webrtc',
            '--trace-id', trace_id,
            '--payload', json.dumps({'session_id': 'cost-test', 'offer_type': 'video'}),
            '--tokens-in', '150',
            '--tokens-out', '100',
            '--cost', '0.00035',
            '--model', 'claude-haiku-4.5'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Cost logging failed: {result.stderr}")
        self.assertIn('Cost:', result.stdout)
        self.assertIn('0.00035', result.stdout)
        self.assertIn('250 tokens', result.stdout)

    def test_hash_chain_integrity_across_operations(self):
        """Test hash chain integrity is maintained across WebRTC operations"""
        trace_id = "webrtc-integrity-" + uuid4().hex

        # Log multiple operations
        for i in range(5):
            self._run_cli_log(
                event=f'webrtc_event_{i}',
                component='IF.witness.webrtc',
                trace_id=trace_id,
                payload={'step': i, 'session_id': 'integrity-test'}
            )

        # Verify hash chain
        result = self._run_cli_verify()
        self.assertEqual(result.returncode, 0, f"Verification failed: {result.stderr}")
        self.assertIn('verified', result.stdout.lower())
        self.assertIn('intact', result.stdout.lower())

    def test_webrtc_connection_state_tracking(self):
        """Test tracking WebRTC connection state transitions"""
        trace_id = "webrtc-state-" + uuid4().hex
        session_id = "state-session-" + uuid4().hex

        states = [
            ('new', 'new'),
            ('connecting', 'connecting'),
            ('connected', 'connected'),
            ('completed', 'completed')
        ]

        # Log state transitions
        for state, description in states:
            result = self._run_cli_log(
                event='webrtc_connection_state_change',
                component='IF.witness.webrtc',
                trace_id=trace_id,
                payload={
                    'session_id': session_id,
                    'new_state': state,
                    'previous_state': states[max(0, states.index((state, description))-1)][0] if states.index((state, description)) > 0 else None
                }
            )
            self.assertEqual(result.returncode, 0, f"State change {state} failed: {result.stderr}")

        # Retrieve and verify states are logged in order
        result = self._run_cli_trace(trace_id, output_format='json')
        trace_data = json.loads(result.stdout)
        self.assertEqual(len(trace_data['entries']), len(states))

    def test_invalid_payload_error_handling(self):
        """Test error handling for invalid JSON payload"""
        trace_id = "webrtc-error-" + uuid4().hex

        db_path = str(Path(__file__).parent.parent.parent / 'tests' / 'integration' / '.witness.db')
        cmd = [
            'python3', str(Path(__file__).parent.parent.parent / 'src' / 'cli' / 'if-witness.py'),
            '--db', db_path,
            'log',
            '--event', 'webrtc_sdp_offer',
            '--component', 'IF.witness.webrtc',
            '--trace-id', trace_id,
            '--payload', 'invalid json {{{'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, "Should fail with invalid JSON")
        self.assertIn('Invalid JSON', result.stderr)

    def test_missing_required_parameters(self):
        """Test error handling for missing required parameters"""
        # Missing trace-id
        db_path = str(Path(__file__).parent.parent.parent / 'tests' / 'integration' / '.witness.db')
        cmd = [
            'python3', str(Path(__file__).parent.parent.parent / 'src' / 'cli' / 'if-witness.py'),
            '--db', db_path,
            'log',
            '--event', 'webrtc_sdp_offer',
            '--component', 'IF.witness.webrtc',
            '--payload', json.dumps({'test': 'data'})
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, "Should fail with missing trace-id")

    def test_trace_nonexistent_trace_id(self):
        """Test error handling for nonexistent trace_id"""
        nonexistent_trace = "webrtc-nonexistent-" + uuid4().hex

        result = self._run_cli_trace(nonexistent_trace)
        self.assertNotEqual(result.returncode, 0, "Should fail for nonexistent trace")
        self.assertIn('No entries found', result.stderr)

    def test_webrtc_payload_with_complex_structure(self):
        """Test WebRTC events with complex nested payload structures"""
        trace_id = "webrtc-complex-" + uuid4().hex

        complex_payload = {
            'session_id': 'complex-session',
            'sdp': {
                'type': 'offer',
                'media': [
                    {
                        'type': 'video',
                        'codecs': ['vp8', 'h264'],
                        'rtcp_feedback': ['ccm fir', 'nack', 'nack pli']
                    },
                    {
                        'type': 'audio',
                        'codecs': ['opus'],
                        'sample_rate': 48000
                    }
                ]
            },
            'ice_credentials': {
                'username': 'user123',
                'password': 'pass456',
                'refresh_interval': 3600
            },
            'stats': {
                'cpu_usage': 45.2,
                'memory_usage': 128.5,
                'network_latency_ms': 12.5
            }
        }

        result = self._run_cli_log(
            event='webrtc_sdp_offer',
            component='IF.witness.webrtc',
            trace_id=trace_id,
            payload=complex_payload
        )

        self.assertEqual(result.returncode, 0, f"Complex payload failed: {result.stderr}")

        # Verify the payload is stored and retrievable
        result = self._run_cli_trace(trace_id, output_format='json')
        trace_data = json.loads(result.stdout)
        stored_payload = json.loads(trace_data['entries'][0]['payload'])
        self.assertEqual(stored_payload['session_id'], 'complex-session')
        self.assertEqual(len(stored_payload['sdp']['media']), 2)


if __name__ == '__main__':
    unittest.main()
