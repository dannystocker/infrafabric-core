"""
IF.integrations Home Assistant Adapter Base Class - Unified Interface to Home Assistant Instances

Applies IF.talent pattern: Abstract interface with bloom pattern detection

Home Assistant Domain Bloom Patterns:
- Early bloomer: Lights, switches, sensors (simple on/off control)
- Steady performer: Cameras, media players, automations (reliable core features)
- Late bloomer: Advanced automations, custom integrations, Node-RED

Philosophy Grounding:
- IF.ground:principle_1 (Open Source First): Home Assistant is open-source champion
- IF.ground:principle_4 (Underdetermination): Multiple home automation platforms exist
- IF.ground:principle_6 (Pragmatism): Judge by usefulness (bloom patterns matter)
- IF.ground:principle_8 (Stoic Prudence): Physical infrastructure control requires reliability
- Wu Lun: HA domains as friends (朋友) - each with unique strengths

Author: Session 6 (IF.talent)
Date: 2025-11-12
Citation: if://component/integrations/home-assistant-adapter-base-v1
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json


class HAVersion(Enum):
    """Home Assistant versions"""
    HA_2022 = "2022"  # Older
    HA_2023 = "2023"  # Stable
    HA_2024 = "2024"  # Current
    HAOS = "haos"  # Home Assistant OS
    SUPERVISED = "supervised"  # Supervised install
    CONTAINER = "container"  # Docker container
    CORE = "core"  # Core only
    UNKNOWN = "unknown"


class BloomPattern(Enum):
    """Bloom pattern classification (from IF.talent)"""
    EARLY_BLOOMER = "early_bloomer"  # Simple tasks easy, complex hard
    STEADY_PERFORMER = "steady_performer"  # Consistent across all scenarios
    LATE_BLOOMER = "late_bloomer"  # Excels at high-scale/complex scenarios


class HADomain(Enum):
    """Home Assistant domain categories"""
    LIGHTS = "light"  # Light control
    SWITCHES = "switch"  # Switch control
    SENSORS = "sensor"  # Sensor monitoring
    CAMERAS = "camera"  # Camera integration
    MEDIA_PLAYERS = "media_player"  # Media playback
    CLIMATE = "climate"  # HVAC control
    COVERS = "cover"  # Blinds, garage doors
    LOCKS = "lock"  # Lock control
    AUTOMATIONS = "automation"  # Automation rules
    SCRIPTS = "script"  # Script execution
    SCENES = "scene"  # Scene activation
    NOTIFICATIONS = "notify"  # Notification services
    TTS = "tts"  # Text-to-speech
    WEBHOOKS = "webhook"  # Webhook triggers
    CUSTOM_INTEGRATIONS = "custom"  # Custom components


@dataclass
class HACapability:
    """
    Capability profile for Home Assistant domain (IF.talent pattern)

    Similar to VMixCapability/OBSCapability, but for HA domains
    """
    domain: HADomain
    bloom_pattern: BloomPattern
    best_for: List[str]  # Use cases where it excels
    avoid_for: List[str]  # Use cases where it struggles
    requires_version: HAVersion  # Minimum HA version needed
    avg_response_latency_ms: float  # API response time
    learning_curve_hours: float  # Time to master domain
    stability_score: int  # 1-100 (100 = rock solid)
    physical_safety_critical: bool  # Physical infrastructure risk
    cost: float  # Cost in USD (HA is free, but devices cost money)


# Capability profiles for each Home Assistant domain
HA_DOMAIN_CAPABILITIES = {
    HADomain.LIGHTS: HACapability(
        domain=HADomain.LIGHTS,
        bloom_pattern=BloomPattern.EARLY_BLOOMER,
        best_for=["on_off_control", "brightness", "color", "simple_automation"],
        avoid_for=["complex_light_shows", "dmx_control"],
        requires_version=HAVersion.HA_2022,
        avg_response_latency_ms=100.0,
        learning_curve_hours=0.5,
        stability_score=98,
        physical_safety_critical=False,
        cost=0.0  # HA free, lights vary
    ),
    HADomain.SWITCHES: HACapability(
        domain=HADomain.SWITCHES,
        bloom_pattern=BloomPattern.EARLY_BLOOMER,
        best_for=["on_off_control", "simple_devices", "power_monitoring"],
        avoid_for=["complex_state_machines"],
        requires_version=HAVersion.HA_2022,
        avg_response_latency_ms=80.0,
        learning_curve_hours=0.25,
        stability_score=99,
        physical_safety_critical=False,
        cost=0.0
    ),
    HADomain.SENSORS: HACapability(
        domain=HADomain.SENSORS,
        bloom_pattern=BloomPattern.EARLY_BLOOMER,
        best_for=["temperature", "humidity", "motion", "door_contact"],
        avoid_for=["high_frequency_data", "industrial_sensors"],
        requires_version=HAVersion.HA_2022,
        avg_response_latency_ms=200.0,
        learning_curve_hours=1.0,
        stability_score=97,
        physical_safety_critical=False,
        cost=0.0
    ),
    HADomain.CAMERAS: HACapability(
        domain=HADomain.CAMERAS,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["rtsp_streams", "motion_detection", "snapshots", "ndi_bridge"],
        avoid_for=["professional_video_production"],  # Use vMix/OBS for that
        requires_version=HAVersion.HA_2022,
        avg_response_latency_ms=500.0,
        learning_curve_hours=2.0,
        stability_score=93,
        physical_safety_critical=False,
        cost=0.0
    ),
    HADomain.MEDIA_PLAYERS: HACapability(
        domain=HADomain.MEDIA_PLAYERS,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["music_playback", "video_playback", "volume_control", "announcements"],
        avoid_for=["professional_audio_mixing"],  # Use vMix/OBS for that
        requires_version=HAVersion.HA_2022,
        avg_response_latency_ms=300.0,
        learning_curve_hours=1.5,
        stability_score=94,
        physical_safety_critical=False,
        cost=0.0
    ),
    HADomain.CLIMATE: HACapability(
        domain=HADomain.CLIMATE,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["hvac_control", "temperature_regulation", "energy_saving"],
        avoid_for=["industrial_hvac"],
        requires_version=HAVersion.HA_2022,
        avg_response_latency_ms=400.0,
        learning_curve_hours=3.0,
        stability_score=95,
        physical_safety_critical=True,  # HVAC affects physical comfort
        cost=0.0
    ),
    HADomain.LOCKS: HACapability(
        domain=HADomain.LOCKS,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["door_locks", "access_control", "security"],
        avoid_for=["high_security_facilities"],  # Physical locks preferred
        requires_version=HAVersion.HA_2022,
        avg_response_latency_ms=600.0,
        learning_curve_hours=2.5,
        stability_score=96,
        physical_safety_critical=True,  # Security critical!
        cost=0.0
    ),
    HADomain.AUTOMATIONS: HACapability(
        domain=HADomain.AUTOMATIONS,
        bloom_pattern=BloomPattern.LATE_BLOOMER,
        best_for=["complex_workflows", "conditional_logic", "state_machines"],
        avoid_for=["simple_on_off"],  # Overkill for simple tasks
        requires_version=HAVersion.HA_2022,
        avg_response_latency_ms=150.0,
        learning_curve_hours=10.0,  # YAML + concepts
        stability_score=92,
        physical_safety_critical=True,  # Can control safety-critical devices
        cost=0.0
    ),
    HADomain.SCRIPTS: HACapability(
        domain=HADomain.SCRIPTS,
        bloom_pattern=BloomPattern.LATE_BLOOMER,
        best_for=["reusable_sequences", "complex_actions", "parameterized_workflows"],
        avoid_for=["simple_scenes"],
        requires_version=HAVersion.HA_2022,
        avg_response_latency_ms=100.0,
        learning_curve_hours=8.0,
        stability_score=93,
        physical_safety_critical=True,
        cost=0.0
    ),
    HADomain.TTS: HACapability(
        domain=HADomain.TTS,
        bloom_pattern=BloomPattern.STEADY_PERFORMER,
        best_for=["announcements", "alerts", "accessibility"],
        avoid_for=["professional_voice_over"],
        requires_version=HAVersion.HA_2022,
        avg_response_latency_ms=800.0,
        learning_curve_hours=1.0,
        stability_score=91,
        physical_safety_critical=False,
        cost=0.0
    ),
    HADomain.WEBHOOKS: HACapability(
        domain=HADomain.WEBHOOKS,
        bloom_pattern=BloomPattern.LATE_BLOOMER,
        best_for=["external_integrations", "if_bus_triggers", "custom_events"],
        avoid_for=["simple_automations"],
        requires_version=HAVersion.HA_2023,
        avg_response_latency_ms=200.0,
        learning_curve_hours=12.0,  # HTTP + security concepts
        stability_score=90,
        physical_safety_critical=False,
        cost=0.0
    ),
    HADomain.CUSTOM_INTEGRATIONS: HACapability(
        domain=HADomain.CUSTOM_INTEGRATIONS,
        bloom_pattern=BloomPattern.LATE_BLOOMER,
        best_for=["custom_devices", "proprietary_protocols", "advanced_features"],
        avoid_for=["beginners"],
        requires_version=HAVersion.HA_2022,
        avg_response_latency_ms=300.0,
        learning_curve_hours=20.0,  # Python + HA architecture
        stability_score=85,  # Custom code varies
        physical_safety_critical=True,  # Can control any device
        cost=0.0
    )
}


@dataclass
class HAEntityState:
    """Home Assistant entity state"""
    entity_id: str  # e.g., "light.living_room"
    state: str  # e.g., "on", "off", "unavailable"
    attributes: Dict[str, Any]
    last_changed: str
    last_updated: str


@dataclass
class HAService:
    """Home Assistant service"""
    domain: str
    service: str
    service_data: Dict[str, Any]


class HomeAssistantAdapter(ABC):
    """
    Abstract base class for all Home Assistant adapters

    Unified interface to Home Assistant instances (local, remote, different versions)

    Philosophy:
    - Wu Lun: Each HA domain is a friend (朋友) with unique strengths
    - IF.talent: Apply bloom patterns to select optimal domains for task
    - IF.ground:principle_1: Open source first - HA is free, community-driven
    - IF.ground:principle_8: Stoic prudence - physical infrastructure control requires reliability
    """

    def __init__(self, host: str = "homeassistant.local", port: int = 8123, token: Optional[str] = None):
        """
        Initialize Home Assistant adapter

        Args:
            host: Home Assistant hostname/IP (default: homeassistant.local)
            port: Home Assistant port (default: 8123)
            token: Long-lived access token (required for auth)
        """
        self.host = host
        self.port = port
        self.token = token
        self.version = HAVersion.UNKNOWN
        self.connected = False
        self.api_base = f"http://{host}:{port}/api"

    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to Home Assistant REST API

        Returns:
            True if connected successfully
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from Home Assistant

        Returns:
            True if disconnected successfully
        """
        pass

    @abstractmethod
    def get_version(self) -> Dict:
        """
        Get Home Assistant version information

        Returns:
            {"version": "2024.11.0", "installation_type": "Home Assistant Container"}
        """
        pass

    # Entity State Management

    @abstractmethod
    def get_state(self, entity_id: str) -> HAEntityState:
        """
        Get entity state

        Args:
            entity_id: Entity ID (e.g., "light.living_room")

        Returns:
            HAEntityState with current state
        """
        pass

    @abstractmethod
    def get_states(self, domain: Optional[str] = None) -> List[HAEntityState]:
        """
        Get all entity states (optionally filtered by domain)

        Args:
            domain: Optional domain filter (e.g., "light")

        Returns:
            List of HAEntityState objects
        """
        pass

    # Service Calls

    @abstractmethod
    def call_service(
        self,
        domain: str,
        service: str,
        service_data: Optional[Dict] = None,
        target: Optional[Dict] = None
    ) -> bool:
        """
        Call Home Assistant service

        Args:
            domain: Domain (e.g., "light")
            service: Service name (e.g., "turn_on")
            service_data: Service-specific data (e.g., {"brightness": 255})
            target: Target entities (e.g., {"entity_id": "light.living_room"})

        Returns:
            True if service called successfully
        """
        pass

    # Convenience Methods (Domain-Specific)

    @abstractmethod
    def turn_on_light(self, entity_id: str, brightness: Optional[int] = None, color: Optional[str] = None) -> bool:
        """
        Turn on light with optional brightness/color

        Args:
            entity_id: Light entity ID
            brightness: Brightness (0-255)
            color: Color name or hex

        Returns:
            True if light turned on
        """
        pass

    @abstractmethod
    def turn_off_light(self, entity_id: str) -> bool:
        """
        Turn off light

        Args:
            entity_id: Light entity ID

        Returns:
            True if light turned off
        """
        pass

    @abstractmethod
    def turn_on_switch(self, entity_id: str) -> bool:
        """
        Turn on switch

        Args:
            entity_id: Switch entity ID

        Returns:
            True if switch turned on
        """
        pass

    @abstractmethod
    def turn_off_switch(self, entity_id: str) -> bool:
        """
        Turn off switch

        Args:
            entity_id: Switch entity ID

        Returns:
            True if switch turned off
        """
        pass

    @abstractmethod
    def get_camera_snapshot(self, entity_id: str) -> bytes:
        """
        Get camera snapshot (JPEG)

        Args:
            entity_id: Camera entity ID

        Returns:
            JPEG image bytes
        """
        pass

    @abstractmethod
    def media_player_play(self, entity_id: str) -> bool:
        """
        Play media player

        Args:
            entity_id: Media player entity ID

        Returns:
            True if playing
        """
        pass

    @abstractmethod
    def media_player_pause(self, entity_id: str) -> bool:
        """
        Pause media player

        Args:
            entity_id: Media player entity ID

        Returns:
            True if paused
        """
        pass

    @abstractmethod
    def speak_tts(self, message: str, entity_id: Optional[str] = None) -> bool:
        """
        Speak text via TTS

        Args:
            message: Text to speak
            entity_id: Optional TTS entity ID

        Returns:
            True if TTS triggered
        """
        pass

    @abstractmethod
    def trigger_automation(self, entity_id: str) -> bool:
        """
        Trigger automation manually

        Args:
            entity_id: Automation entity ID

        Returns:
            True if automation triggered
        """
        pass

    @abstractmethod
    def execute_script(self, entity_id: str, variables: Optional[Dict] = None) -> bool:
        """
        Execute script with optional variables

        Args:
            entity_id: Script entity ID
            variables: Script variables

        Returns:
            True if script executed
        """
        pass

    @abstractmethod
    def activate_scene(self, entity_id: str) -> bool:
        """
        Activate scene

        Args:
            entity_id: Scene entity ID

        Returns:
            True if scene activated
        """
        pass

    # Common utilities (implemented in base class)

    def detect_version(self) -> HAVersion:
        """
        Determine Home Assistant version and installation type

        Returns:
            HAVersion enum
        """
        # Real implementation would call get_version() and parse
        return HAVersion.UNKNOWN

    def get_capability_profile(self, domain: HADomain) -> Optional[HACapability]:
        """
        Get capability profile for Home Assistant domain

        Returns bloom pattern and performance characteristics

        Args:
            domain: Domain to query

        Returns:
            HACapability or None if domain not supported
        """
        return HA_DOMAIN_CAPABILITIES.get(domain)

    def is_suitable_for(self, use_case: str, domain: HADomain) -> Tuple[bool, str]:
        """
        Check if Home Assistant domain is suitable for a use case

        Applies IF.talent bloom pattern logic

        Args:
            use_case: Use case string (e.g., "on_off_control")
            domain: Domain to check

        Returns:
            (suitable, reasoning) tuple
        """
        capability = self.get_capability_profile(domain)

        if not capability:
            return False, f"Domain {domain.value} not found"

        if use_case in capability.best_for:
            return True, f"{domain.value} excels at {use_case} ({capability.bloom_pattern.value})"

        if use_case in capability.avoid_for:
            return False, f"{domain.value} struggles with {use_case}"

        return True, f"{domain.value} can handle {use_case} (neutral)"

    def is_safety_critical(self, domain: HADomain) -> bool:
        """
        Check if domain controls safety-critical infrastructure

        Args:
            domain: Domain to check

        Returns:
            True if safety-critical (locks, climate, etc.)
        """
        capability = self.get_capability_profile(domain)
        if not capability:
            return False
        return capability.physical_safety_critical

    def estimate_learning_time(self, domains: List[HADomain]) -> float:
        """
        Estimate time to learn multiple Home Assistant domains

        Args:
            domains: List of domains

        Returns:
            Estimated learning time in hours
        """
        total_hours = 0.0
        for domain in domains:
            capability = self.get_capability_profile(domain)
            if capability:
                total_hours += capability.learning_curve_hours

        return total_hours

    def calculate_cost_advantage(self) -> Dict:
        """
        Calculate Home Assistant cost advantage vs commercial alternatives

        Returns:
            Cost comparison analysis
        """
        # HA is free, commercial alternatives (Control4, Crestron) cost $1000-$10000+
        control4_cost = 5000.0  # Approximate
        ha_cost = 0.0

        return {
            "ha_cost_usd": ha_cost,
            "commercial_alternative_cost_usd": control4_cost,
            "savings_usd": control4_cost - ha_cost,
            "open_source": True,
            "community_integrations": "Free",
            "philosophy": "IF.ground:principle_1 (Open Source First)"
        }

    def log_operation(self, operation: str, params: Dict, witness_enabled: bool = True) -> str:
        """
        Log operation with IF.witness integration

        CRITICAL: Physical infrastructure operations must be logged for safety

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
            "version": self.version.value,
            "safety_critical": self.is_safety_critical(params.get("domain", "unknown"))
        }

        # IF.witness integration (CRITICAL for physical infrastructure)
        if witness_enabled:
            # Real: import infrafabric.witness as witness
            # witness.log_event("ha_operation", log_entry)
            pass

        log_id = f"ha-op-{datetime.utcnow().timestamp()}"
        return log_id

    def to_dict(self) -> Dict:
        """Export adapter configuration"""
        return {
            "host": self.host,
            "port": self.port,
            "version": self.version.value,
            "connected": self.connected,
            "api_type": "REST + WebSocket"
        }


# Example concrete adapter (REST API)
class HomeAssistantRESTAdapter(HomeAssistantAdapter):
    """Home Assistant REST API implementation"""

    def __init__(self, host: str = "homeassistant.local", port: int = 8123, token: Optional[str] = None):
        super().__init__(host, port, token)
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def connect(self) -> bool:
        # Real: import requests
        # response = requests.get(f"{self.api_base}/", headers=self.headers)
        # response.raise_for_status()
        self.connected = True
        self.version = self.detect_version()
        return True

    def disconnect(self) -> bool:
        self.connected = False
        return True

    def get_version(self) -> Dict:
        # Real: requests.get(f"{self.api_base}/config", headers=self.headers).json()
        return {
            "version": "2024.11.0",
            "installation_type": "Home Assistant Container"
        }

    def get_state(self, entity_id: str) -> HAEntityState:
        # Real: requests.get(f"{self.api_base}/states/{entity_id}", headers=self.headers).json()
        return HAEntityState(
            entity_id=entity_id,
            state="on",
            attributes={},
            last_changed=datetime.utcnow().isoformat() + 'Z',
            last_updated=datetime.utcnow().isoformat() + 'Z'
        )

    def get_states(self, domain: Optional[str] = None) -> List[HAEntityState]:
        # Real: requests.get(f"{self.api_base}/states", headers=self.headers).json()
        # Filter by domain if specified
        return []

    def call_service(self, domain: str, service: str, service_data: Optional[Dict] = None, target: Optional[Dict] = None) -> bool:
        # Real: requests.post(f"{self.api_base}/services/{domain}/{service}", json={"entity_id": target, **service_data}, headers=self.headers)
        self.log_operation("call_service", {"domain": domain, "service": service, "data": service_data})
        return True

    def turn_on_light(self, entity_id: str, brightness: Optional[int] = None, color: Optional[str] = None) -> bool:
        service_data = {}
        if brightness is not None:
            service_data["brightness"] = brightness
        if color is not None:
            service_data["color_name"] = color

        return self.call_service("light", "turn_on", service_data, {"entity_id": entity_id})

    def turn_off_light(self, entity_id: str) -> bool:
        return self.call_service("light", "turn_off", target={"entity_id": entity_id})

    def turn_on_switch(self, entity_id: str) -> bool:
        return self.call_service("switch", "turn_on", target={"entity_id": entity_id})

    def turn_off_switch(self, entity_id: str) -> bool:
        return self.call_service("switch", "turn_off", target={"entity_id": entity_id})

    def get_camera_snapshot(self, entity_id: str) -> bytes:
        # Real: requests.get(f"{self.api_base}/camera_proxy/{entity_id}", headers=self.headers).content
        return b""

    def media_player_play(self, entity_id: str) -> bool:
        return self.call_service("media_player", "media_play", target={"entity_id": entity_id})

    def media_player_pause(self, entity_id: str) -> bool:
        return self.call_service("media_player", "media_pause", target={"entity_id": entity_id})

    def speak_tts(self, message: str, entity_id: Optional[str] = None) -> bool:
        return self.call_service("tts", "speak", {"message": message}, target={"entity_id": entity_id} if entity_id else None)

    def trigger_automation(self, entity_id: str) -> bool:
        return self.call_service("automation", "trigger", target={"entity_id": entity_id})

    def execute_script(self, entity_id: str, variables: Optional[Dict] = None) -> bool:
        return self.call_service("script", entity_id.split(".")[1], variables or {})

    def activate_scene(self, entity_id: str) -> bool:
        return self.call_service("scene", "turn_on", target={"entity_id": entity_id})


# CLI usage example
if __name__ == "__main__":
    # Example: Connect to local Home Assistant instance
    ha = HomeAssistantRESTAdapter("homeassistant.local", 8123, "your_long_lived_token_here")

    # Connect
    ha.connect()
    print(f"Connected to Home Assistant {ha.version.value}")

    # Check domain capabilities
    lights_cap = ha.get_capability_profile(HADomain.LIGHTS)
    print(f"\nLights Domain:")
    print(f"  Bloom: {lights_cap.bloom_pattern.value}")
    print(f"  Best for: {', '.join(lights_cap.best_for)}")
    print(f"  Learning curve: {lights_cap.learning_curve_hours}h")
    print(f"  Safety critical: {lights_cap.physical_safety_critical}")

    # Check suitability
    suitable, reason = ha.is_suitable_for("on_off_control", HADomain.LIGHTS)
    print(f"\nSuitable for on/off control: {suitable} - {reason}")

    # Safety check
    is_critical = ha.is_safety_critical(HADomain.LOCKS)
    print(f"\nLocks safety critical: {is_critical}")

    # Estimate learning time for home automation workflow
    workflow_domains = [
        HADomain.LIGHTS,
        HADomain.SWITCHES,
        HADomain.SENSORS,
        HADomain.AUTOMATIONS
    ]
    learning_time = ha.estimate_learning_time(workflow_domains)
    print(f"\nEstimated learning time for home automation: {learning_time}h")

    # Cost advantage
    cost_analysis = ha.calculate_cost_advantage()
    print(f"\nCost Advantage Analysis:")
    print(f"  Home Assistant: ${cost_analysis['ha_cost_usd']}")
    print(f"  Commercial (Control4): ${cost_analysis['commercial_alternative_cost_usd']}")
    print(f"  Savings: ${cost_analysis['savings_usd']}")

    # Example operations
    print(f"\n--- Example Smart Home Workflow ---")
    ha.turn_on_light("light.living_room", brightness=200, color="warm_white")
    ha.turn_on_switch("switch.coffee_maker")
    ha.speak_tts("Good morning! Coffee is brewing.")
    ha.activate_scene("scene.morning_routine")
    print("Morning routine activated!")

    ha.disconnect()
