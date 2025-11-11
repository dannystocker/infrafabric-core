# InfraFabric Talent Lifecycle - Complete Integration

**Synthesis of: Gemini Audit (121 topics) + GPT-5 Genesis (13 sections) + Perplexity Digest (5-phase model)**

**Date:** 2025-11-11
**Purpose:** Unified reference for the complete talent lifecycle architecture

---

## Executive Summary

InfraFabric manages AI agents and code modules using a **talent agency metaphor** with:
- **5 lifecycle phases** (Discovery → Development → Management → Deployment → Governance)
- **9 operational roles** (scout, developer, coach, packager, manager, agent, caster, booker, + 3 support roles)
- **3 integration tiers** (full-trust, read-only, batch-processing)
- **Governance tax** (all adapters must pay compliance cost to gain benefits)

This document maps all three source models into a single, actionable reference.

---

## The Five-Phase Lifecycle (Perplexity Model)

### Phase 1: Discovery & Acquisition

**Purpose:** Find and vet external capabilities (primarily from GitHub)

**Roles:**
- `if.talent.scout` - Automated capability discovery

**Process:**
1. Search GitHub for needed functionality (keywords, stars, license)
2. Filter by quality heuristics (tests, documentation, activity)
3. License compatibility check (MIT, Apache 2.0, BSD)
4. Initial static analysis (security, code quality)
5. Quarantine viable candidates

**Real-World Analogy:** Talent scout searching for raw potential

**Why Novel:** Converts global open-source code into ops-grade capabilities with reproducibility

**Example CLI:**
```bash
$ if scout search "legal document analysis" --license mit,apache
Found 12 candidates:
1. LegalBERT (Hugging Face) - 94% accuracy, MIT license ⭐ 2.3K
2. DocFormer (GitHub) - 89% accuracy, Apache 2.0 ⭐ 1.8K
...

$ if scout quarantine nom-789
Quarantining LegalBERT...
Quarantine ID: quar-123
Status: ISOLATED (sandboxed environment)
```

---

### Phase 2: Development & Packaging

**Purpose:** Adapt external code to InfraFabric standards and certify it

**Roles:**
- `if.talent.developer` - AI-generated adapters and glue code
- `if.talent.coach` - Quality gates (linters, static/dynamic analysis)
- `if.talent.packager` - Cryptographic signing and registry publishing

**Process:**

#### 2A. Adaptation (Developer)
1. Analyze quarantined code's API surface
2. Generate adapter code (Python wrapper → WASM-compatible interface)
3. Integrate with IF.chassis host API
4. Add hazard detection (IF.veritas integration)
5. Compile to WASM module

**Example:**
```python
# Auto-generated adapter (if.talent.developer output)
class LegalBERTAdapter:
    def __init__(self, chassis: ChassisHost):
        self.chassis = chassis
        self.model = AutoModel.from_pretrained("legalbert")

    def analyze(self, documents: List[str]) -> IFMessage:
        # Run model
        outputs = self.model(documents)

        # Detect hazards (IF.veritas)
        hazard = None
        if "liability" in prediction and confidence < 0.7:
            hazard = Hazard(
                type=HazardType.LEGAL,
                severity="high",
                rationale="Low confidence on liability claim"
            )

        return IFMessage(
            performative="inform",
            content={"claim": prediction, "confidence": confidence},
            hazard=hazard,
            citation_ids=self.extract_citations(documents)
        )
```

#### 2B. Quality Gating (Coach)
1. Static analysis (SAST):
   - Secret detection (IF.yologuard)
   - Dependency vulnerabilities (SCA)
   - Code quality (linters, complexity)
2. Dynamic analysis:
   - Fuzz testing in sandbox
   - Behavior monitoring (IF.deception honeypots)
   - Resource limits (CPU/memory/network)
3. Policy compliance:
   - License verification
   - IP/trademark checks
   - Export control (if applicable)

**Gates:**
- Must pass all SAST checks (no secrets, no vulns)
- Must complete 100 fuzz iterations without crash
- Must respect WASI sandbox constraints

#### 2C. Certification (Packager)
1. Generate provenance record (SLSA-style):
   - Source: GitHub URL + commit hash
   - Build: Compiler version, flags, timestamp
   - Tests: All test results + coverage
   - Security: SAST/DAST reports
2. Sign with Ed25519 keypair
3. Publish to capability registry (OCI-compatible)
4. Update talent registry with new capability

**Example:**
```bash
$ if packager certify quar-123
Running certification pipeline...
✅ Static analysis passed (0 secrets, 0 vulns)
✅ Dynamic analysis passed (100/100 fuzz tests)
✅ Policy compliance verified

Generating provenance record...
Signing with key: if://keys/packager-001
Publishing to registry: registry.infrafabric.io/talent/legalbert-001:v1.0.0

Capability certified: cap-abc123
```

**Real-World Analogy:**
- Developer = Producer prepping for showtime
- Coach = Acting coach / editor ensuring quality
- Packager = Security admin certifying release

**Why Novel:** Closes typical open-source supply-chain holes with automated, strict quality gates

---

### Phase 3: Management & Strategy

**Purpose:** Orchestrate swarms and assign capabilities to agents

**Roles:**
- `if.talent.manager` - Swarm-wide strategy and long-term goals
- `if.talent.agent` - Assigns agents to projects, updates agent registries

**Process:**

#### 3A. Strategic Management (Manager)
1. Define swarm goals (e.g., "Analyze Epic settlement by Nov 15")
2. Decompose into sub-tasks
3. Allocate resources (budget, compute, agents)
4. Monitor progress and adjust strategy
5. Handle escalations (conflicts, blockers)

**Example:**
```bash
$ if manager create-swarm epic-settlement-analysis \
  --goal "Comprehensive settlement analysis" \
  --teams legal,finance,markets,macro \
  --deadline 2025-11-15

Swarm created: swarm-epic-001
Allocated resources:
  - 4 teams (legal, finance, markets, macro)
  - Budget: $500 compute credits
  - Agents: Auto-assigned based on capabilities

$ if manager monitor swarm-epic-001
Progress: 65% complete
- Legal team: ✅ Completed (confidence: 0.85)
- Finance team: ⚠️  Conflict detected (variance: 25%)
- Markets team: 🔄 In progress (80% complete)
- Macro team: ⏸️  Waiting on Finance resolution

⚠️  Escalation: Finance/Legal variance requires human resolution
```

#### 3B. Agent Assignment (Agent)
1. Receive new capability from registry
2. Identify agents that would benefit
3. Update agent profiles with new skill
4. Notify booker of availability

**Example:**
```bash
$ if agent assign cap-abc123 \
  --agents agent-legal-001,agent-legal-002 \
  --skill-level advanced

Updated agent profiles:
✅ agent-legal-001: +legalbert-analysis (advanced)
✅ agent-legal-002: +legalbert-analysis (advanced)

Notified booker: 2 agents now capable of legal document analysis
```

**Real-World Analogy:**
- Manager = Talent manager (long-term career strategy)
- Agent = Talent agent (finds projects for clients)

**Organizational Memory:** Delivers trust and structured tasking

---

### Phase 4: Deployment & Booking

**Purpose:** Match agents to tasks and execute work

**Roles:**
- `if.talent.caster` - Selects best agent for task (casting director)
- `if.talent.booker` - Allocates compute, spins up containers, manages execution

**Process:**

#### 4A. Casting (Caster)
1. Receive task request (e.g., "Analyze contract for liability")
2. Query talent registry for matching skills
3. Score candidates:
   - Skill match (required capabilities)
   - Trust score (past performance)
   - Availability (current workload)
   - Cost (compute budget)
4. Select best candidate(s)

**Casting Algorithm:**
```python
def cast_agent(task: Task) -> List[Agent]:
    # Find agents with required skills
    candidates = talent_registry.query(skills=task.required_skills)

    # Score each candidate
    scored = []
    for agent in candidates:
        score = (
            0.4 * skill_match(agent, task) +      # 40% skill match
            0.3 * trust_score(agent) +             # 30% trust/performance
            0.2 * availability(agent) +            # 20% availability
            0.1 * cost_efficiency(agent, task)     # 10% cost
        )
        scored.append((score, agent))

    # Return top 3 candidates
    return sorted(scored, reverse=True)[:3]
```

**Example:**
```bash
$ if caster cast --task "Analyze contract for liability" --top 3

Casting agents for task: "Analyze contract for liability"

Top candidates:
1. agent-legal-003 (score: 0.92)
   - Skills: contract-analysis ✅, liability-detection ✅
   - Trust: 0.95 (18 successful tasks, 0 failures)
   - Availability: HIGH (0% workload)
   - Cost: $0.05/analysis

2. agent-legal-001 (score: 0.87)
   - Skills: legalbert-analysis ✅, contract-analysis ✅
   - Trust: 0.88 (12 successful, 1 timeout)
   - Availability: MEDIUM (40% workload)
   - Cost: $0.08/analysis

3. agent-legal-005 (score: 0.81)
   - Skills: general-nlp ⚠️, contract-analysis ✅
   - Trust: 0.90 (22 successful, 0 failures)
   - Availability: LOW (75% workload)
   - Cost: $0.04/analysis

Recommend: agent-legal-003
```

#### 4B. Booking (Booker)
1. Receive cast decision from caster
2. Allocate compute resources (K8s pod, WASM runtime)
3. Load agent's WASM payloads
4. Execute task with monitoring
5. Handle failures (retry, escalate, circuit-break)

**Example:**
```bash
$ if booker book agent-legal-003 --task task-456

Booking agent-legal-003 for task-456...
✅ Allocated compute: pod-abc123 (2 CPU, 4GB RAM)
✅ Loaded WASM payloads:
   - legalbert-001:v1.0.0 (sha256:a2f9c3b8...)
   - contract-analyzer:v2.1.0 (sha256:d1e5f6g7...)
✅ Executing task...

Task progress:
[████████████████░░░░] 80% (2m 15s elapsed)

✅ Task completed successfully
Result: {
  "liability_detected": true,
  "confidence": 0.92,
  "summary": "Contract contains uncapped liability clause in Section 7.3"
}

Logged to witness: event-789
```

**Real-World Analogy:**
- Caster = Casting director (chooses actors for roles)
- Booker = Scheduler (books gigs, manages logistics)

---

### Phase 5: Governance & Compliance

**Purpose:** Enforce policy, send alerts, and monitor security continuously

**Roles:**
- `if.talent.businessaffairs` - Policy engine (IF.guard)
- `if.talent.publicist` - System alerts and notifications
- `if.talent.security` - Continuous security monitoring (IF.armour, IF.deception, IF.vigil)

**Process:**

#### 5A. Policy Enforcement (Business Affairs / IF.guard)
1. Intercept every action before execution
2. Check policy rules:
   - Operational policies (e.g., "no delete on production")
   - Compliance policies (e.g., "GDPR data handling")
   - Security policies (e.g., "require 2FA for sensitive ops")
3. Make decision: Allow / Deny / Escalate
4. Log decision to IF.witness

**Policy Rules Example:**
```yaml
# /etc/infrafabric/guard-policies.yaml
policies:
  - name: "Protect production databases"
    condition: "action == 'delete' AND resource CONTAINS 'production'"
    decision: DENY
    reason: "Cannot delete production resources without approval"

  - name: "Critical deployments require human approval"
    condition: "action == 'deploy' AND resource CONTAINS 'critical'"
    decision: ESCALATE
    reason: "Critical deployments require guardian approval"

  - name: "PII must be encrypted"
    condition: "data.contains_pii == true AND encryption == false"
    decision: DENY
    reason: "GDPR violation: PII must be encrypted at rest"
```

**Example:**
```bash
$ if guard check delete production-db

🛡️  Checking policy: delete on production-db

Policy matched: "Protect production databases"
❌ DENY - Cannot delete production resources without approval

Action blocked. To override, request approval:
$ if guard request-approval --policy prod-delete --justification "..."
```

#### 5B. Alerting (Publicist)
1. Monitor system events from IF.witness
2. Generate alerts for:
   - Policy violations
   - Security incidents
   - Operational anomalies
   - SLA breaches
3. Route to appropriate channels (Slack, PagerDuty, email)

**Example:**
```bash
$ if publicist configure alert \
  --type policy_violation \
  --severity high \
  --channel slack-security

Alert configured: alert-123
Trigger: policy_violation (severity >= high)
Channel: slack-security (#infra-security)

$ if publicist send-notification \
  --message "Cross-swarm conflict detected in Epic settlement analysis" \
  --severity medium \
  --channels slack-ops,email-managers

Notification sent:
✅ Slack: #infra-ops (3 members notified)
✅ Email: managers@company.com (5 recipients)
```

#### 5C. Security Monitoring (Security / IF.armour + IF.deception + IF.vigil)

**IF.armour - Active Defense:**
- Static + dynamic security scanning
- Threat hunting
- Deception traps (honeypots) to exhaust attackers

**IF.deception - Adversarial Drain:**
- Fake success responses to waste attacker time
- Behavior fingerprinting to identify malicious patterns

**IF.vigil - Retrospective Analysis:**
- Re-scan witness logs with new threat intelligence
- Late-bloomer detection (vulnerabilities discovered post-deployment)
- Continuous re-verification of past decisions

**Example:**
```bash
$ if security scan --target agent-legal-003

Running security scan...
✅ Static analysis: No vulnerabilities detected
✅ Dynamic analysis: Behavior within expected bounds
⚠️  Deception trap triggered: 3 suspicious queries detected

Suspicious queries:
1. "SELECT * FROM users WHERE password LIKE '%'" (SQL injection attempt)
2. "../../../etc/passwd" (path traversal attempt)
3. Excessive rate (1000 req/s from single IP)

Actions taken:
✅ Blocked attacker IP: 192.168.1.100
✅ Logged to witness: event-890
✅ Notified security team: alert-124

$ if vigil retrospective --days 30

Re-scanning 30 days of witness logs with latest threat intel...
🔍 Analyzing 45,123 events...

Findings:
⚠️  5 events matched new CVE-2025-12345 signature
   - Affected agent: agent-finance-002
   - Risk: Medium (potential data leak)
   - Action: Rotate credentials, re-certify agent

✅ Retrospective scan complete
Generated report: reports/vigil-2025-11-11.pdf
```

**Real-World Analogy:**
- Business Affairs = Legal/compliance team
- Publicist = PR/communications team
- Security = Security operations center (SOC)

---

## Governance Tax

**Concept:** Any system/adapter must comply with InfraFabric's rules to gain full provenance and security coverage.

**What You Pay (Compliance Costs):**
1. **Adapter Development:** Generate IF-compatible wrapper (automated)
2. **Certification Pipeline:** Pass SAST, DAST, policy checks (~1-2 days per component)
3. **Registry Publishing:** Sign and publish to capability registry
4. **Operational Monitoring:** IF.witness logging, IF.guard policy enforcement

**What You Gain (Benefits):**
1. **Full Provenance:** Traceable lineage for every action
2. **Security Coverage:** IF.armour, IF.deception, IF.vigil protection
3. **Audit Compliance:** Immutable logs for regulatory requirements
4. **Hot-Swap Capability:** Zero-downtime updates
5. **Trust Score:** Verified reputation in talent registry

**Example:**
```text
External Code (GitHub):
   ↓ (Pay governance tax)
   ├─ Adapt: Generate wrapper (~1 hour automated)
   ├─ Certify: Pass security gates (~1 day)
   ├─ Sign: Cryptographic attestation
   └─ Publish: Capability registry

Result:
   ✅ Trusted, auditable, hot-swappable capability
   ✅ Full IF.witness provenance
   ✅ IF.guard policy enforcement
   ✅ IF.armour security monitoring
```

---

## Legacy Integration Tiers

InfraFabric supports three integration levels for legacy systems:

### Tier 1: Full-Trust Integration

**Description:** Legacy system fully integrated with IF governance

**Requirements:**
- Adapter generates complete IF messages (performative, hazard, citations)
- All actions logged to IF.witness
- IF.guard policy checks enforced
- Ed25519 signatures on all messages

**Use Cases:**
- Critical financial systems
- Legal/compliance systems
- Production databases

**Example:**
```python
# Full-trust adapter for SAP ERP
class SAPAdapter:
    def __init__(self, chassis: ChassisHost):
        self.chassis = chassis
        self.sap_client = SAPClient(credentials)

    def execute_transaction(self, txn: Transaction) -> IFMessage:
        # Check policy BEFORE executing
        decision = self.chassis.check_policy("execute", f"sap-txn-{txn.type}")
        if decision == GuardDecision.DENY:
            raise PolicyViolation("Transaction blocked by IF.guard")

        # Execute transaction
        result = self.sap_client.execute(txn)

        # Log to witness
        self.chassis.log_event("sap_transaction", {
            "txn_id": txn.id,
            "type": txn.type,
            "result": result
        })

        # Return IF message with full provenance
        return IFMessage(
            performative="inform",
            content={"result": result},
            citation_ids=[f"sap-txn-{txn.id}"],
            signature=self.chassis.sign(...)
        )
```

### Tier 2: Read-Only Integration

**Description:** Legacy system read-only access (queries, not writes)

**Requirements:**
- IF messages generated for reads only
- Writes require manual human approval
- Witness logging for read operations
- No signature requirement (lower risk)

**Use Cases:**
- Reporting/analytics systems
- Read-only databases
- Public APIs

**Example:**
```python
# Read-only adapter for legacy PostgreSQL
class PostgreSQLReadOnlyAdapter:
    def query(self, sql: str) -> IFMessage:
        # Allow reads, block writes
        if any(keyword in sql.upper() for keyword in ["INSERT", "UPDATE", "DELETE", "DROP"]):
            raise PolicyViolation("Write operations not allowed in read-only mode")

        result = self.pg_client.execute(sql)

        return IFMessage(
            performative="inform",
            content={"rows": result},
            citation_ids=[f"pg-query-{hash(sql)}"]
        )
```

### Tier 3: Batch-Processing Integration

**Description:** Async, batch-mode integration (eventual consistency)

**Requirements:**
- Messages queued for batch processing
- Results delivered asynchronously
- Reduced logging (sampled, not every event)
- No real-time policy enforcement

**Use Cases:**
- Data warehouses
- Batch ETL jobs
- Historical analytics

**Example:**
```python
# Batch adapter for data warehouse
class DataWarehouseBatchAdapter:
    def submit_query(self, query: str) -> str:
        # Submit to batch queue
        job_id = self.warehouse.submit_batch_job(query)

        # Log submission (not result)
        self.chassis.log_event("batch_job_submitted", {"job_id": job_id})

        return job_id

    def poll_result(self, job_id: str) -> IFMessage:
        result = self.warehouse.get_job_result(job_id)

        return IFMessage(
            performative="inform",
            content={"result": result},
            citation_ids=[f"batch-job-{job_id}"]
        )
```

**Tier Selection Guide:**
| Legacy System Type | Recommended Tier | Rationale |
|--------------------|------------------|-----------|
| Financial transactions | Tier 1 (Full-Trust) | Requires audit trail |
| Legal document storage | Tier 1 (Full-Trust) | Compliance requirements |
| Public APIs (read-only) | Tier 2 (Read-Only) | Low risk, high frequency |
| Data warehouse analytics | Tier 3 (Batch) | Eventual consistency OK |
| Production databases (write) | Tier 1 (Full-Trust) | Critical operations |

---

## IF.preflight: Predictive Risk Assessment

**Purpose:** Proactively flag likely operational errors/failures BEFORE they escalate

**How It Works:**

1. **Historical Learning:**
   - Mine IF.witness logs for failure patterns
   - Identify common precursors to:
     - Timeouts
     - Cross-swarm conflicts
     - Resource exhaustion
     - Policy violations

2. **Risk Scoring:**
   - Attach "hazard risk" score to each incoming task:
     - `risk_timeout`: Likelihood of exceeding time limit (0.0-1.0)
     - `risk_conflict`: Likelihood of cross-swarm disagreement (0.0-1.0)
     - `risk_overload`: Likelihood of resource exhaustion (0.0-1.0)

3. **Dynamic Routing:**
   - High-risk tasks → More capable agents
   - Low-risk tasks → Standard agents
   - Critical-risk tasks → Human review queue

4. **Circuit-Breaking:**
   - If risk exceeds threshold (e.g., 0.9), hold task
   - Trigger pre-emptive escalation to human
   - Avoid cascading failures

**Example:**

```python
# IF.preflight risk assessment
class PreflightAgent:
    def __init__(self, witness_chain: List[WitnessEvent]):
        self.history = witness_chain
        self.failure_patterns = self.learn_patterns()

    def learn_patterns(self) -> Dict[str, Pattern]:
        """Mine witness logs for failure patterns"""
        patterns = {}

        # Find all timeout events
        timeouts = [e for e in self.history if e.event_type == "task_timeout"]

        # Analyze common features
        for timeout in timeouts:
            task = timeout.payload["task"]
            # Pattern: Tasks with >5 swarms have 70% timeout rate
            if len(task["swarms"]) > 5:
                patterns["many_swarms_timeout"] = Pattern(
                    condition=lambda t: len(t["swarms"]) > 5,
                    risk_score=0.7
                )

        return patterns

    def assess_risk(self, task: Task) -> RiskScore:
        """Assess risk before task execution"""
        risk = RiskScore(
            risk_timeout=0.0,
            risk_conflict=0.0,
            risk_overload=0.0
        )

        # Check each pattern
        for pattern in self.failure_patterns.values():
            if pattern.condition(task):
                risk.risk_timeout = max(risk.risk_timeout, pattern.risk_score)

        # Check for cross-swarm conflicts
        if task.requires_consensus and len(task.swarms) >= 3:
            risk.risk_conflict = 0.6  # Historical: 60% of 3+ swarm tasks have conflicts

        return risk
```

**CLI Example:**
```bash
$ if preflight analyze --task task-456

Analyzing task: "Epic settlement cross-swarm analysis"

Risk Assessment:
⚠️  risk_timeout: 0.72 (HIGH)
    Reason: Task involves 4 swarms (historical timeout rate: 72%)
    Mitigation: Increase timeout from 60s to 120s

⚠️  risk_conflict: 0.65 (MEDIUM-HIGH)
    Reason: Finance/Legal swarms historically disagree 65% of time
    Mitigation: Add explicit conflict resolution step

✅ risk_overload: 0.15 (LOW)
    Reason: Task complexity within normal bounds

Recommendations:
1. if task update task-456 --timeout 120
2. if task config task-456 --conflict-resolution manual
3. Pre-allocate human reviewer for expected conflict

Apply recommendations? [y/N]
```

**Synergy with IF.armour:**

**IF.armour** defends against adversarial threats (malicious actors)
**IF.preflight** defends against operational risks (accidental failures)

Combined, they provide:
- **Adversarial defense:** IF.armour catches attacks, honeypots drain attackers
- **Operational defense:** IF.preflight prevents predictable failures
- **Holistic resilience:** System handles both intentional AND accidental harm

---

## Implementation Priority Matrix

Based on all three sources, here's the recommended build order:

| Priority | Component | Complexity | Impact | Rationale |
|----------|-----------|------------|--------|-----------|
| 1 | IF.chassis + IF.witness | Medium | Critical | Foundation for all other components |
| 2 | if-cli (--why, --trace) | Low | High | Developer workflow, immediate productivity |
| 3 | IF.guard (policy engine) | Medium | High | Governance baseline |
| 4 | IF.scout (GitHub discovery) | Medium | Very High | **Development speed multiplier** |
| 5 | IF.adapter_agent | High | Very High | Enables talent ingestion |
| 6 | IF.preflight | Medium | High | Operational risk reduction |
| 7 | IF.caster + IF.booker | Medium | High | Deployment automation |
| 8 | IF.armour + IF.deception | High | High | Security hardening |
| 9 | IF.vigil | Medium | Medium | Continuous improvement |
| 10 | Legacy adapters (Tier 1-3) | High | Medium | Enterprise integration |

---

## Summary: Three-Source Synthesis

**GPT-5 Genesis contributed:**
- 90/10 chassis architecture
- CLI philosophy (--why, --trace, --mode=falsify)
- 9-role talent model
- Communication layer (Swarp v4*)

**Gemini Audit contributed:**
- 121 topics covering all system aspects
- VC audit response plan
- Security red-teaming scenarios
- Comprehensive extraction of all features

**Perplexity Digest contributed:**
- 5-phase lifecycle structure (more digestible)
- IF.preflight detailed explanation
- Governance tax concept
- Legacy integration tier system
- Clearer role mapping

**This document unifies all three sources into a single, actionable reference for building InfraFabric.**

---

**Questions? Next Steps:**
1. Follow 12-week implementation plan: `docs/IMPLEMENTATION-ROADMAP-TALENT-CLI.md`
2. Build Rust POC: `RUST-QUICKSTART.md`
3. Week 1 focus: IF.chassis + IF.witness + if-cli foundations
