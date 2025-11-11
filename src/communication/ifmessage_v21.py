"""
IFMessage v2.1 Implementation (Swarp v4* Hardening)

This module implements the enhanced message schema with:
- Anti-replay protection (nonce, TTL, sequence)
- Hazard tags for policy-driven escalation
- Scope metadata for parallel workflow isolation
- Ed25519 signatures for authenticity

Author: Claude (Integration), GPT-5 Pro (Swarp v4* Design)
Date: 2025-11-11
"""

import json
import time
import hashlib
import secrets
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum


class Performative(Enum):
    """FIPA-ACL speech acts"""
    REQUEST = "request"
    INFORM = "inform"
    AGREE = "agree"
    REFUSE = "refuse"
    QUERY_IF = "query-if"
    QUERY_REF = "query-ref"
    CONTRADICT = "contradict"
    ESCALATE = "escalate"
    SHARE = "share"
    HOLD = "hold"


class HazardType(Enum):
    """Hazard categories for policy-driven escalation"""
    LEGAL = "legal"
    SAFETY = "safety"
    CONFLICT = "conflict"
    ETHICAL = "ethical"
    PRIVACY = "privacy"


class HazardSeverity(Enum):
    """Hazard severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Domain(Enum):
    """Agent domain/swarm specialization"""
    LEGAL = "legal"
    FINANCE = "finance"
    MARKETS = "markets"
    MACRO = "macro"
    TECHNICAL = "technical"
    GOVERNANCE = "governance"


@dataclass
class Scope:
    """
    Scope metadata prevents false conflicts across parallel workflows

    Example:
        Legal swarm analyzing Epic Games (mission_id="epic-v4")
        vs
        Legal swarm analyzing Microsoft (mission_id="msft-v1")

        Without scope, confidence conflicts would be flagged incorrectly
    """
    mission_id: str
    workflow: str  # "legal-findings-pass-3", "market-analysis-initial", etc.
    domain: Domain
    priority: str = "medium"  # low/medium/high/critical


@dataclass
class Hazard:
    """
    Hazard tags force escalation independent of confidence scores

    Critical Fix: v2 bug where `if confidence < 0.3 → HOLD` buried legal issues
    Solution: Check hazards BEFORE confidence thresholds

    Example:
        Message about $520M settlement has confidence=0.25 (LOW)
        Without hazard: HOLD (buried)
        With hazard: {type: "legal", severity: "high", auto_escalate: True} → ESCALATE
    """
    type: HazardType
    severity: HazardSeverity
    rationale: str
    auto_escalate: bool = False
    threshold_override: Optional[Dict[str, Any]] = None


@dataclass
class Signature:
    """Ed25519 signature for message authenticity"""
    algorithm: str  # "ed25519"
    public_key: str  # "ed25519:base64..."
    signature_bytes: str  # "ed25519:hex..."
    signed_fields: List[str]


@dataclass
class IFMessage:
    """
    InfraFabric Message v2.1 (Swarp v4* Hardening)

    Key Enhancements from v2.0:
    - nonce: 96-bit random (anti-replay beyond sequence)
    - ttl: Message expiration (seconds)
    - scope: Parallel workflow isolation
    - hazard: Policy-driven escalation
    - topic_hash: Conversation ID collision detection
    """

    # Core fields (v2.0)
    performative: Performative
    sender: str  # "if://agent/swarm/legal-1@1.2.0"
    receiver: List[str]  # ["if://agent/swarm/financial/*"]
    conversation_id: str  # "if://conversation/epic-2025-11-10-xyz"
    content: Dict[str, Any]
    timestamp: str  # ISO 8601
    sequence_num: int

    # Anti-replay (v2.1)
    nonce: str  # 96-bit hex (24 chars)
    ttl: int = 300  # seconds (default 5 minutes)

    # Scoping (v2.1)
    scope: Scope = field(default_factory=lambda: Scope(
        mission_id="default",
        workflow="default",
        domain=Domain.TECHNICAL
    ))
    topic_hash: str = ""  # sha256:hex

    # Policy-driven escalation (v2.1 - CRITICAL FIX)
    hazard: Optional[Hazard] = None

    # Optional fields
    topic: Optional[str] = None  # "if://topic/mission/legal/findings"
    protocol: str = "fipa-request"
    citation_ids: List[str] = field(default_factory=list)
    trace_id: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[Signature] = None

    def __post_init__(self):
        """Auto-generate fields if not provided"""
        if not self.nonce:
            self.nonce = self.generate_nonce()
        if not self.topic_hash:
            self.topic_hash = self.hash_conversation_id()
        if not self.trace_id:
            self.trace_id = self.generate_trace_id()

    @staticmethod
    def generate_nonce() -> str:
        """Generate 96-bit random nonce (anti-replay)"""
        return secrets.token_hex(12)  # 12 bytes = 96 bits

    @staticmethod
    def generate_trace_id() -> str:
        """Generate 48-bit trace ID (distributed tracing)"""
        return secrets.token_hex(6)  # 6 bytes = 48 bits

    def hash_conversation_id(self) -> str:
        """SHA-256 hash of conversation_id (collision detection)"""
        h = hashlib.sha256(self.conversation_id.encode()).hexdigest()
        return f"sha256:{h}"

    def is_expired(self) -> bool:
        """Check if message has exceeded TTL"""
        msg_time = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
        now = datetime.now(msg_time.tzinfo)
        age_seconds = (now - msg_time).total_seconds()
        return age_seconds > self.ttl

    def should_escalate(self, confidence: Optional[float] = None) -> bool:
        """
        Determine if message should trigger ESCALATE

        Priority order (CRITICAL FIX):
        1. Hazard auto_escalate flag (overrides confidence)
        2. Confidence < 0.2 (critical uncertainty)
        3. Otherwise: HOLD or SHARE based on confidence

        Args:
            confidence: Agent's confidence score (0.0-1.0)

        Returns:
            True if ESCALATE should be triggered
        """
        # 1. Check hazard first (v4* critical fix)
        if self.hazard and self.hazard.auto_escalate:
            return True

        # 2. Check critical confidence threshold
        if confidence is not None and confidence < 0.2:
            return True

        return False

    def route_decision(self, confidence: float) -> str:
        """
        Route message based on confidence + hazards

        Returns: "ESCALATE", "HOLD", or "SHARE"
        """
        # Hazard-first routing (v4* fix)
        if self.hazard and self.hazard.auto_escalate:
            return "ESCALATE"

        # Confidence-based routing (reordered from v2)
        if confidence < 0.2:
            return "ESCALATE"
        elif confidence < 0.3:
            return "HOLD"
        elif confidence >= 0.7:
            return "SHARE"
        else:
            return "HOLD"  # default conservative

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for JSON/gRPC"""
        result = asdict(self)

        # Convert enums to strings
        result['performative'] = self.performative.value
        result['scope']['domain'] = self.scope.domain.value

        if self.hazard:
            result['hazard']['type'] = self.hazard.type.value
            result['hazard']['severity'] = self.hazard.severity.value

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IFMessage':
        """Deserialize from dict"""
        # Convert string enums back to Enum objects
        data['performative'] = Performative(data['performative'])
        data['scope'] = Scope(
            mission_id=data['scope']['mission_id'],
            workflow=data['scope']['workflow'],
            domain=Domain(data['scope']['domain']),
            priority=data['scope'].get('priority', 'medium')
        )

        if 'hazard' in data and data['hazard']:
            data['hazard'] = Hazard(
                type=HazardType(data['hazard']['type']),
                severity=HazardSeverity(data['hazard']['severity']),
                rationale=data['hazard']['rationale'],
                auto_escalate=data['hazard'].get('auto_escalate', False),
                threshold_override=data['hazard'].get('threshold_override')
            )

        if 'signature' in data and data['signature']:
            data['signature'] = Signature(**data['signature'])

        return cls(**data)

    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict(), sort_keys=True, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'IFMessage':
        """Deserialize from JSON string"""
        return cls.from_dict(json.loads(json_str))


# Example usage
if __name__ == "__main__":
    # Example 1: Legal agent informs about settlement (with hazard tag)
    msg = IFMessage(
        performative=Performative.INFORM,
        sender="if://agent/swarm/legal-1@1.2.0",
        receiver=["if://agent/swarm/financial/*"],
        conversation_id="if://conversation/epic-2025-11-10-xyz",
        topic="if://topic/mission/legal/findings",
        content={
            "claim": "Epic Games settled antitrust lawsuit for $520M",
            "confidence": 0.25,  # LOW confidence
            "evidence": ["SEC-10K-2023:pg14", "Reuters:2025-09-17"]
        },
        citation_ids=["if://citation/9f2b3a1e"],
        timestamp=datetime.utcnow().isoformat() + "Z",
        sequence_num=42,
        scope=Scope(
            mission_id="epic-intelligence-v4",
            workflow="legal-findings-pass-3",
            domain=Domain.LEGAL
        ),
        hazard=Hazard(
            type=HazardType.LEGAL,
            severity=HazardSeverity.HIGH,
            auto_escalate=True,  # Force ESCALATE despite low confidence
            rationale="Potential liability exposure >$100M",
            threshold_override={
                "original_confidence": 0.25,
                "reason": "Legal hazard overrides confidence threshold"
            }
        )
    )

    print("=== Example Message (v2.1 with Hazard) ===")
    print(msg.to_json())
    print()

    # Test routing
    confidence = msg.content.get("confidence", 0.5)
    decision = msg.route_decision(confidence)
    print(f"Routing Decision: {decision}")
    print(f"Should Escalate: {msg.should_escalate(confidence)}")
    print(f"Is Expired: {msg.is_expired()}")
    print()

    # Example 2: Regular message without hazard
    msg2 = IFMessage(
        performative=Performative.INFORM,
        sender="if://agent/swarm/finance-2@2.3.1",
        receiver=["if://agent/swarm/legal-1@1.2.0"],
        conversation_id="if://conversation/epic-2025-11-10-xyz",
        content={
            "claim": "Epic Games Q3 2024 revenue: $1.2B",
            "confidence": 0.85  # HIGH confidence
        },
        citation_ids=["if://citation/4d8a7c2d"],
        timestamp=datetime.utcnow().isoformat() + "Z",
        sequence_num=43,
        scope=Scope(
            mission_id="epic-intelligence-v4",
            workflow="financial-analysis-pass-2",
            domain=Domain.FINANCE
        )
    )

    print("=== Example Message (v2.1 without Hazard) ===")
    print(msg2.to_json())
    print()

    confidence2 = msg2.content.get("confidence", 0.5)
    decision2 = msg2.route_decision(confidence2)
    print(f"Routing Decision: {decision2}")
    print(f"Should Escalate: {msg2.should_escalate(confidence2)}")
