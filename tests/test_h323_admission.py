"""
Unit Tests for H.323 Admission Control (Kantian Policy Gates)

Tests the four categorical imperatives:
1. Authenticity (Ed25519 signature verification)
2. Anti-Sybil (guardian registry whitelist)
3. PII Protection (ESCALATE call constraint)
4. Fairness (bandwidth quota enforcement)

Author: InfraFabric Project
License: CC BY 4.0
Last Updated: 2025-11-11
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from communication.h323_gatekeeper import (
    H323Gatekeeper,
    AdmissionRequest,
    AdmissionResponse,
    CallType,
    RejectReason,
    GuardianRegistry,
    KantianPolicyEngine,
    SignatureVerifier,
    WitnessLogger,
    generate_test_keypair,
    sign_admission_request,
)


class TestEd25519SignatureVerification(unittest.TestCase):
    """Test Gate 1: Authenticity (Ed25519 signature verification)"""

    def setUp(self):
        """Generate test keypair"""
        self.private_key, self.public_key = generate_test_keypair()
        self.verifier = SignatureVerifier()

    def test_valid_signature_passes(self):
        """✅ Valid signature should pass verification"""
        # Create admission request
        arq = AdmissionRequest(
            terminal_id="if://guardian/technical",
            call_id="test-call-001",
            call_type=CallType.ROUTINE,
            bandwidth_bps=5_000_000,
            has_pii=False,
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature="",  # Will be filled
            public_key=self.public_key
        )

        # Sign request
        arq.signature = sign_admission_request(arq, self.private_key)

        # Verify signature
        canonical = arq.to_canonical()
        result = self.verifier.verify_signature(canonical, arq.signature, self.public_key)

        self.assertTrue(result, "Valid signature should pass verification")

    def test_invalid_signature_fails(self):
        """❌ Invalid signature should fail verification"""
        arq = AdmissionRequest(
            terminal_id="if://guardian/technical",
            call_id="test-call-002",
            call_type=CallType.ROUTINE,
            bandwidth_bps=5_000_000,
            has_pii=False,
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature="invalid_signature_hex",
            public_key=self.public_key
        )

        canonical = arq.to_canonical()
        result = self.verifier.verify_signature(canonical, arq.signature, self.public_key)

        self.assertFalse(result, "Invalid signature should fail verification")

    def test_wrong_public_key_fails(self):
        """❌ Signature with wrong public key should fail"""
        # Generate two different keypairs
        private_key_1, public_key_1 = generate_test_keypair()
        _, public_key_2 = generate_test_keypair()

        arq = AdmissionRequest(
            terminal_id="if://guardian/technical",
            call_id="test-call-003",
            call_type=CallType.ROUTINE,
            bandwidth_bps=5_000_000,
            has_pii=False,
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature="",
            public_key=public_key_1
        )

        # Sign with private_key_1
        arq.signature = sign_admission_request(arq, private_key_1)

        # Verify with public_key_2 (wrong key)
        canonical = arq.to_canonical()
        result = self.verifier.verify_signature(canonical, arq.signature, public_key_2)

        self.assertFalse(result, "Signature with wrong public key should fail")


class TestGuardianRegistry(unittest.TestCase):
    """Test Gate 2: Anti-Sybil (guardian registry)"""

    def setUp(self):
        """Create test registry"""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = Path(self.temp_dir) / "test-registry.yaml"

        # Create test registry
        registry_yaml = """
guardians:
  - terminal_id: "if://guardian/technical"
    public_key: "AAAC3NzaC1lZDI1NTE5AAAAIOMq"
    role: "Technical Guardian"
    bandwidth_quota_bps: 10000000
    registered_at: "2025-11-11T00:00:00Z"
    status: "active"

  - terminal_id: "if://guardian/civic"
    public_key: "BBBD4OzaC2lZDI1NTE5AAAAIPNr"
    role: "Civic Guardian"
    bandwidth_quota_bps: 10000000
    registered_at: "2025-11-11T00:00:00Z"
    status: "active"

  - terminal_id: "if://guardian/suspended"
    public_key: "CCCE5PzaC3lZDI1NTE5AAAAIQOs"
    role: "Suspended Guardian"
    bandwidth_quota_bps: 10000000
    registered_at: "2025-11-11T00:00:00Z"
    status: "suspended"
"""
        with open(self.registry_path, 'w') as f:
            f.write(registry_yaml)

        self.registry = GuardianRegistry(self.registry_path)

    def tearDown(self):
        """Clean up temp directory"""
        shutil.rmtree(self.temp_dir)

    def test_registered_guardian_accepted(self):
        """✅ Registered guardian should be accepted"""
        result = self.registry.is_registered("if://guardian/technical")
        self.assertTrue(result, "Registered guardian should be accepted")

    def test_unregistered_guardian_rejected(self):
        """❌ Unregistered guardian should be rejected"""
        result = self.registry.is_registered("if://guardian/unknown")
        self.assertFalse(result, "Unregistered guardian should be rejected")

    def test_suspended_guardian_rejected(self):
        """❌ Suspended guardian should be rejected"""
        result = self.registry.is_registered("if://guardian/suspended")
        self.assertFalse(result, "Suspended guardian should be rejected")

    def test_get_public_key(self):
        """✅ Should retrieve guardian's public key"""
        key = self.registry.get_public_key("if://guardian/technical")
        self.assertEqual(key, "AAAC3NzaC1lZDI1NTE5AAAAIOMq")

    def test_get_bandwidth_quota(self):
        """✅ Should retrieve guardian's bandwidth quota"""
        quota = self.registry.get_bandwidth_quota("if://guardian/technical")
        self.assertEqual(quota, 10_000_000)


class TestKantianPolicyGates(unittest.TestCase):
    """Test all four Kantian policy gates"""

    def setUp(self):
        """Setup gatekeeper with test registry"""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = Path(self.temp_dir) / "test-registry.yaml"
        self.witness_dir = Path(self.temp_dir) / "witness"

        # Generate test keypair
        self.private_key, self.public_key = generate_test_keypair()

        # Create test registry with our public key
        registry_yaml = f"""
guardians:
  - terminal_id: "if://guardian/technical"
    public_key: "{self.public_key}"
    role: "Technical Guardian"
    bandwidth_quota_bps: 10000000
    registered_at: "2025-11-11T00:00:00Z"
    status: "active"
"""
        with open(self.registry_path, 'w') as f:
            f.write(registry_yaml)

        self.registry = GuardianRegistry(self.registry_path)
        self.verifier = SignatureVerifier()
        self.policy_engine = KantianPolicyEngine(self.registry, self.verifier)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def _create_signed_arq(
        self,
        terminal_id: str = "if://guardian/technical",
        call_type: CallType = CallType.ROUTINE,
        bandwidth_bps: int = 5_000_000,
        has_pii: bool = False,
        public_key: str = None
    ) -> AdmissionRequest:
        """Helper to create signed ARQ"""
        arq = AdmissionRequest(
            terminal_id=terminal_id,
            call_id=f"test-call-{datetime.now().timestamp()}",
            call_type=call_type,
            bandwidth_bps=bandwidth_bps,
            has_pii=has_pii,
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature="",
            public_key=public_key or self.public_key
        )
        arq.signature = sign_admission_request(arq, self.private_key)
        return arq

    def test_all_gates_pass_returns_acf(self):
        """✅ All gates pass → ACF (Admission Confirm)"""
        arq = self._create_signed_arq()
        response = self.policy_engine.evaluate_admission(arq)

        self.assertTrue(response.confirmed, "Should return ACF")
        self.assertIsNone(response.reject_reason, "No reject reason")
        self.assertEqual(response.mcu_address, "if://service/guard/mcu:1720")

    def test_gate1_invalid_signature_rejects(self):
        """❌ Gate 1 fail: Invalid signature → ARJ (INVALID_SIGNATURE)"""
        arq = self._create_signed_arq()
        arq.signature = "invalid_signature_hex"  # Tamper with signature

        response = self.policy_engine.evaluate_admission(arq)

        self.assertFalse(response.confirmed, "Should return ARJ")
        self.assertEqual(response.reject_reason, RejectReason.INVALID_SIGNATURE)

    def test_gate2_unregistered_guardian_rejects(self):
        """❌ Gate 2 fail: Unregistered guardian → ARJ (NOT_REGISTERED)"""
        arq = self._create_signed_arq(terminal_id="if://guardian/unknown")

        response = self.policy_engine.evaluate_admission(arq)

        self.assertFalse(response.confirmed, "Should return ARJ")
        self.assertEqual(response.reject_reason, RejectReason.NOT_REGISTERED)

    def test_gate2_public_key_mismatch_rejects(self):
        """❌ Gate 2.1 fail: Public key mismatch → ARJ (INVALID_SIGNATURE)"""
        _, wrong_public_key = generate_test_keypair()
        arq = self._create_signed_arq(public_key=wrong_public_key)

        response = self.policy_engine.evaluate_admission(arq)

        self.assertFalse(response.confirmed, "Should return ARJ")
        self.assertEqual(response.reject_reason, RejectReason.INVALID_SIGNATURE)

    def test_gate3_pii_in_escalate_rejects(self):
        """❌ Gate 3 fail: PII in ESCALATE call → ARJ (PII_POLICY_VIOLATION)"""
        arq = self._create_signed_arq(
            call_type=CallType.ESCALATE,
            has_pii=True
        )

        response = self.policy_engine.evaluate_admission(arq)

        self.assertFalse(response.confirmed, "Should return ARJ")
        self.assertEqual(response.reject_reason, RejectReason.PII_POLICY_VIOLATION)

    def test_gate3_pii_in_routine_allowed(self):
        """✅ Gate 3 pass: PII in ROUTINE call allowed"""
        arq = self._create_signed_arq(
            call_type=CallType.ROUTINE,
            has_pii=True
        )

        response = self.policy_engine.evaluate_admission(arq)

        self.assertTrue(response.confirmed, "PII allowed in ROUTINE calls")

    def test_gate4_bandwidth_exceeded_rejects(self):
        """❌ Gate 4 fail: Bandwidth > quota → ARJ (BANDWIDTH_EXCEEDED)"""
        arq = self._create_signed_arq(
            bandwidth_bps=15_000_000  # Exceeds 10 Mbps quota
        )

        response = self.policy_engine.evaluate_admission(arq)

        self.assertFalse(response.confirmed, "Should return ARJ")
        self.assertEqual(response.reject_reason, RejectReason.BANDWIDTH_EXCEEDED)

    def test_gate4_bandwidth_at_quota_allowed(self):
        """✅ Gate 4 pass: Bandwidth exactly at quota allowed"""
        arq = self._create_signed_arq(
            bandwidth_bps=10_000_000  # Exactly at quota
        )

        response = self.policy_engine.evaluate_admission(arq)

        self.assertTrue(response.confirmed, "Bandwidth at quota should be allowed")


class TestWitnessLogging(unittest.TestCase):
    """Test IF.witness audit logging"""

    def setUp(self):
        """Setup witness logger"""
        self.temp_dir = tempfile.mkdtemp()
        self.witness_dir = Path(self.temp_dir) / "witness"
        self.witness = WitnessLogger(self.witness_dir)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_log_admission_request(self):
        """✅ Should log ARQ to witness"""
        arq = AdmissionRequest(
            terminal_id="if://guardian/technical",
            call_id="test-call-001",
            call_type=CallType.ROUTINE,
            bandwidth_bps=5_000_000,
            has_pii=False,
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature="test_signature_hex",
            public_key="test_public_key"
        )

        self.witness.log_admission_request(arq)

        # Check log file created
        log_files = list(self.witness_dir.glob("h323_ras_*.jsonl"))
        self.assertEqual(len(log_files), 1, "Log file should be created")

        # Check log content
        with open(log_files[0], 'r') as f:
            import json
            log_entry = json.loads(f.read())

        self.assertEqual(log_entry["msg_type"], "ARQ")
        self.assertEqual(log_entry["data"]["terminal_id"], "if://guardian/technical")
        self.assertIn("hash", log_entry, "Log should have content hash")

    def test_log_admission_response(self):
        """✅ Should log ACF/ARJ to witness"""
        response = AdmissionResponse(
            call_id="test-call-001",
            terminal_id="if://guardian/technical",
            confirmed=False,
            reject_reason=RejectReason.INVALID_SIGNATURE
        )

        self.witness.log_admission_response(response)

        # Check log file
        log_files = list(self.witness_dir.glob("h323_ras_*.jsonl"))
        self.assertEqual(len(log_files), 1)

        with open(log_files[0], 'r') as f:
            import json
            log_entry = json.loads(f.read())

        self.assertEqual(log_entry["msg_type"], "ARJ")
        self.assertEqual(log_entry["data"]["reject_reason"], "INVALID_SIGNATURE")


class TestH323GatekeeperIntegration(unittest.TestCase):
    """Integration tests for full gatekeeper workflow"""

    def setUp(self):
        """Setup gatekeeper with test registry"""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = Path(self.temp_dir) / "test-registry.yaml"
        self.witness_dir = Path(self.temp_dir) / "witness"

        # Generate test keypairs for multiple guardians
        self.tech_private, self.tech_public = generate_test_keypair()
        self.civic_private, self.civic_public = generate_test_keypair()

        # Create test registry
        registry_yaml = f"""
guardians:
  - terminal_id: "if://guardian/technical"
    public_key: "{self.tech_public}"
    role: "Technical Guardian"
    bandwidth_quota_bps: 10000000
    registered_at: "2025-11-11T00:00:00Z"
    status: "active"

  - terminal_id: "if://guardian/civic"
    public_key: "{self.civic_public}"
    role: "Civic Guardian"
    bandwidth_quota_bps: 10000000
    registered_at: "2025-11-11T00:00:00Z"
    status: "active"
"""
        with open(self.registry_path, 'w') as f:
            f.write(registry_yaml)

        self.gatekeeper = H323Gatekeeper(
            registry_path=self.registry_path,
            witness_log_dir=self.witness_dir
        )

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_concurrent_admissions(self):
        """✅ Should handle multiple guardians joining concurrently"""
        # Create ARQs for two guardians
        arq_tech = AdmissionRequest(
            terminal_id="if://guardian/technical",
            call_id="council-call-001",
            call_type=CallType.ESCALATE,
            bandwidth_bps=5_000_000,
            has_pii=False,
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature="",
            public_key=self.tech_public
        )
        arq_tech.signature = sign_admission_request(arq_tech, self.tech_private)

        arq_civic = AdmissionRequest(
            terminal_id="if://guardian/civic",
            call_id="council-call-001",
            call_type=CallType.ESCALATE,
            bandwidth_bps=3_000_000,
            has_pii=False,
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature="",
            public_key=self.civic_public
        )
        arq_civic.signature = sign_admission_request(arq_civic, self.civic_private)

        # Both should be admitted
        response_tech = self.gatekeeper.request_admission(arq_tech)
        response_civic = self.gatekeeper.request_admission(arq_civic)

        self.assertTrue(response_tech.confirmed, "Technical guardian admitted")
        self.assertTrue(response_civic.confirmed, "Civic guardian admitted")
        self.assertEqual(self.gatekeeper.get_session_count(), 2, "Two active sessions")

    def test_witness_audit_trail(self):
        """✅ Should create complete audit trail in IF.witness"""
        arq = AdmissionRequest(
            terminal_id="if://guardian/technical",
            call_id="council-call-002",
            call_type=CallType.ROUTINE,
            bandwidth_bps=5_000_000,
            has_pii=False,
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature="",
            public_key=self.tech_public
        )
        arq.signature = sign_admission_request(arq, self.tech_private)

        response = self.gatekeeper.request_admission(arq)

        # Check witness logs
        log_files = list(self.witness_dir.glob("h323_ras_*.jsonl"))
        self.assertEqual(len(log_files), 1, "Witness log created")

        # Should have ARQ and ACF entries
        with open(log_files[0], 'r') as f:
            import json
            lines = f.readlines()

        self.assertEqual(len(lines), 2, "Two log entries (ARQ + ACF)")

        arq_log = json.loads(lines[0])
        acf_log = json.loads(lines[1])

        self.assertEqual(arq_log["msg_type"], "ARQ")
        self.assertEqual(acf_log["msg_type"], "ACF")
        self.assertIn("hash", arq_log, "ARQ has content hash")
        self.assertIn("hash", acf_log, "ACF has content hash")


def run_tests():
    """Run all tests and print summary"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEd25519SignatureVerification))
    suite.addTests(loader.loadTestsFromTestCase(TestGuardianRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestKantianPolicyGates))
    suite.addTests(loader.loadTestsFromTestCase(TestWitnessLogging))
    suite.addTests(loader.loadTestsFromTestCase(TestH323GatekeeperIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("H.323 Admission Control Test Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"❌ Errors: {len(result.errors)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
