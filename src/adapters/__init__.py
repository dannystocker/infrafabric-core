"""
SIP Adapter Framework - Unified interface for 6 SIP server implementations.

This package provides a standardized abstract base class (SIPAdapterBase) that all
SIP server adapters must inherit from, ensuring consistent interfaces across:

- Asterisk (AMI protocol) ✅
- FreeSWITCH (ESL protocol) ✅
- Kamailio (JSON-RPC protocol) ✅
- OpenSIPs (MI JSON-RPC protocol) ✅
- Flexisip (HTTP REST protocol) ✅
- Yate (External Module protocol) ✅

Protocol: IF.TTT (Traceable/Transparent/Trustworthy) compliance
Philosophy: Wu Lun (五伦) Confucian relationship mapping for call hierarchy

Author: Session 7 - IF.bus SIP Adapters
Version: 1.0.0 (Phase 2 Complete)
Date: 2025-11-12
"""

from src.adapters.sip_adapter_base import (
    # Base class
    SIPAdapterBase,
    # Enums
    CallState,
    ConnectionState,
    HealthStatus,
    ErrorSeverity,
    # Data classes
    CallStateEvent,
    IncomingCallEvent,
    ErrorEvent,
    ConnectionStateEvent,
    # Exceptions
    SIPAdapterError,
    ConnectionError,
    CallError,
    ConfigurationError,
    TimeoutError,
    # Utilities
    EventEmitter,
    MetricsCollector,
    # Factory
    create_adapter,
)

# Import all adapter implementations
from src.adapters.asterisk_adapter import AsteriskAdapter
from src.adapters.kamailio_adapter import KamailioAdapter
from src.adapters.freeswitch_adapter import FreeSWITCHAdapter
from src.adapters.flexisip_adapter import FlexisipAdapter
from src.adapters.opensips_adapter import OpenSIPSAdapter
from src.adapters.yate_adapter import YateAdapter

__version__ = "1.0.0"
__author__ = "Session 7 - IF.bus SIP Adapters"
__all__ = [
    # Main class
    "SIPAdapterBase",
    # Enums
    "CallState",
    "ConnectionState",
    "HealthStatus",
    "ErrorSeverity",
    # Events
    "CallStateEvent",
    "IncomingCallEvent",
    "ErrorEvent",
    "ConnectionStateEvent",
    # Exceptions
    "SIPAdapterError",
    "ConnectionError",
    "CallError",
    "ConfigurationError",
    "TimeoutError",
    # Utilities
    "EventEmitter",
    "MetricsCollector",
    # Factory
    "create_adapter",
    # Adapter implementations
    "AsteriskAdapter",
    "KamailioAdapter",
    "FreeSWITCHAdapter",
    "FlexisipAdapter",
    "OpenSIPSAdapter",
    "YateAdapter",
]
