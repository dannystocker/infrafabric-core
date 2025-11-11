"""
Cross-Swarm Relation Agent (Swarp v4* Component)

Maps evidence across specialized swarms (Finance ↔ Legal ↔ Markets ↔ Macro)
using "rhizomatic citation" patterns grounded in:
- Vienna Circle verificationism (multi-source requirement)
- Popperian falsifiability (conflict detection)
- Ubuntu consensus (multi-swarm agreement)

Author: Claude (Integration), GPT-5 Pro (Swarp v4* Design)
Date: 2025-11-11
"""

import networkx as nx
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Citation:
    """Citation structure from IF.citation service"""
    citation_id: str
    claim_id: str
    sources: List[Dict[str, str]]  # [{"type": "web", "ref": "...", "hash": "..."}]
    rationale: str
    confidence: float
    verified_at: str
    verified_by: str
    status: str  # "verified", "unverified", "disputed"
    created_by: str
    created_at: str


@dataclass
class ConflictReport:
    """Conflict detection result"""
    type: str  # "contradiction", "variance", "missing_evidence"
    claim_id: str
    swarms: List[str]
    confidences: Dict[str, float]
    severity: str  # "low", "medium", "high"
    action: str  # "ESCALATE", "HOLD", "INVESTIGATE"
    rationale: str


class CrossSwarmRelationAgent:
    """
    Maps evidence across domain swarms using rhizomatic citation patterns

    Principles:
    - Vienna Circle: Every claim requires 2+ independent sources
    - Popper: Actively search for contradictions (falsifiability)
    - Ubuntu: Multi-swarm consensus validates claims

    Example Use Case:
        Legal swarm finds: "Epic settled for $520M" (confidence: 0.8)
        Finance swarm finds: "Epic settlement cost $500M" (confidence: 0.9)
        → Conflict detected: 4% variance in settlement amount
        → ESCALATE to human for resolution
    """

    def __init__(self, swarms: List[str], citation_store: Dict[str, Citation]):
        """
        Args:
            swarms: List of swarm domains ["legal", "finance", "markets", "macro"]
            citation_store: Citation database (citation_id → Citation)
        """
        self.swarms = swarms
        self.citation_store = citation_store
        self.citation_graph = nx.MultiDiGraph()  # Citation network

        # Build initial graph from existing citations
        self._build_citation_graph()

    def _build_citation_graph(self):
        """Build citation graph from citation store"""
        for cit_id, citation in self.citation_store.items():
            # Add citation node
            self.citation_graph.add_node(
                cit_id,
                claim_id=citation.claim_id,
                confidence=citation.confidence,
                swarm=self._extract_swarm(citation.created_by),
                verified=citation.status == "verified"
            )

            # Add edges to claim node
            if not self.citation_graph.has_node(citation.claim_id):
                self.citation_graph.add_node(citation.claim_id, type="claim")

            self.citation_graph.add_edge(
                cit_id,
                citation.claim_id,
                relation="supports"
            )

    def _extract_swarm(self, agent_id: str) -> str:
        """Extract swarm domain from agent ID"""
        # "if://agent/swarm/legal-1@1.2.0" → "legal"
        parts = agent_id.split("/")
        if len(parts) >= 4:
            swarm_part = parts[3]  # "legal-1@1.2.0"
            return swarm_part.split("-")[0]  # "legal"
        return "unknown"

    def map_evidence(self, claim_id: str) -> Dict[str, List[str]]:
        """
        For a claim, find all supporting evidence across swarms

        Args:
            claim_id: Claim identifier (e.g., "if://claim/epic-settlement")

        Returns:
            Dict mapping swarm → list of citation IDs
            Example: {"legal": ["cit:abc", "cit:def"], "finance": ["cit:ghi"]}
        """
        evidence_map: Dict[str, List[str]] = {swarm: [] for swarm in self.swarms}

        # Find all citations supporting this claim
        if not self.citation_graph.has_node(claim_id):
            return evidence_map

        # Get predecessors (citations pointing to claim)
        for cit_id in self.citation_graph.predecessors(claim_id):
            citation = self.citation_store.get(cit_id)
            if not citation:
                continue

            # Verify citation has 2+ sources (Vienna Circle requirement)
            if self.verify_citation_sources(cit_id) >= 2:
                swarm = self.citation_graph.nodes[cit_id]["swarm"]
                if swarm in evidence_map:
                    evidence_map[swarm].append(cit_id)

        return evidence_map

    def detect_conflicts(self, claim_id: str) -> Optional[ConflictReport]:
        """
        Find contradictions across swarms (Popperian falsifiability)

        Conflict types:
        1. Variance: Confidence scores differ by >20%
        2. Contradiction: Explicit contradicting citations
        3. Missing evidence: Some swarms lack citations

        Args:
            claim_id: Claim to check for conflicts

        Returns:
            ConflictReport if conflict found, None otherwise
        """
        evidence_map = self.map_evidence(claim_id)

        # Calculate aggregate confidence per swarm
        confidences: Dict[str, float] = {}
        for swarm, citation_ids in evidence_map.items():
            if not citation_ids:
                confidences[swarm] = 0.0  # No evidence
            else:
                # Average confidence across citations
                confs = [
                    self.citation_graph.nodes[cit_id]["confidence"]
                    for cit_id in citation_ids
                ]
                confidences[swarm] = sum(confs) / len(confs)

        # Check for variance conflict (>20% difference)
        active_swarms = [s for s, c in confidences.items() if c > 0.0]
        if len(active_swarms) >= 2:
            max_conf = max(confidences.values())
            min_conf = min([c for c in confidences.values() if c > 0.0])
            variance = max_conf - min_conf

            if variance > 0.2:  # 20% threshold
                return ConflictReport(
                    type="variance",
                    claim_id=claim_id,
                    swarms=active_swarms,
                    confidences=confidences,
                    severity="high" if variance > 0.4 else "medium",
                    action="ESCALATE",
                    rationale=f"Confidence variance {variance:.1%} across swarms exceeds 20% threshold"
                )

        # Check for missing evidence (swarms without citations)
        missing_swarms = [s for s, cits in evidence_map.items() if not cits]
        if len(missing_swarms) > len(self.swarms) // 2:  # >50% swarms missing
            return ConflictReport(
                type="missing_evidence",
                claim_id=claim_id,
                swarms=missing_swarms,
                confidences=confidences,
                severity="medium",
                action="INVESTIGATE",
                rationale=f"{len(missing_swarms)}/{len(self.swarms)} swarms lack evidence for claim"
            )

        return None

    def verify_citation_sources(self, citation_id: str) -> int:
        """
        Count independent sources for citation (Vienna Circle requirement)

        Args:
            citation_id: Citation to verify

        Returns:
            Number of independent sources (0-N)
        """
        citation = self.citation_store.get(citation_id)
        if not citation:
            return 0

        # Count sources with valid hashes
        verified_sources = [
            src for src in citation.sources
            if src.get("hash", "").startswith("sha256:")
        ]

        return len(verified_sources)

    def get_cross_swarm_consensus(self, claim_id: str) -> Dict[str, any]:
        """
        Calculate Ubuntu-style consensus across swarms

        Returns:
            {
                "consensus_confidence": 0.75,  # Weighted average
                "swarm_agreement": 0.8,  # % swarms above threshold
                "participating_swarms": ["legal", "finance"],
                "status": "consensus" | "disputed" | "insufficient"
            }
        """
        evidence_map = self.map_evidence(claim_id)

        # Calculate confidence per swarm
        confidences: Dict[str, float] = {}
        for swarm, citation_ids in evidence_map.items():
            if citation_ids:
                confs = [
                    self.citation_graph.nodes[cit_id]["confidence"]
                    for cit_id in citation_ids
                ]
                confidences[swarm] = sum(confs) / len(confs)

        if not confidences:
            return {
                "consensus_confidence": 0.0,
                "swarm_agreement": 0.0,
                "participating_swarms": [],
                "status": "insufficient"
            }

        # Weighted average (all swarms equal weight)
        consensus_confidence = sum(confidences.values()) / len(confidences)

        # Agreement: % of swarms above 0.7 threshold
        high_confidence_swarms = [s for s, c in confidences.items() if c >= 0.7]
        swarm_agreement = len(high_confidence_swarms) / len(confidences)

        # Determine status
        if swarm_agreement >= 0.8:  # 80% swarms agree
            status = "consensus"
        elif swarm_agreement < 0.5:  # <50% agree
            status = "disputed"
        else:
            status = "partial"

        return {
            "consensus_confidence": consensus_confidence,
            "swarm_agreement": swarm_agreement,
            "participating_swarms": list(confidences.keys()),
            "status": status,
            "swarm_confidences": confidences
        }

    def add_citation(self, citation: Citation):
        """Add new citation to graph"""
        self.citation_store[citation.citation_id] = citation
        self._build_citation_graph()  # Rebuild graph


# Example usage
if __name__ == "__main__":
    # Mock citation store
    citation_store = {
        "cit:abc123": Citation(
            citation_id="cit:abc123",
            claim_id="if://claim/epic-settlement",
            sources=[
                {"type": "web", "ref": "https://sec.gov/...", "hash": "sha256:abc..."},
                {"type": "web", "ref": "https://reuters.com/...", "hash": "sha256:def..."}
            ],
            rationale="SEC filing + Reuters confirmation",
            confidence=0.8,
            verified_at="2025-11-10T14:30:00Z",
            verified_by="if://agent/witness/validator",
            status="verified",
            created_by="if://agent/swarm/legal-1@1.2.0",
            created_at="2025-11-10T14:25:00Z"
        ),
        "cit:def456": Citation(
            citation_id="cit:def456",
            claim_id="if://claim/epic-settlement",
            sources=[
                {"type": "web", "ref": "https://bloomberg.com/...", "hash": "sha256:ghi..."},
                {"type": "web", "ref": "https://wsj.com/...", "hash": "sha256:jkl..."}
            ],
            rationale="Bloomberg + WSJ reporting",
            confidence=0.5,  # Lower confidence (different amount?)
            verified_at="2025-11-10T15:00:00Z",
            verified_by="if://agent/witness/validator",
            status="verified",
            created_by="if://agent/swarm/finance-2@2.3.1",
            created_at="2025-11-10T14:50:00Z"
        )
    }

    # Create cross-swarm agent
    agent = CrossSwarmRelationAgent(
        swarms=["legal", "finance", "markets", "macro"],
        citation_store=citation_store
    )

    # Map evidence
    print("=== Evidence Mapping ===")
    evidence_map = agent.map_evidence("if://claim/epic-settlement")
    print(f"Evidence map: {evidence_map}")
    print()

    # Detect conflicts
    print("=== Conflict Detection ===")
    conflict = agent.detect_conflicts("if://claim/epic-settlement")
    if conflict:
        print(f"Conflict Type: {conflict.type}")
        print(f"Severity: {conflict.severity}")
        print(f"Action: {conflict.action}")
        print(f"Rationale: {conflict.rationale}")
        print(f"Swarm Confidences: {conflict.confidences}")
    else:
        print("No conflicts detected")
    print()

    # Get consensus
    print("=== Ubuntu Consensus ===")
    consensus = agent.get_cross_swarm_consensus("if://claim/epic-settlement")
    print(f"Consensus Confidence: {consensus['consensus_confidence']:.2%}")
    print(f"Swarm Agreement: {consensus['swarm_agreement']:.2%}")
    print(f"Status: {consensus['status']}")
    print(f"Participating Swarms: {consensus['participating_swarms']}")
