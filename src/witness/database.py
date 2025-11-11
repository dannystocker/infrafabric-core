"""
IF.witness Database Module
SQLite database for storing witness entries with hash chains and signatures.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4
from queue import Queue, Empty
from contextlib import contextmanager
from functools import lru_cache
from threading import Lock

from .models import WitnessEntry, Cost, TraceInfo
from .crypto import WitnessCrypto, verify_hash_chain


class WitnessConnectionPool:
    """
    Connection pool for better multi-session performance.

    Philosophy: Pool connections to avoid repeated connection overhead
    while maintaining thread safety.
    """

    def __init__(self, db_path: Path, pool_size: int = 5):
        """
        Initialize connection pool.

        Args:
            db_path: Path to SQLite database
            pool_size: Maximum number of connections in pool
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = Lock()

        # Pre-create connections with optimizations
        for _ in range(pool_size):
            conn = self._create_connection()
            self.pool.put(conn)

    def _create_connection(self) -> sqlite3.Connection:
        """Create optimized SQLite connection"""
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row

        # Apply performance optimizations
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA cache_size=-10000")  # 10MB cache
        conn.execute("PRAGMA synchronous=NORMAL")  # Safe with WAL
        conn.execute("PRAGMA mmap_size=10485760")  # 10MB mmap
        conn.execute("PRAGMA temp_store=MEMORY")  # Temp tables in memory

        return conn

    @contextmanager
    def get_connection(self):
        """Context manager for getting connection from pool"""
        conn = None
        try:
            # Try to get connection with timeout
            conn = self.pool.get(timeout=5.0)
            yield conn
        finally:
            if conn:
                self.pool.put(conn)

    def close_all(self):
        """Close all connections in pool"""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except Empty:
                break


class WitnessDatabase:
    """
    SQLite database for IF.witness entries.

    Philosophy: IF.ground Principle 8 - Observability without fragility.
    - Hash chains prevent tampering
    - Ed25519 signatures prove authenticity
    - Append-only log for audit trails
    """

    def __init__(self, db_path: Path = None, crypto: WitnessCrypto = None, use_pool: bool = False):
        """
        Initialize witness database.

        Args:
            db_path: Path to SQLite database file (default: ~/.if-witness/witness.db)
            crypto: WitnessCrypto instance for signatures
            use_pool: Whether to use connection pooling (for multi-threaded scenarios)
        """
        self.db_path = db_path or Path.home() / '.if-witness' / 'witness.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.crypto = crypto or WitnessCrypto()
        self.use_pool = use_pool

        if use_pool:
            self.pool = WitnessConnectionPool(self.db_path)
            # Get a connection to create schema
            with self.pool.get_connection() as conn:
                self._create_schema_with_conn(conn)
            self.conn = None  # Use pool instead
        else:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Enable column access by name

            # Performance optimizations for SQLite
            # Enable WAL mode for better concurrent access
            self.conn.execute("PRAGMA journal_mode=WAL")

            # Increase cache size (10MB)
            self.conn.execute("PRAGMA cache_size=-10000")

            # Use synchronous=NORMAL for better performance
            # (still safe with WAL mode)
            self.conn.execute("PRAGMA synchronous=NORMAL")

            # Enable memory-mapped I/O (10MB)
            self.conn.execute("PRAGMA mmap_size=10485760")

            # Store temp tables in memory
            self.conn.execute("PRAGMA temp_store=MEMORY")

            self._create_schema_with_conn(self.conn)

        # Cache for frequently accessed data
        self._cache_lock = Lock()
        self._last_entry_cache = None
        self._cache_timestamp = None

    def _create_schema_with_conn(self, conn: sqlite3.Connection):
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
        -- Composite index for cost queries
        CREATE INDEX IF NOT EXISTS idx_component_timestamp ON witness_entries(component, timestamp);
        """
        conn.executescript(schema)
        conn.commit()

    def get_last_entry(self) -> Optional[WitnessEntry]:
        """Get the most recent witness entry (for hash chaining)"""
        # Check cache first
        with self._cache_lock:
            if self._last_entry_cache is not None:
                return self._last_entry_cache

        conn = self.conn if not self.use_pool else None
        if self.use_pool:
            with self.pool.get_connection() as pool_conn:
                cursor = pool_conn.execute(
                    "SELECT * FROM witness_entries ORDER BY timestamp DESC LIMIT 1"
                )
                row = cursor.fetchone()
        else:
            cursor = conn.execute(
                "SELECT * FROM witness_entries ORDER BY timestamp DESC LIMIT 1"
            )
            row = cursor.fetchone()

        if row:
            entry = WitnessEntry.from_dict(dict(row))
            # Update cache
            with self._cache_lock:
                self._last_entry_cache = entry
            return entry
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

        conn = self.conn if not self.use_pool else None
        if self.use_pool:
            with self.pool.get_connection() as pool_conn:
                pool_conn.execute(
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
                pool_conn.commit()
        else:
            conn.execute(
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
            conn.commit()

        # Invalidate cache
        with self._cache_lock:
            self._last_entry_cache = entry

    def create_entries_batch(self, entries_data: List[Dict[str, Any]]) -> List[WitnessEntry]:
        """
        Insert multiple entries in a single transaction for better performance.

        Args:
            entries_data: List of dicts with keys: event, component, trace_id, payload, cost

        Returns:
            List of created WitnessEntry objects

        Philosophy: Batch operations dramatically improve throughput by reducing
        transaction overhead from O(n) to O(1).
        """
        entries = []
        conn = self.conn if not self.use_pool else None

        if self.use_pool:
            with self.pool.get_connection() as pool_conn:
                entries = self._batch_insert_with_conn(pool_conn, entries_data)
        else:
            entries = self._batch_insert_with_conn(conn, entries_data)

        # Update cache with last entry
        if entries:
            with self._cache_lock:
                self._last_entry_cache = entries[-1]

        return entries

    def _batch_insert_with_conn(self, conn: sqlite3.Connection, entries_data: List[Dict[str, Any]]) -> List[WitnessEntry]:
        """Helper for batch insert with given connection"""
        entries = []

        try:
            # Begin transaction
            conn.execute("BEGIN")

            # Get last entry for hash chaining
            cursor = conn.execute(
                "SELECT * FROM witness_entries ORDER BY timestamp DESC LIMIT 1"
            )
            row = cursor.fetchone()
            prev_entry = WitnessEntry.from_dict(dict(row)) if row else None
            prev_hash = prev_entry.content_hash if prev_entry else None

            # Create all entries
            for data in entries_data:
                # Create entry
                entry = WitnessEntry(
                    id=str(uuid4()),
                    timestamp=datetime.utcnow(),
                    event=data['event'],
                    component=data['component'],
                    trace_id=data['trace_id'],
                    payload=data['payload'],
                    prev_hash=prev_hash,
                    content_hash="",
                    signature="",
                    cost=data.get('cost')
                )

                # Compute hash and signature
                canonical_content = entry.get_canonical_content()
                entry.content_hash = WitnessCrypto.compute_hash(canonical_content)
                entry.signature = self.crypto.sign(canonical_content)

                # Insert
                entry_dict = entry.to_dict()
                conn.execute(
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
                    entry_dict
                )

                entries.append(entry)
                # Update prev_hash for next entry
                prev_hash = entry.content_hash

            # Commit transaction
            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e

        return entries

    def get_all_entries(self) -> List[WitnessEntry]:
        """Get all witness entries sorted by timestamp"""
        conn = self.conn if not self.use_pool else None
        if self.use_pool:
            with self.pool.get_connection() as pool_conn:
                cursor = pool_conn.execute(
                    "SELECT * FROM witness_entries ORDER BY timestamp ASC"
                )
                return [WitnessEntry.from_dict(dict(row)) for row in cursor.fetchall()]
        else:
            cursor = conn.execute(
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
        conn = self.conn if not self.use_pool else None
        if self.use_pool:
            with self.pool.get_connection() as pool_conn:
                cursor = pool_conn.execute(
                    "SELECT * FROM witness_entries WHERE trace_id = ? ORDER BY timestamp ASC",
                    (trace_id,)
                )
                entries = [WitnessEntry.from_dict(dict(row)) for row in cursor.fetchall()]
        else:
            cursor = conn.execute(
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

        conn = self.conn if not self.use_pool else None
        if self.use_pool:
            with self.pool.get_connection() as pool_conn:
                cursor = pool_conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        else:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def export_json(self) -> List[Dict[str, Any]]:
        """Export all entries as JSON-serializable list"""
        entries = self.get_all_entries()
        return [e.to_dict() for e in entries]

    def get_entries_by_date_range(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[WitnessEntry]:
        """
        Get entries within a date range.

        Args:
            start_date: Start date (inclusive), None for no limit
            end_date: End date (inclusive), None for no limit

        Returns:
            List of WitnessEntry objects sorted by timestamp
        """
        query = "SELECT * FROM witness_entries WHERE 1=1"
        params = []

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY timestamp ASC"

        conn = self.conn if not self.use_pool else None
        if self.use_pool:
            with self.pool.get_connection() as pool_conn:
                cursor = pool_conn.execute(query, params)
                return [WitnessEntry.from_dict(dict(row)) for row in cursor.fetchall()]
        else:
            cursor = conn.execute(query, params)
            return [WitnessEntry.from_dict(dict(row)) for row in cursor.fetchall()]

    def export_csv_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Export entries in CSV-friendly format with optional date range filtering.

        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering

        Returns:
            List of dictionaries with all entry fields
        """
        query = (
            "SELECT id, timestamp, event, component, trace_id, "
            "prev_hash, content_hash, signature, "
            "tokens_in, tokens_out, cost_usd, model FROM witness_entries "
            "WHERE 1=1"
        )
        params = []

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY timestamp ASC"

        conn = self.conn if not self.use_pool else None
        if self.use_pool:
            with self.pool.get_connection() as pool_conn:
                cursor = pool_conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        else:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection"""
        if self.use_pool:
            self.pool.close_all()
        else:
            self.conn.close()
