"""
Integration tests for IF.witness CLI - Live Session Testing

This test suite validates the CLI works correctly with all 4 sessions:
- Session 1 (NDI): Network Device Interface video frame publishing
- Session 2 (WebRTC): Peer-to-peer real-time communication
- Session 3 (H.323): Legacy video conferencing protocol
- Session 4 (SIP): Session Initiation Protocol with ESCALATE extension

Tests cover:
1. End-to-end flow for each session with witness logging
2. Cross-session trace propagation (single trace_id across all sessions)
3. Cost tracking and aggregation across sessions
4. Hash chain integrity verification
5. Export functionality (JSON, CSV, PDF)
6. Budget alert integration

Philosophy: IF.ground Principle 8 - Observability without fragility
Every operation across all sessions is logged with cryptographic proof.
"""

import sys
import json
import tempfile
import subprocess
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta

import pytest


class TestLiveSessionIntegration:
    """Live integration tests with all 4 sessions"""

    @pytest.fixture(scope="class")
    def test_db(self, tmp_path_factory):
        """Create temporary test database for all tests"""
        db_path = tmp_path_factory.mktemp("witness") / "test_live.db"
        yield db_path
        # Cleanup handled by tmp_path_factory

    @pytest.fixture(scope="class")
    def cross_session_trace_id(self):
        """Single trace ID for cross-session testing"""
        return f"cross-session-{uuid4().hex[:16]}"

    def _run_witness_cli(self, *args, db_path=None):
        """
        Run IF.witness CLI command.

        Args:
            *args: Command arguments
            db_path: Path to database (required)

        Returns:
            subprocess.CompletedProcess result
        """
        cmd = [
            'python3',
            'src/cli/if_witness.py',
            '--db', str(db_path),
        ] + list(args)

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True,
            timeout=10
        )
        return result

    def _run_optimise_cli(self, *args, db_path=None):
        """
        Run IF.optimise CLI command.

        Args:
            *args: Command arguments
            db_path: Path to database (required)

        Returns:
            subprocess.CompletedProcess result
        """
        cmd = [
            'python3',
            'src/cli/if_optimise.py',
            '--db', str(db_path),
        ] + list(args)

        result = subprocess.run(
            cmd,
            cwd='/home/user/infrafabric',
            capture_output=True,
            text=True,
            timeout=10
        )
        return result

    # ===========================
    # Session 1: NDI Frame Publishing
    # ===========================

    def test_session1_ndi_flow(self, test_db):
        """
        Test NDI frame publishing flow with witness logging.

        Flow:
        1. ndi_source_registered - NDI source comes online
        2. ndi_frame_captured - Frame captured from source
        3. ndi_frame_published - Frame published to network

        Verification:
        - All 3 events logged successfully
        - Hash chain intact
        - All events retrievable
        """
        trace_id = f"ndi-flow-{uuid4().hex[:16]}"

        # Step 1: Register NDI source
        result = self._run_witness_cli(
            'log',
            '--event', 'ndi_source_registered',
            '--component', 'IF.witness.ndi-publisher',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'source_name': 'IF.yologuard.cam01',
                'resolution': '1920x1080',
                'fps': 30,
                'format': 'UYVY'
            }),
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to register NDI source: {result.stderr}"
        assert 'Witness entry created' in result.stdout
        assert 'Hash chain verified' in result.stdout

        # Step 2: Capture frame
        result = self._run_witness_cli(
            'log',
            '--event', 'ndi_frame_captured',
            '--component', 'IF.witness.ndi-publisher',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'source_name': 'IF.yologuard.cam01',
                'frame_number': 42,
                'timestamp_ns': 1699738800000000000,
                'size_bytes': 8294400
            }),
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to capture frame: {result.stderr}"
        assert 'Witness entry created' in result.stdout

        # Step 3: Publish frame
        result = self._run_witness_cli(
            'log',
            '--event', 'ndi_frame_published',
            '--component', 'IF.witness.ndi-publisher',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'source_name': 'IF.yologuard.cam01',
                'frame_number': 42,
                'destination': 'multicast://239.255.0.1:5960',
                'latency_ms': 2.3
            }),
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to publish frame: {result.stderr}"
        assert 'Witness entry created' in result.stdout

        # Verify: Retrieve full trace
        result = self._run_witness_cli(
            'trace', trace_id,
            '--format', 'json',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to retrieve trace: {result.stderr}"

        trace_data = json.loads(result.stdout)
        assert len(trace_data['entries']) == 3
        assert trace_data['trace_id'] == trace_id
        assert 'IF.witness.ndi-publisher' in trace_data['components']

        # Verify event sequence
        events = [e['event'] for e in trace_data['entries']]
        assert events == ['ndi_source_registered', 'ndi_frame_captured', 'ndi_frame_published']

    # ===========================
    # Session 2: WebRTC Signaling
    # ===========================

    def test_session2_webrtc_flow(self, test_db):
        """
        Test WebRTC signaling flow with witness logging.

        Flow:
        1. peer_connection_created - Create peer connection
        2. offer_created - Generate SDP offer
        3. answer_received - Receive SDP answer
        4. ice_candidate_gathered (x3) - Gather ICE candidates
        5. connection_established - Connection successful

        Verification:
        - All signaling events logged
        - Hash chain intact
        - Connection timeline correct
        """
        trace_id = f"webrtc-flow-{uuid4().hex[:16]}"

        # Step 1: Create peer connection
        result = self._run_witness_cli(
            'log',
            '--event', 'peer_connection_created',
            '--component', 'IF.witness.webrtc-client',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'peer_id': 'peer-alice-001',
                'config': {
                    'iceServers': ['stun:stun.l.google.com:19302'],
                    'iceTransportPolicy': 'all'
                }
            }),
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to create peer connection: {result.stderr}"

        # Step 2: Create offer
        result = self._run_witness_cli(
            'log',
            '--event', 'offer_created',
            '--component', 'IF.witness.webrtc-client',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'peer_id': 'peer-alice-001',
                'sdp_type': 'offer',
                'has_audio': True,
                'has_video': True,
                'has_data': False
            }),
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to create offer: {result.stderr}"

        # Step 3: Receive answer
        result = self._run_witness_cli(
            'log',
            '--event', 'answer_received',
            '--component', 'IF.witness.webrtc-client',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'peer_id': 'peer-bob-002',
                'sdp_type': 'answer',
                'accepted_codecs': ['VP8', 'opus']
            }),
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to receive answer: {result.stderr}"

        # Step 4: Gather ICE candidates (3 candidates)
        for i in range(3):
            result = self._run_witness_cli(
                'log',
                '--event', 'ice_candidate_gathered',
                '--component', 'IF.witness.webrtc-client',
                '--trace-id', trace_id,
                '--payload', json.dumps({
                    'peer_id': 'peer-alice-001',
                    'candidate_type': ['host', 'srflx', 'relay'][i],
                    'protocol': 'udp',
                    'priority': 2130706431 - (i * 1000)
                }),
                db_path=test_db
            )
            assert result.returncode == 0, f"Failed to gather ICE candidate {i}: {result.stderr}"

        # Step 5: Connection established
        result = self._run_witness_cli(
            'log',
            '--event', 'connection_established',
            '--component', 'IF.witness.webrtc-client',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'peer_id': 'peer-alice-001',
                'selected_candidate_pair': 'host-host',
                'rtt_ms': 15.2,
                'connection_state': 'connected'
            }),
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to establish connection: {result.stderr}"

        # Verify: Retrieve trace
        result = self._run_witness_cli(
            'trace', trace_id,
            '--format', 'json',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to retrieve trace: {result.stderr}"

        trace_data = json.loads(result.stdout)
        # Verify all WebRTC events present (at least 6 for this trace)
        webrtc_entries = [e for e in trace_data['entries'] if e['trace_id'] == trace_id]
        assert len(webrtc_entries) >= 6  # At least: 1 + 1 + 1 + 3 ICE + 1
        assert 'IF.witness.webrtc-client' in trace_data['components']

    # ===========================
    # Session 3: H.323 with Cost Tracking
    # ===========================

    def test_session3_h323_flow_with_costs(self, test_db):
        """
        Test H.323 admission control with cost tracking.

        Flow:
        1. arq_request - Admission Request (with cost)
        2. acf_response - Admission Confirm (with cost)
        3. call_setup - Call Setup Complete (with cost)

        Verification:
        - All events logged with costs
        - Cost tracking works correctly
        - Report shows correct totals
        """
        trace_id = f"h323-flow-{uuid4().hex[:16]}"

        # Step 1: ARQ Request
        result = self._run_witness_cli(
            'log',
            '--event', 'arq_request',
            '--component', 'IF.witness.h323-endpoint',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'call_id': 'h323-call-001',
                'endpoint_id': 'ep-001',
                'bandwidth_requested': 384,  # kbps
                'call_type': 'video'
            }),
            '--tokens-in', '150',
            '--tokens-out', '75',
            '--cost', '0.00025',
            '--model', 'h323-processor-v2',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed ARQ request: {result.stderr}"
        assert 'Cost:' in result.stdout

        # Step 2: ACF Response
        result = self._run_witness_cli(
            'log',
            '--event', 'acf_response',
            '--component', 'IF.witness.h323-gatekeeper',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'call_id': 'h323-call-001',
                'admission_granted': True,
                'bandwidth_allocated': 384,
                'time_limit_seconds': 3600
            }),
            '--tokens-in', '100',
            '--tokens-out', '50',
            '--cost', '0.00015',
            '--model', 'h323-processor-v2',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed ACF response: {result.stderr}"

        # Step 3: Call Setup
        result = self._run_witness_cli(
            'log',
            '--event', 'call_setup_complete',
            '--component', 'IF.witness.h323-endpoint',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'call_id': 'h323-call-001',
                'remote_endpoint': 'ep-002',
                'codecs': ['H.264', 'G.711'],
                'setup_time_ms': 523
            }),
            '--tokens-in', '200',
            '--tokens-out', '100',
            '--cost', '0.00035',
            '--model', 'h323-processor-v2',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed call setup: {result.stderr}"

        # Verify: Check costs via trace
        result = self._run_witness_cli(
            'trace', trace_id,
            '--format', 'json',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to retrieve trace: {result.stderr}"

        trace_data = json.loads(result.stdout)
        assert len(trace_data['entries']) == 3

        # Verify total cost
        total_cost = trace_data['total_cost_usd']
        expected_cost = 0.00025 + 0.00015 + 0.00035  # 0.00075
        assert abs(total_cost - expected_cost) < 0.000001

        # Verify total tokens
        total_tokens = trace_data['total_tokens']
        expected_tokens = (150 + 75) + (100 + 50) + (200 + 100)  # 675
        assert total_tokens == expected_tokens

        # Verify: Check cost report
        result = self._run_optimise_cli(
            'report',
            '--format', 'json',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to get cost report: {result.stderr}"

        report_data = json.loads(result.stdout)
        assert len(report_data) > 0

        # Find H.323 components in report
        h323_components = [r for r in report_data if 'h323' in r['component'].lower()]
        assert len(h323_components) >= 2  # endpoint and gatekeeper

    # ===========================
    # Session 4: SIP ESCALATE Pattern
    # ===========================

    def test_session4_sip_escalate_flow(self, test_db):
        """
        Test SIP ESCALATE pattern with witness logging.

        Flow:
        1. INVITE - Initial call invitation
        2. 100 Trying - Provisional response
        3. ESCALATE - Custom SIP method for security escalation
        4. 200 OK - Final success response
        5. ACK - Acknowledgment

        Verification:
        - Full call flow logged
        - Custom ESCALATE method captured
        - All SIP responses tracked
        """
        trace_id = f"sip-escalate-{uuid4().hex[:16]}"

        # Step 1: INVITE
        result = self._run_witness_cli(
            'log',
            '--event', 'sip_invite_sent',
            '--component', 'IF.witness.sip-ua',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'call_id': 'sip-call-001@infrafabric',
                'from_uri': 'sip:alice@infrafabric.com',
                'to_uri': 'sip:bob@infrafabric.com',
                'method': 'INVITE',
                'has_sdp': True
            }),
            '--tokens-in', '100',
            '--tokens-out', '50',
            '--cost', '0.0001',
            '--model', 'sip-processor-v1',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed INVITE: {result.stderr}"

        # Step 2: 100 Trying
        result = self._run_witness_cli(
            'log',
            '--event', 'sip_response_received',
            '--component', 'IF.witness.sip-ua',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'call_id': 'sip-call-001@infrafabric',
                'status_code': 100,
                'reason_phrase': 'Trying',
                'response_time_ms': 12
            }),
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed 100 Trying: {result.stderr}"

        # Step 3: ESCALATE (custom SIP method)
        result = self._run_witness_cli(
            'log',
            '--event', 'sip_escalate_sent',
            '--component', 'IF.witness.sip-ua',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'call_id': 'sip-call-001@infrafabric',
                'method': 'ESCALATE',
                'escalation_reason': 'security_verification',
                'requires_auth': True,
                'challenge_type': 'digest'
            }),
            '--tokens-in', '200',
            '--tokens-out', '150',
            '--cost', '0.0003',
            '--model', 'sip-processor-v1',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed ESCALATE: {result.stderr}"

        # Step 4: 200 OK
        result = self._run_witness_cli(
            'log',
            '--event', 'sip_response_received',
            '--component', 'IF.witness.sip-ua',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'call_id': 'sip-call-001@infrafabric',
                'status_code': 200,
                'reason_phrase': 'OK',
                'has_sdp': True,
                'response_time_ms': 456
            }),
            '--tokens-in', '75',
            '--tokens-out', '25',
            '--cost', '0.00008',
            '--model', 'sip-processor-v1',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed 200 OK: {result.stderr}"

        # Step 5: ACK
        result = self._run_witness_cli(
            'log',
            '--event', 'sip_ack_sent',
            '--component', 'IF.witness.sip-ua',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'call_id': 'sip-call-001@infrafabric',
                'method': 'ACK',
                'final_state': 'established'
            }),
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed ACK: {result.stderr}"

        # Verify: Full call flow
        result = self._run_witness_cli(
            'trace', trace_id,
            '--format', 'json',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to retrieve trace: {result.stderr}"

        trace_data = json.loads(result.stdout)
        assert len(trace_data['entries']) == 5

        # Verify ESCALATE method captured
        escalate_entry = [e for e in trace_data['entries'] if e['event'] == 'sip_escalate_sent']
        assert len(escalate_entry) == 1
        escalate_payload = json.loads(escalate_entry[0]['payload'])
        assert escalate_payload['method'] == 'ESCALATE'
        assert escalate_payload['escalation_reason'] == 'security_verification'

    # ===========================
    # Cross-Session Testing
    # ===========================

    def test_cross_session_trace(self, test_db, cross_session_trace_id):
        """
        Test trace_id propagation across all 4 sessions.

        Scenario:
        A single operation involves all 4 protocols in sequence:
        1. NDI frame captured
        2. WebRTC peer connection for distribution
        3. H.323 bridge for legacy endpoint
        4. SIP gateway for final delivery

        Verification:
        - All 4 sessions share same trace_id
        - Events from all sessions retrievable
        - Chronological ordering maintained
        - Cost aggregation across all sessions
        """
        trace_id = cross_session_trace_id

        # Session 1: NDI
        result = self._run_witness_cli(
            'log',
            '--event', 'ndi_frame_captured',
            '--component', 'IF.witness.ndi-publisher',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'frame_number': 1001,
                'source': 'cam01',
                'cross_session': True
            }),
            db_path=test_db
        )
        assert result.returncode == 0

        # Session 2: WebRTC
        result = self._run_witness_cli(
            'log',
            '--event', 'peer_connection_created',
            '--component', 'IF.witness.webrtc-client',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'peer_id': 'cross-session-peer',
                'source_protocol': 'ndi'
            }),
            '--tokens-in', '100',
            '--tokens-out', '50',
            '--cost', '0.0001',
            '--model', 'webrtc-processor',
            db_path=test_db
        )
        assert result.returncode == 0

        # Session 3: H.323
        result = self._run_witness_cli(
            'log',
            '--event', 'arq_request',
            '--component', 'IF.witness.h323-endpoint',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'call_id': 'cross-session-h323',
                'bridge_from': 'webrtc'
            }),
            '--tokens-in', '150',
            '--tokens-out', '75',
            '--cost', '0.00025',
            '--model', 'h323-processor-v2',
            db_path=test_db
        )
        assert result.returncode == 0

        # Session 4: SIP
        result = self._run_witness_cli(
            'log',
            '--event', 'sip_invite_sent',
            '--component', 'IF.witness.sip-ua',
            '--trace-id', trace_id,
            '--payload', json.dumps({
                'call_id': 'cross-session-sip',
                'gateway_from': 'h323'
            }),
            '--tokens-in', '120',
            '--tokens-out', '60',
            '--cost', '0.00015',
            '--model', 'sip-processor-v1',
            db_path=test_db
        )
        assert result.returncode == 0

        # Verify: Single trace contains all 4 sessions
        result = self._run_witness_cli(
            'trace', trace_id,
            '--format', 'json',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to retrieve cross-session trace: {result.stderr}"

        trace_data = json.loads(result.stdout)

        # Verify all 4 sessions present
        assert len(trace_data['entries']) == 4

        # Verify all 4 components present
        components = trace_data['components']
        assert 'IF.witness.ndi-publisher' in components
        assert 'IF.witness.webrtc-client' in components
        assert 'IF.witness.h323-endpoint' in components
        assert 'IF.witness.sip-ua' in components

        # Verify chronological ordering (timestamps should be ascending)
        timestamps = [e['timestamp'] for e in trace_data['entries']]
        assert timestamps == sorted(timestamps), "Events not in chronological order"

        # Verify cost aggregation
        total_cost = trace_data['total_cost_usd']
        expected_cost = 0.0001 + 0.00025 + 0.00015  # 0.0005
        assert abs(total_cost - expected_cost) < 0.000001

        # Verify total tokens
        total_tokens = trace_data['total_tokens']
        expected_tokens = (100 + 50) + (150 + 75) + (120 + 60)  # 555
        assert total_tokens == expected_tokens

    def test_cost_aggregation_all_sessions(self, test_db):
        """
        Test cost tracking across all sessions.

        Verification:
        - Cost report includes all sessions
        - Per-component breakdown correct
        - Total costs match individual session costs
        """
        trace_id = f"cost-agg-{uuid4().hex[:16]}"

        # Log events with costs from each session
        sessions = [
            ('ndi_frame_published', 'IF.witness.ndi-publisher', 100, 50, 0.0001, 'ndi-encoder'),
            ('connection_established', 'IF.witness.webrtc-client', 200, 100, 0.0002, 'webrtc-processor'),
            ('call_setup_complete', 'IF.witness.h323-endpoint', 150, 75, 0.00025, 'h323-processor-v2'),
            ('sip_ack_sent', 'IF.witness.sip-ua', 120, 60, 0.00015, 'sip-processor-v1'),
        ]

        for event, component, tokens_in, tokens_out, cost, model in sessions:
            result = self._run_witness_cli(
                'log',
                '--event', event,
                '--component', component,
                '--trace-id', trace_id,
                '--payload', json.dumps({'test': 'cost_aggregation'}),
                '--tokens-in', str(tokens_in),
                '--tokens-out', str(tokens_out),
                '--cost', str(cost),
                '--model', model,
                db_path=test_db
            )
            assert result.returncode == 0

        # Verify: Cost report
        result = self._run_optimise_cli(
            'report',
            '--format', 'json',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to get cost report: {result.stderr}"

        report_data = json.loads(result.stdout)
        assert len(report_data) > 0

        # Verify each session component appears in report
        component_names = [r['component'] for r in report_data]
        assert 'IF.witness.ndi-publisher' in component_names
        assert 'IF.witness.webrtc-client' in component_names
        assert 'IF.witness.h323-endpoint' in component_names
        assert 'IF.witness.sip-ua' in component_names

    def test_budget_alerts_integration(self, test_db):
        """
        Test budget alerts trigger correctly.

        Scenario:
        - Set budget: $0.01 daily (10 cents to avoid float issues, but we'll use $0.01)
        - Log costs exceeding 90% threshold
        - Verify alert triggered
        """
        trace_id = f"budget-alert-{uuid4().hex[:16]}"

        # Set budget: $0.01 daily
        result = self._run_optimise_cli(
            'budget',
            '--set', '0.01',
            '--period', 'day',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to set budget: {result.stderr}"
        assert 'Budget set: $0.01 per day' in result.stdout

        # Log events with costs totaling > 90% of budget (> $0.009)
        # We'll log 3 events at $0.004 each = $0.012 total (120% of budget)
        for i in range(3):
            result = self._run_witness_cli(
                'log',
                '--event', f'test_budget_event_{i}',
                '--component', 'IF.witness.budget-test',
                '--trace-id', trace_id,
                '--payload', json.dumps({'iteration': i}),
                '--tokens-in', '1000',
                '--tokens-out', '500',
                '--cost', '0.004',
                '--model', 'test-model',
                db_path=test_db
            )
            assert result.returncode == 0

        # Check budget status - should show alert
        result = self._run_optimise_cli(
            'budget',
            '--period', 'day',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to check budget: {result.stderr}"

        # Verify alert message present (>100% used) - check both stdout and stderr
        output = result.stdout + result.stderr
        assert 'ALERT' in output or 'WARNING' in output
        assert 'Budget' in output

    # ===========================
    # Hash Chain Integrity
    # ===========================

    def test_hash_chain_verification(self, test_db):
        """
        Test hash chain integrity verification.

        Steps:
        1. Log 10 events in sequence
        2. Verify hash chain passes
        3. Manually corrupt one entry (if possible via DB)
        4. Verify corruption detected

        Note: Step 3-4 require direct DB access, which is complex.
        For now, we verify the positive case.
        """
        trace_id = f"hash-chain-{uuid4().hex[:16]}"

        # Log 10 events
        for i in range(10):
            result = self._run_witness_cli(
                'log',
                '--event', f'event_{i}',
                '--component', 'IF.witness.hash-test',
                '--trace-id', trace_id,
                '--payload', json.dumps({'sequence': i}),
                db_path=test_db
            )
            assert result.returncode == 0
            # Each log operation already verifies the chain
            assert 'Hash chain verified' in result.stdout

        # Verify entire chain
        result = self._run_witness_cli(
            'verify',
            db_path=test_db
        )
        assert result.returncode == 0, f"Hash chain verification failed: {result.stderr}"
        assert 'entries verified' in result.stdout
        assert 'Hash chain intact' in result.stdout
        assert 'All signatures valid' in result.stdout

    # ===========================
    # Export Functionality
    # ===========================

    def test_export_json_all_sessions(self, test_db, tmp_path):
        """
        Test JSON export for all sessions.

        Steps:
        1. Log events from all 4 sessions
        2. Export to JSON file
        3. Verify JSON is valid and complete
        """
        trace_id = f"export-json-{uuid4().hex[:16]}"

        # Log one event from each session
        events = [
            ('ndi_frame_published', 'IF.witness.ndi-publisher'),
            ('connection_established', 'IF.witness.webrtc-client'),
            ('call_setup_complete', 'IF.witness.h323-endpoint'),
            ('sip_ack_sent', 'IF.witness.sip-ua'),
        ]

        for event, component in events:
            result = self._run_witness_cli(
                'log',
                '--event', event,
                '--component', component,
                '--trace-id', trace_id,
                '--payload', json.dumps({'export_test': True}),
                db_path=test_db
            )
            assert result.returncode == 0

        # Export to JSON
        output_file = tmp_path / 'export_test.json'
        result = self._run_witness_cli(
            'export',
            '--format', 'json',
            '--output', str(output_file),
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to export JSON: {result.stderr}"
        assert output_file.exists()

        # Verify JSON content
        with open(output_file, 'r') as f:
            export_data = json.load(f)

        assert isinstance(export_data, list)
        assert len(export_data) >= 4  # At least our 4 events

        # Verify all required fields present
        for entry in export_data[:4]:
            assert 'id' in entry
            assert 'event' in entry
            assert 'component' in entry
            assert 'signature' in entry
            assert 'content_hash' in entry
            assert 'timestamp' in entry

    def test_export_csv_with_date_range(self, test_db, tmp_path):
        """
        Test CSV export with date filtering.

        Steps:
        1. Log events (we'll use today's date)
        2. Export with date range
        3. Verify CSV format and content
        """
        trace_id = f"export-csv-{uuid4().hex[:16]}"
        today = datetime.utcnow().date()

        # Log several events
        for i in range(5):
            result = self._run_witness_cli(
                'log',
                '--event', f'csv_test_event_{i}',
                '--component', 'IF.witness.csv-test',
                '--trace-id', trace_id,
                '--payload', json.dumps({'index': i}),
                '--tokens-in', '100',
                '--tokens-out', '50',
                '--cost', '0.0001',
                '--model', 'test-model',
                db_path=test_db
            )
            assert result.returncode == 0

        # Export to CSV with date range (today only)
        output_file = tmp_path / 'export_test.csv'
        result = self._run_witness_cli(
            'export',
            '--format', 'csv',
            '--output', str(output_file),
            '--date-range', f'{today}',
            db_path=test_db
        )
        assert result.returncode == 0, f"Failed to export CSV: {result.stderr}"
        assert output_file.exists()

        # Verify CSV content
        import csv
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) >= 5  # At least our 5 events

        # Verify columns present
        assert 'id' in rows[0]
        assert 'event' in rows[0]
        assert 'component' in rows[0]
        assert 'cost_usd' in rows[0]

    def test_export_pdf_compliance_report(self, test_db, tmp_path):
        """
        Test PDF compliance report generation.

        Steps:
        1. Log events from all sessions
        2. Export to PDF
        3. Verify PDF file created

        Note: Full PDF content verification requires PDF parsing library.
        We verify file existence and basic generation success.
        """
        trace_id = f"export-pdf-{uuid4().hex[:16]}"

        # Log events from all 4 sessions with costs
        sessions = [
            ('ndi_frame_published', 'IF.witness.ndi-publisher', 100, 50, 0.0001),
            ('connection_established', 'IF.witness.webrtc-client', 200, 100, 0.0002),
            ('call_setup_complete', 'IF.witness.h323-endpoint', 150, 75, 0.00025),
            ('sip_ack_sent', 'IF.witness.sip-ua', 120, 60, 0.00015),
        ]

        for event, component, tokens_in, tokens_out, cost in sessions:
            result = self._run_witness_cli(
                'log',
                '--event', event,
                '--component', component,
                '--trace-id', trace_id,
                '--payload', json.dumps({'pdf_test': True}),
                '--tokens-in', str(tokens_in),
                '--tokens-out', str(tokens_out),
                '--cost', str(cost),
                '--model', 'test-model',
                db_path=test_db
            )
            assert result.returncode == 0

        # Export to PDF
        output_file = tmp_path / 'compliance_report.pdf'
        result = self._run_witness_cli(
            'export',
            '--format', 'pdf',
            '--output', str(output_file),
            db_path=test_db
        )

        # PDF export requires reportlab - may not be installed in test environment
        if 'reportlab' in result.stderr:
            pytest.skip("reportlab not installed - skipping PDF export test")

        assert result.returncode == 0, f"Failed to export PDF: {result.stderr}"
        assert output_file.exists()
        assert output_file.stat().st_size > 0  # PDF has content

    # ===========================
    # Performance Verification
    # ===========================

    def test_log_operation_performance(self, test_db):
        """
        Test log operation performance meets requirements.

        Requirement: <50ms (we achieved 0.25ms in Phase 2)

        This test verifies operations complete quickly.
        """
        import time

        trace_id = f"perf-test-{uuid4().hex[:16]}"

        start_time = time.time()
        result = self._run_witness_cli(
            'log',
            '--event', 'performance_test',
            '--component', 'IF.witness.perf-test',
            '--trace-id', trace_id,
            '--payload', json.dumps({'test': 'performance'}),
            db_path=test_db
        )
        duration_ms = (time.time() - start_time) * 1000

        assert result.returncode == 0
        # Allow generous margin for subprocess overhead
        # The actual operation is 0.25ms, but subprocess adds ~10-30ms
        assert duration_ms < 500, f"Log operation took {duration_ms:.2f}ms (expected <50ms + subprocess overhead)"

    def test_verify_operation_performance(self, test_db):
        """
        Test verify operation performance.

        Requirement: <500ms for 100 entries
        """
        import time

        # We should have many entries from previous tests (probably >100)
        start_time = time.time()
        result = self._run_witness_cli(
            'verify',
            db_path=test_db
        )
        duration_ms = (time.time() - start_time) * 1000

        assert result.returncode == 0
        # Extract entry count from output
        # Output format: "✓ N entries verified"
        import re
        match = re.search(r'(\d+) entries verified', result.stdout)
        if match:
            entry_count = int(match.group(1))
            # Allow 5ms per entry + subprocess overhead
            max_duration = max(500, entry_count * 5 + 100)
            assert duration_ms < max_duration, f"Verify took {duration_ms:.2f}ms for {entry_count} entries"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
