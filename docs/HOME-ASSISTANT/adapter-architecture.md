# Home Assistant Adapter Architecture

**Purpose:** Unified interface to Home Assistant instances (physical infrastructure control)
**Pattern:** Adapter + IF.talent Bloom Detection + Safety-Critical Physical Control
**Author:** Session 6 (IF.talent)
**Date:** 2025-11-12
**Citation:** if://design/integrations/home-assistant-adapter-v1

---

## Problem Statement

**Challenge:** Consistent control of Home Assistant physical infrastructure across different installations and domains

**Home Assistant as Physical Infrastructure Layer:**
- **Lights:** Z-Wave, Zigbee, WiFi bulbs
- **Cameras:** RTSP, ONVIF, USB cameras
- **Climate:** HVAC, thermostats
- **Locks:** Smart locks (security-critical!)
- **Sensors:** Motion, temperature, humidity
- **Automation:** Complex workflows

**Traditional Approach:**
```python
# Direct REST API calls - no abstraction
import requests

headers = {"Authorization": "Bearer TOKEN"}
requests.post("http://homeassistant.local:8123/api/services/light/turn_on",
             json={"entity_id": "light.living_room"},
             headers=headers)
```

**Problems:**
- No bloom pattern guidance
- No safety checks for critical infrastructure
- No IF.witness logging
- No polymorphism (can't swap HA for other platforms)

---

## Solution: Unified Adapter Pattern + Safety-Critical Controls

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│          IF.bus / vMix / OBS (Production Layer)          │
│  "Turn on studio lights when streaming starts"          │
└───────────────────────┬─────────────────────────────────┘
                        │
                        v
            ┌───────────────────────┐
            │ HomeAssistantAdapter  │
            │  (Abstract Base)      │
            │                       │
            │ + turn_on_light()     │
            │ + get_camera_snapshot()│
            │ + trigger_automation()│
            │ + is_safety_critical()│ ← Safety checks!
            │ + log_operation()     │ ← IF.witness required
            └───────────┬───────────┘
                        │
                        v
             ┌──────────────────┐
             │  HA REST Adapter │
             │                  │
             │ GET /api/states  │
             │ POST /api/services│
             └───────┬──────────┘
                     │
                     v
┌────────────────────────────────────────────────────────┐
│         Home Assistant (Physical Infrastructure)       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Lights  │  │  Cameras │  │  Locks   │           │
│  │ (Z-Wave) │  │  (RTSP)  │  │ (Zigbee) │           │
│  └──────────┘  └──────────┘  └──────────┘           │
└────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Domain-Based Architecture

**Home Assistant uses "domains":**
- `light.*` - Lights
- `camera.*` - Cameras
- `lock.*` - Locks
- `automation.*` - Automations
- `script.*` - Scripts

**Adapter provides domain-specific methods:**
```python
# Domain: light
ha.turn_on_light("light.living_room", brightness=255)

# Domain: camera
snapshot = ha.get_camera_snapshot("camera.studio_cam")

# Domain: automation
ha.trigger_automation("automation.studio_startup")
```

---

### 2. Safety-Critical Infrastructure

**CRITICAL:** Physical infrastructure control requires special handling

```python
def is_safety_critical(self, domain: HADomain) -> bool:
    """Check if domain controls safety-critical infrastructure"""
    capability = self.get_capability_profile(domain)
    return capability.physical_safety_critical

# Safety-critical domains:
- HADomain.LOCKS: True  # Security!
- HADomain.CLIMATE: True  # Physical comfort
- HADomain.AUTOMATIONS: True  # Can control anything
- HADomain.LIGHTS: False  # Not safety-critical
```

**IF.witness Integration (REQUIRED for safety-critical ops):**
All physical infrastructure operations MUST be logged with IF.witness for audit trails.

---

### 3. Bloom Pattern Detection

**Home Assistant Domain Bloom Patterns:**

| Domain | Bloom Pattern | Meaning | Best For |
|--------|---------------|---------|----------|
| **Lights** | Early Bloomer | Simple on/off, easy | Basic control |
| **Switches** | Early Bloomer | Simplest domain | Power control |
| **Sensors** | Early Bloomer | Read-only, simple | Monitoring |
| **Cameras** | Steady Performer | Reliable RTSP | Video feeds |
| **Media Players** | Steady Performer | Consistent API | Audio/video |
| **Climate** | Steady Performer | Reliable HVAC | Temperature |
| **Locks** | Steady Performer | Security-critical | Access control |
| **Automations** | Late Bloomer | Complex YAML | Workflows |
| **Scripts** | Late Bloomer | Reusable sequences | Custom actions |
| **Webhooks** | Late Bloomer | External integrations | IF.bus triggers |

---

## Integration with Production (vMix/OBS)

### Flow 1: Camera → Production
```
HA Camera (RTSP) → NDI Bridge → vMix/OBS Input → Live Production
```

```python
# Get camera stream from HA
camera_state = ha.get_state("camera.studio_cam")
rtsp_url = camera_state.attributes.get("entity_picture")

# Add to vMix/OBS via NDI bridge
vmix.add_input("NDI", rtsp_url, "Studio Camera")
obs.create_source("Scene 1", "Studio Camera", "obs_ndi_source")
```

### Flow 2: Production → Physical Response
```
vMix/OBS Streaming Start → IF.bus → HA Automation → "ON AIR" Light Red
```

```python
# When streaming starts, trigger HA automation
ha.trigger_automation("automation.on_air_lights")

# Or directly control lights
ha.turn_on_light("light.on_air_sign", color="red", brightness=255)
```

### Flow 3: Motion Detection → Scene Switch
```
HA Motion Sensor → IF.bus → vMix/OBS Scene Switch
```

```python
# HA automation triggers webhook
# IF.bus receives webhook, triggers production

# In HA automation:
- trigger: state
    entity_id: binary_sensor.studio_motion
    to: "on"
  action:
    service: rest_command.if_bus_scene_switch
```

---

## Use Case Examples

### Use Case 1: Studio Lighting Automation
```python
# Turn on studio lights when streaming starts
ha.activate_scene("scene.studio_production")  # Activates:
# - Key light (100%)
# - Fill light (60%)
# - Back light (80%)
# - ON AIR sign (red)

# Safety check
is_critical = ha.is_safety_critical(HADomain.LIGHTS)
print(f"Lights safety critical: {is_critical}")  # False
```

### Use Case 2: Camera Integration
```python
# Get camera snapshot for thumbnail
snapshot = ha.get_camera_snapshot("camera.studio_cam")

# Or stream via RTSP → NDI
camera = ha.get_state("camera.studio_cam")
rtsp_url = camera.attributes["entity_picture"]
# Bridge to vMix/OBS
```

### Use Case 3: Security Integration
```python
# Lock doors when production starts (SAFETY-CRITICAL!)
is_critical = ha.is_safety_critical(HADomain.LOCKS)
print(f"Locks safety critical: {is_critical}")  # True

# IF.witness MUST log this operation
ha.call_service("lock", "lock", target={"entity_id": "lock.studio_door"})
# Logged with timestamp, user, provenance
```

---

## Cost Advantage

**Home Assistant:**
- Software: $0 (FREE!)
- Installation: Raspberry Pi ($50-$150)
- Total: $50-$150

**Commercial Alternatives (Control4, Crestron):**
- Software: $2,000-$5,000
- Installation: $3,000-$10,000
- Total: $5,000-$15,000

**Savings: $4,850-$14,850**

**Open Source:** GPL, community-driven, no vendor lock-in

---

## IF.ground Philosophy Integration

### Principle 1: Open Source First
✅ Home Assistant is open-source champion
- Free software
- Community integrations
- No licensing fees

### Principle 8: Stoic Prudence (Physical Infrastructure)
✅ Safety-critical operations require special care
- IF.witness logging REQUIRED
- Safety checks before critical operations
- Graceful degradation (if HA unavailable, fail safe)

---

## Conclusion

**Home Assistant Adapter Pattern:**
1. **Domain-based architecture** (lights, cameras, locks, etc.)
2. **Safety-critical awareness** (locks, climate, automations)
3. **IF.witness integration** (REQUIRED for physical infrastructure)
4. **Bloom patterns** (early: lights/switches, late: automations)
5. **Production integration** (cameras → vMix/OBS, automations ← IF.bus)
6. **Cost advantage** ($5K-$15K savings vs commercial)

**Result:** Physical infrastructure joins InfraFabric as controllable layer

**Philosophy:** Stoic prudence - physical control requires reliability and logging

---

**Citation:** if://design/integrations/home-assistant-adapter-v1
**Status:** Complete ✅
**Time:** 3 hours
**Cost:** ~$5
**Savings:** $5K-$15K vs Control4/Crestron

---

*Session 6 (IF.talent) - Physical Infrastructure Control*

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
