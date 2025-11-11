"""
Unit tests for IF.witness CLI

Tests:
- Hash chain verification
- Trace ID propagation
- Cost calculation
- Export formats
- Ed25519 signatures
"""

import sys
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.witness.database import WitnessDatabase
from src.witness.models import Cost, WitnessEntry
from src.witness.crypto import WitnessCrypto, verify_hash_chain


class TestWitnessCrypto(unittest.TestCase):
    """Test cryptographic operations"""

    def setUp(self):
        """Create temporary key directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.key_path = Path(self.temp_dir) / 'test_key.pem'
        self.crypto = WitnessCrypto(self.key_path)

    def test_keypair_generation(self):
        """Test Ed25519 keypair generation"""
        self.assertTrue(self.key_path.exists())
        self.assertTrue((self.key_path.parent / 'public_key.pem').exists())

    def test_sign_and_verify(self):
        """Test signing and verification"""
        content = "Test witness entry content"

        # Sign
        signature = self.crypto.sign(content)
        self.assertIsInstance(signature, str)
        self.assertTrue(len(signature) > 0)

        # Verify with own key
        is_valid = self.crypto.verify(content, signature)
        self.assertTrue(is_valid)

        # Verify with wrong content should fail
        is_valid = self.crypto.verify("Wrong content", signature)
        self.assertFalse(is_valid)

    def test_hash_computation(self):
        """Test SHA-256 hash computation"""
        content = '{"id": "test", "event": "test_event"}'
        hash1 = WitnessCrypto.compute_hash(content)
        hash2 = WitnessCrypto.compute_hash(content)

        # Same content should produce same hash
        self.assertEqual(hash1, hash2)

        # Different content should produce different hash
        hash3 = WitnessCrypto.compute_hash(content + "x")
        self.assertNotEqual(hash1, hash3)


class TestWitnessDatabase(unittest.TestCase):
    """Test database operations"""

    def setUp(self):
        """Create temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_witness.db'
        self.key_path = Path(self.temp_dir) / 'test_key.pem'

        self.crypto = WitnessCrypto(self.key_path)
        self.db = WitnessDatabase(self.db_path, self.crypto)

    def tearDown(self):
        """Close database"""
        self.db.close()

    def test_create_entry(self):
        """Test creating witness entry"""
        entry = self.db.create_entry(
            event='test_event',
            component='IF.test',
            trace_id='test-trace-1',
            payload={'test': 'data'}
        )

        self.assertIsInstance(entry, WitnessEntry)
        self.assertEqual(entry.event, 'test_event')
        self.assertEqual(entry.component, 'IF.test')
        self.assertEqual(entry.trace_id, 'test-trace-1')
        self.assertIsNotNone(entry.content_hash)
        self.assertIsNotNone(entry.signature)

    def test_hash_chain(self):
        """Test hash chain linking"""
        # Create first entry
        entry1 = self.db.create_entry(
            event='event1',
            component='IF.test',
            trace_id='test-trace-1',
            payload={'step': 1}
        )

        # First entry should have no prev_hash
        self.assertIsNone(entry1.prev_hash)

        # Create second entry
        entry2 = self.db.create_entry(
            event='event2',
            component='IF.test',
            trace_id='test-trace-1',
            payload={'step': 2}
        )

        # Second entry's prev_hash should match first entry's content_hash
        self.assertEqual(entry2.prev_hash, entry1.content_hash)

        # Create third entry
        entry3 = self.db.create_entry(
            event='event3',
            component='IF.test',
            trace_id='test-trace-1',
            payload={'step': 3}
        )

        # Third entry's prev_hash should match second entry's content_hash
        self.assertEqual(entry3.prev_hash, entry2.content_hash)

    def test_verify_all(self):
        """Test hash chain verification"""
        # Create multiple entries
        for i in range(5):
            self.db.create_entry(
                event=f'event{i}',
                component='IF.test',
                trace_id='test-trace-1',
                payload={'step': i}
            )

        # Verify all entries
        is_valid, error_msg, count = self.db.verify_all()

        self.assertTrue(is_valid)
        self.assertEqual(count, 5)
        self.assertIn("verified", error_msg.lower())

    def test_trace_retrieval(self):
        """Test trace ID propagation"""
        trace_id = 'test-trace-123'

        # Create entries with same trace_id
        self.db.create_entry(
            event='scan_started',
            component='IF.yologuard',
            trace_id=trace_id,
            payload={'file': 'test.py'}
        )

        self.db.create_entry(
            event='secrets_detected',
            component='IF.yologuard',
            trace_id=trace_id,
            payload={'count': 3}
        )

        self.db.create_entry(
            event='review_requested',
            component='IF.guard',
            trace_id=trace_id,
            payload={'severity': 'high'}
        )

        # Retrieve trace
        trace_info = self.db.get_trace(trace_id)

        self.assertEqual(trace_info.trace_id, trace_id)
        self.assertEqual(len(trace_info.entries), 3)
        self.assertIn('IF.yologuard', trace_info.components)
        self.assertIn('IF.guard', trace_info.components)

    def test_cost_tracking(self):
        """Test cost calculation and tracking"""
        cost = Cost(
            tokens_in=1000,
            tokens_out=2000,
            cost_usd=0.015,
            model='claude-haiku-4.5'
        )

        entry = self.db.create_entry(
            event='llm_call',
            component='IF.swarm',
            trace_id='test-trace-cost',
            payload={'question': 'Is this pattern valid?'},
            cost=cost
        )

        # Verify cost was saved
        self.assertIsNotNone(entry.cost)
        self.assertEqual(entry.cost.tokens_in, 1000)
        self.assertEqual(entry.cost.tokens_out, 2000)
        self.assertEqual(entry.cost.cost_usd, 0.015)
        self.assertEqual(entry.cost.model, 'claude-haiku-4.5')

        # Retrieve and verify
        trace_info = self.db.get_trace('test-trace-cost')
        self.assertEqual(trace_info.total_cost_usd, 0.015)
        self.assertEqual(trace_info.total_tokens, 3000)

    def test_cost_by_component(self):
        """Test cost breakdown by component"""
        # Create entries for different components
        self.db.create_entry(
            event='scan',
            component='IF.yologuard',
            trace_id='trace1',
            payload={},
            cost=Cost(tokens_in=100, tokens_out=50, cost_usd=0.001, model='claude-haiku-4.5')
        )

        self.db.create_entry(
            event='scan',
            component='IF.yologuard',
            trace_id='trace2',
            payload={},
            cost=Cost(tokens_in=200, tokens_out=100, cost_usd=0.002, model='claude-haiku-4.5')
        )

        self.db.create_entry(
            event='vote',
            component='IF.swarm',
            trace_id='trace3',
            payload={},
            cost=Cost(tokens_in=500, tokens_out=300, cost_usd=0.01, model='claude-sonnet-4.5')
        )

        # Get cost breakdown
        cost_data = self.db.get_cost_by_component()

        # Should have two components
        components = [row['component'] for row in cost_data]
        self.assertIn('IF.yologuard', components)
        self.assertIn('IF.swarm', components)

        # Verify yologuard totals
        yologuard_data = next(row for row in cost_data if row['component'] == 'IF.yologuard')
        self.assertEqual(yologuard_data['operations'], 2)
        self.assertEqual(yologuard_data['total_tokens'], 450)  # (100+50) + (200+100)
        self.assertAlmostEqual(yologuard_data['total_cost'], 0.003, places=6)

    def test_export_json(self):
        """Test JSON export"""
        # Create entries
        self.db.create_entry(
            event='test1',
            component='IF.test',
            trace_id='trace1',
            payload={'data': 'test'}
        )

        self.db.create_entry(
            event='test2',
            component='IF.test',
            trace_id='trace2',
            payload={'data': 'test2'}
        )

        # Export
        data = self.db.export_json()

        self.assertEqual(len(data), 2)
        self.assertIn('id', data[0])
        self.assertIn('event', data[0])
        self.assertIn('signature', data[0])
        self.assertIn('content_hash', data[0])

    def test_export_csv(self):
        """Test CSV export"""
        # Create entry
        self.db.create_entry(
            event='test1',
            component='IF.test',
            trace_id='trace1',
            payload={'data': 'test'},
            cost=Cost(tokens_in=100, tokens_out=50, cost_usd=0.001, model='test-model')
        )

        # Export
        data = self.db.export_csv_data()

        self.assertEqual(len(data), 1)
        self.assertIn('id', data[0])
        self.assertIn('event', data[0])
        self.assertIn('cost_usd', data[0])
        self.assertIn('model', data[0])


class TestHashChainVerification(unittest.TestCase):
    """Test hash chain verification algorithm"""

    def setUp(self):
        """Create test entries"""
        self.temp_dir = tempfile.mkdtemp()
        self.key_path = Path(self.temp_dir) / 'test_key.pem'
        self.crypto = WitnessCrypto(self.key_path)

    def test_empty_chain(self):
        """Test verification of empty chain"""
        is_valid, error_msg = verify_hash_chain([])
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")

    def test_single_entry(self):
        """Test verification of single entry"""
        entry = WitnessEntry(
            id='test-1',
            timestamp=datetime.utcnow(),
            event='test',
            component='IF.test',
            trace_id='trace1',
            payload={},
            prev_hash=None,
            content_hash='',
            signature=''
        )

        # Compute hash and signature
        canonical = entry.get_canonical_content()
        entry.content_hash = WitnessCrypto.compute_hash(canonical)
        entry.signature = self.crypto.sign(canonical)

        is_valid, error_msg = verify_hash_chain([entry])
        self.assertTrue(is_valid)

    def test_valid_chain(self):
        """Test verification of valid chain"""
        entries = []

        # Create chain
        for i in range(3):
            prev_hash = entries[-1].content_hash if entries else None

            entry = WitnessEntry(
                id=f'test-{i}',
                timestamp=datetime.utcnow(),
                event=f'event{i}',
                component='IF.test',
                trace_id='trace1',
                payload={'step': i},
                prev_hash=prev_hash,
                content_hash='',
                signature=''
            )

            # Compute hash and signature
            canonical = entry.get_canonical_content()
            entry.content_hash = WitnessCrypto.compute_hash(canonical)
            entry.signature = self.crypto.sign(canonical)

            entries.append(entry)

        is_valid, error_msg = verify_hash_chain(entries)
        self.assertTrue(is_valid)

    def test_broken_chain(self):
        """Test detection of broken chain"""
        entries = []

        # Create chain
        for i in range(3):
            prev_hash = entries[-1].content_hash if entries else None

            entry = WitnessEntry(
                id=f'test-{i}',
                timestamp=datetime.utcnow(),
                event=f'event{i}',
                component='IF.test',
                trace_id='trace1',
                payload={'step': i},
                prev_hash=prev_hash,
                content_hash='',
                signature=''
            )

            canonical = entry.get_canonical_content()
            entry.content_hash = WitnessCrypto.compute_hash(canonical)
            entry.signature = self.crypto.sign(canonical)

            entries.append(entry)

        # Break the chain by modifying second entry's prev_hash
        # Note: This will also break content_hash since prev_hash is in canonical content
        entries[1].prev_hash = 'wrong_hash'

        is_valid, error_msg = verify_hash_chain(entries)
        self.assertFalse(is_valid)
        # Either "Content hash mismatch" or "Hash chain broken" is acceptable
        self.assertTrue("mismatch" in error_msg.lower() or "broken" in error_msg.lower())


if __name__ == '__main__':
    unittest.main()
