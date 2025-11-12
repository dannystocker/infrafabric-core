"""
IF.integrations OBS Adapter Base Class - Unified Interface to OBS Instances

Applies IF.talent pattern: Abstract interface with bloom pattern detection

OBS Feature Bloom Patterns:
- Early bloomer: Basic streaming, scene switching, free/open-source onboarding
- Steady performer: Source management, filters, recording (consistent API)
- Late bloomer: Custom plugins, scripting (Lua/Python), complex automations

Philosophy Grounding:
- IF.ground:principle_1 (Open Source First): OBS is open-source champion
- IF.ground:principle_4 (Underdetermination): OBS vs vMix solve same problem differently
- IF.ground:principle_6 (Pragmatism): Judge by usefulness (bloom patterns matter)
- Wu Lun: OBS features as friends (朋友) - each with unique strengths

Author: Session 6 (IF.talent)
Date: 2025-11-12
Citation: if://component/integrations/obs-adapter-base-v1
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import asyncio


class OBSVersion(Enum):
    """OBS versions and editions"""
    OBS_27 = "27"  # Legacy
    OBS_28 = "28"  # WebSocket 5.x
    OBS_29 = "29"  # Current stable
    OBS_30 = "30"  # Latest
    UNKNOWN = "unknown"


class BloomPattern(Enum):
    """Bloom pattern classification (from IF.talent)"""
    EARLY_BLOOMER = "early_bloomer"  # Simple tasks easy, complex hard
    STEADY_PERFORMER = "steady_performer"  # Consistent across all scenarios
    LATE_BLOOMER = "late_bloomer"  # Excels at high-scale/complex scenarios


class OBSFeatureCategory(Enum):
    """OBS feature categories"""
    BASIC_STREAMING = "basic_streaming"  # Stream to Twitch, YouTube, etc.
    SCENE_SWITCHING = "scene_switching"  # Scene management, transitions
    SOURCE_MANAGEMENT = "source_management"  # Add/remove sources, settings
    RECORDING = "recording"  # Local recording, formats
    FILTERS = "filters"  # Chroma key, color correction, audio filters
    VIRTUAL_CAMERA = "virtual_camera"  # Virtual webcam output
    PLUGINS = "plugins"  # NDI, browser sources, custom plugins
    SCRIPTING = "scripting"  # Lua/Python automation
    ADVANCED_WEBSOCKET = "advanced_websocket"  # Custom WebSocket integrations


@dataclass
class OBSCapability:
    """
    Capability profile for OBS feature category (IF.talent pattern)

    Similar to VMixCapability, but for OBS features
    """
    feature_category: OBSFeatureCategory
    bloom_pattern: BloomPattern
    best_for: List[str]  # Use cases where it excels
    avoid_for: List[str]  # Use cases where it struggles
    requires_version: OBSVersion  # Minimum OBS version needed
    avg_setup_latency_ms: float  # Time to execute operation
    learning_curve_hours: float  # Time to master feature
    stability_score: int  # 1-100 (100 = rock solid)
    cost: float  # Cost in USD (0 for free features)


# Capability profiles for each OBS feature category
OBS_FEATURE_CAPABILITIES = {
    OBSFeatureCategory.BASIC_STREAMING: OBSCapability(
        feature_category=OBSFeatureCategory.BASIC_STREAMING,
        bloom_pattern=BloomPattern.EARLY_BLOOMER,
        best_for=["twitch_streaming", "youtube_live", "facebook_gaming", "beginner_streaming"],
        avoid_for=["ultra_low_latency_srt", "complex_multi_destination"],
        requires_version=OBSVersion.OBS_27,
        avg_setup_latency_ms=2000.0,  # Stream startup
        learning_curve_hours=0.5,  # Very easy to start
        stability_score=96,
        cost=0.0  # Free!
    ),
    OBSFeatureCategory.SCENE_SWITCHING: OBSCapability(
        feature_category=OBSFeatureCategory.SCENE_SWITCHING,
        bloom_pattern=BloomPattern.EARLY_BLOOMER,
        best_for=["simple_scene_changes", "hotkey_switching", "stream_deck_control"],
        avoid_for=["complex_multi_layer_compositing"],
        requires_version=OBSVersion.OBS_27,
        avg_setup_latency_ms=100.0,
        learning_curve_hours=1.0,
        stability_score=98,
        cost=0.0
    ),
    OBSFeatureCategory.SOURCE_MANAGEMENT: OBSCapability(
        feature_category=OBSFeatureCategory.SOURCE_MANAGEMENT,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["window_capture", "game_capture", "media_sources", "browser_sources"],
        avoid_for=["extreme_source_counts"],  # >100 sources can lag
        requires_version=OBSVersion.OBS_27,
        avg_setup_latency_ms=300.0,
        learning_curve_hours=2.0,
        stability_score=94,
        cost=0.0
    ),
    OBSFeatureCategory.RECORDING: OBSCapability(
        feature_category=OBSFeatureCategory.RECORDING,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["local_recording", "mkv_safe_mode", "multi_track_audio", "high_quality_archive"],
        avoid_for=["network_recording"],  # Prefer local drives
        requires_version=OBSVersion.OBS_27,
        avg_setup_latency_ms=500.0,
        learning_curve_hours=1.0,
        stability_score=97,
        cost=0.0
    ),
    OBSFeatureCategory.FILTERS: OBSCapability(
        feature_category=OBSFeatureCategory.FILTERS,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["chroma_key", "color_correction", "noise_suppression", "compressor"],
        avoid_for=["extreme_real_time_effects"],  # GPU-intensive
        requires_version=OBSVersion.OBS_27,
        avg_setup_latency_ms=150.0,
        learning_curve_hours=3.0,
        stability_score=93,
        cost=0.0
    ),
    OBSFeatureCategory.VIRTUAL_CAMERA: OBSCapability(
        feature_category=OBSFeatureCategory.VIRTUAL_CAMERA,
        bloom_pattern=BloomPattern.EARLY_BLOOMER,
        best_for=["zoom_calls", "teams_meetings", "video_conferencing", "obs_to_browser"],
        avoid_for=["low_latency_gaming"],  # Has slight delay
        requires_version=OBSVersion.OBS_28,  # Virtual camera added in 28
        avg_setup_latency_ms=800.0,
        learning_curve_hours=0.25,  # Extremely simple
        stability_score=95,
        cost=0.0
    ),
    OBSFeatureCategory.PLUGINS: OBSCapability(
        feature_category=OBSFeatureCategory.PLUGINS,
        bloom_pattern=BloomPattern.LATE_BLOOMER,
        best_for=["ndi_plugin", "browser_dock", "websocket_api", "advanced_scene_switcher"],
        avoid_for=["simple_setups"],  # Overkill for basics
        requires_version=OBSVersion.OBS_27,
        avg_setup_latency_ms=200.0,
        learning_curve_hours=8.0,  # Plugin ecosystem requires research
        stability_score=88,  # Third-party plugins vary
        cost=0.0  # Most plugins free
    ),
    OBSFeatureCategory.SCRIPTING: OBSCapability(
        feature_category=OBSFeatureCategory.SCRIPTING,
        bloom_pattern=BloomPattern.LATE_BLOOMER,
        best_for=["automation", "custom_workflows", "conditional_logic", "advanced_control"],
        avoid_for=["simple_productions", "non_programmers"],
        requires_version=OBSVersion.OBS_27,
        avg_setup_latency_ms=50.0,
        learning_curve_hours=15.0,  # Requires Lua or Python knowledge
        stability_score=90,
        cost=0.0
    ),
    OBSFeatureCategory.ADVANCED_WEBSOCKET: OBSCapability(
        feature_category=OBSFeatureCategory.ADVANCED_WEBSOCKET,
        bloom_pattern=BloomPattern.LATE_BLOOMER,
        best_for=["custom_integrations", "if_bus_control", "external_automation", "api_control"],
        avoid_for=["simple_streaming"],
        requires_version=OBSVersion.OBS_28,  # WebSocket 5.x
        avg_setup_latency_ms=100.0,
        learning_curve_hours=20.0,  # Requires programming + WebSocket knowledge
        stability_score=92,
        cost=0.0
    )
}


@dataclass
class OBSStreamStatus:
    """Current OBS streaming status"""
    streaming: bool
    recording: bool
    virtual_camera: bool
    stream_duration_sec: int
    stream_bitrate_kbps: int
    fps: float
    cpu_usage: float
    output_skipped_frames: int
    output_total_frames: int


@dataclass
class OBSScene:
    """OBS scene representation"""
    scene_name: str
    scene_index: int
    is_current: bool
    sources: List[str]


@dataclass
class OBSSource:
    """OBS source representation"""
    source_name: str
    source_type: str  # "ffmpeg_source", "browser_source", "window_capture", etc.
    source_kind: str  # "input", "filter", "transition"
    source_settings: Dict[str, Any]


class OBSAdapter(ABC):
    """
    Abstract base class for all OBS adapters

    Unified interface to OBS instances (local, remote, different versions)

    Philosophy:
    - Wu Lun: Each OBS feature is a friend (朋友) with unique strengths
    - IF.talent: Apply bloom patterns to select optimal features for task
    - IF.ground:principle_1: Open source first - OBS is free, community-driven
    - IF.ground: Pragmatism - judge by usefulness, not ideology
    """

    def __init__(self, host: str = "localhost", port: int = 4455, password: Optional[str] = None):
        """
        Initialize OBS adapter

        Args:
            host: OBS WebSocket hostname/IP (default: localhost)
            port: OBS WebSocket port (default: 4455)
            password: OBS WebSocket password (optional)
        """
        self.host = host
        self.port = port
        self.password = password
        self.version = OBSVersion.UNKNOWN
        self.connected = False
        self.ws = None

    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to OBS WebSocket

        Returns:
            True if connected successfully
        """
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from OBS WebSocket

        Returns:
            True if disconnected successfully
        """
        pass

    @abstractmethod
    async def get_version(self) -> Dict:
        """
        Get OBS version information

        Returns:
            {"obs_version": "30.0.0", "obs_websocket_version": "5.3.0"}
        """
        pass

    # Scene Management

    @abstractmethod
    async def get_scene_list(self) -> List[OBSScene]:
        """
        List all scenes

        Returns:
            List of OBSScene objects
        """
        pass

    @abstractmethod
    async def get_current_scene(self) -> str:
        """
        Get current program scene name

        Returns:
            Scene name
        """
        pass

    @abstractmethod
    async def set_current_scene(self, scene_name: str) -> bool:
        """
        Switch to scene

        Args:
            scene_name: Scene to switch to

        Returns:
            True if switched successfully
        """
        pass

    @abstractmethod
    async def create_scene(self, scene_name: str) -> bool:
        """
        Create new scene

        Args:
            scene_name: Name for new scene

        Returns:
            True if created successfully
        """
        pass

    # Source Management

    @abstractmethod
    async def create_source(
        self,
        scene_name: str,
        source_name: str,
        source_kind: str,
        source_settings: Optional[Dict] = None
    ) -> bool:
        """
        Create source in scene

        Args:
            scene_name: Scene to add source to
            source_name: Name for source
            source_kind: Source type ("ffmpeg_source", "browser_source", etc.)
            source_settings: Source-specific settings

        Returns:
            True if created successfully
        """
        pass

    @abstractmethod
    async def remove_source(self, scene_name: str, source_name: str) -> bool:
        """
        Remove source from scene

        Args:
            scene_name: Scene containing source
            source_name: Source to remove

        Returns:
            True if removed successfully
        """
        pass

    @abstractmethod
    async def set_source_settings(self, source_name: str, settings: Dict) -> bool:
        """
        Update source settings

        Args:
            source_name: Source to update
            settings: New settings

        Returns:
            True if updated successfully
        """
        pass

    @abstractmethod
    async def set_source_visibility(
        self,
        scene_name: str,
        source_name: str,
        visible: bool
    ) -> bool:
        """
        Show/hide source in scene

        Args:
            scene_name: Scene containing source
            source_name: Source to show/hide
            visible: True to show, False to hide

        Returns:
            True if visibility changed
        """
        pass

    # Streaming

    @abstractmethod
    async def start_stream(self) -> bool:
        """
        Start streaming (uses configured stream settings)

        Returns:
            True if stream started
        """
        pass

    @abstractmethod
    async def stop_stream(self) -> bool:
        """
        Stop streaming

        Returns:
            True if stream stopped
        """
        pass

    @abstractmethod
    async def get_stream_status(self) -> OBSStreamStatus:
        """
        Get streaming status

        Returns:
            OBSStreamStatus with current metrics
        """
        pass

    # Recording

    @abstractmethod
    async def start_recording(self) -> bool:
        """
        Start recording

        Returns:
            True if recording started
        """
        pass

    @abstractmethod
    async def stop_recording(self) -> bool:
        """
        Stop recording

        Returns:
            True if recording stopped
        """
        pass

    @abstractmethod
    async def pause_recording(self) -> bool:
        """
        Pause recording

        Returns:
            True if recording paused
        """
        pass

    @abstractmethod
    async def resume_recording(self) -> bool:
        """
        Resume recording

        Returns:
            True if recording resumed
        """
        pass

    # Virtual Camera

    @abstractmethod
    async def start_virtual_camera(self) -> bool:
        """
        Start virtual camera

        Returns:
            True if virtual camera started
        """
        pass

    @abstractmethod
    async def stop_virtual_camera(self) -> bool:
        """
        Stop virtual camera

        Returns:
            True if virtual camera stopped
        """
        pass

    # Filters

    @abstractmethod
    async def create_source_filter(
        self,
        source_name: str,
        filter_name: str,
        filter_kind: str,
        filter_settings: Optional[Dict] = None
    ) -> bool:
        """
        Add filter to source

        Args:
            source_name: Source to add filter to
            filter_name: Name for filter
            filter_kind: Filter type ("chroma_key_filter", "color_correction_filter", etc.)
            filter_settings: Filter-specific settings

        Returns:
            True if filter created
        """
        pass

    @abstractmethod
    async def remove_source_filter(self, source_name: str, filter_name: str) -> bool:
        """
        Remove filter from source

        Args:
            source_name: Source containing filter
            filter_name: Filter to remove

        Returns:
            True if filter removed
        """
        pass

    # Stats

    @abstractmethod
    async def get_stats(self) -> Dict:
        """
        Get OBS statistics

        Returns:
            {
                "fps": float,
                "cpu_usage": float,
                "memory_usage_mb": float,
                "active_fps": float,
                "output_skipped_frames": int,
                "render_total_frames": int
            }
        """
        pass

    # Common utilities (implemented in base class)

    def detect_version(self) -> OBSVersion:
        """
        Determine OBS version from version info

        Returns:
            OBSVersion enum
        """
        # Real implementation would call get_version() and parse
        return OBSVersion.UNKNOWN

    def get_capability_profile(self, feature: OBSFeatureCategory) -> Optional[OBSCapability]:
        """
        Get capability profile for OBS feature

        Returns bloom pattern and performance characteristics

        Args:
            feature: Feature category to query

        Returns:
            OBSCapability or None if feature not supported
        """
        return OBS_FEATURE_CAPABILITIES.get(feature)

    def is_suitable_for(self, use_case: str, feature: OBSFeatureCategory) -> Tuple[bool, str]:
        """
        Check if OBS feature is suitable for a use case

        Applies IF.talent bloom pattern logic

        Args:
            use_case: Use case string (e.g., "twitch_streaming")
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

    def estimate_learning_time(self, features: List[OBSFeatureCategory]) -> float:
        """
        Estimate time to learn multiple OBS features

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

    def calculate_cost_advantage(self) -> Dict:
        """
        Calculate OBS cost advantage vs commercial alternatives

        Returns:
            Cost comparison analysis
        """
        # OBS is free, vMix Pro costs ~$1200
        vmix_pro_cost = 1200.0
        obs_cost = 0.0

        return {
            "obs_cost_usd": obs_cost,
            "vmix_pro_cost_usd": vmix_pro_cost,
            "savings_usd": vmix_pro_cost - obs_cost,
            "open_source": True,
            "community_plugins": "Free",
            "philosophy": "IF.ground:principle_1 (Open Source First)"
        }

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
            "host": self.host,
            "operation": operation,
            "params": params,
            "version": self.version.value
        }

        # IF.witness integration (when available)
        if witness_enabled:
            # Real: import infrafabric.witness as witness
            # witness.log_event("obs_operation", log_entry)
            pass

        log_id = f"obs-op-{datetime.utcnow().timestamp()}"
        return log_id

    def to_dict(self) -> Dict:
        """Export adapter configuration"""
        return {
            "host": self.host,
            "port": self.port,
            "version": self.version.value,
            "connected": self.connected,
            "websocket_protocol": "obs-websocket 5.x"
        }


# Example concrete adapter (WebSocket)
class OBSWebSocketAdapter(OBSAdapter):
    """OBS WebSocket implementation (async)"""

    def __init__(self, host: str = "localhost", port: int = 4455, password: Optional[str] = None):
        super().__init__(host, port, password)

    async def connect(self) -> bool:
        # Real: import obswebsocket
        # self.ws = obswebsocket.obsws(self.host, self.port, self.password)
        # await self.ws.connect()
        self.connected = True
        self.version = self.detect_version()
        return True

    async def disconnect(self) -> bool:
        # Real: await self.ws.disconnect()
        self.connected = False
        return True

    async def get_version(self) -> Dict:
        # Real: response = await self.ws.call(requests.GetVersion())
        return {
            "obs_version": "30.0.0",
            "obs_websocket_version": "5.3.0"
        }

    async def get_scene_list(self) -> List[OBSScene]:
        # Real: response = await self.ws.call(requests.GetSceneList())
        return []

    async def get_current_scene(self) -> str:
        # Real: response = await self.ws.call(requests.GetCurrentProgramScene())
        return "Scene 1"

    async def set_current_scene(self, scene_name: str) -> bool:
        # Real: await self.ws.call(requests.SetCurrentProgramScene(sceneName=scene_name))
        self.log_operation("set_current_scene", {"scene": scene_name})
        return True

    async def create_scene(self, scene_name: str) -> bool:
        # Real: await self.ws.call(requests.CreateScene(sceneName=scene_name))
        self.log_operation("create_scene", {"scene": scene_name})
        return True

    async def create_source(self, scene_name: str, source_name: str, source_kind: str, source_settings: Optional[Dict] = None) -> bool:
        # Real: await self.ws.call(requests.CreateInput(sceneName=scene_name, inputName=source_name, inputKind=source_kind, inputSettings=source_settings))
        self.log_operation("create_source", {"scene": scene_name, "source": source_name, "kind": source_kind})
        return True

    async def remove_source(self, scene_name: str, source_name: str) -> bool:
        self.log_operation("remove_source", {"scene": scene_name, "source": source_name})
        return True

    async def set_source_settings(self, source_name: str, settings: Dict) -> bool:
        self.log_operation("set_source_settings", {"source": source_name, "settings": settings})
        return True

    async def set_source_visibility(self, scene_name: str, source_name: str, visible: bool) -> bool:
        self.log_operation("set_source_visibility", {"scene": scene_name, "source": source_name, "visible": visible})
        return True

    async def start_stream(self) -> bool:
        # Real: await self.ws.call(requests.StartStream())
        self.log_operation("start_stream", {})
        return True

    async def stop_stream(self) -> bool:
        # Real: await self.ws.call(requests.StopStream())
        self.log_operation("stop_stream", {})
        return True

    async def get_stream_status(self) -> OBSStreamStatus:
        # Real: response = await self.ws.call(requests.GetStreamStatus())
        return OBSStreamStatus(
            streaming=False,
            recording=False,
            virtual_camera=False,
            stream_duration_sec=0,
            stream_bitrate_kbps=0,
            fps=60.0,
            cpu_usage=15.0,
            output_skipped_frames=0,
            output_total_frames=0
        )

    async def start_recording(self) -> bool:
        self.log_operation("start_recording", {})
        return True

    async def stop_recording(self) -> bool:
        self.log_operation("stop_recording", {})
        return True

    async def pause_recording(self) -> bool:
        self.log_operation("pause_recording", {})
        return True

    async def resume_recording(self) -> bool:
        self.log_operation("resume_recording", {})
        return True

    async def start_virtual_camera(self) -> bool:
        self.log_operation("start_virtual_camera", {})
        return True

    async def stop_virtual_camera(self) -> bool:
        self.log_operation("stop_virtual_camera", {})
        return True

    async def create_source_filter(self, source_name: str, filter_name: str, filter_kind: str, filter_settings: Optional[Dict] = None) -> bool:
        self.log_operation("create_source_filter", {"source": source_name, "filter": filter_name, "kind": filter_kind})
        return True

    async def remove_source_filter(self, source_name: str, filter_name: str) -> bool:
        self.log_operation("remove_source_filter", {"source": source_name, "filter": filter_name})
        return True

    async def get_stats(self) -> Dict:
        # Real: response = await self.ws.call(requests.GetStats())
        return {
            "fps": 60.0,
            "cpu_usage": 15.0,
            "memory_usage_mb": 512.0,
            "active_fps": 60.0,
            "output_skipped_frames": 0,
            "render_total_frames": 36000
        }


# CLI usage example
if __name__ == "__main__":
    async def main():
        # Example: Connect to local OBS instance
        obs = OBSWebSocketAdapter("localhost", 4455, "password123")

        # Connect
        await obs.connect()
        print(f"Connected to OBS {obs.version.value}")

        # Check feature capabilities
        streaming_cap = obs.get_capability_profile(OBSFeatureCategory.BASIC_STREAMING)
        print(f"\nBasic Streaming Feature:")
        print(f"  Bloom: {streaming_cap.bloom_pattern.value}")
        print(f"  Best for: {', '.join(streaming_cap.best_for)}")
        print(f"  Learning curve: {streaming_cap.learning_curve_hours}h")
        print(f"  Cost: ${streaming_cap.cost} (FREE!)")

        # Check suitability
        suitable, reason = obs.is_suitable_for("twitch_streaming", OBSFeatureCategory.BASIC_STREAMING)
        print(f"\nSuitable for Twitch streaming: {suitable} - {reason}")

        # Estimate learning time for full streaming workflow
        workflow_features = [
            OBSFeatureCategory.BASIC_STREAMING,
            OBSFeatureCategory.SCENE_SWITCHING,
            OBSFeatureCategory.SOURCE_MANAGEMENT,
            OBSFeatureCategory.FILTERS
        ]
        learning_time = obs.estimate_learning_time(workflow_features)
        print(f"\nEstimated learning time for streaming workflow: {learning_time}h")

        # Cost advantage
        cost_analysis = obs.calculate_cost_advantage()
        print(f"\nCost Advantage Analysis:")
        print(f"  OBS: ${cost_analysis['obs_cost_usd']}")
        print(f"  vMix Pro: ${cost_analysis['vmix_pro_cost_usd']}")
        print(f"  Savings: ${cost_analysis['savings_usd']}")
        print(f"  Philosophy: {cost_analysis['philosophy']}")

        # Example operations
        print(f"\n--- Example Streaming Workflow ---")
        await obs.create_scene("Gaming Scene")
        await obs.create_source("Gaming Scene", "Webcam", "dshow_input")
        await obs.create_source("Gaming Scene", "Game Capture", "game_capture")
        await obs.create_source_filter("Webcam", "Chroma Key", "chroma_key_filter")
        await obs.set_current_scene("Gaming Scene")
        await obs.start_stream()
        await obs.start_recording()
        await obs.start_virtual_camera()
        print("Stream started (FREE!)")

        await obs.disconnect()

    # Run async example
    asyncio.run(main())
