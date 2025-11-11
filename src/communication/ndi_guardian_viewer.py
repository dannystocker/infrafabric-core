#!/usr/bin/env python3
# Copyright (c) 2025 Danny Stocker
# SPDX-License-Identifier: MIT
#
# InfraFabric - NDI Guardian Viewer
# Source: https://github.com/dannystocker/infrafabric
# Licensed under the MIT License.

"""
NDI Guardian Viewer - Subscribe to NDI streams and verify witness provenance

Philosophy Grounding:
- Wu Lun (五倫) Relationship: 父子 (Parent-Child) — Viewer consumes stream created by publisher
- IF.ground Principle 1: Ground in Observable Artifacts — Verify every frame's hash
- IF.witness: Validate provenance (Ed25519 signature verification)
- IF.TTT: Traceable (hash chain continuity), Transparent (metadata visible), Trustworthy (crypto verified)

Architecture:
1. Subscribe to NDI streams (IF.witness.* naming convention)
2. Extract witness metadata from each frame
3. Verify Ed25519 signatures in real-time
4. Validate hash chain continuity
5. Display stream with provenance overlay

Verification Process:
- Check signature: Ed25519.verify(public_key, metadata, signature)
- Check hash: SHA-256(frame_data + metadata) == content_hash
- Check chain: prev_hash[N] == content_hash[N-1]
"""

import hashlib
import json
import base64
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


# Mock NDI interface (replace with real ndi-python when SDK available)
class MockNDIReceiver:
    """Mock NDI receiver for testing without SDK

    Replace with real NDI SDK:
    from NDIlib import NDIlib_recv_create, NDIlib_recv_capture_v2
    """

    def __init__(self, stream_name: str):
        self.stream_name = stream_name
        self.is_running = False
        self.frame_queue = []  # Simulated frame buffer
        print(f"[MockNDI] Created receiver: {stream_name}")

    def start(self):
        self.is_running = True
        print(f"[MockNDI] Started receiver: {self.stream_name}")

    def receive_frame(self) -> Optional[Tuple[bytes, Dict[str, Any]]]:
        """Receive video frame with metadata

        Returns:
            (frame_data, metadata) tuple or None if no frame available
        """
        if not self.is_running:
            raise RuntimeError("Receiver not started")

        if self.frame_queue:
            return self.frame_queue.pop(0)
        return None

    def inject_test_frame(self, frame_data: bytes, metadata: Dict[str, Any]):
        """Inject test frame into queue (for testing)"""
        self.frame_queue.append((frame_data, metadata))

    def stop(self):
        self.is_running = False
        print(f"[MockNDI] Stopped receiver: {self.stream_name}")


class WitnessVerifier:
    """Verify witness provenance (signatures + hash chains)"""

    GENESIS_HASH = "0" * 64  # SHA-256 zero hash

    def __init__(self):
        self.last_content_hash = None
        self.verification_stats = {
            "frames_verified": 0,
            "signature_failures": 0,
            "hash_failures": 0,
            "chain_failures": 0
        }

    def verify_signature(
        self,
        metadata: Dict[str, Any],
        signature_hex: str,
        public_key_base64: str
    ) -> bool:
        """Verify Ed25519 signature on metadata

        Args:
            metadata: Metadata dict (without signature/public_key fields)
            signature_hex: Hex-encoded signature
            public_key_base64: Base64-encoded public key

        Returns:
            True if signature valid, False otherwise
        """
        try:
            # Reconstruct public key
            public_key_bytes = base64.b64decode(public_key_base64)
            public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)

            # Reconstruct canonical metadata (what was signed)
            metadata_to_verify = {k: v for k, v in metadata.items()
                                  if k not in ('signature', 'public_key')}
            canonical = json.dumps(metadata_to_verify, sort_keys=True)

            # Verify signature
            signature_bytes = bytes.fromhex(signature_hex)
            public_key.verify(signature_bytes, canonical.encode('utf-8'))
            return True

        except InvalidSignature:
            return False
        except Exception as e:
            print(f"[ERROR] Signature verification error: {e}")
            return False

    def verify_content_hash(
        self,
        frame_data: bytes,
        metadata: Dict[str, Any],
        claimed_hash: str
    ) -> bool:
        """Verify content hash matches frame + metadata

        Args:
            frame_data: Raw frame bytes
            metadata: Frame metadata (without signature/public_key)
            claimed_hash: Hash from metadata

        Returns:
            True if hash matches, False otherwise
        """
        try:
            hasher = hashlib.sha256()
            hasher.update(frame_data)

            # Hash metadata (exclude signature fields)
            metadata_to_hash = {k: v for k, v in metadata.items()
                                if k not in ('signature', 'public_key', 'content_hash')}
            metadata_json = json.dumps(metadata_to_hash, sort_keys=True)
            hasher.update(metadata_json.encode('utf-8'))

            computed_hash = hasher.hexdigest()
            return computed_hash == claimed_hash

        except Exception as e:
            print(f"[ERROR] Hash verification error: {e}")
            return False

    def verify_hash_chain(
        self,
        metadata: Dict[str, Any],
        is_genesis: bool = False
    ) -> bool:
        """Verify hash chain continuity

        Args:
            metadata: Frame metadata with chain_state
            is_genesis: True if this is the first frame

        Returns:
            True if chain valid, False otherwise
        """
        try:
            chain_state = metadata.get("chain_state", {})
            prev_hash = chain_state.get("prev_hash")
            content_hash = metadata.get("content_hash")

            if is_genesis:
                # Genesis frame: prev_hash should be all zeros
                if prev_hash != self.GENESIS_HASH:
                    print(f"[WARN] Genesis frame has non-zero prev_hash: {prev_hash[:16]}...")
                    return False
            else:
                # Non-genesis: prev_hash should match last frame's content_hash
                if prev_hash != self.last_content_hash:
                    print(f"[WARN] Chain break: prev_hash {prev_hash[:16]}... != last_hash {self.last_content_hash[:16] if self.last_content_hash else 'None'}...")
                    return False

            # Update last hash for next frame
            self.last_content_hash = content_hash
            return True

        except Exception as e:
            print(f"[ERROR] Chain verification error: {e}")
            return False

    def verify_frame(
        self,
        frame_data: bytes,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify complete frame (signature + hash + chain)

        Args:
            frame_data: Raw frame bytes
            metadata: Frame metadata

        Returns:
            Verification result dict with pass/fail status
        """
        frame_number = metadata.get("frame_number", "?")
        is_genesis = (frame_number == 1)

        result = {
            "frame_number": frame_number,
            "timestamp": metadata.get("timestamp"),
            "signature_valid": False,
            "hash_valid": False,
            "chain_valid": False,
            "overall_valid": False
        }

        # Verify signature
        signature = metadata.get("signature")
        public_key = metadata.get("public_key")
        if signature and public_key:
            result["signature_valid"] = self.verify_signature(metadata, signature, public_key)
            if not result["signature_valid"]:
                self.verification_stats["signature_failures"] += 1
        else:
            print(f"[ERROR] Frame {frame_number} missing signature or public_key")

        # Verify content hash
        content_hash = metadata.get("content_hash")
        if content_hash:
            result["hash_valid"] = self.verify_content_hash(frame_data, metadata, content_hash)
            if not result["hash_valid"]:
                self.verification_stats["hash_failures"] += 1
        else:
            print(f"[ERROR] Frame {frame_number} missing content_hash")

        # Verify hash chain
        result["chain_valid"] = self.verify_hash_chain(metadata, is_genesis)
        if not result["chain_valid"]:
            self.verification_stats["chain_failures"] += 1

        # Overall verdict
        result["overall_valid"] = (
            result["signature_valid"] and
            result["hash_valid"] and
            result["chain_valid"]
        )

        if result["overall_valid"]:
            self.verification_stats["frames_verified"] += 1

        return result

    def get_stats(self) -> Dict[str, int]:
        """Get verification statistics"""
        return self.verification_stats.copy()


class NDIGuardianViewer:
    """NDI Guardian Viewer - Subscribe and verify witness streams

    Usage:
        viewer = NDIGuardianViewer(stream_name="IF.witness.yologuard.01")
        viewer.start()

        while True:
            frame_info = viewer.receive_and_verify()
            if frame_info:
                display_frame(frame_info)

        viewer.stop()
    """

    def __init__(self, stream_name: str, use_mock: bool = True):
        """Initialize NDI guardian viewer

        Args:
            stream_name: NDI stream name to subscribe to
            use_mock: Use mock NDI receiver (True) or real SDK (False)
        """
        self.stream_name = stream_name
        self.verifier = WitnessVerifier()

        # Create NDI receiver (mock or real)
        if use_mock:
            self.ndi_receiver = MockNDIReceiver(stream_name)
        else:
            # Real NDI SDK integration point
            raise NotImplementedError("Real NDI SDK not available - install ndi-python")

        self.started = False

    def start(self):
        """Start receiving NDI stream"""
        self.ndi_receiver.start()
        self.started = True

    def receive_and_verify(self) -> Optional[Dict[str, Any]]:
        """Receive frame and verify provenance

        Returns:
            Frame info dict with verification results, or None if no frame
        """
        if not self.started:
            raise RuntimeError("Viewer not started - call start() first")

        frame_tuple = self.ndi_receiver.receive_frame()
        if frame_tuple is None:
            return None

        frame_data, metadata = frame_tuple

        # Verify frame
        verification_result = self.verifier.verify_frame(frame_data, metadata)

        # Build frame info
        frame_info = {
            "frame_data": frame_data,
            "metadata": metadata,
            "verification": verification_result,
            "scan_metadata": metadata.get("scan_metadata", {})
        }

        return frame_info

    def stop(self):
        """Stop receiving NDI stream"""
        self.ndi_receiver.stop()
        self.started = False

    def get_verification_stats(self) -> Dict[str, int]:
        """Get verification statistics"""
        return self.verifier.get_stats()


def main():
    """Example usage: View and verify NDI witness stream"""
    import argparse
    import time

    parser = argparse.ArgumentParser(description="NDI Guardian Viewer")
    parser.add_argument('--stream-name', default='IF.witness.yologuard.01',
                        help='NDI stream name to view')
    args = parser.parse_args()

    print("=" * 80)
    print("NDI Guardian Viewer - IF.witness Verification")
    print("=" * 80)

    viewer = NDIGuardianViewer(stream_name=args.stream_name)
    viewer.start()
    print(f"Subscribed to: {args.stream_name}")
    print("\nWaiting for frames (mock mode - use with publisher)...")
    print("Press Ctrl+C to stop\n")

    try:
        frame_count = 0
        while True:
            frame_info = viewer.receive_and_verify()

            if frame_info:
                frame_count += 1
                ver = frame_info["verification"]
                scan = frame_info["scan_metadata"]

                # Display verification result
                status = "✓ VERIFIED" if ver["overall_valid"] else "✗ FAILED"
                print(f"\nFrame {ver['frame_number']}: {status}")
                print(f"  Timestamp:       {ver['timestamp']}")
                print(f"  Signature valid: {ver['signature_valid']}")
                print(f"  Hash valid:      {ver['hash_valid']}")
                print(f"  Chain valid:     {ver['chain_valid']}")

                if scan:
                    print(f"  Scan result:     {scan.get('file', '?')}:{scan.get('line', '?')}")
                    print(f"                   {scan.get('pattern', '?')} [{scan.get('severity', '?')}]")

            time.sleep(0.1)  # Polling interval

    except KeyboardInterrupt:
        print("\n\nStopping viewer...")

    viewer.stop()

    # Print statistics
    stats = viewer.get_verification_stats()
    print("\n" + "=" * 80)
    print("Verification Statistics")
    print("=" * 80)
    print(f"Frames verified:      {stats['frames_verified']}")
    print(f"Signature failures:   {stats['signature_failures']}")
    print(f"Hash failures:        {stats['hash_failures']}")
    print(f"Chain failures:       {stats['chain_failures']}")

    total_frames = (
        stats['frames_verified'] +
        stats['signature_failures'] +
        stats['hash_failures'] +
        stats['chain_failures']
    )
    if total_frames > 0:
        success_rate = (stats['frames_verified'] / total_frames) * 100
        print(f"\nSuccess rate:         {success_rate:.1f}%")


if __name__ == "__main__":
    main()
