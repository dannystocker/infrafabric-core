# CLI Architecture Gaps & Implementation Plan

**Status:** CRITICAL - CLI not ready for 116+ provider integrations
**Date:** 2025-11-12
**Branch:** claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

---

## Executive Summary

**Question:** Is our CLI ready for 116+ integrations (vMix, OBS, HA, cloud, SIP, payment, chat, AI)?

**Answer:** **NO** - Critical architecture gaps must be addressed first.

**Current State:**
- ✅ Python package exists: `infrafabric/` (v0.1.0)
- ✅ Core modules: guardians, coordination, manifests
- ⚠️ Minimal CLI: `tools/ifctl.py` (50 lines, lint only)
- ⚠️ Proof-of-concept: `tools/bus_sip.py` (28 lines, SIP only)
- ❌ No unified `if` command
- ❌ No plugin system for providers
- ❌ No adapter pattern implementation
- ❌ No IF.witness/IF.optimise CLI integration
- ❌ No IF.swarm orchestration module

---

## Gap Analysis

### Gap 1: No Unified CLI Entry Point

**Current:**
```bash
# No "if" command exists
which if  # Not found

# Only have:
./tools/ifctl.py lint
./tools/bus_sip.py add sip ...
```

**Required (Per Sprint Files):**
```bash
if vmix add myvmix --host 192.168.1.100
if obs scene switch myobs "Main Scene"
if ha camera stream myhome camera.front_door
if cloud vm create aws myaccount --type t3.medium
if sip call twilio myprovider --to +1234567890
if payment charge stripe mypayments --amount 1000
if chat send telegram mychannel "Hello"
if ai complete openai mygpt4 --prompt "Explain IF"
if swarm spawn --profile production-sprint --sessions 7
if bus orchestrate --profile live-streaming-studio
```

**Impact:** **CRITICAL** - No way to invoke 116+ provider integrations

---

### Gap 2: No Provider Plugin System

**Current:**
```python
# infrafabric/__init__.py exports only:
- GuardianPanel
- WeightedCoordinator
- ManifestGenerator

# No provider plugin loading mechanism
```

**Required:**
```python
# Plugin discovery and loading
class ProviderRegistry:
    """Discover and load provider plugins"""

    def discover_plugins(self, plugin_dir='~/.if/plugins'):
        """Auto-discover provider plugins"""
        # Load from:
        # - ~/.if/plugins/vmix/
        # - ~/.if/plugins/obs/
        # - ~/.if/plugins/cloud_aws/
        # etc.

    def load_provider(self, provider_name):
        """Dynamically load provider adapter"""
        # Import and instantiate adapter class

# Plugin structure
~/.if/plugins/
├── vmix/
│   ├── __init__.py
│   ├── adapter.py      # VMixAdapter(BaseAdapter)
│   ├── commands.py     # CLI command definitions
│   └── config.yaml     # Provider metadata
├── obs/
│   ├── adapter.py      # OBSAdapter(BaseAdapter)
│   └── ...
├── cloud_aws/
│   ├── adapter.py      # AWSAdapter(BaseAdapter)
│   └── ...
└── ai_openai/
    ├── adapter.py      # OpenAIAdapter(BaseAdapter)
    └── ...
```

**Impact:** **CRITICAL** - Cannot scale to 116+ providers without plugin system

---

### Gap 3: No Base Adapter Pattern

**Current:**
```python
# No base adapter class exists
# Each integration would be ad-hoc
```

**Required (Per Session 6 Sprint Files):**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAdapter(ABC):
    """Unified interface for all provider integrations"""

    # Lifecycle
    @abstractmethod
    async def connect(self, config: Dict[str, Any]):
        """Establish connection to provider"""

    @abstractmethod
    async def disconnect(self):
        """Clean disconnect"""

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health"""

    # Discovery
    @abstractmethod
    async def discover_instances(self) -> List[Dict]:
        """Auto-discover provider instances (mDNS, API, etc.)"""

    # Execution
    @abstractmethod
    async def execute_command(self, command: str, **params) -> Dict[str, Any]:
        """Execute provider-specific command"""

    # Observability
    def log_operation(self, operation: str, params: Dict, result: Any):
        """Log to IF.witness"""
        from infrafabric.witness import log_operation
        log_operation(
            provider=self.provider_name,
            operation=operation,
            params=params,
            result=result,
            signature=self._sign_operation(operation, params, result)
        )

    def track_cost(self, operation: str, cost: float):
        """Track to IF.optimise"""
        from infrafabric.optimise import track_operation_cost
        track_operation_cost(
            provider=self.provider_name,
            operation=operation,
            cost=cost
        )

# Provider-specific adapters inherit from BaseAdapter
class VMixAdapter(BaseAdapter):
    provider_name = "vmix"

    async def connect(self, config):
        # Connect to vMix TCP API
        self.host = config['host']
        self.port = config.get('port', 8088)
        # ...

    async def execute_command(self, command, **params):
        if command == "cut":
            # Send vMix CUT command
        elif command == "fade":
            # Send vMix FADE command
        # ...

class OBSAdapter(BaseAdapter):
    provider_name = "obs"
    # ... obs-websocket implementation

class OpenAIAdapter(BaseAdapter):
    provider_name = "openai"
    # ... OpenAI API implementation
```

**Impact:** **CRITICAL** - No consistent interface across 116+ providers

---

### Gap 4: No Config Management System

**Current:**
```python
# tools/bus_sip.py stores config ad-hoc:
~/.if/sip_servers.json

# No unified config system
```

**Required:**
```yaml
# ~/.if/config.yaml - Global config
if:
  witness:
    enabled: true
    signing_key: ~/.if/keys/ed25519.key
  optimise:
    enabled: true
    budget_alerts: true
    cost_tracking: true
  ground:
    philosophy: wu_lun
    principles:
      - open_source_first
      - validate_with_toolchain
      - observability_without_fragility

# ~/.if/providers/vmix.yaml
instances:
  myvmix:
    host: 192.168.1.100
    port: 8088
    enabled: true
  studio2:
    host: 192.168.1.101
    port: 8088
    enabled: false

# ~/.if/providers/openai.yaml
instances:
  mygpt4:
    api_key: sk-...  # Or reference to keychain
    model: gpt-4
    max_tokens: 2000
```

**Impact:** **HIGH** - No way to manage 116+ provider credentials/configs

---

### Gap 5: No IF.witness CLI Integration

**Current:**
```python
# infrafabric/manifests.py exists
# But no CLI integration
```

**Required:**
```bash
# All CLI operations should be logged
if vmix cut myvmix --input 1
  ├─> Execute vMix command
  ├─> IF.witness: Log operation with Ed25519 signature
  └─> Hash chain: link to previous operation

# Query provenance
if witness log --operation vmix.cut --since "1 hour ago"
if witness verify --operation-id abc123
if witness chain --trace-from abc123
```

**Impact:** **MEDIUM** - No cryptographic provenance for operations

---

### Gap 6: No IF.optimise CLI Integration

**Current:**
```python
# No IF.optimise module exists yet
```

**Required:**
```bash
# Cost tracking for all operations
if ai complete openai mygpt4 --prompt "Long prompt..."
  ├─> Execute OpenAI completion
  ├─> IF.optimise: Track cost ($0.02)
  └─> Budget: $48.50 remaining / $50.00 daily limit

# Cost queries
if optimise report --provider openai --since "1 week ago"
if optimise budget set --daily 50 --monthly 1000
if optimise budget status
```

**Impact:** **MEDIUM** - No cost control for 116+ providers

---

### Gap 7: No IF.swarm Orchestration Module

**Current:**
```python
# S² (Swarm of Swarms) documented in sprint files
# But no IF.swarm module implementation
```

**Required (Per Phase 6 Roadmap):**
```bash
# Multi-session orchestration
if swarm spawn --profile production-sprint --sessions 7
  ├─> Session 1-7: Each spawns agent swarms
  ├─> Git-based coordination (30s polling)
  ├─> Auto-detect blockers
  └─> "Gang Up on Blocker" pattern

# Orchestration profiles
if bus orchestrate --profile live-streaming-studio
  ├─> HA: Turn on studio lights
  ├─> HA: Enable cameras
  ├─> vMix: Load production scene
  ├─> OBS: Start virtual camera
  └─> IF.witness: Log all actions

# Swarm status
if swarm status
if swarm sessions
if swarm help session-4  # Trigger "Gang Up on Blocker"
```

**Impact:** **HIGH** - Revolutionary feature not implemented

---

## Implementation Plan

### Phase 0: CLI Foundation (Before ANY Provider Integration)

**Estimated:** 8-12 hours
**Cost:** $120-180
**Deliverables:**

1. **Unified CLI Entry Point**
   ```bash
   # Install as package
   pip install -e .  # Installs "if" command

   # Usage
   if --version
   if --help
   if <provider> <command> [args]
   ```

2. **Base Adapter Pattern**
   ```python
   # src/infrafabric/adapters/base.py
   class BaseAdapter(ABC):
       # ... (see Gap 3 above)
   ```

3. **Plugin System**
   ```python
   # src/infrafabric/plugins/registry.py
   class ProviderRegistry:
       def discover_plugins(self)
       def load_provider(self, name)
       def register_commands(self, provider)
   ```

4. **Config Management**
   ```python
   # src/infrafabric/config/manager.py
   class ConfigManager:
       def load_global_config(self)
       def load_provider_config(self, provider)
       def save_provider_instance(self, provider, name, config)
   ```

5. **IF.witness Integration**
   ```python
   # src/infrafabric/witness.py (enhance existing manifests.py)
   def log_operation(provider, operation, params, result)
   def verify_operation(operation_id)
   def get_operation_chain(operation_id)
   ```

6. **IF.optimise Module**
   ```python
   # src/infrafabric/optimise.py
   class CostTracker:
       def track_operation_cost(provider, operation, cost)
       def get_budget_status(period='daily')
       def set_budget_limit(daily=None, monthly=None)
   ```

**File Structure After Phase 0:**
```
infrafabric/
├── __init__.py
├── cli/
│   ├── __init__.py
│   ├── main.py           # Entry point for "if" command
│   └── commands.py       # Core commands (witness, optimise, swarm, bus)
├── adapters/
│   ├── __init__.py
│   ├── base.py           # BaseAdapter ABC
│   └── registry.py       # Provider plugin registry
├── plugins/
│   ├── __init__.py
│   └── loader.py         # Plugin discovery and loading
├── config/
│   ├── __init__.py
│   └── manager.py        # Config management
├── witness.py            # IF.witness (enhance manifests.py)
├── optimise.py           # IF.optimise (NEW)
├── swarm.py              # IF.swarm orchestration (NEW)
├── guardians.py          # Existing
├── coordination.py       # Existing
└── manifests.py          # Existing

setup.py or pyproject.toml:
  entry_points:
    console_scripts:
      if = infrafabric.cli.main:main
```

---

### Phase 1.5a: First 3 Provider Integrations (vMix, OBS, HA)

**Estimated:** 5-6 hours wall-clock (with S² parallelization)
**Cost:** $135-210
**Status:** IN PROGRESS (sprint files exist)

**Deliverables:**
```
infrafabric/plugins/
├── vmix/
│   ├── __init__.py
│   ├── adapter.py        # VMixAdapter(BaseAdapter)
│   └── commands.py       # cut, fade, stream, record, etc.
├── obs/
│   ├── adapter.py        # OBSAdapter(BaseAdapter)
│   └── commands.py       # scene, source, stream, record, etc.
└── home_assistant/
    ├── adapter.py        # HomeAssistantAdapter(BaseAdapter)
    └── commands.py       # camera, light, automation, etc.
```

**Note:** Sprint files already designed (VMIX-SPRINT-ALL-SESSIONS.md, etc.)

---

### Phase 2-6: Remaining 113+ Provider Integrations

**Timeline:** Post-GPT-5 Pro review (phased)
**Total:** 146-183 hours, $2,300-3,380

Each provider follows same pattern:
```
infrafabric/plugins/<provider_name>/
├── adapter.py      # Inherits from BaseAdapter
└── commands.py     # CLI commands
```

---

## Critical Path Decision

**MUST DO BEFORE vMix/OBS/HA sprints complete:**

### Option A: Build CLI Foundation NOW (Recommended)

**Timeline:**
1. **Now:** Build Phase 0 (CLI foundation) - 8-12 hours
2. **Then:** vMix/OBS/HA sprints can complete properly - 5-6 hours
3. **Then:** GPT-5 Pro review
4. **Then:** Phases 2-6 (113+ providers)

**Pros:**
- ✅ vMix/OBS/HA integrations work immediately
- ✅ Proper architecture from day 1
- ✅ Easy to add 113+ providers after review
- ✅ IF.witness/IF.optimise tracking from start

**Cons:**
- ⏰ Adds 8-12 hours before sprints complete

---

### Option B: Retrofit CLI Foundation Later (Not Recommended)

**Timeline:**
1. **Now:** Complete vMix/OBS/HA sprints without unified CLI - 5-6 hours
2. **Problem:** Each creates ad-hoc CLI (like bus_sip.py)
3. **Then:** Retrofit unified CLI - 12-16 hours (harder!)
4. **Then:** Migrate vMix/OBS/HA to new pattern - 4-6 hours
5. **Then:** GPT-5 Pro review
6. **Then:** Phases 2-6

**Pros:**
- ⏰ Sprints complete faster (no foundation wait)

**Cons:**
- ❌ vMix/OBS/HA become ad-hoc implementations
- ❌ Retrofitting is harder (12-16h vs 8-12h)
- ❌ Migration pain (4-6h additional work)
- ❌ Technical debt before 113+ providers
- ❌ No IF.witness/IF.optimise tracking initially

---

## Recommendation

### ✅ Option A: Build CLI Foundation NOW

**Rationale:**
1. **S² parallelization works for foundation too:**
   - Spawn agents for Phase 0 just like provider integrations
   - 8-12h sequential → 2-3h wall-clock with 4-5 agents

2. **Proper architecture is cheaper:**
   - Phase 0: 8-12h
   - vs Retrofit: 12-16h + 4-6h migration = 16-22h

3. **116+ providers need it anyway:**
   - Can't add cloud/SIP/payment/chat/AI providers without foundation
   - Better to build once, build right

4. **IF.witness/IF.optimise tracking:**
   - Critical for production use
   - Should track from first operation

---

## Next Steps

### Immediate Actions

1. **Create Phase 0 Sprint:**
   ```markdown
   # PHASE-0-CLI-FOUNDATION-SPRINT.md

   Mission: Build unified CLI foundation before provider integrations

   Session Assignment:
   - Session 5 (CLI): Lead - unified CLI entry point
   - Session 6 (Talent): Base adapter pattern
   - Session 7 (IF.bus): Plugin system + IF.swarm module
   - All: Help with IF.witness/IF.optimise integration

   Timeline: 8-12h sequential → 2-3h wall-clock (S² parallelization)
   Cost: $120-180
   ```

2. **Update vMix/OBS/HA sprints:**
   - Block on Phase 0 completion
   - Update to use unified plugin pattern

3. **After Phase 0:**
   - Resume vMix/OBS/HA sprints with proper foundation
   - GPT-5 Pro review
   - Phases 2-6 (113+ providers)

---

## File Structure Roadmap

### Now (Pre-Phase 0)
```
infrafabric/
├── __init__.py           # Exports: guardians, coordination, manifests
├── guardians.py
├── coordination.py
└── manifests.py

tools/
├── ifctl.py              # Lint only (50 lines)
└── bus_sip.py            # Ad-hoc SIP (28 lines)
```

### After Phase 0 (CLI Foundation)
```
infrafabric/
├── __init__.py
├── cli/
│   ├── main.py           # "if" command entry point
│   └── commands.py
├── adapters/
│   ├── base.py           # BaseAdapter
│   └── registry.py
├── plugins/
│   └── loader.py
├── config/
│   └── manager.py
├── witness.py            # IF.witness
├── optimise.py           # IF.optimise
├── swarm.py              # IF.swarm
├── guardians.py
├── coordination.py
└── manifests.py

setup.py or pyproject.toml  # "if" console script

~/.if/                    # User config directory
├── config.yaml           # Global config
├── providers/            # Provider configs
│   ├── vmix.yaml
│   ├── obs.yaml
│   └── ...
└── keys/
    └── ed25519.key       # IF.witness signing key
```

### After Phase 1.5a (vMix/OBS/HA)
```
infrafabric/plugins/
├── vmix/
│   ├── adapter.py
│   └── commands.py
├── obs/
│   ├── adapter.py
│   └── commands.py
└── home_assistant/
    ├── adapter.py
    └── commands.py
```

### After Phases 2-6 (All 116+ Providers)
```
infrafabric/plugins/
├── vmix/
├── obs/
├── home_assistant/
├── cloud_aws/
├── cloud_azure/
├── cloud_gcp/
├── ... (17 more cloud)
├── sip_twilio/
├── sip_bandwidth/
├── ... (28 more SIP)
├── payment_stripe/
├── payment_paypal/
├── ... (38 more payment)
├── chat_whatsapp/
├── chat_telegram/
├── chat_slack/
├── ... (13 more chat)
├── ai_openai/
├── ai_anthropic/
├── ai_google/
├── ... (17 more AI)
└── ... (126 total)
```

---

## Cost Analysis

### Building Foundation Now (Option A)
| Phase | Work | Cost | Timeline |
|-------|------|------|----------|
| Phase 0 | CLI Foundation | $120-180 | 2-3h wall-clock |
| Phase 1.5a | vMix/OBS/HA | $135-210 | 5-6h wall-clock |
| **Subtotal** | **Foundation + First 3** | **$255-390** | **7-9h wall-clock** |

### Retrofitting Later (Option B)
| Phase | Work | Cost | Timeline |
|-------|------|------|----------|
| Phase 1.5a | vMix/OBS/HA (ad-hoc) | $135-210 | 5-6h wall-clock |
| Retrofit | Rebuild CLI foundation | $180-240 | 3-4h wall-clock |
| Migration | Migrate vMix/OBS/HA | $60-90 | 1-2h wall-clock |
| **Subtotal** | **Foundation + First 3** | **$375-540** | **9-12h wall-clock** |

**Savings with Option A:** $120-150 + 2-3h wall-clock

---

## Status Summary

**Question:** Is our CLI ready for 116+ integrations?

**Answer:** **NO**

**Critical gaps:**
1. ❌ No unified `if` command
2. ❌ No plugin system
3. ❌ No base adapter pattern
4. ❌ No config management
5. ❌ No IF.witness CLI integration
6. ❌ No IF.optimise module
7. ❌ No IF.swarm orchestration

**Recommendation:** Build Phase 0 (CLI foundation) NOW before continuing vMix/OBS/HA sprints

**Timeline:** 8-12h sequential → **2-3h wall-clock** (S² parallelization)
**Cost:** $120-180
**ROI:** Saves $120-150 vs retrofitting later

**Next Step:** Create PHASE-0-CLI-FOUNDATION-SPRINT.md and spawn agents

---

## Philosophy Grounding

**Wu Lun (五倫) - 朋友 (Friends):**
All 116+ providers join as "friends" working together through unified interface.

**IF.ground Principles Applied:**
- **Principle 1:** Open source first (OBS, HA, open AI gateways)
- **Principle 2:** Validate with toolchain (all adapters tested)
- **Principle 8:** Observability without fragility (IF.witness/IF.optimise)

**IF.TTT:**
- **Traceable:** All CLI operations logged via IF.witness
- **Transparent:** All costs tracked via IF.optimise
- **Trustworthy:** Unified adapter pattern, comprehensive testing

---

**Prepared by:** Session 7 (Orchestrator)
**Date:** 2025-11-12
**Branch:** claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
**Status:** Ready for review and decision
