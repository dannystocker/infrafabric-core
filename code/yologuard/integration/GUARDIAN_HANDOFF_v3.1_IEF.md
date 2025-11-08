# IF.guard Guardian Handoff — IF.yologuard v3.1 (IEF + TTT + PQ)

**Date:** 2025-11-08
**Version:** 3.1 (Immuno-Epistemic Forensics Release)
**Decision Required:** APPROVE/REJECT release + adopt governance policies
**Submitter:** Development Team
**Review Council:** IF.guard (6 Core Guardians + Extended Council)

---

## Executive Summary

**Request:** Approve IF.yologuard v3.1 release with:
1. **Immuno-Epistemic Forensics (IEF)** layer - danger signals, structure checks, Indra graph
2. **TTT Framework** (Traceability • Trust • Transparency) - provenance, rationale, manifests
3. **Quantum Readiness (PQ)** analysis - classical crypto detection, Quantum Exposure Scoring
4. **Audience Profiles** - ci/ops/audit/research/forensics with graduated thresholds
5. **Governance Policy** - CI gates, weekly forensics audits, manifest retention

**Status:** All code implemented, validated on Leaky Repo benchmark + public corpus, no breaking changes.

**Key Metric:** 107/96 detections (component-inclusive), 95/96 (usable-only), 42/42 coverage, ~0 FP on falsifiers.

---

## What Changed Since v3.0

### 1. Immuno-Epistemic Forensics (IEF v1)

**Philosophy:** Apply immunology metaphors to secret detection - innate/adaptive, danger signals, antigen presentation.

**Implementation:**

- **Danger Signals** (innate immunity):
  - `encoded_blob_in_text`: Long Base64-like blocks that may hide exfiltration vectors
  - `honeypot_marker`: Detection of "canary", "honeypot", "honeytoken" strings (may indicate traps)

- **Structure Checks** (Formality-Conserving Proofs, no live validation):
  - `jwt_struct_valid`: JWT header/payload JSON parsing (structure only, no signature verification)
  - `pem_block`: PEM certificate/key block presence detection

- **APC Packet** (Antigen Presentation Cell):
  - Each detection bundles: provenance (repoCommit, fileSha256, scanTimestamp) + relations + dangerSignals
  - Enables downstream "T-cell" logic (guardian gates, severity boosts)

- **Indra's Net Graph** (`--graph-out`):
  - Nodes: files, antigens (secrets)
  - Edges: `contains` (file→antigen), `relation` (antigen→antigen), `danger` (antigen→signal)
  - Future: Severity boosts when relation triangles close (key+endpoint+config)

**Files:** `src/IF.yologuard_v3.py:257-350, 565-690`

**Safety:** No live validations, no data exfiltration, no network calls. Read-only structure analysis.

---

### 2. TTT (Traceability • Trust • Transparency)

**Principle:** Every detection must be auditable, every run must be reproducible.

**Implementation:**

- **Provenance** (per detection):
  ```json
  {
    "repoCommit": "a3f7b2c",
    "fileSha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "scanTimestamp": "2025-11-08T04:30:00Z"
  }
  ```

- **Rationale** (per detection):
  ```json
  {
    "pattern": "AWS_SECRET_REDACTED",
    "classification": "usable",
    "relations": ["user-password", "metadata-sibling"],
    "relation_score": 0.85,
    "always_error": true,
    "thresholds": {"error": 0.75, "warn": 0.5},
    "two_source": false
  }
  ```

- **Manifest** (`--manifest <file>`):
  - Records: config (thresholds, mode, profile), inputs (files scanned, skipped), results (detections, usable/components)
  - Includes: quantum summary (classicalUse, pqUse, avgExposureScore)
  - Machine-readable, timestamped, suitable for evidence chains

**Files:** `src/IF.yologuard_v3.py:690-850`

**Use Case:** Compliance audits, incident forensics, reproducibility verification.

---

### 3. Quantum Readiness (PQ v1)

**Motivation:** Post-quantum cryptography transition is imminent. Organizations need to know their quantum exposure.

**Detection Approach:**

**Classical Algorithms (vulnerable):**
- Public key: RSA, ECDSA, ECDH, X25519, DSA
- Symmetric: AES-128 (Grover's algorithm vulnerability)
- Hashing: SHA-1, MD5 (quantum collision attacks)
- Protocols: TLS 1.2 and earlier

**PQ Hints (quantum-resistant):**
- KYBER, DILITHIUM, FALCON, SPHINCS+
- liboqs, OQS mentions
- TLS 1.3 with PQ extensions

**Quantum Exposure Score (QES):**
- Range: 0-100
- Drivers:
  - Classical public key use (+30)
  - AES-128 (+10)
  - SHA1/MD5 (+10)
  - Usable secret (+20)
  - Relational context (+10)
  - Long-lived data hints (backup/archive/dump keywords) (+20)
  - PQ presence (-dampens by 50%)

**Outputs:**
- Per-detection: `pqRisk: {algorithms, keySize, protocols, qes: {score, drivers}}`
- Repo-level: `--pq-report <file>` with classicalUse/pqUse counts, exposureScores[], avgExposureScore

**Example QES:**
```json
{
  "score": 40,
  "drivers": ["classical_public_key", "usable_secret"]
}
```

**Files:** `src/IF.yologuard_v3.py:565-650, 850-900`

**Use Case:** Quantum migration planning, risk prioritization, compliance (NIST PQC mandates).

---

### 4. Audience Profiles

**Problem:** One threshold doesn't fit all use cases. CI needs low noise, forensics needs max sensitivity.

**Solution:** Pre-configured profiles.

| Profile | Mode | Error | Warn | Max File | Use Case |
|---------|------|-------|------|----------|----------|
| **ci** | usable | 0.80 | 0.60 | 5 MB | PR gates, minimal noise |
| **ops** | both | 0.75 | 0.50 | 10 MB | Daily scanning, balanced |
| **audit** | both | 0.70 | 0.40 | 20 MB | Compliance reviews, broad |
| **research** | both | 0.60 | 0.35 | 100 MB | Academic benchmarks, max recall |
| **forensics** | both | 0.65 | 0.45 | 50 MB | Incident response, IEF enabled |

**Usage:** `--profile forensics` sets all related flags automatically.

**Files:** `src/IF.yologuard_v3.py:700-715`

---

## Current Performance (Verified)

### Leaky Repo Benchmark (Standard Dataset)
```
Component-inclusive: 107/96 (111.5%)
Usable-only:         95/96  (98.96%)
File coverage:       42/42  (100%)
Scan time:           ~0.4s
False positives:     0 (on falsifier tests)
```

### Public Corpus Survey (2 repos, shallow clone)
```
Repos:           psf/requests, pallets/flask
Total files:     349
Detections:      73 (includes test fixtures)
Avg files/sec:   ~454
```

### Performance (infrafabric repo)
```
Files scanned:   471
Bytes scanned:   13.65 MB
Duration:        4.04s
Files/sec:       116.55
MB/sec:          3.55
```

### Quantum Readiness (Leaky Repo)
```
Classical use:   {rsa: 2, ...}
PQ hints:        {liboqs: 1}
Avg QES:         26.7
High-risk:       3 secrets with QES ≥40
```

**Artifacts:** `code/yologuard/reports/20251108T020047Z/`, `code/yologuard/reports/20251108T020506Z/`

---

## Benefits

### 1. Security Benefits
- **Danger signals** detect encoded exfiltration attempts and honeypot markers
- **PQ analysis** enables quantum migration planning before "Y2Q" deadline
- **Forensics mode** provides incident response-grade context (provenance, graph, structure checks)
- **Profiles** reduce noise in CI while maintaining max sensitivity for audits

### 2. Governance Benefits
- **TTT manifests** provide audit trails for compliance (SOC2, ISO27001, PCI-DSS)
- **Rationale capture** enables explainability for security findings
- **Provenance tracking** supports incident forensics and root cause analysis
- **Guardian gates** enforce two-source journalism principles (require validation before blocking)

### 3. Operational Benefits
- **Profiles** eliminate manual threshold tuning per environment
- **SARIF integration** works with GitHub Advanced Security, GitLab, Azure DevOps
- **Graph output** enables visualization and relationship analysis
- **Quantum reports** provide actionable migration roadmaps

### 4. Research Benefits
- **Immuno-epistemic framework** opens new detection paradigms (adaptive memory, clonal selection)
- **Indra graph** enables network-based severity scoring
- **Benchmark transparency** supports reproducibility and peer review

---

## Risks & Mitigations

### 1. Sensitivity / Noise
**Risk:** Forensics mode may surface too many signals for daily use.
**Mitigation:** Use `--profile ci` for PR gates (usable-only, conservative thresholds). Reserve forensics for weekly audits.

### 2. Heuristic Thresholds
**Risk:** QES scores and severity thresholds are heuristics, not empirically fitted.
**Mitigation:** Document as heuristics in README. Commit to calibration using curated clean corpus within 2-4 weeks. Provide tuning flags.

### 3. Structure Checks Are Not Proofs
**Risk:** `jwt_struct_valid` and `pem_block` are pattern-based, not cryptographic validation.
**Mitigation:** Name them "structure checks", not "validity checks". Document safety constraints (no live validation). Future: Add FCP (Formality-Conserving Proofs) for rigorous verification.

### 4. PQ Detection is String-Based (v1)
**Risk:** May miss PQ libraries if not mentioned in strings. May false-positive on comments/docs.
**Mitigation:** SBOM integration assists best-effort. Document as v1 (pattern-based). Future: Parser-based AST analysis and library version checks.

### 5. Cross-File Relationships Not Yet Implemented
**Risk:** Graph doesn't link `.env` → `config.yml` references.
**Mitigation:** Acknowledged in docs. Roadmap item for v3.2. Current graph still provides value for single-file context.

---

## Safeguards

### 1. Kantian Duty Constraints (Non-Negotiable)
- ✅ No live validation of secrets (no network calls, no crypto ops)
- ✅ Always redact secrets in output (never log plaintext)
- ✅ No data exfiltration (read-only, local scanning only)
- ✅ Respect privacy (no upload without explicit consent)

### 2. Falsifier Tests
- ✅ UUIDs, git SHAs, benign Base64 → 0 detections
- ✅ `tests/test_falsifiers.py` must pass before release

### 3. CI Gates
- ✅ Benchmark must detect ≥95 secrets
- ✅ File coverage must be 42/42
- ✅ Falsifier tests must pass
- ✅ `.github/workflows/yologuard-ci.yml` enforces

### 4. Guardian Review
- ✅ This handoff requires IF.guard approval
- ✅ Contrarian Guardian can veto with 2-week cooling-off

### 5. Manifest Retention
- ✅ All runs produce machine-readable manifests
- ✅ Forensics runs retain manifests + SARIF + graphs for audit
- ✅ Provenance enables incident traceability

---

## Governance Policy Proposal

### 1. CI Integration (`--profile ci`)
- **Gate:** Block on ERROR severity:
  - Always-error patterns (private keys, passwords, JWT tokens)
  - Validated two-source items (relationship_score ≥0.80 + usable)
- **Log:** WARN items for review, but don't block
- **Manifest:** Required for all CI runs, retained 90 days
- **SARIF:** Upload to GitHub Code Scanning

### 2. Weekly Forensics Audits (`--profile forensics`)
- **Schedule:** Every Sunday 02:00 UTC
- **Outputs:** JSON, SARIF, Indra graph, TTT manifest, PQ report
- **Retention:** 1 year for compliance
- **Review:** Security team reviews PQ trends, danger signals, new relationship patterns

### 3. Threshold Governance
- **Initial:** error=0.75, warn=0.5 (CI); error=0.65, warn=0.45 (forensics)
- **Tuning:** Quarterly review based on FP corpus runs
- **Override:** Teams can tune per-repo via `.yologuard.yml` config (future)

### 4. Quantum Readiness
- **Baseline:** Establish org-level QES threshold (e.g., avg ≤30)
- **Alert:** PR adds new classical crypto to sensitive paths (secrets/, config/, .env) → manual review
- **Planning:** Use PQ reports to prioritize migration (high QES secrets first)

### 5. Manifest Auditing
- **Compliance:** SOC2/ISO27001 auditors can request manifests by date range
- **Forensics:** Incident response team uses provenance to trace secret exposure timeline
- **Trends:** Monthly report on detections, usable/components ratio, quantum exposure

---

## Evidence

### 1. Code Implementation
- **IEF layer:** `src/IF.yologuard_v3.py:257-690`
- **TTT framework:** `src/IF.yologuard_v3.py:690-850`
- **PQ analysis:** `src/IF.yologuard_v3.py:850-900`
- **Profiles:** `src/IF.yologuard_v3.py:700-715`

### 2. Validation Artifacts
- **Benchmark:** `benchmarks/run_leaky_repo_v3_philosophical_fast_v2.py`
- **Falsifiers:** `tests/test_falsifiers.py`
- **CI workflow:** `.github/workflows/yologuard-ci.yml`
- **Reports:** `code/yologuard/reports/20251108T*/`

### 3. Documentation
- **IEF/TTT/PQ:** This handoff
- **Benchmarks:** `code/yologuard/docs/BENCHMARKS.md`
- **Comparison:** `code/yologuard/docs/COMPARISON.md`
- **Harness:** `code/yologuard/harness/README.md`

### 4. External Validation
- **GPT-5 package:** `VALIDATION_PACKAGE_FOR_GPT5.md`
- **Quick start:** `GPT5_HANDOFF.md`
- **Bug disclosure:** `QUICK_SUMMARY.md`

---

## Roadmap Commitments (v3.2)

### 1. Empirical Calibration (2-4 weeks)
- Curate clean corpus (100 public repos)
- Run FP analysis, measure precision
- Tune thresholds based on data
- Publish calibration report

### 2. Enhanced IEF (4-6 weeks)
- Add stylometry_delta to danger signals (authorship shifts)
- Git history anomalies (file author changes, suspicious timestamps)
- Indra severity boosts (relation triangle closure)
- Forgeries toolkit (EXIF/C2PA heads-up for media files)

### 3. SBOM-Aware PQ (6-8 weeks)
- Parse CycloneDX/SPDX SBOMs
- Version-aware library checks (e.g., OpenSSL 3.0 PQ support)
- Dependency graph integration
- Vulnerability cross-reference (CVE lookup for quantum-vulnerable libs)

### 4. Cross-File Relationships (8-10 weeks)
- Link `.env` → `config.yml` references
- Template interpolation detection (${VAR}, {{var}}, %VAR%)
- Multi-file relationship scoring
- Graph-based severity propagation

---

## Decision Request

**APPROVE** IF.yologuard v3.1 release with:

1. ✅ **IEF layer** enabled via `--forensics` and `--profile forensics`
2. ✅ **TTT framework** with provenance, rationale, manifests
3. ✅ **PQ analysis** with `--pq-report` and Quantum Exposure Scoring
4. ✅ **Profiles** (ci/ops/audit/research/forensics) for graduated sensitivity
5. ✅ **Governance policy** as outlined above (CI gates, weekly audits, manifest retention)

**Commitments:**
- Calibrate thresholds within 2-4 weeks using curated clean corpus
- Deliver v3.2 roadmap items within 10 weeks
- Maintain falsifier tests, CI gates, and guardian review for all releases

**Alternatives Considered:**
- Ship without IEF/PQ → Rejected: Market differentiation requires advanced features
- Wait for cross-file relationships → Rejected: Single-file relationships already provide value
- Skip profiles → Rejected: One-size threshold doesn't fit all use cases

---

## Guardian Questions for Deliberation

1. **Transparency Guardian:** Is the TTT framework sufficient for audit compliance? Are manifests machine-readable enough?

2. **Safety Guardian:** Are the Kantian duty constraints adequately enforced? Is the "no live validation" rule clear?

3. **Epistemic Guardian:** Are the heuristics (QES, thresholds) documented honestly? Is the calibration commitment credible?

4. **Contrarian Guardian:** What could go wrong? Are we over-engineering? Is the immunology metaphor obscuring simplicity?

5. **Ethics Guardian:** Does PQ analysis create undue alarm? Are we framing quantum risk responsibly?

6. **Action Guardian:** Is the governance policy actionable? Can teams actually use the profiles without confusion?

---

## Recommended Decision

**APPROVE** with conditions:

1. ✅ Release v3.1 with all features enabled
2. ⚠️ **Require:** Calibration report within 4 weeks (not optional)
3. ⚠️ **Require:** User docs update explaining profiles, IEF, PQ for non-technical stakeholders
4. ⚠️ **Monitor:** Weekly forensics runs for first month, adjust thresholds if noise is excessive
5. ⚠️ **Review:** 30-day retrospective on adoption, FP rates, and governance policy effectiveness

**Dissent Window:** 2 weeks for Contrarian Guardian to raise substantive objections.

---

**Submitted:** 2025-11-08
**Decision Required By:** 2025-11-10
**Implementation Target:** 2025-11-11 (pending approval)

---

**Attachments:**
- Guardian deliberation script: `integration/guardian_handoff.py`
- Decision JSON: `integration/guardian_handoff_result.json`
- Latest reports: `code/yologuard/reports/20251108T*/`
