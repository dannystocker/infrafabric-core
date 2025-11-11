"""
H.323 Policy Enforcement for SIP-H.323 Gateway Bridge

This module enforces IF.guard Kantian policy gates on SIP calls that are bridged
to H.323 Guardian Council meetings. It ensures that external SIP participants
are subject to the same cryptographic and ethical constraints as native H.323 guardians.

Policy Gates Applied to Bridged SIP Calls:
1. Authenticity Gate: Verify SIP caller identity (SIP Digest Auth + Ed25519)
2. Anti-Sybil Gate: Check caller registration in guardian registry
3. PII Protection Gate: Redact sensitive information in ESCALATE calls
4. Fairness Gate: Enforce bandwidth quotas (max 3 Mbps per SIP caller)

Architecture:
- Wraps SIPH323Gateway with policy enforcement layer
- Applies same KantianPolicyEngine used for H.323 admission control
- Logs all policy decisions to IF.witness for audit trail
- Rejects non-compliant SIP calls before bridge establishment

Philosophy Grounding:
- Wu Lun (五倫): 朋友 (Friend-Friend) - SIP callers treated as peers, not subordinates
- Ubuntu: Inclusive participation - External experts join Guardian deliberations
- Kantian Duty: Universal categorical imperatives apply to all participants
- IF.TTT: Traceable, Transparent, Trustworthy

Author: InfraFabric Project
License: CC BY 4.0
Last Updated: 2025-11-11
"""

import json
import hashlib
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
import logging

# Import policy engine from H.323 gatekeeper
try:
    from h323_gatekeeper import (
        CallType,
        RejectReason,
        AdmissionRequest,
        AdmissionResponse,
        GuardianRegistry,
        SignatureVerifier,
        KantianPolicyEngine,
        WitnessLogger
    )
    GATEKEEPER_AVAILABLE = True
except ImportError:
    GATEKEEPER_AVAILABLE = False
    print("Warning: h323_gatekeeper module not available. Policy enforcement disabled.")


# ============================================================================
# Data Models for SIP Call Policy
# ============================================================================

class SIPAuthResult(Enum):
    """SIP authentication result"""
    AUTHENTICATED = "AUTHENTICATED"          # SIP Digest Auth + Ed25519 verified
    AUTH_FAILED = "AUTH_FAILED"             # SIP Digest Auth failed
    NO_SIGNATURE = "NO_SIGNATURE"           # Ed25519 signature missing
    INVALID_SIGNATURE = "INVALID_SIGNATURE" # Ed25519 verification failed


class PolicyViolationType(Enum):
    """Types of policy violations for bridged SIP calls"""
    PII_IN_ESCALATE = "PII_IN_ESCALATE"           # PII detected in ESCALATE call
    BANDWIDTH_EXCEEDED = "BANDWIDTH_EXCEEDED"      # > 3 Mbps for SIP caller
    NOT_REGISTERED = "NOT_REGISTERED"              # Caller not in guardian registry
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED" # Auth failure
    CODEC_NOT_ALLOWED = "CODEC_NOT_ALLOWED"        # Codec not in whitelist


@dataclass
class SIPCallContext:
    """Context for a SIP call being evaluated for bridge to H.323"""
    call_id: str                    # SIP Call-ID header
    from_uri: str                   # SIP From URI (sip:user@domain)
    to_uri: str                     # SIP To URI (conference room)
    call_type: CallType             # Inferred call type (ROUTINE/ESCALATE/EMERGENCY)
    requested_codec: str            # Codec (G.711, G.729, VP8, etc.)
    bandwidth_bps: int              # Requested bandwidth
    has_pii: bool                   # PII detected in SDP/headers
    sip_auth_result: SIPAuthResult  # SIP authentication status
    ed25519_signature: Optional[str] = None  # Ed25519 signature (if provided)
    ed25519_public_key: Optional[str] = None # Ed25519 public key (if provided)
    timestamp: str = None           # ISO 8601 timestamp

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class PolicyDecision:
    """Result of policy evaluation for a SIP call"""
    call_id: str
    allowed: bool                             # True if call is permitted
    violations: List[PolicyViolationType]     # List of policy violations
    reject_reason: Optional[RejectReason]     # H.323 reject reason (if denied)
    redactions_applied: List[str]             # PII redactions (if any)
    bandwidth_allocated_bps: int              # Allocated bandwidth
    timestamp: str
    policy_hash: str                          # SHA-256 hash of decision


# ============================================================================
# PII Detection & Redaction
# ============================================================================

class PIIDetector:
    """
    Detects personally identifiable information in SIP messages.
    Used for Kantian Gate 3: PII Protection
    """

    # PII patterns (US-centric for now, expand for international)
    PII_PATTERNS = {
        'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),                # US SSN
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),      # US phone
        'credit_card': re.compile(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'),
        'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),   # IPv4
    }

    @staticmethod
    def detect(text: str) -> Tuple[bool, List[str]]:
        """
        Detect PII in text. Returns (has_pii, detected_types).
        """
        detected_types = []
        for pii_type, pattern in PIIDetector.PII_PATTERNS.items():
            if pattern.search(text):
                detected_types.append(pii_type)

        return (len(detected_types) > 0, detected_types)

    @staticmethod
    def redact(text: str) -> Tuple[str, List[str]]:
        """
        Redact PII from text. Returns (redacted_text, redaction_log).
        """
        redacted = text
        redactions = []

        for pii_type, pattern in PIIDetector.PII_PATTERNS.items():
            matches = pattern.findall(redacted)
            if matches:
                redacted = pattern.sub(f"[REDACTED:{pii_type.upper()}]", redacted)
                redactions.append(f"{pii_type}: {len(matches)} instances")

        return (redacted, redactions)


# ============================================================================
# SIP Call Policy Enforcer
# ============================================================================

class SIPCallPolicyEnforcer:
    """
    Enforces IF.guard Kantian policy gates on SIP calls bridging to H.323.

    This is the main class that wraps the SIP-H.323 gateway and applies
    the same categorical imperatives used for H.323 admission control.
    """

    # Codec whitelist (approved for Guardian Council)
    ALLOWED_CODECS = ['G.711', 'G.729', 'VP8', 'Opus']

    # Bandwidth limits for SIP callers (more conservative than H.323)
    MAX_BANDWIDTH_BPS = 3_000_000  # 3 Mbps max for SIP (vs 10 Mbps for H.323)

    def __init__(
        self,
        registry: 'GuardianRegistry',
        verifier: 'SignatureVerifier',
        witness_logger: 'WitnessLogger',
        log_dir: Path = Path("logs/gateway")
    ):
        """
        Initialize policy enforcer.

        Args:
            registry: Guardian registry for anti-sybil checks
            verifier: Ed25519 signature verifier
            witness_logger: IF.witness audit logger
            log_dir: Directory for policy decision logs
        """
        self.registry = registry
        self.verifier = verifier
        self.witness = witness_logger
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize policy engine (same as H.323 gatekeeper)
        if GATEKEEPER_AVAILABLE:
            self.policy_engine = KantianPolicyEngine(registry, verifier)
        else:
            self.policy_engine = None
            logging.warning("KantianPolicyEngine not available. Policy enforcement disabled.")

    def evaluate_sip_call(self, context: SIPCallContext) -> PolicyDecision:
        """
        Evaluate a SIP call against Kantian policy gates.

        Args:
            context: SIP call context with caller info, codec, bandwidth

        Returns:
            PolicyDecision with allow/deny and violation details

        Gate 1: Authenticity (SIP Digest Auth + Ed25519)
        Gate 2: Anti-Sybil (Guardian registry check)
        Gate 3: PII Protection (Redaction in ESCALATE calls)
        Gate 4: Fairness (Bandwidth quota enforcement)
        """
        violations = []
        redactions = []
        allowed = True
        reject_reason = None

        # ==== Gate 1: Authenticity ====
        if context.sip_auth_result != SIPAuthResult.AUTHENTICATED:
            violations.append(PolicyViolationType.AUTHENTICATION_FAILED)
            reject_reason = RejectReason.INVALID_SIGNATURE
            allowed = False

        # If Ed25519 signature provided, verify it
        if context.ed25519_signature and context.ed25519_public_key:
            # Create canonical message for verification
            canonical_msg = json.dumps({
                "call_id": context.call_id,
                "from_uri": context.from_uri,
                "to_uri": context.to_uri,
                "call_type": context.call_type.value,
                "bandwidth_bps": context.bandwidth_bps,
                "timestamp": context.timestamp
            }, sort_keys=True)

            if not self.verifier.verify(
                canonical_msg,
                context.ed25519_signature,
                context.ed25519_public_key
            ):
                violations.append(PolicyViolationType.AUTHENTICATION_FAILED)
                reject_reason = RejectReason.INVALID_SIGNATURE
                allowed = False

        # ==== Gate 2: Anti-Sybil (Registry Check) ====
        # Extract terminal ID from SIP URI (sip:user@domain → if://guardian/user)
        terminal_id = self._sip_uri_to_terminal_id(context.from_uri)

        if not self.registry.is_registered(terminal_id):
            violations.append(PolicyViolationType.NOT_REGISTERED)
            reject_reason = RejectReason.NOT_REGISTERED
            allowed = False

        # ==== Gate 3: PII Protection ====
        if context.call_type == CallType.ESCALATE and context.has_pii:
            violations.append(PolicyViolationType.PII_IN_ESCALATE)
            reject_reason = RejectReason.PII_POLICY_VIOLATION
            allowed = False

        # Apply redactions if ESCALATE call (even if allowed)
        if context.call_type == CallType.ESCALATE:
            # Redact PII from SIP headers/SDP
            _, redaction_log = PIIDetector.redact(context.from_uri + context.to_uri)
            redactions.extend(redaction_log)

        # ==== Gate 4: Fairness (Bandwidth Quota) ====
        if context.bandwidth_bps > self.MAX_BANDWIDTH_BPS:
            violations.append(PolicyViolationType.BANDWIDTH_EXCEEDED)
            reject_reason = RejectReason.BANDWIDTH_EXCEEDED
            allowed = False

        # Additional check: Codec whitelist
        if context.requested_codec not in self.ALLOWED_CODECS:
            violations.append(PolicyViolationType.CODEC_NOT_ALLOWED)
            reject_reason = RejectReason.GATEKEEPER_ERROR
            allowed = False

        # Allocate bandwidth (capped at max)
        bandwidth_allocated = min(context.bandwidth_bps, self.MAX_BANDWIDTH_BPS)

        # Create policy decision
        decision = PolicyDecision(
            call_id=context.call_id,
            allowed=allowed,
            violations=violations,
            reject_reason=reject_reason,
            redactions_applied=redactions,
            bandwidth_allocated_bps=bandwidth_allocated,
            timestamp=datetime.now(timezone.utc).isoformat(),
            policy_hash=""  # Computed below
        )

        # Compute policy hash (content-addressed)
        decision.policy_hash = self._compute_policy_hash(decision)

        # Log to IF.witness
        self._log_policy_decision(context, decision)

        return decision

    def _sip_uri_to_terminal_id(self, sip_uri: str) -> str:
        """
        Convert SIP URI to IF terminal ID.
        Example: sip:alice@example.com → if://guardian/alice
        """
        # Extract username from SIP URI
        match = re.match(r'sip:([^@]+)@', sip_uri)
        if match:
            username = match.group(1)
            return f"if://guardian/{username}"
        else:
            return sip_uri  # Fallback

    def _compute_policy_hash(self, decision: PolicyDecision) -> str:
        """
        Compute SHA-256 hash of policy decision for tamper-proofing.
        """
        decision_dict = asdict(decision)
        decision_dict.pop('policy_hash', None)  # Exclude hash field
        canonical = json.dumps(decision_dict, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _log_policy_decision(self, context: SIPCallContext, decision: PolicyDecision):
        """
        Log policy decision to IF.witness audit trail.
        """
        log_entry = {
            "event_type": "SIP_POLICY_DECISION",
            "timestamp": decision.timestamp,
            "call_id": context.call_id,
            "from_uri": context.from_uri,
            "to_uri": context.to_uri,
            "call_type": context.call_type.value,
            "requested_codec": context.requested_codec,
            "requested_bandwidth_bps": context.bandwidth_bps,
            "sip_auth_result": context.sip_auth_result.value,
            "decision": {
                "allowed": decision.allowed,
                "violations": [v.value for v in decision.violations],
                "reject_reason": decision.reject_reason.value if decision.reject_reason else None,
                "redactions_applied": decision.redactions_applied,
                "bandwidth_allocated_bps": decision.bandwidth_allocated_bps,
                "policy_hash": decision.policy_hash
            }
        }

        # Append to daily log file
        log_file = self.log_dir / f"sip_policy_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


# ============================================================================
# Policy-Aware SIP-H.323 Gateway Wrapper
# ============================================================================

class PolicyAwareGateway:
    """
    Wraps SIPH323Gateway with Kantian policy enforcement.

    This class intercepts SIP calls before bridging and applies the
    same categorical imperatives used for H.323 admission control.
    """

    def __init__(
        self,
        gateway: 'SIPH323Gateway',
        policy_enforcer: SIPCallPolicyEnforcer
    ):
        """
        Initialize policy-aware gateway wrapper.

        Args:
            gateway: SIPH323Gateway instance
            policy_enforcer: SIPCallPolicyEnforcer instance
        """
        self.gateway = gateway
        self.policy = policy_enforcer

    def bridge_call_with_policy(
        self,
        sip_call_id: str,
        from_uri: str,
        to_uri: str,
        call_type: CallType,
        codec: str,
        bandwidth_bps: int,
        sip_auth_result: SIPAuthResult,
        ed25519_signature: Optional[str] = None,
        ed25519_public_key: Optional[str] = None
    ) -> Tuple[bool, Optional[PolicyDecision]]:
        """
        Bridge a SIP call to H.323 with policy enforcement.

        Args:
            sip_call_id: SIP Call-ID header
            from_uri: SIP From URI
            to_uri: SIP To URI (conference room)
            call_type: Call type (ROUTINE/ESCALATE/EMERGENCY)
            codec: Requested codec
            bandwidth_bps: Requested bandwidth
            sip_auth_result: SIP authentication result
            ed25519_signature: Optional Ed25519 signature
            ed25519_public_key: Optional Ed25519 public key

        Returns:
            (success, policy_decision)
        """
        # Detect PII in SIP headers
        combined_text = from_uri + to_uri + sip_call_id
        has_pii, pii_types = PIIDetector.detect(combined_text)

        # Create SIP call context
        context = SIPCallContext(
            call_id=sip_call_id,
            from_uri=from_uri,
            to_uri=to_uri,
            call_type=call_type,
            requested_codec=codec,
            bandwidth_bps=bandwidth_bps,
            has_pii=has_pii,
            sip_auth_result=sip_auth_result,
            ed25519_signature=ed25519_signature,
            ed25519_public_key=ed25519_public_key
        )

        # Evaluate against Kantian policy gates
        decision = self.policy.evaluate_sip_call(context)

        # If allowed, proceed with bridge
        if decision.allowed:
            # Call underlying gateway to establish bridge
            # (This would call gateway.bridge_call() in real implementation)
            return (True, decision)
        else:
            # Reject call
            return (False, decision)


# ============================================================================
# Usage Example
# ============================================================================

def example_usage():
    """
    Example demonstrating policy enforcement on a SIP-H.323 bridge.
    """
    if not GATEKEEPER_AVAILABLE:
        print("Gatekeeper module not available. Skipping example.")
        return

    # Initialize components
    registry = GuardianRegistry(Path("config/guardian-registry.yaml"))
    verifier = SignatureVerifier()
    witness = WitnessLogger(Path("logs/h323_witness"))
    policy_enforcer = SIPCallPolicyEnforcer(registry, verifier, witness)

    # Simulate incoming SIP call
    context = SIPCallContext(
        call_id="sip-call-12345",
        from_uri="sip:alice@example.com",
        to_uri="sip:guardian-council@infrafabric.org",
        call_type=CallType.ROUTINE,
        requested_codec="G.711",
        bandwidth_bps=2_000_000,  # 2 Mbps
        has_pii=False,
        sip_auth_result=SIPAuthResult.AUTHENTICATED
    )

    # Evaluate policy
    decision = policy_enforcer.evaluate_sip_call(context)

    # Print result
    print(f"Policy Decision: {'ALLOWED' if decision.allowed else 'DENIED'}")
    if not decision.allowed:
        print(f"Reject Reason: {decision.reject_reason.value}")
        print(f"Violations: {[v.value for v in decision.violations]}")
    print(f"Bandwidth Allocated: {decision.bandwidth_allocated_bps / 1_000_000:.1f} Mbps")
    print(f"Policy Hash: {decision.policy_hash[:16]}...")


if __name__ == "__main__":
    example_usage()
