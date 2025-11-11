# IF.bus Adapter Pattern Design

**Purpose:** Unified interface to heterogeneous SIP servers
**Pattern:** Adapter + Strategy + IF.talent Bloom Detection
**Author:** Session 6 (IF.talent) helping Session 7 (IF.bus)
**Date:** 2025-11-11
**Citation:** if://design/bus/adapter-pattern-v1

---

## Problem Statement

**Challenge:** 7 different SIP servers, 7 different APIs

| Server | API Style | Auth Method | Complexity |
|--------|-----------|-------------|-----------|
| Asterisk | AMI (Manager Interface) | Basic/Digest | Medium |
| FreeSWITCH | ESL (Event Socket) | Custom | High |
| Kamailio | JSONRPC / MI | Basic/OAuth | Medium |
| OpenSIPs | MI (Management Interface) | Basic/OAuth | Medium |
| Elastix | FreePBX API (REST) | API Key | Low |
| Yate | Telnet/Custom | Custom | High |
| Jitsi | REST API | OAuth | Low |

**Traditional Approach:**
```python
# Brittle, hard to maintain
if server_type == "asterisk":
    ami = AsteriskAMI(host, port)
    ami.login(username, password)
    ami.originate(channel, context, exten)
elif server_type == "freeswitch":
    esl = FreeSWITCHESL(host, port)
    esl.connect(password)
    esl.api("originate", params)
elif server_type == "kamailio":
    # ... 5 more elif branches
```

**Problems:**
- High coupling (caller knows all server implementations)
- Hard to add new servers (modify all call sites)
- No polymorphism (can't treat servers uniformly)
- No bloom pattern optimization (all servers treated equally)

---

## Solution: Unified Adapter Pattern + IF.talent Bloom Detection

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│               IF.bus Client (User Code)                  │
│  "I want to make a call, don't care which server"       │
└───────────────────────┬─────────────────────────────────┘
                        │
                        v
            ┌───────────────────────┐
            │ SIPServerAdapter      │
            │  (Abstract Base)      │
            │                       │
            │ + connect()           │
            │ + make_call()         │
            │ + hangup()            │
            │ + get_status()        │
            │ + detect_server_type()│
            │ + is_suitable_for()   │ ← IF.talent bloom logic
            └───────────┬───────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        v               v               v
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Asterisk   │ │  FreeSWITCH  │ │   Kamailio   │
│   Adapter    │ │   Adapter    │ │   Adapter    │
│              │ │              │ │              │
│ AMI Protocol │ │ ESL Protocol │ │ JSONRPC API  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       v                v                v
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Asterisk    │ │ FreeSWITCH   │ │  Kamailio    │
│   Server     │ │   Server     │ │   Server     │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## Core Components

### 1. Abstract Base Class (`SIPServerAdapter`)

**Philosophy:** Define contract, not implementation

```python
class SIPServerAdapter(ABC):
    """Unified interface to heterogeneous SIP servers"""

    @abstractmethod
    def connect(self, auth_config: Dict) -> bool:
        """Connect with flexible auth (apikey, basic, oauth, custom)"""
        pass

    @abstractmethod
    def make_call(self, from_uri, to_uri, codec="opus", options=None):
        """Initiate call (returns success, call_id)"""
        pass

    @abstractmethod
    def hangup(self, call_id: str) -> bool:
        """Terminate call"""
        pass

    # ... other methods
```

**Benefits:**
- **Polymorphism:** Treat all servers uniformly
- **Extensibility:** Add new servers without changing client code
- **Testability:** Mock adapters for testing

---

### 2. Bloom Pattern Detection (IF.talent Integration)

**Insight from IF.talent:** Capabilities have bloom patterns - when do they excel?

**Application to SIP Servers:**

| Server | Bloom Pattern | Meaning | Best For |
|--------|---------------|---------|----------|
| **Asterisk** | Early Bloomer | Simple tasks easy, complex hard | Small office PBX, voicemail |
| **FreeSWITCH** | Steady Performer | Consistent across scenarios | Conferencing, transcoding |
| **Kamailio** | Late Bloomer | Excels at high scale | Carrier-grade routing |
| **OpenSIPs** | Late Bloomer | Scales well, WebRTC strong | WebRTC gateway, load balancing |
| **Elastix** | Early Bloomer | Legacy support strong | H.323 bridging, fax |
| **Yate** | Steady Performer | Flexible, multi-protocol | Custom routing |
| **Jitsi** | Early Bloomer | WebRTC native | Browser conferencing |

**Capability Profile Example (Asterisk):**
```python
SIPServerCapability(
    server_type=SIPServerType.ASTERISK,
    bloom_pattern=BloomPattern.EARLY_BLOOMER,
    best_for=["simple_pbx", "voicemail", "ivr"],
    avoid_for=["high_scale_routing", "complex_conferencing"],
    max_concurrent_calls=500,
    protocols_supported=["SIP", "H.323", "IAX2"],
    avg_setup_latency_ms=250.0,
    cost_per_call=0.001
)
```

**Usage:**
```python
# IF.bus router can select optimal server for task
asterisk = AsteriskAdapter("myasterisk", "10.0.0.5")

# Check suitability
suitable, reason = asterisk.is_suitable_for("simple_pbx")
# Returns: (True, "asterisk excels at simple_pbx (early_bloomer)")

suitable, reason = asterisk.is_suitable_for("high_scale_routing")
# Returns: (False, "asterisk struggles with high_scale_routing")
```

---

### 3. Auto-Detection

**Challenge:** User shouldn't need to specify server type manually

**Solution:** Probe with SIP OPTIONS

```python
def detect_server_type(self) -> SIPServerType:
    """
    Send SIP OPTIONS request, parse User-Agent header

    Example responses:
    - "Asterisk PBX 18.0.0" → SIPServerType.ASTERISK
    - "FreeSWITCH 1.10.7" → SIPServerType.FREESWITCH
    - "kamailio (5.5.0)" → SIPServerType.KAMAILIO
    """
    # Send: OPTIONS sip:host:port SIP/2.0
    # Parse: User-Agent header
    # Match against patterns
```

**CLI Integration:**
```bash
# Auto-detect server type
if bus add sip myserver --host 10.0.0.5 --auto-detect

# Output: Detected: Asterisk PBX 18.0.0 (early_bloomer)
```

---

### 4. Flexible Authentication

**Problem:** Each server uses different auth methods

**Solution:** Unified auth config structure

```python
auth_config = {
    "method": "apikey" | "basic" | "oauth" | "custom",
    "credentials": {
        # Method-specific credentials
        # apikey: {"key": "ABC123"}
        # basic: {"username": "admin", "password": "secret"}
        # oauth: {"token": "bearer_token"}
        # custom: {"connection_string": "..."}
    }
}
```

**Adapter-specific handling:**
```python
class AsteriskAdapter(SIPServerAdapter):
    def connect(self, auth_config):
        if auth_config["method"] == "basic":
            username = auth_config["credentials"]["username"]
            password = auth_config["credentials"]["password"]
            self.ami.login(username, password)
        else:
            raise ValueError("Asterisk only supports basic auth")
```

---

## Design Patterns Applied

### 1. **Adapter Pattern** (GoF)
- **Intent:** Convert interface of a class into another interface clients expect
- **Application:** Convert heterogeneous SIP server APIs to unified SIPServerAdapter interface

### 2. **Strategy Pattern** (GoF)
- **Intent:** Define family of algorithms, encapsulate each, make them interchangeable
- **Application:** Each adapter is a strategy for SIP communication

### 3. **Template Method** (GoF)
- **Intent:** Define skeleton of algorithm, let subclasses override specific steps
- **Application:** Base class provides common utilities (detect_server_type, validate_auth), subclasses implement server-specific methods

### 4. **IF.talent Bloom Pattern** (InfraFabric)
- **Intent:** Characterize when capabilities excel (early, steady, late bloomers)
- **Application:** SIP servers have bloom patterns - select optimal server for use case

---

## IF.ground Philosophy Integration

| Principle | Application |
|-----------|-------------|
| **Principle 4: Underdetermination** | Multiple servers solve same problem differently, choice depends on context |
| **Principle 6: Pragmatism** | Judge servers by usefulness (bloom patterns), not ideology |
| **Principle 8: Stoic Prudence** | Graceful degradation (if primary server fails, fall back to secondary) |

### Wu Lun (Five Relationships)

**朋友 (Friends):** Each adapter is a friend with unique strengths

- Asterisk: Friend who's great at simple tasks (小事高手)
- FreeSWITCH: Friend who's reliable in all scenarios (稳定可靠)
- Kamailio: Friend who excels under pressure (高压专家)

**Principle:** Don't force friends into roles they're bad at. Asterisk shouldn't handle high-scale routing (that's Kamailio's strength).

---

## Usage Examples

### Example 1: Make a Call (Polymorphic)

```python
# Works with ANY adapter!
def make_call_via_adapter(adapter: SIPServerAdapter, from_uri, to_uri):
    """Polymorphic - works with Asterisk, FreeSWITCH, Kamailio, etc."""

    if not adapter.connected:
        adapter.connect(auth_config)

    success, call_id = adapter.make_call(from_uri, to_uri, codec="opus")

    if success:
        print(f"Call initiated: {call_id}")
    else:
        print("Call failed")

# Use with Asterisk
asterisk = AsteriskAdapter("myasterisk", "10.0.0.5")
make_call_via_adapter(asterisk, "sip:alice@example.com", "sip:bob@example.com")

# Use with FreeSWITCH (SAME CODE!)
freeswitch = FreeSWITCHAdapter("myfs", "10.0.0.6")
make_call_via_adapter(freeswitch, "sip:alice@example.com", "sip:bob@example.com")
```

### Example 2: Bloom-Aware Routing

```python
def select_optimal_server(use_case: str, available_servers: List[SIPServerAdapter]):
    """Select optimal SIP server based on bloom patterns"""

    for server in available_servers:
        suitable, reason = server.is_suitable_for(use_case)
        if suitable:
            capability = server.get_capability_profile()
            print(f"Selected: {server.server_name} ({capability.bloom_pattern.value})")
            print(f"  Reason: {reason}")
            return server

    # Fallback
    return available_servers[0]

# Usage
servers = [
    AsteriskAdapter("asterisk1", "10.0.0.5"),
    KamailioAdapter("kamailio1", "10.0.0.6")
]

# For simple PBX task → selects Asterisk (early bloomer)
server = select_optimal_server("simple_pbx", servers)

# For high-scale routing → selects Kamailio (late bloomer)
server = select_optimal_server("high_scale_routing", servers)
```

### Example 3: Cost Estimation

```python
# IF.optimise integration
def estimate_call_cost(adapter, duration_minutes):
    """Estimate cost before making call"""
    cost = adapter.estimate_cost(duration_minutes * 60)
    print(f"Estimated cost: ${cost:.4f}")
    return cost

# Asterisk: $0.001/call = $0.05 for 50 min call
cost = estimate_call_cost(asterisk, 50)

# Kamailio: $0.0005/call = $0.025 for 50 min call (cheaper!)
cost = estimate_call_cost(kamailio, 50)
```

---

## Implementation Roadmap

### Phase 1: Base Class + 1 Adapter (Week 1)
- ✅ `SIPServerAdapter` abstract base class
- ✅ `AsteriskAdapter` concrete implementation
- ✅ Bloom pattern integration
- ✅ Auto-detection skeleton

### Phase 2: Add 6 More Adapters (Week 2-3)
- [ ] `FreeSWITCHAdapter` (ESL protocol)
- [ ] `KamailioAdapter` (JSONRPC)
- [ ] `OpenSIPsAdapter` (MI interface)
- [ ] `ElastixAdapter` (FreePBX REST API)
- [ ] `YateAdapter` (Telnet/Custom)
- [ ] `JitsiAdapter` (REST API)

### Phase 3: Advanced Features (Week 4)
- [ ] Real auto-detection (SIP OPTIONS probe)
- [ ] IF.witness logging (all adapter operations)
- [ ] IF.optimise cost tracking
- [ ] CLI integration (`if bus add sip ...`)
- [ ] Config file persistence (`~/.if/bus/sip-servers.yaml`)

### Phase 4: Production (Week 5+)
- [ ] High availability (failover between adapters)
- [ ] Load balancing (distribute calls across servers)
- [ ] Monitoring dashboard
- [ ] Integration tests (real SIP servers in Docker)

---

## Testing Strategy

### Unit Tests
```python
def test_adapter_polymorphism():
    """Verify all adapters implement SIPServerAdapter interface"""
    adapters = [
        AsteriskAdapter("test", "localhost"),
        FreeSWITCHAdapter("test", "localhost"),
        KamailioAdapter("test", "localhost")
    ]

    for adapter in adapters:
        assert hasattr(adapter, "connect")
        assert hasattr(adapter, "make_call")
        assert hasattr(adapter, "hangup")
```

### Integration Tests
```python
def test_real_asterisk_call():
    """Test with real Asterisk server in Docker"""
    # docker run -d -p 5060:5060 asterisk

    asterisk = AsteriskAdapter("test", "localhost", 5060)
    asterisk.connect({"method": "basic", "credentials": {...}})

    success, call_id = asterisk.make_call("sip:100@localhost", "sip:200@localhost")
    assert success
    assert call_id is not None

    time.sleep(5)  # Let call ring

    asterisk.hangup(call_id)
```

---

## Benefits Summary

### For IF.bus Users
- **Simplicity:** One interface for all SIP servers
- **Flexibility:** Switch servers without code changes
- **Optimization:** Bloom-aware routing saves cost + latency

### For IF.bus Maintainers
- **Extensibility:** Add new servers easily (inherit + implement)
- **Testability:** Mock adapters for unit tests
- **Maintainability:** Changes localized to one adapter

### For Session 7
- **Accelerated Development:** Base class + pattern ready, just implement 7 adapters
- **Philosophy Grounded:** IF.talent bloom patterns + Wu Lun relationships
- **Production Ready:** Follows IF.ground principles (pragmatism, coherentism)

---

## Conclusion

The **IF.bus Adapter Pattern** unifies heterogeneous SIP servers with:

1. **Abstract Base Class:** `SIPServerAdapter` defines contract
2. **Bloom Patterns:** IF.talent capability profiling (early/steady/late bloomers)
3. **Auto-Detection:** Probe servers to identify type
4. **Flexible Auth:** Support apikey, basic, oauth, custom
5. **Polymorphism:** Treat all servers uniformly in client code

**Result:** Session 7 can implement 7 adapters quickly, IF.bus users get simple unified API

**Philosophy:** Wu Lun - Each server is a friend (朋友) with unique strengths, don't force them into wrong roles

---

**Citation:** if://design/bus/adapter-pattern-v1
**Status:** Design Complete ✅
**Next:** Session 7 implements 7 concrete adapters (Phase 2)
**Time:** 4 hours (Session 6 contribution)
**Cost:** ~$6 (Sonnet agent)

---

*Session 6 (IF.talent) helping Session 7 (IF.bus) - Swarm Coordination*

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
