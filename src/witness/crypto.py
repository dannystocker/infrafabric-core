"""
IF.witness Cryptographic Utilities
Ed25519 signatures and SHA-256 hash chains for tamper-proof witness entries.
"""

import hashlib
from pathlib import Path
from typing import Tuple
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey
)
from cryptography.hazmat.primitives import serialization


class WitnessCrypto:
    """
    Cryptographic operations for IF.witness.

    Philosophy: SWARM-COMMUNICATION-SECURITY.md
    - Ed25519 for signatures (fast, secure, 256-bit)
    - SHA-256 for content hashing (collision-resistant)
    - Hash chains for tamper detection
    """

    def __init__(self, private_key_path: Path = None):
        """
        Initialize crypto with optional private key path.
        If not provided, generates a new key pair.
        """
        self.private_key_path = private_key_path or Path.home() / '.if-witness' / 'private_key.pem'
        self.public_key_path = private_key_path.parent / 'public_key.pem' if private_key_path else Path.home() / '.if-witness' / 'public_key.pem'

        # Load or generate keys
        if self.private_key_path.exists():
            self.private_key = self._load_private_key()
        else:
            self.private_key = self._generate_and_save_keypair()

        self.public_key = self.private_key.public_key()

    def _generate_and_save_keypair(self) -> Ed25519PrivateKey:
        """Generate new Ed25519 keypair and save to disk"""
        # Create directory if it doesn't exist
        self.private_key_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate keypair
        private_key = Ed25519PrivateKey.generate()

        # Save private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        self.private_key_path.write_bytes(private_pem)
        self.private_key_path.chmod(0o600)  # Read/write for owner only

        # Save public key
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.public_key_path.write_bytes(public_pem)

        return private_key

    def _load_private_key(self) -> Ed25519PrivateKey:
        """Load private key from disk"""
        private_pem = self.private_key_path.read_bytes()
        return serialization.load_pem_private_key(private_pem, password=None)

    def sign(self, content: str) -> str:
        """
        Sign content with Ed25519 private key.

        Args:
            content: String to sign (canonical JSON representation)

        Returns:
            Hex-encoded signature string
        """
        signature_bytes = self.private_key.sign(content.encode('utf-8'))
        return signature_bytes.hex()

    def verify(self, content: str, signature: str, public_key_pem: bytes = None) -> bool:
        """
        Verify Ed25519 signature.

        Args:
            content: Original content that was signed
            signature: Hex-encoded signature
            public_key_pem: Optional PEM-encoded public key (uses own if not provided)

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Use provided public key or own
            if public_key_pem:
                public_key = serialization.load_pem_public_key(public_key_pem)
            else:
                public_key = self.public_key

            # Verify signature
            signature_bytes = bytes.fromhex(signature)
            public_key.verify(signature_bytes, content.encode('utf-8'))
            return True
        except Exception:
            return False

    @staticmethod
    def compute_hash(content: str) -> str:
        """
        Compute SHA-256 hash of content.

        Args:
            content: String to hash (canonical JSON representation)

        Returns:
            Hex-encoded hash string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get_public_key_string(self) -> str:
        """Get public key as PEM string for storage"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')


def verify_hash_chain(entries: list) -> Tuple[bool, str]:
    """
    Verify hash chain integrity.

    Args:
        entries: List of WitnessEntry objects (sorted by timestamp)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not entries:
        return True, ""

    for i in range(len(entries)):
        entry = entries[i]

        # Verify content hash matches computed hash
        computed_hash = WitnessCrypto.compute_hash(entry.get_canonical_content())
        if entry.content_hash != computed_hash:
            return False, f"Entry {i} ({entry.id}): Content hash mismatch"

        # Verify prev_hash points to previous entry (except first)
        if i > 0:
            prev_entry = entries[i - 1]
            if entry.prev_hash != prev_entry.content_hash:
                return False, f"Entry {i} ({entry.id}): Hash chain broken (prev_hash mismatch)"

        # First entry should have None prev_hash
        if i == 0 and entry.prev_hash is not None:
            return False, f"Entry 0 ({entry.id}): First entry should have prev_hash=None"

    return True, ""
