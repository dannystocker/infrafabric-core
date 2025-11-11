"""
IF.witness Test Fixtures

Provides sample data for integration testing across Sessions 1-4:
- NDI (Network Device Interface) events
- WebRTC (Real-Time Communication) events
- H.323 (VoIP) events
- SIP (Session Initiation Protocol) events
- Cost tracking data
- Pre-populated test databases

Each fixture returns realistic event sequences matching actual protocol behavior.
"""

import json
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from src.witness.models import WitnessEntry, Cost
from src.witness.database import WitnessDatabase
from src.witness.crypto import WitnessCrypto


def get_ndi_events() -> List[Dict[str, Any]]:
    """
    Sample NDI (Network Device Interface) frame publishing events.

    NDI is a protocol for real-time video/audio transmission over IP networks.
    Simulates a video frame capture and publishing workflow.

    Returns:
        List of NDI event dictionaries with realistic payload data
    """
    base_time = datetime.utcnow()

    return [
        {
            'event': 'ndi_source_registered',
            'component': 'IF.ndi',
            'trace_id': 'ndi-trace-001',
            'timestamp': base_time,
            'payload': {
                'source_name': 'Studio A Camera',
                'source_id': 'ndi-source-camera-1',
                'ip_address': '192.168.1.100',
                'port': 5961,
                'metadata': {'resolution': '1920x1080', 'fps': 60}
            },
            'cost': Cost(tokens_in=10, tokens_out=5, cost_usd=0.00005, model='claude-haiku-4.5')
        },
        {
            'event': 'ndi_frame_captured',
            'component': 'IF.ndi',
            'trace_id': 'ndi-trace-001',
            'timestamp': base_time + timedelta(milliseconds=16),
            'payload': {
                'frame_id': 1,
                'resolution': '1920x1080',
                'color_format': 'RGBA',
                'frame_size_bytes': 8294400,
                'timestamp_ns': 1234567890000
            },
            'cost': Cost(tokens_in=50, tokens_out=25, cost_usd=0.0001, model='claude-haiku-4.5')
        },
        {
            'event': 'ndi_frame_published',
            'component': 'IF.ndi',
            'trace_id': 'ndi-trace-001',
            'timestamp': base_time + timedelta(milliseconds=32),
            'payload': {
                'frame_id': 1,
                'sender_id': 'ndi-source-camera-1',
                'receivers': ['viewer-1', 'viewer-2'],
                'network_latency_ms': 2.5,
                'bandwidth_mbps': 850
            },
            'cost': Cost(tokens_in=75, tokens_out=40, cost_usd=0.00015, model='claude-haiku-4.5')
        },
        {
            'event': 'ndi_frame_delivered',
            'component': 'IF.ndi',
            'trace_id': 'ndi-trace-001',
            'timestamp': base_time + timedelta(milliseconds=48),
            'payload': {
                'frame_id': 1,
                'receiver_id': 'viewer-1',
                'delivery_time_ms': 2.5,
                'packet_loss_percent': 0.0
            },
            'cost': Cost(tokens_in=30, tokens_out=20, cost_usd=0.00008, model='claude-haiku-4.5')
        },
        {
            'event': 'ndi_source_unregistered',
            'component': 'IF.ndi',
            'trace_id': 'ndi-trace-001',
            'timestamp': base_time + timedelta(seconds=5),
            'payload': {
                'source_id': 'ndi-source-camera-1',
                'reason': 'normal_shutdown',
                'total_frames_sent': 300
            },
            'cost': Cost(tokens_in=15, tokens_out=10, cost_usd=0.00005, model='claude-haiku-4.5')
        }
    ]


def get_webrtc_events() -> List[Dict[str, Any]]:
    """
    Sample WebRTC (Web Real-Time Communication) events.

    WebRTC enables real-time peer-to-peer communication for video/audio.
    Simulates connection establishment and media flow.

    Returns:
        List of WebRTC event dictionaries with realistic payload data
    """
    base_time = datetime.utcnow()

    return [
        {
            'event': 'webrtc_peer_connection_created',
            'component': 'IF.webrtc',
            'trace_id': 'webrtc-trace-001',
            'timestamp': base_time,
            'payload': {
                'peer_id': 'peer-alice-001',
                'connection_id': 'webrtc-conn-001',
                'ice_servers': ['stun:stun.l.google.com:19302'],
                'rtc_configuration': {
                    'bundlePolicy': 'max-bundle',
                    'rtcpMuxPolicy': 'require'
                }
            },
            'cost': Cost(tokens_in=40, tokens_out=20, cost_usd=0.0001, model='claude-haiku-4.5')
        },
        {
            'event': 'webrtc_ice_candidate_gathered',
            'component': 'IF.webrtc',
            'trace_id': 'webrtc-trace-001',
            'timestamp': base_time + timedelta(milliseconds=50),
            'payload': {
                'connection_id': 'webrtc-conn-001',
                'candidate_type': 'host',
                'protocol': 'udp',
                'address': '192.168.1.50',
                'port': 54321,
                'priority': 2130706431
            },
            'cost': Cost(tokens_in=25, tokens_out=15, cost_usd=0.00008, model='claude-haiku-4.5')
        },
        {
            'event': 'webrtc_ice_candidate_gathered',
            'component': 'IF.webrtc',
            'trace_id': 'webrtc-trace-001',
            'timestamp': base_time + timedelta(milliseconds=60),
            'payload': {
                'connection_id': 'webrtc-conn-001',
                'candidate_type': 'srflx',
                'protocol': 'udp',
                'address': '203.0.113.45',
                'port': 54322,
                'priority': 1694498815
            },
            'cost': Cost(tokens_in=25, tokens_out=15, cost_usd=0.00008, model='claude-haiku-4.5')
        },
        {
            'event': 'webrtc_offer_created',
            'component': 'IF.webrtc',
            'trace_id': 'webrtc-trace-001',
            'timestamp': base_time + timedelta(milliseconds=100),
            'payload': {
                'connection_id': 'webrtc-conn-001',
                'sdp_lines_count': 42,
                'media_sections': ['audio', 'video'],
                'video_codecs': ['VP8', 'VP9', 'H264']
            },
            'cost': Cost(tokens_in=80, tokens_out=50, cost_usd=0.0002, model='claude-haiku-4.5')
        },
        {
            'event': 'webrtc_answer_received',
            'component': 'IF.webrtc',
            'trace_id': 'webrtc-trace-001',
            'timestamp': base_time + timedelta(milliseconds=150),
            'payload': {
                'connection_id': 'webrtc-conn-001',
                'remote_peer_id': 'peer-bob-001',
                'sdp_lines_count': 44,
                'media_sections': ['audio', 'video']
            },
            'cost': Cost(tokens_in=70, tokens_out=45, cost_usd=0.00018, model='claude-haiku-4.5')
        },
        {
            'event': 'webrtc_connection_established',
            'component': 'IF.webrtc',
            'trace_id': 'webrtc-trace-001',
            'timestamp': base_time + timedelta(milliseconds=500),
            'payload': {
                'connection_id': 'webrtc-conn-001',
                'local_candidate': '192.168.1.50:54321',
                'remote_candidate': '192.168.1.75:54320',
                'selected_candidate_pair_type': 'host-to-host',
                'rtt_ms': 5,
                'state': 'connected'
            },
            'cost': Cost(tokens_in=60, tokens_out=35, cost_usd=0.00015, model='claude-haiku-4.5')
        },
        {
            'event': 'webrtc_media_stream_started',
            'component': 'IF.webrtc',
            'trace_id': 'webrtc-trace-001',
            'timestamp': base_time + timedelta(milliseconds=600),
            'payload': {
                'connection_id': 'webrtc-conn-001',
                'stream_id': 'stream-video-001',
                'media_type': 'video',
                'codec': 'VP8',
                'bitrate_kbps': 2500,
                'frame_rate': 30
            },
            'cost': Cost(tokens_in=90, tokens_out=55, cost_usd=0.00025, model='claude-haiku-4.5')
        }
    ]


def get_h323_events() -> List[Dict[str, Any]]:
    """
    Sample H.323 (VoIP protocol) events.

    H.323 is an ITU standard for multimedia communication.
    Simulates call setup and media establishment.

    Returns:
        List of H.323 event dictionaries with realistic payload data
    """
    base_time = datetime.utcnow()

    return [
        {
            'event': 'h323_endpoint_registered',
            'component': 'IF.h323',
            'trace_id': 'h323-trace-001',
            'timestamp': base_time,
            'payload': {
                'endpoint_id': 'h323-endpoint-001',
                'endpoint_name': 'Conference Room 1',
                'gatekeeper_id': 'gk-main-001',
                'ip_address': '10.0.1.100',
                'port': 1720,
                'bandwidth_allocation': 2048
            },
            'cost': Cost(tokens_in=35, tokens_out=20, cost_usd=0.0001, model='claude-haiku-4.5')
        },
        {
            'event': 'h323_call_initiated',
            'component': 'IF.h323',
            'trace_id': 'h323-trace-001',
            'timestamp': base_time + timedelta(milliseconds=100),
            'payload': {
                'call_id': 'h323-call-001',
                'calling_endpoint': 'h323-endpoint-001',
                'called_alias': 'conference@example.com',
                'call_type': 'point_to_point',
                'bandwidth_required': 384
            },
            'cost': Cost(tokens_in=55, tokens_out=30, cost_usd=0.00015, model='claude-haiku-4.5')
        },
        {
            'event': 'h323_call_proceeding',
            'component': 'IF.h323',
            'trace_id': 'h323-trace-001',
            'timestamp': base_time + timedelta(milliseconds=200),
            'payload': {
                'call_id': 'h323-call-001',
                'calling_endpoint': 'h323-endpoint-001',
                'called_endpoint': 'h323-endpoint-002',
                'bandwidth_confirmed': 384,
                'call_state': 'proceeding'
            },
            'cost': Cost(tokens_in=50, tokens_out=28, cost_usd=0.00012, model='claude-haiku-4.5')
        },
        {
            'event': 'h323_alerting',
            'component': 'IF.h323',
            'trace_id': 'h323-trace-001',
            'timestamp': base_time + timedelta(milliseconds=500),
            'payload': {
                'call_id': 'h323-call-001',
                'called_endpoint': 'h323-endpoint-002',
                'alerting_message': 'User alerting',
                'ring_indication': True
            },
            'cost': Cost(tokens_in=30, tokens_out=18, cost_usd=0.0001, model='claude-haiku-4.5')
        },
        {
            'event': 'h323_connect',
            'component': 'IF.h323',
            'trace_id': 'h323-trace-001',
            'timestamp': base_time + timedelta(seconds=3),
            'payload': {
                'call_id': 'h323-call-001',
                'calling_endpoint': 'h323-endpoint-001',
                'called_endpoint': 'h323-endpoint-002',
                'connection_address': '10.0.1.200:1234',
                'media_channels': ['audio', 'video'],
                'call_state': 'active'
            },
            'cost': Cost(tokens_in=75, tokens_out=40, cost_usd=0.0002, model='claude-haiku-4.5')
        },
        {
            'event': 'h323_call_active',
            'component': 'IF.h323',
            'trace_id': 'h323-trace-001',
            'timestamp': base_time + timedelta(seconds=4),
            'payload': {
                'call_id': 'h323-call-001',
                'call_duration_seconds': 1,
                'audio_codec': 'G.711',
                'video_codec': 'H.264',
                'jitter_ms': 2.5,
                'packet_loss_percent': 0.1
            },
            'cost': Cost(tokens_in=60, tokens_out=35, cost_usd=0.00018, model='claude-haiku-4.5')
        },
        {
            'event': 'h323_disconnect_indication',
            'component': 'IF.h323',
            'trace_id': 'h323-trace-001',
            'timestamp': base_time + timedelta(seconds=30),
            'payload': {
                'call_id': 'h323-call-001',
                'disconnect_reason': 'normal_disconnect',
                'total_call_duration_seconds': 26,
                'release_code': 0
            },
            'cost': Cost(tokens_in=40, tokens_out=22, cost_usd=0.00012, model='claude-haiku-4.5')
        }
    ]


def get_sip_events() -> List[Dict[str, Any]]:
    """
    Sample SIP (Session Initiation Protocol) events.

    SIP is the standard protocol for VoIP and multimedia session control.
    Simulates a complete SIP dialog lifecycle.

    Returns:
        List of SIP event dictionaries with realistic payload data
    """
    base_time = datetime.utcnow()

    return [
        {
            'event': 'sip_register_request',
            'component': 'IF.sip',
            'trace_id': 'sip-trace-001',
            'timestamp': base_time,
            'payload': {
                'user_agent': 'alice@example.com',
                'registrar_uri': 'sip:example.com',
                'contact_uri': 'sip:alice@192.168.1.50:5060',
                'expiration_seconds': 3600,
                'request_uri': 'sip:example.com'
            },
            'cost': Cost(tokens_in=45, tokens_out=25, cost_usd=0.00012, model='claude-haiku-4.5')
        },
        {
            'event': 'sip_register_success',
            'component': 'IF.sip',
            'trace_id': 'sip-trace-001',
            'timestamp': base_time + timedelta(milliseconds=50),
            'payload': {
                'user_agent': 'alice@example.com',
                'status_code': 200,
                'reason_phrase': 'OK',
                'registered_contacts': 1,
                'expires_seconds': 3600
            },
            'cost': Cost(tokens_in=35, tokens_out=20, cost_usd=0.0001, model='claude-haiku-4.5')
        },
        {
            'event': 'sip_invite_request',
            'component': 'IF.sip',
            'trace_id': 'sip-trace-001',
            'timestamp': base_time + timedelta(seconds=5),
            'payload': {
                'from_uri': 'sip:alice@example.com',
                'to_uri': 'sip:bob@example.com',
                'call_id': 'sip-call-001@192.168.1.50',
                'cseq': 1,
                'method': 'INVITE',
                'sdp_version': 0,
                'session_name': 'SIP Session'
            },
            'cost': Cost(tokens_in=90, tokens_out=50, cost_usd=0.00025, model='claude-haiku-4.5')
        },
        {
            'event': 'sip_trying_response',
            'component': 'IF.sip',
            'trace_id': 'sip-trace-001',
            'timestamp': base_time + timedelta(seconds=5.1),
            'payload': {
                'call_id': 'sip-call-001@192.168.1.50',
                'cseq': 1,
                'status_code': 100,
                'reason_phrase': 'Trying',
                'server': 'bob@example.com'
            },
            'cost': Cost(tokens_in=25, tokens_out=15, cost_usd=0.00008, model='claude-haiku-4.5')
        },
        {
            'event': 'sip_ringing_response',
            'component': 'IF.sip',
            'trace_id': 'sip-trace-001',
            'timestamp': base_time + timedelta(seconds=5.5),
            'payload': {
                'call_id': 'sip-call-001@192.168.1.50',
                'cseq': 1,
                'status_code': 180,
                'reason_phrase': 'Ringing',
                'contact_uri': 'sip:bob@192.168.1.75:5060'
            },
            'cost': Cost(tokens_in=30, tokens_out=18, cost_usd=0.00009, model='claude-haiku-4.5')
        },
        {
            'event': 'sip_ok_response',
            'component': 'IF.sip',
            'trace_id': 'sip-trace-001',
            'timestamp': base_time + timedelta(seconds=8),
            'payload': {
                'call_id': 'sip-call-001@192.168.1.50',
                'cseq': 1,
                'status_code': 200,
                'reason_phrase': 'OK',
                'contact_uri': 'sip:bob@192.168.1.75:5060',
                'sdp_version': 0
            },
            'cost': Cost(tokens_in=100, tokens_out=60, cost_usd=0.0003, model='claude-haiku-4.5')
        },
        {
            'event': 'sip_ack_request',
            'component': 'IF.sip',
            'trace_id': 'sip-trace-001',
            'timestamp': base_time + timedelta(seconds=8.1),
            'payload': {
                'from_uri': 'sip:alice@example.com',
                'to_uri': 'sip:bob@example.com',
                'call_id': 'sip-call-001@192.168.1.50',
                'cseq': 1,
                'method': 'ACK',
                'dialog_state': 'confirmed'
            },
            'cost': Cost(tokens_in=40, tokens_out=22, cost_usd=0.00012, model='claude-haiku-4.5')
        },
        {
            'event': 'sip_media_session_active',
            'component': 'IF.sip',
            'trace_id': 'sip-trace-001',
            'timestamp': base_time + timedelta(seconds=9),
            'payload': {
                'call_id': 'sip-call-001@192.168.1.50',
                'audio_codec': 'PCMU',
                'video_codec': None,
                'rtp_payload_type': 0,
                'jitter_ms': 3.0,
                'latency_ms': 45,
                'session_duration_seconds': 1
            },
            'cost': Cost(tokens_in=70, tokens_out=40, cost_usd=0.0002, model='claude-haiku-4.5')
        },
        {
            'event': 'sip_bye_request',
            'component': 'IF.sip',
            'trace_id': 'sip-trace-001',
            'timestamp': base_time + timedelta(seconds=45),
            'payload': {
                'from_uri': 'sip:alice@example.com',
                'to_uri': 'sip:bob@example.com',
                'call_id': 'sip-call-001@192.168.1.50',
                'cseq': 2,
                'method': 'BYE',
                'reason': 'call_ended'
            },
            'cost': Cost(tokens_in=35, tokens_out=20, cost_usd=0.0001, model='claude-haiku-4.5')
        },
        {
            'event': 'sip_bye_response',
            'component': 'IF.sip',
            'trace_id': 'sip-trace-001',
            'timestamp': base_time + timedelta(seconds=45.1),
            'payload': {
                'call_id': 'sip-call-001@192.168.1.50',
                'cseq': 2,
                'status_code': 200,
                'reason_phrase': 'OK',
                'total_call_duration_seconds': 36,
                'dialog_state': 'terminated'
            },
            'cost': Cost(tokens_in=25, tokens_out=15, cost_usd=0.00008, model='claude-haiku-4.5')
        }
    ]


def get_cost_data() -> List[Dict[str, Any]]:
    """
    Sample cost objects for different models and operation types.

    Returns:
        List of cost dictionaries representing various operations
    """
    return [
        {
            'operation': 'scan_file',
            'component': 'IF.yologuard',
            'model': 'claude-haiku-4.5',
            'tokens_in': 500,
            'tokens_out': 100,
            'cost_usd': 0.0002
        },
        {
            'operation': 'analyze_pattern',
            'component': 'IF.guard',
            'model': 'claude-haiku-4.5',
            'tokens_in': 1000,
            'tokens_out': 250,
            'cost_usd': 0.0005
        },
        {
            'operation': 'verify_decision',
            'component': 'IF.swarm',
            'model': 'claude-sonnet-4.5',
            'tokens_in': 2000,
            'tokens_out': 500,
            'cost_usd': 0.003
        },
        {
            'operation': 'optimize_cost',
            'component': 'IF.optimise',
            'model': 'claude-haiku-4.5',
            'tokens_in': 800,
            'tokens_out': 200,
            'cost_usd': 0.0003
        },
        {
            'operation': 'generate_report',
            'component': 'IF.witness',
            'model': 'claude-sonnet-4.5',
            'tokens_in': 3000,
            'tokens_out': 1000,
            'cost_usd': 0.005
        },
        {
            'operation': 'ndi_frame_analysis',
            'component': 'IF.ndi',
            'model': 'claude-haiku-4.5',
            'tokens_in': 200,
            'tokens_out': 50,
            'cost_usd': 0.00008
        },
        {
            'operation': 'webrtc_connection_setup',
            'component': 'IF.webrtc',
            'model': 'claude-haiku-4.5',
            'tokens_in': 400,
            'tokens_out': 150,
            'cost_usd': 0.0002
        },
        {
            'operation': 'h323_call_management',
            'component': 'IF.h323',
            'model': 'claude-haiku-4.5',
            'tokens_in': 350,
            'tokens_out': 120,
            'cost_usd': 0.00015
        },
        {
            'operation': 'sip_dialog_control',
            'component': 'IF.sip',
            'model': 'claude-haiku-4.5',
            'tokens_in': 300,
            'tokens_out': 100,
            'cost_usd': 0.00012
        }
    ]


def create_test_database(db_path: Optional[Path] = None) -> WitnessDatabase:
    """
    Create a pre-populated test database with sample witness entries.

    Creates a temporary test database and populates it with:
    - NDI frame publishing events
    - WebRTC connection events
    - H.323 VoIP call events
    - SIP dialog events

    Each event includes cost tracking for integration testing.

    Args:
        db_path: Optional path to database file. If None, creates temporary database.

    Returns:
        WitnessDatabase instance populated with test data

    Example:
        >>> db = create_test_database()
        >>> trace = db.get_trace('ndi-trace-001')
        >>> print(f"Trace has {len(trace.entries)} entries")
        >>> db.close()
    """
    # Use provided path or create temporary
    if db_path is None:
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_witness.db'

    # Create crypto and database
    key_path = db_path.parent / 'test_witness_key.pem'
    crypto = WitnessCrypto(key_path)
    db = WitnessDatabase(db_path, crypto)

    # Prepare batch data for all protocols
    all_events = []

    # Add NDI events
    ndi_events = get_ndi_events()
    for event_data in ndi_events:
        timestamp = event_data.pop('timestamp')
        cost = event_data.pop('cost')
        all_events.append({
            **event_data,
            'timestamp': timestamp,
            'cost': cost
        })

    # Add WebRTC events
    webrtc_events = get_webrtc_events()
    for event_data in webrtc_events:
        timestamp = event_data.pop('timestamp')
        cost = event_data.pop('cost')
        all_events.append({
            **event_data,
            'timestamp': timestamp,
            'cost': cost
        })

    # Add H.323 events
    h323_events = get_h323_events()
    for event_data in h323_events:
        timestamp = event_data.pop('timestamp')
        cost = event_data.pop('cost')
        all_events.append({
            **event_data,
            'timestamp': timestamp,
            'cost': cost
        })

    # Add SIP events
    sip_events = get_sip_events()
    for event_data in sip_events:
        timestamp = event_data.pop('timestamp')
        cost = event_data.pop('cost')
        all_events.append({
            **event_data,
            'timestamp': timestamp,
            'cost': cost
        })

    # Sort by timestamp to maintain chronological order
    all_events.sort(key=lambda x: x['timestamp'])

    # Prepare batch insert data
    batch_data = []
    for event in all_events:
        batch_data.append({
            'event': event['event'],
            'component': event['component'],
            'trace_id': event['trace_id'],
            'payload': event['payload'],
            'cost': event['cost']
        })

    # Insert all entries in batch
    db.create_entries_batch(batch_data)

    return db


# Convenience function for getting all trace IDs
def get_trace_ids() -> List[str]:
    """
    Get all trace IDs available in fixtures.

    Returns:
        List of trace IDs: ['ndi-trace-001', 'webrtc-trace-001', 'h323-trace-001', 'sip-trace-001']
    """
    return [
        'ndi-trace-001',
        'webrtc-trace-001',
        'h323-trace-001',
        'sip-trace-001',
    ]


# Convenience function for getting all events
def get_all_protocol_events() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all protocol events organized by protocol type.

    Returns:
        Dictionary with keys: 'ndi', 'webrtc', 'h323', 'sip', each containing list of events
    """
    return {
        'ndi': get_ndi_events(),
        'webrtc': get_webrtc_events(),
        'h323': get_h323_events(),
        'sip': get_sip_events(),
    }
