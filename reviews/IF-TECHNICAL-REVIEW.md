# IF-TECHNICAL-REVIEW.md

**Generated:** 2025-11-12
**Reviewer:** Production readiness assessment
**Branch:** claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

---

## Executive Summary

InfraFabric's core architecture (IF.connect → IF.guard → IF.witness + S²) is well-conceived and matches the project's philosophy (verificationism, provenance, falsifiability, Ubuntu). The single largest **execution risk** is the **Phase-0 CLI/control-plane** not being production-ready for 116+ integrations; without it, policy, traceability, and safe rollout discipline will fragment across ad-hoc scripts.

**Top call:** Build **Phase-0 CLI** and adopt **IF.connect v2.1** (replay-safe envelopes + hazard gates) **before expanding provider integrations**.

### TTT Anchors

- *What to evaluate (your own brief):* `COMPREHENSIVE-EVAL-PROMPT.md`.
  **TTT:** repo:/COMPREHENSIVE-EVAL-PROMPT.md
- *Branch/overview:* `BRANCH-SUMMARY-FOR-REVIEW.md`.
  **TTT:** repo:/BRANCH-SUMMARY-FOR-REVIEW.md
- *CLI concerns:* `CLI-ARCHITECTURE-GAPS-AND-PLAN.md`.
  **TTT:** repo:/CLI-ARCHITECTURE-GAPS-AND-PLAN.md
- *Integrations plan (116+):* `INTEGRATION-ROADMAP-POST-GPT5-REVIEW.md`.
  **TTT:** repo:/INTEGRATION-ROADMAP-POST-GPT5-REVIEW.md
- *S² design:* `docs/SWARM-OF-SWARMS-ARCHITECTURE.md`.
  **TTT:** repo:/docs/SWARM-OF-SWARMS-ARCHITECTURE.md
- *S² critical bugs:* `S2-CRITICAL-BUGS-AND-FIXES.md`.
  **TTT:** repo:/S2-CRITICAL-BUGS-AND-FIXES.md
- *Realtime comms plan:* `docs/IF-REALTIME-COMMUNICATION-INTEGRATION.md`.
  **TTT:** repo:/docs/IF-REALTIME-COMMUNICATION-INTEGRATION.md
- *Current CLI + SIP stubs:* `tools/ifctl.py`, `tools/bus_sip.py`.
  **TTT:** repo:/tools/ifctl.py · repo:/tools/bus_sip.py

---

## A. Architecture Quality

### Strengths

✅ **Clear layering**: **message semantics** (IF.connect) vs **transport** (WebRTC/SIP/H.323).
**TTT:** repo:/docs/IF-REALTIME-COMMUNICATION-INTEGRATION.md

✅ **IF.witness aligns to IF.TTT** (append-only, provenance).
**TTT:** repo:/BRANCH-SUMMARY-FOR-REVIEW.md (§IF.witness overview)

✅ **S² ("Swarm of Swarms") explicit** in docs; rescue/Gang-Up pattern is thoughtfully described.
**TTT:** repo:/docs/SWARM-OF-SWARMS-ARCHITECTURE.md

✅ **Philosophy grounding**: Wu Lun (五倫) relationships map to system components.
**TTT:** repo:/S2-CRITICAL-BUGS-AND-FIXES.md (§Wu Lun Balance Restored)

### Gaps / Missing planks

❌ **Signed Capability Registry** absent in runnable code: dynamic adapters need signature/allow-list + declared scopes.
**TTT:** repo:/INTEGRATION-ROADMAP-POST-GPT5-REVIEW.md (adapters inventory)

❌ **Secrets & cost**: no enforced redaction/rotation or IF.optimise cost hooks in core paths.
**TTT:** repo:/BRANCH-SUMMARY-FOR-REVIEW.md (§cost/observability goals)

❌ **IF.connect envelope**: replay safety (seq/nonce/ttl), hazard category overrides, and scope fields must be enforced.
**TTT:** repo:/COMPREHENSIVE-EVAL-PROMPT.md (security/scalability qs)

❌ **Transport enforcement**: SIPS/TLS admission via IF.guard and witness logging of signaling artifacts not yet wired.
**TTT:** repo:/docs/IF-REALTIME-COMMUNICATION-INTEGRATION.md

❌ **IF.coordinator, IF.governor, IF.chassis** not yet implemented (identified as critical in S2-CRITICAL-BUGS-AND-FIXES.md).
**TTT:** repo:/S2-CRITICAL-BUGS-AND-FIXES.md

---

## B. Code Quality (sampled)

> You noted: `tools/ifctl.py` ~50 LOC (lint-only), `tools/bus_sip.py` ~28 LOC (minimal). Those sizes are consistent with early stubs.

### CLI (`tools/ifctl.py`)

**Current state:**
- Has `argparse` for basic linting
- **Missing**: `--why` (provenance), `--trace` (trace-token), `--mode=falsify` (pre-commit red-team), normalized error codes
- No subcommand family for `capability|talent|message|witness|falsify`

**Required for production:**
```python
# Subcommands needed
if capability list
if capability apply vmix.switcher --scene "Intro" --why "..." --trace --mode=falsify
if talent add --name "Finance.Agent" --role analyst --why "earnings pass"
if talent grant --name Finance.Agent --capability veritas:secrets --why "scan PRs"
if message send --json @frame.json --trace
if witness query --trace-token <uuid>
if falsify --task "..." --mode=pre-commit
```

### SIP adapter (`tools/bus_sip.py`)

**Current state:**
- Minimal INVITE/REGISTER handling
- Not yet anchored to **IF.guard** for admission policies
- Not yet anchored to **IF.witness** for append-only logs

**Required for production:**
- Rate-limits and circuit-breakers for session storms
- SIPS/TLS hard-require
- IF.guard policy enforcement before accepting calls
- IF.witness logging of all signaling events

### `infrafabric/` package (guardians/coordination/manifests)

**Current state:**
- Good separation of concerns on paper

**Required for production:**
1. **Typed config** (pydantic/dataclasses) with schema validation
2. **Uniform error taxonomy** (`IF_ERR_*` codes)
3. **Adapter interface** with consistent `plan/apply/dry_run` and backoff

**Recommended adapter shape:**
```python
class BaseAdapter(Protocol):
    id: str
    limits: dict  # {rps, burst, backoff}

    async def plan(self, intent: dict) -> dict: ...
    async def apply(self, plan: dict, dry_run: bool=False) -> dict: ...
```

---

## C. Integration Design @ 116+ Providers

### What's good

✅ **Clear ambition & coverage** (studio, home automation, chat, payments, SIP, clouds).
**TTT:** repo:/INTEGRATION-ROADMAP-POST-GPT5-REVIEW.md

✅ **Detailed sprint plans** for vMix, OBS, Home Assistant with session allocation.
**TTT:** repo:/VMIX-SPRINT-ALL-SESSIONS.md, repo:/OBS-SPRINT-ALL-SESSIONS.md, repo:/HOME-ASSISTANT-SPRINT-ALL-SESSIONS.md

### What must exist before scale

❌ **Capability Manifest (signed)** per adapter:

```yaml
id: if://capability/vmix.switcher
version: 1.1.0
entrypoint: providers/vmix/adapter.py:VmixAdapter
requires_secrets: [VMIX_HOST, VMIX_PORT]
scopes: [studio:control]
limits: {rps: 3, burst: 6, backoff: [1,2,5,10]}
signature: ed25519:PUBLIC_KEY:SIG
```

❌ **Loader policy**: allow-list by `id@version` + signature; block unsigned.

❌ **Runtime limits**: per-adapter token/API budgets; exponential backoff; circuit breakers.

❌ **Observability**: adapter emits cost counters to IF.optimise; witness tokens per action.

---

## D. Scalability & Observability

### S² at 100+ concurrent sessions needs:

**Event bus** (NATS/Redis Streams) over git polling:
- Current: 30-second git polling creates race conditions and 30,000ms latency
- Required: Real-time event bus with idempotency keys and DLQs
- **TTT:** repo:/S2-CRITICAL-BUGS-AND-FIXES.md (Bug #1)

**Bounded queues** with backpressure & work-stealing:
- Prevent queue exhaustion under load
- Implement fair scheduling across swarms

**Witness store evolution**:
- Current: File-based or SQLite
- Required: SQLite→Postgres for production scale
- Periodic **hash anchors** to object storage for cold-start verification

### SLIs/SLOs needed:

| Metric | Target | Why |
|--------|--------|-----|
| Time-to-decision | p95 < 15s | User experience |
| Escalations % | 1-5% | Quality indicator |
| Duplicate suppression % | >95% | Efficiency |
| Cost per decision | Track & trend | Budget control |
| IF.coordinator latency | <10ms | Real-time coordination |

---

## E. Security Findings (ranked)

| Issue | Severity | Why it matters | What to fix |
|-------|----------|----------------|-------------|
| **Unsigned dynamic plugins** | **CRITICAL** | RCE via malicious adapter | Signed Capability Registry + allow-list loader |
| **Secret handling in code/logs** | **CRITICAL** | Key leakage, compliance risk | Vault, redaction, rotation, deny-listed prints |
| **Replay-unsafe messages** | **HIGH** | Valid replays skew consensus | IF.connect v2.1: `seq`,`nonce`,`ttl`; per-sender monotonic seq |
| **No hazard overrides** | **HIGH** | "Confidence laundering" to dodge human review | `hazards: [legal\|safety\|conflict>20%]` force ESCALATE |
| **DoS via HOLD/ESCALATE storms** | **HIGH** | Queue starvation | Per-agent quotas, HOLD bandwidth caps, triage batching |
| **No rate-limits/circuit-breakers** | **HIGH** | API bans & cost spikes | RPS caps + exponential backoff per adapter |
| **Witness durability** | **MEDIUM** | Audit gaps | DB + periodic anchoring |
| **Git polling race conditions** | **CRITICAL** | Double work, merge conflicts | IF.coordinator with atomic CAS operations |
| **Uncontrolled escalation** | **HIGH** | 57% cost waste, expertise mismatch | IF.governor with capability matching |
| **No sandboxing** | **MEDIUM→CRITICAL** | Noisy neighbor, security breach | IF.chassis with WASM isolation |

**TTT:** repo:/S2-CRITICAL-BUGS-AND-FIXES.md (complete bug analysis)

---

## F. Concrete Patches (copy-paste)

### 1) CLI flags

```bash
# provenance + traceability + pre-commit red-team
if <subcmd> ... --why "business justification" --trace --mode=falsify
```

### 2) IF.connect v2.1 envelope

```json
{
  "id":"msg-uuidv7",
  "performative":"inform",
  "conversation_id":"conv-uuidv7",
  "topic_hash":"sha256:<seed-citations>",
  "sender":"if://agent/Finance.Agent/42",
  "issued_at":"2025-11-12T10:21:00Z",
  "ttl_s":900,
  "seq":142,
  "nonce":"b64...",
  "signature":{
    "algorithm":"ed25519",
    "pubkey":"...",
    "sig":"..."
  },
  "content":{
    "claim_id":"C-00192",
    "scope":{
      "year":2024,
      "includes":["mobile"]
    },
    "evidence":[{
      "type":"filing",
      "url":"...",
      "hash":"sha256:..."
    }],
    "source_diversity":{
      "domain_unique":true,
      "type_mix":["filing","db"]
    },
    "confidence":{
      "raw":0.75,
      "normalized":0.72,
      "basis":["sample:large"]
    },
    "hazards":["conflict>20%"]
  }
}
```

### 3) Routing invariants (bug-class fix)

```python
if "legal" in hazards or "safety" in hazards or "conflict>20%" in hazards:
    return ESCALATE("policy: hazard override")
if conf_norm < 0.20:
    return ESCALATE("low confidence")
elif conf_norm < 0.30:
    return HOLD("borderline; need second source/scope check")
return SHARE()
```

### 4) Signed capability loader (sketch)

```python
def load_cap(manifest):
    # Verify signature
    assert verify_signature(manifest["signature"], manifest_bytes)

    # Check allow-list
    assert manifest["id"] in ALLOWLIST
    assert manifest["version"] in ALLOWLIST[manifest["id"]]

    # Load entrypoint
    return import_entrypoint(manifest["entrypoint"])
```

---

## G. Summary Recommendations

### Immediate (Phase 0 - Weeks 0-3)

1. ✅ Build unified CLI with subcommands (`capability`, `talent`, `message`, `witness`, `falsify`)
2. ✅ Add `--why`, `--trace`, `--mode=falsify` flags to all commands
3. ✅ Implement IF.connect v2.1 envelope (seq, nonce, ttl, hazards, scope)
4. ✅ Create Signed Capability Registry with allow-list loader
5. ✅ Build IF.coordinator (replaces git polling, <10ms latency, atomic CAS)
6. ✅ Build IF.governor (capability matching, budget enforcement, circuit breakers)
7. ✅ Build IF.chassis (WASM sandboxing, resource isolation, SLO tracking)

### Short-term (Weeks 4-8)

8. ✅ Witness backend (SQLite→Postgres) + periodic hash anchors
9. ✅ Rate-limit & circuit-breakers per adapter; backoff `[1,2,5,10,30]`
10. ✅ Event bus (NATS/Redis Streams) to replace git polling; idempotent consumers
11. ✅ Pilot 12 providers with full Phase 0 infrastructure

### Medium-term (Weeks 9-24)

12. ✅ Error taxonomy (`IF_ERR_*`) and common retry envelopes
13. ✅ Typed config (pydantic/dataclasses) with schema validation
14. ✅ Scale to 116+ providers with proper sandboxing and observability

---

## H. Production Readiness Score

| Aspect | Current | Required | Gap |
|--------|---------|----------|-----|
| **CLI** | Stub (lint only) | Full subcommands | **CRITICAL** |
| **Message safety** | Basic | v2.1 (replay-safe) | **HIGH** |
| **Capability registry** | None | Signed manifests | **CRITICAL** |
| **Secrets** | Ad-hoc | Vault + redaction | **CRITICAL** |
| **S² coordination** | Git polling (30s) | IF.coordinator (<10ms) | **CRITICAL** |
| **Resource control** | None | IF.governor + circuit breakers | **HIGH** |
| **Sandboxing** | None | IF.chassis + WASM | **MEDIUM→CRITICAL** |
| **Witness durability** | File/SQLite | Postgres + anchors | **MEDIUM** |
| **Observability** | Basic | Full SLIs/SLOs | **MEDIUM** |

**Overall:** Not production-ready. **Phase 0 required** before scaling to 116+ integrations.

---

**Prepared by:** Production readiness review
**Date:** 2025-11-12
**Recommendation:** Build Phase 0 (6-8 weeks) before expanding integrations
**Risk if skipped:** Race conditions, cost spirals, security breaches (estimated $2,000-5,000 risk)
