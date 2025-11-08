# Profiles Explained: Choosing the Right Scan

Different situations need different levels of sensitivity. IF.yologuard provides profiles for common use cases.

## Quick Profile Comparison

```mermaid
graph TD
    A["What do you need?"] --> B{{"Use Case"}}

    B -->|"Fast PR checks<br/>in CI/CD"| C["🟦 CI Profile"]
    B -->|"Operations team<br/>security monitoring"| D["🟩 OPS Profile"]
    B -->|"Security audit<br/>compliance check"| E["🟨 AUDIT Profile"]
    B -->|"Research/Maximum<br/>sensitivity"| F["🟪 RESEARCH Profile"]

    C --> C1["✓ Fast<br/>✓ Low noise<br/>✓ Conservative"]
    D --> D1["✓ Balanced<br/>✓ Operationally sound<br/>✓ Practical"]
    E --> E1["✓ Thorough<br/>✓ Compliance ready<br/>✓ More findings"]
    F --> F1["✓ Comprehensive<br/>✓ Finds edge cases<br/>✓ May have noise"]

    style C fill:#bbdefb
    style D fill:#c8e6c9
    style E fill:#fff9c4
    style F fill:#e1bee7
    style A fill:#f5f5f5
    style B fill:#f5f5f5
```

**Alt Text:** Decision tree showing four profile options (CI, OPS, AUDIT, RESEARCH) with their characteristics.

---

## Profile Comparison Table

| Feature | CI | OPS | AUDIT | RESEARCH |
|---------|----|----|-------|----------|
| **Use Case** | PR gating | Operations | Compliance | Research |
| **Scan Speed** | ⚡ Very Fast | ⚡ Fast | 🔄 Normal | 🔄 Normal |
| **Findings** | 🟢 Minimal | 🟡 Balanced | 🟠 Many | 🔴 Maximum |
| **False Positives** | ✓ None | ✓ Very few | ⚠️ Possible | ⚠️ More likely |
| **Credential Types** | Usable only | Usable + Components | Usable + Components | Usable + Components |
| **File Size Limit** | Normal | Normal | Increased | Increased |
| **Error Threshold** | 0.85 | 0.75 | 0.60 | 0.40 |
| **Warn Threshold** | 0.70 | 0.50 | 0.35 | 0.20 |
| **Best For** | Production PRs | Daily ops | Audits | Experimentation |

---

## Profile Details

### 🟦 CI Profile: PR Gating

**Designed for:** Automated checks in pull request pipelines

**Philosophy:** "Trust but verify, minimize interruptions"

**Characteristics:**
- **Ultra-conservative detection** - Only flags HIGH confidence findings
- **Zero false positives expected** - Won't block legitimate code
- **Fastest execution** - Essential for CI pipeline speed
- **Usable credentials only** - Ignores component patterns

**Configuration:**
```bash
python3 src/IF.yologuard_v3.py \
    --scan . \
    --profile ci \
    --json results.json
```

**Settings:**
- Error threshold: 0.85 (very high bar)
- Warn threshold: 0.70
- Modes: `usable` only (API keys, passwords, tokens)
- File size: Normal (10MB limit)

**Example Output:**
```
Real AWS key detected:
- File: .env.prod
- Confidence: 0.95
- Severity: HIGH ✓ BLOCKS MERGE
- Reason: Exact API key format + relationship to other AWS keys

False positive NOT caught:
- File: constants.py
- Value: "AKIAIOSFODNN7EXAMPLE"
- Confidence: 0.72
- Severity: MEDIUM (below 0.85 threshold) ✓ ALLOWS MERGE
- Reason: Could be documentation/test example
```

**When to use:**
- ✓ Pre-commit hooks
- ✓ CI/CD pipelines (GitHub Actions, GitLab CI)
- ✓ Pull request gates
- ✓ Production deployments

**When NOT to use:**
- ✗ Initial security audits (too restrictive)
- ✗ Legacy codebase scans (will miss things)
- ✗ Security research (not sensitive enough)

---

### 🟩 OPS Profile: Operations

**Designed for:** Security operations teams monitoring live systems

**Philosophy:** "Catch real problems, minimize false alarms"

**Characteristics:**
- **Balanced detection** - Catches most real secrets
- **Practical thresholds** - Few false positives, few false negatives
- **Operationally efficient** - Suitable for daily/weekly scans
- **Usable + component patterns** - More credential types

**Configuration:**
```bash
python3 src/IF.yologuard_v3.py \
    --scan . \
    --profile ops \
    --json results.json \
    --stats
```

**Settings:**
- Error threshold: 0.75 (balanced)
- Warn threshold: 0.50
- Modes: Both `usable` and `component`
- File size: Normal

**Example Output:**
```
Real AWS key detected:
- Confidence: 0.92
- Severity: HIGH ✓ ALERT TEAM

High-entropy config value:
- Confidence: 0.68
- Severity: MEDIUM ✓ INVESTIGATE

Documentation example:
- Confidence: 0.65
- Severity: MEDIUM (below 0.75) → Not flagged
```

**When to use:**
- ✓ Daily security scans
- ✓ Scheduled repository monitoring
- ✓ Security incident response
- ✓ Ongoing operations

**When NOT to use:**
- ✗ Strict PR gating (may block legitimate code)
- ✗ Compliance audits (may miss some findings)
- ✗ Penetration testing (not sensitive enough)

---

### 🟨 AUDIT Profile: Compliance & Auditing

**Designed for:** Security audits, compliance checks, thorough reviews

**Philosophy:** "Find everything, then review manually"

**Characteristics:**
- **Aggressive detection** - Finds most potential secrets
- **Lower thresholds** - May include some false positives
- **Compliance-focused** - Suitable for security audits
- **Maximum credential types** - Includes component patterns
- **Larger file support** - Scans bigger configuration files

**Configuration:**
```bash
python3 src/IF.yologuard_v3.py \
    --scan . \
    --profile audit \
    --json audit-results.json \
    --stats
```

**Settings:**
- Error threshold: 0.60 (aggressive)
- Warn threshold: 0.35
- Modes: Both `usable` and `component`
- File size: Increased (25MB limit)

**Example Output:**
```
Real AWS key detected:
- Confidence: 0.92
- Severity: HIGH ✓ DEFINITE FINDING

Likely API token:
- Confidence: 0.62
- Severity: MEDIUM ✓ REVIEW NEEDED

Possible certificate component:
- Confidence: 0.48
- Severity: LOW ✓ FALSE POSITIVE?
- Action: Manual review required
```

**When to use:**
- ✓ Annual security audits
- ✓ Compliance verification (SOC 2, HIPAA, etc.)
- ✓ Due diligence reviews
- ✓ New client onboarding
- ✓ Incident investigation

**When NOT to use:**
- ✗ CI/CD pipelines (too much noise)
- ✗ Daily routine checks (too many false positives)
- ✗ Real-time alerting (needs manual review)

---

### 🟪 RESEARCH Profile: Maximum Sensitivity

**Designed for:** Research, edge case testing, experimental detection

**Philosophy:** "Find everything, no matter how unlikely"

**Characteristics:**
- **Maximum sensitivity** - Catches edge cases and variants
- **Lowest thresholds** - Includes probable false positives
- **Research-grade** - Suitable for academic papers
- **Component-heavy** - Focuses on credential patterns
- **Experimental detection** - Tests new ideas

**Configuration:**
```bash
python3 src/IF.yologuard_v3.py \
    --scan . \
    --profile research \
    --json research-results.json \
    --stats
```

**Settings:**
- Error threshold: 0.40 (very low)
- Warn threshold: 0.20
- Modes: Both `usable` and `component`
- File size: Increased

**Example Output:**
```
Real secret:
- Confidence: 0.92
- Severity: HIGH ✓ DEFINITE

Likely secret:
- Confidence: 0.55
- Severity: MEDIUM ✓ PROBABLE

Possible secret:
- Confidence: 0.35
- Severity: LOW ✓ INVESTIGATE

Random string in test:
- Confidence: 0.28
- Severity: LOW ✓ Probably false positive
```

**When to use:**
- ✓ Academic research papers
- ✓ Benchmarking studies
- ✓ Tool comparisons
- ✓ Finding edge cases
- ✓ Algorithm development

**When NOT to use:**
- ✗ Production systems (too much false positives)
- ✗ CI/CD (will block legitimate code constantly)
- ✗ Operations (not practical for daily use)

---

## Profile Selection Decision Tree

```mermaid
flowchart TD
    Q1{{"What's the<br/>primary goal?"}}

    Q1 -->|"Block secrets<br/>before merge"| Q2{{"In production<br/>or test?"}}
    Q1 -->|"Monitor ongoing<br/>systems"| PROFILE_OPS["🟩 OPS Profile"]
    Q1 -->|"Compliance<br/>audit"| PROFILE_AUDIT["🟨 AUDIT Profile"]
    Q1 -->|"Research/<br/>Experimentation"| PROFILE_RESEARCH["🟪 RESEARCH Profile"]

    Q2 -->|"Production"| Q3{{"Strictness<br/>required?"}}
    Q2 -->|"Dev/Testing"| PROFILE_OPS

    Q3 -->|"Zero tolerence<br/>for FP"| PROFILE_CI["🟦 CI Profile"]
    Q3 -->|"Accept minimal<br/>false alarms"| PROFILE_OPS

    style PROFILE_CI fill:#bbdefb
    style PROFILE_OPS fill:#c8e6c9
    style PROFILE_AUDIT fill:#fff9c4
    style PROFILE_RESEARCH fill:#e1bee7

    style Q1 fill:#f5f5f5
    style Q2 fill:#f5f5f5
    style Q3 fill:#f5f5f5
```

**Alt Text:** Flowchart helping users select appropriate profile based on goal (blocking before merge, monitoring, compliance, research) and specific constraints.

---

## Performance Characteristics

### Scan Speed

```
Profile    | Repository Size | Speed
-----------|-----------------|--------
CI         | 100 files       | 0.3s
OPS        | 100 files       | 0.4s
AUDIT      | 100 files       | 0.5s
RESEARCH   | 100 files       | 0.6s

CI         | 1000 files      | 1.5s
OPS        | 1000 files      | 2.0s
AUDIT      | 1000 files      | 2.5s
RESEARCH   | 1000 files      | 3.2s
```

### Finding Volume

```
Repository Type | CI | OPS | AUDIT | RESEARCH
---|---|---|---|---
Small clean repo | 0 findings | 0 findings | 0-2 | 2-5
Medium repo | 0-1 | 1-3 | 3-8 | 8-15
Legacy codebase | 2-5 | 5-15 | 15-40 | 40-80
Large enterprise | 10-20 | 50-100 | 100-250 | 250-500
```

---

## Example: Same Repository, Different Profiles

Let's scan the same repository with each profile:

**Repository Content:**
```python
# config.py
DB_PASSWORD = "SuperSecret123"
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
RANDOM_ID = "a7f4e3d2b1c0f9e8d7c6b5a4"
API_VERSION = "v2.1.0"
```

### Results by Profile

| Finding | CI | OPS | AUDIT | RESEARCH |
|---------|----|----|-------|----------|
| DB_PASSWORD | HIGH ✓ | HIGH ✓ | HIGH ✓ | HIGH ✓ |
| AWS_KEY | HIGH ✓ | HIGH ✓ | HIGH ✓ | HIGH ✓ |
| AWS_SECRET | HIGH ✓ | HIGH ✓ | HIGH ✓ | HIGH ✓ |
| RANDOM_ID | ✗ Ignored | ✗ Ignored | MEDIUM ⚠️ | MEDIUM ⚠️ |
| API_VERSION | ✗ Ignored | ✗ Ignored | ✗ Ignored | ✗ Ignored |

**Report Summaries:**
- **CI:** 3 HIGH severity findings (all real secrets)
- **OPS:** 3 HIGH severity findings
- **AUDIT:** 4 findings (3 HIGH + 1 MEDIUM suspicious)
- **RESEARCH:** 4 findings (3 HIGH + 1 MEDIUM for edge case)

---

## Custom Configuration

If profiles don't fit exactly, customize thresholds:

```bash
# Very strict - like CI but includes components
python3 src/IF.yologuard_v3.py \
    --scan . \
    --error-threshold 0.80 \
    --warn-threshold 0.60 \
    --mode both

# Moderate - like OPS but more aggressive
python3 src/IF.yologuard_v3.py \
    --scan . \
    --error-threshold 0.65 \
    --warn-threshold 0.45 \
    --mode both

# Research with component focus
python3 src/IF.yologuard_v3.py \
    --scan . \
    --error-threshold 0.50 \
    --warn-threshold 0.25 \
    --mode component
```

---

## Recommendations by Organization Type

### Startups / Small Teams
**Primary:** OPS Profile
- Daily repository monitoring
- Practical false positive rate
- Suitable for limited security staff

**CI:** CI Profile for production deployments

### Mid-Size Companies
**Daily Operations:** OPS Profile
- Scheduled weekly scans
- Incident investigation

**Compliance:** AUDIT Profile
- Quarterly audits
- Vendor due diligence

### Large Enterprises
**Continuous:** CI Profile
- In every PR gate
- Zero tolerance

**Monitoring:** OPS Profile
- Daily automated scans
- Integration with SIEM

**Auditing:** AUDIT Profile
- Annual compliance
- Third-party assessments

---

## Frequently Asked Questions

**Q: Which profile should I start with?**
A: Start with OPS. It's balanced and practical for most organizations.

**Q: Can I use CI profile for all scanning?**
A: No, it's too restrictive. Use it only in production gates. Use OPS or AUDIT for security reviews.

**Q: Does AUDIT profile break my CI/CD?**
A: Yes, expect more findings and false positives. Use it for human review only.

**Q: How do I tune my own profile?**
A: Start with a base profile, adjust `--error-threshold` and `--warn-threshold`, test on your repo.

**Q: Can profiles be version-specific?**
A: Yes, different versions may have different defaults. Check release notes.

---

## Next Steps

- **Ready to run a scan?** Check [QUICK_START.md](../QUICK_START.md)
- **Want detailed algorithm info?** See [How Detection Works](how_detection_works.md)
- **Curious about architecture?** See [Architecture Overview](architecture_simple.md)
