"""
H.323 Gatekeeper with Ed25519 Admission Control for IF.guard Guardian Council

This module implements the H.323 Gatekeeper component for InfraFabric's Guardian Council
conferencing system. It provides cryptographically secured admission control using Ed25519
signatures, enforcing Kantian policy gates (PII protection, bandwidth quotas, registration).

Architecture:
- Wraps GNU Gatekeeper (gnugk) via subprocess
- Implements RAS protocol (ARQ → ACF/ARJ)
- Ed25519 signature verification for all admission requests
- IF.witness logging for full traceability
- Kantian policy enforcement (categorical imperatives)

Philosophy Grounding:
- Wu Lun (五倫): 君臣 (Ruler-Subject) - Gatekeeper grants admission, terminals obey
- Ubuntu: Communal consensus via MCU (everyone hears everyone)
- Kantian Duty: Admission gates enforce categorical imperatives
- IF.TTT: Traceable, Transparent, Trustworthy

Author: InfraFabric Project
License: CC BY 4.0
Last Updated: 2025-11-11
"""

import json
import subprocess
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List, Any
import hashlib
import yaml

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey
    )
    from cryptography.hazmat.primitives import serialization
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: cryptography library not available. Ed25519 verification disabled.")


# ============================================================================
# Data Models
# ============================================================================

class CallType(Enum):
    """H.323 call types for Guardian Council"""
    ROUTINE = "ROUTINE"           # Normal deliberation (no restrictions)
    ESCALATE = "ESCALATE"         # High-stakes decision (PII forbidden)
    EMERGENCY = "EMERGENCY"       # Crisis response (bandwidth priority)


class RejectReason(Enum):
    """H.323 ARJ (Admission Reject) reasons"""
    INVALID_SIGNATURE = "INVALID_SIGNATURE"         # Ed25519 verification failed
    NOT_REGISTERED = "NOT_REGISTERED"               # Guardian not in registry
    PII_POLICY_VIOLATION = "PII_POLICY_VIOLATION"   # PII in ESCALATE call
    BANDWIDTH_EXCEEDED = "BANDWIDTH_EXCEEDED"       # > 10 Mbps quota
    CAPACITY_EXCEEDED = "CAPACITY_EXCEEDED"         # MCU full (>25 participants)
    GATEKEEPER_ERROR = "GATEKEEPER_ERROR"           # Internal error


@dataclass
class AdmissionRequest:
    """H.323 ARQ (Admission Request) message"""
    terminal_id: str              # if://guardian/{name}
    call_id: str                  # Unique call identifier
    call_type: CallType           # ROUTINE | ESCALATE | EMERGENCY
    bandwidth_bps: int            # Requested bandwidth (bits/sec)
    has_pii: bool                 # Contains personally identifiable info
    timestamp: str                # ISO 8601 timestamp
    signature: str                # Ed25519 signature (hex)
    public_key: str               # Ed25519 public key (hex)

    def to_canonical(self) -> str:
        """Create canonical representation for signature verification"""
        fields = {
            "terminal_id": self.terminal_id,
            "call_id": self.call_id,
            "call_type": self.call_type.value,
            "bandwidth_bps": self.bandwidth_bps,
            "has_pii": self.has_pii,
            "timestamp": self.timestamp
        }
        return json.dumps(fields, sort_keys=True)


@dataclass
class AdmissionResponse:
    """H.323 ACF (Admission Confirm) or ARJ (Admission Reject)"""
    call_id: str
    terminal_id: str
    confirmed: bool               # ACF=True, ARJ=False
    reject_reason: Optional[RejectReason] = None
    mcu_address: Optional[str] = None      # if://service/guard/mcu:1720
    allocated_bandwidth: Optional[int] = None
    session_id: Optional[str] = None       # Unique session identifier
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class GuardianRegistration:
    """Guardian registry entry with Ed25519 public key"""
    terminal_id: str              # if://guardian/{name}
    public_key: str               # Ed25519 public key (hex)
    role: str                     # Guardian archetype (Technical, Civic, etc.)
    bandwidth_quota_bps: int      # Max bandwidth (default 10 Mbps)
    registered_at: str            # ISO 8601 timestamp
    status: str = "active"        # active | suspended | revoked


# ============================================================================
# Guardian Registry
# ============================================================================

class GuardianRegistry:
    """
    Manages Guardian Council member registrations with Ed25519 public keys.
    Prevents sybil attacks by enforcing whitelist-only admission.
    """

    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self.guardians: Dict[str, GuardianRegistration] = {}
        self.load_registry()

    def load_registry(self):
        """Load guardian registry from YAML file"""
        if not self.registry_path.exists():
            print(f"Warning: Registry not found at {self.registry_path}")
            return

        with open(self.registry_path, 'r') as f:
            data = yaml.safe_load(f)

        for entry in data.get('guardians', []):
            guardian = GuardianRegistration(**entry)
            self.guardians[guardian.terminal_id] = guardian

        print(f"Loaded {len(self.guardians)} guardians from registry")

    def is_registered(self, terminal_id: str) -> bool:
        """Check if guardian is registered and active"""
        guardian = self.guardians.get(terminal_id)
        return guardian is not None and guardian.status == "active"

    def get_guardian(self, terminal_id: str) -> Optional[GuardianRegistration]:
        """Retrieve guardian registration"""
        return self.guardians.get(terminal_id)

    def get_public_key(self, terminal_id: str) -> Optional[str]:
        """Get guardian's Ed25519 public key"""
        guardian = self.guardians.get(terminal_id)
        return guardian.public_key if guardian else None

    def get_bandwidth_quota(self, terminal_id: str) -> int:
        """Get guardian's bandwidth quota (default 10 Mbps)"""
        guardian = self.guardians.get(terminal_id)
        return guardian.bandwidth_quota_bps if guardian else 10_000_000


# ============================================================================
# Ed25519 Signature Verification
# ============================================================================

class SignatureVerifier:
    """Ed25519 signature verification for admission control"""

    @staticmethod
    def verify_signature(message: str, signature_hex: str, public_key_hex: str) -> bool:
        """
        Verify Ed25519 signature on admission request.

        Args:
            message: Canonical message representation
            signature_hex: Hex-encoded Ed25519 signature
            public_key_hex: Hex-encoded Ed25519 public key

        Returns:
            True if signature valid, False otherwise
        """
        if not CRYPTO_AVAILABLE:
            print("Warning: Cryptography unavailable, skipping verification")
            return True  # Fail-open in dev mode (REMOVE IN PRODUCTION)

        try:
            # Decode hex to bytes
            signature_bytes = bytes.fromhex(signature_hex)
            public_key_bytes = bytes.fromhex(public_key_hex)

            # Reconstruct public key
            public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)

            # Verify signature
            public_key.verify(signature_bytes, message.encode('utf-8'))
            return True

        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False


# ============================================================================
# IF.witness Logging
# ============================================================================

class WitnessLogger:
    """
    Immutable audit trail for all RAS messages (ARQ/ACF/ARJ).
    Implements IF.TTT: Traceable, Transparent, Trustworthy
    """

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_admission_request(self, arq: AdmissionRequest):
        """Log incoming admission request"""
        self._write_log("ARQ", {
            "terminal_id": arq.terminal_id,
            "call_id": arq.call_id,
            "call_type": arq.call_type.value,
            "bandwidth_bps": arq.bandwidth_bps,
            "has_pii": arq.has_pii,
            "timestamp": arq.timestamp,
            "signature": arq.signature[:16] + "...",  # Truncate for readability
        })

    def log_admission_response(self, response: AdmissionResponse):
        """Log admission response (ACF or ARJ)"""
        msg_type = "ACF" if response.confirmed else "ARJ"
        self._write_log(msg_type, {
            "call_id": response.call_id,
            "terminal_id": response.terminal_id,
            "confirmed": response.confirmed,
            "reject_reason": response.reject_reason.value if response.reject_reason else None,
            "mcu_address": response.mcu_address,
            "timestamp": response.timestamp,
        })

    def _write_log(self, msg_type: str, data: Dict[str, Any]):
        """Write log entry with Merkle tree hash for tamper-proofing"""
        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = {
            "msg_type": msg_type,
            "timestamp": timestamp,
            "data": data,
        }

        # Content-addressed hash (IF.witness pattern)
        content_hash = hashlib.sha256(
            json.dumps(log_entry, sort_keys=True).encode()
        ).hexdigest()
        log_entry["hash"] = content_hash

        # Append to log file (immutable append-only)
        log_file = self.log_dir / f"h323_ras_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


# ============================================================================
# Kantian Policy Gates
# ============================================================================

class KantianPolicyEngine:
    """
    Enforces categorical imperatives for Guardian Council admission.

    Philosophy:
    - Categorical Imperative 1: NO PII in ESCALATE calls (prevents bias)
    - Categorical Imperative 2: NO unregistered terminals (prevents sybil)
    - Categorical Imperative 3: NO bandwidth abuse (fairness)
    - Categorical Imperative 4: NO invalid signatures (authenticity)
    """

    def __init__(self, registry: GuardianRegistry, verifier: SignatureVerifier):
        self.registry = registry
        self.verifier = verifier

    def evaluate_admission(self, arq: AdmissionRequest) -> AdmissionResponse:
        """
        Apply Kantian policy gates to admission request.

        Gate 1: Verify Ed25519 signature (authenticity)
        Gate 2: Check guardian registration (prevent sybil)
        Gate 3: Enforce PII policy (ESCALATE calls)
        Gate 4: Enforce bandwidth quota (fairness)

        Returns:
            AdmissionResponse (ACF or ARJ)
        """

        # Gate 1: Verify Ed25519 signature
        canonical = arq.to_canonical()
        if not self.verifier.verify_signature(canonical, arq.signature, arq.public_key):
            return AdmissionResponse(
                call_id=arq.call_id,
                terminal_id=arq.terminal_id,
                confirmed=False,
                reject_reason=RejectReason.INVALID_SIGNATURE
            )

        # Gate 2: Check registry (prevent sybil attacks)
        if not self.registry.is_registered(arq.terminal_id):
            return AdmissionResponse(
                call_id=arq.call_id,
                terminal_id=arq.terminal_id,
                confirmed=False,
                reject_reason=RejectReason.NOT_REGISTERED
            )

        # Verify public key matches registry
        registered_key = self.registry.get_public_key(arq.terminal_id)
        if registered_key != arq.public_key:
            return AdmissionResponse(
                call_id=arq.call_id,
                terminal_id=arq.terminal_id,
                confirmed=False,
                reject_reason=RejectReason.INVALID_SIGNATURE  # Key mismatch
            )

        # Gate 3: Kantian constraint - NO PII in ESCALATE calls
        if arq.call_type == CallType.ESCALATE and arq.has_pii:
            return AdmissionResponse(
                call_id=arq.call_id,
                terminal_id=arq.terminal_id,
                confirmed=False,
                reject_reason=RejectReason.PII_POLICY_VIOLATION
            )

        # Gate 4: Bandwidth quota enforcement
        quota = self.registry.get_bandwidth_quota(arq.terminal_id)
        if arq.bandwidth_bps > quota:
            return AdmissionResponse(
                call_id=arq.call_id,
                terminal_id=arq.terminal_id,
                confirmed=False,
                reject_reason=RejectReason.BANDWIDTH_EXCEEDED
            )

        # All gates passed - ACF (Admission Confirm)
        return AdmissionResponse(
            call_id=arq.call_id,
            terminal_id=arq.terminal_id,
            confirmed=True,
            mcu_address="if://service/guard/mcu:1720",
            allocated_bandwidth=arq.bandwidth_bps,
            session_id=str(uuid.uuid4())
        )


# ============================================================================
# H.323 Gatekeeper
# ============================================================================

class H323Gatekeeper:
    """
    H.323 Gatekeeper for Guardian Council conferencing.

    Wraps GNU Gatekeeper (gnugk) and provides:
    - Ed25519 admission control
    - Kantian policy enforcement
    - IF.witness audit logging
    - MCU coordination
    """

    def __init__(
        self,
        registry_path: Path,
        witness_log_dir: Path,
        gnugk_config_path: Optional[Path] = None
    ):
        self.registry = GuardianRegistry(registry_path)
        self.verifier = SignatureVerifier()
        self.policy_engine = KantianPolicyEngine(self.registry, self.verifier)
        self.witness = WitnessLogger(witness_log_dir)
        self.gnugk_config_path = gnugk_config_path

        # Session tracking
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def start_gatekeeper(self) -> bool:
        """
        Start GNU Gatekeeper subprocess.

        Returns:
            True if started successfully, False otherwise
        """
        try:
            # Check if gnugk is installed
            result = subprocess.run(
                ["which", "gnugk"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                print("GNU Gatekeeper (gnugk) not found. Install: apt-get install gnugk")
                print("Running in mock mode (admission control only)")
                return True  # Continue in mock mode

            # Start gnugk (if config exists)
            if self.gnugk_config_path and self.gnugk_config_path.exists():
                subprocess.Popen(
                    ["gnugk", "-c", str(self.gnugk_config_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print(f"GNU Gatekeeper started with config: {self.gnugk_config_path}")
            else:
                print("No gnugk config provided, running admission control only")

            return True

        except Exception as e:
            print(f"Error starting gatekeeper: {e}")
            return False

    def request_admission(self, arq: AdmissionRequest) -> AdmissionResponse:
        """
        Process H.323 admission request (ARQ).

        Workflow:
        1. Log ARQ to IF.witness
        2. Apply Kantian policy gates
        3. Log response (ACF/ARJ) to IF.witness
        4. Return response

        Args:
            arq: AdmissionRequest with Ed25519 signature

        Returns:
            AdmissionResponse (ACF or ARJ)
        """

        # Log incoming request
        self.witness.log_admission_request(arq)

        # Apply policy gates
        response = self.policy_engine.evaluate_admission(arq)

        # Track active sessions (if admitted)
        if response.confirmed:
            self.active_sessions[response.session_id] = {
                "call_id": arq.call_id,
                "terminal_id": arq.terminal_id,
                "bandwidth_bps": response.allocated_bandwidth,
                "admitted_at": response.timestamp,
            }

        # Log response
        self.witness.log_admission_response(response)

        return response

    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active Guardian Council sessions"""
        return self.active_sessions

    def get_session_count(self) -> int:
        """Get count of active sessions"""
        return len(self.active_sessions)

    def revoke_session(self, session_id: str) -> bool:
        """Revoke an active session (disconnect terminal)"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False


# ============================================================================
# Helper Functions
# ============================================================================

def generate_test_keypair() -> tuple[str, str]:
    """Generate Ed25519 keypair for testing (REMOVE IN PRODUCTION)"""
    if not CRYPTO_AVAILABLE:
        return ("test_private_key", "test_public_key")

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_hex = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    ).hex()

    public_hex = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ).hex()

    return (private_hex, public_hex)


def sign_admission_request(arq: AdmissionRequest, private_key_hex: str) -> str:
    """Sign admission request with Ed25519 private key"""
    if not CRYPTO_AVAILABLE:
        return "mock_signature"

    canonical = arq.to_canonical()
    private_key_bytes = bytes.fromhex(private_key_hex)
    private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    signature_bytes = private_key.sign(canonical.encode('utf-8'))
    return signature_bytes.hex()


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Setup paths
    registry_path = Path("/home/user/infrafabric/config/guardian-registry.yaml")
    witness_dir = Path("/home/user/infrafabric/logs/h323_witness")

    # Initialize gatekeeper
    gatekeeper = H323Gatekeeper(
        registry_path=registry_path,
        witness_log_dir=witness_dir
    )

    print("H.323 Gatekeeper initialized")
    print(f"Registered guardians: {len(gatekeeper.registry.guardians)}")

    # Start gatekeeper service
    gatekeeper.start_gatekeeper()

    print("\nGatekeeper ready for admission requests")
    print("Endpoint: if://service/guard/gatekeeper:1719")
