# H.323 Codec Selection Guide for Guardian Council

**Document Version**: 1.0
**Last Updated**: 2025-11-11
**Author**: InfraFabric Project

---

## Overview

This document provides comprehensive guidance on codec selection for the H.323 Guardian Council system. It covers audio and video codecs, their tradeoffs, and recommendations for different scenarios.

**Key Decision Factors**:
1. **Bandwidth Availability**: Available network capacity
2. **Quality Requirements**: Audio/video fidelity needs
3. **Endpoint Compatibility**: H.323, SIP, WebRTC, NDI support
4. **Licensing**: Open-source vs. proprietary codecs
5. **Hardware Support**: Acceleration availability

---

## Audio Codecs

### Codec Comparison Table

| Codec | Bandwidth | Quality | Latency | License | Browser Support | Hardware Accel | CPU Cost |
|-------|-----------|---------|---------|---------|----------------|----------------|----------|
| **Opus** | 6-510 kbps (adaptive) | ★★★★★ (9.5/10) | 5ms | Open (BSD) | ✅ Yes | ❌ No | Medium (15%) |
| **G.711** | 64 kbps | ★★★★☆ (8.0/10) | 2ms | Open | ✅ Yes | ✅ Yes | Low (5%) |
| **G.729** | 8 kbps | ★★★☆☆ (7.0/10) | 15ms | Proprietary | ❌ No | ✅ Yes | High (25%) |
| **AMR** | 4.75-12.2 kbps | ★★★☆☆ (6.5/10) | 20ms | Proprietary | ❌ No | ❌ No | High (30%) |

**Quality Scale**: 1-10, based on PESQ (Perceptual Evaluation of Speech Quality) scores

---

### Opus (Recommended for Most Use Cases)

**Strengths**:
- ✅ **Adaptive bitrate**: Automatically adjusts 6-510 kbps based on network
- ✅ **Best quality-per-bit**: Superior audio quality at low bitrates
- ✅ **Low latency**: 5ms encoding latency
- ✅ **Open source**: Royalty-free (BSD license)
- ✅ **WebRTC native**: Fully supported in all modern browsers
- ✅ **Wide frequency range**: 8 kHz - 48 kHz (full bandwidth)

**Weaknesses**:
- ❌ **No hardware acceleration**: Software-only encoding/decoding
- ❌ **Limited H.323 support**: Not natively supported by legacy H.323 terminals

**Use Cases**:
- ✅ **Browser-based guardians** (WebRTC)
- ✅ **Bandwidth-constrained networks** (adaptive bitrate)
- ✅ **High-quality audio requirements** (music, multilingual)
- ✅ **Modern SIP endpoints**

**Bandwidth Calculation** (Opus @ 32 kbps typical):
```
Per-guardian: 32 kbps
8 guardians: 256 kbps (0.256 Mbps)
12 guardians: 384 kbps (0.384 Mbps)
```

**Configuration** (`src/communication/codec_selector.py`):
```python
audio_codec = "Opus"
bitrate_kbps = 32  # Can range 6-510 kbps
```

---

### G.711 (Universal Compatibility)

**Strengths**:
- ✅ **Universal support**: Supported by all H.323, SIP, and VoIP devices
- ✅ **Ultra-low latency**: 2ms encoding latency
- ✅ **Hardware acceleration**: DSP support on most platforms
- ✅ **No licensing fees**: Public domain
- ✅ **Simple implementation**: No complex encoding

**Weaknesses**:
- ❌ **High bandwidth**: 64 kbps fixed (8x more than G.729)
- ❌ **No compression**: Uncompressed PCM audio
- ❌ **Limited scalability**: Bandwidth increases linearly with participants

**Use Cases**:
- ✅ **Legacy H.323 terminals** (Polycom, Cisco)
- ✅ **Low-latency requirements** (<5ms total latency)
- ✅ **High-bandwidth networks** (LAN, fiber)
- ✅ **Fallback codec** (when negotiation fails)

**Bandwidth Calculation** (G.711 @ 64 kbps):
```
Per-guardian: 64 kbps
8 guardians: 512 kbps (0.512 Mbps)
12 guardians: 768 kbps (0.768 Mbps)
```

**Configuration**:
```python
audio_codec = "G.711"  # PCMU (μ-law) or PCMA (A-law)
```

---

### G.729 (Bandwidth-Constrained)

**Strengths**:
- ✅ **Very low bandwidth**: 8 kbps (8x less than G.711)
- ✅ **Hardware acceleration**: DSP support available
- ✅ **Wide deployment**: Common in telecom/VoIP

**Weaknesses**:
- ❌ **Licensing required**: Patented (expired 2017, but legacy concerns)
- ❌ **Lower quality**: PESQ 7.0/10 (vs. 8.0/10 for G.711)
- ❌ **No browser support**: Not available in WebRTC
- ❌ **Higher latency**: 15ms encoding latency
- ❌ **High CPU cost**: 25% CPU per stream (software encoding)

**Use Cases**:
- ✅ **Satellite/cellular links** (bandwidth-limited)
- ✅ **Large-scale conferences** (>25 participants)
- ✅ **Legacy telecom integration** (PSTN gateways)

**Bandwidth Calculation** (G.729 @ 8 kbps):
```
Per-guardian: 8 kbps
8 guardians: 64 kbps (0.064 Mbps)
12 guardians: 96 kbps (0.096 Mbps)
```

**Note**: G.729 patents expired in 2017, but check local regulations.

---

## Video Codecs

### Codec Comparison Table

| Codec | Bandwidth (720p) | Quality | Latency | License | Browser Support | Hardware Accel | CPU Cost |
|-------|------------------|---------|---------|---------|----------------|----------------|----------|
| **VP8** | 1 Mbps | ★★★★☆ (8.5/10) | 30ms | Open (BSD) | ✅ Yes | ✅ Yes (modern) | Medium (40%) |
| **VP9** | 700 kbps | ★★★★★ (9.0/10) | 50ms | Open (BSD) | ✅ Yes | ⚠️ Limited | High (60%) |
| **H.264** | 1.2 Mbps | ★★★★★ (9.0/10) | 40ms | Proprietary | ✅ Yes | ✅ Yes (widespread) | Low (35%) |
| **H.263** | 500 kbps | ★★☆☆☆ (6.0/10) | 30ms | Proprietary | ❌ No | ❌ No | Low (20%) |

**Quality Scale**: 1-10, based on PSNR (Peak Signal-to-Noise Ratio) at 720p

---

### VP8 (Recommended for Guardian Council)

**Strengths**:
- ✅ **Royalty-free**: Open-source (BSD license)
- ✅ **WebRTC native**: Default codec for browsers
- ✅ **Good quality**: PSNR 8.5/10 at 1 Mbps
- ✅ **Hardware acceleration**: Intel Quick Sync, AMD VCE support
- ✅ **Wide compatibility**: Supported by Jitsi, Kurento MCUs

**Weaknesses**:
- ❌ **Higher bandwidth than VP9**: ~40% more than VP9
- ❌ **Less efficient than H.264**: Slightly larger files
- ❌ **Limited H.323 support**: Not standard H.323 codec

**Use Cases**:
- ✅ **Browser-based guardians** (Chrome, Firefox, Edge)
- ✅ **Open-source preference** (avoid licensing fees)
- ✅ **Modern endpoints** (post-2015)
- ✅ **Balanced quality/bandwidth**

**Bandwidth Calculation** (VP8 @ 1 Mbps for 720p):
```
Per-guardian (720p): 1 Mbps
8 guardians: 8 Mbps
12 guardians: 12 Mbps

# With audio (Opus @ 32 kbps):
Per-guardian total: 1.032 Mbps
12 guardians total: 12.384 Mbps
```

**Configuration**:
```python
video_codec = "VP8"
bitrate_kbps = 1000  # 1 Mbps for 720p
resolution = "1280x720"
framerate = 30
```

---

### H.264 (Best Quality, Hardware Support)

**Strengths**:
- ✅ **Excellent quality**: PSNR 9.0/10
- ✅ **Widespread hardware acceleration**: All modern GPUs/SoCs
- ✅ **Efficient encoding**: Better compression than VP8
- ✅ **Universal support**: H.323, SIP, WebRTC, NDI
- ✅ **Low CPU cost**: ~35% with hardware encoding

**Weaknesses**:
- ❌ **Licensing fees**: MPEG-LA patent pool (free for end users, fees for distributors)
- ❌ **Proprietary**: Not open-source

**Use Cases**:
- ✅ **Hardware-accelerated endpoints** (dedicated H.323 terminals)
- ✅ **Highest quality requirements** (board presentations)
- ✅ **Heterogeneous environments** (mixed H.323/SIP/WebRTC)
- ✅ **NDI integration** (NewTek NDI uses H.264)

**Bandwidth Calculation** (H.264 @ 1.2 Mbps for 720p):
```
Per-guardian (720p): 1.2 Mbps
8 guardians: 9.6 Mbps
12 guardians: 14.4 Mbps
```

**Configuration**:
```python
video_codec = "H.264"
profile = "baseline"  # or "main", "high"
bitrate_kbps = 1200
resolution = "1280x720"
framerate = 30
```

---

### VP9 (Most Efficient, Future-Proof)

**Strengths**:
- ✅ **Best compression**: 30-50% better than VP8/H.264
- ✅ **Royalty-free**: Open-source (BSD license)
- ✅ **Excellent quality**: PSNR 9.0/10
- ✅ **WebRTC support**: Supported in Chrome, Firefox

**Weaknesses**:
- ❌ **Limited hardware support**: Only newest GPUs (2018+)
- ❌ **High CPU cost**: 60% CPU per stream (software encoding)
- ❌ **Higher latency**: 50ms encoding latency
- ❌ **Poor H.323 support**: Not standard H.323 codec

**Use Cases**:
- ✅ **Bandwidth-constrained networks** (satellite, cellular)
- ✅ **Future-proof deployments** (long-term)
- ✅ **Hardware acceleration available** (Intel Gen 11+, AMD RX 6000+)

**Bandwidth Calculation** (VP9 @ 700 kbps for 720p):
```
Per-guardian (720p): 700 kbps
8 guardians: 5.6 Mbps
12 guardians: 8.4 Mbps
```

---

## Codec Selection Decision Tree

```
┌─────────────────────────────────────────────────┐
│      Guardian Council Codec Selection          │
└─────────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Audio or Video?        │
        └─────────────────────────┘
         │                       │
    [Audio]                  [Video]
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ Bandwidth?       │    │ Bandwidth?       │
├──────────────────┤    ├──────────────────┤
│ >1 Mbps: Opus    │    │ >5 Mbps: VP8     │
│ <1 Mbps: G.729   │    │ <5 Mbps: VP9     │
│ LAN: G.711       │    │ LAN: H.264       │
└──────────────────┘    └──────────────────┘
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ Endpoints?       │    │ Endpoints?       │
├──────────────────┤    ├──────────────────┤
│ Browser: Opus    │    │ Browser: VP8     │
│ H.323: G.711     │    │ H.323: H.264     │
│ SIP: Opus/G.711  │    │ SIP: VP8/H.264   │
└──────────────────┘    └──────────────────┘
```

---

## Recommended Configurations

### Configuration 1: Browser-Based Guardians (Recommended)

**Scenario**: All guardians using WebRTC browsers (Chrome, Firefox, Edge)

**Codec Selection**:
- Audio: **Opus @ 32 kbps**
- Video: **VP8 @ 1 Mbps (720p)**

**Bandwidth per Guardian**: 1.032 Mbps
**Total (12 guardians)**: 12.384 Mbps

**Advantages**:
- ✅ Royalty-free (no licensing)
- ✅ Native browser support
- ✅ Excellent quality
- ✅ Adaptive bitrate (Opus)

---

### Configuration 2: Mixed H.323/SIP/WebRTC (Universal)

**Scenario**: Legacy H.323 terminals + SIP phones + browsers

**Codec Selection**:
- Audio: **G.711 @ 64 kbps** (universal compatibility)
- Video: **H.264 @ 1.2 Mbps (720p)** (universal support)

**Bandwidth per Guardian**: 1.264 Mbps
**Total (12 guardians)**: 15.168 Mbps

**Advantages**:
- ✅ Works with all endpoints
- ✅ Hardware acceleration
- ✅ Excellent quality
- ✅ Low latency

**Disadvantages**:
- ❌ Higher bandwidth
- ❌ H.264 licensing (free for end-users)

---

### Configuration 3: Bandwidth-Constrained (Satellite/Cellular)

**Scenario**: Limited bandwidth (< 5 Mbps total)

**Codec Selection**:
- Audio: **G.729 @ 8 kbps** (or Opus @ 16 kbps)
- Video: **VP9 @ 500 kbps (480p)** (or disable video)

**Bandwidth per Guardian**: 0.508 Mbps
**Total (12 guardians)**: 6.096 Mbps

**Advantages**:
- ✅ Minimal bandwidth usage
- ✅ Supports large-scale meetings

**Disadvantages**:
- ❌ Lower video quality (480p)
- ❌ High CPU cost (VP9)
- ❌ G.729 licensing

---

### Configuration 4: Audio-Only (Minimum Bandwidth)

**Scenario**: Voice-only deliberations, no video

**Codec Selection**:
- Audio: **Opus @ 32 kbps** (or G.729 @ 8 kbps)
- Video: **None**

**Bandwidth per Guardian**: 0.032 Mbps (Opus) or 0.008 Mbps (G.729)
**Total (12 guardians)**: 0.384 Mbps (Opus) or 0.096 Mbps (G.729)

**Advantages**:
- ✅ Extremely low bandwidth
- ✅ Supports 50+ concurrent guardians

---

## Transcoding Considerations

### When Transcoding is Required

Transcoding is needed when endpoints use **incompatible codecs**. The SIP-H.323 gateway handles transcoding automatically.

**Common Transcoding Scenarios**:
| Source Codec | Target Codec | Transcoding Latency | CPU Cost | Quality Loss |
|--------------|--------------|---------------------|----------|--------------|
| G.711 | G.729 | 15ms | 30% | Moderate (8.0 → 7.0) |
| G.729 | G.711 | 15ms | 25% | Minimal |
| Opus | G.711 | 20ms | 40% | Moderate |
| VP8 | H.264 | 50ms | 70% | Minimal |

**Transcoding Performance** (`src/communication/h323_sip_gateway.py`):
- **Max Concurrent Transcoding**: 5 streams
- **CPU Usage**: ~40% per stream
- **Latency Addition**: 15-50ms
- **Quality Impact**: 0.5-1.0 points (on 10-point scale)

**Recommendation**: **Avoid transcoding** whenever possible by standardizing on a common codec (Opus + VP8 for WebRTC, G.711 + H.264 for H.323).

---

## Quality vs. Bandwidth Tradeoffs

### Audio Codecs (Quality per kbps)

```
Efficiency = Quality Score / Bandwidth (kbps)

Opus:     9.5 / 32  = 0.297  ⭐ Best
G.711:    8.0 / 64  = 0.125
G.729:    7.0 / 8   = 0.875  ⭐ Best for low bandwidth
AMR:      6.5 / 12  = 0.542
```

**Recommendation**: Use **Opus** for best quality-per-bit. Use **G.729** only for extreme bandwidth constraints.

---

### Video Codecs (Quality per Mbps at 720p)

```
Efficiency = Quality Score / Bandwidth (Mbps)

VP9:      9.0 / 0.7  = 12.86  ⭐ Best
VP8:      8.5 / 1.0  = 8.50
H.264:    9.0 / 1.2  = 7.50
H.263:    6.0 / 0.5  = 12.00  (but poor quality)
```

**Recommendation**: Use **VP9** if hardware acceleration available and CPU permits. Otherwise use **VP8** for balance.

---

## Hardware Acceleration

### GPUs with VP8/VP9 Support

| GPU Series | VP8 Encode/Decode | VP9 Encode/Decode | H.264 Encode/Decode |
|------------|-------------------|-------------------|---------------------|
| Intel Quick Sync (Gen 7+) | ✅ / ✅ | ❌ / ✅ | ✅ / ✅ |
| Intel Quick Sync (Gen 11+) | ✅ / ✅ | ✅ / ✅ | ✅ / ✅ |
| AMD VCE/VCN (Polaris+) | ✅ / ✅ | ❌ / ✅ | ✅ / ✅ |
| AMD VCN (RDNA 2+) | ✅ / ✅ | ✅ / ✅ | ✅ / ✅ |
| NVIDIA NVENC (Pascal+) | ❌ / ✅ | ❌ / ✅ | ✅ / ✅ |

**Recommendation**: If hardware acceleration is available, use **VP8** or **H.264** for lowest CPU usage.

---

## Licensing Summary

| Codec | License Type | Cost | Notes |
|-------|--------------|------|-------|
| **Opus** | Open (BSD) | Free | Royalty-free |
| **VP8** | Open (BSD) | Free | Google patent grant |
| **VP9** | Open (BSD) | Free | Google patent grant |
| **G.711** | Public Domain | Free | No patents |
| **G.729** | Proprietary | Free* | Patents expired 2017 (check local laws) |
| **H.264** | Proprietary (MPEG-LA) | Free** | Free for end-users, fees for distributors |
| **AMR** | Proprietary | Paid | VoiceAge license required |

\* G.729 patents expired, but some countries may have extended protections
\** H.264 free for "free internet broadcast" per MPEG-LA terms

**Recommendation for InfraFabric**: Use **open-source codecs** (Opus, VP8, VP9) to avoid any licensing complexity.

---

## Monitoring Codec Performance

### Prometheus Metrics

Monitor codec performance using Prometheus metrics:

```promql
# Audio codec distribution
h323_audio_codec_usage{codec="Opus"} 8
h323_audio_codec_usage{codec="G.711"} 4

# Video codec distribution
h323_video_codec_usage{codec="VP8"} 10
h323_video_codec_usage{codec="H.264"} 2

# Transcoding CPU usage
h323_transcoding_cpu_percent 35.2

# Codec quality (MOS score)
h323_audio_quality_mos{codec="Opus"} 4.5
h323_audio_quality_mos{codec="G.711"} 4.2
```

### Grafana Dashboard

Create Grafana dashboard to visualize:
1. **Codec Distribution Pie Chart**: Which codecs are in use
2. **Quality Metrics**: PESQ/MOS scores over time
3. **Transcoding Load**: CPU usage for transcoding
4. **Bandwidth Usage**: Per-codec bandwidth consumption

---

## Best Practices

### ✅ DO:
- ✅ Prefer **open-source codecs** (Opus, VP8) for licensing simplicity
- ✅ Use **hardware acceleration** when available
- ✅ **Standardize** on a single audio + video codec pair
- ✅ **Test bandwidth** before large meetings
- ✅ **Monitor quality** via PESQ/MOS metrics
- ✅ **Document** codec choices in deployment runbook

### ❌ DON'T:
- ❌ Use **proprietary codecs** without verifying licenses
- ❌ **Force transcoding** unnecessarily (adds latency)
- ❌ **Over-provision bandwidth** (use adaptive bitrate)
- ❌ **Ignore CPU usage** (transcoding is expensive)
- ❌ **Mix incompatible codecs** without gateway

---

## References

1. **Opus**: https://opus-codec.org/
2. **VP8/VP9**: https://www.webmproject.org/
3. **H.264**: https://www.itu.int/rec/T-REC-H.264
4. **G.711**: https://www.itu.int/rec/T-REC-G.711
5. **G.729**: https://www.itu.int/rec/T-REC-G.729
6. **WebRTC Codec Requirements**: https://datatracker.ietf.org/doc/html/rfc7874
7. **Opus Codec Comparison**: https://opus-codec.org/comparison/

---

**Document Owner**: InfraFabric Operations Team
**Review Cycle**: Quarterly (or when new codecs emerge)
**Next Review**: 2025-Q2

---

**END OF DOCUMENT**
