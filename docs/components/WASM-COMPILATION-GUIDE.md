# WASM Compilation Guide for IF.chassis

**Component**: IF.chassis
**Purpose**: Compile swarm code to WASM for sandboxed execution
**Status**: Phase 0 (P0.3.1)
**Author**: Session 3 (H.323 Guardian Council)
**Last Updated**: 2025-11-12

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Compiling Rust to WASM](#compiling-rust-to-wasm)
4. [Compiling Python to WASM](#compiling-python-to-wasm)
5. [Compiling JavaScript/TypeScript to WASM](#compiling-javascripttypescript-to-wasm)
6. [Loading WASM into IF.chassis](#loading-wasm-into-ifchassis)
7. [Service Contract Specification](#service-contract-specification)
8. [Sandbox Limitations](#sandbox-limitations)
9. [Troubleshooting](#troubleshooting)
10. [Examples](#examples)

---

## Overview

IF.chassis uses WebAssembly (WASM) to provide secure, isolated execution environments for swarms. WASM offers:

- **Sandboxing**: No filesystem, network, or process execution access
- **Portability**: Run anywhere wasmtime is available
- **Performance**: Near-native execution speed
- **Safety**: Memory-safe by design

### Why WASM?

**Before WASM (Security Risks)**:
- Direct Python/JavaScript execution with full system access
- Malicious code could read files, create network connections, spawn processes
- One compromised swarm could affect entire system

**After WASM (Sandboxed)**:
- Code executes in isolated WASM sandbox
- NO filesystem access (cannot read/write files)
- NO network access (cannot create sockets)
- NO process execution (cannot run shell commands)
- Only controlled APIs via IF.bus (future)

---

## Prerequisites

### Required Tools

```bash
# Install wasmtime (WASM runtime)
pip install wasmtime

# Install Rust compiler (for Rust → WASM)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add wasm32-wasi

# Install wasm-pack (for Rust → WASM with npm)
cargo install wasm-pack

# Install Emscripten (for C/C++ → WASM)
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install latest
./emsdk activate latest

# Install Python WASM toolchain (experimental)
pip install pyodide-build
```

---

## Compiling Rust to WASM

### 1. Create Rust Project

```bash
cargo new --lib swarm-analyzer
cd swarm-analyzer
```

### 2. Configure Cargo.toml

```toml
[package]
name = "swarm-analyzer"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
# No dependencies needed for basic WASM
```

### 3. Write Rust Code (src/lib.rs)

```rust
// src/lib.rs

// Export functions that will be called from IF.chassis
#[no_mangle]
pub extern "C" fn analyze_code(file_ptr: *const u8, file_len: usize) -> i32 {
    // This function is exported and can be called from WASM host

    // Read file content from WASM memory
    let file_bytes = unsafe {
        std::slice::from_raw_parts(file_ptr, file_len)
    };

    let file_content = std::str::from_utf8(file_bytes).unwrap();

    // Perform analysis (example: count lines)
    let line_count = file_content.lines().count();

    // Return result (simplified - real implementation would serialize to memory)
    line_count as i32
}

#[no_mangle]
pub extern "C" fn initialize() -> i32 {
    // Initialization function called when swarm loads
    // Return 0 for success, non-zero for error
    0
}
```

### 4. Compile to WASM

```bash
# Compile with wasm32-wasi target (WASI = WebAssembly System Interface)
cargo build --target wasm32-wasi --release

# Output: target/wasm32-wasi/release/swarm_analyzer.wasm
```

### 5. Optimize WASM (Optional)

```bash
# Install wasm-opt (part of binaryen toolchain)
apt-get install binaryen

# Optimize WASM file (reduces size, improves performance)
wasm-opt -Os target/wasm32-wasi/release/swarm_analyzer.wasm \
    -o swarm_analyzer_optimized.wasm
```

---

## Compiling Python to WASM

### Note: Python → WASM is experimental

Python to WASM is supported via **Pyodide** (CPython compiled to WASM) or **RustPython** (Python interpreter in Rust compiled to WASM).

### Using Pyodide

```bash
# Install pyodide-build
pip install pyodide-build

# Create Python swarm
# swarm.py
def analyze_code(file_content: str) -> dict:
    """Analyze Python code"""
    lines = file_content.split('\n')
    return {
        'line_count': len(lines),
        'blank_lines': sum(1 for line in lines if not line.strip()),
        'comment_lines': sum(1 for line in lines if line.strip().startswith('#'))
    }

# Compile to WASM (via pyodide-build)
# This creates a WASM module that can run Python code
```

### Alternative: Write Rust Wrapper

For production, write Rust wrappers that call Python via PyO3, then compile to WASM:

```rust
// Use PyO3 to embed Python in Rust, compile to WASM
use pyo3::prelude::*;

#[no_mangle]
pub extern "C" fn run_python_analyzer() {
    Python::with_gil(|py| {
        let code = "print('Analyzing code...')";
        py.run(code, None, None).unwrap();
    });
}
```

---

## Compiling JavaScript/TypeScript to WASM

### Using AssemblyScript

AssemblyScript is a TypeScript-like language that compiles directly to WASM.

```bash
# Install AssemblyScript
npm install -g assemblyscript

# Create project
npm init
asc --init

# Write AssemblyScript code (assembly/index.ts)
export function analyzeCode(fileLength: i32): i32 {
  // Analyze code (simplified example)
  return fileLength;
}

# Compile to WASM
npm run asbuild
```

Output: `build/optimized.wasm`

---

## Loading WASM into IF.chassis

### Python Example

```python
from infrafabric.chassis import IFChassis, ServiceContract

# Create chassis instance
chassis = IFChassis()

# Read compiled WASM module
with open('swarm_analyzer.wasm', 'rb') as f:
    wasm_bytes = f.read()

# Define service contract
contract = ServiceContract(
    swarm_id='analyzer-swarm',
    capabilities=[
        'code-analysis:python',
        'code-analysis:rust',
        'code-analysis:javascript'
    ],
    resource_limits={
        'max_memory_mb': 256,  # 256 MB memory limit
        'max_cpu_percent': 25,  # 25% CPU limit
        'max_api_calls_per_second': 10,
        'max_execution_time_seconds': 300  # 5 minutes max
    },
    slos={
        'target_latency_ms': 100,  # 100ms target
        'target_throughput_rps': 10  # 10 requests/sec
    },
    version='1.0',
    metadata={
        'author': 'session-3-h323',
        'language': 'rust',
        'description': 'Code analysis swarm'
    }
)

# Load swarm into chassis
chassis.load_swarm('analyzer-swarm', wasm_bytes, contract)

# Execute task (P0.3.2 will implement full task execution)
result = chassis.execute_task(
    swarm_id='analyzer-swarm',
    task_name='analyze_code',
    task_params={
        'file': 'example.py',
        'checks': ['style', 'security', 'complexity']
    }
)

print(result['status'])  # 'success'
print(result['execution_time_seconds'])  # 0.15
```

---

## Service Contract Specification

### Contract Structure

```python
@dataclass
class ServiceContract:
    swarm_id: str  # Unique identifier
    capabilities: List[str]  # What the swarm can do
    resource_limits: Dict[str, Any]  # Hard resource limits
    slos: Dict[str, float]  # Service Level Objectives
    version: str  # Contract version
    created_at: float  # Timestamp
    metadata: Dict[str, Any]  # Additional info
```

### Capability Types

From `infrafabric/schemas/capability.py`:

```python
# Code Analysis
'code-analysis:python'
'code-analysis:rust'
'code-analysis:javascript'
'code-analysis:go'
'code-analysis:typescript'

# Integrations
'integration:sip'
'integration:ndi'
'integration:webrtc'
'integration:h323'
'integration:vmix'
'integration:obs'

# Documentation
'docs:technical-writing'
'docs:api-design'
'docs:tutorials'

# Testing
'testing:unit'
'testing:integration'
'testing:performance'
```

### Resource Limits

```python
resource_limits = {
    'max_memory_mb': 256,  # Maximum memory (default: 256 MB)
    'max_cpu_percent': 25,  # CPU limit (default: 25%)
    'max_api_calls_per_second': 10,  # Rate limit (default: 10/sec)
    'max_execution_time_seconds': 300  # Timeout (default: 5 min)
}
```

### SLOs (Service Level Objectives)

```python
slos = {
    'target_latency_ms': 100,  # Target latency (default: 100ms)
    'target_throughput_rps': 10,  # Target throughput (default: 10 req/sec)
    'target_availability_percent': 99.9  # Target uptime (default: 99.9%)
}
```

---

## Sandbox Limitations

### What WASM CAN Do

✅ **Memory Operations**: Read/write within allocated WASM linear memory
✅ **Computation**: Arbitrary calculations (sorting, parsing, analysis)
✅ **Function Calls**: Call other WASM functions
✅ **Scoped Logging**: Log messages via `env.log` host function
✅ **Return Values**: Return results to host (IF.chassis)

### What WASM CANNOT Do

❌ **Filesystem**: Cannot read/write files (no open, read, write syscalls)
❌ **Network**: Cannot create sockets (no network syscalls)
❌ **Process Execution**: Cannot spawn processes (no fork, exec)
❌ **System Calls**: Cannot make arbitrary syscalls
❌ **Dynamic Loading**: Cannot load external libraries at runtime

### Scoped Host Functions

IF.chassis exposes minimal, controlled host functions:

```python
# ONLY exposed function to WASM:
linker.define_func("env", "log", log_func_type, scoped_log_wrapper)
# Allows WASM to log messages with swarm ID prefix
```

No filesystem, network, or exec functions are exposed.

---

## Troubleshooting

### Error: "WASM compilation failed"

**Cause**: Invalid WASM bytecode

**Solution**:
- Verify WASM file is valid: `wasm-validate swarm.wasm`
- Check compilation command succeeded
- Ensure correct target (`wasm32-wasi` for Rust)

### Error: "Task not exported by swarm"

**Cause**: WASM module doesn't export requested function

**Solution**:
- Verify function is marked with `#[no_mangle]` and `pub extern "C"` (Rust)
- Check exports: `wasm-objdump -x swarm.wasm -j Export`
- Ensure function name matches task name

### Error: "Swarm already loaded"

**Cause**: Attempting to load swarm that is already loaded

**Solution**:
- Unload existing swarm first: `chassis.unload_swarm(swarm_id)`
- Use different swarm_id

### Memory Limit Exceeded

**Cause**: Swarm exceeded `max_memory_mb` limit

**Solution**:
- Increase limit in service contract
- Optimize WASM code to use less memory
- Process data in chunks

---

## Examples

### Example 1: Simple Code Counter

```rust
// src/lib.rs

#[no_mangle]
pub extern "C" fn count_lines(ptr: *const u8, len: usize) -> i32 {
    let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
    let text = std::str::from_utf8(bytes).unwrap();
    text.lines().count() as i32
}
```

**Compile**:
```bash
cargo build --target wasm32-wasi --release
```

**Load**:
```python
chassis.load_swarm('counter', wasm_bytes, contract)
```

### Example 2: JSON Parser

```rust
use serde_json::Value;

#[no_mangle]
pub extern "C" fn parse_json(ptr: *const u8, len: usize) -> i32 {
    let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
    let text = std::str::from_utf8(bytes).unwrap();

    match serde_json::from_str::<Value>(text) {
        Ok(_) => 1,  // Valid JSON
        Err(_) => 0  // Invalid JSON
    }
}
```

### Example 3: Security Analyzer

```rust
#[no_mangle]
pub extern "C" fn check_security(ptr: *const u8, len: usize) -> i32 {
    let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
    let code = std::str::from_utf8(bytes).unwrap();

    let mut issues = 0;

    // Check for SQL injection patterns
    if code.contains("SELECT") && code.contains("WHERE") {
        if !code.contains("?") && !code.contains("$") {
            issues += 1;  // Potential SQL injection
        }
    }

    // Check for hardcoded secrets
    if code.contains("password") || code.contains("secret") {
        issues += 1;
    }

    issues
}
```

---

## References

**WASM Standards**:
- WebAssembly Core Specification: https://webassembly.github.io/spec/
- WASI (WebAssembly System Interface): https://wasi.dev/

**Toolchains**:
- Rust → WASM: https://rustwasm.github.io/
- wasmtime (Rust runtime): https://wasmtime.dev/
- wasm-pack: https://rustwasm.github.io/wasm-pack/
- AssemblyScript (TypeScript → WASM): https://www.assemblyscript.org/

**InfraFabric Documents**:
- IF.chassis architecture: `docs/components/IF.CHASSIS.md`
- Capability registry: `infrafabric/schemas/capability.py`
- Resource limits: P0.3.2 documentation (upcoming)

---

**Next Steps**:
- P0.3.2: Resource limit enforcement (CPU, memory, API rate limiting)
- P0.3.3: Scoped credentials (temporary, task-scoped API keys)
- P0.3.4: SLO tracking (latency, throughput, availability monitoring)

---

**Author**: Session 3 (H.323 Guardian Council)
**License**: CC BY 4.0
**Contact**: InfraFabric Project
**Last Updated**: 2025-11-12
