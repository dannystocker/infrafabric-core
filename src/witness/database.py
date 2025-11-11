"""
IF.witness Database Module
SQLite database for storing witness entries with hash chains and signatures.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from .models import WitnessEntry, Cost, TraceInfo
from .crypto import WitnessCrypto, verify_hash_chain


class WitnessDatabase:
    """
    SQLite database for IF.witness entries.

    Philosophy: IF.ground Principle 8 - Observability without fragility.
    - Hash chains prevent tampering
    - Ed25519 signatures prove authenticity
    - Append-only log for audit trails
    """

    def __init__(self, db_path: Path = None, crypto: WitnessCrypto = None):
        """
        Initialize witness database.

        Args:
            db_path: Path to SQLite database file (default: ~/.if-witness/witness.db)
            crypto: WitnessCrypto instance for signatures
        """
        self.db_path = db_path or Path.home() / '.if-witness' / 'witness.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.crypto = crypto or WitnessCrypto()
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Enable column access by name

        self._create_schema()

    def _create_schema(self):
        """Create database schema if it doesn't exist"""
        schema = """
        CREATE TABLE IF NOT EXISTS witness_entries (
            id TEXT PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            event TEXT NOT NULL,
            component TEXT NOT NULL,
            trace_id TEXT NOT NULL,
            payload JSON NOT NULL,
            prev_hash TEXT,
            content_hash TEXT NOT NULL,
            signature TEXT NOT NULL,

            -- Cost tracking (IF.optimise)
            tokens_in INTEGER,
            tokens_out INTEGER,
            cost_usd REAL,
            model TEXT
        );

        -- Indexes for efficient queries
        CREATE INDEX IF NOT EXISTS idx_trace_id ON witness_entries(trace_id);
        CREATE INDEX IF NOT EXISTS idx_timestamp ON witness_entries(timestamp);
        CREATE INDEX IF NOT EXISTS idx_component ON witness_entries(component);
        CREATE INDEX IF NOT EXISTS idx_event ON witness_entries(event);
        """
        self.conn.executescript(schema)
        self.conn.commit()

    def get_last_entry(self) -> Optional[WitnessEntry]:
        """Get the most recent witness entry (for hash chaining)"""
        cursor = self.conn.execute(
            "SELECT * FROM witness_entries ORDER BY timestamp DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if row:
            return WitnessEntry.from_dict(dict(row))
        return None

    def create_entry(
        self,
        event: str,
        component: str,
        trace_id: str,
        payload: Dict[str, Any],
        cost: Optional[Cost] = None
    ) -> WitnessEntry:
        """
        Create a new witness entry with hash chain and signature.

        Args:
            event: Event type (e.g., "yologuard_scan", "guard_decision")
            component: Component name (e.g., "IF.yologuard", "IF.guard")
            trace_id: Trace ID linking related operations
            payload: Event-specific data
            cost: Optional cost tracking information

        Returns:
            New WitnessEntry with hash chain and signature
        """
        # Get previous entry for hash chaining
        prev_entry = self.get_last_entry()
        prev_hash = prev_entry.content_hash if prev_entry else None

        # Create entry
        entry = WitnessEntry(
            id=str(uuid4()),
            timestamp=datetime.utcnow(),
            event=event,
            component=component,
            trace_id=trace_id,
            payload=payload,
            prev_hash=prev_hash,
            content_hash="",  # Computed below
            signature="",  # Computed below
            cost=cost
        )

        # Compute content hash
        canonical_content = entry.get_canonical_content()
        entry.content_hash = WitnessCrypto.compute_hash(canonical_content)

        # Sign entry
        entry.signature = self.crypto.sign(canonical_content)

        # Store in database
        self._insert_entry(entry)

        return entry

    def _insert_entry(self, entry: WitnessEntry):
        """Insert witness entry into database"""
        data = entry.to_dict()
        self.conn.execute(
            """
            INSERT INTO witness_entries (
                id, timestamp, event, component, trace_id, payload,
                prev_hash, content_hash, signature,
                tokens_in, tokens_out, cost_usd, model
            ) VALUES (
                :id, :timestamp, :event, :component, :trace_id, :payload,
                :prev_hash, :content_hash, :signature,
                :tokens_in, :tokens_out, :cost_usd, :model
            )
            """,
            data
        )
        self.conn.commit()

    def get_all_entries(self) -> List[WitnessEntry]:
        """Get all witness entries sorted by timestamp"""
        cursor = self.conn.execute(
            "SELECT * FROM witness_entries ORDER BY timestamp ASC"
        )
        return [WitnessEntry.from_dict(dict(row)) for row in cursor.fetchall()]

    def verify_all(self) -> tuple[bool, str, int]:
        """
        Verify entire hash chain integrity.

        Returns:
            Tuple of (is_valid, error_message, entry_count)
        """
        entries = self.get_all_entries()

        if not entries:
            return True, "No entries to verify", 0

        # Verify hash chain
        is_valid, error_msg = verify_hash_chain(entries)
        if not is_valid:
            return False, error_msg, len(entries)

        # Verify signatures
        for i, entry in enumerate(entries):
            canonical = entry.get_canonical_content()
            if not self.crypto.verify(canonical, entry.signature):
                return False, f"Entry {i} ({entry.id}): Invalid signature", len(entries)

        return True, f"All {len(entries)} entries verified", len(entries)

    def get_trace(self, trace_id: str) -> TraceInfo:
        """
        Get all entries for a specific trace ID.

        Args:
            trace_id: Trace ID to query

        Returns:
            TraceInfo with complete trace chain
        """
        cursor = self.conn.execute(
            "SELECT * FROM witness_entries WHERE trace_id = ? ORDER BY timestamp ASC",
            (trace_id,)
        )
        entries = [WitnessEntry.from_dict(dict(row)) for row in cursor.fetchall()]

        if not entries:
            return TraceInfo(
                trace_id=trace_id,
                entries=[],
                duration_seconds=0.0,
                total_cost_usd=0.0,
                total_tokens=0,
                components=[]
            )

        # Calculate metrics
        first_ts = entries[0].timestamp
        last_ts = entries[-1].timestamp
        duration = (last_ts - first_ts).total_seconds()

        total_cost = sum(e.cost.cost_usd for e in entries if e.cost)
        total_tokens = sum((e.cost.tokens_in + e.cost.tokens_out) for e in entries if e.cost)
        components = list(set(e.component for e in entries))

        return TraceInfo(
            trace_id=trace_id,
            entries=[e.to_dict() for e in entries],
            duration_seconds=duration,
            total_cost_usd=total_cost,
            total_tokens=total_tokens,
            components=components
        )

    def get_cost_by_component(
        self,
        component: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get cost breakdown by component.

        Args:
            component: Optional component filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of cost records grouped by component
        """
        query = """
            SELECT
                component,
                COUNT(*) as operations,
                SUM(tokens_in + tokens_out) as total_tokens,
                SUM(cost_usd) as total_cost,
                model
            FROM witness_entries
            WHERE 1=1
        """
        params = []

        if component:
            query += " AND component = ?"
            params.append(component)

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())

        query += " GROUP BY component, model ORDER BY total_cost DESC"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def export_json(self) -> List[Dict[str, Any]]:
        """Export all entries as JSON-serializable list"""
        entries = self.get_all_entries()
        return [e.to_dict() for e in entries]

    def export_csv_data(self) -> List[Dict[str, Any]]:
        """Export entries in CSV-friendly format"""
        cursor = self.conn.execute(
            "SELECT id, timestamp, event, component, trace_id, content_hash, "
            "tokens_in, tokens_out, cost_usd, model FROM witness_entries "
            "ORDER BY timestamp ASC"
        )
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection"""
        self.conn.close()
