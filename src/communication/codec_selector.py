"""
Intelligent Codec Selection for H.323 Guardian Council

This module implements smart codec selection to optimize bandwidth efficiency
while maintaining quality. Preferences VP8 over H.264 for video (royalty-free,
better browser support) and Opus over G.711 for audio (lower bandwidth).

Codec Selection Strategy:
1. Prefer open, royalty-free codecs (VP8, Opus)
2. Analyze available bandwidth before selecting codec
3. Downgrade quality gracefully under bandwidth constraints
4. Negotiate common codec across all MCU participants

Optimization Goals:
- Reduce bandwidth by 30-50% (H.264 → VP8, G.711 → Opus)
- Maintain quality (PESQ >4.0 for audio, PSNR >35 dB for video)
- Support heterogeneous endpoints (H.323, SIP, WebRTC, NDI)

Philosophy:
- Wu Lun (五倫): 朋友 (Friend-Friend) - Accommodate diverse endpoints
- Ubuntu: Inclusive participation - No endpoint left behind
- Kantian Duty: Efficient resource use - Minimize bandwidth waste
- IF.TTT: Transparent codec selection

Author: InfraFabric Project
License: CC BY 4.0
Last Updated: 2025-11-11
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

# ============================================================================
# Data Models
# ============================================================================

class CodecType(Enum):
    """Codec media types"""
    AUDIO = "audio"
    VIDEO = "video"


class CodecCategory(Enum):
    """Codec licensing category"""
    OPEN_SOURCE = "open_source"      # Royalty-free (VP8, Opus)
    PROPRIETARY = "proprietary"      # Licensed (H.264, G.729)
    LEGACY = "legacy"                # Older codecs (G.711)


@dataclass
class CodecProfile:
    """Profile for a supported codec"""
    name: str                        # Codec name (e.g., "VP8", "Opus")
    media_type: CodecType            # Audio or video
    category: CodecCategory          # Open source, proprietary, legacy
    bandwidth_kbps: int              # Typical bandwidth usage
    quality_score: float             # Quality metric (1-10, higher better)
    browser_support: bool            # WebRTC browser support
    hardware_accel: bool             # Hardware acceleration available
    latency_ms: int                  # Encoding/decoding latency
    cpu_cost_percent: int            # CPU usage (% per stream)

    def efficiency_score(self) -> float:
        """
        Compute efficiency score (quality per bandwidth).

        Returns:
            Efficiency score (higher is better)
        """
        return (self.quality_score * 10) / max(self.bandwidth_kbps, 1)


# ============================================================================
# Codec Database
# ============================================================================

class CodecDatabase:
    """
    Database of supported codecs with their characteristics.
    """

    CODECS = [
        # Audio Codecs
        CodecProfile(
            name="Opus",
            media_type=CodecType.AUDIO,
            category=CodecCategory.OPEN_SOURCE,
            bandwidth_kbps=32,           # Adaptive 6-510 kbps, typical 32
            quality_score=9.5,           # Excellent quality
            browser_support=True,
            hardware_accel=False,
            latency_ms=5,                # Very low latency
            cpu_cost_percent=15
        ),
        CodecProfile(
            name="G.711",
            media_type=CodecType.AUDIO,
            category=CodecCategory.LEGACY,
            bandwidth_kbps=64,
            quality_score=8.0,           # Good quality
            browser_support=True,
            hardware_accel=True,
            latency_ms=2,                # Extremely low latency
            cpu_cost_percent=5
        ),
        CodecProfile(
            name="G.729",
            media_type=CodecType.AUDIO,
            category=CodecCategory.PROPRIETARY,
            bandwidth_kbps=8,
            quality_score=7.0,           # Acceptable quality
            browser_support=False,
            hardware_accel=True,
            latency_ms=15,               # Moderate latency
            cpu_cost_percent=25
        ),
        CodecProfile(
            name="AMR",
            media_type=CodecType.AUDIO,
            category=CodecCategory.PROPRIETARY,
            bandwidth_kbps=12,
            quality_score=6.5,
            browser_support=False,
            hardware_accel=False,
            latency_ms=20,
            cpu_cost_percent=30
        ),

        # Video Codecs
        CodecProfile(
            name="VP8",
            media_type=CodecType.VIDEO,
            category=CodecCategory.OPEN_SOURCE,
            bandwidth_kbps=1000,         # ~1 Mbps typical for 720p
            quality_score=8.5,           # Very good quality
            browser_support=True,
            hardware_accel=True,         # Modern GPUs support VP8
            latency_ms=30,
            cpu_cost_percent=40
        ),
        CodecProfile(
            name="H.264",
            media_type=CodecType.VIDEO,
            category=CodecCategory.PROPRIETARY,
            bandwidth_kbps=1200,         # ~1.2 Mbps typical for 720p
            quality_score=9.0,           # Excellent quality
            browser_support=True,
            hardware_accel=True,
            latency_ms=40,
            cpu_cost_percent=35
        ),
        CodecProfile(
            name="VP9",
            media_type=CodecType.VIDEO,
            category=CodecCategory.OPEN_SOURCE,
            bandwidth_kbps=700,          # ~700 kbps typical for 720p
            quality_score=9.0,           # Excellent quality
            browser_support=True,
            hardware_accel=True,         # Newer GPUs only
            latency_ms=50,
            cpu_cost_percent=60
        ),
        CodecProfile(
            name="H.263",
            media_type=CodecType.VIDEO,
            category=CodecCategory.LEGACY,
            bandwidth_kbps=500,
            quality_score=6.0,           # Poor quality (legacy)
            browser_support=False,
            hardware_accel=False,
            latency_ms=30,
            cpu_cost_percent=20
        ),
    ]

    @classmethod
    def get_codec(cls, name: str) -> Optional[CodecProfile]:
        """Get codec profile by name."""
        for codec in cls.CODECS:
            if codec.name.lower() == name.lower():
                return codec
        return None

    @classmethod
    def get_codecs_by_type(cls, media_type: CodecType) -> List[CodecProfile]:
        """Get all codecs of a specific media type."""
        return [c for c in cls.CODECS if c.media_type == media_type]


# ============================================================================
# Codec Selector
# ============================================================================

class CodecSelector:
    """
    Intelligent codec selector for Guardian Council MCU.

    Selects optimal codec based on:
    1. Available bandwidth
    2. Endpoint capabilities (H.323, SIP, WebRTC, NDI)
    3. Quality requirements
    4. Hardware acceleration availability
    """

    # Codec preference order (higher index = higher preference)
    AUDIO_CODEC_PREFERENCE = ["Opus", "G.711", "G.729", "AMR"]
    VIDEO_CODEC_PREFERENCE = ["VP8", "VP9", "H.264", "H.263"]

    # Bandwidth thresholds for quality levels
    BANDWIDTH_THRESHOLDS = {
        "low": 500_000,          # <500 kbps: Low quality
        "medium": 2_000_000,     # 500kbps-2Mbps: Medium quality
        "high": 5_000_000        # >2Mbps: High quality
    }

    def __init__(self):
        self.db = CodecDatabase()

    def select_audio_codec(
        self,
        available_bandwidth_bps: int,
        endpoint_capabilities: List[str],
        prefer_open_source: bool = True,
        require_browser_support: bool = False
    ) -> CodecProfile:
        """
        Select optimal audio codec.

        Args:
            available_bandwidth_bps: Available bandwidth (bits/sec)
            endpoint_capabilities: List of codecs supported by endpoint
            prefer_open_source: Prefer royalty-free codecs
            require_browser_support: Require WebRTC browser support

        Returns:
            Selected codec profile
        """
        audio_codecs = self.db.get_codecs_by_type(CodecType.AUDIO)

        # Filter by endpoint capabilities
        if endpoint_capabilities:
            audio_codecs = [
                c for c in audio_codecs
                if c.name in endpoint_capabilities
            ]

        # Filter by browser support requirement
        if require_browser_support:
            audio_codecs = [c for c in audio_codecs if c.browser_support]

        # Filter by bandwidth constraint
        available_bandwidth_kbps = available_bandwidth_bps // 1000
        audio_codecs = [
            c for c in audio_codecs
            if c.bandwidth_kbps <= available_bandwidth_kbps
        ]

        if not audio_codecs:
            # Fallback to G.711 (universally supported)
            return self.db.get_codec("G.711")

        # Sort by preference order
        def preference_key(codec: CodecProfile) -> int:
            try:
                return self.AUDIO_CODEC_PREFERENCE.index(codec.name)
            except ValueError:
                return -1

        # Apply preference order
        audio_codecs.sort(key=preference_key, reverse=True)

        # If prefer open source, prioritize those
        if prefer_open_source:
            open_source = [c for c in audio_codecs if c.category == CodecCategory.OPEN_SOURCE]
            if open_source:
                return open_source[0]

        return audio_codecs[0]

    def select_video_codec(
        self,
        available_bandwidth_bps: int,
        endpoint_capabilities: List[str],
        prefer_open_source: bool = True,
        hardware_accel_available: bool = False,
        resolution: str = "720p"
    ) -> CodecProfile:
        """
        Select optimal video codec.

        Args:
            available_bandwidth_bps: Available bandwidth (bits/sec)
            endpoint_capabilities: List of codecs supported by endpoint
            prefer_open_source: Prefer royalty-free codecs (VP8/VP9 over H.264)
            hardware_accel_available: Hardware encoding/decoding available
            resolution: Target resolution (720p, 1080p, etc.)

        Returns:
            Selected codec profile
        """
        video_codecs = self.db.get_codecs_by_type(CodecType.VIDEO)

        # Filter by endpoint capabilities
        if endpoint_capabilities:
            video_codecs = [
                c for c in video_codecs
                if c.name in endpoint_capabilities
            ]

        # Filter by bandwidth constraint
        available_bandwidth_kbps = available_bandwidth_bps // 1000
        video_codecs = [
            c for c in video_codecs
            if c.bandwidth_kbps <= available_bandwidth_kbps
        ]

        if not video_codecs:
            # Fallback to H.263 (lowest bandwidth)
            return self.db.get_codec("H.263")

        # Sort by preference order
        def preference_key(codec: CodecProfile) -> int:
            try:
                return self.VIDEO_CODEC_PREFERENCE.index(codec.name)
            except ValueError:
                return -1

        video_codecs.sort(key=preference_key, reverse=True)

        # If prefer open source, prioritize VP8/VP9
        if prefer_open_source:
            open_source = [c for c in video_codecs if c.category == CodecCategory.OPEN_SOURCE]
            if open_source:
                # Prefer VP8 over VP9 for better hardware support
                vp8 = [c for c in open_source if c.name == "VP8"]
                if vp8:
                    return vp8[0]
                return open_source[0]

        return video_codecs[0]

    def negotiate_common_codec(
        self,
        participants: List[Dict[str, any]],
        media_type: CodecType
    ) -> Optional[CodecProfile]:
        """
        Negotiate common codec supported by all participants.

        Args:
            participants: List of participant dicts with 'capabilities' key
            media_type: Audio or video

        Returns:
            Common codec, or None if no common codec
        """
        if not participants:
            return None

        # Get codec capabilities for all participants
        all_capabilities = [p.get('capabilities', []) for p in participants]

        # Find intersection of capabilities
        common_codecs = set(all_capabilities[0])
        for caps in all_capabilities[1:]:
            common_codecs &= set(caps)

        if not common_codecs:
            return None

        # Select best codec from common set
        codecs_by_type = self.db.get_codecs_by_type(media_type)
        common_codec_profiles = [
            c for c in codecs_by_type
            if c.name in common_codecs
        ]

        if not common_codec_profiles:
            return None

        # Return highest preference codec
        preference = (
            self.AUDIO_CODEC_PREFERENCE if media_type == CodecType.AUDIO
            else self.VIDEO_CODEC_PREFERENCE
        )

        def preference_key(codec: CodecProfile) -> int:
            try:
                return preference.index(codec.name)
            except ValueError:
                return -1

        common_codec_profiles.sort(key=preference_key, reverse=True)
        return common_codec_profiles[0]


# ============================================================================
# Bandwidth Analyzer
# ============================================================================

class BandwidthAnalyzer:
    """
    Analyzes bandwidth usage and recommends codec downgrades if needed.
    """

    def __init__(self):
        self.selector = CodecSelector()

    def analyze_guardian_bandwidth(
        self,
        num_guardians: int,
        video_enabled: bool = True
    ) -> Dict[str, any]:
        """
        Analyze total bandwidth for Guardian Council meeting.

        Args:
            num_guardians: Number of concurrent guardians
            video_enabled: Whether video is enabled

        Returns:
            Bandwidth analysis with recommendations
        """
        # Default codec selection
        audio_codec = self.selector.select_audio_codec(
            available_bandwidth_bps=10_000_000,  # 10 Mbps
            endpoint_capabilities=["Opus", "G.711"],
            prefer_open_source=True
        )

        video_codec = None
        if video_enabled:
            video_codec = self.selector.select_video_codec(
                available_bandwidth_bps=10_000_000,
                endpoint_capabilities=["VP8", "H.264"],
                prefer_open_source=True
            )

        # Calculate per-guardian bandwidth
        per_guardian_audio_kbps = audio_codec.bandwidth_kbps
        per_guardian_video_kbps = video_codec.bandwidth_kbps if video_codec else 0
        per_guardian_total_kbps = per_guardian_audio_kbps + per_guardian_video_kbps

        # Total bandwidth (each guardian sends and receives from all others)
        # Simplified model: MCU mixes, so each guardian sends once, receives mixed stream
        total_bandwidth_kbps = num_guardians * per_guardian_total_kbps

        # Recommendations
        recommendations = []

        if total_bandwidth_kbps > 50_000:  # >50 Mbps
            recommendations.append("High bandwidth usage. Consider disabling video for some participants.")

        if video_codec and video_codec.name == "H.264":
            recommendations.append("Recommendation: Switch to VP8 to save ~200 kbps per guardian (royalty-free).")

        if audio_codec.name == "G.711":
            recommendations.append("Recommendation: Switch to Opus to save ~32 kbps per guardian.")

        return {
            "num_guardians": num_guardians,
            "audio_codec": audio_codec.name,
            "video_codec": video_codec.name if video_codec else "None",
            "per_guardian_bandwidth_kbps": per_guardian_total_kbps,
            "total_bandwidth_kbps": total_bandwidth_kbps,
            "total_bandwidth_mbps": round(total_bandwidth_kbps / 1000, 2),
            "recommendations": recommendations
        }


# ============================================================================
# Usage Example
# ============================================================================

def example_usage():
    """
    Example demonstrating codec selection and bandwidth analysis.
    """
    print("Intelligent Codec Selection for Guardian Council")
    print("=" * 60)

    selector = CodecSelector()

    # Example 1: Select audio codec for WebRTC endpoint
    print("\n[Example 1] Audio codec for WebRTC (browser-based guardian)")
    audio_codec = selector.select_audio_codec(
        available_bandwidth_bps=2_000_000,  # 2 Mbps
        endpoint_capabilities=["Opus", "G.711"],
        prefer_open_source=True,
        require_browser_support=True
    )
    print(f"Selected: {audio_codec.name}")
    print(f"  Bandwidth: {audio_codec.bandwidth_kbps} kbps")
    print(f"  Quality: {audio_codec.quality_score}/10")
    print(f"  Category: {audio_codec.category.value}")
    print(f"  Efficiency: {audio_codec.efficiency_score():.2f} (quality/kbps)")

    # Example 2: Select video codec (prefer VP8 over H.264)
    print("\n[Example 2] Video codec (prefer open source)")
    video_codec = selector.select_video_codec(
        available_bandwidth_bps=5_000_000,  # 5 Mbps
        endpoint_capabilities=["VP8", "H.264"],
        prefer_open_source=True,
        hardware_accel_available=True
    )
    print(f"Selected: {video_codec.name}")
    print(f"  Bandwidth: {video_codec.bandwidth_kbps} kbps (~{video_codec.bandwidth_kbps/1000:.1f} Mbps)")
    print(f"  Quality: {video_codec.quality_score}/10")
    print(f"  Category: {video_codec.category.value}")
    print(f"  Hardware Accel: {video_codec.hardware_accel}")

    # Example 3: Bandwidth analysis for 12-guardian meeting
    print("\n[Example 3] Bandwidth analysis for 12-guardian meeting")
    analyzer = BandwidthAnalyzer()
    analysis = analyzer.analyze_guardian_bandwidth(
        num_guardians=12,
        video_enabled=True
    )
    print(f"Guardians: {analysis['num_guardians']}")
    print(f"Audio Codec: {analysis['audio_codec']}")
    print(f"Video Codec: {analysis['video_codec']}")
    print(f"Per-Guardian: {analysis['per_guardian_bandwidth_kbps']} kbps")
    print(f"Total Bandwidth: {analysis['total_bandwidth_mbps']} Mbps")
    print("\nRecommendations:")
    for rec in analysis['recommendations']:
        print(f"  - {rec}")

    # Example 4: Negotiate common codec across heterogeneous endpoints
    print("\n[Example 4] Negotiate common codec for mixed endpoints")
    participants = [
        {"id": "guardian-1", "type": "H.323", "capabilities": ["G.711", "G.729"]},
        {"id": "guardian-2", "type": "SIP", "capabilities": ["G.711", "Opus"]},
        {"id": "guardian-3", "type": "WebRTC", "capabilities": ["Opus", "G.711"]},
    ]
    common_codec = selector.negotiate_common_codec(participants, CodecType.AUDIO)
    if common_codec:
        print(f"Common Codec: {common_codec.name}")
        print(f"  All {len(participants)} participants support this codec")
    else:
        print("No common codec found!")


if __name__ == "__main__":
    example_usage()
