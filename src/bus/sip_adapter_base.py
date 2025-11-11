"""
IF.bus SIP Adapter Base Class - Unified Interface to Heterogeneous SIP Servers

Applies IF.talent pattern: Abstract interface with bloom pattern detection

Supported SIP Servers:
- Asterisk (early bloomer - simple calls easy, complex features hard)
- FreeSWITCH (steady performer - consistent across scenarios)
- Kamailio (late bloomer - excels at high-scale routing)
- OpenSIPs (balanced - good WebRTC support)
- Elastix (legacy - FreePBX-based, H.323 bridge)
- Yate (multi-protocol - H.323, SIP, IAX2)
- Jitsi (WebRTC-native - conferencing focus)

Philosophy Grounding:
- IF.ground:principle_4 (Underdetermination): Multiple servers solve same problem differently
- IF.ground:principle_6 (Pragmatism): Judge by usefulness (bloom patterns matter)
- Wu Lun: Adapters as friends (朋友) - each with unique strengths

Author: Session 6 (IF.talent) helping Session 7 (IF.bus)
Date: 2025-11-11
Citation: if://component/bus/sip-adapter-base-v1
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json


class SIPServerType(Enum):
    """Enumeration of supported SIP server types"""
    ASTERISK = "asterisk"
    FREESWITCH = "freeswitch"
    KAMAILIO = "kamailio"
    OPENSIPS = "opensips"
    ELASTIX = "elastix"
    YATE = "yate"
    JITSI = "jitsi"
    UNKNOWN = "unknown"


class BloomPattern(Enum):
    """Bloom pattern classification (from IF.talent)"""
    EARLY_BLOOMER = "early_bloomer"  # Simple tasks easy, complex hard
    STEADY_PERFORMER = "steady_performer"  # Consistent across all scenarios
    LATE_BLOOMER = "late_bloomer"  # Excels at high-scale/complex scenarios


@dataclass
class SIPServerCapability:
    """
    Capability profile for SIP server (IF.talent pattern)

    Similar to IF.talent Capability dataclass, but for SIP servers
    """
    server_type: SIPServerType
    bloom_pattern: BloomPattern
    best_for: List[str]  # Use cases where it excels
    avoid_for: List[str]  # Use cases where it struggles
    max_concurrent_calls: int  # Performance limit
    protocols_supported: List[str]  # SIP, H.323, WebRTC, etc.
    auth_methods: List[str]  # apikey, basic, oauth, custom
    avg_setup_latency_ms: float  # Call setup time
    cost_per_call: float  # Operational cost (if cloud-hosted)


# Capability profiles for each SIP server type
SIP_SERVER_CAPABILITIES = {
    SIPServerType.ASTERISK: SIPServerCapability(
        server_type=SIPServerType.ASTERISK,
        bloom_pattern=BloomPattern.EARLY_BLOOMER,
        best_for=["simple_pbx", "voicemail", "ivr", "small_office"],
        avoid_for=["high_scale_routing", "complex_conferencing", "advanced_media"],
        max_concurrent_calls=500,
        protocols_supported=["SIP", "H.323", "IAX2"],
        auth_methods=["basic", "digest"],
        avg_setup_latency_ms=250.0,
        cost_per_call=0.001
    ),
    SIPServerType.FREESWITCH: SIPServerCapability(
        server_type=SIPServerType.FREESWITCH,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["conferencing", "media_processing", "transcoding", "mid_scale"],
        avoid_for=["extreme_scale_routing"],  # Kamailio better for this
        max_concurrent_calls=2000,
        protocols_supported=["SIP", "H.323", "WebRTC", "RTMP"],
        auth_methods=["basic", "digest", "custom"],
        avg_setup_latency_ms=180.0,
        cost_per_call=0.0008
    ),
    SIPServerType.KAMAILIO: SIPServerCapability(
        server_type=SIPServerType.KAMAILIO,
        bloom_pattern=BloomPattern.LATE_BLOOMER,
        best_for=["high_scale_routing", "load_balancing", "enterprise", "carrier_grade"],
        avoid_for=["media_processing", "transcoding"],  # Not a B2BUA
        max_concurrent_calls=10000,
        protocols_supported=["SIP", "WebRTC"],
        auth_methods=["basic", "digest", "oauth", "custom"],
        avg_setup_latency_ms=120.0,
        cost_per_call=0.0005
    ),
    SIPServerType.OPENSIPS: SIPServerCapability(
        server_type=SIPServerType.OPENSIPS,
        bloom_pattern=BloomPattern.LATE_BLOOMER,
        best_for=["webrtc_gateway", "high_scale_routing", "load_balancing"],
        avoid_for=["complex_media", "ivr"],
        max_concurrent_calls=8000,
        protocols_supported=["SIP", "WebRTC"],
        auth_methods=["basic", "digest", "oauth"],
        avg_setup_latency_ms=140.0,
        cost_per_call=0.0006
    ),
    SIPServerType.ELASTIX: SIPServerCapability(
        server_type=SIPServerType.ELASTIX,
        bloom_pattern=BloomPattern.EARLY_BLOOMER,
        best_for=["legacy_h323", "pbx", "fax", "small_enterprise"],
        avoid_for=["high_scale", "modern_webrtc"],
        max_concurrent_calls=300,
        protocols_supported=["SIP", "H.323", "IAX2"],
        auth_methods=["basic", "digest"],
        avg_setup_latency_ms=300.0,
        cost_per_call=0.0012
    ),
    SIPServerType.YATE: SIPServerCapability(
        server_type=SIPServerType.YATE,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["multi_protocol", "custom_routing", "flexibility"],
        avoid_for=["gui_administration"],  # Less polished UI
        max_concurrent_calls=1500,
        protocols_supported=["SIP", "H.323", "IAX2", "Jabber"],
        auth_methods=["basic", "custom"],
        avg_setup_latency_ms=200.0,
        cost_per_call=0.0009
    ),
    SIPServerType.JITSI: SIPServerCapability(
        server_type=SIPServerType.JITSI,
        bloom_pattern=BloomPattern.EARLY_BLOOMER,
        best_for=["webrtc_conferencing", "browser_clients", "video"],
        avoid_for=["traditional_sip", "high_scale_routing"],
        max_concurrent_calls=200,
        protocols_supported=["SIP", "WebRTC", "XMPP"],
        auth_methods=["oauth", "custom"],
        avg_setup_latency_ms=350.0,
        cost_per_call=0.0015
    )
}


@dataclass
class CallSession:
    """Active SIP call session"""
    call_id: str
    from_uri: str
    to_uri: str
    codec: str
    status: str  # "ringing", "active", "hold", "ended"
    started_at: str
    duration_seconds: float
    cost_usd: float


class SIPServerAdapter(ABC):
    """
    Abstract base class for all SIP server adapters

    Unified interface to heterogeneous SIP servers (Asterisk, FreeSWITCH, etc.)

    Philosophy:
    - Wu Lun: Each adapter is a friend (朋友) with unique strengths
    - IF.talent: Apply bloom patterns to select optimal server for task
    - IF.ground: Pragmatism - judge by usefulness, not ideology
    """

    def __init__(self, server_name: str, host: str, port: int = 5060):
        """
        Initialize SIP server adapter

        Args:
            server_name: Human-readable name (e.g., "myasterisk")
            host: Server hostname/IP
            port: SIP port (default: 5060)
        """
        self.server_name = server_name
        self.host = host
        self.port = port
        self.server_type = SIPServerType.UNKNOWN
        self.capability = None
        self.connected = False
        self.active_calls: Dict[str, CallSession] = {}

    @abstractmethod
    def connect(self, auth_config: Dict) -> bool:
        """
        Connect to SIP server with authentication

        Args:
            auth_config: Authentication configuration
                {
                    "method": "apikey" | "basic" | "oauth" | "custom",
                    "credentials": {...}
                }

        Returns:
            True if connected successfully
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from SIP server

        Returns:
            True if disconnected successfully
        """
        pass

    @abstractmethod
    def make_call(
        self,
        from_uri: str,
        to_uri: str,
        codec: str = "opus",
        options: Optional[Dict] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Initiate SIP call

        Args:
            from_uri: Caller SIP URI (e.g., "sip:alice@example.com")
            to_uri: Callee SIP URI (e.g., "sip:bob@example.com")
            codec: Audio codec (default: opus)
            options: Additional call options

        Returns:
            (success, call_id) tuple
        """
        pass

    @abstractmethod
    def hangup(self, call_id: str) -> bool:
        """
        Terminate SIP call

        Args:
            call_id: Call identifier

        Returns:
            True if call terminated successfully
        """
        pass

    @abstractmethod
    def hold(self, call_id: str) -> bool:
        """
        Put call on hold

        Args:
            call_id: Call identifier

        Returns:
            True if call placed on hold
        """
        pass

    @abstractmethod
    def resume(self, call_id: str) -> bool:
        """
        Resume held call

        Args:
            call_id: Call identifier

        Returns:
            True if call resumed
        """
        pass

    @abstractmethod
    def transfer(self, call_id: str, to_uri: str) -> bool:
        """
        Transfer call to another URI

        Args:
            call_id: Call identifier
            to_uri: Transfer destination URI

        Returns:
            True if transfer initiated
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict:
        """
        Get SIP server health status

        Returns:
            {
                "connected": bool,
                "active_calls": int,
                "cpu_usage": float,
                "memory_usage": float,
                "uptime_seconds": float
            }
        """
        pass

    @abstractmethod
    def get_active_calls(self) -> List[CallSession]:
        """
        List all active calls

        Returns:
            List of active call sessions
        """
        pass

    # Common utilities (implemented in base class)

    def detect_server_type(self) -> SIPServerType:
        """
        Auto-detect SIP server type from SIP OPTIONS response

        Strategy:
        1. Send SIP OPTIONS request
        2. Parse User-Agent header
        3. Match against known patterns

        Returns:
            Detected server type
        """
        # Mock implementation (real version would send OPTIONS)
        user_agent_patterns = {
            "Asterisk": SIPServerType.ASTERISK,
            "FreeSWITCH": SIPServerType.FREESWITCH,
            "Kamailio": SIPServerType.KAMAILIO,
            "OpenSIPS": SIPServerType.OPENSIPS,
            "Elastix": SIPServerType.ELASTIX,
            "Yate": SIPServerType.YATE,
            "Jitsi": SIPServerType.JITSI
        }

        # Real implementation would:
        # 1. Send OPTIONS sip:host:port SIP/2.0
        # 2. Parse response header: User-Agent: Asterisk PBX 18.0.0
        # 3. Match against patterns above

        return SIPServerType.UNKNOWN

    def validate_auth(self, auth_config: Dict) -> Tuple[bool, str]:
        """
        Test authentication without making full connection

        Args:
            auth_config: Authentication configuration

        Returns:
            (valid, error_message) tuple
        """
        method = auth_config.get("method", "basic")

        if method not in ["apikey", "basic", "oauth", "custom"]:
            return False, f"Unsupported auth method: {method}"

        if "credentials" not in auth_config:
            return False, "Missing credentials"

        # Real implementation would test auth against server
        return True, ""

    def get_capability_profile(self) -> Optional[SIPServerCapability]:
        """
        Get capability profile for this server type

        Returns bloom pattern and performance characteristics

        Returns:
            SIPServerCapability or None if unknown type
        """
        if self.server_type == SIPServerType.UNKNOWN:
            self.server_type = self.detect_server_type()

        return SIP_SERVER_CAPABILITIES.get(self.server_type)

    def is_suitable_for(self, use_case: str) -> Tuple[bool, str]:
        """
        Check if this server is suitable for a use case

        Applies IF.talent bloom pattern logic

        Args:
            use_case: Use case string (e.g., "high_scale_routing")

        Returns:
            (suitable, reasoning) tuple
        """
        capability = self.get_capability_profile()

        if not capability:
            return False, "Server type unknown, cannot assess suitability"

        if use_case in capability.best_for:
            return True, f"{self.server_type.value} excels at {use_case} ({capability.bloom_pattern.value})"

        if use_case in capability.avoid_for:
            return False, f"{self.server_type.value} struggles with {use_case}"

        return True, f"{self.server_type.value} can handle {use_case} (neutral)"

    def estimate_cost(self, duration_seconds: float) -> float:
        """
        Estimate call cost based on duration

        Args:
            duration_seconds: Call duration

        Returns:
            Estimated cost in USD
        """
        capability = self.get_capability_profile()
        if not capability:
            return 0.0

        return capability.cost_per_call * (duration_seconds / 60.0)

    def to_dict(self) -> Dict:
        """Export adapter configuration"""
        return {
            "server_name": self.server_name,
            "host": self.host,
            "port": self.port,
            "server_type": self.server_type.value,
            "connected": self.connected,
            "active_calls": len(self.active_calls)
        }


# Example concrete adapter (Asterisk)
class AsteriskAdapter(SIPServerAdapter):
    """Asterisk-specific implementation"""

    def __init__(self, server_name: str, host: str, port: int = 5060):
        super().__init__(server_name, host, port)
        self.server_type = SIPServerType.ASTERISK
        self.capability = SIP_SERVER_CAPABILITIES[SIPServerType.ASTERISK]

    def connect(self, auth_config: Dict) -> bool:
        # Asterisk AMI connection implementation
        self.connected = True
        return True

    def disconnect(self) -> bool:
        self.connected = False
        return True

    def make_call(self, from_uri, to_uri, codec="opus", options=None):
        # Asterisk call origination via AMI
        call_id = f"asterisk-call-{len(self.active_calls)+1}"
        return True, call_id

    def hangup(self, call_id):
        if call_id in self.active_calls:
            del self.active_calls[call_id]
            return True
        return False

    def hold(self, call_id):
        return True

    def resume(self, call_id):
        return True

    def transfer(self, call_id, to_uri):
        return True

    def get_status(self):
        return {
            "connected": self.connected,
            "active_calls": len(self.active_calls),
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "uptime_seconds": 0.0
        }

    def get_active_calls(self):
        return list(self.active_calls.values())


# CLI usage example
if __name__ == "__main__":
    # Example: Connect to Asterisk server
    asterisk = AsteriskAdapter("myasterisk", "10.0.0.5", 5060)

    # Test auth
    auth_valid, error = asterisk.validate_auth({
        "method": "basic",
        "credentials": {"username": "admin", "password": "secret"}
    })
    print(f"Auth valid: {auth_valid}")

    # Check capability
    capability = asterisk.get_capability_profile()
    print(f"\nAsterisk Profile:")
    print(f"  Bloom: {capability.bloom_pattern.value}")
    print(f"  Best for: {', '.join(capability.best_for)}")
    print(f"  Avoid: {', '.join(capability.avoid_for)}")

    # Check suitability
    suitable, reason = asterisk.is_suitable_for("simple_pbx")
    print(f"\nSuitable for simple_pbx: {suitable} - {reason}")

    suitable, reason = asterisk.is_suitable_for("high_scale_routing")
    print(f"Suitable for high_scale_routing: {suitable} - {reason}")
