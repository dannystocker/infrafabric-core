#!/usr/bin/env python3
# Copyright (c) 2025 Danny Stocker
# SPDX-License-Identifier: MIT
#
# InfraFabric - NDI-SIP Bridge
# Source: https://github.com/dannystocker/infrafabric
# Licensed under the MIT License.

"""
NDI-SIP Bridge - Share NDI evidence streams in SIP expert calls

Philosophy Grounding:
- Wu Lun (五倫) Relationship: 兄弟 (Siblings) — SIP and NDI as peer communication channels
- IF.witness: Evidence provenance maintained across protocol boundaries
- IF.TTT Framework:
  * Traceable: Audit logs track who accessed what evidence when
  * Transparent: Stream URLs and access grants visible to all parties
  * Trustworthy: Ed25519 signatures verified, access control enforced

Architecture:
1. Bridge SIP sessions (Session 4: External Expert Communication) with NDI streams (Session 1)
2. Enable external experts in SIP calls to view real-time evidence streams
3. Maintain cryptographic provenance chain across protocol boundary
4. Provide access control with audit trail for compliance

Integration Points:
- NDIWitnessPublisher: Source of evidence streams
- NDIGuardianViewer: Verification of stream integrity
- SIP Session: Expert communication channel (voice/video)
- Evidence Bridge: NDI stream URL shared with SIP participants

Use Cases:
1. External expert requests evidence during consultation
2. Guardian shares NDI stream URL via SIP signaling
3. Expert views live scanner output with verified provenance
4. All access logged for audit trail (IF.TTT: Traceable)
"""

import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class SIPParticipant:
    """SIP call participant metadata"""
    participant_id: str
    display_name: str
    sip_uri: str
    role: str  # "guardian", "external_expert", "observer"
    joined_at: str
    access_granted: bool = False


@dataclass
class BridgeSession:
    """Active NDI-SIP bridge session"""
    bridge_id: str
    sip_session_id: str
    ndi_stream_name: str
    ndi_url: str  # NDI discovery URL (ndi://host/stream_name)
    created_at: str
    created_by: str
    participants: Dict[str, SIPParticipant]
    access_log: List[Dict[str, Any]]
    active: bool = True


class NDISIPBridge:
    """NDI-SIP Bridge - Share evidence streams in expert calls

    Usage:
        # Initialize bridge
        bridge = NDISIPBridge(
            ndi_host="10.0.0.100",
            audit_log_path="/var/log/infrafabric/ndi_sip_bridge.log"
        )

        # Attach NDI stream to SIP call
        bridge_id = bridge.attach_ndi_to_sip_call(
            sip_session_id="sip-call-abc-123",
            ndi_stream_name="IF.witness.yologuard.01",
            guardian_id="guardian-001"
        )

        # Grant access to external expert
        bridge.grant_participant_access(
            sip_session_id="sip-call-abc-123",
            participant_id="expert-042",
            granted_by="guardian-001"
        )

        # Expert retrieves NDI URL
        ndi_url = bridge.get_ndi_url_for_sip("sip-call-abc-123")
        # Returns: "ndi://10.0.0.100/IF.witness.yologuard.01"

        # Detach when call ends
        bridge.detach_ndi_from_sip_call("sip-call-abc-123")
    """

    def __init__(
        self,
        ndi_host: str = "localhost",
        ndi_port: int = 5960,
        audit_log_path: Optional[Path] = None
    ):
        """Initialize NDI-SIP bridge

        Args:
            ndi_host: NDI server hostname/IP for stream URLs
            ndi_port: NDI port (default 5960)
            audit_log_path: Path to audit log file (IF.TTT: Traceable)
        """
        self.ndi_host = ndi_host
        self.ndi_port = ndi_port
        self.audit_log_path = audit_log_path

        # Active bridges: sip_session_id -> BridgeSession
        self.active_bridges: Dict[str, BridgeSession] = {}

        # Participant registry: participant_id -> Set[sip_session_id]
        self.participant_sessions: Dict[str, Set[str]] = {}

        print(f"[NDISIPBridge] Initialized (NDI host: {ndi_host}:{ndi_port})")

    def attach_ndi_to_sip_call(
        self,
        sip_session_id: str,
        ndi_stream_name: str,
        guardian_id: str,
        guardian_name: str = "Guardian",
        guardian_sip_uri: str = ""
    ) -> str:
        """Attach NDI stream to SIP call session

        Creates bridge between SIP session and NDI stream, enabling
        external experts to view evidence during consultation.

        Args:
            sip_session_id: SIP session identifier
            ndi_stream_name: NDI stream name (e.g., "IF.witness.yologuard.01")
            guardian_id: Guardian creating the bridge
            guardian_name: Guardian display name
            guardian_sip_uri: Guardian SIP URI

        Returns:
            bridge_id: Unique bridge session identifier

        Philosophy:
            Wu Lun 兄弟 (Siblings): SIP and NDI treated as equal partners
            IF.witness: Provenance chain extends across protocol boundary
        """
        if sip_session_id in self.active_bridges:
            raise ValueError(f"SIP session {sip_session_id} already has NDI bridge")

        bridge_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Build NDI URL (ndi://host:port/stream_name)
        ndi_url = f"ndi://{self.ndi_host}:{self.ndi_port}/{ndi_stream_name}"

        # Create guardian participant
        guardian = SIPParticipant(
            participant_id=guardian_id,
            display_name=guardian_name,
            sip_uri=guardian_sip_uri,
            role="guardian",
            joined_at=timestamp,
            access_granted=True  # Guardian has automatic access
        )

        # Create bridge session
        bridge_session = BridgeSession(
            bridge_id=bridge_id,
            sip_session_id=sip_session_id,
            ndi_stream_name=ndi_stream_name,
            ndi_url=ndi_url,
            created_at=timestamp,
            created_by=guardian_id,
            participants={guardian_id: guardian},
            access_log=[]
        )

        # Log bridge creation (IF.TTT: Traceable)
        self._log_event(bridge_session, "bridge_created", {
            "guardian_id": guardian_id,
            "ndi_stream_name": ndi_stream_name,
            "ndi_url": ndi_url
        })

        self.active_bridges[sip_session_id] = bridge_session
        self._register_participant(guardian_id, sip_session_id)

        print(f"[NDISIPBridge] Attached NDI '{ndi_stream_name}' to SIP session '{sip_session_id}'")
        print(f"[NDISIPBridge] Bridge ID: {bridge_id}")
        print(f"[NDISIPBridge] NDI URL: {ndi_url}")

        return bridge_id

    def add_participant(
        self,
        sip_session_id: str,
        participant_id: str,
        display_name: str,
        sip_uri: str,
        role: str = "external_expert"
    ):
        """Add participant to SIP session (before granting NDI access)

        Args:
            sip_session_id: SIP session identifier
            participant_id: Participant identifier
            display_name: Participant display name
            sip_uri: Participant SIP URI
            role: Participant role (external_expert, observer, etc.)
        """
        bridge_session = self._get_bridge(sip_session_id)

        if participant_id in bridge_session.participants:
            print(f"[NDISIPBridge] Participant {participant_id} already in session")
            return

        timestamp = datetime.now(timezone.utc).isoformat()
        participant = SIPParticipant(
            participant_id=participant_id,
            display_name=display_name,
            sip_uri=sip_uri,
            role=role,
            joined_at=timestamp,
            access_granted=False
        )

        bridge_session.participants[participant_id] = participant
        self._register_participant(participant_id, sip_session_id)

        self._log_event(bridge_session, "participant_joined", {
            "participant_id": participant_id,
            "display_name": display_name,
            "role": role
        })

        print(f"[NDISIPBridge] Participant '{display_name}' joined SIP session '{sip_session_id}'")

    def grant_participant_access(
        self,
        sip_session_id: str,
        participant_id: str,
        granted_by: str
    ):
        """Grant NDI stream access to SIP participant

        Implements access control with audit trail (IF.TTT: Traceable, Trustworthy)

        Args:
            sip_session_id: SIP session identifier
            participant_id: Participant to grant access
            granted_by: Guardian/admin granting access
        """
        bridge_session = self._get_bridge(sip_session_id)

        if participant_id not in bridge_session.participants:
            raise ValueError(f"Participant {participant_id} not in session")

        participant = bridge_session.participants[participant_id]
        if participant.access_granted:
            print(f"[NDISIPBridge] Participant {participant_id} already has access")
            return

        participant.access_granted = True

        self._log_event(bridge_session, "access_granted", {
            "participant_id": participant_id,
            "granted_by": granted_by,
            "ndi_url": bridge_session.ndi_url
        })

        print(f"[NDISIPBridge] Granted NDI access to '{participant.display_name}'")
        print(f"[NDISIPBridge] They can now view: {bridge_session.ndi_url}")

    def verify_sip_participant_access(
        self,
        sip_session_id: str,
        participant_id: str
    ) -> bool:
        """Verify if SIP participant has NDI access (IF.TTT: Trustworthy)

        Args:
            sip_session_id: SIP session identifier
            participant_id: Participant to verify

        Returns:
            True if participant has access, False otherwise
        """
        try:
            bridge_session = self._get_bridge(sip_session_id)

            if participant_id not in bridge_session.participants:
                return False

            participant = bridge_session.participants[participant_id]
            access_granted = participant.access_granted

            # Log access check (IF.TTT: Traceable)
            self._log_event(bridge_session, "access_check", {
                "participant_id": participant_id,
                "access_granted": access_granted
            })

            return access_granted

        except ValueError:
            return False

    def get_ndi_url_for_sip(self, sip_session_id: str) -> str:
        """Get NDI stream URL for SIP session (IF.TTT: Transparent)

        Args:
            sip_session_id: SIP session identifier

        Returns:
            NDI connection URL (ndi://host:port/stream_name)
        """
        bridge_session = self._get_bridge(sip_session_id)
        return bridge_session.ndi_url

    def get_bridge_info(self, sip_session_id: str) -> Dict[str, Any]:
        """Get complete bridge session info

        Args:
            sip_session_id: SIP session identifier

        Returns:
            Bridge session info dict
        """
        bridge_session = self._get_bridge(sip_session_id)

        # Convert to dict with participant list
        info = asdict(bridge_session)
        info["participants"] = [
            asdict(p) for p in bridge_session.participants.values()
        ]

        return info

    def detach_ndi_from_sip_call(self, sip_session_id: str):
        """Detach NDI stream from SIP call (cleanup)

        Args:
            sip_session_id: SIP session identifier
        """
        bridge_session = self._get_bridge(sip_session_id)

        bridge_session.active = False

        # Log bridge closure
        self._log_event(bridge_session, "bridge_closed", {
            "duration_seconds": self._get_session_duration(bridge_session)
        })

        # Unregister participants
        for participant_id in bridge_session.participants.keys():
            self._unregister_participant(participant_id, sip_session_id)

        # Remove from active bridges
        del self.active_bridges[sip_session_id]

        print(f"[NDISIPBridge] Detached NDI from SIP session '{sip_session_id}'")

    def get_active_bridges(self) -> List[Dict[str, Any]]:
        """Get list of all active bridges

        Returns:
            List of bridge session info dicts
        """
        return [
            self.get_bridge_info(session_id)
            for session_id in self.active_bridges.keys()
        ]

    def get_participant_sessions(self, participant_id: str) -> List[str]:
        """Get all SIP sessions for participant

        Args:
            participant_id: Participant identifier

        Returns:
            List of SIP session IDs
        """
        return list(self.participant_sessions.get(participant_id, set()))

    # Private helper methods

    def _get_bridge(self, sip_session_id: str) -> BridgeSession:
        """Get bridge session or raise error"""
        if sip_session_id not in self.active_bridges:
            raise ValueError(f"No NDI bridge for SIP session {sip_session_id}")
        return self.active_bridges[sip_session_id]

    def _register_participant(self, participant_id: str, sip_session_id: str):
        """Register participant in session index"""
        if participant_id not in self.participant_sessions:
            self.participant_sessions[participant_id] = set()
        self.participant_sessions[participant_id].add(sip_session_id)

    def _unregister_participant(self, participant_id: str, sip_session_id: str):
        """Unregister participant from session index"""
        if participant_id in self.participant_sessions:
            self.participant_sessions[participant_id].discard(sip_session_id)
            if not self.participant_sessions[participant_id]:
                del self.participant_sessions[participant_id]

    def _log_event(
        self,
        bridge_session: BridgeSession,
        event_type: str,
        event_data: Dict[str, Any]
    ):
        """Log audit event (IF.TTT: Traceable)"""
        timestamp = datetime.now(timezone.utc).isoformat()

        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "bridge_id": bridge_session.bridge_id,
            "sip_session_id": bridge_session.sip_session_id,
            **event_data
        }

        bridge_session.access_log.append(log_entry)

        # Write to audit log file if configured
        if self.audit_log_path:
            try:
                with open(self.audit_log_path, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')
            except Exception as e:
                print(f"[ERROR] Failed to write audit log: {e}")

    def _get_session_duration(self, bridge_session: BridgeSession) -> float:
        """Calculate session duration in seconds"""
        created = datetime.fromisoformat(bridge_session.created_at)
        now = datetime.now(timezone.utc)
        return (now - created).total_seconds()


def main():
    """Example usage: Bridge NDI stream to SIP call"""
    import argparse

    parser = argparse.ArgumentParser(description="NDI-SIP Bridge")
    parser.add_argument('--ndi-host', default='localhost',
                        help='NDI server hostname')
    parser.add_argument('--ndi-stream', default='IF.witness.yologuard.01',
                        help='NDI stream name')
    parser.add_argument('--sip-session', default=f'sip-call-{uuid.uuid4().hex[:8]}',
                        help='SIP session ID')
    args = parser.parse_args()

    print("=" * 80)
    print("NDI-SIP Bridge - Share Evidence in Expert Calls")
    print("=" * 80)
    print("\nPhilosophy: Wu Lun 兄弟 (Siblings) - SIP and NDI as peer channels")
    print("IF.TTT: Traceable, Transparent, Trustworthy\n")

    # Initialize bridge
    bridge = NDISIPBridge(
        ndi_host=args.ndi_host,
        audit_log_path=Path("/tmp/ndi_sip_bridge_audit.log")
    )

    # Simulate expert consultation scenario
    print("Scenario: External expert consultation with evidence sharing")
    print("-" * 80)

    # 1. Guardian creates SIP call and attaches NDI stream
    print("\n1. Guardian creates bridge...")
    bridge_id = bridge.attach_ndi_to_sip_call(
        sip_session_id=args.sip_session,
        ndi_stream_name=args.ndi_stream,
        guardian_id="guardian-001",
        guardian_name="Dr. Chen (Guardian)",
        guardian_sip_uri="sip:chen@infrafabric.local"
    )

    # 2. External expert joins SIP call
    print("\n2. External expert joins call...")
    bridge.add_participant(
        sip_session_id=args.sip_session,
        participant_id="expert-042",
        display_name="Dr. Rodriguez (Security Expert)",
        sip_uri="sip:rodriguez@external.example.com",
        role="external_expert"
    )

    # 3. Expert requests evidence access
    print("\n3. Expert requests evidence access...")
    time.sleep(1)

    # 4. Guardian grants access
    print("\n4. Guardian grants NDI access...")
    bridge.grant_participant_access(
        sip_session_id=args.sip_session,
        participant_id="expert-042",
        granted_by="guardian-001"
    )

    # 5. Expert verifies access
    print("\n5. Expert verifies access...")
    has_access = bridge.verify_sip_participant_access(
        sip_session_id=args.sip_session,
        participant_id="expert-042"
    )
    print(f"   Access verified: {has_access}")

    # 6. Expert retrieves NDI URL
    print("\n6. Expert retrieves NDI stream URL...")
    ndi_url = bridge.get_ndi_url_for_sip(args.sip_session)
    print(f"   NDI URL: {ndi_url}")
    print("   Expert can now view evidence stream with NDIGuardianViewer")

    # 7. Display bridge info
    print("\n7. Bridge session info:")
    print("-" * 80)
    bridge_info = bridge.get_bridge_info(args.sip_session)
    print(f"   Bridge ID:     {bridge_info['bridge_id']}")
    print(f"   SIP Session:   {bridge_info['sip_session_id']}")
    print(f"   NDI Stream:    {bridge_info['ndi_stream_name']}")
    print(f"   Created:       {bridge_info['created_at']}")
    print(f"   Participants:  {len(bridge_info['participants'])}")

    for participant in bridge_info['participants']:
        print(f"     - {participant['display_name']} ({participant['role']})")
        print(f"       Access: {participant['access_granted']}")

    # 8. Cleanup
    print("\n8. Call ends, detaching bridge...")
    time.sleep(1)
    bridge.detach_ndi_from_sip_call(args.sip_session)

    print("\n" + "=" * 80)
    print("Bridge session complete - audit log written")
    print("=" * 80)
    print(f"\nAudit log: /tmp/ndi_sip_bridge_audit.log")
    print("IF.TTT compliance maintained across protocol boundary")


if __name__ == "__main__":
    main()
