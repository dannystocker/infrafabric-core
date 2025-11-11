# InfraFabric Rust Implementation - Quick Start

This guide shows you how to build and run the InfraFabric Rust components (IF.chassis + if-cli).

## 📋 Prerequisites

- **Rust** 1.70+ (install via [rustup](https://rustup.rs/))
- **Git** (for cloning/pushing)

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Verify installation
rustc --version
cargo --version
```

## 🏗️ Project Structure

```text
infrafabric/
├── Cargo.toml               # Workspace configuration
├── src/
│   ├── chassis/             # IF.chassis (90% infrastructure)
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── lib.rs       # Core chassis implementation
│   └── cli/                 # if-cli (Philosophy-grounded CLI)
│       ├── Cargo.toml
│       └── src/
│           └── main.rs      # CLI implementation
```

## 🚀 Build Instructions

### 1. Build Everything

From the project root:

```bash
cd /home/user/infrafabric

# Build all workspace members (chassis + CLI)
cargo build --release
```

This will:
- Download dependencies (~100MB first time)
- Compile `infrafabric-chassis` library
- Compile `if` CLI binary
- Place binary at `target/release/if`

Expected output:
```
   Compiling infrafabric-chassis v0.1.0
   Compiling if-cli v0.1.0
    Finished release [optimized] target(s) in 2m 15s
```

### 2. Install CLI Globally (Optional)

```bash
# Install 'if' command globally
cargo install --path src/cli

# Verify installation
if --help
```

## 🧪 Run Tests

```bash
# Run all tests
cargo test

# Run chassis tests only
cargo test -p infrafabric-chassis

# Run with verbose output
cargo test -- --nocapture
```

Expected test output:
```
running 3 tests
test tests::test_message_signing ... ok
test tests::test_policy_enforcement ... ok
test tests::test_witness_chain_integrity ... ok

test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured
```

## 📖 CLI Usage Examples

### Basic Message Sending

```bash
# Send message with justification (--why required)
./target/release/if message send \
  --claim "Deploy v2 to production" \
  --to if://swarm/deployment \
  --why "Security patches approved by team"

# With distributed tracing
./target/release/if message send \
  --claim "Process refund request" \
  --to if://swarm/finance \
  --trace \
  --why "Customer ticket #12345"
```

### Popperian Falsification Mode

```bash
# Run pre-mortem analysis before deployment
./target/release/if deploy app-v2 \
  --mode falsify \
  --why "Quarterly release Q4"

# Output:
# 🔍 Running pre-mortem analysis for: app-v2
#
# ⚠️  Failure Mode 1: Cross-swarm conflict (likelihood: 70%)
#     Prediction: Finance swarm may disagree on cost estimate
#     Mitigation: Add explicit conflict resolution step
# ...
```

### Policy Enforcement (IF.guard)

```bash
# Check if action is allowed
./target/release/if guard check delete production-db

# Output:
# 🛡️  Checking policy: delete on production-db
# ❌ DENY - Cannot delete production resources without approval

# Approve a proposal
./target/release/if guard approve prop-789 \
  --why "Legal team reviewed settlement terms"
```

### Witness Audit Log (IF.witness)

```bash
# Show recent audit events
./target/release/if witness show --last 10

# Output (table format):
# 📜 Witness Log (10 events)
#
# Time     | Event          | Agent                | Hash (first 8)
# --------------------------------------------------------------
# 14:23:15 | message_sent   | if://agent/cli-user  | a2f9c3b8
# 14:23:16 | message_sent   | if://agent/cli-user  | d1e5f6g7
# ...

# Verify chain integrity
./target/release/if witness verify

# Output:
# 🔐 Verifying witness chain integrity...
# ✅ Witness chain is valid (all hashes verified)
```

### Consensus Voting (Ubuntu Model)

```bash
# Propose a decision
./target/release/if consensus propose \
  "Upgrade database schema to v3" \
  --period 24

# Output:
# 📋 Proposal created
#    ID: prop-a2f9c3b8
#    Description: Upgrade database schema to v3
#    Voting period: 24 hours

# Vote on proposal
./target/release/if consensus vote prop-a2f9c3b8 \
  --decision approve \
  --why "Schema changes reviewed and tested"

# List active proposals
./target/release/if consensus list
```

### Distributed Tracing

```bash
# Show trace details
./target/release/if trace show trace-a2f9c3b8d1e5

# Output:
# 🔍 Trace: trace-a2f9c3b8d1e5
#
# Call Graph:
# ├─ IF.swarm.legal [14:00:01 - 14:02:15] (2m 14s)
# │  ├─ talent-legalbert-001 → Claim: "Settlement analysis"
# ├─ IF.swarm.finance [14:00:03 - 14:02:30] (2m 27s)
# │  ├─ talent-finbert-003 → Claim: "Cost projection"
# └─ IF.relation_agent [14:02:31 - 14:02:45] (14s)
```

## 🧩 Using IF.chassis as a Library

If you're building a new agent/capability, import the chassis library:

```rust
// In your Cargo.toml
[dependencies]
infrafabric-chassis = { path = "../../chassis" }

// In your code
use infrafabric_chassis::{Chassis, IFMessage};

fn main() -> anyhow::Result<()> {
    // Create chassis
    let chassis = Chassis::new("if://agent/my-agent".to_string());

    // Send message
    let msg = IFMessage {
        performative: "inform".to_string(),
        sender: String::new(),
        receiver: vec!["if://swarm/test".to_string()],
        content: serde_json::json!({"claim": "Test message"}),
        timestamp: String::new(),
        sequence_num: 0,
        trace_id: "trace-123".to_string(),
        hazard: None,
        citation_ids: None,
        nonce: None,
        ttl: Some(3600),
        signature: None,
    };

    chassis.send_message(msg)?;

    // Verify witness chain
    assert!(chassis.verify_witness_chain()?);

    Ok(())
}
```

## 🔧 Development Workflow

### 1. Make Changes

```bash
# Edit chassis code
vim src/chassis/src/lib.rs

# Edit CLI code
vim src/cli/src/main.rs
```

### 2. Check for Errors

```bash
# Fast compile-check (no binary generation)
cargo check

# Check with linting
cargo clippy

# Format code
cargo fmt
```

### 3. Run Tests

```bash
# Run tests after changes
cargo test

# Run specific test
cargo test test_witness_chain_integrity
```

### 4. Build and Test CLI

```bash
# Build in debug mode (faster, for testing)
cargo build

# Run debug binary
./target/debug/if --help

# Build optimized binary
cargo build --release
./target/release/if --help
```

## 📚 Key Components

### IF.chassis Features

- ✅ **Ed25519 Signatures** - All messages cryptographically signed
- ✅ **IF.witness Integration** - Immutable audit log with hash chaining
- ✅ **IF.guard Integration** - Policy enforcement (allow/deny/escalate)
- ✅ **Replay Protection** - Nonce-based deduplication
- ✅ **TTL Enforcement** - Message expiration
- ✅ **WASM Runtime** - Wasmtime integration (hot-swap ready)

### if-cli Features

- ✅ **`--why` Flag** - Justification required (verificationism)
- ✅ **`--trace` Flag** - Distributed tracing with trace tokens
- ✅ **`--mode=falsify`** - Popperian pre-mortem analysis
- ✅ **Consensus Commands** - Ubuntu-style voting
- ✅ **Guard Integration** - Policy checking and approvals
- ✅ **Witness Queries** - Audit log inspection and verification

## 🐛 Troubleshooting

### Build Errors

**Error:** `could not find crate for 'hex'`

**Fix:** Run `cargo update` to refresh dependencies.

**Error:** `linker 'cc' not found`

**Fix:** Install build essentials:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS
xcode-select --install
```

### Runtime Errors

**Error:** `SignatureError: Unknown sender`

**Fix:** Register trusted public keys before verifying messages:
```rust
let chassis1 = Chassis::new("if://agent/sender".to_string());
let chassis2 = Chassis::new("if://agent/receiver".to_string());

// Register sender's public key with receiver
chassis2.register_trusted_key(
    "if://agent/sender".to_string(),
    chassis1.public_key()
);
```

## 🎯 Next Steps

1. **Build POC Demo** - Follow `docs/IMPLEMENTATION-ROADMAP-TALENT-CLI.md` Week 1-2
2. **Integrate IF.witness Storage** - Replace in-memory chain with PostgreSQL/SQLite
3. **Add NATS Transport** - Replace `println!` with actual pub/sub
4. **Implement IF.scout** - Start building talent discovery (Week 5-6)
5. **Deploy WebRTC Gateway** - Enable real-time communication

## 📖 Further Reading

- **Architecture Overview**: `docs/IMPLEMENTATION-ROADMAP-TALENT-CLI.md`
- **Communication Layer**: `docs/IMPLEMENTATION-GUIDE-COMMUNICATION.md`
- **Business Strategy**: `docs/AUDIT-RESPONSE-ACTION-PLAN.md`
- **Comprehensive Audit**: `docs/AUDIT-COMPREHENSIVE-EXTRACTION.md`

## 🤝 Contributing

This implementation is based on:
- **GPT-5 Pro** - Architecture design (Genesis mapping)
- **Claude Sonnet 4.5** - Rust implementation
- **Gemini Audit** - 121 topic extraction

All code follows InfraFabric principles:
- **Verificationism** - Every claim requires evidence (`--why`)
- **Falsifiability** - Pre-mortem analysis (`--mode=falsify`)
- **Provenance** - Immutable audit trails (IF.witness)
- **Consensus** - Ubuntu-style agreement (consensus commands)

---

**Built with InfraFabric v0.1.0** | [Report Issues](https://github.com/dannystocker/infrafabric/issues)
