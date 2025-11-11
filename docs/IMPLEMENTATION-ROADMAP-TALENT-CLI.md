# InfraFabric Implementation Roadmap: Talent Agency + CLI

**Status:** READY TO BUILD
**Sources:**
- Gemini 2.5 Pro comprehensive audit (121 topics)
- GPT-5 Pro Genesis architecture (13 sections)
- Combined synthesis with prioritized implementation plan

**Timeline:** 12 weeks to production-ready "AI Talent Agency"

---

## Executive Summary

This document integrates **two major architectural visions** into a single, actionable roadmap:

1. **Gemini's Comprehensive Audit** (121 topics) → Identified gaps, opportunities, full ecosystem
2. **GPT-5's Genesis Architecture** (13 core sections) → Practical talent agency + CLI implementation

**The Big Idea:** InfraFabric as an **"AI Talent Agency"** with a philosophy-driven CLI

**Key Innovation:** Reduce AI capability integration from **2-4 weeks → 10 hours** (80% automated)

---

## Core Architecture (The 90/10 Split)

### IF.chassis (90% - Stable Infrastructure)

**What It Is:**
The unchanging foundation that every capability runs on:
- Networking (WebRTC, SIP, HTTP)
- Authentication (Ed25519 signatures, IF.guard integration)
- Logging (IF.witness append-only audit)
- Policy enforcement (IF.guard admission control)
- Message routing (IF.bus pub/sub)

**Why 90%:**
Most capabilities need the same plumbing. Build it once, verified, hardened.

**Implementation:**
```rust
// IF.chassis host API (in Rust for performance + safety)
pub trait ChassisHost {
    fn send_message(&self, msg: IFMessage) -> Result<()>;
    fn verify_signature(&self, msg: &IFMessage) -> bool;
    fn log_event(&self, event: WitnessEvent);
    fn check_policy(&self, action: &str, agent: &str) -> GuardDecision;
}
```

### logic.wasm (10% - Swappable Business Logic)

**What It Is:**
The actual capability code, compiled to WASM:
- Legal analysis (LegalBERT wrapper)
- Finance analysis (FinBERT wrapper)
- Market analysis (custom model)

**Why 10%:**
Only the unique business logic changes between capabilities.

**Implementation:**
```rust
// Capability WASM interface (WebAssembly)
#[wasm_bindgen]
pub fn analyze(input: &str) -> String {
    // Business logic here
    // Calls Chassis via host API
    let result = do_analysis(input);
    json!({"claim": result, "confidence": 0.85}).to_string()
}
```

**Hot-Swap:**
```bash
$ if-cli capability update legal-bert --version=2.1.0

Downloading: legal-bert-2.1.0.wasm [████████] 100%
Verifying signature... ✓
Running pre-flight checks... ✓
Hot-swapping 5 instances... ✓
Rollback available for 24h

Updated: legal-bert@2.1.0 (0 downtime)
```

---

## The Talent Agency Model (Detailed)

### Roles Mapping

| Role | IF Component | Function | Human Analogy |
|------|--------------|----------|---------------|
| **Scout** | `if.talent.scout` | Discover capabilities (GitHub, Hugging Face) | Talent scout finding new actors |
| **Developer** | `if.talent.developer` | Generate adapters, write glue code | Acting coach developing skills |
| **Coach** | `if.talent.coach` | Train/fine-tune models | Voice coach refining performance |
| **Packager** | `if.foundry` | Compile to WASM, sign, verify | Studio packaging final product |
| **Manager** | `if.talent.manager` | Track performance, suggest improvements | Talent manager guiding career |
| **Agent** | `if.talent.agent` | Negotiate capabilities (what can talent do?) | Agent negotiating roles |
| **Caster** | `if.talent.caster` | Select talent for projects | Casting director choosing actors |
| **Booker** | `if.talent.booker` | Deploy to projects, load balance | Booking agent scheduling gigs |
| **Business Affairs** | `if.guard` | Approve/reject deployments | Legal team approving contracts |
| **Publicist** | `if.witness` | Audit trail, public record | PR team managing public image |
| **Security** | `if.armour`, `if.vigil` | Monitor, detect threats | Security team protecting talent |

### The Complete Lifecycle (Step-by-Step)

#### Phase 1: Discovery (IF.scout)

```bash
$ if-cli scout search "legal document analysis"

Searching GitHub, Hugging Face, ArXiv...

Found 12 candidates:
1. LegalBERT (Hugging Face) - 94% accuracy, MIT license
2. DocFormer (GitHub) - 89% accuracy, Apache 2.0
3. LayoutLM (Microsoft) - 92% accuracy, MIT license
...

Recommend: LegalBERT (best accuracy, active maintenance)

$ if-cli scout nominate LegalBERT --priority=high

Nomination created: nom-789
Assigned to: if.talent.developer
```

**How IF.scout Works:**
1. Search APIs (GitHub GraphQL, Hugging Face Hub)
2. Filter by: license, stars, recent commits, documentation quality
3. Rank by: performance benchmarks, maintenance activity
4. Nominate top candidates for developer review

#### Phase 2: Ingestion (IF.prospector)

```bash
$ if-cli prospector ingest nom-789

Downloading LegalBERT...
- Model weights: 440MB [████████] 100%
- Config files: 12KB [████████] 100%
- README, LICENSE: 8KB [████████] 100%

Quarantine ID: quar-123
Status: QUARANTINED (isolated environment)

Running static analysis:
✓ License check: MIT (approved)
✓ Code scanning: No malicious patterns
✓ Dependency audit: 23 deps, 0 high-risk
✓ Model inspection: PyTorch, 110M params

Quarantine report: /tmp/quar-123-report.json
```

**Quarantine Environment:**
- No network access
- No file system write (except /tmp)
- Resource limits (4GB RAM, 2 CPUs)
- All actions logged to IF.witness

#### Phase 3: Adaptation (IF.adapter_agent)

```bash
$ if-cli adapter generate quar-123 --target=IFMessage

Analyzing model interface...
- Input: List[str] (documents)
- Output: Dict[str, Any] (predictions)
- Framework: PyTorch + Transformers

Generating adapter code...

[AUTO-GENERATED CODE]
# adapter_legalbert_001.py

from transformers import AutoModel, AutoTokenizer
from if_chassis import ChassisHost, IFMessage, Hazard, HazardType

class LegalBERTAdapter:
    def __init__(self, chassis: ChassisHost):
        self.chassis = chassis
        self.model = AutoModel.from_pretrained("legalbert")
        self.tokenizer = AutoTokenizer.from_pretrained("legalbert")

    def analyze(self, documents: List[str]) -> IFMessage:
        # Run model
        inputs = self.tokenizer(documents, return_tensors="pt")
        outputs = self.model(**inputs)

        # Extract predictions
        prediction = extract_prediction(outputs)
        confidence = calculate_confidence(outputs)

        # Detect hazards (IF.veritas integration)
        hazard = None
        if "liability" in prediction and confidence < 0.7:
            hazard = Hazard(
                type=HazardType.LEGAL,
                severity="high",
                rationale="Low confidence on liability claim"
            )

        # Return IFMessage
        return IFMessage(
            performative="inform",
            sender="if://talent/legalbert-001",
            content={"claim": prediction, "confidence": confidence},
            hazard=hazard,
            citation_ids=self.extract_citations(documents)
        )

Adapter generated: adapter-legalbert-001
Language: Python → WASM (via py2wasm)
Size: 2.3MB (compiled)

$ if-cli adapter compile adapter-legalbert-001

Compiling to WASM...
- Bundling dependencies...
- Optimizing for size...
- Adding WASI syscalls...

Output: adapter-legalbert-001.wasm (1.8MB)
```

**Adapter Requirements:**
- ✅ Converts model I/O to IFMessage format
- ✅ Adds hazard detection (legal, safety, conflict)
- ✅ Calibrates confidence scores (avoid over-confidence)
- ✅ Signs all outputs (Ed25519)
- ✅ Logs to IF.witness

#### Phase 4: Verification (IF.sandbox + IF.deception)

```bash
$ if-cli sandbox test adapter-legalbert-001 --duration=7d

Creating sandbox environment...
- Isolated network (no external calls)
- IF.deception honeypots enabled
- Test dataset: 1,000 legal documents

Running tests (7 days, continuous)...

Day 1: [████████████████████] 100% (142 docs tested)
  Accuracy: 94%
  False positives: 3%
  Latency: 120ms avg
  Hazards detected: 12 (all valid)

Day 2-6: [Background testing...]

Day 7: Final report
  Total docs: 1,000
  Accuracy: 94.2% (✓ meets 90% threshold)
  False positive rate: 2.8% (✓ below 5% threshold)
  Latency p50: 115ms, p99: 340ms (✓ acceptable)
  Security: 0 malicious behaviors (✓)
  Honeypot interactions: 0 (✓ didn't bite bait)

Status: PASS
Recommendation: CERTIFY for production
```

**IF.deception Honeypots:**
- Fake PII in test documents (does adapter leak it?)
- Fake credentials (does adapter try to exfiltrate?)
- Fake vulnerabilities (does adapter exploit them?)

#### Phase 5: Certification (IF.talent)

```bash
$ if-cli talent certify adapter-legalbert-001 --role=legal-analysis

Certification review:
- Sandbox tests: PASS (94.2% accuracy)
- Security audit: PASS (0 vulnerabilities)
- Performance: PASS (115ms p50)
- License: MIT (approved)
- Documentation: PASS (README complete)

Awaiting IF.guard approval...

[IF.guard Council Vote]
Guardian 1 (Popper): APPROVE - "Falsifiable claims, good evidence"
Guardian 2 (Vienna Circle): APPROVE - "Multi-source verification present"
Guardian 3 (Ubuntu): APPROVE - "Consensus reached"
...
Vote: 8 APPROVE, 0 REJECT, 1 ABSTAIN

✅ Certified: talent-legalbert-001
   Role: legal-analysis
   Restrictions: no_PII_logging, audit_all_outputs
   Certification level: PRODUCTION
   Valid until: 2026-11-11

Signing with Ed25519...
Publishing to capability registry...

Registry: if://registry/capabilities/legalbert/1.0.0
Signature: ed25519:a7f3d2e1c9b8...
```

**Certification Levels:**
- **EXPERIMENTAL:** Sandbox only, not production
- **BETA:** Production, but monitored closely
- **PRODUCTION:** Full production use
- **DEPRECATED:** Being phased out

#### Phase 6: Deployment (IF.booker)

```bash
$ if-cli booking assign talent-legalbert-001 --project=epic-v4

Checking project requirements...
  Domain: legal
  Required capabilities: document analysis, antitrust expertise
  Confidence threshold: >0.8
  Max latency: 500ms

Matching talent...
  talent-legalbert-001: ✓ (94% match)
  talent-docformer-002: ✓ (87% match)
  talent-layoutlm-003: ✓ (92% match)

Selected: talent-legalbert-001 (highest match)

Deploying to project epic-v4...
- Loading WASM module...
- Initializing in IF.chassis host...
- Registering with IF.guard...
- Connecting to IF.bus...

Deployed: talent-legalbert-001 → epic-v4
Status: ACTIVE
Endpoints:
  - Message bus: if://bus/epic-v4/legal
  - REST API: https://epic-v4.infrafabric.local/legal
  - WebSocket: wss://epic-v4.infrafabric.local/legal/ws

Ready to receive tasks.
```

#### Phase 7: Management (IF.career)

```bash
$ if-cli career report talent-legalbert-001

=== Career Report: talent-legalbert-001 ===

Tenure: 47 days
Projects: 3 (epic-v4, microsoft-v2, google-v1)
Total tasks: 1,247

Performance:
  Average confidence: 0.89 (↑ +0.04 from onboarding)
  Accuracy (human-verified): 96% (↑ +2% from certification)
  Escalation rate: 12% (industry avg: 18%) ✓
  Latency p50: 108ms (↓ -7ms from certification) ✓

User Satisfaction: 4.2/5 (23 reviews)
  "Very accurate on antitrust cases" - epic-v4 lead
  "Sometimes overcautious, but better safe" - microsoft-v2 lead

Career Trajectory:
  Current: Junior Legal Analyst
  Recommendation: Promote to Senior Legal Analyst
  Requirements for promotion:
    ✓ 30+ days tenure
    ✓ 90%+ accuracy
    ✓ <15% escalation rate
    ✓ 4.0+ satisfaction

Actions:
  [ ] Promote to Senior (unlocks higher-stakes cases)
  [ ] Specialize in antitrust (assign more antitrust projects)
  [ ] Continue general legal work

$ if-cli career promote talent-legalbert-001 --level=senior

Promotion approved by IF.guard.
talent-legalbert-001 is now: Senior Legal Analyst
New capabilities unlocked:
  - Handle cases >$100M in liability
  - Approve junior analyst outputs
  - Contribute to policy updates
```

---

## The CLI Philosophy (Operational Guarantees)

### 1. The `--why` Flag (Transparency)

**Concept:** Every command must justify itself

**Implementation:**
```bash
$ if-cli guard approve proposal-789 --why

Why are you approving this proposal?
> The legal team has reviewed the Epic settlement dossier and found no issues.
  All citations are verified and the confidence threshold is met (0.92 > 0.7).

Intent captured.
Proposal-789 approval logged with rationale:
  "Legal team review complete, citations verified, confidence 0.92"

Trace token: trace-b3c4d5e6
```

**Stored in IF.witness:**
```json
{
  "event": "guard_approval",
  "proposal_id": "proposal-789",
  "approver": "human://legal-lead@company.com",
  "rationale": "Legal team review complete, citations verified, confidence 0.92",
  "trace_token": "trace-b3c4d5e6",
  "timestamp": "2025-11-11T15:30:00Z",
  "signature": "ed25519:..."
}
```

### 2. The `--mode=falsify` Flag (Popperian Falsification)

**Concept:** Actively search for ways the command could fail BEFORE executing

**Implementation:**
```bash
$ if-cli swarm deploy epic-v4 --mode=falsify

Running pre-mortem analysis (Popperian falsification)...

Querying IF.preflight for potential failures:

⚠️  Failure Mode 1: Cross-swarm conflict (likelihood: 70%)
    Prediction: Finance swarm has $500M, Legal has $520M
    Historical: Last 3 times this pattern ran, conflict occurred
    Mitigation: Add explicit conflict resolution step

⚠️  Failure Mode 2: Timeout (likelihood: 60%)
    Prediction: Dossier >100 pages, timeout set to 30s
    Historical: 12/20 large dossiers timed out
    Mitigation: Increase timeout to 120s

⚠️  Failure Mode 3: Missing citation (likelihood: 40%)
    Prediction: Legal swarm may cite inaccessible source
    Historical: 8/50 runs had broken citation links
    Mitigation: Pre-validate all citation URLs

Recommendations:
  1. Add conflict resolution: if-cli swarm config --conflict-resolution=manual
  2. Increase timeout: if-cli swarm config --timeout=120s
  3. Enable citation pre-check: if-cli swarm config --verify-citations=true

Apply recommendations? [y/N] y

Applying mitigations...
✓ Conflict resolution: MANUAL
✓ Timeout: 120s
✓ Citation verification: ENABLED

Proceed with deployment? [y/N] y

Deploying epic-v4 with mitigations...
```

**How IF.preflight Works:**
1. Analyze historical witness logs (last 1000 similar commands)
2. Identify patterns that led to failures
3. Match current command against failure patterns
4. Predict likelihood of each failure mode
5. Suggest mitigations

### 3. Consensus Commands (Ubuntu Philosophy)

**Concept:** Major decisions require multi-stakeholder agreement

**Implementation:**
```bash
$ if-cli consensus propose "Deploy yologuard v4 to production" \
    --rationale="Benchmarks show 98.96% recall, all tests pass" \
    --required-votes=5 \
    --voting-period=24h

Proposal created: prop-456
Voting period: 24 hours (ends 2025-11-12 15:00:00)
Required votes: 5/8 Guardians
Notification sent to: [8 Guardians]

View proposal: if-cli consensus show prop-456
Vote: if-cli consensus vote prop-456 --decision=approve

$ if-cli consensus vote prop-456 --decision=approve \
    --rationale="Benchmarks are solid, no security concerns"

Vote recorded:
  Voter: guardian://popper@infrafabric.local
  Decision: APPROVE
  Rationale: "Benchmarks are solid, no security concerns"

Current tally:
  APPROVE: 3/8
  REJECT: 0/8
  PENDING: 5/8

Status: Voting in progress

$ if-cli consensus show prop-456

Proposal: prop-456
Title: Deploy yologuard v4 to production
Status: APPROVED (5 approve, 0 reject, 3 abstain)
Created: 2025-11-11 15:00:00
Closed: 2025-11-12 10:30:00

Votes:
  ✓ Popper: APPROVE - "Benchmarks solid, no security concerns"
  ✓ Vienna Circle: APPROVE - "Multi-source verification complete"
  ✓ Ubuntu: APPROVE - "Community consensus reached"
  ✓ Dewey: APPROVE - "Pragmatic benefits clear"
  ✓ Habermas: APPROVE - "Communicative rationality satisfied"
  - Kant: ABSTAIN - "Need more ethical review"
  - Rawls: ABSTAIN - "Justice implications unclear"
  - Foucault: ABSTAIN - "Power dynamics need analysis"

Actions available:
  if-cli consensus execute prop-456
```

### 4. The `--trace` Flag (Distributed Tracing)

**Concept:** Full observability - trace any request across entire system

**Implementation:**
```bash
$ if-cli swarm run epic-v4 --trace

Trace token: trace-a2f9c3b8d1e5

Starting epic-v4 swarm...
  Legal swarm: STARTED (3 agents)
  Finance swarm: STARTED (2 agents)
  Markets swarm: STARTED (2 agents)

Run ID: run-xyz789
Trace: https://infrafabric.local/trace/a2f9c3b8d1e5

$ if-cli trace show trace-a2f9c3b8d1e5

=== Trace: epic-v4 Analysis ===
Started: 2025-11-10 14:00:00
Duration: 4m 23s
Status: ESCALATED (human intervention required)

Call Graph:
├─ IF.swarm.legal [14:00:01 - 14:02:15] (2m 14s)
│  ├─ talent-legalbert-001 → Claim: "$520M settlement" (confidence: 0.8)
│  ├─ talent-docformer-002 → Claim: "$520M settlement" (confidence: 0.85)
│  └─ Consensus: "$520M settlement" (0.825 avg confidence)
│
├─ IF.swarm.finance [14:00:03 - 14:02:30] (2m 27s)
│  ├─ talent-finbert-003 → Claim: "$500M settlement" (confidence: 0.9)
│  └─ Consensus: "$500M settlement" (0.9 confidence)
│
├─ IF.relation_agent [14:02:31 - 14:02:45] (14s)
│  ├─ Detected: CONFLICT (Legal: $520M vs Finance: $500M)
│  ├─ Variance: 4% ($20M difference)
│  └─ Action: Trigger hazard tag (auto_escalate)
│
├─ IFMessage [14:02:46]
│  ├─ Hazard: {type: "conflict", severity: "high", auto_escalate: true}
│  └─ Route decision: ESCALATE (hazard overrides confidence)
│
├─ IF.escalate_handler [14:02:47 - 14:03:12] (25s)
│  ├─ Routing to: legal-expert@company.com
│  ├─ SIP INVITE sent
│  ├─ WebRTC connection: ESTABLISHED
│  └─ Evidence streaming: 2 citations sent
│
└─ Human Resolution [14:03:13 - 14:04:23] (1m 10s)
   ├─ Expert reviewed: Both claims + evidence
   ├─ Decision: "$520M is correct (Finance used old filing)"
   ├─ Action: Update Finance swarm data source
   └─ Status: RESOLVED

Total Messages: 23
Total Agents Involved: 6 (3 talent, 3 infrastructure)
Cost: $0.12 (tokens + compute)

Download full trace: if-cli trace download trace-a2f9c3b8d1e5 --format=json
```

---

## Implementation Timeline (12 Weeks)

### Weeks 1-2: Foundation (IF.chassis + IF.witness)

**Goal:** Basic chassis with message routing and audit logging

**Tasks:**
- [ ] Build IF.chassis host API (Rust)
  - Message send/receive
  - Signature verification (Ed25519)
  - Policy checking stub (IF.guard integration later)
- [ ] Build IF.witness append-only log
  - Hash-chained events
  - JSON storage (PostgreSQL or SQLite)
  - Query API
- [ ] Build simple CLI (`if-cli`)
  - `message send` command
  - `witness query` command
- [ ] Write 5 unit tests

**Deliverable:** Can send signed messages and log to witness

### Weeks 3-4: CLI Philosophy (--why, --trace, --mode=falsify)

**Goal:** Add philosophical guarantees to CLI

**Tasks:**
- [ ] Implement `--why` flag
  - Prompt user for rationale
  - Store in witness event
- [ ] Implement `--trace` flag
  - Generate trace tokens (UUID)
  - Link all events in a transaction
  - Build trace visualization (ASCII tree)
- [ ] Implement `--mode=falsify` (basic)
  - Query witness for similar past commands
  - Detect failures (status != success)
  - Warn user if >50% failure rate
- [ ] Add consensus commands
  - `consensus propose`
  - `consensus vote`
  - `consensus show`
  - `consensus execute`

**Deliverable:** CLI with full philosophical features

### Weeks 5-6: Talent Discovery (IF.scout + IF.prospector)

**Goal:** Discover and ingest capabilities from GitHub/Hugging Face

**Tasks:**
- [ ] Build IF.scout
  - GitHub API integration (GraphQL)
  - Hugging Face Hub integration
  - Ranking algorithm (stars, maintenance, license)
  - `if-cli scout search` command
- [ ] Build IF.prospector
  - Download to quarantine
  - Static analysis (license check, code scan)
  - `if-cli prospector ingest` command
- [ ] Build quarantine environment
  - Docker container with restrictions
  - Resource limits (RAM, CPU)
  - Network isolation

**Deliverable:** Can discover and quarantine capabilities

### Weeks 7-8: Adapter Generation (IF.adapter_agent)

**Goal:** Auto-generate adapters from quarantined capabilities

**Tasks:**
- [ ] Build IF.adapter_agent
  - Analyze model interface (input/output types)
  - Generate Python wrapper code
  - Add IFMessage conversion
  - Add hazard detection logic
  - `if-cli adapter generate` command
- [ ] Implement WASM compilation
  - Python → WASM (via py2wasm or similar)
  - Bundle dependencies
  - Optimize for size
  - `if-cli adapter compile` command

**Deliverable:** Can auto-generate and compile adapters

### Weeks 9-10: Testing & Certification (IF.sandbox + IF.talent)

**Goal:** Test adapters and certify for production

**Tasks:**
- [ ] Build IF.sandbox
  - Isolated environment (Docker/WASM runtime)
  - Test dataset management
  - Performance metrics collection
  - `if-cli sandbox test` command
- [ ] Build IF.deception honeypots
  - Fake PII in test data
  - Fake credentials
  - Monitor for exfiltration attempts
- [ ] Build IF.talent certification
  - IF.guard integration (approval workflow)
  - Signature generation
  - Capability registry storage
  - `if-cli talent certify` command

**Deliverable:** Can test and certify capabilities

### Weeks 11-12: Deployment & Management (IF.booker + IF.career)

**Goal:** Deploy certified talents and track performance

**Tasks:**
- [ ] Build IF.booker
  - Project requirements matching
  - Load balancing algorithm
  - Hot-swap orchestration
  - `if-cli booking assign` command
- [ ] Build IF.career tracking
  - Performance metrics aggregation
  - Promotion recommendations
  - `if-cli career report` command
  - `if-cli career promote` command
- [ ] Build capability registry
  - WASM module storage (OCI registry)
  - Version management
  - Signature verification

**Deliverable:** Full talent lifecycle operational

---

## Success Metrics (End of 12 Weeks)

### Functional Metrics:
- ✅ Can onboard new AI capability in <10 hours (vs 2-4 weeks)
- ✅ 100% of messages are signed and traced
- ✅ 100% of actions have `--why` rationales
- ✅ `--mode=falsify` reduces failures by >50%
- ✅ Consensus commands work for major decisions

### Technical Metrics:
- ✅ IF.chassis supports >100 msg/sec throughput
- ✅ WASM modules load in <500ms
- ✅ Hot-swap completes in <5s with 0 downtime
- ✅ Witness logs queryable in <100ms (p99)

### Business Metrics:
- ✅ 3+ capabilities onboarded via IF.scout
- ✅ 10+ test deployments to real projects
- ✅ 1+ production deployment (beta user)

---

## Quick Start (This Week)

Want to start RIGHT NOW? Here's what to do:

### Day 1-2: Set Up Development Environment

```bash
# Clone repo
cd /home/user/infrafabric

# Install Rust (for IF.chassis)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Create project structure
mkdir -p src/chassis src/witness src/cli
mkdir -p tools/scout tools/prospector tools/adapter_agent

# Initialize Rust workspace
cargo init --lib src/chassis
cargo init --lib src/witness
cargo init --bin src/cli

# Install Python dependencies (for adapter generation)
pip install transformers torch huggingface_hub

# Install Node (for WebRTC later)
# Already installed: Node 18+
```

### Day 3-5: Build Minimal IF.chassis

```rust
// src/chassis/src/lib.rs

use serde::{Deserialize, Serialize};
use ed25519_dalek::{Keypair, PublicKey, Signature, Signer, Verifier};

#[derive(Serialize, Deserialize, Debug)]
pub struct IFMessage {
    pub performative: String,
    pub sender: String,
    pub receiver: Vec<String>,
    pub content: serde_json::Value,
    pub timestamp: String,
    pub sequence_num: u64,
    pub trace_id: String,
}

pub struct Chassis {
    keypair: Keypair,
}

impl Chassis {
    pub fn new() -> Self {
        let mut csprng = rand::rngs::OsRng{};
        let keypair = Keypair::generate(&mut csprng);
        Self { keypair }
    }

    pub fn send_message(&self, mut msg: IFMessage) -> Result<(), Box<dyn std::error::Error>> {
        // Add signature
        let msg_json = serde_json::to_string(&msg)?;
        let signature = self.keypair.sign(msg_json.as_bytes());

        // Log to witness
        self.log_event("message_sent", &msg)?;

        // TODO: Actually send via IF.bus
        println!("Sent: {:?}", msg);
        Ok(())
    }

    pub fn verify_signature(&self, msg: &IFMessage, sig: &Signature, pub_key: &PublicKey) -> bool {
        let msg_json = serde_json::to_string(msg).unwrap();
        pub_key.verify(msg_json.as_bytes(), sig).is_ok()
    }

    pub fn log_event(&self, event_type: &str, data: &IFMessage) -> Result<(), Box<dyn std::error::Error>> {
        // TODO: Implement IF.witness integration
        println!("LOG: {} - {:?}", event_type, data);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_send_message() {
        let chassis = Chassis::new();
        let msg = IFMessage {
            performative: "inform".to_string(),
            sender: "if://test/agent-1".to_string(),
            receiver: vec!["if://test/agent-2".to_string()],
            content: serde_json::json!({"claim": "test"}),
            timestamp: "2025-11-11T15:00:00Z".to_string(),
            sequence_num: 1,
            trace_id: "trace-test-123".to_string(),
        };

        assert!(chassis.send_message(msg).is_ok());
    }
}
```

### Day 6-7: Build Minimal CLI

```rust
// src/cli/src/main.rs

use clap::{Parser, Subcommand};
use infrafabric_chassis::{Chassis, IFMessage};

#[derive(Parser)]
#[command(name = "if-cli")]
#[command(about = "InfraFabric CLI", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Send a message
    Message {
        #[arg(long)]
        claim: String,

        #[arg(long)]
        why: Option<String>,

        #[arg(long)]
        trace: bool,
    },

    /// Query witness logs
    Witness {
        #[arg(long)]
        trace_id: Option<String>,
    },
}

fn main() {
    let cli = Cli::parse();
    let chassis = Chassis::new();

    match &cli.command {
        Commands::Message { claim, why, trace } => {
            // Prompt for --why if not provided
            let rationale = if let Some(w) = why {
                w.clone()
            } else {
                println!("Why are you sending this message?");
                let mut input = String::new();
                std::io::stdin().read_line(&mut input).unwrap();
                input.trim().to_string()
            };

            // Generate trace token if --trace
            let trace_id = if *trace {
                format!("trace-{}", uuid::Uuid::new_v4())
            } else {
                String::new()
            };

            let msg = IFMessage {
                performative: "inform".to_string(),
                sender: "if://cli/user".to_string(),
                receiver: vec!["if://swarm/test".to_string()],
                content: serde_json::json!({
                    "claim": claim,
                    "rationale": rationale
                }),
                timestamp: chrono::Utc::now().to_rfc3339(),
                sequence_num: 1,
                trace_id: trace_id.clone(),
            };

            chassis.send_message(msg).unwrap();

            if *trace {
                println!("Trace token: {}", trace_id);
            }
        }

        Commands::Witness { trace_id } => {
            println!("Querying witness logs...");
            // TODO: Implement witness query
        }
    }
}
```

### Test It:

```bash
# Build
cargo build --release

# Run
./target/release/if-cli message --claim "Test message" --trace

Why are you sending this message?
> Testing the CLI implementation

Sent: IFMessage { ... }
Trace token: trace-a2f9c3b8-d1e5-4f6a-7b8c-9d0e1f2a3b4c
```

---

## Next Steps After Week 1

1. ✅ You have working chassis + CLI
2. → Week 2: Add IF.witness (persistent logging)
3. → Week 3-4: Add `--mode=falsify` and consensus
4. → Week 5+: Start talent lifecycle (scout, prospector, etc.)

---

**Want me to:**
1. **Create the actual Rust code files** for IF.chassis?
2. **Build the Python adapter generator** for Week 7-8?
3. **Design the database schema** for IF.witness?
4. **Create a detailed Week 1 task list** with hourly breakdown?
5. **Something else?**

Let's build this! 🚀
