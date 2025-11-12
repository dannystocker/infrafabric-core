"""
IF.integrations vMix Adapter Base Class - Unified Interface to vMix Instances

Applies IF.talent pattern: Abstract interface with bloom pattern detection

vMix Feature Bloom Patterns:
- Early bloomer: Basic switching, NDI I/O, simple overlays
- Steady performer: Streaming, recording, audio mixing (core production features)
- Late bloomer: Advanced scripting, automation, custom APIs

Philosophy Grounding:
- IF.ground:principle_4 (Underdetermination): Multiple vMix versions solve same problem differently
- IF.ground:principle_6 (Pragmatism): Judge by usefulness (bloom patterns matter)
- Wu Lun: vMix features as friends (朋友) - each with unique strengths

Author: Session 6 (IF.talent) + Session 7 (IF.bus)
Date: 2025-11-12
Citation: if://component/integrations/vmix-adapter-base-v1
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json


class VMixVersion(Enum):
    """Enumeration of vMix editions"""
    BASIC = "basic"  # Free, limited features
    HD = "hd"  # 1080p, more inputs
    FOURK = "4k"  # 4K support, unlimited inputs
    PRO = "pro"  # Full feature set
    MAX = "max"  # 8 channels, advanced features
    UNKNOWN = "unknown"


class BloomPattern(Enum):
    """Bloom pattern classification (from IF.talent)"""
    EARLY_BLOOMER = "early_bloomer"  # Simple tasks easy, complex hard
    STEADY_PERFORMER = "steady_performer"  # Consistent across all scenarios
    LATE_BLOOMER = "late_bloomer"  # Excels at high-scale/complex scenarios


class VMixFeatureCategory(Enum):
    """vMix feature categories"""
    BASIC_SWITCHING = "basic_switching"  # Cut, fade, transitions
    INPUT_MANAGEMENT = "input_management"  # Add/remove inputs, NDI, capture cards
    STREAMING = "streaming"  # RTMP, RTMPS, multistreaming
    RECORDING = "recording"  # Local recording, ISO recording
    AUDIO = "audio"  # Mixing, ducking, EQ
    OVERLAYS = "overlays"  # Titles, graphics, lower thirds
    AUTOMATION = "automation"  # Scripting, triggers, shortcuts
    ADVANCED_API = "advanced_api"  # Custom integrations, web controller


@dataclass
class VMixCapability:
    """
    Capability profile for vMix feature category (IF.talent pattern)

    Similar to SIPServerCapability, but for vMix features
    """
    feature_category: VMixFeatureCategory
    bloom_pattern: BloomPattern
    best_for: List[str]  # Use cases where it excels
    avoid_for: List[str]  # Use cases where it struggles
    requires_version: VMixVersion  # Minimum vMix edition needed
    avg_setup_latency_ms: float  # Time to execute operation
    learning_curve_hours: float  # Time to master feature
    stability_score: int  # 1-100 (100 = rock solid)


# Capability profiles for each vMix feature category
VMIX_FEATURE_CAPABILITIES = {
    VMixFeatureCategory.BASIC_SWITCHING: VMixCapability(
        feature_category=VMixFeatureCategory.BASIC_SWITCHING,
        bloom_pattern=BloomPattern.EARLY_BLOOMER,
        best_for=["simple_cuts", "fades", "basic_transitions", "small_productions"],
        avoid_for=["complex_multi_layer", "high_frequency_switching"],
        requires_version=VMixVersion.BASIC,
        avg_setup_latency_ms=50.0,
        learning_curve_hours=1.0,
        stability_score=98
    ),
    VMixFeatureCategory.INPUT_MANAGEMENT: VMixCapability(
        feature_category=VMixFeatureCategory.INPUT_MANAGEMENT,
        bloom_pattern=BloomPattern.EARLY_BLOOMER,
        best_for=["ndi_sources", "capture_cards", "camera_switching", "media_playback"],
        avoid_for=["extreme_input_counts"],  # Even Pro has practical limits
        requires_version=VMixVersion.BASIC,
        avg_setup_latency_ms=200.0,
        learning_curve_hours=2.0,
        stability_score=95
    ),
    VMixFeatureCategory.STREAMING: VMixCapability(
        feature_category=VMixFeatureCategory.STREAMING,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["rtmp_streaming", "multi_destination", "youtube_facebook_twitch", "reliable_delivery"],
        avoid_for=["extreme_bitrates", "ultra_low_latency_srt"],  # SRT supported but has edge cases
        requires_version=VMixVersion.BASIC,
        avg_setup_latency_ms=1500.0,  # Stream startup takes time
        learning_curve_hours=3.0,
        stability_score=92
    ),
    VMixFeatureCategory.RECORDING: VMixCapability(
        feature_category=VMixFeatureCategory.RECORDING,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["local_recording", "iso_recording", "multi_track_audio", "high_quality_archive"],
        avoid_for=["network_storage_only"],  # Works best with local drives
        requires_version=VMixVersion.BASIC,
        avg_setup_latency_ms=800.0,
        learning_curve_hours=1.5,
        stability_score=96
    ),
    VMixFeatureCategory.AUDIO: VMixCapability(
        feature_category=VMixFeatureCategory.AUDIO,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["mixing", "ducking", "eq", "compression", "multi_bus"],
        avoid_for=["extreme_dsp"],  # Not a DAW replacement
        requires_version=VMixVersion.BASIC,
        avg_setup_latency_ms=100.0,
        learning_curve_hours=4.0,
        stability_score=94
    ),
    VMixFeatureCategory.OVERLAYS: VMixCapability(
        feature_category=VMixFeatureCategory.OVERLAYS,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["titles", "lower_thirds", "graphics", "scoreboards", "data_driven"],
        avoid_for=["3d_graphics", "particle_effects"],  # Not a motion graphics tool
        requires_version=VMixVersion.BASIC,
        avg_setup_latency_ms=150.0,
        learning_curve_hours=3.0,
        stability_score=93
    ),
    VMixFeatureCategory.AUTOMATION: VMixCapability(
        feature_category=VMixFeatureCategory.AUTOMATION,
        bloom_pattern=BloomPattern.LATE_BLOOMER,
        best_for=["scripting", "triggers", "shortcuts", "complex_workflows", "repeatable_productions"],
        avoid_for=["real_time_ai", "predictive_automation"],  # Rule-based only
        requires_version=VMixVersion.HD,
        avg_setup_latency_ms=50.0,
        learning_curve_hours=10.0,  # Steep learning curve
        stability_score=90
    ),
    VMixFeatureCategory.ADVANCED_API: VMixCapability(
        feature_category=VMixFeatureCategory.ADVANCED_API,
        bloom_pattern=BloomPattern.LATE_BLOOMER,
        best_for=["custom_integrations", "web_controller", "external_control", "if_bus_integration"],
        avoid_for=["simple_productions"],  # Overkill for basic use
        requires_version=VMixVersion.BASIC,  # API available in all versions
        avg_setup_latency_ms=100.0,
        learning_curve_hours=20.0,  # Requires programming knowledge
        stability_score=88
    )
}


@dataclass
class VMixState:
    """Current vMix production state"""
    active_input: int
    preview_input: int
    streaming: bool
    recording: bool
    audio_levels: Dict[str, float]  # Input name → dB level
    overlays_active: List[int]
    timestamp: str


@dataclass
class VMixInput:
    """vMix input representation"""
    input_number: int
    input_type: str  # "Video", "NDI", "Camera", "Image", etc.
    title: str
    state: str  # "Running", "Paused", "Completed"
    duration: Optional[int]  # milliseconds


class VMixAdapter(ABC):
    """
    Abstract base class for all vMix adapters

    Unified interface to vMix instances (local, remote, different versions)

    Philosophy:
    - Wu Lun: Each vMix feature is a friend (朋友) with unique strengths
    - IF.talent: Apply bloom patterns to select optimal features for task
    - IF.ground: Pragmatism - judge by usefulness, not ideology
    """

    def __init__(self, instance_name: str, host: str = "localhost", port: int = 8088):
        """
        Initialize vMix adapter

        Args:
            instance_name: Human-readable name (e.g., "production-vmix-1")
            host: vMix API hostname/IP (default: localhost)
            port: vMix API port (default: 8088)
        """
        self.instance_name = instance_name
        self.host = host
        self.port = port
        self.version = VMixVersion.UNKNOWN
        self.connected = False
        self.current_state: Optional[VMixState] = None

    @abstractmethod
    def connect(self, auth_config: Optional[Dict] = None) -> bool:
        """
        Connect to vMix instance

        Args:
            auth_config: Optional authentication (for remote instances)
                {
                    "method": "basic" | "token",
                    "credentials": {...}
                }

        Returns:
            True if connected successfully
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from vMix instance

        Returns:
            True if disconnected successfully
        """
        pass

    @abstractmethod
    def switch_to_input(self, input_number: int, transition: str = "Cut") -> bool:
        """
        Switch to input (make it active/program)

        Args:
            input_number: Input number (1-based)
            transition: "Cut", "Fade", "Merge", "Wipe", "Zoom", etc.

        Returns:
            True if switch successful
        """
        pass

    @abstractmethod
    def preview_input(self, input_number: int) -> bool:
        """
        Set input to preview

        Args:
            input_number: Input number (1-based)

        Returns:
            True if preview set
        """
        pass

    @abstractmethod
    def add_input(self, input_type: str, source: str, title: Optional[str] = None) -> Tuple[bool, Optional[int]]:
        """
        Add new input to vMix

        Args:
            input_type: "Video", "NDI", "Camera", "Image", "AudioFile", etc.
            source: File path, NDI source name, or device name
            title: Optional custom title

        Returns:
            (success, input_number) tuple
        """
        pass

    @abstractmethod
    def remove_input(self, input_number: int) -> bool:
        """
        Remove input from vMix

        Args:
            input_number: Input number to remove

        Returns:
            True if removed successfully
        """
        pass

    @abstractmethod
    def start_stream(self, stream_number: int = 0) -> bool:
        """
        Start RTMP stream

        Args:
            stream_number: Stream index (0-2 for multi-streaming)

        Returns:
            True if stream started
        """
        pass

    @abstractmethod
    def stop_stream(self, stream_number: int = 0) -> bool:
        """
        Stop RTMP stream

        Args:
            stream_number: Stream index

        Returns:
            True if stream stopped
        """
        pass

    @abstractmethod
    def start_recording(self) -> bool:
        """
        Start local recording

        Returns:
            True if recording started
        """
        pass

    @abstractmethod
    def stop_recording(self) -> bool:
        """
        Stop local recording

        Returns:
            True if recording stopped
        """
        pass

    @abstractmethod
    def set_overlay(self, overlay_number: int, input_number: int, visible: bool = True) -> bool:
        """
        Set overlay input

        Args:
            overlay_number: Overlay slot (1-4)
            input_number: Input to use as overlay
            visible: Show or hide overlay

        Returns:
            True if overlay set
        """
        pass

    @abstractmethod
    def set_audio_level(self, input_identifier: str, volume: float, fade_duration_ms: int = 0) -> bool:
        """
        Set audio volume for input

        Args:
            input_identifier: Input number or name
            volume: Volume level (0.0 to 1.0)
            fade_duration_ms: Fade duration in milliseconds

        Returns:
            True if audio set
        """
        pass

    @abstractmethod
    def get_state(self) -> VMixState:
        """
        Get current vMix state

        Returns:
            VMixState with current production state
        """
        pass

    @abstractmethod
    def get_inputs(self) -> List[VMixInput]:
        """
        List all inputs

        Returns:
            List of VMixInput objects
        """
        pass

    @abstractmethod
    def execute_function(self, function_name: str, **kwargs) -> bool:
        """
        Execute arbitrary vMix function (for advanced use)

        Args:
            function_name: vMix function name (e.g., "SetText", "StartStopMultiCorder")
            **kwargs: Function parameters

        Returns:
            True if function executed
        """
        pass

    # Common utilities (implemented in base class)

    def detect_version(self) -> VMixVersion:
        """
        Auto-detect vMix version from API response

        Strategy:
        1. Query vMix API endpoint
        2. Parse version string from XML
        3. Map to VMixVersion enum

        Returns:
            Detected vMix version
        """
        # Mock implementation (real version would query API)
        # Real: GET http://localhost:8088/api -> parse <vmix><version>24.0.0.65</version>
        return VMixVersion.UNKNOWN

    def get_capability_profile(self, feature: VMixFeatureCategory) -> Optional[VMixCapability]:
        """
        Get capability profile for vMix feature

        Returns bloom pattern and performance characteristics

        Args:
            feature: Feature category to query

        Returns:
            VMixCapability or None if feature not supported
        """
        return VMIX_FEATURE_CAPABILITIES.get(feature)

    def is_suitable_for(self, use_case: str, feature: VMixFeatureCategory) -> Tuple[bool, str]:
        """
        Check if vMix feature is suitable for a use case

        Applies IF.talent bloom pattern logic

        Args:
            use_case: Use case string (e.g., "rtmp_streaming")
            feature: Feature category to check

        Returns:
            (suitable, reasoning) tuple
        """
        capability = self.get_capability_profile(feature)

        if not capability:
            return False, f"Feature {feature.value} not found"

        if use_case in capability.best_for:
            return True, f"{feature.value} excels at {use_case} ({capability.bloom_pattern.value})"

        if use_case in capability.avoid_for:
            return False, f"{feature.value} struggles with {use_case}"

        return True, f"{feature.value} can handle {use_case} (neutral)"

    def estimate_learning_time(self, features: List[VMixFeatureCategory]) -> float:
        """
        Estimate time to learn multiple vMix features

        Args:
            features: List of feature categories

        Returns:
            Estimated learning time in hours
        """
        total_hours = 0.0
        for feature in features:
            capability = self.get_capability_profile(feature)
            if capability:
                total_hours += capability.learning_curve_hours

        return total_hours

    def log_operation(self, operation: str, params: Dict, witness_enabled: bool = True) -> str:
        """
        Log operation with IF.witness integration

        Args:
            operation: Operation name
            params: Operation parameters
            witness_enabled: Enable IF.witness logging

        Returns:
            Operation log ID
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "instance": self.instance_name,
            "operation": operation,
            "params": params,
            "version": self.version.value
        }

        # IF.witness integration (when available)
        if witness_enabled:
            # Real: import infrafabric.witness as witness
            # witness.log_event("vmix_operation", log_entry)
            pass

        log_id = f"vmix-op-{datetime.utcnow().timestamp()}"
        return log_id

    def to_dict(self) -> Dict:
        """Export adapter configuration"""
        return {
            "instance_name": self.instance_name,
            "host": self.host,
            "port": self.port,
            "version": self.version.value,
            "connected": self.connected
        }


# Example concrete adapter (HTTP API)
class VMixHTTPAdapter(VMixAdapter):
    """vMix HTTP API implementation (most common)"""

    def __init__(self, instance_name: str, host: str = "localhost", port: int = 8088):
        super().__init__(instance_name, host, port)
        self.api_base = f"http://{host}:{port}/api"

    def connect(self, auth_config: Optional[Dict] = None) -> bool:
        # Test connection with API call
        # Real: requests.get(self.api_base)
        self.connected = True
        self.version = self.detect_version()
        return True

    def disconnect(self) -> bool:
        self.connected = False
        return True

    def switch_to_input(self, input_number: int, transition: str = "Cut") -> bool:
        # Real: requests.get(f"{self.api_base}/?Function={transition}&Input={input_number}")
        self.log_operation("switch_to_input", {"input": input_number, "transition": transition})
        return True

    def preview_input(self, input_number: int) -> bool:
        # Real: requests.get(f"{self.api_base}/?Function=PreviewInput&Input={input_number}")
        self.log_operation("preview_input", {"input": input_number})
        return True

    def add_input(self, input_type: str, source: str, title: Optional[str] = None) -> Tuple[bool, Optional[int]]:
        # Real: requests.get(f"{self.api_base}/?Function=AddInput&Value={source}")
        input_number = 1  # Mock
        self.log_operation("add_input", {"type": input_type, "source": source, "title": title})
        return True, input_number

    def remove_input(self, input_number: int) -> bool:
        # Real: requests.get(f"{self.api_base}/?Function=RemoveInput&Input={input_number}")
        self.log_operation("remove_input", {"input": input_number})
        return True

    def start_stream(self, stream_number: int = 0) -> bool:
        # Real: requests.get(f"{self.api_base}/?Function=StartStreaming&Value={stream_number}")
        self.log_operation("start_stream", {"stream_number": stream_number})
        return True

    def stop_stream(self, stream_number: int = 0) -> bool:
        # Real: requests.get(f"{self.api_base}/?Function=StopStreaming&Value={stream_number}")
        self.log_operation("stop_stream", {"stream_number": stream_number})
        return True

    def start_recording(self) -> bool:
        # Real: requests.get(f"{self.api_base}/?Function=StartRecording")
        self.log_operation("start_recording", {})
        return True

    def stop_recording(self) -> bool:
        # Real: requests.get(f"{self.api_base}/?Function=StopRecording")
        self.log_operation("stop_recording", {})
        return True

    def set_overlay(self, overlay_number: int, input_number: int, visible: bool = True) -> bool:
        function = "OverlayInput" + str(overlay_number) + ("In" if visible else "Out")
        # Real: requests.get(f"{self.api_base}/?Function={function}&Input={input_number}")
        self.log_operation("set_overlay", {"overlay": overlay_number, "input": input_number, "visible": visible})
        return True

    def set_audio_level(self, input_identifier: str, volume: float, fade_duration_ms: int = 0) -> bool:
        # Real: requests.get(f"{self.api_base}/?Function=SetVolume&Input={input_identifier}&Value={int(volume*100)}")
        self.log_operation("set_audio_level", {"input": input_identifier, "volume": volume, "fade": fade_duration_ms})
        return True

    def get_state(self) -> VMixState:
        # Real: requests.get(f"{self.api_base}/"), parse XML
        return VMixState(
            active_input=1,
            preview_input=2,
            streaming=False,
            recording=False,
            audio_levels={},
            overlays_active=[],
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )

    def get_inputs(self) -> List[VMixInput]:
        # Real: Parse XML from API, extract <input> elements
        return []

    def execute_function(self, function_name: str, **kwargs) -> bool:
        # Real: requests.get(f"{self.api_base}/?Function={function_name}&{urlencode(kwargs)}")
        self.log_operation("execute_function", {"function": function_name, "params": kwargs})
        return True


# CLI usage example
if __name__ == "__main__":
    # Example: Connect to local vMix instance
    vmix = VMixHTTPAdapter("production-vmix", "localhost", 8088)

    # Connect
    vmix.connect()
    print(f"Connected to vMix {vmix.version.value}")

    # Check feature capabilities
    streaming_cap = vmix.get_capability_profile(VMixFeatureCategory.STREAMING)
    print(f"\nStreaming Feature:")
    print(f"  Bloom: {streaming_cap.bloom_pattern.value}")
    print(f"  Best for: {', '.join(streaming_cap.best_for)}")
    print(f"  Learning curve: {streaming_cap.learning_curve_hours}h")

    # Check suitability
    suitable, reason = vmix.is_suitable_for("rtmp_streaming", VMixFeatureCategory.STREAMING)
    print(f"\nSuitable for RTMP streaming: {suitable} - {reason}")

    suitable, reason = vmix.is_suitable_for("extreme_bitrates", VMixFeatureCategory.STREAMING)
    print(f"Suitable for extreme bitrates: {suitable} - {reason}")

    # Estimate learning time for full production workflow
    workflow_features = [
        VMixFeatureCategory.BASIC_SWITCHING,
        VMixFeatureCategory.STREAMING,
        VMixFeatureCategory.AUDIO,
        VMixFeatureCategory.OVERLAYS
    ]
    learning_time = vmix.estimate_learning_time(workflow_features)
    print(f"\nEstimated learning time for production workflow: {learning_time}h")

    # Example operations
    print(f"\n--- Example Production Workflow ---")
    vmix.add_input("NDI", "LAPTOP-CAM-1 (OBS)", "Camera 1")
    vmix.add_input("Video", "C:/Videos/intro.mp4", "Intro Video")
    vmix.switch_to_input(1, "Fade")
    vmix.preview_input(2)
    vmix.set_overlay(1, 3, visible=True)  # Lower third
    vmix.start_stream(0)
    print("Production started!")
