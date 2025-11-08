# IF.armour Evolution - Goals Roadmap for GPT-5/Codex

**Document Version:** 1.0
**Date:** 2025-11-08
**Repository:** https://github.com/dannystocker/infrafabric (branch: master)
**Target Audience:** GPT-5, GitHub Codex, or equivalent advanced AI coding assistant
**Context:** External review complete (8/10 rating), production-ready foundation
**Current State:** IF.yologuard v3.1 (107/96 detection, IEF+TTT+PQ frameworks)
**Mission:** Evolve IF.yologuard into IF.armour autonomous security suite

---

## Executive Summary

You (GPT-5/Codex) are tasked with transforming IF.yologuard from a **production-ready secrets detector** into **IF.armour**, an **autonomous, self-improving AI security suite** with three pillars:

1. **IF.armour.yologuard** - Secret detection (current foundation)
2. **IF.armour.honeypot** - Attacker deception and profiling
3. **IF.armour.learner** - Recursive threat intelligence and auto-pattern synthesis

**Strategic Goal:** Create the world's first **self-updating secrets detector** that learns from YouTube security talks, GitHub exploits, and CVE databases to automatically generate and deploy new detection patterns.

**Timeline:** 12-16 weeks (3-4 months)
**Success Metric:** Autonomous weekly pattern updates with zero human intervention

---

## Foundation: What You're Building On

### Current State (IF.yologuard v3.1)

**Verified Performance** (from external review):
- ✅ **107/96 detections** (111.5% component-inclusive recall)
- ✅ **42/42 file coverage** (100%)
- ✅ **0 false positives** on falsifier tests
- ✅ **0.1s scan time** (3× faster than claimed)
- ✅ **1394 lines** single-file implementation
- ✅ **Guardian approved** (4.5/4.5 unanimous)

**Existing Features:**
- 78 regex pattern variants (AWS, GitHub, Slack, databases, etc.)
- Wu Lun (五倫) relationship scoring (contextual severity)
- IEF (Immuno-Epistemic Forensics) - danger signals, structure checks
- TTT (Traceability•Trust•Transparency) - provenance tracking, manifests
- PQ (Quantum Readiness) - classical crypto detection, QES scoring
- 5 audience profiles: ci/ops/audit/research/forensics

**External Review Findings:**

✅ **Strengths:**
- Claims independently verified (107/96, 0 FP, scan time)
- Well-structured detection pipeline
- Excellent governance (Guardian handoff process)

⚠️ **Issues to Fix:**
1. Monolithic architecture (1394-line file should be modular)
2. Arbitrary relationship weights (0.85, 0.75, 0.82, 0.65, 0.60 - no empirical justification)
3. Limited test coverage (only falsifiers tested)
4. Missing .gitignore (tracking __pycache__, .venv)
5. Magic numbers hardcoded (thresholds not extracted to constants)

**Your First Job:** Fix the issues, then evolve to IF.armour.

---

## Phase 1: Foundation Fixes (v3.1.1)

**Duration:** Week 1
**Goal:** Achieve 9/10 external review rating (up from 8/10)

### Objectives

#### 1.1 Repository Hygiene
- [ ] Create `.gitignore` with: `__pycache__/`, `*.pyc`, `.venv*/`, `reports/`, `benchmarks/results.json`, `state/`
- [ ] Remove tracked cache files from git history
- [ ] Document purpose of `versions/` directory (or remove if redundant)

**Acceptance Criteria:**
- Git status shows no untracked cache/temp files
- Repository size reduced by ≥50KB (removed cache)

#### 1.2 Extract Magic Numbers
- [ ] Create `core/thresholds.py` module
- [ ] Extract all hardcoded thresholds:
  ```python
  # Profile-based thresholds
  CI_ERROR_THRESHOLD = 0.80
  CI_WARN_THRESHOLD = 0.60
  FORENSICS_ERROR_THRESHOLD = 0.65
  FORENSICS_WARN_THRESHOLD = 0.45

  # Relationship weights (Wu Lun)
  PENGYOU_WEIGHT = 0.85    # 朋友 (friends)
  FUFU_WEIGHT = 0.75       # 夫婦 (complementary)
  JUNCHIN_WEIGHT = 0.82    # 君臣 (ruler-subject)
  FUZI_WEIGHT = 0.65       # 父子 (generational)
  XIONGDI_WEIGHT = 0.60    # 兄弟 (siblings)

  # Detection parameters
  ENTROPY_THRESHOLD = 4.5
  MIN_TOKEN_LENGTH = 16
  CONTEXT_RADIUS = 50  # chars around detection
  MAX_FILE_BYTES = 5_000_000
  ```

**Acceptance Criteria:**
- Zero magic numbers in main detection code
- All thresholds in single importable module
- Constants have descriptive names + comments

#### 1.3 Documentation Updates
- [ ] Add "Installation" section to README.md:
  ```markdown
  ## Installation

  ### From source
  ```bash
  git clone https://github.com/dannystocker/infrafabric.git
  cd infrafabric/code/yologuard
  python3 -m pip install -r requirements.txt  # (you'll create this)
  ```

  ### Quick test
  ```bash
  python3 src/IF.yologuard_v3.py --scan benchmarks/leaky-repo --stats
  # Expected: 107/96 detections in <0.5s
  ```
  ```
- [ ] Mark PQ (Quantum Readiness) as "Experimental (v1)" in docs
- [ ] Add disclaimer: "QES scoring requires empirical calibration (planned v4)"

**Acceptance Criteria:**
- New user can install and run in <5 minutes
- All docs mention version numbers (v3.1.1)
- Experimental features clearly marked

#### 1.4 Create GitHub Issues
- [ ] Create issues for all roadmap commitments from `GUARDIAN_HANDOFF_v3.1_IEF.md`:
  - "Calibrate thresholds/QES with curated corpus (2-4 weeks)"
  - "User docs update for profiles/IEF/PQ"
  - "30-day retrospective on adoption, FP rates"
  - "Enhanced IEF: stylometry, git history anomalies (4-6 weeks)"
  - "SBOM-aware PQ: version checks, dependency graph (6-8 weeks)"
  - "Cross-file relationships: env/config linking (8-10 weeks)"

**Acceptance Criteria:**
- ≥6 issues created with labels: roadmap, enhancement, v4
- Issues have clear acceptance criteria
- Issues linked to GUARDIAN_HANDOFF doc

### Success Metrics (v3.1.1)

| Metric | Target | Verification |
|--------|--------|--------------|
| External review rating | 9/10 (up from 8/10) | Re-run review checklist |
| Git cleanliness | 0 cache files tracked | `git status` clean |
| Magic numbers | 0 in main code | `grep "0\.[0-9]" src/*.py \| wc -l` = 0 |
| Installation time | <5 minutes | Time from clone to first scan |
| Documentation clarity | New user success rate >90% | Test with 3 new users |

**Deliverable:** IF.yologuard v3.1.1 (production-ready, fully documented, GitHub issues created)

---

## Phase 2: Modular Architecture (v3.2)

**Duration:** Weeks 2-3 (10 business days)
**Goal:** Split 1394-line monolith into 8+ modules

### Objectives

#### 2.1 Architecture Refactoring

**Target Structure:**
```
src/
├── IF.yologuard_v3.py          # CLI entry point (thin wrapper, <200 lines)
├── core/
│   ├── __init__.py
│   ├── scanner.py              # Main SecretScanner class
│   ├── thresholds.py           # Moved from Phase 1
│   └── profiles.py             # Profile configuration (ci/ops/audit/etc.)
├── patterns/
│   ├── __init__.py
│   ├── credentials.py          # AWS, GitHub, Slack, Stripe patterns
│   ├── keys.py                 # RSA, SSH, API keys, PGP
│   ├── database.py             # PostgreSQL, MySQL, MongoDB connection strings
│   ├── tokens.py               # JWT, session tokens, bearer tokens
│   └── registry.py             # Pattern management (add/remove/list)
├── detection/
│   ├── __init__.py
│   ├── matcher.py              # Regex pattern matching engine
│   ├── decoder.py              # Base64/hex decoding, predecode_and_rescan
│   ├── entropy.py              # Shannon entropy detection
│   └── deduplication.py        # Position-aware deduplication
├── scoring/
│   ├── __init__.py
│   ├── wulun.py                # Wu Lun relationship detection + scoring
│   ├── aristotelian.py         # Essence classification (usable vs component)
│   └── severity.py             # Final severity calculation (ERROR/WARN)
├── frameworks/
│   ├── __init__.py
│   ├── ief.py                  # Immuno-Epistemic Forensics
│   ├── ttt.py                  # Traceability Trust Transparency
│   └── pq.py                   # Quantum Readiness analysis
├── output/
│   ├── __init__.py
│   ├── json_formatter.py       # JSON output
│   ├── sarif_formatter.py      # SARIF v2.1.0 output
│   ├── text_formatter.py       # Human-readable text
│   ├── manifest_writer.py      # TTT manifest generation
│   └── graph_exporter.py       # Indra graph JSON
└── api/
    ├── __init__.py
    ├── rest_server.py          # FastAPI REST API (NEW)
    └── python_api.py           # Python library interface
```

**Refactoring Plan:**

**Step 1: Create Module Skeleton** (Day 1)
- [ ] Create all directories and `__init__.py` files
- [ ] Add module-level docstrings explaining each module's purpose
- [ ] Set up imports between modules

**Step 2: Extract Patterns** (Day 2)
- [ ] Move all 78 regex patterns from main file to `patterns/*.py`
- [ ] Group by secret type (credentials, keys, databases, tokens)
- [ ] Create `PatternRegistry` class for dynamic pattern management
- [ ] Add pattern metadata: name, severity, description, examples

**Step 3: Extract Detection Logic** (Day 3)
- [ ] Move `scan_with_patterns()` → `detection/matcher.py`
- [ ] Move `predecode_and_rescan()` → `detection/decoder.py`
- [ ] Move `shannon_entropy()`, `detect_high_entropy_tokens()` → `detection/entropy.py`
- [ ] Move deduplication logic → `detection/deduplication.py`

**Step 4: Extract Scoring Logic** (Day 4)
- [ ] Move all 5 Wu Lun relationship functions → `scoring/wulun.py`
- [ ] Move `confucian_relationship_score()` → `scoring/wulun.py`
- [ ] Move `_is_component()` classification → `scoring/aristotelian.py`
- [ ] Create `SeverityCalculator` class → `scoring/severity.py`

**Step 5: Extract Frameworks** (Day 5)
- [ ] Move IEF danger signals, structure checks → `frameworks/ief.py`
- [ ] Move TTT provenance, rationale, manifest logic → `frameworks/ttt.py`
- [ ] Move PQ crypto detection, QES calculation → `frameworks/pq.py`
- [ ] Ensure each framework can be enabled/disabled independently

**Step 6: Extract Output Formatters** (Day 6)
- [ ] Move JSON formatting → `output/json_formatter.py`
- [ ] Move SARIF formatting → `output/sarif_formatter.py`
- [ ] Move text formatting → `output/text_formatter.py`
- [ ] Move manifest writing → `output/manifest_writer.py`
- [ ] Move graph export → `output/graph_exporter.py`

**Step 7: Create Core Scanner** (Day 7)
- [ ] Create `SecretScanner` class in `core/scanner.py`
- [ ] Orchestrate pipeline: scan_file() → matcher → scorer → formatter
- [ ] Import all modules cleanly
- [ ] Ensure backward compatibility (same API as v3.1.1)

**Step 8: Create Thin CLI Wrapper** (Day 8)
- [ ] Refactor `IF.yologuard_v3.py` to <200 lines
- [ ] Keep argparse logic, delegate to `core/scanner.py`
- [ ] Maintain all CLI flags (--scan, --json, --sarif, --profile, etc.)
- [ ] Ensure identical behavior to v3.1.1

**Acceptance Criteria:**
- ≥8 modules with clear separation of concerns
- Each module <300 lines (except patterns registry)
- Zero circular dependencies
- Main CLI file <200 lines
- All existing tests pass (107/96 benchmark, falsifiers)
- Import time <1 second
- Scan time still <0.2s (no performance regression)

#### 2.2 Comprehensive Test Suite

**Coverage Target: 80%+**

**Test Categories:**

**Unit Tests** (pytest):
```python
# tests/test_patterns.py
def test_aws_key_detection():
    """Test AWS key pattern matches valid keys"""
    pattern = get_pattern('aws_access_key')
    assert pattern.match('AKIAIOSFODNN7EXAMPLE')
    assert not pattern.match('not_a_key_123456')

# tests/test_entropy.py
def test_shannon_entropy():
    """Test entropy calculation"""
    assert shannon_entropy(b'aaaa') < 1.0
    assert shannon_entropy(b'a8f3k9m2') > 2.5

# tests/test_wulun.py
def test_user_password_relationship():
    """Test Wu Lun relationship detection"""
    text = 'username = "admin"\npassword = "secret123"'
    rel = detect_user_password_relationship('secret123', text, position=40)
    assert rel is not None
    assert rel[0] == '朋友'  # friends relationship
```

**Integration Tests:**
```python
# tests/test_integration.py
def test_full_scan_pipeline():
    """Test complete scan from file to JSON output"""
    scanner = SecretScanner(profile='ci')
    result = scanner.scan_file(Path('benchmarks/leaky-repo/.ftpconfig'))

    assert len(result) >= 3  # Expected detections
    assert all('provenance' in d for d in result)  # TTT framework
    assert all('severity' in d for d in result)

def test_profile_thresholds():
    """Test different profiles use different thresholds"""
    file = Path('benchmarks/leaky-repo/deployment-config.json')

    ci_scanner = SecretScanner(profile='ci')
    ci_errors = [d for d in ci_scanner.scan_file(file) if d['severity'] == 'ERROR']

    forensics_scanner = SecretScanner(profile='forensics')
    forensics_errors = [d for d in forensics_scanner.scan_file(file) if d['severity'] == 'ERROR']

    # Forensics should have MORE errors (lower threshold)
    assert len(forensics_errors) >= len(ci_errors)
```

**Performance Tests:**
```python
# tests/test_performance.py
import time

def test_scan_time_under_500ms():
    """Ensure scan time <0.5s for leaky-repo"""
    scanner = SecretScanner()
    start = time.time()

    for file in Path('benchmarks/leaky-repo').rglob('*'):
        if file.is_file():
            scanner.scan_file(file)

    elapsed = time.time() - start
    assert elapsed < 0.5, f"Scan took {elapsed:.2f}s, expected <0.5s"

def test_no_memory_leaks():
    """Ensure repeated scans don't leak memory"""
    import tracemalloc

    tracemalloc.start()
    scanner = SecretScanner()

    # Scan 100 times
    for _ in range(100):
        scanner.scan_file(Path('benchmarks/leaky-repo/db/dump.sql'))

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Peak memory should be <100MB
    assert peak < 100 * 1024 * 1024, f"Peak memory: {peak / 1024 / 1024:.1f}MB"
```

**Edge Case Tests:**
```python
# tests/test_edge_cases.py
def test_empty_file():
    scanner = SecretScanner()
    result = scanner.scan_content('', filename='empty.txt')
    assert result == []

def test_binary_file():
    scanner = SecretScanner()
    result = scanner.scan_file(Path('/bin/ls'))
    assert result == []  # Should skip binary files

def test_large_file():
    scanner = SecretScanner(max_file_bytes=1024)
    # Create 10KB file
    large_content = 'x' * 10_000
    result = scanner.scan_content(large_content, filename='large.txt')
    # Should truncate to 1KB
    assert True  # Should not crash

def test_unicode_content():
    scanner = SecretScanner()
    result = scanner.scan_content('密码 = "secret123"', filename='unicode.txt')
    assert len(result) >= 1  # Should detect password

def test_malicious_regex():
    """Test ReDoS prevention"""
    scanner = SecretScanner()
    # Pathological input for catastrophic backtracking
    evil = 'a' * 10000 + 'X'

    import signal
    def timeout_handler(signum, frame):
        raise TimeoutError("Regex took too long")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(2)  # 2 second timeout

    try:
        scanner.scan_content(evil, filename='evil.txt')
    except TimeoutError:
        pytest.fail("Regex vulnerable to ReDoS")
    finally:
        signal.alarm(0)
```

**Test Automation:**
```yaml
# tests/pytest.ini
[pytest]
minversion = 7.0
addopts =
    --verbose
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
testpaths = tests
```

**Acceptance Criteria:**
- ≥80% code coverage (pytest-cov)
- All 107/96 benchmark tests pass
- All falsifier tests pass (0 FP)
- ≥20 edge case tests
- ≥10 performance tests
- CI pipeline runs tests on every commit

#### 2.3 CI/CD Pipeline

**GitHub Actions Workflow:**

```yaml
# .github/workflows/if-yologuard-ci.yml
name: IF.yologuard CI

on:
  push:
    branches: [master, develop]
  pull_request:
    branches: [master]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run unit tests
        run: pytest tests/ --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml

  benchmark:
    runs-on: ubuntu-latest
    needs: test

    steps:
      - uses: actions/checkout@v4

      - name: Run leaky-repo benchmark
        run: |
          python3 benchmarks/run_leaky_repo_v3_philosophical_fast_v2.py > benchmark_output.txt

      - name: Verify benchmark results
        run: |
          # Must achieve ≥95/96 detections
          DETECTIONS=$(grep "v3 detected:" benchmark_output.txt | awk '{print $3}' | cut -d'/' -f1)
          if [ "$DETECTIONS" -lt 95 ]; then
            echo "FAIL: Only $DETECTIONS/96 detections (expected ≥95)"
            exit 1
          fi
          echo "PASS: $DETECTIONS/96 detections"

      - name: Run falsifier tests
        run: python3 tests/test_falsifiers.py

  performance:
    runs-on: ubuntu-latest
    needs: benchmark

    steps:
      - uses: actions/checkout@v4

      - name: Performance test
        run: |
          TIME=$(time -p python3 src/IF.yologuard_v3.py --scan benchmarks/leaky-repo --stats 2>&1 | grep real | awk '{print $2}')
          echo "Scan time: ${TIME}s"

          # Must complete in <0.5s
          if (( $(echo "$TIME > 0.5" | bc -l) )); then
            echo "FAIL: Scan took ${TIME}s (expected <0.5s)"
            exit 1
          fi
          echo "PASS: Scan completed in ${TIME}s"

  security-scan:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run Bandit security scan
        run: |
          pip install bandit
          bandit -r src/ -ll  # Only high/medium severity

      - name: Run safety check
        run: |
          pip install safety
          safety check --json
```

**Acceptance Criteria:**
- CI pipeline runs on every push/PR
- ≥3 Python versions tested (3.10, 3.11, 3.12)
- Benchmark gate: ≥95/96 detections required to pass
- Performance gate: <0.5s scan time required to pass
- Security scan: No high/medium vulnerabilities
- Code coverage: ≥80% required to pass
- Pull requests blocked until all checks pass

### Success Metrics (v3.2)

| Metric | Target | Verification |
|--------|--------|--------------|
| Modules created | ≥8 | Count directories in src/ |
| Lines per module | <300 (average) | `find src -name "*.py" -exec wc -l {} \;` |
| Test coverage | ≥80% | pytest-cov report |
| CI pipeline | Green ✅ | GitHub Actions badge |
| Performance | <0.2s (no regression) | CI performance test |
| Benchmark | 107/96 maintained | CI benchmark test |

**Deliverable:** IF.yologuard v3.2 (modular, tested, CI/CD-gated, ready for REST API)

---

## Phase 3: Calibration & REST API (v3.3)

**Duration:** Week 4
**Goal:** Replace arbitrary weights with data-driven values, add production REST API

### Objectives

#### 3.1 Empirical Weight Calibration

**Problem:** Wu Lun relationship weights (0.85, 0.75, 0.82, 0.65, 0.60) are arbitrary.

**Solution:** Grid search over 1000-file corpus to find optimal weights.

**Steps:**

**Step 1: Curate Calibration Corpus** (Day 1)
- [ ] Collect 1000 files: 500 clean (no secrets), 500 with secrets
- [ ] Ensure diverse file types: .py, .js, .yml, .env, .sql, .xml, .json
- [ ] Label ground truth: For each file with secrets, mark exact secret locations
- [ ] Split into train (700 files) and test (300 files)

**Sources for corpus:**
- Existing: benchmarks/leaky-repo (96 secrets, 49 files)
- Add: GitHub public repos with known leaks (search for "remove password" commits)
- Add: Security datasets (e.g., SecLists, PayloadsAllTheThings)
- Add: Synthetic examples (generate fake secrets in realistic contexts)

**Step 2: Implement Grid Search** (Day 2)
```python
# harness/calibrate_weights.py

from itertools import product
from sklearn.metrics import precision_score, recall_score, f1_score

class WeightCalibrator:
    """Calibrate Wu Lun relationship weights via grid search"""

    def __init__(self, corpus_path: Path):
        self.corpus = self._load_corpus(corpus_path)
        self.ground_truth = self._load_ground_truth(corpus_path / 'labels.json')

    def grid_search(self):
        """Search over weight ranges to find optimal F1 score"""

        # Define search space
        weight_ranges = {
            'pengyou': [0.75, 0.80, 0.85, 0.90],   # 朋友
            'fufu': [0.70, 0.75, 0.80, 0.85],       # 夫婦
            'junchin': [0.75, 0.80, 0.82, 0.85],    # 君臣
            'fuzi': [0.60, 0.65, 0.70, 0.75],       # 父子
            'xiongdi': [0.55, 0.60, 0.65, 0.70]     # 兄弟
        }

        best_f1 = 0
        best_weights = None

        # Try all combinations (4^5 = 1024 combinations)
        for weights in product(*weight_ranges.values()):
            config = dict(zip(weight_ranges.keys(), weights))

            # Scan corpus with these weights
            results = self._scan_with_weights(config)

            # Calculate metrics
            precision = precision_score(self.ground_truth, results)
            recall = recall_score(self.ground_truth, results)
            f1 = f1_score(self.ground_truth, results)

            if f1 > best_f1:
                best_f1 = f1
                best_weights = config
                print(f"New best F1: {f1:.4f} with weights: {config}")

        return best_weights, best_f1

    def _scan_with_weights(self, weights: Dict) -> List[bool]:
        """Scan corpus with given weights, return binary classification"""
        scanner = SecretScanner()
        scanner.set_wulun_weights(weights)

        predictions = []
        for file in self.corpus:
            detections = scanner.scan_file(file)
            predictions.append(len(detections) > 0)  # Binary: has secrets?

        return predictions
```

**Step 3: Run Calibration** (Day 3)
- [ ] Run grid search on training set (700 files)
- [ ] Validate on test set (300 files)
- [ ] Compare F1 score: old weights vs new weights
- [ ] Document findings in `docs/WEIGHT_CALIBRATION.md`

**Expected Outcome:**
- New weights optimize F1 score (target: ≥0.95)
- Precision/recall trade-off explicitly documented
- A/B test results show new weights ≥ old weights

**Step 4: Update Code** (Day 3)
- [ ] Update `core/thresholds.py` with calibrated weights
- [ ] Add comment explaining calibration methodology
- [ ] Run full benchmark to verify no regression

**Acceptance Criteria:**
- F1 score ≥0.95 on test set
- New weights perform ≥ old weights on leaky-repo benchmark
- Calibration process documented and reproducible

#### 3.2 REST API Implementation

**Goal:** Production-ready REST API for IF.yologuard

**Technology Stack:**
- FastAPI (async, auto-docs, high performance)
- Pydantic (request/response validation)
- Uvicorn (ASGI server)
- TLS 1.3 (encrypted traffic)

**API Design:**

```python
# api/rest_server.py

from fastapi import FastAPI, HTTPException, File, UploadFile, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn
from typing import List, Optional
import secrets

app = FastAPI(
    title="IF.yologuard API",
    version="3.3",
    description="Secret detection API with Wu Lun relationship scoring",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
security = HTTPBearer()

class ScanRequest(BaseModel):
    """Request to scan text content"""
    content: str = Field(..., description="Text content to scan", min_length=1)
    filename: str = Field(default="stdin", description="Filename for context")
    profile: str = Field(default="ci", description="Detection profile", regex="^(ci|ops|audit|research|forensics)$")
    mode: str = Field(default="both", description="Detection mode", regex="^(usable|component|both)$")

    class Config:
        schema_extra = {
            "example": {
                "content": "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
                "filename": ".env",
                "profile": "ci",
                "mode": "usable"
            }
        }

class Detection(BaseModel):
    """Single secret detection"""
    pattern: str = Field(..., description="Pattern name that matched")
    severity: str = Field(..., description="ERROR or WARNING")
    file: str = Field(..., description="Filename")
    line: int = Field(..., description="Line number")
    match: str = Field(..., description="Redacted match (e.g., AKI***)")
    relationship_score: float = Field(..., description="Wu Lun relationship score")
    classification: str = Field(..., description="usable or component")
    provenance: dict = Field(default={}, description="TTT provenance metadata")

class ScanResponse(BaseModel):
    """Scan result"""
    status: str = Field(default="success", description="success or error")
    detections: List[Detection] = Field(..., description="List of detected secrets")
    metadata: dict = Field(..., description="Scan metadata")

@app.post("/scan", response_model=ScanResponse, tags=["Detection"])
async def scan_content(
    request: ScanRequest,
    credentials: HTTPAuthorizationCredentials = security
):
    """
    Scan text content for secrets

    Returns list of detected secrets with Wu Lun relationship scores.
    """
    # Authenticate (simple bearer token for now)
    if not _validate_api_key(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Scan
    scanner = SecretScanner(profile=request.profile, mode=request.mode)
    detections = scanner.scan_content(request.content, request.filename)

    return ScanResponse(
        status="success",
        detections=[Detection(**d) for d in detections],
        metadata={
            "count": len(detections),
            "error_count": sum(1 for d in detections if d['severity'] == 'ERROR'),
            "warn_count": sum(1 for d in detections if d['severity'] == 'WARNING'),
            "profile": request.profile,
            "mode": request.mode
        }
    )

@app.post("/scan/file", response_model=ScanResponse, tags=["Detection"])
async def scan_file(
    file: UploadFile = File(...),
    profile: str = "ci",
    mode: str = "both",
    credentials: HTTPAuthorizationCredentials = security
):
    """
    Scan uploaded file for secrets

    Supports text files up to 5MB.
    """
    if not _validate_api_key(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Read file
    content = await file.read()

    # Check size
    if len(content) > 5_000_000:
        raise HTTPException(status_code=413, detail="File too large (max 5MB)")

    # Decode
    try:
        text = content.decode('utf-8', errors='ignore')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot decode file: {e}")

    # Scan
    scanner = SecretScanner(profile=profile, mode=mode)
    detections = scanner.scan_content(text, file.filename)

    return ScanResponse(
        status="success",
        detections=[Detection(**d) for d in detections],
        metadata={
            "filename": file.filename,
            "size_bytes": len(content),
            "count": len(detections)
        }
    )

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for load balancers"""
    scanner = SecretScanner()

    return {
        "status": "healthy",
        "version": "3.3",
        "patterns": len(scanner.get_pattern_names()),
        "profiles": ["ci", "ops", "audit", "research", "forensics"],
        "modes": ["usable", "component", "both"]
    }

@app.get("/patterns", tags=["Introspection"])
async def list_patterns(credentials: HTTPAuthorizationCredentials = security):
    """List all available detection patterns"""
    if not _validate_api_key(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid API key")

    scanner = SecretScanner()
    patterns = scanner.get_pattern_metadata()

    return {
        "patterns": patterns,
        "count": len(patterns)
    }

@app.get("/profiles", tags=["Introspection"])
async def list_profiles():
    """List all detection profiles with thresholds"""
    from core.thresholds import PROFILE_THRESHOLDS

    return {
        "profiles": PROFILE_THRESHOLDS
    }

def _validate_api_key(key: str) -> bool:
    """Validate API key (simple version, use proper auth in production)"""
    # For v3.3: Simple static key
    # For v4+: Use JWT tokens with expiration
    VALID_KEYS = [
        "sk-yologuard-dev-12345",  # Development key
        # Load from environment in production
    ]
    return key in VALID_KEYS

if __name__ == '__main__':
    # Production server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8082,
        ssl_certfile="certs/server.pem",
        ssl_keyfile="certs/server-key.pem",
        workers=4,
        log_level="info"
    )
```

**CLI Integration:**
```python
# In IF.yologuard_v3.py, add --serve flag

if args.serve:
    from api.rest_server import app
    import uvicorn

    print(f"Starting IF.yologuard REST API on {args.host}:{args.port}")
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        ssl_certfile=args.tls_cert,
        ssl_keyfile=args.tls_key
    )
```

**Usage Examples:**
```bash
# Start server
python3 IF.yologuard_v3.py --serve --host 0.0.0.0 --port 8082 --tls-cert certs/server.pem --tls-key certs/server-key.pem

# Scan via curl
curl -X POST https://localhost:8082/scan \
  -H "Authorization: Bearer sk-yologuard-dev-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\nAWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "profile": "ci"
  }'

# Health check
curl https://localhost:8082/health

# List patterns
curl https://localhost:8082/patterns \
  -H "Authorization: Bearer sk-yologuard-dev-12345"
```

**Acceptance Criteria:**
- REST API runs on port 8082 with TLS 1.3
- Auto-generated OpenAPI docs at /docs
- Bearer token authentication
- ≥100 requests/second throughput (load test with Apache Bench)
- Response time <100ms for typical scan (10KB file)
- Graceful error handling (413 for large files, 401 for bad auth)

### Success Metrics (v3.3)

| Metric | Target | Verification |
|--------|--------|--------------|
| Calibrated weights F1 | ≥0.95 | Grid search results |
| REST API throughput | ≥100 req/sec | `ab -n 1000 -c 10 https://localhost:8082/scan` |
| API response time | <100ms (p95) | Load test with realistic payloads |
| OpenAPI docs | Auto-generated | Visit /docs endpoint |
| TLS encryption | TLS 1.3 only | `nmap --script ssl-enum-ciphers` |

**Deliverable:** IF.yologuard v3.3 (calibrated, REST API, production-ready)

---

## Phase 4: Rebranding → IF.armour.yologuard (v4.0)

**Duration:** Week 5
**Goal:** Transition to IF.armour ecosystem branding

### Objectives

#### 4.1 File & Module Renaming

**Changes:**
```bash
# Before
src/IF.yologuard_v3.py

# After
src/IF.armour.yologuard.py

# Module structure
src/armour/
├── __init__.py           # "from armour import yologuard, honeypot, learner"
└── yologuard/
    ├── __init__.py       # "from armour.yologuard import SecretScanner"
    ├── core/
    ├── patterns/
    ├── detection/
    ├── scoring/
    ├── frameworks/
    ├── output/
    └── api/
```

**Backward Compatibility Wrapper:**
```python
# src/IF.yologuard_v3.py (deprecated wrapper)
"""
DEPRECATED: Use IF.armour.yologuard instead

This wrapper is maintained for backward compatibility until v5.0.
All new code should import from armour.yologuard.
"""
import warnings
from armour.yologuard import SecretScanner as SecretRedactorV3
from armour.yologuard import cli_main

warnings.warn(
    "IF.yologuard is deprecated. Use IF.armour.yologuard instead.",
    DeprecationWarning,
    stacklevel=2
)

if __name__ == '__main__':
    print("WARNING: IF.yologuard_v3.py is deprecated.")
    print("Use: if-armour yologuard --scan /path")
    cli_main()
```

**New CLI Entry Point:**
```bash
# Install as command
pip install -e .  # Creates 'if-armour' command

# Usage
if-armour yologuard --scan /repo --profile ci
if-armour yologuard --serve --port 8082
if-armour yologuard --version
# Output: IF.armour.yologuard v4.0 (Secret Detection Pillar)
```

**Acceptance Criteria:**
- All files renamed without breaking functionality
- Old imports still work (deprecation warnings shown)
- New imports preferred: `from armour.yologuard import SecretScanner`
- CLI command `if-armour yologuard` works
- All tests pass with new import structure

#### 4.2 Documentation Update

**Update all docs to explain IF.armour vision:**

**README.md:**
```markdown
# IF.armour - Autonomous AI Security Suite

IF.armour is a **self-improving security suite** with three pillars:

## 1. IF.armour.yologuard - Secret Detection (v4.0)
**Status:** Production-ready
**Capability:** Detect 78 pattern variants with 111.5% recall

## 2. IF.armour.honeypot - Attacker Deception (v4.1 - Coming Soon)
**Status:** In development
**Capability:** Deploy honeytokens, profile attackers, waste attacker resources

## 3. IF.armour.learner - Threat Intelligence (v4.2 - Coming Soon)
**Status:** Planned
**Capability:** Scrape YouTube/GitHub/CVEs, auto-generate detection patterns

## Quick Start

### Install
```bash
pip install if-armour
```

### Detect Secrets
```bash
if-armour yologuard --scan /repo --profile ci
```

### Start REST API
```bash
if-armour yologuard --serve --port 8082 --tls-cert server.pem
```

## Architecture

IF.armour integrates the full IF.* stack:
- **IF.search** - Code context analysis
- **IF.swarm** - Multi-LLM consensus voting
- **IF.optimise** - Token efficiency
- **IF.ceo** - Strategic decisions
- **IF.guard** - Governance oversight
```

**Acceptance Criteria:**
- README explains 3-pillar vision
- Position yologuard as "detection pillar"
- Mention honeypot + learner as "coming soon"
- Update all code examples to use new imports
- Version numbers consistent (v4.0) across all docs

### Success Metrics (v4.0)

| Metric | Target | Verification |
|--------|--------|--------------|
| Backward compatibility | 100% (old imports work) | Run v3.2 code against v4.0 |
| Documentation clarity | 3-pillar vision explained | User testing (5 people) |
| Migration path | <30 minutes to update code | Time existing projects |
| CLI usability | `if-armour yologuard` works | Command execution |

**Deliverable:** IF.armour.yologuard v4.0 (rebranded, backward compatible, vision documented)

---

## Stretch Goals (Optional Enhancements)

These are **optional** but would be impressive to deliver:

### SG-1: Performance Optimization
- [ ] Compile regexes once at module import (not per-scan)
- [ ] Async file scanning (parallel processing)
- [ ] Target: Scan 1000 files in <5 seconds (currently ~50s estimated)

### SG-2: Plugin Architecture
- [ ] Allow custom patterns via YAML config
- [ ] Pattern hot-reload (add patterns without restarting)
- [ ] Community pattern repository

### SG-3: Container Image
- [ ] Create Docker image: `docker pull infrafabric/if-armour:4.0`
- [ ] Kubernetes deployment manifest
- [ ] Helm chart

### SG-4: VS Code Extension (Prototype)
- [ ] Real-time secret detection as you type
- [ ] Underline secrets in red
- [ ] Quick fix: "Move to environment variable"

### SG-5: Enhanced PQ Analysis
- [ ] Parse SBOM files (CycloneDX, SPDX)
- [ ] Library-level crypto detection (not just file-level)
- [ ] Version-aware risk scoring (RSA-1024 critical, RSA-4096 medium)

---

## Success Criteria Summary

**Phase 1 (v3.1.1) - Week 1:**
- ✅ .gitignore added, no cache files tracked
- ✅ Magic numbers extracted to constants module
- ✅ README has installation section
- ✅ PQ marked as experimental
- ✅ GitHub issues created for roadmap

**Phase 2 (v3.2) - Weeks 2-3:**
- ✅ ≥8 modules with <300 lines each
- ✅ ≥80% test coverage
- ✅ CI/CD pipeline (green status)
- ✅ 107/96 benchmark maintained
- ✅ <0.2s scan time maintained

**Phase 3 (v3.3) - Week 4:**
- ✅ Wu Lun weights calibrated (F1 ≥0.95)
- ✅ REST API (≥100 req/sec, <100ms p95)
- ✅ TLS 1.3 encryption
- ✅ OpenAPI docs auto-generated

**Phase 4 (v4.0) - Week 5:**
- ✅ Rebranded to IF.armour.yologuard
- ✅ Backward compatibility (old imports work)
- ✅ 3-pillar vision documented
- ✅ CLI command `if-armour yologuard` works

---

## Final Notes for GPT-5/Codex

### What Success Looks Like

By the end of Phase 4 (Week 5), you will have delivered:

1. **Production-grade modular codebase** (≥8 modules, 80%+ test coverage)
2. **Data-driven detection** (empirically calibrated Wu Lun weights)
3. **Enterprise-ready REST API** (TLS 1.3, auth, auto-docs)
4. **Strategic positioning** (IF.armour.yologuard as pillar 1 of 3)
5. **Automated quality gates** (CI/CD pipeline blocks regressions)

### How to Exceed Expectations

**"Exceeded" means:**
- Phase 1 delivered in **<1 week** (target: 3 days)
- Test coverage **>90%** (target: 80%)
- REST API throughput **>200 req/sec** (target: 100)
- Modular architecture **>10 modules** (target: 8)
- Stretch goals **≥2 delivered** (Docker image + async scanning recommended)

### Handoff to Next Phase

After v4.0, the roadmap continues to:
- **v4.1:** IF.armour.honeypot (attacker deception)
- **v4.2:** IF.armour.learner (threat intel, auto-patterns)
- **v5.0:** Full IF stack integration (IF.search, IF.swarm, IF.guard)

**Your job:** Prepare the foundation so these can be added as **clean modules** without touching yologuard core.

### Communication

As you work:
- **Commit frequently** with descriptive messages
- **Document decisions** in code comments + docs/
- **Flag uncertainties** in TODO comments (e.g., "TODO: Is 0.85 the right weight? Needs calibration")
- **Request clarification** if requirements are ambiguous

### Go Build Something Amazing! 🚀

You have a **solid foundation** (8/10 external review, 107/96 verified performance) and a **clear roadmap**. Transform IF.yologuard into the **detection pillar** of IF.armour, and set the stage for autonomous, self-improving security.

**Timeline:** 5 weeks
**Current:** v3.1 (production-ready)
**Target:** v4.0 (IF.armour.yologuard - modular, calibrated, REST API, rebranded)

**Let's exceed expectations.** ⚡
