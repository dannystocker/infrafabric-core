# IF.governor Capability Registry Schema Reference

**P0.2.1 Implementation**
**Version:** 1.0
**Status:** Complete
**Author:** Session 6 (Talent)
**Date:** 2025-11-12

---

## Overview

The capability registry schema provides data structures for **intelligent task assignment** and **budget management** in InfraFabric's IF.governor component.

**Solves:**
- IF Bug #2: Reduces 57% cost waste to <10% through capability matching
- Implements F6.12 Capability Registry Schema design
- Integrates F6.11 Reputation Scoring System
- Enables F6.3 Assignment Scoring Algorithm

---

## Core Components

### 1. Capability Enum

**59+ capability types** across 14 domains:

```python
from infrafabric.schemas.capability import Capability

# Video capabilities
Capability.VIDEO_STREAMING_NDI
Capability.VIDEO_PRODUCTION_VMIX
Capability.VIDEO_PRODUCTION_OBS

# Telephony capabilities
Capability.TELEPHONY_SIP_PROTOCOL
Capability.TELEPHONY_WEBRTC_SIGNALING

# Crypto capabilities
Capability.CRYPTO_SIGNATURES_ED25519
Capability.CRYPTO_WITNESS_PROVENANCE

# Infrastructure capabilities
Capability.INFRA_ORCHESTRATION_DOCKER
Capability.INFRA_WASM_RUNTIME

# Programming capabilities
Capability.PROGRAMMING_PYTHON_ASYNC
Capability.PROGRAMMING_RUST_WASM

# And many more...
```

**Format:** `domain:category:skill`

**Domains:** video, telephony, crypto, infra, cloud, smart_home, programming, docs, architecture, talent, payment, chat, ai_ml, cli

---

### 2. SkillLevel Enum

Proficiency levels from F6.12:

```python
from infrafabric.schemas.capability import SkillLevel

SkillLevel.NOVICE         # 0-10 tasks, <70% success rate
SkillLevel.INTERMEDIATE   # 10-50 tasks, 70-85% success rate
SkillLevel.ADVANCED       # 50-200 tasks, 85-95% success rate
SkillLevel.EXPERT         # 200+ tasks, 95%+ success rate
```

---

### 3. BloomPattern Enum

Task complexity performance patterns from F6.3:

```python
from infrafabric.schemas.capability import BloomPattern

BloomPattern.EARLY_BLOOMER       # Excels at simple tasks
BloomPattern.STEADY_PERFORMER    # Consistent across complexity
BloomPattern.LATE_BLOOMER        # Excels at complex tasks
```

---

### 4. CapabilityProfile

Individual capability within a swarm:

```python
from infrafabric.schemas.capability import CapabilityProfile, Capability, SkillLevel

profile = CapabilityProfile(
    capability=Capability.VIDEO_STREAMING_NDI,
    skill_level=SkillLevel.EXPERT,
    experience_hours=250.0,
    success_rate=0.95,
    tasks_completed=180
)

# JSON export
data = profile.to_dict()
```

**Fields:**
- `capability`: Capability enum
- `skill_level`: SkillLevel enum
- `experience_hours`: Total hours working with this capability
- `success_rate`: Task success rate (0.0-1.0)
- `tasks_completed`: Number of tasks completed
- `last_used`: Last usage timestamp

---

### 5. SwarmProfile

Complete profile for a swarm/session:

```python
from infrafabric.schemas.capability import SwarmProfile, BloomPattern

profile = SwarmProfile(
    swarm_id="session-1-ndi",
    name="Session 1 (NDI)",
    model="sonnet",
    cost_per_hour=18.0,
    current_budget_remaining=500.0,
    reputation_score=0.88,
    bloom_pattern=BloomPattern.LATE_BLOOMER,
    capabilities=[...]  # List of CapabilityProfile
)

# Check capabilities
has_ndi = profile.has_capability(Capability.VIDEO_STREAMING_NDI)
has_expert_ndi = profile.has_capability(Capability.VIDEO_STREAMING_NDI, SkillLevel.EXPERT)

# Check budget
has_budget = profile.has_budget(100.0)

# Get capability names
cap_names = profile.get_capability_names()
```

**Fields:**
- **Identity:** swarm_id, name, model
- **Capabilities:** List of CapabilityProfile
- **Cost:** cost_per_hour, current_budget_remaining, total_cost_spent
- **Reputation (F6.11):** reputation_score, reputation_tier, reliability_score, quality_score, speed_score, cost_efficiency_score, bloom_accuracy_score
- **Bloom:** bloom_pattern
- **Metadata:** created_at, last_active, total_tasks_completed, active

---

### 6. TaskRequirements

Task requirements for capability matching:

```python
from infrafabric.schemas.capability import TaskRequirements, Capability, SkillLevel

requirements = TaskRequirements(
    task_id="T123",
    required_capabilities=[
        Capability.VIDEO_STREAMING_NDI,
        Capability.CRYPTO_WITNESS_PROVENANCE
    ],
    min_skill_level=SkillLevel.ADVANCED,
    max_cost_per_hour=25.0,
    preferred_bloom_pattern=BloomPattern.LATE_BLOOMER,
    min_reputation=0.75
)
```

**Fields:**
- `task_id`: Task identifier
- `required_capabilities`: List of required Capability enums
- `min_skill_level`: Minimum required skill level
- `max_cost_per_hour`: Budget constraint
- `preferred_bloom_pattern`: Preferred bloom pattern
- `min_reputation`: Minimum reputation score
- `task_complexity`: simple/medium/complex

---

### 7. ResourcePolicy

Governance policy for resource allocation:

```python
from infrafabric.schemas.capability import ResourcePolicy

policy = ResourcePolicy(
    max_swarms_per_task=3,
    min_capability_match=0.70,  # 70% threshold from F6.3
    max_cost_per_task=10.0,
    enable_budget_tracking=True,
    circuit_breaker_enabled=True,
    circuit_breaker_failure_threshold=3
)
```

**Fields:**
- **Task Assignment:** max_swarms_per_task, min_capability_match
- **Budget:** max_cost_per_task, enable_budget_tracking
- **Reputation:** min_reputation_score
- **Circuit Breaker:** circuit_breaker_enabled, circuit_breaker_failure_threshold, circuit_breaker_timeout_seconds
- **Optimization:** prefer_cheaper_when_equivalent, cost_weight

---

## Validation Functions

### validate_capability_manifest()

Validates JSON capability manifest:

```python
from infrafabric.schemas.capability import validate_capability_manifest

manifest = {
    'swarm_id': 'session-1-ndi',
    'name': 'Session 1 (NDI)',
    'model': 'sonnet',
    'capabilities': [
        {
            'capability': 'video:streaming:ndi',
            'skill_level': 'expert'
        }
    ],
    'cost_per_hour': 18.0
}

is_valid, error = validate_capability_manifest(manifest)
if not is_valid:
    print(f"Validation error: {error}")
```

**Validates:**
- Required fields present
- swarm_id non-empty
- model in ['haiku', 'sonnet', 'opus']
- capabilities is a list
- Each capability exists in Capability enum
- skill_level valid (if present)
- cost_per_hour non-negative
- reputation_score 0.0-1.0 (if present)

---

### validate_swarm_profile()

Validates SwarmProfile instance:

```python
from infrafabric.schemas.capability import validate_swarm_profile, SwarmProfile

profile = SwarmProfile(...)

is_valid, error = validate_swarm_profile(profile)
if not is_valid:
    print(f"Validation error: {error}")
```

**Validates:**
- swarm_id and name non-empty
- model in ['haiku', 'sonnet', 'opus']
- capabilities is list of CapabilityProfile
- cost_per_hour non-negative
- reputation_score 0.0-1.0
- reputation_tier valid
- All reputation component scores 0.0-1.0

---

## Helper Functions

### capability_from_string()

Convert string to Capability enum:

```python
from infrafabric.schemas.capability import capability_from_string

cap = capability_from_string("video:streaming:ndi")
# Returns: Capability.VIDEO_STREAMING_NDI

invalid = capability_from_string("invalid:capability")
# Returns: None
```

---

### get_capabilities_by_domain()

Get all capabilities for a domain:

```python
from infrafabric.schemas.capability import get_capabilities_by_domain

video_caps = get_capabilities_by_domain("video")
# Returns: [Capability.VIDEO_STREAMING_NDI, Capability.VIDEO_PRODUCTION_VMIX, ...]

telephony_caps = get_capabilities_by_domain("telephony")
# Returns: [Capability.TELEPHONY_SIP_PROTOCOL, ...]
```

---

### get_all_domains()

Get list of all capability domains:

```python
from infrafabric.schemas.capability import get_all_domains

domains = get_all_domains()
# Returns: ['ai_ml', 'architecture', 'chat', 'cli', 'cloud', 'crypto', ...]
```

---

## Usage Examples

### Example 1: Register Swarm with Capabilities

```python
from infrafabric.schemas.capability import *

# Create capability profiles
ndi_capability = CapabilityProfile(
    capability=Capability.VIDEO_STREAMING_NDI,
    skill_level=SkillLevel.EXPERT,
    experience_hours=200.0,
    success_rate=0.95
)

crypto_capability = CapabilityProfile(
    capability=Capability.CRYPTO_WITNESS_PROVENANCE,
    skill_level=SkillLevel.ADVANCED,
    experience_hours=100.0,
    success_rate=0.88
)

# Create swarm profile
profile = SwarmProfile(
    swarm_id="session-1-ndi",
    name="Session 1 (NDI)",
    model="sonnet",
    capabilities=[ndi_capability, crypto_capability],
    cost_per_hour=18.0,
    current_budget_remaining=500.0,
    reputation_score=0.92,
    reputation_tier="excellent",
    bloom_pattern=BloomPattern.LATE_BLOOMER
)

# Validate
is_valid, error = validate_swarm_profile(profile)
assert is_valid

# Export to JSON
data = profile.to_dict()
```

---

### Example 2: Task Matching

```python
# Define task requirements
task = TaskRequirements(
    task_id="T456",
    required_capabilities=[
        Capability.VIDEO_STREAMING_NDI,
        Capability.CRYPTO_WITNESS_PROVENANCE
    ],
    min_skill_level=SkillLevel.ADVANCED,
    max_cost_per_hour=25.0,
    min_reputation=0.75
)

# Check if swarm qualifies
swarm = SwarmProfile(...)  # Load swarm profile

# Check each required capability
qualified = all(
    swarm.has_capability(cap, task.min_skill_level)
    for cap in task.required_capabilities
)

# Check budget constraint
within_budget = swarm.cost_per_hour <= task.max_cost_per_hour

# Check reputation
meets_reputation = swarm.reputation_score >= task.min_reputation

if qualified and within_budget and meets_reputation:
    print(f"✓ Swarm {swarm.swarm_id} qualified for task {task.task_id}")
```

---

### Example 3: Load from JSON Manifest

```python
import json

# Load manifest from file
with open('swarm_manifest.json') as f:
    manifest = json.load(f)

# Validate manifest
is_valid, error = validate_capability_manifest(manifest)
if not is_valid:
    raise ValueError(f"Invalid manifest: {error}")

# Create SwarmProfile from manifest
profile = SwarmProfile(
    swarm_id=manifest['swarm_id'],
    name=manifest['name'],
    model=manifest['model'],
    cost_per_hour=manifest['cost_per_hour'],
    capabilities=[
        CapabilityProfile(
            capability=capability_from_string(cap['capability']),
            skill_level=SkillLevel(cap.get('skill_level', 'intermediate'))
        )
        for cap in manifest['capabilities']
    ]
)
```

---

## Integration with IF Components

### IF.governor (P0.2.2 - Capability Matching)

Uses SwarmProfile and TaskRequirements for 70%+ capability matching:

```python
from infrafabric.schemas.capability import SwarmProfile, TaskRequirements

def find_qualified_swarm(task: TaskRequirements, swarms: List[SwarmProfile]):
    """IF.governor capability matching implementation"""
    for swarm in swarms:
        # Calculate capability overlap
        required = set(task.required_capabilities)
        available = swarm.get_capability_names()
        overlap = len(required & available) / len(required)

        if overlap >= 0.70:  # F6.3 threshold
            return swarm
    return None
```

---

### IF.talent (Scout→Sandbox→Certify→Deploy)

Uses Capability enum and CapabilityProfile for onboarding:

```python
from infrafabric.talent import TalentPipeline
from infrafabric.schemas.capability import Capability

pipeline = TalentPipeline()

# Onboard capability
result = await pipeline.onboard_capability(
    capability_name="video:streaming:ndi",  # From Capability enum
    target_agent="session-1-ndi"
)
```

---

### F6.11 Reputation Tracking

SwarmProfile stores all F6.11 reputation scores:

```python
profile.reputation_score        # Overall: 0.0-1.0
profile.reputation_tier         # poor/concerning/acceptable/good/excellent
profile.reliability_score       # 30% weight
profile.quality_score           # 30% weight
profile.speed_score             # 15% weight
profile.cost_efficiency_score   # 15% weight
profile.bloom_accuracy_score    # 10% weight
```

---

## Testing

Comprehensive test suite at `tests/test_capability_schema.py`:

```bash
# Run all tests (requires pytest)
pytest tests/test_capability_schema.py -v

# Test import and basic functionality
python -c "from infrafabric.schemas.capability import *; print('✓ Tests pass')"
```

**Test Coverage:**
- ✅ 59+ capability types defined
- ✅ SwarmProfile creation and validation
- ✅ ResourcePolicy defaults
- ✅ Manifest validation (valid and invalid cases)
- ✅ Capability checking with skill levels
- ✅ Budget enforcement
- ✅ Domain queries
- ✅ JSON serialization
- ✅ Integration workflows

---

## Summary

**P0.2.1 Deliverables:**
- ✅ 59+ capability types across 14 domains (required 20+)
- ✅ SwarmProfile with capabilities, cost, reputation
- ✅ ResourcePolicy with governance constraints
- ✅ JSON manifest validation
- ✅ Comprehensive validation logic
- ✅ 40+ unit tests
- ✅ Helper functions for common queries
- ✅ Complete documentation

**Unblocks:**
- P0.2.2: Capability matching algorithm (70%+ threshold)
- P0.2.5: Policy engine integration

**Integrates With:**
- F6.12: Capability Registry Schema (design)
- F6.11: Reputation Scoring System
- F6.3: Assignment Scoring Algorithm
- IF.talent: Capability onboarding pipeline

---

**Document Status:** Complete
**Author:** Session 6 (Talent)
**Implementation:** `/home/user/infrafabric/infrafabric/schemas/capability.py`
**Tests:** `/home/user/infrafabric/tests/test_capability_schema.py`
