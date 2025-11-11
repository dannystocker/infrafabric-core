#!/usr/bin/env python3
# Copyright (c) 2025 Danny Stocker
# SPDX-License-Identifier: MIT
#
# InfraFabric - NDI Witness Publisher
# Source: https://github.com/dannystocker/infrafabric
# Licensed under the MIT License.

"""
NDI Witness Publisher - Stream IF.yologuard output as NDI with witness provenance

Philosophy Grounding:
- Wu Lun (五倫) Relationship: 父子 (Parent-Child) — NDI sender creates stream, receivers consume
- IF.ground Principle 1: Ground in Observable Artifacts — Every frame is verifiable by hash
- IF.witness: Every frame has provenance (who scanned, what found, when, trace_id)
- IF.TTT: Traceable (hash chain), Transparent (metadata visible), Trustworthy (Ed25519 signed)

Architecture:
1. Wraps IF.yologuard scanner output as video stream
2. Injects witness hash chain into NDI metadata
3. Signs each frame with Ed25519 (cryptographic provenance)
4. Propagates trace_id from IFMessage v2.1 schema

Witness Hash Chain: prev_hash → content_hash → signature
- Genesis frame: prev_hash = "0" * 64 (SHA-256 zero)
- Each frame: content_hash = SHA-256(frame_data + metadata)
- Next frame: prev_hash = content_hash of previous frame
"""

import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey
)
from cryptography.hazmat.primitives import serialization


# Mock NDI interface (replace with real ndi-python when SDK available)
class MockNDISender:
    """Mock NDI sender for testing without SDK

    Replace with real NDI SDK:
    from NDIlib import NDIlib_send_create, NDIlib_send_send_video
    """

    def __init__(self, stream_name: str):
        self.stream_name = stream_name
        self.is_running = False
        print(f"[MockNDI] Created sender: {stream_name}")

    def start(self):
        self.is_running = True
        print(f"[MockNDI] Started sender: {self.stream_name}")

    def send_frame(self, frame_data: bytes, metadata: Dict[str, Any]):
        """Send video frame with metadata"""
        if not self.is_running:
            raise RuntimeError("Sender not started")
        print(f"[MockNDI] Sent frame {metadata.get('frame_number', '?')} with {len(frame_data)} bytes")

    def stop(self):
        self.is_running = False
        print(f"[MockNDI] Stopped sender: {self.stream_name}")


class WitnessHashChain:
    """Witness hash chain implementation

    Creates cryptographic chain linking frames:
    Genesis: prev_hash = "0"*64 → content_hash → signature
    Frame N: prev_hash = hash(N-1) → content_hash → signature
    """

    GENESIS_HASH = "0" * 64  # SHA-256 zero hash

    def __init__(self):
        self.prev_hash = self.GENESIS_HASH
        self.chain_id = str(uuid.uuid4())
        self.frame_count = 0

    def compute_content_hash(self, frame_data: bytes, metadata: Dict[str, Any]) -> str:
        """Compute SHA-256 hash of frame content + metadata

        Args:
            frame_data: Raw frame bytes
            metadata: Frame metadata dict

        Returns:
            Hex-encoded SHA-256 hash
        """
        hasher = hashlib.sha256()
        hasher.update(frame_data)

        # Hash metadata in canonical form (sorted JSON)
        metadata_json = json.dumps(metadata, sort_keys=True)
        hasher.update(metadata_json.encode('utf-8'))

        return hasher.hexdigest()

    def advance(self, content_hash: str):
        """Advance chain to next frame

        Args:
            content_hash: Hash of current frame (becomes prev_hash for next frame)
        """
        self.prev_hash = content_hash
        self.frame_count += 1

    def get_chain_state(self) -> Dict[str, Any]:
        """Get current chain state for metadata"""
        return {
            "chain_id": self.chain_id,
            "frame_count": self.frame_count,
            "prev_hash": self.prev_hash
        }


class Ed25519Signer:
    """Ed25519 signature provider for witness provenance

    Follows SWARM-COMMUNICATION-SECURITY.md architecture
    """

    def __init__(self, private_key: Optional[Ed25519PrivateKey] = None):
        """Initialize signer with private key

        Args:
            private_key: Ed25519 private key (generates new if None)
        """
        if private_key is None:
            self.private_key = Ed25519PrivateKey.generate()
        else:
            self.private_key = private_key

        self.public_key = self.private_key.public_key()

    def sign_metadata(self, metadata: Dict[str, Any]) -> str:
        """Sign metadata dict with Ed25519

        Args:
            metadata: Metadata to sign

        Returns:
            Hex-encoded signature
        """
        # Canonical representation (sorted JSON)
        canonical = json.dumps(metadata, sort_keys=True)
        signature_bytes = self.private_key.sign(canonical.encode('utf-8'))
        return signature_bytes.hex()

    def get_public_key_base64(self) -> str:
        """Export public key as Base64 (for metadata)"""
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        import base64
        return base64.b64encode(public_bytes).decode('ascii')

    def save_keypair(self, private_path: Path, public_path: Path):
        """Save keypair to files for persistent identity"""
        # Save private key
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        private_path.write_bytes(private_pem)

        # Save public key
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        public_path.write_bytes(public_pem)

    @classmethod
    def load_private_key(cls, private_path: Path) -> 'Ed25519Signer':
        """Load signer from private key file"""
        private_pem = private_path.read_bytes()
        private_key = serialization.load_pem_private_key(
            private_pem,
            password=None
        )
        return cls(private_key)


class NDIWitnessPublisher:
    """NDI Witness Publisher - Stream scanner output with cryptographic provenance

    Usage:
        publisher = NDIWitnessPublisher(
            stream_name="IF.witness.yologuard.01",
            component="IF.yologuard",
            signer=Ed25519Signer()
        )

        publisher.start()

        for scan_result in scanner_output:
            publisher.publish_frame(
                frame_data=render_scan_result(scan_result),
                scan_metadata=scan_result,
                trace_id="trace-abc-123"
            )

        publisher.stop()
    """

    def __init__(
        self,
        stream_name: str,
        component: str,
        signer: Ed25519Signer,
        use_mock: bool = True
    ):
        """Initialize NDI witness publisher

        Args:
            stream_name: NDI stream name (e.g., "IF.witness.yologuard.01")
            component: Component identifier (e.g., "IF.yologuard")
            signer: Ed25519 signer for frame signatures
            use_mock: Use mock NDI sender (True) or real SDK (False)
        """
        self.stream_name = stream_name
        self.component = component
        self.signer = signer
        self.hash_chain = WitnessHashChain()

        # Create NDI sender (mock or real)
        if use_mock:
            self.ndi_sender = MockNDISender(stream_name)
        else:
            # Real NDI SDK integration point
            raise NotImplementedError("Real NDI SDK not available - install ndi-python")

        self.started = False

    def start(self):
        """Start NDI stream"""
        self.ndi_sender.start()
        self.started = True

    def publish_frame(
        self,
        frame_data: bytes,
        scan_metadata: Dict[str, Any],
        trace_id: Optional[str] = None
    ):
        """Publish frame with witness metadata

        Args:
            frame_data: Frame image bytes (rendered scan output)
            scan_metadata: Scanner metadata (findings, file, line, etc.)
            trace_id: IFMessage trace_id for correlation
        """
        if not self.started:
            raise RuntimeError("Publisher not started - call start() first")

        frame_number = self.hash_chain.frame_count + 1
        timestamp = datetime.now(timezone.utc).isoformat()

        # Build witness metadata
        witness_metadata = {
            "frame_number": frame_number,
            "timestamp": timestamp,
            "component": self.component,
            "trace_id": trace_id or str(uuid.uuid4()),
            "scan_metadata": scan_metadata,
            "chain_state": self.hash_chain.get_chain_state()
        }

        # Compute content hash (frame + metadata)
        content_hash = self.hash_chain.compute_content_hash(frame_data, witness_metadata)
        witness_metadata["content_hash"] = content_hash

        # Sign metadata (Ed25519)
        signature = self.signer.sign_metadata(witness_metadata)
        witness_metadata["signature"] = signature
        witness_metadata["public_key"] = self.signer.get_public_key_base64()

        # Send frame with metadata via NDI
        self.ndi_sender.send_frame(frame_data, witness_metadata)

        # Advance hash chain
        self.hash_chain.advance(content_hash)

    def stop(self):
        """Stop NDI stream"""
        self.ndi_sender.stop()
        self.started = False

    def get_stream_info(self) -> Dict[str, Any]:
        """Get stream info for discovery"""
        return {
            "stream_name": self.stream_name,
            "component": self.component,
            "chain_id": self.hash_chain.chain_id,
            "frame_count": self.hash_chain.frame_count,
            "public_key": self.signer.get_public_key_base64()
        }


def main():
    """Example usage: Stream IF.yologuard output as NDI"""
    import argparse

    parser = argparse.ArgumentParser(description="NDI Witness Publisher")
    parser.add_argument('--stream-name', default='IF.witness.yologuard.01',
                        help='NDI stream name')
    parser.add_argument('--component', default='IF.yologuard',
                        help='Component identifier')
    parser.add_argument('--frames', type=int, default=10,
                        help='Number of test frames to publish')
    args = parser.parse_args()

    print("=" * 80)
    print("NDI Witness Publisher - IF.witness Integration")
    print("=" * 80)

    # Create signer
    signer = Ed25519Signer()
    print(f"Generated Ed25519 keypair")
    print(f"Public key: {signer.get_public_key_base64()}")

    # Create publisher
    publisher = NDIWitnessPublisher(
        stream_name=args.stream_name,
        component=args.component,
        signer=signer
    )

    # Start streaming
    publisher.start()
    print(f"\nStreaming as: {args.stream_name}")

    # Publish test frames
    for i in range(args.frames):
        # Simulate IF.yologuard scan result
        scan_metadata = {
            "file": f"/code/test/secrets_{i}.py",
            "line": 42 + i,
            "pattern": "AWS_KEY_REDACTED",
            "severity": "ERROR",
            "relationship_score": 0.85
        }

        # Simulate rendered frame (in real use, render scan output to image)
        frame_data = f"Frame {i+1}: {scan_metadata}".encode('utf-8')

        publisher.publish_frame(
            frame_data=frame_data,
            scan_metadata=scan_metadata,
            trace_id=f"trace-{uuid.uuid4()}"
        )

        time.sleep(0.5)  # 2 FPS for demo

    # Stop streaming
    publisher.stop()

    # Print stream info
    print("\n" + "=" * 80)
    print("Stream Summary")
    print("=" * 80)
    info = publisher.get_stream_info()
    print(f"Stream name:  {info['stream_name']}")
    print(f"Component:    {info['component']}")
    print(f"Chain ID:     {info['chain_id']}")
    print(f"Frames sent:  {info['frame_count']}")
    print(f"Public key:   {info['public_key']}")


if __name__ == "__main__":
    main()
