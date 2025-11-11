# PHILOSOPHY → CODE Examples (InfraFabric)
_Last updated: 2025-11-11T07:38:46Z_

This document shows how philosophical principles map to **concrete code** and **InfraFabric components**. Each snippet is annotated with which IF principle and component it operationalizes.

---

## 1) Verificationism → CI Toolchain Gate (IF.ground: Principle 2; IF.guard)

**Why:** A claim about correctness is meaningful only if the toolchain verifies it.

**Mapping:** Vienna Circle → `ifctl.py` + CI gate.

```yaml
# .github/workflows/ifctl-lint.yml
name: ifctl-lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {{ python-version: '3.11' }}
      - run: python ifctl.py lint   # Fails the build on schema/constitution errors
```

---

## 2) Falsifiability → One-Line Rollback (IF.ground: Principle 7; IF.guard)

**Why:** Scientific claims must be refutable; production changes must be **reversible**.

```ts
// feature-flags.ts
export const ENABLE_EXPERIMENTAL_ROUTING = false; // Reversible switch
```

```ts
// router.ts
if (ENABLE_EXPERIMENTAL_ROUTING) {
  return experimentalRouter(request);
}
return stableRouter(request);
```

---

## 3) Schema Tolerance → Multi-variant Parse (IF.ground: Principle 4; IF.search)

**Why:** Duhem–Quine: multiple schemas can fit the same evidence. Be tolerant.

```ts
type StationSchema = {{ metro_stations?: string[]; metroStations?: string[]; stations?: string[]; }};

export function extractStations(api: StationSchema): string[] {{
  return api.metro_stations || api.metroStations || api.stations || [];
}}
```

---

## 4) Ubuntu Consensus → Guard Gating (IF.guard; IF.ground: Principle 5)

**Why:** “I am because we are.” Gate high-risk actions behind **council consensus**.

```python
# guard_gate.py
def approve(action_votes, quorum=15, approval=0.50, supermajority=0.80):
    present = sum(v is not None for v in action_votes)
    if present < quorum: return "NO-QUORUM"
    rate = sum(1 for v in action_votes if v is True)/present
    if rate >= supermajority: return "ADVISE-PROCEED"
    if rate > approval: return "PROCEED"
    return "VETO"
```

---

## 5) Process Philosophy → Event Witness Log (IF.witness; IF.ground: Principle 8)

**Why:** Reality as process; log **occasions** with provenance.

```yaml
# witness/event-log.yaml (append-only)
- id: evt-0001
  at: 2025-11-11T10:21:00Z
  actor: if://agent/Finance.Agent/42
  claim: "UEFN payout policy updated"
  evidence: ["url:https://devdocs.epicgames.com/...","news:turnXnewsY"]
  signature: "ed25519:..."
```

---

## 6) Indigenous Relationality → Rhizomatic Citations (IF.citation; IF.search)

**Why:** Knowledge as relationships; avoid single roots.

```yaml
# citations/Evidence-Epic-V4.csv (excerpt as YAML for clarity)
- claim_id: C-0002
  sources:
    - type: filing; ref: "10-Q: 2025-Q2"; hash: "sha256:..."
    - type: blog; ref: "Epic Creator Economy 2.0"
    - type: interview; ref: "executive-podcast-2025-09-12"
  coherence_check: true
```

---

## 7) Joe’s Heuristics → Search Pass Filters (IF.search; IF.optimise)

**Why:** Curate “one-of-one” and drop undifferentiated categories.

```yaml
# SWARM.config.v4-epic.yaml (policy overlay)
if.search:
  passes: 8
  filters:
    - name: "differentiation-filter"
      rule: "require unique value vs peers; else drop"
    - name: "private-label-only-when-better"
      rule: "prefer best-in-class unless own label is provably superior"
```
