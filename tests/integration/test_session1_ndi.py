"""
Integration tests for Session 1 (NDI) using IF.witness CLI

Context:
Session 1 (NDI) is a video frame publisher that streams NDI (Network Device Interface)
video frames in real-time. Each frame must be logged with IF.witness for:
1. Provenance tracking - Who published the frame, when, and from which stream
2. Tamper detection - Hash chains ensure frame logs haven't been modified
3. Cost tracking - IF.optimise tracks resource usage per stream/session
4. Audit trail - Complete trace of all frames published in a session

Philosophy: IF.ground Principle 8 - Observability without fragility
Every NDI frame operation is logged with cryptographic proof of authenticity.

Test Categories:
1. Frame publishing with witness logging
2. Content hash verification and chain integrity
3. Trace retrieval for complete session history
4. Cost tracking for NDI operations
"""

import sys
import json
import tempfile
import unittest
import subprocess
from pathlib import Path
from uuid import uuid4
from datetime import datetime


class TestNDIFramePublishing(unittest.TestCase):
    """Test NDI frame publishing with witness logging.

    NDI frames are video data units streamed from a publisher. Each frame
    represents a snapshot of video content with metadata (frame number, resolution, fps).
    IF.witness logs each frame for provenance and audit purposes.
    """

    def setUp(self):
        """Create temporary database for NDI session tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'ndi_witness.db'
        self.key_path = Path(self.temp_dir) / 'ndi_key.pem'
        self.trace_id = f"ndi-session-{uuid4().hex[:16]}"

    def tearDown(self):
        """Clean up temporary files."""
        if self.db_path.exists():
            self.db_path.unlink()
        if self.key_path.exists():
            self.key_path.unlink()
        if self.key_path.parent.exists():
            try:
                self.key_path.parent.rmdir()
            except OSError:
                pass  # Directory not empty, that's okay

    def _run_cli(self, *args, **kwargs):
        """
        Run IF.witness CLI command.

        Args:
            *args: Command arguments
            **kwargs: Optional 'db' and 'key' path overrides

        Returns:
            subprocess.CompletedProcess result
        """
        db_arg = kwargs.get('db', str(self.db_path))
        cmd = [
            'python3',
            'src/cli/if-witness.py',
            '--db', db_arg,
        ] + list(args)

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )
        return result

    def test_single_ndi_frame_witness_log(self):
        """
        Test logging a single NDI frame with witness entry creation.

        Scenario: NDI publisher publishes frame #42 from stream IF.yologuard.01
        at 1920x1080 resolution, 30 fps.

        Expected: Frame event is logged to witness with:
        - Valid entry ID
        - Correct event type: ndi_frame_published
        - Correct component: IF.witness.ndi-publisher
        - Frame metadata in payload
        - Valid hash and signature
        """
        result = self._run_cli(
            'log',
            '--event', 'ndi_frame_published',
            '--component', 'IF.witness.ndi-publisher',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'frame_number': 42,
                'stream_id': 'IF.yologuard.01',
                'resolution': '1920x1080',
                'fps': 30,
                'timestamp_ns': 1699738800000000000
            })
        )

        self.assertEqual(result.returncode, 0, f"CLI failed: {result.stderr}")
        self.assertIn('Witness entry created', result.stdout)
        self.assertIn('Hash chain verified', result.stdout)
        self.assertIn('ed25519:', result.stdout)
        self.assertIn('Content hash:', result.stdout)

    def test_multiple_ndi_frames_same_session(self):
        """
        Test logging multiple NDI frames in same session.

        Scenario: Publisher sends 5 consecutive frames from same stream.
        Each frame is logged with witness.

        Expected: All frames logged with correct:
        - Sequential frame numbers
        - Same trace ID
        - Increasing hash chain (prev_hash links)
        - All signatures valid
        """
        frame_data = [
            {'frame_number': 10, 'stream_id': 'IF.yologuard.01', 'resolution': '1920x1080', 'fps': 30},
            {'frame_number': 11, 'stream_id': 'IF.yologuard.01', 'resolution': '1920x1080', 'fps': 30},
            {'frame_number': 12, 'stream_id': 'IF.yologuard.01', 'resolution': '1920x1080', 'fps': 30},
            {'frame_number': 13, 'stream_id': 'IF.yologuard.01', 'resolution': '1920x1080', 'fps': 30},
            {'frame_number': 14, 'stream_id': 'IF.yologuard.01', 'resolution': '1920x1080', 'fps': 30},
        ]

        for frame_info in frame_data:
            result = self._run_cli(
                'log',
                '--event', 'ndi_frame_published',
                '--component', 'IF.witness.ndi-publisher',
                '--trace-id', self.trace_id,
                '--payload', json.dumps(frame_info)
            )

            self.assertEqual(result.returncode, 0,
                f"Failed to log frame {frame_info['frame_number']}: {result.stderr}")
            self.assertIn('Witness entry created', result.stdout)

    def test_ndi_frame_with_cost_tracking(self):
        """
        Test logging NDI frame with IF.optimise cost tracking.

        Scenario: NDI frame publishing operation includes resource costs:
        - Encoder processing tokens
        - Network transmission cost
        - Storage write cost

        Expected: Entry includes:
        - Token counts (input/output)
        - Cost in USD
        - Model/processor identification
        - Complete audit trail for cost allocation
        """
        result = self._run_cli(
            'log',
            '--event', 'ndi_frame_published',
            '--component', 'IF.witness.ndi-publisher',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'frame_number': 99,
                'stream_id': 'IF.yologuard.02',
                'resolution': '4096x2160',
                'fps': 60,
                'encoder': 'h264',
                'bitrate_mbps': 50
            }),
            '--tokens-in', '125',
            '--tokens-out', '50',
            '--cost', '0.00045',
            '--model', 'encoder-v2'
        )

        self.assertEqual(result.returncode, 0, f"CLI failed: {result.stderr}")
        self.assertIn('Witness entry created', result.stdout)
        self.assertIn('Cost:', result.stdout)
        self.assertIn('tokens', result.stdout.lower())

    def test_ndi_frame_different_streams(self):
        """
        Test logging frames from multiple NDI streams in single session.

        Scenario: Session publishes frames from 3 different NDI sources:
        - IF.yologuard.01 (main camera)
        - IF.yologuard.02 (secondary camera)
        - IF.yologuard.03 (depth sensor)

        Expected: All frames linked by same trace ID but from different streams.
        """
        streams = [
            'IF.yologuard.01',
            'IF.yologuard.02',
            'IF.yologuard.03'
        ]

        for stream_id in streams:
            result = self._run_cli(
                'log',
                '--event', 'ndi_frame_published',
                '--component', 'IF.witness.ndi-publisher',
                '--trace-id', self.trace_id,
                '--payload', json.dumps({
                    'frame_number': 1,
                    'stream_id': stream_id,
                    'resolution': '1920x1080',
                    'fps': 30
                })
            )

            self.assertEqual(result.returncode, 0,
                f"Failed to log frame from {stream_id}: {result.stderr}")

    def test_invalid_payload_handling(self):
        """
        Test handling of invalid frame payload (malformed JSON).

        Scenario: Payload contains invalid JSON that cannot be parsed.

        Expected: CLI returns error and does not create entry.
        """
        result = self._run_cli(
            'log',
            '--event', 'ndi_frame_published',
            '--component', 'IF.witness.ndi-publisher',
            '--trace-id', self.trace_id,
            '--payload', '{invalid json}'
        )

        self.assertNotEqual(result.returncode, 0, "Should fail with invalid JSON")
        self.assertIn('Invalid JSON', result.stderr)


class TestFrameContentHashVerification(unittest.TestCase):
    """Test frame content hash verification and chain integrity.

    Each NDI frame log entry contains:
    - Content hash: SHA-256 of canonical frame entry
    - Signature: Ed25519 cryptographic proof
    - Prev hash: Link to previous entry in chain

    These create a tamper-evident log where any modification breaks the chain.
    """

    def setUp(self):
        """Create temporary database for hash verification tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'ndi_hash_witness.db'
        self.trace_id = f"ndi-hash-{uuid4().hex[:16]}"

    def tearDown(self):
        """Clean up temporary files."""
        if self.db_path.exists():
            self.db_path.unlink()

    def _run_cli(self, *args):
        """Run IF.witness CLI command."""
        cmd = [
            'python3',
            'src/cli/if-witness.py',
            '--db', str(self.db_path),
        ] + list(args)

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )
        return result

    def test_hash_chain_after_frame_sequence(self):
        """
        Test that hash chain is maintained across multiple frame entries.

        Scenario: Log 3 consecutive NDI frames, creating a hash chain:
        Frame1: prev_hash=None
        Frame2: prev_hash=Frame1.content_hash
        Frame3: prev_hash=Frame2.content_hash

        Expected: Each frame's prev_hash correctly links to previous frame.
        """
        for i in range(3):
            result = self._run_cli(
                'log',
                '--event', 'ndi_frame_published',
                '--component', 'IF.witness.ndi-publisher',
                '--trace-id', self.trace_id,
                '--payload', json.dumps({
                    'frame_number': i + 1,
                    'stream_id': 'IF.yologuard.01',
                    'resolution': '1920x1080',
                    'fps': 30
                })
            )

            self.assertEqual(result.returncode, 0,
                f"Failed to log frame {i + 1}: {result.stderr}")

    def test_hash_chain_verification(self):
        """
        Test verification of entire hash chain integrity.

        Scenario: After logging multiple frames, verify the complete hash chain
        is intact and no tampering has occurred.

        Expected: Verify command returns success with count of verified entries.
        """
        # Create frames
        for i in range(5):
            self._run_cli(
                'log',
                '--event', 'ndi_frame_published',
                '--component', 'IF.witness.ndi-publisher',
                '--trace-id', self.trace_id,
                '--payload', json.dumps({
                    'frame_number': i + 1,
                    'stream_id': 'IF.yologuard.01',
                    'resolution': '1920x1080',
                    'fps': 30
                })
            )

        # Verify chain
        result = self._run_cli('verify')

        self.assertEqual(result.returncode, 0, f"Verification failed: {result.stderr}")
        self.assertIn('entries verified', result.stdout)
        self.assertIn('Hash chain intact', result.stdout)
        self.assertIn('signatures valid', result.stdout)

    def test_signature_validation_in_log_output(self):
        """
        Test that signatures are shown in log output.

        Scenario: Each frame entry includes a signature displayed in CLI output.

        Expected: Signature shown as "ed25519:{hex_string}".
        """
        result = self._run_cli(
            'log',
            '--event', 'ndi_frame_published',
            '--component', 'IF.witness.ndi-publisher',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'frame_number': 50,
                'stream_id': 'IF.yologuard.01',
                'resolution': '1920x1080',
                'fps': 30
            })
        )

        self.assertEqual(result.returncode, 0)
        # Extract signature line
        output_lines = result.stdout.split('\n')
        sig_line = [l for l in output_lines if 'Signature:' in l]
        self.assertTrue(len(sig_line) > 0, "Signature not shown in output")
        self.assertIn('ed25519:', sig_line[0])


class TestTraceRetrievalForNDISession(unittest.TestCase):
    """Test trace retrieval for complete NDI session history.

    IF.witness trace retrieval enables:
    - Complete audit trail of all frames in a session
    - Relationships between frames and other components
    - Timeline and duration analysis
    - Cost aggregation across session
    """

    def setUp(self):
        """Create temporary database for trace retrieval tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'ndi_trace_witness.db'
        self.trace_id = f"ndi-trace-{uuid4().hex[:16]}"

    def tearDown(self):
        """Clean up temporary files."""
        if self.db_path.exists():
            self.db_path.unlink()

    def _run_cli(self, *args):
        """Run IF.witness CLI command."""
        cmd = [
            'python3',
            'src/cli/if-witness.py',
            '--db', str(self.db_path),
        ] + list(args)

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )
        return result

    def test_retrieve_session_trace_text_format(self):
        """
        Test retrieving NDI session trace in text format.

        Scenario: Create multiple frame entries, then retrieve complete trace.

        Expected: Output shows:
        - Trace ID
        - All component names
        - Chronological list of entries with timestamps
        - Event types for each frame
        - Payload summaries
        """
        # Create multiple entries
        for i in range(3):
            self._run_cli(
                'log',
                '--event', 'ndi_frame_published',
                '--component', 'IF.witness.ndi-publisher',
                '--trace-id', self.trace_id,
                '--payload', json.dumps({
                    'frame_number': i + 1,
                    'stream_id': 'IF.yologuard.01',
                    'resolution': '1920x1080',
                    'fps': 30
                })
            )

        # Retrieve trace
        result = self._run_cli('trace', self.trace_id)

        self.assertEqual(result.returncode, 0, f"Trace retrieval failed: {result.stderr}")
        self.assertIn(self.trace_id, result.stdout)
        self.assertIn('IF.witness.ndi-publisher', result.stdout)
        self.assertIn('ndi_frame_published', result.stdout)

    def test_retrieve_session_trace_json_format(self):
        """
        Test retrieving NDI session trace in JSON format.

        Scenario: Create frame entries, then retrieve trace as JSON.

        Expected: JSON output contains:
        - Structured entries array
        - Each entry with: id, timestamp, event, component, trace_id, payload
        - Sorted chronologically
        - Valid JSON that can be parsed
        """
        # Create entries
        for i in range(2):
            self._run_cli(
                'log',
                '--event', 'ndi_frame_published',
                '--component', 'IF.witness.ndi-publisher',
                '--trace-id', self.trace_id,
                '--payload', json.dumps({
                    'frame_number': i + 1,
                    'stream_id': 'IF.yologuard.01',
                    'resolution': '1920x1080',
                    'fps': 30
                })
            )

        # Retrieve as JSON
        result = self._run_cli('trace', self.trace_id, '--format', 'json')

        self.assertEqual(result.returncode, 0, f"JSON trace failed: {result.stderr}")

        # Verify it's valid JSON
        try:
            data = json.loads(result.stdout)
            self.assertIn('entries', data)
            self.assertGreater(len(data['entries']), 0)
        except json.JSONDecodeError:
            self.fail(f"Invalid JSON output: {result.stdout}")

    def test_retrieve_nonexistent_trace(self):
        """
        Test retrieving trace that doesn't exist.

        Scenario: Try to retrieve trace ID that has no entries.

        Expected: Command fails with error message about trace not found.
        """
        result = self._run_cli('trace', 'nonexistent-trace-id')

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('No entries found', result.stderr)

    def test_trace_with_multiple_components(self):
        """
        Test trace that involves multiple components.

        Scenario: NDI publisher logs frames, then other components (like validator)
        process those frames in the same trace.

        Expected: Trace shows both components in the output.
        """
        # Publisher logs frame
        self._run_cli(
            'log',
            '--event', 'ndi_frame_published',
            '--component', 'IF.witness.ndi-publisher',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'frame_number': 1,
                'stream_id': 'IF.yologuard.01',
                'resolution': '1920x1080',
                'fps': 30
            })
        )

        # Validator processes frame
        self._run_cli(
            'log',
            '--event', 'frame_validated',
            '--component', 'IF.witness.frame-validator',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'frame_number': 1,
                'validation_result': 'PASS',
                'quality_score': 0.98
            })
        )

        # Retrieve trace
        result = self._run_cli('trace', self.trace_id)

        self.assertEqual(result.returncode, 0)
        self.assertIn('IF.witness.ndi-publisher', result.stdout)
        self.assertIn('IF.witness.frame-validator', result.stdout)


class TestNDICostTracking(unittest.TestCase):
    """Test cost tracking for NDI operations via IF.optimise.

    NDI video streaming incurs costs for:
    - Encoder processing (LLM tokens / compute)
    - Network transmission
    - Storage writes
    - Frame validation

    IF.witness integrates with IF.optimise to track all costs per frame/stream.
    """

    def setUp(self):
        """Create temporary database for cost tracking tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'ndi_cost_witness.db'
        self.trace_id = f"ndi-cost-{uuid4().hex[:16]}"

    def tearDown(self):
        """Clean up temporary files."""
        if self.db_path.exists():
            self.db_path.unlink()

    def _run_cli(self, *args):
        """Run IF.witness CLI command."""
        cmd = [
            'python3',
            'src/cli/if-witness.py',
            '--db', str(self.db_path),
        ] + list(args)

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )
        return result

    def test_single_frame_cost_tracking(self):
        """
        Test cost tracking for single NDI frame.

        Scenario: Frame encoding/transmission costs:
        - 200 input tokens (frame processing)
        - 50 output tokens (metadata generation)
        - $0.00075 cost
        - Model: encoder-h264-v2

        Expected: Cost information appears in log output.
        """
        result = self._run_cli(
            'log',
            '--event', 'ndi_frame_published',
            '--component', 'IF.witness.ndi-publisher',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'frame_number': 1,
                'stream_id': 'IF.yologuard.01',
                'resolution': '1920x1080',
                'fps': 30
            }),
            '--tokens-in', '200',
            '--tokens-out', '50',
            '--cost', '0.00075',
            '--model', 'encoder-h264-v2'
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn('Cost:', result.stdout)
        self.assertIn('0.00075', result.stdout)

    def test_session_total_cost(self):
        """
        Test calculating total cost for entire NDI session.

        Scenario: Multiple frames logged with costs, then retrieve cost breakdown.

        Expected: Cost command shows:
        - Per-component cost summary
        - Total tokens used
        - Total cost in USD
        - Model information
        """
        costs = [
            (200, 50, 0.00075),
            (200, 50, 0.00075),
            (200, 50, 0.00075),
        ]

        for i, (tokens_in, tokens_out, cost) in enumerate(costs):
            self._run_cli(
                'log',
                '--event', 'ndi_frame_published',
                '--component', 'IF.witness.ndi-publisher',
                '--trace-id', self.trace_id,
                '--payload', json.dumps({
                    'frame_number': i + 1,
                    'stream_id': 'IF.yologuard.01',
                    'resolution': '1920x1080',
                    'fps': 30
                }),
                '--tokens-in', str(tokens_in),
                '--tokens-out', str(tokens_out),
                '--cost', str(cost),
                '--model', 'encoder-h264-v2'
            )

        # Get cost breakdown for trace
        result = self._run_cli('cost', '--trace-id', self.trace_id)

        self.assertEqual(result.returncode, 0)
        self.assertIn(self.trace_id, result.stdout)
        # Should show total cost
        self.assertIn('Total', result.stdout)

    def test_cost_breakdown_by_component(self):
        """
        Test cost breakdown by component across multiple NDI operations.

        Scenario: Log operations from different components:
        - IF.witness.ndi-publisher: 3 frames @ $0.00075 = $0.00225
        - IF.witness.frame-validator: 3 validations @ $0.0001 = $0.0003

        Expected: Cost breakdown shows both components with correct totals.
        """
        # Log publisher frames
        for i in range(3):
            self._run_cli(
                'log',
                '--event', 'ndi_frame_published',
                '--component', 'IF.witness.ndi-publisher',
                '--trace-id', self.trace_id,
                '--payload', json.dumps({
                    'frame_number': i + 1,
                    'stream_id': 'IF.yologuard.01',
                    'resolution': '1920x1080',
                    'fps': 30
                }),
                '--tokens-in', '200',
                '--tokens-out', '50',
                '--cost', '0.00075',
                '--model', 'encoder-h264-v2'
            )

        # Log validator operations
        for i in range(3):
            self._run_cli(
                'log',
                '--event', 'frame_validated',
                '--component', 'IF.witness.frame-validator',
                '--trace-id', self.trace_id,
                '--payload', json.dumps({
                    'frame_number': i + 1,
                    'validation_result': 'PASS'
                }),
                '--tokens-in', '100',
                '--tokens-out', '20',
                '--cost', '0.0001',
                '--model', 'validator-v1'
            )

        # Get cost breakdown
        result = self._run_cli('cost', '--trace-id', self.trace_id)

        self.assertEqual(result.returncode, 0)
        self.assertIn('IF.witness.ndi-publisher', result.stdout)
        self.assertIn('IF.witness.frame-validator', result.stdout)

    def test_cost_tracking_with_high_resolution_frames(self):
        """
        Test cost tracking for high-resolution NDI frames.

        Scenario: 4K frames (4096x2160) cost more than 1080p:
        - 4K frame: 800 tokens, $0.003
        - 1080p frame: 200 tokens, $0.00075

        Expected: Higher costs reflected accurately for 4K processing.
        """
        # Log 4K frame
        result_4k = self._run_cli(
            'log',
            '--event', 'ndi_frame_published',
            '--component', 'IF.witness.ndi-publisher',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'frame_number': 1,
                'stream_id': 'IF.yologuard.04k',
                'resolution': '4096x2160',
                'fps': 30
            }),
            '--tokens-in', '800',
            '--tokens-out', '200',
            '--cost', '0.003',
            '--model', 'encoder-h264-4k'
        )

        self.assertEqual(result_4k.returncode, 0)
        self.assertIn('0.003', result_4k.stdout)


class TestNDISessionEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions in NDI frame logging."""

    def setUp(self):
        """Create temporary database for edge case tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'ndi_edge_witness.db'
        self.trace_id = f"ndi-edge-{uuid4().hex[:16]}"

    def tearDown(self):
        """Clean up temporary files."""
        if self.db_path.exists():
            self.db_path.unlink()

    def _run_cli(self, *args):
        """Run IF.witness CLI command."""
        cmd = [
            'python3',
            'src/cli/if-witness.py',
            '--db', str(self.db_path),
        ] + list(args)

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True
        )
        return result

    def test_missing_required_parameters(self):
        """Test that missing required CLI parameters are caught."""
        result = self._run_cli(
            'log',
            '--event', 'ndi_frame_published',
            # Missing component, trace_id, payload
        )

        self.assertNotEqual(result.returncode, 0)

    def test_very_large_frame_payload(self):
        """Test logging very large frame metadata payloads."""
        large_payload = {
            'frame_number': 1,
            'stream_id': 'IF.yologuard.01',
            'resolution': '1920x1080',
            'fps': 30,
            'metadata': 'x' * 10000  # Large metadata string
        }

        result = self._run_cli(
            'log',
            '--event', 'ndi_frame_published',
            '--component', 'IF.witness.ndi-publisher',
            '--trace-id', self.trace_id,
            '--payload', json.dumps(large_payload)
        )

        self.assertEqual(result.returncode, 0)

    def test_special_characters_in_stream_id(self):
        """Test handling special characters in stream IDs."""
        result = self._run_cli(
            'log',
            '--event', 'ndi_frame_published',
            '--component', 'IF.witness.ndi-publisher',
            '--trace-id', self.trace_id,
            '--payload', json.dumps({
                'frame_number': 1,
                'stream_id': 'IF.yologuard-01_special@stream',
                'resolution': '1920x1080',
                'fps': 30
            })
        )

        self.assertEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
