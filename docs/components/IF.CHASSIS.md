# IF.chassis - WASM Sandbox Runtime for Secure Swarm Execution

**Component**: IF.chassis
**Version**: 1.0
**Status**: Phase 0 Development
**Author**: Session 3 (H.323 Guardian Council)
**Last Updated**: 2025-11-12

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [WASM Compilation Guide](#wasm-compilation-guide)
4. [Resource Limits Configuration](#resource-limits-configuration)
5. [SLO Definition Guide](#slo-definition-guide)
6. [Security Best Practices](#security-best-practices)
7. [Example Service Contracts](#example-service-contracts)
8. [Integration Examples](#integration-examples)
9. [Troubleshooting](#troubleshooting)
10. [References](#references)

---

## Overview

### What is IF.chassis?

IF.chassis is InfraFabric's **WASM sandbox runtime** that provides secure, isolated execution environments for AI agent swarms. It solves the critical security problem: *How do we safely run untrusted or semi-trusted agent code without compromising the host system?*

### The Problem

**Before IF.chassis:**
- Swarms run as Python processes with full system access
- No resource isolation → "noisy neighbor" problem
- Shared credentials → security risk
- No SLO tracking → reputation system impossible
- Cannot safely run third-party or experimental swarms

**After IF.chassis:**
- Swarms compiled to WASM modules with strict sandboxing
- Resource limits enforced (CPU, memory, network)
- Scoped credentials (each swarm sees only its own secrets)
- SLO tracking enables reputation scores
- Production-ready security for untrusted code

### Key Benefits

1. **Security**: WASM sandboxing prevents filesystem access, network access, and system calls
2. **Isolation**: Each swarm has CPU/memory/bandwidth limits
3. **Accountability**: SLO tracking and reputation scoring
4. **Portability**: WASM modules run anywhere (Linux, macOS, Windows)
5. **Performance**: Near-native execution speed with wasmtime JIT

### Philosophical Grounding

IF.chassis embodies **IF.TTT principles**:
- **Traceable**: Every resource access logged via IF.witness
- **Transparent**: SLO metrics and resource usage visible to all
- **Trustworthy**: Sandboxing enables trust in untrusted code

Security boundaries follow **Kantian duty ethics**: Respect swarm autonomy while protecting the collective from harm.

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  IF.chassis - WASM Sandbox Runtime                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Swarm Registration & Service Contract Validation        │  │
│  │  - Load WASM module                                      │  │
│  │  - Verify service contract                               │  │
│  │  - Initialize resource limits                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  wasmtime Runtime (JIT Compiler)                         │  │
│  │  - wasm32-wasi target                                    │  │
│  │  - Memory sandboxing (linear memory model)               │  │
│  │  - Capability-based security                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Resource Manager                                         │  │
│  │  - CPU throttling (cgroups or libwasmtime limits)       │  │
│  │  - Memory limits (WASM linear memory + host overhead)   │  │
│  │  - Network bandwidth shaping (tc qdisc or eBPF)         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Credential Scoping Manager                              │  │
│  │  - Per-swarm secret store                               │  │
│  │  - WASI-crypto for key management                       │  │
│  │  - No cross-swarm credential access                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SLO Tracker & Reputation System                         │  │
│  │  - Response time p95 tracking                           │  │
│  │  - Error rate monitoring                                │  │
│  │  - Availability calculation (uptime / total time)       │  │
│  │  - Reputation score (weighted average of SLO metrics)   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  IF.witness Integration                                  │  │
│  │  - Log WASM module loads                                │  │
│  │  - Log resource limit violations                        │  │
│  │  - Log credential access (allowed/denied)               │  │
│  │  - Log SLO violations                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
        │                       │                      │
        │ Swarm calls           │ Resource metrics     │ Audit logs
        ↓                       ↓                      ↓
┌──────────────┐    ┌────────────────────┐    ┌──────────────┐
│ IF.coordinator│    │  IF.governor       │    │  IF.witness  │
│ (task queue)  │    │  (budget tracking) │    │  (audit)     │
└──────────────┘    └────────────────────┘    └──────────────┘
```

### Data Flow

**1. Swarm Registration:**
```
Swarm Owner → IF.chassis.load_swarm(swarm_id, wasm_path, service_contract)
              ↓
          Validate WASM module (wasmtime validate)
              ↓
          Parse service contract (required capabilities, resource limits)
              ↓
          Initialize resource manager (cgroups, memory limits)
              ↓
          Register with IF.governor (swarm profile + reputation)
              ↓
          Log to IF.witness (module_loaded event)
```

**2. Task Execution:**
```
IF.coordinator.push_task(swarm_id, task) → IF.chassis.execute_task(swarm_id, task)
                                             ↓
                                         Start SLO timer
                                             ↓
                                         Call WASM exported function
                                             ↓
                                         Monitor resources (CPU, memory)
                                             ↓
                                         Check credential access (scoped)
                                             ↓
                                         Stop SLO timer
                                             ↓
                                         Update reputation score
                                             ↓
                                         Return result + metadata
```

**3. Resource Violation:**
```
WASM module exceeds CPU limit → Resource Manager detects violation
                                  ↓
                              Throttle or kill WASM instance
                                  ↓
                              Log to IF.witness (resource_limit_exceeded)
                                  ↓
                              Notify IF.governor (SLO violation)
                                  ↓
                              Update reputation score (negative impact)
```

---

## WASM Compilation Guide

### Prerequisites

**System Requirements:**
- Rust 1.70+ with `wasm32-wasi` target
- wasmtime 16.0+ runtime
- Python 3.9+ (for IF.chassis host)

**Install Rust and WASM target:**
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Add wasm32-wasi target
rustup target add wasm32-wasi

# Install wasmtime
curl https://wasmtime.dev/install.sh -sSf | bash
```

### Basic WASM Module (Hello World)

**File: `swarms/hello_world/src/lib.rs`**

```rust
// WASM module for IF.chassis
// Exports a simple hello function

#[no_mangle]
pub extern "C" fn hello(name_ptr: *const u8, name_len: usize) -> i32 {
    // Read name from WASM linear memory
    let name = unsafe {
        let slice = std::slice::from_raw_parts(name_ptr, name_len);
        std::str::from_utf8_unchecked(slice)
    };

    // Return success code
    println!("Hello, {}!", name);
    0
}

#[no_mangle]
pub extern "C" fn execute_task(task_ptr: *const u8, task_len: usize) -> i32 {
    // Parse task JSON from linear memory
    let task_json = unsafe {
        let slice = std::slice::from_raw_parts(task_ptr, task_len);
        std::str::from_utf8_unchecked(slice)
    };

    // Execute task (placeholder implementation)
    println!("Executing task: {}", task_json);

    // Return success
    0
}
```

**Compile to WASM:**
```bash
cd swarms/hello_world
rustc --target wasm32-wasi --crate-type cdylib src/lib.rs -o hello_world.wasm

# Or using Cargo
cargo build --target wasm32-wasi --release
cp target/wasm32-wasi/release/hello_world.wasm ../../wasm_modules/
```

**Validate WASM module:**
```bash
wasmtime validate wasm_modules/hello_world.wasm
# Expected output: "Validation succeeded"
```

### Advanced WASM Module (H.323 Guardian)

**File: `swarms/guardian_council/src/lib.rs`**

```rust
use serde::{Deserialize, Serialize};
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

#[derive(Deserialize)]
struct Task {
    task_id: String,
    task_type: String,
    payload: serde_json::Value,
}

#[derive(Serialize)]
struct TaskResult {
    task_id: String,
    status: String,
    result: serde_json::Value,
}

#[no_mangle]
pub extern "C" fn execute_task(task_json_ptr: *const c_char) -> *mut c_char {
    // Safety: Assuming host provides valid C string
    let task_json = unsafe {
        CStr::from_ptr(task_json_ptr).to_str().unwrap()
    };

    // Parse task
    let task: Task = serde_json::from_str(task_json).unwrap();

    // Execute task based on type
    let result = match task.task_type.as_str() {
        "guardian_vote" => execute_guardian_vote(&task),
        "quality_assessment" => execute_quality_assessment(&task),
        _ => TaskResult {
            task_id: task.task_id.clone(),
            status: "error".to_string(),
            result: serde_json::json!({"error": "Unknown task type"}),
        },
    };

    // Serialize result to JSON
    let result_json = serde_json::to_string(&result).unwrap();

    // Return as C string (host must free this)
    CString::new(result_json).unwrap().into_raw()
}

fn execute_guardian_vote(task: &Task) -> TaskResult {
    // Guardian voting logic
    TaskResult {
        task_id: task.task_id.clone(),
        status: "success".to_string(),
        result: serde_json::json!({
            "vote": "approve",
            "guardian_id": "guardian-3",
            "signature": "ed25519:..."
        }),
    }
}

fn execute_quality_assessment(task: &Task) -> TaskResult {
    // Quality assessment logic
    TaskResult {
        task_id: task.task_id.clone(),
        status: "success".to_string(),
        result: serde_json::json!({
            "quality_score": 0.95,
            "assessment": "Production-ready",
            "reviewer": "guardian-council"
        }),
    }
}

#[no_mangle]
pub extern "C" fn free_result(ptr: *mut c_char) {
    // Free result string allocated by execute_task
    unsafe {
        if !ptr.is_null() {
            let _ = CString::from_raw(ptr);
        }
    }
}
```

**Cargo.toml:**
```toml
[package]
name = "guardian_council"
version = "1.0.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
```

**Build:**
```bash
cd swarms/guardian_council
cargo build --target wasm32-wasi --release
cp target/wasm32-wasi/release/guardian_council.wasm ../../wasm_modules/
```

---

## Resource Limits Configuration

### Resource Limit Specification

Resource limits are defined in the **service contract** YAML file for each swarm:

**File: `config/chassis/guardian-council.yaml`**

```yaml
swarm_id: guardian-council
wasm_module: wasm_modules/guardian_council.wasm

resource_limits:
  # CPU limit (percentage of 1 core)
  max_cpu_percent: 50

  # Memory limit (WASM linear memory + host overhead)
  max_memory_mb: 512

  # Network bandwidth limit
  max_network_bandwidth_mbps: 10

  # Maximum concurrent tasks
  max_concurrent_tasks: 5

  # Task execution timeout
  task_timeout_seconds: 30

slo_targets:
  # p95 response time target (milliseconds)
  response_time_p95_ms: 150

  # Error rate target (percentage)
  error_rate_percent: 1.0

  # Availability target (percentage)
  availability_percent: 99.9

security:
  # Credential scope (swarm can only access these credentials)
  scoped_credentials:
    - h323_gatekeeper_api_key
    - guardian_signing_key
    - mcu_admin_password

  # Allowed WASI capabilities
  wasi_capabilities:
    - wasi:io/streams
    - wasi:clocks/wall-clock
    - wasi:random/random

  # Filesystem access (none for security)
  filesystem_access: none

  # Network access (IF.chassis proxies API calls)
  network_access: proxy_only

reputation:
  # Initial reputation score (0.0-1.0)
  initial_score: 0.8

  # Weight for SLO compliance in reputation calculation
  slo_weight: 0.7

  # Weight for security compliance
  security_weight: 0.3
```

### Loading Configuration in Python

**File: `infrafabric/chassis/runtime.py`**

```python
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ResourceLimits:
    """Resource limits for WASM swarm"""
    max_cpu_percent: int
    max_memory_mb: int
    max_network_bandwidth_mbps: int
    max_concurrent_tasks: int
    task_timeout_seconds: int

@dataclass
class SLOTargets:
    """SLO targets for swarm reputation"""
    response_time_p95_ms: int
    error_rate_percent: float
    availability_percent: float

@dataclass
class ServiceContract:
    """Complete service contract for swarm"""
    swarm_id: str
    wasm_module: Path
    resource_limits: ResourceLimits
    slo_targets: SLOTargets
    scoped_credentials: List[str]
    wasi_capabilities: List[str]

def load_service_contract(config_path: Path) -> ServiceContract:
    """Load service contract from YAML"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return ServiceContract(
        swarm_id=config['swarm_id'],
        wasm_module=Path(config['wasm_module']),
        resource_limits=ResourceLimits(**config['resource_limits']),
        slo_targets=SLOTargets(**config['slo_targets']),
        scoped_credentials=config['security']['scoped_credentials'],
        wasi_capabilities=config['security']['wasi_capabilities']
    )
```

### Enforcing Resource Limits

**CPU Throttling (Linux cgroups):**

```python
import os
import subprocess

def enforce_cpu_limit(swarm_id: str, max_cpu_percent: int):
    """
    Enforce CPU limit using cgroups v2

    Example: max_cpu_percent=50 → swarm can use 50% of 1 core
    """
    cgroup_path = f"/sys/fs/cgroup/infrafabric/{swarm_id}"

    # Create cgroup
    os.makedirs(cgroup_path, exist_ok=True)

    # Set CPU quota (50% = 50000 microseconds per 100ms period)
    cpu_quota = max_cpu_percent * 1000  # microseconds per period
    with open(f"{cgroup_path}/cpu.max", 'w') as f:
        f.write(f"{cpu_quota} 100000\n")

    # Add current process to cgroup
    with open(f"{cgroup_path}/cgroup.procs", 'w') as f:
        f.write(str(os.getpid()))
```

**Memory Limit (wasmtime API):**

```python
import wasmtime

def create_wasm_store_with_limits(max_memory_mb: int) -> wasmtime.Store:
    """
    Create wasmtime Store with memory limit

    WASM linear memory is isolated and capped at max_memory_mb
    """
    config = wasmtime.Config()

    # Set maximum memory (in bytes)
    max_memory_bytes = max_memory_mb * 1024 * 1024
    config.max_memory_size = max_memory_bytes

    # Enable memory guards for out-of-bounds detection
    config.guard_region_size = 64 * 1024  # 64 KB guard pages

    engine = wasmtime.Engine(config)
    store = wasmtime.Store(engine)

    return store
```

**Network Bandwidth Limit (Linux tc):**

```python
def enforce_network_limit(swarm_id: str, max_bandwidth_mbps: int):
    """
    Enforce network bandwidth limit using Linux traffic control (tc)

    This limits outgoing bandwidth for the swarm's network namespace
    """
    # Create network namespace for isolation
    subprocess.run([
        'ip', 'netns', 'add', f'chassis_{swarm_id}'
    ], check=True)

    # Set bandwidth limit using tc qdisc
    subprocess.run([
        'tc', 'qdisc', 'add', 'dev', 'veth0', 'root', 'tbf',
        'rate', f'{max_bandwidth_mbps}mbit',
        'burst', '32kbit',
        'latency', '400ms'
    ], check=True)
```

---

## SLO Definition Guide

### What are SLOs?

**Service Level Objectives (SLOs)** define the expected performance and reliability of a swarm. IF.chassis tracks SLO compliance and uses it to calculate **reputation scores**.

### SLO Metrics

IF.chassis tracks three core SLO metrics:

1. **Response Time (p95)**: 95th percentile task execution time
2. **Error Rate**: Percentage of tasks that fail
3. **Availability**: Percentage of time swarm is responsive

### Defining SLO Targets

**Conservative (High-Reputation Swarm):**
```yaml
slo_targets:
  response_time_p95_ms: 100   # Very fast
  error_rate_percent: 0.5     # Very low error rate
  availability_percent: 99.99 # Four nines
```

**Moderate (Standard Production):**
```yaml
slo_targets:
  response_time_p95_ms: 500   # Reasonable for most tasks
  error_rate_percent: 2.0     # Acceptable error rate
  availability_percent: 99.9  # Three nines
```

**Permissive (Experimental/Development):**
```yaml
slo_targets:
  response_time_p95_ms: 2000  # Allow slower processing
  error_rate_percent: 10.0    # Higher error tolerance
  availability_percent: 95.0  # Development environment
```

### SLO Tracking Implementation

**File: `infrafabric/chassis/slo.py`**

```python
import time
from dataclasses import dataclass, field
from typing import List
from collections import deque

@dataclass
class SLOMetrics:
    """Real-time SLO metrics for a swarm"""
    swarm_id: str

    # Response time tracking (circular buffer for p95 calculation)
    response_times_ms: deque = field(default_factory=lambda: deque(maxlen=1000))

    # Error tracking
    total_tasks: int = 0
    failed_tasks: int = 0

    # Availability tracking
    uptime_seconds: float = 0.0
    downtime_seconds: float = 0.0
    last_health_check: float = field(default_factory=time.time)

    def record_task_response(self, response_time_ms: float, success: bool):
        """Record a task execution"""
        self.response_times_ms.append(response_time_ms)
        self.total_tasks += 1
        if not success:
            self.failed_tasks += 1

    def calculate_p95_response_time(self) -> float:
        """Calculate 95th percentile response time"""
        if not self.response_times_ms:
            return 0.0

        sorted_times = sorted(self.response_times_ms)
        p95_index = int(len(sorted_times) * 0.95)
        return sorted_times[p95_index]

    def calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        if self.total_tasks == 0:
            return 0.0
        return (self.failed_tasks / self.total_tasks) * 100.0

    def calculate_availability(self) -> float:
        """Calculate availability percentage"""
        total_time = self.uptime_seconds + self.downtime_seconds
        if total_time == 0:
            return 100.0
        return (self.uptime_seconds / total_time) * 100.0

    def check_slo_compliance(self, targets: SLOTargets) -> dict:
        """Check if metrics meet SLO targets"""
        p95 = self.calculate_p95_response_time()
        error_rate = self.calculate_error_rate()
        availability = self.calculate_availability()

        return {
            'response_time': {
                'actual': p95,
                'target': targets.response_time_p95_ms,
                'compliant': p95 <= targets.response_time_p95_ms
            },
            'error_rate': {
                'actual': error_rate,
                'target': targets.error_rate_percent,
                'compliant': error_rate <= targets.error_rate_percent
            },
            'availability': {
                'actual': availability,
                'target': targets.availability_percent,
                'compliant': availability >= targets.availability_percent
            }
        }
```

### Reputation Calculation

**Formula:**
```
reputation_score = (slo_compliance_score * slo_weight) + (security_compliance_score * security_weight)

slo_compliance_score = (
    response_time_compliance * 0.4 +
    error_rate_compliance * 0.3 +
    availability_compliance * 0.3
)
```

**File: `infrafabric/chassis/reputation.py`**

```python
from dataclasses import dataclass

@dataclass
class ReputationScore:
    """Reputation score for a swarm (0.0-1.0)"""
    swarm_id: str
    current_score: float
    slo_compliance_score: float
    security_compliance_score: float

    def update_from_slo_metrics(self, slo_compliance: dict):
        """Update reputation based on SLO compliance"""
        # Calculate compliance score (0.0-1.0)
        response_time_score = 1.0 if slo_compliance['response_time']['compliant'] else 0.5
        error_rate_score = 1.0 if slo_compliance['error_rate']['compliant'] else 0.5
        availability_score = 1.0 if slo_compliance['availability']['compliant'] else 0.3

        self.slo_compliance_score = (
            response_time_score * 0.4 +
            error_rate_score * 0.3 +
            availability_score * 0.3
        )

        # Update overall score (weighted average)
        self.current_score = (
            self.slo_compliance_score * 0.7 +
            self.security_compliance_score * 0.3
        )

    def record_security_violation(self):
        """Penalize reputation for security violations"""
        self.security_compliance_score *= 0.8  # 20% penalty
        self.update_overall_score()

    def update_overall_score(self):
        """Recalculate overall reputation score"""
        self.current_score = (
            self.slo_compliance_score * 0.7 +
            self.security_compliance_score * 0.3
        )
```

---

## Security Best Practices

### Principle 1: Least Privilege

**Never grant more access than necessary.**

❌ **Bad:**
```yaml
security:
  scoped_credentials:
    - "*"  # All credentials accessible
  wasi_capabilities:
    - "*"  # All capabilities enabled
  filesystem_access: full
```

✅ **Good:**
```yaml
security:
  scoped_credentials:
    - h323_gatekeeper_api_key  # Only what's needed
  wasi_capabilities:
    - wasi:clocks/wall-clock   # Minimal capabilities
  filesystem_access: none      # No filesystem access
```

### Principle 2: Credential Scoping

**Each swarm should only access its own credentials.**

**Implementation:**

```python
class CredentialScoper:
    """Manage per-swarm credential isolation"""

    def __init__(self):
        self.swarm_credentials = {}  # swarm_id → {key: value}

    def set_credential(self, swarm_id: str, key: str, value: str):
        """Set a credential for a specific swarm"""
        if swarm_id not in self.swarm_credentials:
            self.swarm_credentials[swarm_id] = {}
        self.swarm_credentials[swarm_id][key] = value

    def get_credential(self, swarm_id: str, key: str) -> Optional[str]:
        """Get credential (only accessible to owning swarm)"""
        if swarm_id not in self.swarm_credentials:
            return None
        return self.swarm_credentials[swarm_id].get(key)

    def check_access(self, swarm_id: str, credential_key: str) -> bool:
        """Check if swarm is allowed to access credential"""
        contract = load_service_contract(f"config/chassis/{swarm_id}.yaml")
        return credential_key in contract.scoped_credentials
```

**Example:**

```python
# Guardian council can access H.323 credentials
scoper.set_credential('guardian-council', 'h323_gatekeeper_api_key', 'secret123')

# Guardian council CANNOT access SIP credentials
scoper.check_access('guardian-council', 'sip_twilio_api_key')  # Returns False
```

### Principle 3: No Filesystem Access

**WASM modules should NOT have direct filesystem access.**

- Use **WASI capabilities** for controlled access (stdin/stdout only)
- For file operations, use **IF.chassis proxy API**
- All file reads/writes go through host with audit logging

### Principle 4: Network Isolation

**WASM modules cannot make direct network calls.**

Instead, use IF.chassis **proxy API**:

```rust
// Inside WASM module
#[no_mangle]
pub extern "C" fn call_external_api(endpoint_ptr: *const c_char) -> *mut c_char {
    // WASM cannot directly call HTTP APIs
    // Instead, request IF.chassis host to make the call

    let endpoint = unsafe { CStr::from_ptr(endpoint_ptr).to_str().unwrap() };

    // Host function (imported via WASI)
    let result = host_http_get(endpoint);

    CString::new(result).unwrap().into_raw()
}

// Host provides this function
extern "C" {
    fn host_http_get(endpoint: *const c_char) -> *const c_char;
}
```

**Host implementation:**

```python
def host_http_get(swarm_id: str, endpoint: str) -> str:
    """Proxy HTTP GET request with audit logging"""

    # Check if swarm is allowed to call this endpoint
    if not is_endpoint_allowed(swarm_id, endpoint):
        witness_log(
            component='IF.chassis',
            operation='http_proxy_denied',
            swarm_id=swarm_id,
            endpoint=endpoint
        )
        return json.dumps({'error': 'Unauthorized'})

    # Make the HTTP request on behalf of swarm
    response = requests.get(endpoint)

    # Log to IF.witness
    witness_log(
        component='IF.chassis',
        operation='http_proxy',
        swarm_id=swarm_id,
        endpoint=endpoint,
        status_code=response.status_code
    )

    return response.text
```

### Principle 5: Audit Everything

**All security-sensitive operations must be logged to IF.witness.**

```python
from infrafabric.witness import log_operation

def execute_wasm_task(swarm_id: str, task: dict) -> dict:
    """Execute task with comprehensive audit logging"""

    # Log task execution start
    log_operation(
        component='IF.chassis',
        operation='task_start',
        params={
            'swarm_id': swarm_id,
            'task_id': task['task_id'],
            'task_type': task['task_type']
        }
    )

    # Execute task
    try:
        result = wasm_instance.call_exported_function('execute_task', task)

        # Log success
        log_operation(
            component='IF.chassis',
            operation='task_complete',
            params={
                'swarm_id': swarm_id,
                'task_id': task['task_id'],
                'status': 'success'
            }
        )

        return result

    except Exception as e:
        # Log failure
        log_operation(
            component='IF.chassis',
            operation='task_failed',
            params={
                'swarm_id': swarm_id,
                'task_id': task['task_id'],
                'error': str(e)
            }
        )
        raise
```

---

## Example Service Contracts

### Example 1: Guardian Council (High Security)

```yaml
swarm_id: guardian-council
wasm_module: wasm_modules/guardian_council.wasm

resource_limits:
  max_cpu_percent: 50       # Moderate CPU usage
  max_memory_mb: 512        # Sufficient for voting logic
  max_network_bandwidth_mbps: 10
  max_concurrent_tasks: 8   # Handle 8 simultaneous votes
  task_timeout_seconds: 30

slo_targets:
  response_time_p95_ms: 150   # Fast response for governance
  error_rate_percent: 0.5     # Very low error tolerance
  availability_percent: 99.9  # High availability required

security:
  scoped_credentials:
    - h323_gatekeeper_api_key
    - guardian_signing_key
    - mcu_admin_password

  wasi_capabilities:
    - wasi:io/streams          # For logging
    - wasi:clocks/wall-clock   # For timestamps
    - wasi:random/random       # For cryptographic operations

  filesystem_access: none
  network_access: proxy_only

reputation:
  initial_score: 0.98  # High initial reputation (production-proven)
  slo_weight: 0.7
  security_weight: 0.3
```

### Example 2: Experimental Research Swarm (Permissive)

```yaml
swarm_id: research-agent-001
wasm_module: wasm_modules/research_agent.wasm

resource_limits:
  max_cpu_percent: 20       # Limited CPU
  max_memory_mb: 256        # Limited memory
  max_network_bandwidth_mbps: 5
  max_concurrent_tasks: 2
  task_timeout_seconds: 60

slo_targets:
  response_time_p95_ms: 2000  # Allow slower processing
  error_rate_percent: 10.0    # High error tolerance
  availability_percent: 95.0  # Development environment

security:
  scoped_credentials:
    - research_api_key

  wasi_capabilities:
    - wasi:io/streams
    - wasi:clocks/wall-clock

  filesystem_access: none
  network_access: proxy_only

reputation:
  initial_score: 0.5   # Low initial reputation (untested)
  slo_weight: 0.6
  security_weight: 0.4
```

### Example 3: Third-Party Integration (Untrusted)

```yaml
swarm_id: third-party-analyzer
wasm_module: wasm_modules/third_party_analyzer.wasm

resource_limits:
  max_cpu_percent: 10       # Very limited CPU
  max_memory_mb: 128        # Minimal memory
  max_network_bandwidth_mbps: 1
  max_concurrent_tasks: 1   # One task at a time
  task_timeout_seconds: 30

slo_targets:
  response_time_p95_ms: 5000
  error_rate_percent: 20.0
  availability_percent: 90.0

security:
  scoped_credentials: []    # No credentials provided

  wasi_capabilities:
    - wasi:io/streams       # Minimal capabilities

  filesystem_access: none
  network_access: none      # Completely isolated

reputation:
  initial_score: 0.3   # Very low initial reputation (untrusted)
  slo_weight: 0.5
  security_weight: 0.5
```

---

## Integration Examples

### Full Example: Loading and Executing a WASM Swarm

**File: `examples/load_guardian_council.py`**

```python
#!/usr/bin/env python3
"""
Example: Load Guardian Council WASM module into IF.chassis

This demonstrates the complete workflow:
1. Load service contract
2. Initialize WASM runtime
3. Execute a task
4. Track SLO metrics
5. Update reputation
"""

import time
from pathlib import Path
from infrafabric.chassis.runtime import IFChassis, ServiceContract, load_service_contract
from infrafabric.chassis.slo import SLOMetrics
from infrafabric.chassis.reputation import ReputationScore
from infrafabric.witness import log_operation

def main():
    # Step 1: Load service contract
    print("Loading service contract...")
    contract = load_service_contract(Path("config/chassis/guardian-council.yaml"))
    print(f"  Swarm ID: {contract.swarm_id}")
    print(f"  WASM module: {contract.wasm_module}")
    print(f"  CPU limit: {contract.resource_limits.max_cpu_percent}%")
    print(f"  Memory limit: {contract.resource_limits.max_memory_mb} MB")

    # Step 2: Initialize IF.chassis
    print("\nInitializing IF.chassis...")
    chassis = IFChassis()
    chassis.load_swarm(contract)
    print("  ✅ WASM module loaded and validated")

    # Step 3: Initialize SLO tracking
    slo_metrics = SLOMetrics(swarm_id=contract.swarm_id)
    reputation = ReputationScore(
        swarm_id=contract.swarm_id,
        current_score=0.98,
        slo_compliance_score=1.0,
        security_compliance_score=1.0
    )

    # Step 4: Execute a task
    print("\nExecuting guardian vote task...")
    task = {
        'task_id': 'vote-001',
        'task_type': 'guardian_vote',
        'payload': {
            'session': 'session-4-sip',
            'proposal': 'Approve SIP integration Phase 3',
            'voting_period': 3600
        }
    }

    start_time = time.time()
    try:
        result = chassis.execute_task(contract.swarm_id, task)
        response_time_ms = (time.time() - start_time) * 1000

        print(f"  ✅ Task completed in {response_time_ms:.2f}ms")
        print(f"  Result: {result}")

        # Record success
        slo_metrics.record_task_response(response_time_ms, success=True)

    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        print(f"  ❌ Task failed: {e}")

        # Record failure
        slo_metrics.record_task_response(response_time_ms, success=False)

    # Step 5: Check SLO compliance
    print("\nChecking SLO compliance...")
    compliance = slo_metrics.check_slo_compliance(contract.slo_targets)

    for metric, details in compliance.items():
        status = "✅" if details['compliant'] else "❌"
        print(f"  {status} {metric}: {details['actual']:.2f} (target: {details['target']})")

    # Step 6: Update reputation
    reputation.update_from_slo_metrics(compliance)
    print(f"\nReputation score: {reputation.current_score:.2f}")
    print(f"  SLO compliance: {reputation.slo_compliance_score:.2f}")
    print(f"  Security compliance: {reputation.security_compliance_score:.2f}")

    # Step 7: Log to IF.witness
    log_operation(
        component='IF.chassis',
        operation='example_complete',
        params={
            'swarm_id': contract.swarm_id,
            'tasks_executed': 1,
            'reputation_score': reputation.current_score
        }
    )

    print("\n✅ Example complete!")

if __name__ == '__main__':
    main()
```

**Run:**
```bash
python3 examples/load_guardian_council.py
```

**Expected Output:**
```
Loading service contract...
  Swarm ID: guardian-council
  WASM module: wasm_modules/guardian_council.wasm
  CPU limit: 50%
  Memory limit: 512 MB

Initializing IF.chassis...
  ✅ WASM module loaded and validated

Executing guardian vote task...
  ✅ Task completed in 87.32ms
  Result: {'vote': 'approve', 'guardian_id': 'guardian-3', 'signature': 'ed25519:...'}

Checking SLO compliance...
  ✅ response_time: 87.32 (target: 150)
  ✅ error_rate: 0.00 (target: 0.5)
  ✅ availability: 100.00 (target: 99.9)

Reputation score: 0.98
  SLO compliance: 1.00
  Security compliance: 1.00

✅ Example complete!
```

---

## Troubleshooting

### Issue: WASM module fails to load

**Symptoms:**
- Error: `wasmtime validation failed`
- Error: `Invalid WASM magic number`

**Diagnosis:**
```bash
# Validate WASM module
wasmtime validate wasm_modules/your_module.wasm

# Check WASM module info
wasm-objdump -h wasm_modules/your_module.wasm
```

**Solutions:**
1. **Wrong compilation target**: Ensure compiled for `wasm32-wasi`
   ```bash
   rustc --target wasm32-wasi --crate-type cdylib src/lib.rs
   ```

2. **Corrupted WASM file**: Recompile from source

3. **Missing exports**: Verify exported functions
   ```bash
   wasm-objdump -x wasm_modules/your_module.wasm | grep export
   ```

### Issue: Resource limit exceeded

**Symptoms:**
- Log: `resource_limit_exceeded` in IF.witness
- Swarm terminated unexpectedly

**Diagnosis:**
```python
# Check resource usage
chassis.get_resource_usage('your-swarm-id')
# Returns: {'cpu_percent': 75, 'memory_mb': 600, 'network_mbps': 15}
```

**Solutions:**
1. **Increase limits** (if justified):
   ```yaml
   resource_limits:
     max_cpu_percent: 75  # Increased from 50
     max_memory_mb: 1024  # Increased from 512
   ```

2. **Optimize WASM code**: Reduce computational complexity

3. **Batch processing**: Process multiple items per task invocation

### Issue: Credential access denied

**Symptoms:**
- Log: `credential_access_denied` in IF.witness
- Swarm cannot access required API keys

**Diagnosis:**
```bash
# Check credential scoping
grep "credential_access" logs/chassis/*.jsonl | jq '.credential_key'
```

**Solutions:**
1. **Add credential to service contract**:
   ```yaml
   security:
     scoped_credentials:
       - missing_credential_key  # Add this
   ```

2. **Check credential exists**:
   ```python
   scoper.get_credential('your-swarm-id', 'credential_key')
   ```

### Issue: SLO violations causing reputation drop

**Symptoms:**
- Reputation score decreasing over time
- Swarm no longer selected by IF.governor

**Diagnosis:**
```python
# Check SLO metrics
metrics = chassis.get_slo_metrics('your-swarm-id')
print(f"p95 response time: {metrics.calculate_p95_response_time()}ms")
print(f"Error rate: {metrics.calculate_error_rate()}%")
print(f"Availability: {metrics.calculate_availability()}%")
```

**Solutions:**
1. **Optimize performance**: Reduce task execution time

2. **Adjust SLO targets** (if too aggressive):
   ```yaml
   slo_targets:
     response_time_p95_ms: 500  # Relaxed from 150
   ```

3. **Fix errors**: Investigate and fix root cause of task failures

4. **Check availability**: Ensure swarm not crashing/restarting

---

## References

### External Resources

1. **wasmtime Documentation**: https://docs.wasmtime.dev/
2. **WASI Specification**: https://github.com/WebAssembly/WASI
3. **Rust WASM Book**: https://rustwasm.github.io/docs/book/
4. **Linux cgroups v2**: https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html
5. **SLO Best Practices**: https://sre.google/workbook/implementing-slos/

### InfraFabric Components

- **IF.coordinator**: Real-time task distribution (etcd/NATS)
- **IF.governor**: Capability matching and budget tracking
- **IF.witness**: Audit logging with SHA-256 hashing
- **IF.optimise**: Cost tracking and optimization

### Related Documentation

- `docs/H323-PRODUCTION-RUNBOOK.md` - IF.chassis integration for H.323 Guardian Council
- `docs/components/IF.COORDINATOR.md` - Coordination service (when available)
- `docs/components/IF.GOVERNOR.md` - Resource management (when available)
- `PHASE-0-TASK-BOARD.md` - Phase 0 implementation roadmap

---

**Document Version**: 1.0
**Author**: Session 3 (H.323 Guardian Council)
**License**: MIT (InfraFabric Project)
**Last Updated**: 2025-11-12
