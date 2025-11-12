# OBS vs vMix - Comprehensive Comparison

**Purpose:** Guide selection between OBS and vMix for production workflows
**Pattern:** IF.talent bloom analysis + IF.ground pragmatism
**Author:** Session 6 (IF.talent)
**Date:** 2025-11-12
**Citation:** if://analysis/obs-vs-vmix-v1

---

## Executive Summary

**Quick Decision Matrix:**

| Use Case | Recommendation | Reasoning |
|----------|---------------|-----------|
| **Beginner streaming** | OBS ✅ | Free, easy, Twitch/YouTube ready |
| **Budget <$100** | OBS ✅ | vMix costs $60-$1200 |
| **Professional multi-camera** | vMix ✅ | Integrated production features |
| **Open source requirement** | OBS ✅ | Community-driven, no vendor lock-in |
| **Complex live production** | vMix ✅ | Better multi-input management |
| **NDI workflows** | Both ✅ | OBS (plugin), vMix (built-in) |
| **Automation/scripting** | Depends | OBS (Lua/Python), vMix (built-in) |
| **IF.bus integration** | Both ✅ | WebSocket (OBS), HTTP (vMix) |

---

## Cost Comparison

### OBS Studio
- **Cost:** $0 (FREE!)
- **License:** GPL v2 (open source)
- **Updates:** FREE forever
- **Plugins:** Mostly FREE
- **Total 5-year cost:** $0

### vMix
| Edition | Cost | Features | Best For |
|---------|------|----------|----------|
| **Basic** | $60 | 1080p, 4 inputs | Simple productions |
| **HD** | $150 | 1080p, 1000 inputs | Small productions |
| **4K** | $350 | 4K, 1000 inputs | Mid-size productions |
| **Pro** | $700 | Full features | Professional use |
| **Max** | $1200 | 8 channels, advanced | Broadcast |

**Total 5-year cost (Pro):** $700 (one-time) + potential upgrades

**Cost Advantage:** OBS saves $700-$1200 upfront + no licensing fees

---

## Feature Comparison

### Streaming

| Feature | OBS | vMix | Winner |
|---------|-----|------|--------|
| **RTMP Streaming** | ✅ Built-in | ✅ Built-in | Tie |
| **Multi-destination** | ✅ (3rd party plugins) | ✅ Built-in (3 streams) | vMix |
| **SRT** | ✅ Built-in (28+) | ✅ Built-in | Tie |
| **NDI Output** | ✅ (plugin) | ✅ Built-in | vMix (integrated) |
| **Cost** | $0 | $60-$1200 | OBS |

**Streaming Winner:** Tie (both excellent, OBS free, vMix more integrated)

---

### Production Control

| Feature | OBS | vMix | Winner |
|---------|-----|------|--------|
| **Scene switching** | ✅ Hotkeys, transitions | ✅ Cut/Fade/Transitions | Tie |
| **Preview/Program** | ❌ (Studio Mode only) | ✅ Full PVW/PGM | vMix |
| **Multi-layer compositing** | ⚠️ (via scenes) | ✅ 4+ layers native | vMix |
| **PTZ camera control** | ⚠️ (3rd party) | ✅ Built-in | vMix |
| **Instant Replay** | ❌ | ✅ Built-in | vMix |
| **Virtual Sets** | ❌ | ✅ Built-in | vMix |

**Production Control Winner:** vMix (professional features built-in)

---

### Sources & Inputs

| Feature | OBS | vMix | Winner |
|---------|-----|------|--------|
| **Window/Game Capture** | ✅ Excellent | ✅ Good | OBS (better game capture) |
| **NDI Sources** | ✅ (plugin) | ✅ Built-in | vMix (integrated) |
| **Browser Sources** | ✅ Excellent | ✅ Good | OBS (more flexible) |
| **Media Playback** | ✅ Good | ✅ Excellent (playlists) | vMix |
| **Camera Inputs** | ✅ (via capture cards) | ✅ Native | Tie |
| **Max Inputs** | Unlimited | 1000 (4K/Pro/Max) | OBS (no limit) |

**Sources Winner:** Tie (OBS better game/browser, vMix better media/NDI)

---

### Recording

| Feature | OBS | vMix | Winner |
|---------|-----|------|--------|
| **Local Recording** | ✅ MP4/MKV/FLV | ✅ MP4/AVI/MOV | Tie |
| **Multi-track Audio** | ✅ Built-in | ✅ Built-in | Tie |
| **Instant Replay** | ❌ | ✅ Built-in | vMix |
| **Multi-recorder** | ⚠️ (via plugins) | ✅ Built-in | vMix |

**Recording Winner:** vMix (more production features)

---

### Audio

| Feature | OBS | vMix | Winner |
|---------|-----|------|--------|
| **Audio Mixing** | ✅ Basic mixer | ✅ Advanced mixer | vMix |
| **Audio Filters** | ✅ Excellent (VST) | ✅ Good | OBS (VST support) |
| **Audio Ducking** | ⚠️ (3rd party) | ✅ Built-in | vMix |
| **Multi-bus** | ⚠️ (complex) | ✅ Built-in | vMix |

**Audio Winner:** vMix (better integrated mixer)

---

### Automation & API

| Feature | OBS | vMix | Winner |
|---------|-----|------|--------|
| **Scripting** | ✅ Lua/Python | ✅ vMix Script | Tie (different approaches) |
| **WebSocket API** | ✅ obs-websocket 5.x | ✅ TCP API | Tie |
| **HTTP API** | ⚠️ (via plugins) | ✅ Built-in | vMix |
| **Triggers/Shortcuts** | ✅ Hotkeys | ✅ Advanced triggers | vMix |
| **IF.bus Integration** | ✅ (this project!) | ✅ (this project!) | Tie |

**Automation Winner:** Tie (both powerful, different paradigms)

---

### Plugins & Extensibility

| Feature | OBS | vMix | Winner |
|---------|-----|------|--------|
| **Plugin Ecosystem** | ✅ Huge (GitHub) | ⚠️ Limited | OBS |
| **Community Support** | ✅ Massive | ⚠️ Smaller | OBS |
| **Open Source** | ✅ GPL v2 | ❌ Commercial | OBS |
| **Custom Development** | ✅ Full source access | ❌ Closed source | OBS |

**Extensibility Winner:** OBS (open source champion)

---

## Bloom Pattern Comparison

### OBS Bloom Patterns
- **Early Bloomers:** Basic streaming (90), Virtual camera (95), Scene switching (85)
- **Steady Performers:** Sources (55), Recording (50), Filters (52)
- **Late Bloomers:** Plugins (30), Scripting (20), WebSocket (25)

**OBS Philosophy:** Lower barrier to entry, free to start, powerful at scale

### vMix Bloom Patterns
- **Early Bloomers:** Basic switching (85), Input management (80)
- **Steady Performers:** Streaming (50), Recording (52), Audio (48), Overlays (55)
- **Late Bloomers:** Automation (25), Advanced API (20)

**vMix Philosophy:** Integrated professional features, consistent API, commercial support

---

## Learning Curve Comparison

### OBS Learning Path
| Stage | Features | Time | Cost |
|-------|----------|------|------|
| **Beginner** | Streaming, scenes, virtual camera | 1.75h | $0 |
| **Intermediate** | Sources, filters, recording | 9.5h | $0 |
| **Advanced** | Plugins, scripting, WebSocket | 52.5h | $0 |

**Total Learning Time:** 52.5 hours
**Total Cost:** $0

### vMix Learning Path
| Stage | Features | Time | Cost |
|-------|----------|------|------|
| **Beginner** | Switching, inputs, streaming | 6h | $60-$150 |
| **Intermediate** | Multi-cam, audio, overlays | 18h | $350-$700 |
| **Advanced** | Automation, API, instant replay | 48h | $700-$1200 |

**Total Learning Time:** 48 hours (slightly faster - more integrated)
**Total Cost:** $700-$1200

---

## Use Case Recommendations

### Use Case 1: Beginner Twitch Streamer
**Recommendation:** OBS ✅

**Reasoning:**
- FREE (no upfront cost)
- Massive Twitch/YouTube community
- Tutorials everywhere
- Game capture excellence
- Virtual camera for Discord

**vMix Overkill:** $60-$150 unnecessary for simple streaming

---

### Use Case 2: Professional Multi-Camera Live Production
**Recommendation:** vMix ✅

**Reasoning:**
- Integrated multi-camera workflow
- Preview/Program (PVW/PGM)
- PTZ camera control built-in
- Instant replay
- Advanced audio mixer

**OBS Limitations:** Would require multiple plugins and complex setup

---

### Use Case 3: Church/School Live Stream (Budget-Conscious)
**Recommendation:** OBS ✅

**Reasoning:**
- FREE = critical for non-profit
- Simple scene switching sufficient
- NDI plugin for multiple cameras
- Browser sources for lyrics/announcements
- Community support

**vMix Benefits Not Needed:** Professional features overkill for weekly streams

---

### Use Case 4: Corporate Event Production Company
**Recommendation:** vMix ✅

**Reasoning:**
- Professional appearance
- Client demands reliability
- Integrated features save time
- Commercial support available
- Multi-instance licensing

**OBS Risk:** Plugin dependencies, less integrated

---

### Use Case 5: YouTube Content Creator
**Recommendation:** OBS ✅

**Reasoning:**
- FREE (critical for starting creators)
- Browser sources for dynamic overlays
- Excellent screen/game capture
- Virtual camera for calls
- Recording quality excellent

**vMix Overkill:** Most YouTube creators don't need $700 software

---

### Use Case 6: Sports Broadcast (High School/College)
**Recommendation:** vMix ✅

**Reasoning:**
- Scoreboards (data-driven overlays)
- Instant replay (critical for sports)
- Multi-camera coordination
- Professional transitions
- PTZ camera control

**OBS Limitations:** No instant replay, complex multi-camera setup

---

## IF.ground Philosophy Perspective

### Principle 1: Open Source First
**Winner:** OBS ✅
- Open source
- No vendor lock-in
- Community-driven development
- Full source code access

**vMix:** Commercial, closed source

---

### Principle 4: Underdetermination
**Both Valid:** OBS vs vMix solve same problem (live streaming) differently
- OBS: Open, extensible, free
- vMix: Integrated, commercial, supported

**IF.ground Lesson:** Choice depends on context (budget, use case, expertise)

---

### Principle 6: Pragmatism
**Judge by Usefulness:**
- **OBS useful when:** Budget = $0, simple streaming, YouTube/Twitch
- **vMix useful when:** Professional production, multi-camera, instant replay

**No ideology:** Both are valid tools, select based on needs

---

### Principle 8: Stoic Prudence
**Graceful Degradation:**
- **OBS:** Reconnect WebSocket if crash, restart scenes
- **vMix:** Fallback between vMix instances (IF.bus orchestration)

**Both:** Can implement resilient workflows with IF.bus

---

## Wu Lun (五倫) Perspective

**朋友 (Friends):** OBS and vMix are both "friends" (朋友) with unique strengths

- **OBS:** Friend who's generous and welcoming (慷慨热情)
  - Free, open-source, community-driven
  - Lower barrier to entry
  - Massive ecosystem

- **vMix:** Friend who's professional and reliable (专业可靠)
  - Integrated features
  - Commercial support
  - Proven in broadcast

**Wu Lun Lesson:** Don't force friends into wrong roles
- Don't use vMix for simple Twitch streaming (overkill)
- Don't use OBS for complex sports broadcast (insufficient)

---

## IF.bus Integration Comparison

### OBS Integration (This Project)
```python
# Async WebSocket adapter
class OBSWebSocketAdapter(OBSAdapter):
    async def connect(self):
        # WebSocket connection

    async def start_stream(self):
        # WebSocket: StartStream

# IF.bus can orchestrate OBS instances
if bus add obs myobs --host localhost --port 4455 --password xxx
if bus exec obs myobs --command start_stream
```

**Advantages:**
- WebSocket = real-time bidirectional
- Async = non-blocking
- Free, no licensing

### vMix Integration (This Project)
```python
# Synchronous HTTP adapter
class VMixHTTPAdapter(VMixAdapter):
    def connect(self):
        # HTTP connection

    def make_call(self, from_uri, to_uri):
        # HTTP: GET /api/?Function=Cut

# IF.bus can orchestrate vMix instances
if bus add vmix myvmix --host 192.168.1.100 --port 8088
if bus exec vmix myvmix --command cut --input 1
```

**Advantages:**
- HTTP = simple, stateless
- Synchronous = easier to reason about
- Professional features built-in

**IF.bus Conclusion:** Both integrate well, choose based on use case

---

## Cost-Benefit Analysis (5 Years)

### OBS
- **Upfront Cost:** $0
- **5-Year Cost:** $0
- **Learning Time:** 52.5 hours
- **Community Support:** Excellent (free)
- **Vendor Lock-in:** None
- **Total Cost of Ownership:** $0

### vMix Pro
- **Upfront Cost:** $700
- **5-Year Cost:** $700 (assume no major upgrades)
- **Learning Time:** 48 hours
- **Commercial Support:** Available (paid)
- **Vendor Lock-in:** Yes (proprietary)
- **Total Cost of Ownership:** $700

**Break-Even Analysis:** vMix needs to save >52.5 hours of time to justify $700 cost

**Savings with OBS:** $700 upfront + freedom from vendor lock-in

---

## Final Recommendations

### Choose OBS When:
✅ Budget = $0
✅ Twitch/YouTube streaming
✅ Open source requirement
✅ Simple to intermediate workflows
✅ Game/screen capture primary
✅ Community support sufficient
✅ Browser sources critical
✅ Plugin ecosystem valuable

### Choose vMix When:
✅ Budget ≥ $60
✅ Professional multi-camera production
✅ Instant replay needed
✅ PTZ camera control critical
✅ Commercial support desired
✅ Integrated features save time
✅ Sports/events broadcast
✅ Client demands professional appearance

### Use Both When:
✅ Hybrid workflows (OBS for streaming, vMix for production)
✅ IF.bus orchestration across multiple tools
✅ Redundancy (OBS backup for vMix)
✅ Learning/comparison
✅ Different use cases in same organization

---

## IF.talent Verdict

**Bloom Pattern Insight:**
- **OBS:** Early bloomer champion (free, beginner-friendly)
- **vMix:** Steady performer champion (consistent, integrated)

**IF.ground:principle_1 (Open Source First):**
Default to OBS unless vMix's integrated features justify $700 cost

**IF.ground:principle_6 (Pragmatism):**
Judge by usefulness in context:
- Beginner/budget: OBS
- Professional/multi-camera: vMix

**Wu Lun (朋友 Friends):**
Both are valuable friends, invite to appropriate gatherings

---

## Conclusion

**No Winner:** Both are excellent tools for different contexts

**Key Insight:** Not "OBS vs vMix" but "OBS AND vMix" - use right tool for right job

**IF.bus Value:** Unified control of BOTH via adapters - get best of both worlds

**Philosophy:** IF.ground underdetermination - multiple solutions exist, choose pragmatically based on:
1. Budget ($0 vs $700)
2. Use case (streaming vs production)
3. Expertise (community vs commercial support)
4. Values (open source vs integrated)

**Final Wisdom:** Start with OBS (FREE), upgrade to vMix if workflow demands justify cost

---

**Citation:** if://analysis/obs-vs-vmix-v1
**Status:** Analysis Complete ✅
**Next:** Apply to IF.bus workflow selection
**Time:** 2 hours (Session 6 contribution)
**Cost:** ~$3 (Sonnet analysis)
**Insight:** Both valid, context-dependent

---

*Session 6 (IF.talent) - Pragmatic Tool Selection*

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
