# Hello W0RLD: End-to-End Secret Detection Trace

This document traces a **real secret detection** through the complete InfraFabric pipeline, from raw log file to guardian review decision.

## Scenario

A developer accidentally commits an AWS secret key to a repository. We'll trace how IF.yologuard discovers it and surfaces it for decision-making.

---

## Phase 1: The Raw Log

**File:** `/tmp/config.py` (simulated commit)

```python
# AWS configuration
DB_CONFIG = {
    "aws_access_key": "AKIAIOSFODNN7EXAMPLE",
    "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "region": "us-east-1"
}
```

**Problem:** Two secrets exposed in plain text:
- AWS Access Key ID (starts with `AKIA`)
- AWS Secret Access Key (64 characters, high entropy)

---

## Phase 2: Pattern Detection

**Source:** `/home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py:400-450`

The detector scans for AWS key patterns:

| Pattern | Match | Confidence |
|---------|-------|------------|
| `AWS_ACCESS_KEY` | `AKIAIOSFODNN7EXAMPLE` | HIGH |
| `AWS_SECRET_KEY` | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` | HIGH |

**Rationale:** AWS keys have deterministic prefixes and entropy signatures.
- Reference: Shannon entropy calculation at `/home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py:60-72`

---

## Phase 3: Relationship Mapping (Wu Lun)

**Source:** `/home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py:385-450`

The Confucian relationship mapper (Wu Lun) finds **contextual relationships**:

```
┌─────────────────────────────────────────────┐
│  Relationship Graph                         │
├─────────────────────────────────────────────┤
│                                             │
│  aws_access_key ──[KEY_PAIR]── aws_secret  │
│       │                              │     │
│       └──[VALUE_IN_DICT]─────────────┘     │
│                                             │
│  Dict "DB_CONFIG" ──[CONTAINS]─────────────┘
│                                             │
└─────────────────────────────────────────────┘
```

**Relationships Found:**
1. **KEY_PAIR**: Both access key and secret key in same config dict
2. **CONTEXT**: Variables named `aws_*` confirm AWS service
3. **LOCATION**: Both in same file `/tmp/config.py:3-6`

**Relationship Score:** 0.94 (very strong - unambiguous credential pair)

---

## Phase 4: IFMessage JSON Output

**File:** `/tmp/scan.json` (full format)

```json
{
  "file": "/tmp/config.py",
  "line": 5,
  "pattern": "AWS_ACCESS_KEY",
  "match": "AKIAIOSFODNN7EXAMPLE",
  "severity": "ERROR",
  "classification": "usable",
  "relationshipScore": 0.94,
  "relationships": [
    "aws_secret_key at line 6",
    "in dict DB_CONFIG",
    "pattern_context: AWS credentials"
  ],
  "rationale": [
    "Access key starts with AKIA (AWS standard)",
    "Found in variable named 'aws_access_key'",
    "Paired with secret key in same dict (relationship score 0.94)",
    "Dictionary context: DB_CONFIG (AWS-related name)"
  ],
  "provenance": {
    "detector": "IF.yologuard_v3.0",
    "confidence": 0.98,
    "entropy_bits": 5.2,
    "context_window": "3 lines",
    "scan_time": "2025-11-08T14:32:01Z"
  },
  "pqRisk": {
    "algorithms": ["RSA-2048", "HMAC-SHA256"],
    "exposure_score": 8.7,
    "qes": {
      "score": 8.7,
      "rationale": "AWS HMAC-SHA256 vulnerable to quantum pre-computation attacks"
    }
  }
}
```

**Key Fields Explained:**

| Field | Value | Purpose |
|-------|-------|---------|
| `relationshipScore` | 0.94 | Confidence that this is REAL (not noise) |
| `relationships` | array | Wu Lun context - what makes this meaningful |
| `classification` | "usable" | This secret can actually be used (not a component/fragment) |
| `severity` | "ERROR" | Requires immediate action |
| `provenance` | object | Audit trail: how we found it, when, with what confidence |
| `pqRisk` | object | Post-quantum impact: quantum algorithms vulnerable? |

---

## Phase 5: Guardian Review Decision

**Format:** Decision JSON (what humans/systems decide to DO)

```json
{
  "detection_id": "/tmp/config.py:5:AWS_ACCESS_KEY",
  "verdict": "ROTATE_IMMEDIATELY",
  "confidence": 1.0,
  "rationale": [
    "Access key exposed in version control",
    "Relationship score 0.94 confirms real credential pair",
    "Classification 'usable' means attacker can use this immediately",
    "Severity ERROR + exposure in dict = critical"
  ],
  "actions": [
    {
      "priority": 1,
      "action": "REVOKE",
      "target": "AKIAIOSFODNN7EXAMPLE",
      "reason": "AWS access key confirmed in plaintext repository"
    },
    {
      "priority": 2,
      "action": "ROTATE",
      "target": "aws_secret_key",
      "reason": "Secret paired with exposed access key"
    },
    {
      "priority": 3,
      "action": "AUDIT",
      "target": "git_history",
      "reason": "Check if key was used before exposure; revoke if deployed"
    }
  ],
  "decision_maker": "IF.guard",
  "timestamp": "2025-11-08T14:33:15Z"
}
```

---

## Phase 6: Evidence Binding (Audit Trail)

All claims cite actual code locations:

| Claim | Evidence Location |
|-------|-------------------|
| "Pattern detection uses Shannon entropy" | `/home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py:60-72` |
| "Wu Lun relationship mapper" | `/home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py:385-450` |
| "JSON output includes relationshipScore" | `/home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py:1174-1182` |
| "SARIF format with properties" | `/home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py:1228-1236` |
| "Classification logic (usable vs component)" | `/home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py:705-715` |

---

## Complete Message Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. INPUT: Raw file with secrets                         │
│    /tmp/config.py (developer committed by mistake)      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 2. SCAN: IF.yologuard detects patterns + relationships  │
│    - Pattern: AWS_ACCESS_KEY                            │
│    - Relationship: paired with secret_key in same dict  │
│    - Score: 0.94 (high confidence)                      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 3. JSON OUTPUT: Structured detection message            │
│    {                                                    │
│      "file": "/tmp/config.py",                          │
│      "pattern": "AWS_ACCESS_KEY",                       │
│      "relationshipScore": 0.94,                         │
│      "severity": "ERROR",                               │
│      "classification": "usable"                         │
│    }                                                    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 4. GUARD REVIEW: IF.guard council evaluates             │
│    - Is this a real secret? YES (0.94 relationship)     │
│    - Can it be used? YES (classification: usable)       │
│    - Severity? CRITICAL (ERROR + exposed key pair)      │
│    - Decision: ROTATE_IMMEDIATELY                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 5. ACTION: Decision JSON triggers remediation           │
│    - REVOKE access key                                  │
│    - ROTATE secret key                                  │
│    - AUDIT git history for exposure window              │
└─────────────────────────────────────────────────────────┘
```

---

## Key Concepts Demonstrated

### 1. **Pattern Detection**
- **What:** Regex + entropy analysis finds secret-like strings
- **Example:** `AKIA*` prefix is AWS-specific
- **Confidence:** High because of deterministic structure

### 2. **Relationship Mapping (Wu Lun)**
- **What:** Context around the secret makes it meaningful
- **Example:** "aws_access_key + aws_secret_key in same dict"
- **Why:** Isolated tokens are noise; related tokens are secrets

### 3. **Classification**
- **Usable:** Can be used immediately (API keys, credentials)
- **Component:** Partial match, needs context (certificate fragment)
- **Example:** Full AWS key pair = "usable"; just a key ID = "component"

### 4. **Severity Levels**
- **ERROR:** Immediate exposure, must revoke
- **WARNING:** Potential exposure, monitor
- **NOTE:** Low-risk pattern, informational

### 5. **Provenance**
- **Who:** IF.yologuard v3.0
- **When:** Timestamp of detection
- **How:** Confidence score + entropy + relationships
- **Audit Trail:** Every claim cites source code

---

## Running This Example

See `docs/EXAMPLES/01_scan_single_file.sh` to run this exact scenario.

```bash
#!/bin/bash
cd /home/setup/infrafabric
bash docs/EXAMPLES/01_scan_single_file.sh
```

Expected output:
```
Files scanned: 1
Detections:   2
  • Usable credentials:   2
  • Credential components: 0

Wrote JSON:    /tmp/scan.json
```

Then inspect the JSON to see the complete IFMessage format.

---

## Summary

The InfraFabric pipeline turns **raw secrets in logs** into **actionable guardian decisions**:

1. **Pattern detection** finds secret-like strings
2. **Relationship mapping** confirms they're real secrets (not noise)
3. **JSON output** structures the finding with evidence
4. **Guardian review** decides what to do
5. **Audit trail** ensures every claim is traceable

This "Hello W0RLD" demonstrates that secret detection is not just pattern matching—it's context-aware reasoning with evidence-binding at every step.
