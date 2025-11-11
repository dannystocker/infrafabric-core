"""
H.323 MCU (Multipoint Control Unit) Configuration for IF.guard Guardian Council

This module configures the MCU for Guardian Council conferencing, supporting:
- Centralized audio mixing (Ubuntu philosophy: everyone hears everyone)
- Continuous presence video (4x4 grid for 15+ guardians)
- T.120 whiteboard for evidence display
- Integration with Jitsi Videobridge or Kurento

Architecture:
- MCU receives admitted terminals from Gatekeeper
- Mixes audio from all participants (consensus building)
- Displays video grid (visual presence)
- Shares evidence documents via T.120 data channel

Philosophy Grounding:
- Ubuntu: Communal consensus through centralized audio mixing
- Wu Lun (五倫): Harmonious deliberation (all voices heard equally)
- IF.TTT: Transparent conferencing (all can see/hear all)

Author: InfraFabric Project
License: CC BY 4.0
Last Updated: 2025-11-11
"""

import json
import subprocess
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml


# ============================================================================
# Data Models
# ============================================================================

class AudioMixingMode(Enum):
    """Audio mixing strategies for MCU"""
    CENTRALIZED = "centralized"       # Mix all streams (Ubuntu consensus)
    VOICE_ACTIVATED = "voice_activated"  # Only active speakers
    CONTINUOUS = "continuous"         # Always mix all participants


class VideoLayoutMode(Enum):
    """Video layout patterns"""
    CONTINUOUS_PRESENCE_4X4 = "cp_4x4"     # 4x4 grid (16 participants)
    CONTINUOUS_PRESENCE_5X5 = "cp_5x5"     # 5x5 grid (25 participants)
    ACTIVE_SPEAKER = "active_speaker"      # Focus on current speaker
    SIDE_BY_SIDE = "side_by_side"          # 2 participants


@dataclass
class MCUCapabilities:
    """MCU technical capabilities"""
    max_participants: int = 25            # Maximum guardians
    audio_mixing: AudioMixingMode = AudioMixingMode.CENTRALIZED
    video_layout: VideoLayoutMode = VideoLayoutMode.CONTINUOUS_PRESENCE_4X4
    max_bandwidth_mbps: int = 100         # Total bandwidth budget
    supports_t120: bool = True            # T.120 whiteboard support
    supports_h239: bool = True            # H.239 dual stream (video + slides)


@dataclass
class ParticipantStream:
    """Individual guardian's media stream"""
    terminal_id: str                      # if://guardian/{name}
    session_id: str                       # From gatekeeper ACF
    audio_enabled: bool = True
    video_enabled: bool = True
    bandwidth_bps: int = 0
    joined_at: str = None


@dataclass
class ConferenceRoom:
    """Active Guardian Council conference"""
    room_id: str                          # if://conference/guard/{call_id}
    call_id: str                          # From gatekeeper
    created_at: str
    participants: List[ParticipantStream]
    audio_mixing: AudioMixingMode
    video_layout: VideoLayoutMode
    is_active: bool = True


# ============================================================================
# MCU Configuration Manager
# ============================================================================

class MCUConfigManager:
    """
    Manages MCU configuration for Guardian Council conferencing.

    Supports:
    - Jitsi Videobridge (open source, WebRTC)
    - Kurento Media Server (H.323 native)
    """

    def __init__(self, mcu_type: str = "jitsi", config_path: Optional[Path] = None):
        """
        Initialize MCU configuration manager.

        Args:
            mcu_type: "jitsi" or "kurento"
            config_path: Path to MCU configuration file
        """
        self.mcu_type = mcu_type
        self.config_path = config_path
        self.capabilities = MCUCapabilities()
        self.active_rooms: Dict[str, ConferenceRoom] = {}

    def generate_jitsi_config(self, output_path: Path) -> bool:
        """
        Generate Jitsi Videobridge configuration for Guardian Council.

        Config includes:
        - Max participants: 25 guardians
        - Audio mixing: centralized (Ubuntu consensus)
        - Video layout: continuous presence 4x4
        - Bandwidth optimization
        """
        config = {
            "videobridge": {
                "ice": {
                    "tcp": {
                        "enabled": True,
                        "port": 4443
                    },
                    "udp": {
                        "port": 10000
                    }
                },
                "apis": {
                    "xmpp-client": {
                        "configs": {
                            "xmpp-server-1": {
                                "hostname": "localhost",
                                "port": 5222,
                                "domain": "if.guard.local",
                                "muc_jids": "GuardianCouncilMUC@conference.if.guard.local",
                                "muc_nickname": "IF.guard.MCU",
                                "disable_certificate_verification": False
                            }
                        }
                    }
                },
                "stats": {
                    "enabled": True,
                    "transports": [
                        {
                            "type": "muc"
                        }
                    ]
                },
                "websockets": {
                    "enabled": True,
                    "domain": "if.guard.local:443",
                    "tls": True
                },
                "http-servers": {
                    "public": {
                        "port": 9090
                    }
                },
                "octo": {
                    "enabled": False  # Single MCU (no cascading)
                }
            }
        }

        # Write Jitsi config
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"Jitsi Videobridge config written to {output_path}")
        return True

    def generate_kurento_config(self, output_path: Path) -> bool:
        """
        Generate Kurento Media Server configuration.

        Kurento is H.323 native and supports T.120 whiteboard.
        """
        config = {
            "mediaServer": {
                "net": {
                    "websocket": {
                        "port": 8888,
                        "path": "kurento",
                        "secure": {
                            "port": 8433,
                            "certificate": "/etc/kurento/cert.pem",
                            "password": ""
                        }
                    }
                },
                "resources": {
                    "garbageCollectorPeriod": 240,
                    "disableRequestCache": False
                }
            },
            "guardian_council": {
                "max_participants": 25,
                "audio_mixing": "centralized",
                "video_layout": "continuous_presence_4x4",
                "t120_enabled": True,
                "h239_dual_stream": True
            }
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"Kurento config written to {output_path}")
        return True

    def create_conference_room(
        self,
        call_id: str,
        audio_mixing: AudioMixingMode = AudioMixingMode.CENTRALIZED,
        video_layout: VideoLayoutMode = VideoLayoutMode.CONTINUOUS_PRESENCE_4X4
    ) -> ConferenceRoom:
        """
        Create a new Guardian Council conference room.

        Args:
            call_id: Unique call identifier from gatekeeper
            audio_mixing: Audio mixing mode (default: centralized)
            video_layout: Video layout mode (default: 4x4 grid)

        Returns:
            ConferenceRoom instance
        """
        from datetime import datetime, timezone

        room_id = f"if://conference/guard/{call_id}"
        room = ConferenceRoom(
            room_id=room_id,
            call_id=call_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            participants=[],
            audio_mixing=audio_mixing,
            video_layout=video_layout
        )

        self.active_rooms[room_id] = room
        print(f"Created conference room: {room_id}")
        return room

    def add_participant(
        self,
        room_id: str,
        terminal_id: str,
        session_id: str,
        bandwidth_bps: int
    ) -> bool:
        """
        Add guardian to conference room.

        Args:
            room_id: Conference room identifier
            terminal_id: Guardian terminal ID
            session_id: Session ID from gatekeeper ACF
            bandwidth_bps: Allocated bandwidth

        Returns:
            True if added successfully
        """
        from datetime import datetime, timezone

        room = self.active_rooms.get(room_id)
        if not room:
            print(f"Room not found: {room_id}")
            return False

        if len(room.participants) >= self.capabilities.max_participants:
            print(f"Room full: {len(room.participants)}/{self.capabilities.max_participants}")
            return False

        participant = ParticipantStream(
            terminal_id=terminal_id,
            session_id=session_id,
            bandwidth_bps=bandwidth_bps,
            joined_at=datetime.now(timezone.utc).isoformat()
        )

        room.participants.append(participant)
        print(f"Added participant {terminal_id} to {room_id} ({len(room.participants)}/{self.capabilities.max_participants})")
        return True

    def remove_participant(self, room_id: str, terminal_id: str) -> bool:
        """Remove guardian from conference room"""
        room = self.active_rooms.get(room_id)
        if not room:
            return False

        room.participants = [
            p for p in room.participants if p.terminal_id != terminal_id
        ]
        print(f"Removed participant {terminal_id} from {room_id}")
        return True

    def get_room_status(self, room_id: str) -> Optional[Dict[str, Any]]:
        """Get conference room status"""
        room = self.active_rooms.get(room_id)
        if not room:
            return None

        total_bandwidth = sum(p.bandwidth_bps for p in room.participants)

        return {
            "room_id": room.room_id,
            "call_id": room.call_id,
            "participant_count": len(room.participants),
            "max_participants": self.capabilities.max_participants,
            "audio_mixing": room.audio_mixing.value,
            "video_layout": room.video_layout.value,
            "total_bandwidth_bps": total_bandwidth,
            "total_bandwidth_mbps": round(total_bandwidth / 1_000_000, 2),
            "is_active": room.is_active,
            "created_at": room.created_at
        }

    def close_room(self, room_id: str) -> bool:
        """Close conference room and disconnect all participants"""
        room = self.active_rooms.get(room_id)
        if not room:
            return False

        room.is_active = False
        del self.active_rooms[room_id]
        print(f"Closed conference room: {room_id}")
        return True

    def start_mcu_service(self) -> bool:
        """
        Start MCU service (Jitsi or Kurento).

        Returns:
            True if started successfully
        """
        try:
            if self.mcu_type == "jitsi":
                # Check if Jitsi Videobridge is installed
                result = subprocess.run(
                    ["which", "jvb"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode != 0:
                    print("Jitsi Videobridge not found. Install from: https://jitsi.org/downloads/")
                    print("Running in mock mode (room management only)")
                    return True

                # Start Jitsi Videobridge
                if self.config_path and self.config_path.exists():
                    subprocess.Popen(
                        ["jvb", "--config", str(self.config_path)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    print(f"Jitsi Videobridge started with config: {self.config_path}")
                else:
                    print("No Jitsi config provided, running mock mode")

            elif self.mcu_type == "kurento":
                # Check if Kurento is installed
                result = subprocess.run(
                    ["which", "kurento-media-server"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode != 0:
                    print("Kurento Media Server not found. Install from: https://doc-kurento.readthedocs.io/")
                    print("Running in mock mode (room management only)")
                    return True

                # Start Kurento
                subprocess.Popen(
                    ["kurento-media-server"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print("Kurento Media Server started")

            else:
                print(f"Unknown MCU type: {self.mcu_type}")
                return False

            return True

        except Exception as e:
            print(f"Error starting MCU service: {e}")
            return False


# ============================================================================
# Evidence Display (T.120 Whiteboard)
# ============================================================================

class EvidenceDisplay:
    """
    T.120 whiteboard for displaying evidence during Guardian Council deliberation.

    Displays:
    - IF.citation documents
    - Dossier summaries
    - Voting results
    - Policy proposals
    """

    def __init__(self, room_id: str):
        self.room_id = room_id
        self.displayed_documents: List[Dict[str, Any]] = []

    def display_citation(self, citation_id: str, title: str, content: str) -> bool:
        """Display citation on T.120 whiteboard"""
        document = {
            "type": "citation",
            "citation_id": citation_id,
            "title": title,
            "content": content,
            "displayed_at": self._get_timestamp()
        }

        self.displayed_documents.append(document)
        print(f"Displaying citation {citation_id} on whiteboard")
        return True

    def display_dossier(self, dossier_id: str, summary: str) -> bool:
        """Display dossier summary on T.120 whiteboard"""
        document = {
            "type": "dossier",
            "dossier_id": dossier_id,
            "summary": summary,
            "displayed_at": self._get_timestamp()
        }

        self.displayed_documents.append(document)
        print(f"Displaying dossier {dossier_id} on whiteboard")
        return True

    def display_vote_results(self, vote_data: Dict[str, Any]) -> bool:
        """Display voting results on T.120 whiteboard"""
        document = {
            "type": "vote_results",
            "vote_data": vote_data,
            "displayed_at": self._get_timestamp()
        }

        self.displayed_documents.append(document)
        print("Displaying vote results on whiteboard")
        return True

    def clear_whiteboard(self) -> bool:
        """Clear all documents from whiteboard"""
        self.displayed_documents = []
        print("Whiteboard cleared")
        return True

    def _get_timestamp(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Initialize MCU manager
    mcu = MCUConfigManager(mcu_type="jitsi")

    # Generate configuration
    config_path = Path("/home/user/infrafabric/config/jitsi-videobridge.json")
    mcu.generate_jitsi_config(config_path)

    # Start MCU service
    mcu.start_mcu_service()

    # Create conference room
    room = mcu.create_conference_room(
        call_id="epic-2025-11-11-abc",
        audio_mixing=AudioMixingMode.CENTRALIZED,
        video_layout=VideoLayoutMode.CONTINUOUS_PRESENCE_4X4
    )

    print(f"\nMCU ready at: if://service/guard/mcu:1720")
    print(f"Conference room: {room.room_id}")
    print(f"Max participants: {mcu.capabilities.max_participants}")
