"""
IF.witness Data Models
Defines the structure for witness entries, cost tracking, and hash chains.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, Optional
import json


@dataclass
class Cost:
    """Cost tracking for IF.optimise integration"""
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    model: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Cost':
        return cls(**data)


@dataclass
class WitnessEntry:
    """
    A single witness entry in the hash chain.

    Philosophy: IF.ground Principle 8 - Observability without fragility.
    Every operation is logged with provenance (who, what, when, why).

    Hash Chain: prev_hash → content_hash → next.prev_hash
    Signature: Ed25519 cryptographic proof of authenticity
    """
    id: str  # UUID
    timestamp: datetime
    event: str  # e.g., "yologuard_scan", "guard_decision"
    component: str  # e.g., "IF.yologuard", "IF.guard"
    trace_id: str  # Links related operations
    payload: Dict[str, Any]  # Event-specific data
    prev_hash: Optional[str]  # Hash of previous entry (chain)
    content_hash: str  # Hash of this entry's content
    signature: str  # Ed25519 signature
    cost: Optional[Cost] = None  # Token count, $ amount, model

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'event': self.event,
            'component': self.component,
            'trace_id': self.trace_id,
            'payload': json.dumps(self.payload),
            'prev_hash': self.prev_hash,
            'content_hash': self.content_hash,
            'signature': self.signature,
            'tokens_in': self.cost.tokens_in if self.cost else None,
            'tokens_out': self.cost.tokens_out if self.cost else None,
            'cost_usd': self.cost.cost_usd if self.cost else None,
            'model': self.cost.model if self.cost else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WitnessEntry':
        """Create from dictionary (from database)"""
        # Parse timestamp
        timestamp = datetime.fromisoformat(data['timestamp'])

        # Parse payload
        payload = json.loads(data['payload']) if isinstance(data['payload'], str) else data['payload']

        # Parse cost if present
        cost = None
        if data.get('tokens_in') is not None or data.get('cost_usd') is not None:
            cost = Cost(
                tokens_in=data.get('tokens_in') or 0,
                tokens_out=data.get('tokens_out') or 0,
                cost_usd=data.get('cost_usd') or 0.0,
                model=data.get('model') or 'unknown'
            )

        return cls(
            id=data['id'],
            timestamp=timestamp,
            event=data['event'],
            component=data['component'],
            trace_id=data['trace_id'],
            payload=payload,
            prev_hash=data.get('prev_hash'),
            content_hash=data['content_hash'],
            signature=data['signature'],
            cost=cost
        )

    def get_canonical_content(self) -> str:
        """
        Get canonical representation for hashing.
        Excludes content_hash and signature (computed fields).
        Includes prev_hash to chain entries.
        """
        canonical = {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'event': self.event,
            'component': self.component,
            'trace_id': self.trace_id,
            'payload': self.payload,
            'prev_hash': self.prev_hash,
        }
        # Sort keys for deterministic output
        return json.dumps(canonical, sort_keys=True)


@dataclass
class TraceInfo:
    """Information about a complete trace chain"""
    trace_id: str
    entries: list
    duration_seconds: float
    total_cost_usd: float
    total_tokens: int
    components: list

    def to_dict(self) -> Dict[str, Any]:
        return {
            'trace_id': self.trace_id,
            'entries': self.entries,
            'duration_seconds': self.duration_seconds,
            'total_cost_usd': self.total_cost_usd,
            'total_tokens': self.total_tokens,
            'components': self.components,
        }
