# H.323 Kantian Policy Specification for Guardian Council

**Component:** IF.guard Admission Control
**Philosophy:** Kantian Ethics (Categorical Imperatives)
**Purpose:** Enforce governance principles through cryptographic gates
**Version:** 1.0
**Last Updated:** 2025-11-11

---

## Table of Contents

1. [Overview](#overview)
2. [Categorical Imperatives](#categorical-imperatives)
3. [Admission Gates](#admission-gates)
4. [Policy Constraints](#policy-constraints)
5. [ESCALATE Triggers](#escalate-triggers)
6. [Rejection Reasons](#rejection-reasons)
7. [Philosophical Grounding](#philosophical-grounding)

---

## Overview

The H.323 Gatekeeper enforces **Kantian categorical imperatives** as admission gates. These are absolute rules that apply universally, regardless of context or consequences.

### Philosophy: Deontological Ethics

> "Act only according to that maxim whereby you can, at the same time, will that it should become a universal law."
> — Immanuel Kant, *Groundwork for the Metaphysics of Morals* (1785)

**Applied to H.323 Admission**:
- **Universal Law**: Rules must apply to all guardians equally (no exceptions)
- **Duty Over Consequences**: Gates enforce principles, not outcomes
- **Moral Autonomy**: Each guardian's Ed25519 key = autonomous moral agent

---

## Categorical Imperatives

### Imperative 1: Authenticity

> **"Never admit a terminal without cryptographic proof of identity."**

**Rationale**: Trust requires verification. Signatures cannot be forged.

**Implementation**:
- Ed25519 signature on all admission requests (ARQ)
- Public key verification against Guardian Registry
- Constant-time verification (timing attack resistant)

**Failure Mode**:
- Reject with `INVALID_SIGNATURE` if verification fails
- Log to IF.witness for audit

**Why Universal**:
- If one guardian bypasses signatures, impersonation becomes possible
- System collapses if authenticity is optional
- **Categorical Imperative**: "Always verify signatures" must be universal law

---

### Imperative 2: Anti-Sybil

> **"Never admit an unregistered terminal."**

**Rationale**: Governance requires known participants. Sybil attacks (fake identities) undermine consensus.

**Implementation**:
- Guardian Registry whitelist (`config/guardian-registry.yaml`)
- Registry contains: `terminal_id`, `public_key`, `role`, `status`
- Only `status: "active"` guardians admitted

**Failure Mode**:
- Reject with `NOT_REGISTERED` if terminal not in registry
- Reject if terminal's public key ≠ registered public key

**Why Universal**:
- If one unknown terminal joins, votes can be manipulated
- Consensus requires known participants
- **Categorical Imperative**: "Only registered guardians participate" ensures legitimacy

---

### Imperative 3: PII Protection

> **"Never allow personally identifiable information (PII) in ESCALATE calls."**

**Rationale**: High-stakes decisions must be bias-free. PII introduces cognitive bias.

**Implementation**:
- ARQ includes `has_pii: bool` field (self-declared by guardian)
- If `call_type == ESCALATE` AND `has_pii == true` → REJECT
- Honor system (guardians self-declare), enforced by policy engine

**Failure Mode**:
- Reject with `PII_POLICY_VIOLATION`
- Log rejection to IF.witness (audit trail)

**Why Universal**:
- ESCALATE calls address civilizational-scale risks
- PII biases decision-making (e.g., "friend of a friend" logic)
- **Categorical Imperative**: "Decisions affecting millions must be impersonal"

**Example**:
- ❌ **Biased**: "John Smith, age 34, father of 2, lost his job due to AI automation"
- ✅ **Unbiased**: "34% of workers in manufacturing displaced by automation (BLS data)"

---

### Imperative 4: Fairness (Bandwidth Quota)

> **"Never exceed bandwidth quota (10 Mbps per guardian)."**

**Rationale**: Fairness requires equal resource access. Bandwidth monopolization silences others.

**Implementation**:
- Default quota: **10 Mbps** per guardian
- ARQ includes `bandwidth_bps: int` field
- If `bandwidth_bps > quota` → REJECT

**Failure Mode**:
- Reject with `BANDWIDTH_EXCEEDED`
- Guardian can retry with lower bandwidth

**Why Universal**:
- If one guardian uses 50 Mbps, others suffer degraded video/audio
- Ubuntu philosophy: "I am because we are" requires equal participation
- **Categorical Imperative**: "Resource allocation must be fair" ensures consensus

**Technical Note**:
- 10 Mbps supports: 720p video (2-3 Mbps) + high-quality audio (128 kbps)
- Headroom for packet loss, network jitter

---

## Admission Gates

### Gate Sequence (Execute in Order)

```python
def h323_admission_request(arq: AdmissionRequest) -> AdmissionResponse:
    # Gate 1: Verify Ed25519 signature (Imperative 1: Authenticity)
    canonical = arq.to_canonical()
    if not verify_signature(canonical, arq.signature, arq.public_key):
        return AdmissionReject(reason="INVALID_SIGNATURE")

    # Gate 2: Check guardian registry (Imperative 2: Anti-Sybil)
    if not guardian_registry.is_registered(arq.terminal_id):
        return AdmissionReject(reason="NOT_REGISTERED")

    # Gate 2.1: Verify public key matches registry
    registered_key = guardian_registry.get_public_key(arq.terminal_id)
    if registered_key != arq.public_key:
        return AdmissionReject(reason="INVALID_SIGNATURE")  # Key mismatch

    # Gate 3: Kantian PII constraint (Imperative 3: PII Protection)
    if arq.call_type == CallType.ESCALATE and arq.has_pii:
        return AdmissionReject(reason="PII_POLICY_VIOLATION")

    # Gate 4: Bandwidth quota (Imperative 4: Fairness)
    quota = guardian_registry.get_bandwidth_quota(arq.terminal_id)
    if arq.bandwidth_bps > quota:
        return AdmissionReject(reason="BANDWIDTH_EXCEEDED")

    # All gates passed → ACF (Admission Confirm)
    witness.log(arq)
    return AdmissionConfirm(call_id=..., mcu_address="if://service/guard/mcu:1720")
```

### Gate Failure Handling

| Gate | Failure Reason | Recovery |
|------|---------------|----------|
| **Gate 1** | `INVALID_SIGNATURE` | Regenerate signature with correct private key |
| **Gate 2** | `NOT_REGISTERED` | Admin adds guardian to registry |
| **Gate 2.1** | `INVALID_SIGNATURE` | Correct public key mismatch (security incident) |
| **Gate 3** | `PII_POLICY_VIOLATION` | Remove PII, set `has_pii=false`, retry |
| **Gate 4** | `BANDWIDTH_EXCEEDED` | Reduce bandwidth request, retry |

**Non-Recoverable**:
- `INVALID_SIGNATURE` (if signature forged) → Permanent reject
- `NOT_REGISTERED` (if terminal malicious) → Never add to registry

---

## Policy Constraints

### Call Types

| Call Type | PII Allowed? | Bandwidth Priority | Use Case |
|-----------|--------------|-------------------|----------|
| **ROUTINE** | ✅ Yes | Normal | Regular deliberation |
| **ESCALATE** | ❌ No (Imperative 3) | Normal | High-stakes decisions |
| **EMERGENCY** | ⚠️ Yes (override) | High | Crisis response (life/death) |

**ESCALATE Constraint**:
- Triggered when decision affects >1,000 people OR >$1M economic impact
- PII forbidden to prevent bias
- Example: Dossier 07 (Civilizational Collapse) was ESCALATE call

**EMERGENCY Override**:
- PII allowed (e.g., natural disaster response: "Hospital at 123 Main St needs supplies")
- Bandwidth priority (ensure critical info delivered)
- Logged to IF.witness with `emergency_override: true`

### Bandwidth Tiers

| Guardian Role | Quota (Mbps) | Justification |
|---------------|--------------|---------------|
| **Core Guardians** (6) | 10 | Standard video + audio |
| **Specialist Guardians** (4) | 10 | Equal participation |
| **Emergency Services** | 20 | Override for crisis (e.g., real-time video feed) |

**Default**: 10 Mbps for all guardians (fairness)

**Override Mechanism**:
- `guardian-registry.yaml`: `bandwidth_quota_bps: 20_000_000`
- Requires IF.guard approval (logged)

### Capacity Limits

| Limit | Value | Reason |
|-------|-------|--------|
| **Max Guardians** | 25 | MCU processing capacity |
| **Max Concurrent Calls** | 3 | Prevent fragmentation (one primary council) |
| **Max Call Duration** | 4 hours | Prevent burnout (deliberation fatigue) |

**Overflow Handling**:
- If 26th guardian tries to join: `ARJ (CAPACITY_EXCEEDED)`
- Waitlist mechanism (future): Queue guardians, admit when slot available

---

## ESCALATE Triggers

### Conditions for ESCALATE Call

An ESCALATE call is triggered when:
1. **Hazard Severity**: Dossier involves civilizational-scale risk
2. **Population Impact**: Decision affects >1,000 people
3. **Economic Impact**: Decision involves >$1M
4. **Precedent Setting**: Creates new governance rule (IF.constitution)
5. **Contrarian Veto**: >95% approval triggers 2-week cooling-off (Contrarian Guardian forces ESCALATE)

**Example Triggers**:
- Dossier 07: Civilizational Collapse (5,000 years of data, affects all AI systems)
- IF.chase: Police pursuit policy (affects 3,300+ deaths over 6 years)
- IF.yologuard: Secret redaction (affects all code repositories)

### ESCALATE-Specific Rules

**PII Prohibition**:
- No personal names, addresses, phone numbers, emails
- Use aggregate statistics instead ("34% of workers" not "John Smith")
- Citations must be anonymized (e.g., "Plaintiff A" in legal cases)

**Evidence Requirements**:
- All claims backed by IF.citation (verified sources)
- Minimum 2 independent sources per claim
- IF.witness audit trail required

**Voting Rules**:
- 75% supermajority (not simple majority)
- Contrarian Guardian veto power (if approval >95%)
- 30-day cooling-off period before implementation

---

## Rejection Reasons

### ARJ (Admission Reject) Codes

| Code | Meaning | Guardian Action | Gatekeeper Action |
|------|---------|-----------------|-------------------|
| **INVALID_SIGNATURE** | Ed25519 verification failed | Regenerate signature | Log to IF.witness, reject |
| **NOT_REGISTERED** | Terminal not in registry | Contact admin | Permanent reject |
| **PII_POLICY_VIOLATION** | PII in ESCALATE call | Remove PII, retry | Log to IF.witness, reject |
| **BANDWIDTH_EXCEEDED** | Quota >10 Mbps | Lower bandwidth, retry | Suggest lower bandwidth |
| **CAPACITY_EXCEEDED** | MCU full (>25 guardians) | Wait for slot | Add to waitlist (future) |
| **GATEKEEPER_ERROR** | Internal error | Retry after 30 sec | Log error, investigate |

### Audit Trail

Every rejection logged to IF.witness:
```json
{
  "msg_type": "ARJ",
  "timestamp": "2025-11-11T14:32:17.234Z",
  "data": {
    "call_id": "epic-2025-11-11-abc",
    "terminal_id": "if://guardian/technical",
    "reject_reason": "PII_POLICY_VIOLATION",
    "arq_hash": "sha256:7b4c3d2e1f..."
  },
  "hash": "sha256:9c0d1e2f..."
}
```

**Reviewable by**:
- Guardian Council (transparency)
- IF.guard (governance oversight)
- External auditors (compliance)

---

## Philosophical Grounding

### Kant's Formula of Universal Law

> "Act only according to that maxim whereby you can, at the same time, will that it should become a universal law."

**Application**:
- **Maxim**: "I will bypass signature verification to join conference quickly."
- **Universal Law**: "All guardians bypass signature verification."
- **Consequence**: Impersonation becomes possible, system collapses.
- **Conclusion**: Maxim fails universality test → Categorical Imperative enforces signatures

### Kant's Formula of Humanity

> "Act in such a way that you treat humanity, whether in your own person or in the person of any other, never merely as a means to an end, but always at the same time as an end."

**Application**:
- **PII in ESCALATE**: Using "John Smith" as example treats John as *means* (rhetorical device)
- **Aggregate Data**: "34% of workers" treats population as *end* (understanding systemic issue)
- **Conclusion**: PII prohibition respects human dignity

### Ubuntu Philosophy

> "I am because we are."

**Application**:
- **Centralized Audio Mixing**: Everyone hears everyone (communal consensus)
- **Bandwidth Fairness**: Equal resource access (no individual dominates)
- **Continuous Presence Video**: Visual equality (4x4 grid, same size tiles)
- **Conclusion**: Technical architecture embodies Ubuntu philosophy

### Wu Lun (五倫): Five Relationships

**君臣 (Ruler-Subject)**:
- Gatekeeper = Ruler (authority to admit/reject)
- Guardian = Subject (requests permission)
- **Duty**: Gatekeeper enforces rules impartially (no favoritism)

**朋友 (Friend-Friend)**:
- Once admitted, guardians are peers (no hierarchy in MCU)
- **Duty**: Speak truthfully, listen respectfully (deliberation ethics)

---

## Policy Evolution

### Amendment Process

Kantian policies can evolve through **IF.constitution**:
1. **Evidence Gathering**: 100+ incidents analyzed
2. **Pattern Recognition**: Root cause identified
3. **Proposal**: New policy drafted (e.g., "Imperative 5: Anti-Deepfake")
4. **Guardian Vote**: 75% supermajority required
5. **Implementation**: Code updated, gatekeeper restarted

**Example Evolution**:
- Current: 4 categorical imperatives (signature, registry, PII, bandwidth)
- Future: Imperative 5 (anti-deepfake): "Never admit synthetic video without disclosure"

### Historical Precedents

| Policy | Added | Trigger | Status |
|--------|-------|---------|--------|
| **Imperative 1** (Signatures) | 2025-11-11 | Initial design | ✅ Active |
| **Imperative 2** (Registry) | 2025-11-11 | Sybil attack prevention | ✅ Active |
| **Imperative 3** (PII) | 2025-11-11 | Dossier 07 (ESCALATE) | ✅ Active |
| **Imperative 4** (Bandwidth) | 2025-11-11 | Fairness principle | ✅ Active |
| **Imperative 5** (Anti-Deepfake) | TBD | First deepfake incident | 🚧 Proposed |

---

## Compliance & Validation

### EU AI Act Article 10

**Traceability Requirements**:
- ✅ All ARQ/ACF/ARJ logged (IF.witness)
- ✅ Policy gates explicit in code
- ✅ Rejection reasons documented
- ✅ Audit trail immutable (SHA-256 + Merkle)

### IF.TTT Framework

**Traceable**:
- Every admission decision → IF.witness log
- Policy gates → source code (`h323_gatekeeper.py:285-315`)
- Rejection reasons → enumerated codes

**Transparent**:
- Policy rules public (this document)
- Guardian registry public (anonymized roles)
- Audit logs replayable

**Trustworthy**:
- Ed25519 cryptographic verification (not policy compliance)
- Gatekeeper cannot forge signatures
- IF.witness cannot retroactively modify logs

---

## Summary: The Four Gates

```
┌────────────────────────────────────────────────────────────┐
│                    Admission Request (ARQ)                  │
└───────────────────────────┬────────────────────────────────┘
                            │
                            ↓
┌────────────────────────────────────────────────────────────┐
│  Gate 1: Authenticity (Ed25519 Signature)                  │
│  "Never admit without cryptographic proof of identity"     │
│  ✓ Signature valid → Continue                              │
│  ✗ Signature invalid → ARJ (INVALID_SIGNATURE)             │
└───────────────────────────┬────────────────────────────────┘
                            │
                            ↓
┌────────────────────────────────────────────────────────────┐
│  Gate 2: Anti-Sybil (Guardian Registry)                    │
│  "Never admit an unregistered terminal"                    │
│  ✓ In registry → Continue                                  │
│  ✗ Not in registry → ARJ (NOT_REGISTERED)                  │
└───────────────────────────┬────────────────────────────────┘
                            │
                            ↓
┌────────────────────────────────────────────────────────────┐
│  Gate 3: PII Protection (ESCALATE Constraint)              │
│  "Never allow PII in high-stakes decisions"                │
│  ✓ No PII OR call_type ≠ ESCALATE → Continue               │
│  ✗ PII AND call_type == ESCALATE → ARJ (PII_VIOLATION)     │
└───────────────────────────┬────────────────────────────────┘
                            │
                            ↓
┌────────────────────────────────────────────────────────────┐
│  Gate 4: Fairness (Bandwidth Quota)                        │
│  "Never exceed resource quota (10 Mbps)"                   │
│  ✓ Bandwidth ≤ quota → ACF (Admission Confirmed)           │
│  ✗ Bandwidth > quota → ARJ (BANDWIDTH_EXCEEDED)            │
└───────────────────────────┬────────────────────────────────┘
                            │
                            ↓
                   ACF → MCU Connection
```

---

## References

**Philosophy**:
- Kant, I. (1785). *Groundwork for the Metaphysics of Morals*
- Tutu, D. (1999). *No Future Without Forgiveness* (Ubuntu philosophy)

**InfraFabric**:
- IF-vision.md: Guardian Council architecture
- SWARM-COMMUNICATION-SECURITY.md: Ed25519 implementation
- H323-GUARD-COUNCIL.md: Technical architecture

**Standards**:
- ITU-T H.323: Multimedia communications
- RFC 8032: Ed25519 signature algorithm
- EU AI Act Article 10: Traceability requirements

---

**Author**: InfraFabric Project
**License**: CC BY 4.0
**Last Updated**: 2025-11-11
