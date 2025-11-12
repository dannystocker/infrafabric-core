# Capability Profile Examples

**Filler Task:** F6.13 (Session 6 - Talent)
**Created:** 2025-11-12
**Purpose:** Example capability profiles for all 7 InfraFabric sessions

---

## Overview

This directory contains **example capability profiles** for all 7 InfraFabric Phase 0 sessions. These profiles follow the **Capability Registry Schema** defined in [F6.12: CAPABILITY-REGISTRY-SCHEMA.md](../../CAPABILITY-REGISTRY-SCHEMA.md).

Each profile demonstrates:
- How to declare capabilities with skill levels
- Domain taxonomy in practice
- Bloom pattern classification
- Reputation score integration
- Cost and availability profiles

---

## Files

| File | Session | Primary Domains | Bloom Pattern |
|------|---------|----------------|---------------|
| `session-1-ndi.yaml` | Session 1 (NDI Witness Streaming) | video, crypto | Late Bloomer |
| `session-2-webrtc.yaml` | Session 2 (WebRTC Agent Mesh) | telephony, infra | Steady Performer |
| `session-3-h323.yaml` | Session 3 (H.323 Guardian Council) | telephony, video | Late Bloomer |
| `session-4-sip.yaml` | Session 4 (SIP Escalate Integration) | telephony, crypto | Steady Performer |
| `session-5-cli.yaml` | Session 5 (CLI Witness Optimize) | programming, crypto | Early Bloomer |
| `session-6-talent.yaml` | Session 6 (Talent Management) | talent, architecture, video | Steady Performer |
| `session-7-ifbus.yaml` | Session 7 (IF.bus) | infra, architecture | Late Bloomer |

---

## Usage

### 1. Registration with IF.governor

```bash
# Register a session's capabilities
$ if governor register docs/examples/capabilities/session-1-ndi.yaml

✅ Registered session-1-ndi (NDI Witness Streaming)
📊 14 capabilities across 4 domains
⭐ Reputation: Excellent (0.92)
🎯 Bloom: Late Bloomer (excels at complex tasks)
```

### 2. Query for Qualified Agents

```python
from infrafabric.governor import IFGovernor

# Find agents with NDI expertise
candidates = await governor.query_by_capability(
    domain='video',
    category='streaming',
    skill='ndi_protocol',
    min_level=SkillLevel.ADVANCED
)

# Results:
# - session-1-ndi: Expert (0.95 success rate, 120 hours experience)
```

### 3. Task Assignment

```python
# Define task requirements
task = TaskRequirements(
    task_id='P1.1.1',
    complexity=TaskComplexity.COMPLEX,
    required_capabilities=[
        Capability('video', 'streaming', 'ndi_protocol', SkillLevel.EXPERT, 1.0)
    ]
)

# Find best match using F6.3 assignment algorithm
candidates = await governor.find_qualified_swarms(task)

# Assign to top candidate
await coordinator.assign_task(task.task_id, candidates[0].swarm_id)
```

---

## Profile Structure

Each profile includes:

### 1. Metadata
- `swarm_id`: Unique identifier (e.g., "session-1-ndi")
- `display_name`: Human-readable name
- `description`: Brief description of expertise

### 2. Capabilities
```yaml
capabilities:
  video.streaming.ndi_protocol:
    level: expert              # novice | intermediate | advanced | expert
    experience_hours: 120      # Total hours working with this skill
    last_used: "2025-11-12"    # ISO 8601 date
    success_rate: 0.95         # Historical success rate (0.0-1.0)
    notes: "Additional context"
```

### 3. Cost Profile
```yaml
cost_profile:
  base_rate_per_hour: 5.0    # USD per hour
  variable_cost: true         # Adjust based on task complexity
  currency: "USD"
```

### 4. Availability
```yaml
availability:
  status: "available"         # available | busy | offline | maintenance
  max_concurrent_tasks: 3     # Maximum parallel capacity
  current_load: 1             # Current active tasks
```

### 5. Bloom Pattern
```yaml
bloom_pattern:
  classification: "late_bloomer"  # early_bloomer | steady_performer | late_bloomer
  simple_tasks_success: 0.65
  moderate_tasks_success: 0.80
  complex_tasks_success: 0.93
  expert_tasks_success: 0.96
```

### 6. Reputation (from F6.11)
```yaml
reputation:
  overall_score: 0.92            # 0.0-1.0
  reliability: 0.95               # Task completion rate
  quality: 0.93                   # Output quality
  speed: 0.88                     # Time efficiency
  cost_efficiency: 0.91           # Cost effectiveness
  bloom_accuracy: 0.92            # Matches bloom pattern
  tier: "excellent"               # excellent | good | acceptable | concerning | poor
```

---

## Domain Taxonomy

### Primary Domains Used

1. **video**: Video production, streaming, encoding
   - `video.streaming.*`: NDI, RTMP, HLS, WebRTC
   - `video.encoding.*`: H.264, H.265, VP8, VP9
   - `video.production.*`: vMix, OBS

2. **telephony**: Voice/video calling protocols
   - `telephony.sip.*`: SIP signaling, registration, proxy
   - `telephony.webrtc.*`: WebRTC signaling, media, data channels
   - `telephony.h323.*`: H.323 protocol, gatekeeper, gateway
   - `telephony.codecs.*`: G.711, G.729, Opus

3. **crypto**: Cryptographic operations
   - `crypto.signatures.*`: Ed25519, RSA, ECDSA
   - `crypto.hashing.*`: BLAKE3, SHA-256
   - `crypto.key_mgmt.*`: Scoped credentials, key rotation

4. **infra**: Infrastructure orchestration
   - `infra.coordination.*`: etcd, NATS, Consul
   - `infra.orchestration.*`: Docker, Kubernetes
   - `infra.monitoring.*`: Prometheus, logging, SLO tracking
   - `infra.resource_mgmt.*`: Governor, circuit breakers, budgets
   - `infra.sandbox.*`: WASM runtime, resource limits

5. **programming**: Programming languages
   - `programming.python.*`: asyncio, CLI, networking, performance
   - `programming.javascript.*`: Node.js, React
   - `programming.rust.*`: WASM modules

6. **smart_home**: Home automation
   - `smart_home.automation.*`: Home Assistant, OpenHAB
   - `smart_home.protocols.*`: MQTT, Zigbee, Z-Wave

7. **talent**: Talent management (custom domain)
   - `talent.scoring.*`: Assignment, reputation algorithms
   - `talent.registry.*`: Capability registry
   - `talent.analysis.*`: Bloom patterns

8. **architecture**: System architecture
   - `architecture.adapter_patterns`: Integration adapters
   - `architecture.system_design`: System architecture
   - `architecture.policy_engines`: Policy engine design

---

## Skill Levels

| Level | Experience Hours | Success Rate | Use Cases |
|-------|------------------|--------------|-----------|
| **Novice** | 0-20 hours | 50-70% | Learning phase, simple tasks with supervision |
| **Intermediate** | 20-50 hours | 70-85% | Can handle simple and moderate tasks independently |
| **Advanced** | 50-100 hours | 85-95% | Can handle complex tasks, mentors others |
| **Expert** | 100+ hours | 95-100% | Mastery, handles all complexities including edge cases |

---

## Bloom Patterns Explained

### Early Bloomer (Session 5 - CLI)
- **Simple tasks:** 95% success (excellent)
- **Complex tasks:** 65% success (struggles)
- **Best for:** CLI tools, simple scripts, straightforward implementations
- **Avoid:** Complex algorithm design, intricate protocol implementations

### Steady Performer (Sessions 2, 4, 6)
- **All tasks:** 83-89% success (consistent)
- **Best for:** Any task complexity - reliable across the board
- **Avoid:** Nothing specific - well-rounded

### Late Bloomer (Sessions 1, 3, 7)
- **Simple tasks:** 60-65% success (slower)
- **Complex tasks:** 93-97% success (excels)
- **Best for:** Complex protocols, intricate systems, expert-level work
- **Avoid:** Trivial tasks (overkill, inefficient use of expensive resource)

---

## Integration with F6.3 Assignment Algorithm

The capability profiles feed into the **F6.3 multi-factor assignment algorithm**:

```python
Score(agent, task) = 0.40·Capability + 0.30·Bloom + 0.15·Cost + 0.10·Experience + 0.05·Availability

# Components from capability profile:
# - Capability: calculate_capability_score(profile.capabilities, task_requirements)
# - Bloom: profile.bloom_pattern matched against task.complexity
# - Cost: profile.cost_profile.base_rate_per_hour
# - Experience: profile.reputation (from F6.11)
# - Availability: profile.availability.current_load / max_concurrent_tasks
```

**Assignment threshold:** 0.70 (70%) minimum score required

---

## Cost Optimization Examples

### Example 1: Simple NDI Setup

**Before Capability Registry:**
```
Task: Simple NDI setup (complexity=simple)
Assigned: session-1-ndi (expert, late bloomer, $5/hour)
Duration: 1 hour
Cost: $5.00
Performance: 65% success (not optimized for simple tasks)
Issue: Over-qualified, bloom pattern mismatch
```

**After Capability Registry:**
```
Task: Simple NDI setup (complexity=simple)
Query: Find agent with video.streaming.ndi_protocol >= intermediate

Candidates (sorted by F6.3 score):
1. session-early-ndi (intermediate, early bloomer, $3/hour): Score 0.78
2. session-1-ndi (expert, late bloomer, $5/hour): Score 0.72

Assigned: session-early-ndi
Duration: 1 hour
Cost: $3.00 (40% savings)
Performance: 90% success (bloom pattern match)
```

### Example 2: Complex WebRTC Mesh

**Before Capability Registry:**
```
Task: Complex WebRTC mesh (complexity=expert)
Assigned: Random session with some networking experience
Duration: 5 hours (struggled)
Cost: $15.00
Performance: 60% success (barely passed)
```

**After Capability Registry:**
```
Task: Complex WebRTC mesh (complexity=expert)
Query: Find agent with telephony.webrtc.* >= advanced

Candidates (sorted by F6.3 score):
1. session-2-webrtc (expert, steady performer, $5/hour): Score 0.94

Assigned: session-2-webrtc
Duration: 2 hours (efficient)
Cost: $10.00 (33% savings)
Performance: 94% success (capability + bloom match)
```

---

## Validation Checklist

When creating new profiles:

- [ ] All capabilities follow `domain.category.skill` naming
- [ ] Skill levels match experience hours and success rates
- [ ] Bloom pattern classification matches empirical data
- [ ] Reputation scores consistent with F6.11 algorithm
- [ ] Cost profile realistic for agent's expertise
- [ ] Availability reflects actual capacity
- [ ] Documentation URLs valid
- [ ] Tags appropriate and searchable

---

## Next Steps

### Phase 0 (Current)
1. ✅ Create example profiles for all 7 sessions (this directory)
2. ⏳ Implement IF.governor with capability registry
3. ⏳ Sessions register actual profiles
4. ⏳ Test F6.3 assignment algorithm integration

### Phase 1
1. Create profiles for new NDI integration agents
2. Expand domain taxonomy for additional providers
3. Validate cost optimization (57% → <10% waste target)

### Phase 2+
1. Support 116+ integrations (cloud, payment, chat, AI/ML)
2. Automatic skill level updates based on task outcomes
3. Real-time reputation scoring (F6.11 integration)
4. Performance optimization (<50ms query target)

---

## References

- [F6.3: Talent Assignment Scoring Algorithm](../../TALENT-ASSIGNMENT-SCORING-ALGORITHM.md)
- [F6.11: Talent Reputation Scoring System](../../TALENT-REPUTATION-SCORING-SYSTEM.md)
- [F6.12: Capability Registry Schema](../../CAPABILITY-REGISTRY-SCHEMA.md)
- [Phase 0 Task Board](../../../PHASE-0-TASK-BOARD.md)
- [InfraFabric Architecture](../../../SWARM-OF-SWARMS-ARCHITECTURE.md)

---

**Status:** Complete (F6.13)
**Author:** Session 6 (Talent)
**Date:** 2025-11-12
**Integration:** IF.governor (Phase 0), F6.3 (Assignment), F6.11 (Reputation)
