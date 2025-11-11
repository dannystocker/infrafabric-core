"""
Test Fixtures for IF.witness Integration Tests

Provides reusable test data and database fixtures for:
- Sessions 1-4 protocol testing (NDI, WebRTC, H.323, SIP)
- Cost tracking and optimization scenarios
- Hash chain verification
- Trace propagation

Usage:
    from tests.fixtures import (
        get_ndi_events,
        get_webrtc_events,
        get_h323_events,
        get_sip_events,
        get_cost_data,
        create_test_database
    )
"""

from .witness_fixtures import (
    get_ndi_events,
    get_webrtc_events,
    get_h323_events,
    get_sip_events,
    get_cost_data,
    create_test_database,
)

__all__ = [
    'get_ndi_events',
    'get_webrtc_events',
    'get_h323_events',
    'get_sip_events',
    'get_cost_data',
    'create_test_database',
]
