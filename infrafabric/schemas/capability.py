"""
IF.governor Capability Registry Schema

Defines capability types, swarm profiles, and resource policies for
intelligent task assignment and budget management.

Implements F6.12 Capability Registry Schema design.
Addresses IF Bug #2: Reduces 57% cost waste to <10% through capability matching.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Set
import json
from datetime import datetime


class Capability(Enum):
    """
    Capability taxonomy for InfraFabric swarms

    Format: DOMAIN_CATEGORY_SKILL
    Based on F6.12 domain taxonomy.
    """

    # Video Domain
    VIDEO_STREAMING_NDI = "video:streaming:ndi"
    VIDEO_STREAMING_RTSP = "video:streaming:rtsp"
    VIDEO_STREAMING_HLS = "video:streaming:hls"
    VIDEO_PRODUCTION_VMIX = "video:production:vmix"
    VIDEO_PRODUCTION_OBS = "video:production:obs"
    VIDEO_ENCODING_H264 = "video:encoding:h264"
    VIDEO_ENCODING_H265 = "video:encoding:h265"

    # Telephony Domain
    TELEPHONY_SIP_PROTOCOL = "telephony:sip:protocol"
    TELEPHONY_SIP_KAMAILIO = "telephony:sip:kamailio"
    TELEPHONY_H323_PROTOCOL = "telephony:h323:protocol"
    TELEPHONY_WEBRTC_SIGNALING = "telephony:webrtc:signaling"
    TELEPHONY_ASTERISK_PBX = "telephony:asterisk:pbx"

    # Crypto Domain
    CRYPTO_SIGNATURES_ED25519 = "crypto:signatures:ed25519"
    CRYPTO_SIGNATURES_ECDSA = "crypto:signatures:ecdsa"
    CRYPTO_HASHING_SHA256 = "crypto:hashing:sha256"
    CRYPTO_HASHING_BLAKE3 = "crypto:hashing:blake3"
    CRYPTO_WITNESS_PROVENANCE = "crypto:witness:provenance"

    # Infrastructure Domain
    INFRA_ORCHESTRATION_DOCKER = "infra:orchestration:docker"
    INFRA_ORCHESTRATION_KUBERNETES = "infra:orchestration:kubernetes"
    INFRA_NETWORKING_TCP = "infra:networking:tcp"
    INFRA_NETWORKING_UDP = "infra:networking:udp"
    INFRA_DISTRIBUTED_SYSTEMS = "infra:distributed:systems"
    INFRA_PERFORMANCE_OPTIMIZATION = "infra:performance:optimization"
    INFRA_WASM_RUNTIME = "infra:wasm:runtime"

    # Cloud Domain
    CLOUD_AWS_EC2 = "cloud:aws:ec2"
    CLOUD_AWS_S3 = "cloud:aws:s3"
    CLOUD_GCP_COMPUTE = "cloud:gcp:compute"
    CLOUD_AZURE_VM = "cloud:azure:vm"

    # Smart Home Domain
    SMART_HOME_HOME_ASSISTANT = "smart_home:home_assistant:api"
    SMART_HOME_MQTT_PROTOCOL = "smart_home:mqtt:protocol"
    SMART_HOME_ZIGBEE = "smart_home:zigbee:protocol"
    SMART_HOME_ZWAVE = "smart_home:zwave:protocol"

    # Programming Domain
    PROGRAMMING_PYTHON_ASYNC = "programming:python:async"
    PROGRAMMING_PYTHON_PACKAGING = "programming:python:packaging"
    PROGRAMMING_RUST_SYSTEMS = "programming:rust:systems"
    PROGRAMMING_RUST_WASM = "programming:rust:wasm"
    PROGRAMMING_JAVASCRIPT_NODE = "programming:javascript:node"
    PROGRAMMING_GO_CONCURRENCY = "programming:go:concurrency"

    # Documentation Domain
    DOCS_TECHNICAL_WRITING = "docs:technical_writing:general"
    DOCS_API_DESIGN = "docs:api_design:rest"
    DOCS_ARCHITECTURE_DIAGRAMS = "docs:architecture:diagrams"

    # Architecture Domain
    ARCHITECTURE_PATTERNS_MICROSERVICES = "architecture:patterns:microservices"
    ARCHITECTURE_PATTERNS_EVENT_DRIVEN = "architecture:patterns:event_driven"
    ARCHITECTURE_SECURITY_DESIGN = "architecture:security:design"
    ARCHITECTURE_PERFORMANCE = "architecture:performance:optimization"

    # Talent Domain
    TALENT_CAPABILITY_ANALYSIS = "talent:capability:analysis"
    TALENT_BLOOM_PATTERN_ANALYSIS = "talent:bloom_pattern:analysis"
    TALENT_ASSIGNMENT_SCORING = "talent:assignment:scoring"
    TALENT_REPUTATION_TRACKING = "talent:reputation:tracking"

    # Payment Domain
    PAYMENT_STRIPE_API = "payment:stripe:api"
    PAYMENT_BLOCKCHAIN_ETHEREUM = "payment:blockchain:ethereum"

    # Chat Domain
    CHAT_SLACK_BOT = "chat:slack:bot"
    CHAT_DISCORD_BOT = "chat:discord:bot"

    # AI/ML Domain
    AI_ML_LLM_ORCHESTRATION = "ai_ml:llm:orchestration"
    AI_ML_PROMPT_ENGINEERING = "ai_ml:prompt:engineering"
    AI_ML_MODEL_EVALUATION = "ai_ml:model:evaluation"

    # CLI Domain
    CLI_DESIGN = "cli:design:interface"
    CLI_TESTING = "cli:testing:automation"
    CLI_PERFORMANCE = "cli:performance:optimization"


class SkillLevel(Enum):
    """Skill proficiency levels from F6.12"""
    NOVICE = "novice"           # 0-10 tasks, <70% success rate
    INTERMEDIATE = "intermediate"  # 10-50 tasks, 70-85% success rate
    ADVANCED = "advanced"       # 50-200 tasks, 85-95% success rate
    EXPERT = "expert"           # 200+ tasks, 95%+ success rate


class BloomPattern(Enum):
    """Task complexity performance patterns from F6.3"""
    EARLY_BLOOMER = "early_bloomer"      # Excels at simple tasks
    STEADY_PERFORMER = "steady_performer"  # Consistent across complexity
    LATE_BLOOMER = "late_bloomer"        # Excels at complex tasks


@dataclass
class CapabilityProfile:
    """
    Individual capability profile within a swarm

    Based on F6.12 Capability Registry Schema
    """
    capability: Capability
    skill_level: SkillLevel
    experience_hours: float = 0.0
    success_rate: float = 0.70  # F6.11 neutral starting point
    tasks_completed: int = 0
    last_used: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'capability': self.capability.value,
            'skill_level': self.skill_level.value,
            'experience_hours': self.experience_hours,
            'success_rate': self.success_rate,
            'tasks_completed': self.tasks_completed,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }


@dataclass
class SwarmProfile:
    """
    Complete profile for a swarm/session agent

    Integrates F6.12 (capability schema) and F6.11 (reputation)
    """
    swarm_id: str
    name: str
    model: str  # "haiku", "sonnet", "opus"

    # Capabilities (F6.12)
    capabilities: List[CapabilityProfile] = field(default_factory=list)

    # Cost tracking (Bug #2 fix)
    cost_per_hour: float = 0.0  # Haiku: $1-2, Sonnet: $15-20, Opus: $75
    current_budget_remaining: float = 0.0
    total_cost_spent: float = 0.0

    # Reputation (F6.11)
    reputation_score: float = 0.70  # Neutral starting point (Acceptable tier)
    reputation_tier: str = "acceptable"  # poor/concerning/acceptable/good/excellent
    reliability_score: float = 0.70
    quality_score: float = 0.70
    speed_score: float = 0.70
    cost_efficiency_score: float = 0.70
    bloom_accuracy_score: float = 0.70

    # Bloom pattern (F6.3)
    bloom_pattern: BloomPattern = BloomPattern.STEADY_PERFORMER

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    total_tasks_completed: int = 0
    active: bool = True

    def get_capability_names(self) -> Set[Capability]:
        """Get set of all capabilities"""
        return {cp.capability for cp in self.capabilities}

    def get_capability_profile(self, capability: Capability) -> Optional[CapabilityProfile]:
        """Get specific capability profile"""
        for cp in self.capabilities:
            if cp.capability == capability:
                return cp
        return None

    def has_capability(self, capability: Capability, min_level: Optional[SkillLevel] = None) -> bool:
        """Check if swarm has capability at minimum skill level"""
        cp = self.get_capability_profile(capability)
        if not cp:
            return False

        if min_level is None:
            return True

        # Check skill level hierarchy
        level_order = [SkillLevel.NOVICE, SkillLevel.INTERMEDIATE, SkillLevel.ADVANCED, SkillLevel.EXPERT]
        return level_order.index(cp.skill_level) >= level_order.index(min_level)

    def has_budget(self, required_amount: float = 0.0) -> bool:
        """Check if swarm has sufficient budget"""
        return self.current_budget_remaining >= required_amount

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'swarm_id': self.swarm_id,
            'name': self.name,
            'model': self.model,
            'capabilities': [cp.to_dict() for cp in self.capabilities],
            'cost_per_hour': self.cost_per_hour,
            'current_budget_remaining': self.current_budget_remaining,
            'total_cost_spent': self.total_cost_spent,
            'reputation_score': self.reputation_score,
            'reputation_tier': self.reputation_tier,
            'reliability_score': self.reliability_score,
            'quality_score': self.quality_score,
            'speed_score': self.speed_score,
            'cost_efficiency_score': self.cost_efficiency_score,
            'bloom_accuracy_score': self.bloom_accuracy_score,
            'bloom_pattern': self.bloom_pattern.value,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'total_tasks_completed': self.total_tasks_completed,
            'active': self.active
        }


@dataclass
class TaskRequirements:
    """
    Task requirements for capability matching

    Used by IF.governor to find qualified swarms
    """
    task_id: str
    required_capabilities: List[Capability]
    min_skill_level: SkillLevel = SkillLevel.INTERMEDIATE
    max_cost_per_hour: float = 20.0  # Default: Sonnet budget
    preferred_bloom_pattern: Optional[BloomPattern] = None
    min_reputation: float = 0.60  # Minimum acceptable tier
    task_complexity: str = "medium"  # simple/medium/complex

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'required_capabilities': [c.value for c in self.required_capabilities],
            'min_skill_level': self.min_skill_level.value,
            'max_cost_per_hour': self.max_cost_per_hour,
            'preferred_bloom_pattern': self.preferred_bloom_pattern.value if self.preferred_bloom_pattern else None,
            'min_reputation': self.min_reputation,
            'task_complexity': self.task_complexity
        }


@dataclass
class ResourcePolicy:
    """
    Policy constraints for resource allocation

    Enforces governance rules for IF.governor
    """
    # Task assignment limits
    max_swarms_per_task: int = 3
    min_capability_match: float = 0.70  # 70% threshold from F6.3

    # Budget enforcement (Bug #2 fix)
    max_cost_per_task: float = 10.0
    enable_budget_tracking: bool = True

    # Reputation requirements (F6.11)
    min_reputation_score: float = 0.60  # Acceptable tier minimum

    # Circuit breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 3
    circuit_breaker_timeout_seconds: int = 300  # 5 minutes

    # Cost optimization
    prefer_cheaper_when_equivalent: bool = True
    cost_weight: float = 0.15  # Weight in F6.3 assignment algorithm

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


def validate_capability_manifest(manifest: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate capability manifest structure

    Args:
        manifest: Dictionary containing swarm capability manifest

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = [
        'swarm_id',
        'name',
        'model',
        'capabilities',
        'cost_per_hour'
    ]

    # Check required fields
    for field in required_fields:
        if field not in manifest:
            return False, f"Missing required field: {field}"

    # Validate swarm_id format
    if not isinstance(manifest['swarm_id'], str) or len(manifest['swarm_id']) == 0:
        return False, "swarm_id must be a non-empty string"

    # Validate model
    valid_models = ['haiku', 'sonnet', 'opus']
    if manifest['model'] not in valid_models:
        return False, f"model must be one of: {valid_models}"

    # Validate capabilities list
    if not isinstance(manifest['capabilities'], list):
        return False, "capabilities must be a list"

    # Validate each capability
    for cap in manifest['capabilities']:
        if not isinstance(cap, dict):
            return False, "Each capability must be a dictionary"

        if 'capability' not in cap:
            return False, "Each capability must have a 'capability' field"

        # Check if capability exists in enum
        try:
            Capability(cap['capability'])
        except ValueError:
            return False, f"Invalid capability: {cap['capability']}"

        # Validate skill_level if present
        if 'skill_level' in cap:
            try:
                SkillLevel(cap['skill_level'])
            except ValueError:
                return False, f"Invalid skill_level: {cap['skill_level']}"

    # Validate cost_per_hour
    if not isinstance(manifest['cost_per_hour'], (int, float)) or manifest['cost_per_hour'] < 0:
        return False, "cost_per_hour must be a non-negative number"

    # Validate budget if present
    if 'current_budget_remaining' in manifest:
        if not isinstance(manifest['current_budget_remaining'], (int, float)):
            return False, "current_budget_remaining must be a number"

    # Validate reputation_score if present
    if 'reputation_score' in manifest:
        score = manifest['reputation_score']
        if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
            return False, "reputation_score must be between 0.0 and 1.0"

    return True, None


def validate_swarm_profile(profile: SwarmProfile) -> tuple[bool, Optional[str]]:
    """
    Validate a SwarmProfile instance

    Args:
        profile: SwarmProfile to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate swarm_id
    if not profile.swarm_id or not isinstance(profile.swarm_id, str):
        return False, "swarm_id must be a non-empty string"

    # Validate name
    if not profile.name or not isinstance(profile.name, str):
        return False, "name must be a non-empty string"

    # Validate model
    if profile.model not in ['haiku', 'sonnet', 'opus']:
        return False, "model must be one of: haiku, sonnet, opus"

    # Validate capabilities
    if not isinstance(profile.capabilities, list):
        return False, "capabilities must be a list"

    for cap in profile.capabilities:
        if not isinstance(cap, CapabilityProfile):
            return False, "All capabilities must be CapabilityProfile instances"

    # Validate cost
    if profile.cost_per_hour < 0:
        return False, "cost_per_hour must be non-negative"

    # Validate reputation score range
    if not (0.0 <= profile.reputation_score <= 1.0):
        return False, "reputation_score must be between 0.0 and 1.0"

    # Validate reputation tier
    valid_tiers = ['poor', 'concerning', 'acceptable', 'good', 'excellent']
    if profile.reputation_tier not in valid_tiers:
        return False, f"reputation_tier must be one of: {valid_tiers}"

    # Validate individual reputation scores
    for score_name in ['reliability_score', 'quality_score', 'speed_score',
                       'cost_efficiency_score', 'bloom_accuracy_score']:
        score = getattr(profile, score_name)
        if not (0.0 <= score <= 1.0):
            return False, f"{score_name} must be between 0.0 and 1.0"

    return True, None


def capability_from_string(cap_string: str) -> Optional[Capability]:
    """
    Convert string to Capability enum

    Args:
        cap_string: Capability string in format "domain:category:skill"

    Returns:
        Capability enum or None if invalid
    """
    try:
        return Capability(cap_string)
    except ValueError:
        return None


def get_capabilities_by_domain(domain: str) -> List[Capability]:
    """
    Get all capabilities for a specific domain

    Args:
        domain: Domain name (e.g., "video", "telephony", "crypto")

    Returns:
        List of Capability enums matching the domain
    """
    return [
        cap for cap in Capability
        if cap.value.split(':')[0] == domain
    ]


def get_all_domains() -> List[str]:
    """
    Get list of all capability domains

    Returns:
        List of unique domain names
    """
    domains = set()
    for cap in Capability:
        domain = cap.value.split(':')[0]
        domains.add(domain)
    return sorted(list(domains))
