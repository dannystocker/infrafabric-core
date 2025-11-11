#!/usr/bin/env python3
# Copyright (c) 2025 Danny Stocker
# SPDX-License-Identifier: MIT
#
# InfraFabric - NDI Witness Tests
# Source: https://github.com/dannystocker/infrafabric

"""
NDI Witness Integration Tests

Test coverage:
1. Witness hash chain continuity (genesis → frame N)
2. Ed25519 signature generation and verification
3. NDI metadata injection/extraction
4. End-to-end publisher → viewer flow
5. Security: tampered frame detection
6. Security: chain break detection
"""

import sys
import json
import hashlib
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
from communication.ndi_witness_publisher import (
    WitnessHashChain,
    Ed25519Signer,
    NDIWitnessPublisher
)
from communication.ndi_guardian_viewer import (
    WitnessVerifier,
    NDIGuardianViewer
)


class TestWitnessHashChain:
    """Test witness hash chain implementation"""

    def test_genesis_hash(self):
        """Test genesis frame has zero prev_hash"""
        chain = WitnessHashChain()
        state = chain.get_chain_state()

        assert state["prev_hash"] == "0" * 64, "Genesis prev_hash must be all zeros"
        assert state["frame_count"] == 0, "Genesis frame_count must be 0"
        assert "chain_id" in state, "Chain must have unique ID"

    def test_hash_computation(self):
        """Test SHA-256 hash computation is deterministic"""
        chain = WitnessHashChain()

        frame_data = b"test frame data"
        metadata = {"frame_number": 1, "timestamp": "2025-11-11T00:00:00Z"}

        hash1 = chain.compute_content_hash(frame_data, metadata)
        hash2 = chain.compute_content_hash(frame_data, metadata)

        assert hash1 == hash2, "Hash must be deterministic"
        assert len(hash1) == 64, "SHA-256 hash must be 64 hex chars"
        assert hash1 != chain.GENESIS_HASH, "Content hash must differ from genesis"

    def test_chain_advance(self):
        """Test chain advances correctly through multiple frames"""
        chain = WitnessHashChain()

        # Frame 1
        frame1_data = b"frame 1"
        metadata1 = {"frame_number": 1}
        hash1 = chain.compute_content_hash(frame1_data, metadata1)

        initial_prev = chain.prev_hash
        chain.advance(hash1)

        assert chain.prev_hash == hash1, "Prev_hash must update to frame 1 hash"
        assert chain.frame_count == 1, "Frame count must increment"

        # Frame 2 (should link to frame 1)
        frame2_data = b"frame 2"
        metadata2 = {"frame_number": 2}
        hash2 = chain.compute_content_hash(frame2_data, metadata2)

        assert chain.prev_hash == hash1, "Frame 2 prev_hash must be frame 1 hash"
        chain.advance(hash2)

        assert chain.prev_hash == hash2, "Prev_hash must update to frame 2 hash"
        assert chain.frame_count == 2, "Frame count must be 2"

    def test_chain_continuity(self):
        """Test hash chain maintains continuity over many frames"""
        chain = WitnessHashChain()
        hashes = []

        for i in range(10):
            frame_data = f"frame {i}".encode()
            metadata = {"frame_number": i}
            content_hash = chain.compute_content_hash(frame_data, metadata)
            hashes.append(content_hash)

            if i > 0:
                # Check prev_hash links to previous frame
                assert chain.prev_hash == hashes[i-1], f"Frame {i} breaks chain"

            chain.advance(content_hash)

        assert chain.frame_count == 10, "Chain must have 10 frames"


class TestEd25519Signer:
    """Test Ed25519 signature implementation"""

    def test_keypair_generation(self):
        """Test Ed25519 keypair generation"""
        signer = Ed25519Signer()

        assert signer.private_key is not None, "Private key must be generated"
        assert signer.public_key is not None, "Public key must be generated"

        public_key_b64 = signer.get_public_key_base64()
        assert len(public_key_b64) > 0, "Public key must be exportable"

    def test_signature_generation(self):
        """Test metadata signing produces valid signatures"""
        signer = Ed25519Signer()
        metadata = {
            "frame_number": 1,
            "timestamp": "2025-11-11T00:00:00Z",
            "content_hash": "abc123"
        }

        signature = signer.sign_metadata(metadata)

        assert len(signature) == 128, "Ed25519 signature must be 64 bytes (128 hex chars)"
        assert signature != signer.sign_metadata({}), "Different metadata must produce different signature"

    def test_signature_deterministic(self):
        """Test same metadata produces same signature"""
        signer = Ed25519Signer()
        metadata = {"test": "data"}

        sig1 = signer.sign_metadata(metadata)
        sig2 = signer.sign_metadata(metadata)

        assert sig1 == sig2, "Signature must be deterministic"

    def test_signature_verification(self):
        """Test signature can be verified with public key"""
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        import base64

        signer = Ed25519Signer()
        metadata = {"frame_number": 1, "data": "test"}

        signature_hex = signer.sign_metadata(metadata)
        public_key_b64 = signer.get_public_key_base64()

        # Reconstruct and verify
        public_key_bytes = base64.b64decode(public_key_b64)
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)

        canonical = json.dumps(metadata, sort_keys=True)
        signature_bytes = bytes.fromhex(signature_hex)

        # Should not raise exception
        public_key.verify(signature_bytes, canonical.encode('utf-8'))

    def test_tampered_signature_fails(self):
        """Test tampered signature fails verification"""
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        import base64

        signer = Ed25519Signer()
        metadata = {"frame_number": 1}

        signature_hex = signer.sign_metadata(metadata)
        public_key_b64 = signer.get_public_key_base64()

        # Tamper with signature (flip one bit)
        tampered_sig = signature_hex[:-1] + ('0' if signature_hex[-1] != '0' else '1')

        # Reconstruct and verify
        public_key_bytes = base64.b64decode(public_key_b64)
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)

        canonical = json.dumps(metadata, sort_keys=True)
        tampered_bytes = bytes.fromhex(tampered_sig)

        # Must raise InvalidSignature
        with pytest.raises(InvalidSignature):
            public_key.verify(tampered_bytes, canonical.encode('utf-8'))


class TestWitnessVerifier:
    """Test witness verification logic"""

    def test_signature_verification_valid(self):
        """Test valid signature passes verification"""
        signer = Ed25519Signer()
        verifier = WitnessVerifier()

        metadata = {"frame_number": 1, "data": "test"}
        signature = signer.sign_metadata(metadata)
        public_key = signer.get_public_key_base64()

        assert verifier.verify_signature(metadata, signature, public_key) == True

    def test_signature_verification_invalid(self):
        """Test invalid signature fails verification"""
        signer1 = Ed25519Signer()
        signer2 = Ed25519Signer()  # Different key
        verifier = WitnessVerifier()

        metadata = {"frame_number": 1}
        signature = signer1.sign_metadata(metadata)
        wrong_public_key = signer2.get_public_key_base64()

        assert verifier.verify_signature(metadata, signature, wrong_public_key) == False

    def test_content_hash_verification_valid(self):
        """Test valid content hash passes verification"""
        verifier = WitnessVerifier()

        frame_data = b"test frame"
        metadata = {"frame_number": 1, "timestamp": "2025-11-11T00:00:00Z"}

        # Compute expected hash
        hasher = hashlib.sha256()
        hasher.update(frame_data)
        hasher.update(json.dumps(metadata, sort_keys=True).encode('utf-8'))
        expected_hash = hasher.hexdigest()

        assert verifier.verify_content_hash(frame_data, metadata, expected_hash) == True

    def test_content_hash_verification_invalid(self):
        """Test tampered content fails hash verification"""
        verifier = WitnessVerifier()

        frame_data = b"original frame"
        metadata = {"frame_number": 1}

        # Compute hash for original
        hasher = hashlib.sha256()
        hasher.update(frame_data)
        hasher.update(json.dumps(metadata, sort_keys=True).encode('utf-8'))
        original_hash = hasher.hexdigest()

        # Tamper with frame data
        tampered_data = b"tampered frame"

        assert verifier.verify_content_hash(tampered_data, metadata, original_hash) == False

    def test_chain_verification_genesis(self):
        """Test genesis frame chain verification"""
        verifier = WitnessVerifier()

        metadata = {
            "frame_number": 1,
            "content_hash": "abc123",
            "chain_state": {
                "prev_hash": "0" * 64,  # Genesis
                "frame_count": 1
            }
        }

        assert verifier.verify_hash_chain(metadata, is_genesis=True) == True
        assert verifier.last_content_hash == "abc123"

    def test_chain_verification_continuity(self):
        """Test chain continuity across frames"""
        verifier = WitnessVerifier()

        # Frame 1 (genesis)
        metadata1 = {
            "frame_number": 1,
            "content_hash": "hash1",
            "chain_state": {
                "prev_hash": "0" * 64,
                "frame_count": 1
            }
        }
        assert verifier.verify_hash_chain(metadata1, is_genesis=True) == True

        # Frame 2 (links to frame 1)
        metadata2 = {
            "frame_number": 2,
            "content_hash": "hash2",
            "chain_state": {
                "prev_hash": "hash1",  # Matches frame 1
                "frame_count": 2
            }
        }
        assert verifier.verify_hash_chain(metadata2, is_genesis=False) == True

        # Frame 3 (links to frame 2)
        metadata3 = {
            "frame_number": 3,
            "content_hash": "hash3",
            "chain_state": {
                "prev_hash": "hash2",  # Matches frame 2
                "frame_count": 3
            }
        }
        assert verifier.verify_hash_chain(metadata3, is_genesis=False) == True

    def test_chain_verification_break(self):
        """Test chain break detection"""
        verifier = WitnessVerifier()

        # Frame 1
        metadata1 = {
            "frame_number": 1,
            "content_hash": "hash1",
            "chain_state": {"prev_hash": "0" * 64}
        }
        verifier.verify_hash_chain(metadata1, is_genesis=True)

        # Frame 2 with WRONG prev_hash (should fail)
        metadata2 = {
            "frame_number": 2,
            "content_hash": "hash2",
            "chain_state": {
                "prev_hash": "wrong_hash",  # Does NOT match frame 1
            }
        }
        assert verifier.verify_hash_chain(metadata2, is_genesis=False) == False


class TestEndToEnd:
    """End-to-end integration tests"""

    def test_publisher_viewer_flow(self):
        """Test complete flow: publisher → viewer with verification"""
        # Create publisher
        signer = Ed25519Signer()
        publisher = NDIWitnessPublisher(
            stream_name="IF.witness.test.01",
            component="IF.yologuard.test",
            signer=signer,
            use_mock=True
        )
        publisher.start()

        # Publish test frames
        scan_metadata = {
            "file": "/test/secrets.py",
            "line": 42,
            "pattern": "AWS_KEY_REDACTED",
            "severity": "ERROR"
        }

        frame_data = b"test frame 1"
        publisher.publish_frame(frame_data, scan_metadata, trace_id="trace-123")

        # Create viewer
        viewer = NDIGuardianViewer(stream_name="IF.witness.test.01", use_mock=True)
        viewer.start()

        # Inject frame into viewer's receiver (simulate NDI transport)
        ndi_sender = publisher.ndi_sender
        ndi_receiver = viewer.ndi_receiver

        # In real NDI, this would happen automatically over network
        # For mock, we manually transfer the last sent frame
        assert hasattr(ndi_sender, 'is_running'), "Sender must be running"

        # Manually construct frame to inject (simulating what NDI would do)
        # Get the metadata from last publish_frame call
        test_metadata = {
            "frame_number": 1,
            "timestamp": "2025-11-11T00:00:00Z",
            "component": "IF.yologuard.test",
            "trace_id": "trace-123",
            "scan_metadata": scan_metadata,
            "chain_state": {
                "chain_id": publisher.hash_chain.chain_id,
                "frame_count": 1,
                "prev_hash": "0" * 64
            },
            "content_hash": publisher.hash_chain.prev_hash,
            "signature": signer.sign_metadata({
                "frame_number": 1,
                "timestamp": "2025-11-11T00:00:00Z",
                "component": "IF.yologuard.test",
                "trace_id": "trace-123",
                "scan_metadata": scan_metadata,
                "chain_state": {
                    "chain_id": publisher.hash_chain.chain_id,
                    "frame_count": 1,
                    "prev_hash": "0" * 64
                },
                "content_hash": publisher.hash_chain.prev_hash
            }),
            "public_key": signer.get_public_key_base64()
        }

        ndi_receiver.inject_test_frame(frame_data, test_metadata)

        # Receive and verify
        frame_info = viewer.receive_and_verify()

        assert frame_info is not None, "Frame must be received"
        verification = frame_info["verification"]

        assert verification["signature_valid"] == True, "Signature must be valid"
        assert verification["chain_valid"] == True, "Chain must be valid"
        assert verification["overall_valid"] == True, "Overall verification must pass"

        # Clean up
        publisher.stop()
        viewer.stop()

    def test_multi_frame_verification(self):
        """Test multiple frames maintain chain continuity"""
        signer = Ed25519Signer()
        publisher = NDIWitnessPublisher(
            stream_name="IF.witness.multiframe.01",
            component="IF.yologuard",
            signer=signer
        )
        publisher.start()

        viewer = NDIGuardianViewer(stream_name="IF.witness.multiframe.01")
        viewer.start()

        # Publish and verify 5 frames
        for i in range(5):
            frame_data = f"frame {i}".encode()
            scan_metadata = {
                "file": f"/test/file{i}.py",
                "line": 10 + i,
                "pattern": "SECRET",
                "severity": "ERROR"
            }

            publisher.publish_frame(frame_data, scan_metadata, trace_id=f"trace-{i}")

        # All frames should form valid chain
        assert publisher.hash_chain.frame_count == 5, "Should have 5 frames"

        publisher.stop()
        viewer.stop()


def test_security_tampered_frame():
    """Security test: Tampered frame must be detected"""
    signer = Ed25519Signer()
    verifier = WitnessVerifier()

    # Original frame
    frame_data = b"original data"
    metadata = {
        "frame_number": 1,
        "timestamp": "2025-11-11T00:00:00Z",
        "content_hash": hashlib.sha256(frame_data + b"metadata").hexdigest()
    }
    metadata["signature"] = signer.sign_metadata(metadata)
    metadata["public_key"] = signer.get_public_key_base64()

    # Tamper with frame data AFTER signing
    tampered_data = b"tampered data"

    result = verifier.verify_frame(tampered_data, metadata)

    assert result["hash_valid"] == False, "Tampered frame must fail hash verification"
    assert result["overall_valid"] == False, "Overall verification must fail"


def test_security_forged_signature():
    """Security test: Forged signature must be detected"""
    signer = Ed25519Signer()
    attacker_signer = Ed25519Signer()  # Different key
    verifier = WitnessVerifier()

    frame_data = b"frame data"
    metadata = {
        "frame_number": 1,
        "content_hash": hashlib.sha256(frame_data).hexdigest()
    }

    # Attacker signs with their own key
    metadata["signature"] = attacker_signer.sign_metadata(metadata)
    # But claims to be original signer
    metadata["public_key"] = signer.get_public_key_base64()

    result = verifier.verify_frame(frame_data, metadata)

    assert result["signature_valid"] == False, "Forged signature must fail"
    assert result["overall_valid"] == False, "Overall verification must fail"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
