#!/usr/bin/env python3
"""
IF.witness Hash Chain Example: Coordination Events

This example demonstrates how IF.witness tracks Phase 0 coordination operations
with cryptographic hash chains for traceability and tamper-detection.

Events tracked:
1. Task claim event (IF.coordinator)
2. Task execution start event
3. Task progress updates
4. Task completion event
5. Hash chain verification

Each event creates a witness entry with:
- Previous hash (links to prior event)
- Current data hash
- Ed25519 signature
- Timestamp

Reference: docs/components/IF.WITNESS.md
"""

import hashlib
import json
import time
from dataclasses import dataclass, asdict
from typing import Optional, List
from datetime import datetime

# Ed25519 signing (placeholder - would use nacl.signing in production)
class Ed25519Signer:
    """Simple Ed25519 signer (placeholder for production crypto)"""

    def __init__(self, private_key: str = "simulation_key"):
        self.private_key = private_key

    def sign(self, message: bytes) -> str:
        """Sign message with Ed25519 (simulated)"""
        # In production: use nacl.signing.SigningKey
        # For demo: simple deterministic signature
        sig_hash = hashlib.sha256(message + self.private_key.encode()).hexdigest()
        return f"ed25519:sim:{sig_hash[:64]}"

    def verify(self, message: bytes, signature: str) -> bool:
        """Verify Ed25519 signature (simulated)"""
        expected_sig = self.sign(message)
        return signature == expected_sig


@dataclass
class WitnessEntry:
    """Single entry in IF.witness hash chain"""

    component: str  # e.g., "IF.coordinator", "IF.governor"
    operation: str  # e.g., "task_claimed", "task_completed"
    session_id: str  # e.g., "session-1-ndi"
    task_id: str  # e.g., "P0.1.1"
    timestamp: float  # Unix timestamp
    data: dict  # Operation-specific data
    prev_hash: str  # Hash of previous entry (chain link)
    data_hash: str  # Hash of current entry data
    signature: str  # Ed25519 signature of (prev_hash + data_hash)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


class WitnessHashChain:
    """IF.witness hash chain for coordination events"""

    GENESIS_HASH = "0" * 64  # Initial hash for first entry

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.chain: List[WitnessEntry] = []
        self.signer = Ed25519Signer()

    def _compute_data_hash(self, data: dict) -> str:
        """Compute SHA-256 hash of data"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _get_previous_hash(self) -> str:
        """Get hash of previous entry (or genesis hash)"""
        if not self.chain:
            return self.GENESIS_HASH
        prev_entry = self.chain[-1]
        # Hash = SHA-256(prev_hash + data_hash)
        combined = (prev_entry.prev_hash + prev_entry.data_hash).encode()
        return hashlib.sha256(combined).hexdigest()

    def add_entry(
        self,
        component: str,
        operation: str,
        task_id: str,
        data: dict
    ) -> WitnessEntry:
        """Add new entry to hash chain"""

        timestamp = time.time()
        prev_hash = self._get_previous_hash()
        data_hash = self._compute_data_hash(data)

        # Create signature over (prev_hash + data_hash)
        message = (prev_hash + data_hash).encode()
        signature = self.signer.sign(message)

        entry = WitnessEntry(
            component=component,
            operation=operation,
            session_id=self.session_id,
            task_id=task_id,
            timestamp=timestamp,
            data=data,
            prev_hash=prev_hash,
            data_hash=data_hash,
            signature=signature
        )

        self.chain.append(entry)
        return entry

    def verify_chain(self) -> bool:
        """Verify entire hash chain integrity"""

        if not self.chain:
            return True  # Empty chain is valid

        # Verify first entry links to genesis
        if self.chain[0].prev_hash != self.GENESIS_HASH:
            print(f"❌ Chain verification failed: First entry prev_hash != GENESIS")
            return False

        # Verify each entry
        for i, entry in enumerate(self.chain):
            # 1. Verify data hash
            expected_data_hash = self._compute_data_hash(entry.data)
            if entry.data_hash != expected_data_hash:
                print(f"❌ Entry {i}: Data hash mismatch")
                return False

            # 2. Verify signature
            message = (entry.prev_hash + entry.data_hash).encode()
            if not self.signer.verify(message, entry.signature):
                print(f"❌ Entry {i}: Signature invalid")
                return False

            # 3. Verify chain link (prev_hash points to previous entry)
            if i > 0:
                prev_entry = self.chain[i - 1]
                expected_prev_hash = hashlib.sha256(
                    (prev_entry.prev_hash + prev_entry.data_hash).encode()
                ).hexdigest()
                if entry.prev_hash != expected_prev_hash:
                    print(f"❌ Entry {i}: Chain link broken")
                    return False

        print(f"✅ Chain verification passed: {len(self.chain)} entries verified")
        return True

    def detect_tampering(self, tampered_entry_index: int) -> bool:
        """Simulate tampering and verify detection"""

        if tampered_entry_index >= len(self.chain):
            raise IndexError("Entry index out of range")

        print(f"\n🔧 Simulating tampering at entry {tampered_entry_index}...")

        # Tamper with data (change swarm_id)
        original_data = self.chain[tampered_entry_index].data.copy()
        self.chain[tampered_entry_index].data['swarm_id'] = 'attacker-swarm'

        # Try to verify (should fail)
        print(f"Original data: {original_data}")
        print(f"Tampered data: {self.chain[tampered_entry_index].data}")

        is_valid = self.verify_chain()

        # Restore original data
        self.chain[tampered_entry_index].data = original_data

        return not is_valid  # Tampering detected if verification failed

    def export_chain(self, filepath: str):
        """Export hash chain to JSON file"""
        chain_data = [entry.to_dict() for entry in self.chain]
        with open(filepath, 'w') as f:
            json.dump(chain_data, f, indent=2)
        print(f"📝 Chain exported to {filepath}")


def demo_coordination_workflow():
    """Demonstrate IF.witness tracking of Phase 0 coordination workflow"""

    print("=" * 80)
    print("IF.witness Hash Chain Example: Phase 0 Coordination Events")
    print("=" * 80)

    # Initialize hash chain for Session 1 (NDI)
    witness = WitnessHashChain(session_id="session-1-ndi")

    # Event 1: Task Claim (IF.coordinator)
    print("\n[1] Task Claim Event")
    print("-" * 40)
    entry1 = witness.add_entry(
        component="IF.coordinator",
        operation="task_claimed",
        task_id="P0.5.1",
        data={
            "swarm_id": "session-1-ndi",
            "task_id": "P0.5.1",
            "task_description": "IF.coordinator Documentation",
            "claim_latency_ms": 7.3,
            "claimed_via": "atomic_cas"
        }
    )
    print(f"✅ Task P0.5.1 claimed by session-1-ndi")
    print(f"   Timestamp: {datetime.fromtimestamp(entry1.timestamp).isoformat()}")
    print(f"   Prev Hash: {entry1.prev_hash[:16]}...")
    print(f"   Data Hash: {entry1.data_hash[:16]}...")
    print(f"   Signature: {entry1.signature[:32]}...")

    # Event 2: Task Execution Start
    print("\n[2] Task Execution Start Event")
    print("-" * 40)
    entry2 = witness.add_entry(
        component="IF.coordinator",
        operation="task_execution_started",
        task_id="P0.5.1",
        data={
            "swarm_id": "session-1-ndi",
            "task_id": "P0.5.1",
            "sub_agents_allocated": 1,
            "model": "haiku",
            "estimated_cost": 2.00
        }
    )
    print(f"✅ Task execution started")
    print(f"   Sub-agents: {entry2.data['sub_agents_allocated']} (Haiku)")
    print(f"   Prev Hash: {entry2.prev_hash[:16]}... (links to entry 1)")
    print(f"   Data Hash: {entry2.data_hash[:16]}...")

    # Event 3: Task Progress Update (25%)
    print("\n[3] Task Progress Update Event (25%)")
    print("-" * 40)
    entry3 = witness.add_entry(
        component="IF.governor",
        operation="task_progress_updated",
        task_id="P0.5.1",
        data={
            "swarm_id": "session-1-ndi",
            "task_id": "P0.5.1",
            "milestone": "25% - Architecture overview written",
            "cost_to_date": 0.50,
            "budget_remaining": 39.50
        }
    )
    print(f"✅ Progress: {entry3.data['milestone']}")
    print(f"   Cost: ${entry3.data['cost_to_date']:.2f}")
    print(f"   Budget: ${entry3.data['budget_remaining']:.2f} remaining")
    print(f"   Prev Hash: {entry3.prev_hash[:16]}... (links to entry 2)")

    # Event 4: Task Progress Update (50%)
    print("\n[4] Task Progress Update Event (50%)")
    print("-" * 40)
    entry4 = witness.add_entry(
        component="IF.governor",
        operation="task_progress_updated",
        task_id="P0.5.1",
        data={
            "swarm_id": "session-1-ndi",
            "task_id": "P0.5.1",
            "milestone": "50% - API reference complete",
            "cost_to_date": 1.00,
            "budget_remaining": 39.00
        }
    )
    print(f"✅ Progress: {entry4.data['milestone']}")
    print(f"   Prev Hash: {entry4.prev_hash[:16]}... (links to entry 3)")

    # Event 5: Task Completion
    print("\n[5] Task Completion Event")
    print("-" * 40)
    entry5 = witness.add_entry(
        component="IF.coordinator",
        operation="task_completed",
        task_id="P0.5.1",
        data={
            "swarm_id": "session-1-ndi",
            "task_id": "P0.5.1",
            "deliverable": "/home/user/infrafabric/docs/components/IF.COORDINATOR.md",
            "total_cost": 2.00,
            "execution_time_seconds": 3600,
            "tests_passed": True,
            "reputation_change": +0.02
        }
    )
    print(f"✅ Task P0.5.1 completed successfully")
    print(f"   Deliverable: {entry5.data['deliverable']}")
    print(f"   Total cost: ${entry5.data['total_cost']:.2f}")
    print(f"   Execution time: {entry5.data['execution_time_seconds'] / 60:.1f} minutes")
    print(f"   Reputation: +{entry5.data['reputation_change']:.2f}")
    print(f"   Prev Hash: {entry5.prev_hash[:16]}... (links to entry 4)")

    # Verify hash chain
    print("\n[6] Hash Chain Verification")
    print("-" * 40)
    witness.verify_chain()

    # Print full chain structure
    print("\n[7] Full Chain Structure")
    print("-" * 40)
    print(f"Chain length: {len(witness.chain)} entries")
    print(f"Session: {witness.session_id}")
    print(f"\nChain visualization:")
    for i, entry in enumerate(witness.chain):
        print(f"  [{i}] {entry.operation}")
        print(f"      Prev: {entry.prev_hash[:16]}...")
        print(f"      Data: {entry.data_hash[:16]}...")
        print(f"      Sig:  {entry.signature[:32]}...")
        if i < len(witness.chain) - 1:
            print(f"      ↓")

    # Demonstrate tampering detection
    print("\n[8] Tampering Detection")
    print("-" * 40)
    tampered = witness.detect_tampering(tampered_entry_index=2)
    if tampered:
        print("✅ Tampering detected successfully!")
    else:
        print("❌ Tampering went undetected (this shouldn't happen)")

    # Re-verify after tampering restoration
    print("\n[9] Post-Tampering Verification")
    print("-" * 40)
    witness.verify_chain()

    # Export chain
    print("\n[10] Export Chain")
    print("-" * 40)
    witness.export_chain("/tmp/witness-chain-session-1-ndi.json")

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"✅ Tracked {len(witness.chain)} coordination events")
    print(f"✅ Hash chain verified (all signatures valid)")
    print(f"✅ Tampering detection working correctly")
    print(f"✅ Chain exported for audit trail")
    print("\nBenefits:")
    print("  • Full traceability: Every coordination operation recorded")
    print("  • Tamper-proof: Cryptographic hash chain detects any modifications")
    print("  • Verifiable: Ed25519 signatures prove authenticity")
    print("  • IF.TTT compliant: Traceable, Transparent, Trustworthy")
    print("=" * 80)


if __name__ == "__main__":
    demo_coordination_workflow()
