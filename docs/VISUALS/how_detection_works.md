# How Detection Works: The Pipeline

A step-by-step guide to understanding IF.yologuard's detection process.

## The Detection Pipeline

Here's exactly what happens when IF.yologuard scans your code:

```mermaid
flowchart TD
    Start(["Start Scan"]) -->|"Read repo files"| Read["📖 Stage 1: File Read<br/>Extract all text content"]

    Read -->|"Each line of code"| Pattern["🔎 Stage 2: Pattern Match<br/>Compare against 78 patterns"]

    Pattern -->|"Matching found?"| HasMatch{{"✓ Pattern<br/>Match?"}}

    HasMatch -->|No| Read
    HasMatch -->|Yes| Score["📊 Stage 3: Entropy Score<br/>Measure randomness<br/>0.0 = structured, 1.0 = random"]

    Score -->|"Score > threshold?"| IsHigh{{"Is High<br/>Entropy?"}}

    IsHigh -->|"Too ordered<br/>Low entropy"| Reject["❌ Reject<br/>(Probably false positive)"]
    IsHigh -->|"Highly random"| Relations["🔗 Stage 4: Relationship Analysis<br/>Apply Wu Lun Framework"]

    Relations -->|"Calculate relationship<br/>confidence scores"| Scoring["📈 Stage 4.5: Compute<br/>Relationship Score"]

    Scoring -->|"Relationship score<br/>0.0 = isolated, 1.0 = related"| Validate["✅ Stage 5: IEF Validation<br/>Determine severity"]

    Validate -->|"Score + context"| Decision{{"Final<br/>Decision"}}

    Decision -->|"High confidence<br/>+ relationships"| HighSev["🚨 HIGH Severity<br/>(Error level)"]
    Decision -->|"Medium confidence"| MedSev["⚠️ MEDIUM Severity<br/>(Warning level)"]
    Decision -->|"Low confidence"| LowSev["ℹ️ LOW Severity<br/>(Info level)"]
    Decision -->|"Not a secret"| Reject2["❌ Not a Finding"]

    HighSev --> Report["📋 Output Finding"]
    MedSev --> Report
    LowSev --> Report
    Reject --> Next["Continue to next file"]
    Reject2 --> Next

    Report -->|"All files processed?"| End{{"Scan<br/>Complete?"}}
    Next -->|"More files"| Read
    End -->|"Yes"| Output["📊 Generate Report<br/>JSON/SARIF/Stats"]
    Output --> Done(["✓ Done"])

    style Start fill:#e8f5e9
    style Read fill:#e3f2fd
    style Pattern fill:#f3e5f5
    style HasMatch fill:#fff9c4
    style Score fill:#fff3e0
    style IsHigh fill:#fff9c4
    style Relations fill:#fce4ec
    style Scoring fill:#fce4ec
    style Validate fill:#e0f2f1
    style Decision fill:#fff9c4
    style HighSev fill:#ffcdd2
    style MedSev fill:#ffe0b2
    style LowSev fill:#c8e6c9
    style Reject fill:#f5f5f5
    style Reject2 fill:#f5f5f5
    style Report fill:#c5e1a5
    style Output fill:#c5e1a5
    style Done fill:#a5d6a7
```

**Alt Text:** Complex flowchart showing the detection pipeline stages: file reading, pattern matching, entropy scoring, relationship analysis, and final validation with decision points leading to severity levels (HIGH, MEDIUM, LOW) or rejection.

---

## Stage-by-Stage Explanation

### Stage 1: File Read
**Input:** Repository directory
**Output:** All file contents

```
example.py:
"""
import boto3
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

---

### Stage 2: Pattern Match
**Input:** Line of code
**Output:** List of matches or empty

IF.yologuard has 78 pattern variants across these categories:

**Credential Patterns (22):**
- AWS (AccessKeyId, SecretAccessKey)
- Google Cloud (service account keys)
- Azure (connection strings)
- GitHub (personal access tokens)
- Slack (API tokens)
- Database URLs (mysql://, postgres://)
- SSH keys (BEGIN RSA PRIVATE KEY)
- SSL certificates

**Encoding Patterns (15):**
- Base64 credentials
- Hex-encoded secrets
- JWT tokens
- PKCS#12 certificates
- PEM-encoded keys

**Format Patterns (21):**
- Connection strings
- API endpoints with auth
- Configuration values
- License keys
- API keys for 20+ services

**Example:**
```
Line: AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
      ^^^^^^^^^^^ Matches pattern: AWS_SECRET pattern
      "wJalr..." Matches pattern: AWS secret key format
Result: 2 patterns matched → Continue to entropy check
```

---

### Stage 3: Entropy Scoring
**Input:** Matched string
**Output:** Entropy score (0.0 to 1.0)

Entropy measures randomness. Secrets are typically random; false positives are not.

**Examples:**

| String | Entropy | Type | Explanation |
|--------|---------|------|-------------|
| `AKIAIOSFODNN7EXAMPLE` | 0.92 | ✓ Secret | Very random, high entropy |
| `v1.25.3` | 0.45 | ✗ Version | Low entropy, structured |
| `main_branch` | 0.60 | ✗ Variable | Moderate entropy, English word |
| `wJalrXUtnFEMI/K7MD...` | 0.95 | ✓ Secret | Extremely high entropy |
| `deadbeefdeadbeef` | 0.88 | ✓ Possibly secret | High entropy, hex format |

**Decision Point:**
- If entropy < 0.5 → Likely false positive, **REJECT**
- If entropy ≥ 0.5 → Continue to relationships

---

### Stage 4: Relationship Analysis (Wu Lun Framework)
**Input:** High-entropy candidate + surrounding context
**Output:** Relationship scores

This is what makes IF.yologuard powerful: **context matters**.

```python
# Example 1: Isolated string
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
             ^ High entropy
             ^ BUT no relationships
             → Confidence: MEDIUM
```

```python
# Example 2: Related strings (symmetric relationship)
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
               ^ High entropy
               ^ PLUS next to related AWS key
               → Confidence: HIGH
```

```python
# Example 3: Chain of relationships (authority relationship)
import boto3
client = boto3.client('s3')
credentials = {
    "access_key": "AKIAIOSFODNN7EXAMPLE",
    "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "region": "us-east-1"
}
               ^ High entropy
               ^ PLUS within AWS config context
               ^ PLUS multiple related fields
               → Confidence: VERY HIGH
```

**Relationship Scores:**
- Authority (cert ↔ CA chain): 0.85
- Hierarchy (key ↔ version): 0.70
- Complementary (key ↔ endpoint): 0.75
- Symmetric (user ↔ password): 0.85
- Sequential (config ↔ secret): 0.80

---

### Stage 4.5: Compute Combined Score
**Input:** Base entropy + relationship scores
**Output:** Final confidence (0.0 to 1.0)

```
Formula (simplified):
confidence = entropy * 0.4 + relationship_score * 0.6

Example:
entropy: 0.92
relationships: 0.80
confidence: 0.92 * 0.4 + 0.80 * 0.6 = 0.368 + 0.480 = 0.848
```

---

### Stage 5: IEF Validation & Severity
**Input:** Confidence score + credential type
**Output:** Severity level (HIGH/MEDIUM/LOW) or rejection

**Decision Matrix:**

| Credential Type | Confidence | Severity |
|---|---|---|
| Private Key (any) | > 0.0 | **HIGH** (hardcoded) |
| Password field | > 0.70 | **HIGH** |
| Database URL | > 0.70 | **HIGH** |
| API Token | > 0.80 | **HIGH** |
| AWS Key pair | > 0.75 | **MEDIUM** → **HIGH** if related |
| Generic secret | > 0.85 | **MEDIUM** |
| Config value | > 0.90 | **LOW** |

---

## Complete Example Walkthrough

Let's trace a real finding through the entire pipeline:

**Input File: `db_config.py`**
```python
#!/usr/bin/env python3
DATABASE_URL = "postgresql://admin:SuperSecret123@db.example.com:5432/myapp"
REDIS_URL = "redis://:cachePASS123@redis.example.com:6379"
API_VERSION = "v2.1.0"
```

### Trace through pipeline:

**Line 1:** `#!/usr/bin/env python3`
- Stage 2: No patterns match → **SKIP**

**Line 2:** `DATABASE_URL = "postgresql://admin:SuperSecret123@db.example.com:5432/myapp"`
- Stage 2: ✓ Matches database URL pattern
- Stage 3: Entropy of `SuperSecret123` = 0.78 → **PASS** (> 0.5)
- Stage 4:
  - Relationship to `DATABASE_URL` label = 0.80 (symmetric)
  - Context: config file = 0.70 bonus
- Stage 4.5: Score = 0.78 * 0.4 + 0.80 * 0.6 = **0.792**
- Stage 5: Database URL + score 0.792 → **HIGH SEVERITY**

**Line 3:** `REDIS_URL = "redis://:cachePASS123@redis.example.com:6379"`
- Stage 2: ✓ Matches redis pattern
- Stage 3: Entropy = 0.75 → **PASS**
- Stage 4: Relationship to `REDIS_URL` = 0.80
- Stage 4.5: Score = **0.78**
- Stage 5: Database-like URL + score 0.78 → **HIGH SEVERITY**

**Line 4:** `API_VERSION = "v2.1.0"`
- Stage 2: ✓ Matches version pattern
- Stage 3: Entropy = 0.35 → **FAIL** (< 0.5, too structured)
- Stage 5: **REJECT** (not random enough)

---

## Output Example

After scanning `db_config.py`, you get:

```json
{
  "findings": [
    {
      "file": "db_config.py",
      "line": 2,
      "secret_type": "database_url",
      "severity": "HIGH",
      "confidence": 0.792,
      "patterns_matched": ["database_url"],
      "entropy": 0.78,
      "relationships": {
        "label_proximity": 0.80,
        "config_context": 0.70
      },
      "rationale": [
        "High-entropy credential",
        "Matches database URL pattern",
        "Strong relationship to DATABASE_URL label",
        "Located in config section"
      ],
      "provenance": {
        "scan_time": "2025-11-08T14:30:00Z",
        "file_sha256": "abc123...",
        "repo_commit": "def456..."
      }
    },
    // ... more findings
  ],
  "summary": {
    "total_findings": 2,
    "high": 2,
    "medium": 0,
    "low": 0
  }
}
```

---

## Decision Flow Summary

```mermaid
graph LR
    A["Pattern Match?"]
    A -->|No| B["Skip"]
    A -->|Yes| C["High Entropy?"]
    C -->|No| B
    C -->|Yes| D["Relationships?"]
    D -->|No| E["MEDIUM"]
    D -->|Yes| F{{"High<br/>Confidence?"}}
    F -->|Yes| G["HIGH"]
    F -->|No| E
    E --> H["Include in Report"]
    G --> H
    B --> I["Move to next file"]

    style A fill:#fff9c4
    style C fill:#fff9c4
    style F fill:#fff9c4
    style G fill:#ffcdd2
    style E fill:#ffe0b2
    style H fill:#c5e1a5
```

**Alt Text:** Simplified decision tree showing pattern match → entropy check → relationship scoring → final confidence determination → severity assignment.

---

## Key Takeaways

1. **Pattern matching is just the start** - Entropy and relationships do the real work
2. **Context is king** - Related credentials increase confidence
3. **Entropy matters** - Secrets are random; false positives are structured
4. **Severity is proportional** - More relationships = higher severity
5. **Transparency** - Every finding includes its rationale

---

## Next Steps

- **Want to see profiles in action?** See [Profiles Explained](profiles_explained.md)
- **Ready to run a scan?** Check [QUICK_START.md](../QUICK_START.md)
- **Curious about the philosophy?** See [Architecture Overview](architecture_simple.md)
