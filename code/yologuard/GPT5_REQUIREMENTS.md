# IF.armour Evolution - Requirements Specification for GPT-5/Codex

**Document Version:** 1.0
**Date:** 2025-11-08
**Repository:** https://github.com/dannystocker/infrafabric (branch: master)
**Review Date:** [To be filled by external reviewer]
**Target:** GPT-5, GitHub Codex, or equivalent advanced AI assistant

---

## Document Purpose

This requirements specification defines **MUST**, **SHOULD**, and **MAY** criteria for transforming IF.yologuard v3.1 into IF.armour v4.0+. It is designed to be:

1. **Exceeded:** Minimum requirements set deliberately low to enable exceeding expectations
2. **Verifiable:** Every requirement has objective acceptance criteria
3. **Comprehensive:** Covers code, tests, docs, architecture, connectivity, governance

**Success Definition:**
- **MUST** requirements: 100% completion (mandatory)
- **SHOULD** requirements: ≥80% completion (recommended)
- **MAY** requirements: ≥50% completion (exceeds expectations)

---

## R1: Foundation Fixes (v3.1.1)

**Duration:** ≤1 week
**Status:** MANDATORY (all MUST requirements)

### R1.1 Repository Hygiene

**R1.1.1 MUST: Create .gitignore**
- [ ] Create `.gitignore` file in repository root
- [ ] Include: `__pycache__/`, `*.pyc`, `.venv*/`, `reports/`, `benchmarks/results.json`, `state/`, `*.sarif`
- [ ] Remove tracked cache files: `git rm --cached -r __pycache__ .venv_tools`
- [ ] Commit: "Add .gitignore for Python cache and temp files"

**Acceptance Criteria:**
```bash
# Test
git status --porcelain | grep -E "__pycache__|\.pyc|\.venv" | wc -l
# Expected: 0 (no cache files tracked)
```

**R1.1.2 SHOULD: Document versions/ directory**
- [ ] Add `versions/README.md` explaining purpose
- [ ] Options: (a) Keep for historical reference, (b) Remove if redundant with git history
- [ ] If keeping: Document which version maps to which git tag

**R1.1.3 MAY: Clean git history**
- [ ] Use `git filter-repo` to remove large files from history
- [ ] Reduce repository size by ≥20%

---

### R1.2 Extract Magic Numbers

**R1.2.1 MUST: Create core/thresholds.py**
- [ ] Create `src/core/thresholds.py` module
- [ ] Extract ALL hardcoded numeric literals from detection code
- [ ] Group by category: profiles, Wu Lun weights, detection params

**Required Constants:**
```python
# core/thresholds.py

# Profile-based severity thresholds
PROFILE_THRESHOLDS = {
    'ci': {'error': 0.80, 'warn': 0.60},
    'ops': {'error': 0.75, 'warn': 0.55},
    'audit': {'error': 0.70, 'warn': 0.50},
    'research': {'error': 0.65, 'warn': 0.45},
    'forensics': {'error': 0.65, 'warn': 0.45}
}

# Wu Lun relationship weights
WULUN_WEIGHTS = {
    'pengyou': 0.85,    # 朋友 (friends) - user-password pairs
    'fufu': 0.75,       # 夫婦 (complementary) - key-endpoint pairs
    'junchin': 0.82,    # 君臣 (ruler-subject) - cert-authority chains
    'fuzi': 0.65,       # 父子 (generational) - token-session temporal
    'xiongdi': 0.60     # 兄弟 (siblings) - metadata-sibling clusters
}

# Detection parameters
ENTROPY_THRESHOLD = 4.5
MIN_TOKEN_LENGTH = 16
CONTEXT_RADIUS = 50        # chars around detection
MAX_FILE_BYTES = 5_000_000
SCAN_TIMEOUT_SECONDS = 5
```

**Acceptance Criteria:**
```bash
# Test: No magic numbers in main code
grep -n "0\.[0-9]" src/IF.yologuard_v3.py | wc -l
# Expected: ≤5 (only constants for algorithm logic, not thresholds)
```

**R1.2.2 SHOULD: Document weight rationale**
- [ ] Add docstring explaining why each weight has its value
- [ ] Example: "朋友 (0.85): User-password pairs are strongest signal (empirically validated on 1000-file corpus)"
- [ ] Mark as "To be calibrated in v3.3" if arbitrary

**R1.2.3 MAY: Make weights configurable**
- [ ] Allow weights to be overridden via config file (`config/weights.yaml`)
- [ ] Enable A/B testing of different weight combinations

---

### R1.3 Documentation Updates

**R1.3.1 MUST: Add installation section to README**
- [ ] Add "Installation" section near top of README.md
- [ ] Include: prerequisites (Python 3.10+), installation steps, quick test
- [ ] Time-to-hello-world: ≤5 minutes for new user

**Required Content:**
```markdown
## Installation

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### Install from source
\`\`\`bash
git clone https://github.com/dannystocker/infrafabric.git
cd infrafabric/code/yologuard
python3 -m pip install -r requirements.txt
\`\`\`

### Quick test
\`\`\`bash
python3 src/IF.yologuard_v3.py --scan benchmarks/leaky-repo --stats
# Expected: 107/96 detections in <0.5s
\`\`\`

### Verify installation
\`\`\`bash
python3 src/IF.yologuard_v3.py --version
# Output: IF.yologuard v3.1.1
\`\`\`
```

**Acceptance Criteria:**
- [ ] New user can install and run in <5 minutes (tested with 3 people)
- [ ] README links to requirements.txt (you must create this file)

**R1.3.2 MUST: Create requirements.txt**
- [ ] List all Python dependencies with version pins
- [ ] Test: Fresh virtualenv install should work without errors

**Required Dependencies** (minimum):
```
# requirements.txt
# No external dependencies for core functionality (standard library only)
# Optional dependencies for REST API, tests, etc.
pytest>=7.0         # For tests
pytest-cov>=4.0     # For coverage
fastapi>=0.104      # For REST API (optional)
uvicorn>=0.24       # For REST API (optional)
pydantic>=2.0       # For REST API (optional)
```

**R1.3.3 MUST: Mark PQ as experimental**
- [ ] Add "⚠️ EXPERIMENTAL" badge to Quantum Readiness section in README
- [ ] Disclaimer: "PQ analysis is in beta. QES scoring requires empirical calibration (planned v4)."
- [ ] Document limitations: "v1 uses string-based detection, not cryptographic analysis"

**R1.3.4 SHOULD: Update all version numbers**
- [ ] Consistent version numbers across: README, docstrings, `__version__`, CLI output
- [ ] Version: `3.1.1` for this phase

---

### R1.4 Create GitHub Issues

**R1.4.1 MUST: Create roadmap issues**
- [ ] Create GitHub issues for all commitments in `GUARDIAN_HANDOFF_v3.1_IEF.md`
- [ ] Minimum 6 issues required (from roadmap_commitments section)
- [ ] Each issue must have: title, description, acceptance criteria, labels, milestone

**Required Issues:**
1. "Calibrate Wu Lun weights empirically (2-4 weeks)" - label: `enhancement`, `v3.3`
2. "Update user docs for profiles/IEF/PQ" - label: `documentation`, `v3.2`
3. "30-day retrospective on adoption, FP rates" - label: `governance`, `v4.0`
4. "Enhanced IEF: stylometry, git history anomalies (4-6 weeks)" - label: `enhancement`, `v4.1`
5. "SBOM-aware PQ: version checks, dependency graph (6-8 weeks)" - label: `enhancement`, `v4.1`
6. "Cross-file relationships: env/config linking (8-10 weeks)" - label: `enhancement`, `v4.2`

**Acceptance Criteria:**
```bash
# Test
gh issue list --label roadmap --json number,title | jq 'length'
# Expected: ≥6
```

---

## R2: Modular Architecture (v3.2)

**Duration:** ≤3 weeks (10 business days)
**Status:** MANDATORY + RECOMMENDED

### R2.1 Module Extraction

**R2.1.1 MUST: Create 8+ modules**
- [ ] Create directory structure (see architecture diagram in GPT5_GOALS_ROADMAP.md)
- [ ] Extract code into: `patterns/`, `detection/`, `scoring/`, `frameworks/`, `output/`, `core/`, `api/`
- [ ] Each module: <300 lines (average), single responsibility

**Directory Structure (REQUIRED):**
```
src/
├── IF.yologuard_v3.py          # CLI entry point (<200 lines)
├── core/
│   ├── __init__.py
│   ├── scanner.py              # Main SecretScanner class
│   ├── thresholds.py           # From R1.2
│   └── profiles.py             # Profile definitions
├── patterns/
│   ├── __init__.py
│   ├── credentials.py          # AWS, GitHub, Slack, Stripe
│   ├── keys.py                 # RSA, SSH, API keys, PGP
│   ├── database.py             # Connection strings
│   ├── tokens.py               # JWT, session, bearer
│   └── registry.py             # Pattern management
├── detection/
│   ├── __init__.py
│   ├── matcher.py              # Regex matching
│   ├── decoder.py              # Base64/hex
│   ├── entropy.py              # Shannon entropy
│   └── deduplication.py        # Position-aware dedup
├── scoring/
│   ├── __init__.py
│   ├── wulun.py                # Wu Lun relationships
│   ├── aristotelian.py         # Essence classification
│   └── severity.py             # Final severity
├── frameworks/
│   ├── __init__.py
│   ├── ief.py                  # Immuno-Epistemic
│   ├── ttt.py                  # TTT provenance
│   └── pq.py                   # Quantum Readiness
├── output/
│   ├── __init__.py
│   ├── json_formatter.py
│   ├── sarif_formatter.py
│   ├── text_formatter.py
│   ├── manifest_writer.py
│   └── graph_exporter.py
└── api/
    ├── __init__.py
    ├── rest_server.py          # FastAPI (Phase 3)
    └── python_api.py           # Library interface
```

**Acceptance Criteria:**
```bash
# Test: Module count
find src -name "*.py" -type f | grep -v __pycache__ | wc -l
# Expected: ≥25 files (8 directories × ~3 files each)

# Test: Average lines per module
find src -name "*.py" -exec wc -l {} \; | awk '{sum+=$1; count++} END {print sum/count}'
# Expected: <300 lines

# Test: No circular dependencies
python3 -m pytest tests/test_no_circular_imports.py
# Expected: PASS
```

**R2.1.2 MUST: Maintain backward compatibility**
- [ ] Old import paths still work: `from IF.yologuard_v3 import SecretRedactorV3`
- [ ] New import paths preferred: `from core.scanner import SecretScanner`
- [ ] Deprecation warnings shown for old imports
- [ ] CLI usage identical: `python3 IF.yologuard_v3.py --scan /repo`

**R2.1.3 SHOULD: Create migration guide**
- [ ] Document: `docs/MIGRATION_v3.1_to_v3.2.md`
- [ ] Code examples for old → new imports
- [ ] Estimated migration time: <30 minutes for existing projects

---

### R2.2 Comprehensive Test Suite

**R2.2.1 MUST: Achieve 80%+ code coverage**
- [ ] Add pytest configuration: `tests/pytest.ini`
- [ ] Write tests for: patterns, detection, scoring, frameworks, output
- [ ] Coverage target: ≥80% line coverage

**Required Test Categories:**

**Unit Tests** (≥50 tests):
```python
# tests/test_patterns.py - Pattern matching tests
def test_aws_key_pattern()
def test_github_token_pattern()
def test_slack_token_pattern()
# ... 20+ pattern tests

# tests/test_entropy.py - Entropy detection tests
def test_shannon_entropy_low()
def test_shannon_entropy_high()
def test_high_entropy_token_detection()

# tests/test_wulun.py - Relationship detection tests
def test_user_password_relationship()
def test_key_endpoint_relationship()
def test_cert_authority_relationship()
def test_token_session_relationship()
def test_metadata_sibling_relationship()

# tests/test_scoring.py - Scoring tests
def test_confucian_relationship_score()
def test_severity_calculation()
def test_aristotelian_classification()
```

**Integration Tests** (≥20 tests):
```python
# tests/test_integration.py
def test_full_scan_pipeline()
def test_profile_thresholds_ci()
def test_profile_thresholds_forensics()
def test_json_output_format()
def test_sarif_output_format()
def test_manifest_generation()
def test_graph_export()
# ... 20+ integration tests
```

**Performance Tests** (≥10 tests):
```python
# tests/test_performance.py
def test_scan_time_under_500ms()
def test_no_memory_leaks()
def test_concurrent_scans()
def test_large_file_handling()
def test_pattern_compilation_cached()
```

**Edge Case Tests** (≥15 tests):
```python
# tests/test_edge_cases.py
def test_empty_file()
def test_binary_file()
def test_large_file_truncation()
def test_unicode_content()
def test_malformed_json()
def test_malformed_xml()
def test_redos_prevention()
# ... 15+ edge case tests
```

**Acceptance Criteria:**
```bash
# Test: Run full test suite
pytest tests/ --cov=src --cov-report=term-missing

# Expected output:
# =================== test session starts ====================
# collected 95 items (minimum)
# tests/test_patterns.py .................... [ 20%]
# tests/test_entropy.py ......... [ 30%]
# ...
# =================== 95 passed in 5.23s =====================
# TOTAL Coverage: 82% (minimum 80%)
```

**R2.2.2 SHOULD: Add falsifier corpus**
- [ ] Extend `tests/test_falsifiers.py` with ≥20 false positive test cases
- [ ] Categories: UUIDs, SHAs, benign base64, version numbers, random hex
- [ ] Target: 0 false positives on all falsifier tests

**R2.2.3 MAY: Add property-based tests**
- [ ] Use Hypothesis library for property-based testing
- [ ] Generate random inputs, verify invariants
- [ ] Example: "Any detected pattern must have length ≥ MIN_TOKEN_LENGTH"

---

### R2.3 CI/CD Pipeline

**R2.3.1 MUST: Create GitHub Actions workflow**
- [ ] Create `.github/workflows/if-yologuard-ci.yml`
- [ ] Run on: push, pull_request
- [ ] Test matrix: Python 3.10, 3.11, 3.12
- [ ] Gates: tests, benchmark, performance, security

**Required Workflow Jobs:**

**Job 1: Test**
```yaml
test:
  runs-on: ubuntu-latest
  strategy:
    matrix:
      python-version: ['3.10', '3.11', '3.12']
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
    - run: pip install -r requirements.txt pytest pytest-cov
    - run: pytest tests/ --cov=src --cov-report=xml
    - run: |
        COVERAGE=$(grep -oP 'line-rate="\K[0-9.]+' coverage.xml | head -1)
        if (( $(echo "$COVERAGE < 0.80" | bc -l) )); then
          echo "FAIL: Coverage $COVERAGE < 80%"
          exit 1
        fi
```

**Job 2: Benchmark** (MUST pass ≥95/96)
```yaml
benchmark:
  needs: test
  steps:
    - run: python3 benchmarks/run_leaky_repo_v3_philosophical_fast_v2.py > output.txt
    - run: |
        DETECTIONS=$(grep "v3 detected:" output.txt | awk '{print $3}' | cut -d'/' -f1)
        if [ "$DETECTIONS" -lt 95 ]; then
          echo "FAIL: Only $DETECTIONS/96"
          exit 1
        fi
```

**Job 3: Performance** (MUST complete <0.5s)
```yaml
performance:
  needs: benchmark
  steps:
    - run: |
        TIME=$(time -p python3 src/IF.yologuard_v3.py --scan benchmarks/leaky-repo 2>&1 | grep real | awk '{print $2}')
        if (( $(echo "$TIME > 0.5" | bc -l) )); then
          echo "FAIL: Scan took ${TIME}s (expected <0.5s)"
          exit 1
        fi
```

**Job 4: Security Scan** (SHOULD have 0 high/medium issues)
```yaml
security:
  steps:
    - run: pip install bandit safety
    - run: bandit -r src/ -ll  # High/medium severity only
    - run: safety check --json
```

**Acceptance Criteria:**
- [ ] CI badge in README: ![CI](https://github.com/.../workflows/if-yologuard-ci/badge.svg)
- [ ] All jobs pass on master branch
- [ ] PRs blocked until CI passes

**R2.3.2 SHOULD: Add code quality tools**
- [ ] Linting: `flake8` or `pylint`
- [ ] Formatting: `black` (auto-format on commit)
- [ ] Type checking: `mypy` (optional, for type hints)

**R2.3.3 MAY: Add performance regression tracking**
- [ ] Store benchmark results in git (benchmarks/results_history.json)
- [ ] Fail CI if scan time increases >10%
- [ ] Fail CI if detections decrease below 95/96

---

## R3: Calibration & REST API (v3.3)

**Duration:** ≤1 week
**Status:** HIGHLY RECOMMENDED

### R3.1 Empirical Weight Calibration

**R3.1.1 SHOULD: Curate 1000-file corpus**
- [ ] Collect 1000 files: 500 clean, 500 with secrets
- [ ] Sources: leaky-repo (96), GitHub commits (search "remove password"), SecLists, synthetic
- [ ] Label ground truth: exact secret locations for each file
- [ ] Split: 700 training, 300 test

**R3.1.2 SHOULD: Implement grid search**
- [ ] Create `harness/calibrate_weights.py`
- [ ] Search over weight ranges (see GPT5_GOALS_ROADMAP.md for details)
- [ ] Optimize for F1 score (balance precision/recall)
- [ ] Target: F1 ≥0.95 on test set

**R3.1.3 SHOULD: Update thresholds**
- [ ] Replace arbitrary weights in `core/thresholds.py` with calibrated values
- [ ] Document: "Calibrated on 1000-file corpus on [date], F1=0.XX"
- [ ] Run benchmark: verify ≥107/96 maintained

**Acceptance Criteria:**
```bash
# Test: Run calibration
python3 harness/calibrate_weights.py --corpus data/calibration_corpus/

# Expected output:
# Grid search: 1024 combinations tested
# Best weights: {pengyou: 0.87, fufu: 0.74, junchin: 0.83, fuzi: 0.66, xiongdi: 0.61}
# F1 score: 0.96 (train), 0.94 (test)
# Improvement: +2.3% over baseline

# Test: Benchmark with new weights
python3 benchmarks/run_leaky_repo_v3_philosophical_fast_v2.py
# Expected: ≥107/96 (no regression)
```

**R3.1.4 MAY: A/B test in production**
- [ ] Deploy both old and new weights
- [ ] Route 50% of traffic to each
- [ ] Measure FP rate difference over 1 week
- [ ] Choose winner based on data

---

### R3.2 REST API Implementation

**R3.2.1 MUST: Implement FastAPI server**
- [ ] Create `api/rest_server.py` with FastAPI
- [ ] Endpoints: `/scan`, `/scan/file`, `/health`, `/patterns`, `/profiles`
- [ ] Authentication: Bearer token (simple static key for v3.3, JWT in v4+)
- [ ] Auto-generated docs: `/docs` (Swagger UI), `/redoc` (ReDoc)

**Required Endpoints:**

**POST /scan** (MUST):
```python
@app.post("/scan", response_model=ScanResponse)
async def scan_content(request: ScanRequest, credentials: HTTPAuthorizationCredentials = security):
    """Scan text content for secrets"""
    # Validate API key
    if not _validate_api_key(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Scan
    scanner = SecretScanner(profile=request.profile, mode=request.mode)
    detections = scanner.scan_content(request.content, request.filename)

    return ScanResponse(
        status="success",
        detections=detections,
        metadata={'count': len(detections), 'profile': request.profile}
    )
```

**POST /scan/file** (MUST):
```python
@app.post("/scan/file", response_model=ScanResponse)
async def scan_file(file: UploadFile, profile: str = "ci", mode: str = "both", credentials: HTTPAuthorizationCredentials = security):
    """Scan uploaded file"""
    # Validate size (<5MB)
    content = await file.read()
    if len(content) > 5_000_000:
        raise HTTPException(status_code=413, detail="File too large (max 5MB)")

    # Scan
    text = content.decode('utf-8', errors='ignore')
    scanner = SecretScanner(profile=profile, mode=mode)
    detections = scanner.scan_content(text, file.filename)

    return ScanResponse(...)
```

**GET /health** (MUST):
```python
@app.get("/health")
async def health_check():
    """Health check for load balancers"""
    return {
        "status": "healthy",
        "version": "3.3",
        "patterns": len(PatternRegistry.list()),
        "profiles": ["ci", "ops", "audit", "research", "forensics"]
    }
```

**GET /patterns** (SHOULD):
```python
@app.get("/patterns")
async def list_patterns(credentials: HTTPAuthorizationCredentials = security):
    """List all detection patterns"""
    return {
        "patterns": PatternRegistry.get_metadata(),
        "count": len(PatternRegistry.list())
    }
```

**Acceptance Criteria:**
```bash
# Test: Start server
python3 -m uvicorn api.rest_server:app --host 0.0.0.0 --port 8082 &

# Test: Health check
curl http://localhost:8082/health
# Expected: {"status": "healthy", "version": "3.3", ...}

# Test: Scan
curl -X POST http://localhost:8082/scan \
  -H "Authorization: Bearer sk-yologuard-dev-12345" \
  -H "Content-Type: application/json" \
  -d '{"content": "AWS_KEY=AKIAIOSFODNN7EXAMPLE", "profile": "ci"}'
# Expected: {"status": "success", "detections": [{...}], ...}

# Test: OpenAPI docs
curl http://localhost:8082/docs
# Expected: HTML page (Swagger UI)
```

**R3.2.2 MUST: Add --serve CLI flag**
- [ ] Extend CLI: `python3 IF.yologuard_v3.py --serve --port 8082`
- [ ] Support TLS: `--tls-cert server.pem --tls-key server-key.pem`
- [ ] Graceful shutdown on SIGTERM

**R3.2.3 SHOULD: Performance test**
- [ ] Load test with Apache Bench: `ab -n 1000 -c 10 http://localhost:8082/scan`
- [ ] Target: ≥100 requests/second, p95 latency <100ms

**R3.2.4 SHOULD: Add rate limiting**
- [ ] Rate limit: 100 requests/minute per API key
- [ ] Return 429 (Too Many Requests) when exceeded
- [ ] Use Redis for distributed rate limiting (optional)

**R3.2.5 MAY: Add streaming API**
- [ ] WebSocket endpoint for real-time scanning
- [ ] Server-Sent Events (SSE) for long-running scans
- [ ] gRPC streaming for internal services

---

## R4: Rebranding (v4.0)

**Duration:** ≤1 week
**Status:** STRATEGIC (mandatory for IF.armour positioning)

### R4.1 File & Module Renaming

**R4.1.1 MUST: Create armour/ directory**
- [ ] Create `src/armour/` directory structure
- [ ] Move yologuard modules into `src/armour/yologuard/`
- [ ] Prepare for honeypot, learner modules: `src/armour/honeypot/`, `src/armour/learner/`

**Target Structure:**
```
src/
├── armour/
│   ├── __init__.py           # "from armour import yologuard, honeypot, learner"
│   ├── yologuard/            # Detection pillar
│   │   ├── __init__.py
│   │   ├── core/
│   │   ├── patterns/
│   │   ├── detection/
│   │   ├── scoring/
│   │   ├── frameworks/
│   │   ├── output/
│   │   └── api/
│   ├── honeypot/             # Deception pillar (stub for v4.1)
│   │   └── __init__.py
│   └── learner/              # Intelligence pillar (stub for v4.2)
│       └── __init__.py
├── IF.armour.yologuard.py    # New CLI entry point
└── IF.yologuard_v3.py        # Deprecated wrapper (backward compat)
```

**R4.1.2 MUST: Maintain backward compatibility**
- [ ] Old imports work: `from IF.yologuard_v3 import SecretRedactorV3`
- [ ] Deprecation warning shown
- [ ] Old CLI works: `python3 IF.yologuard_v3.py --scan /repo`
- [ ] New CLI preferred: `if-armour yologuard --scan /repo`

**R4.1.3 MUST: Create CLI command**
- [ ] Install as package: `pip install -e .` creates `if-armour` command
- [ ] Usage: `if-armour yologuard --scan /repo --profile ci`
- [ ] Usage: `if-armour yologuard --serve --port 8082`
- [ ] Usage: `if-armour yologuard --version` → "IF.armour.yologuard v4.0"

**Acceptance Criteria:**
```bash
# Test: Old import (backward compat)
python3 -c "from IF.yologuard_v3 import SecretRedactorV3; print('OK')"
# Expected: DeprecationWarning + OK

# Test: New import
python3 -c "from armour.yologuard import SecretScanner; print('OK')"
# Expected: OK (no warning)

# Test: CLI command
if-armour yologuard --version
# Expected: IF.armour.yologuard v4.0 (Secret Detection Pillar)
```

---

### R4.2 Documentation Update

**R4.2.1 MUST: Update README to explain 3-pillar vision**
- [ ] Lead with IF.armour vision (3 pillars)
- [ ] Position yologuard as "detection pillar"
- [ ] Mention honeypot + learner as "coming soon"
- [ ] Update all code examples to use new imports

**Required Sections:**
```markdown
# IF.armour - Autonomous AI Security Suite

IF.armour is a **self-improving security suite** with three pillars:

## 1. IF.armour.yologuard - Secret Detection ✅ (v4.0 - Production Ready)
- **111.5% recall** (107/96 detections on Leaky Repo benchmark)
- **Wu Lun relationship scoring** (contextual severity)
- **IEF + TTT + PQ frameworks** (forensics-grade)
- **5 audience profiles** (ci/ops/audit/research/forensics)

## 2. IF.armour.honeypot - Attacker Deception 🚧 (v4.1 - Coming Soon)
- **Deploy honeytokens** (fake secrets that detect attackers)
- **Profile attackers** (IP, tools, techniques)
- **Tarpit responses** (waste attacker resources)

## 3. IF.armour.learner - Threat Intelligence 🔮 (v4.2 - Planned)
- **Scrape threat intel** (YouTube, GitHub, CVEs)
- **Auto-generate patterns** (LLM-powered synthesis)
- **Recursive improvement** (A/B test, deploy best patterns)

## Quick Start

### Detect Secrets
\`\`\`bash
if-armour yologuard --scan /repo --profile ci
\`\`\`

### Start REST API
\`\`\`bash
if-armour yologuard --serve --port 8082
\`\`\`

### Python API
\`\`\`python
from armour.yologuard import SecretScanner

scanner = SecretScanner(profile='forensics')
secrets = scanner.scan_file(Path('/repo/.env'))

for secret in secrets:
    print(f"{secret['pattern']} at {secret['file']}:{secret['line']}")
\`\`\`
```

**R4.2.2 SHOULD: Create architecture diagram**
- [ ] Visual diagram showing 3 pillars + IF.* integrations
- [ ] Format: Mermaid diagram (renders on GitHub), or PNG
- [ ] Include: IF.search, IF.swarm, IF.guard, IF.optimise connections

**R4.2.3 MAY: Create video walkthrough**
- [ ] 5-minute screencast demonstrating IF.armour
- [ ] Upload to YouTube
- [ ] Embed in README

---

## R5: IF.connect Integration (v4.0+)

**Duration:** Ongoing (parallel with R4)
**Status:** FOUNDATIONAL (enables v5.0 IF.* integration)

### R5.1 Implement IF.connect Protocol

**R5.1.1 MUST: Create IF.connect message format**
- [ ] Implement `IFMessage` class (see IF_CONNECTIVITY_ARCHITECTURE.md)
- [ ] Support: sender, receiver, operation, payload, provenance, connection_type, constraints
- [ ] Serialization: to_dict(), from_dict() for JSON/gRPC/MQ transport

**R5.1.2 MUST: Add TTT provenance to all operations**
- [ ] Every scan includes: timestamp, commit, version, trace_id
- [ ] Provenance tracked through IF.connect message chain
- [ ] Audit log: append-only, includes all IF.connect messages

**R5.1.3 SHOULD: Support multiple transports**
- [ ] Transport abstraction: REST, gRPC, Message Queue
- [ ] Transport selection: based on IF.optimise recommendation (cost, latency)
- [ ] Fallback: REST if gRPC unavailable

**Acceptance Criteria:**
```python
# Test: Create IF.connect message
from IF.connect import IFMessage, ConnectionType

message = IFMessage(
    sender='IF.armour.yologuard',
    receiver='IF.swarm',
    operation='validate_pattern',
    payload={'pattern': 'aws_key', 'regex': r'AKIA[0-9A-Z]{16}'},
    connection_type=ConnectionType.PENGYOU,
    provenance={'timestamp': '2025-11-08T12:00:00Z', 'trace_id': 'abc123'}
)

# Serialize
message_dict = message.to_dict()
assert 'sender' in message_dict
assert 'provenance' in message_dict

# Deserialize
restored = IFMessage.from_dict(message_dict)
assert restored.sender == 'IF.armour.yologuard'
```

**R5.1.4 MAY: Implement gRPC protocol**
- [ ] Create `IF.armour.proto` (protobuf schema)
- [ ] gRPC services: YologuardService, HoneypotService, LearnerService
- [ ] Benefits: 10× faster than REST for internal communication

---

### R5.2 Wu Lun Relationship Typing

**R5.2.1 SHOULD: Tag all inter-module connections**
- [ ] Identify relationship type for each module-to-module connection
- [ ] Use ConnectionType enum: PENGYOU, FUFU, JUNCHIN, FUZI, XIONGDI
- [ ] Document in module docstrings

**Example:**
```python
# core/scanner.py

from detection.matcher import PatternMatcher
from scoring.wulun import WuLunScorer

class SecretScanner:
    """
    Main scanner - orchestrates detection pipeline

    Wu Lun Relationships:
    - 朋友 (PENGYOU) with PatternMatcher - equal peers in detection
    - 朋友 (PENGYOU) with WuLunScorer - equal peers in analysis
    - 君臣 (JUNCHIN) with OutputFormatters - hierarchical control
    """
```

**R5.2.2 MAY: Use relationships for error handling**
- [ ] 朋友 (friends): Retry failures (trust relationship)
- [ ] 君臣 (hierarchical): Fail fast (strict control)
- [ ] 父子 (generational): Queue for later (async, tolerant)

---

## Success Criteria Summary

### Phase 1 (v3.1.1) - Week 1
- ✅ MUST: .gitignore created, magic numbers extracted, installation docs added
- ✅ SHOULD: versions/ documented, weights rationale added
- ✅ MAY: Git history cleaned, weights configurable

### Phase 2 (v3.2) - Weeks 2-3
- ✅ MUST: ≥8 modules, 80%+ test coverage, CI/CD pipeline green
- ✅ SHOULD: Falsifier corpus extended, code quality tools added
- ✅ MAY: Property-based tests, performance regression tracking

### Phase 3 (v3.3) - Week 4
- ✅ SHOULD: Weights calibrated (F1 ≥0.95), REST API implemented
- ✅ MUST: FastAPI endpoints working, CLI --serve flag added
- ✅ MAY: Load tested (≥100 req/sec), rate limiting, streaming API

### Phase 4 (v4.0) - Week 5
- ✅ MUST: Rebranded to IF.armour.yologuard, CLI command created
- ✅ MUST: README updated with 3-pillar vision
- ✅ SHOULD: Architecture diagram, migration guide
- ✅ MAY: Video walkthrough

### Phase 5 (v4.0+) - Ongoing
- ✅ MUST: IF.connect message format implemented, TTT provenance added
- ✅ SHOULD: Multiple transports supported, Wu Lun relationships tagged
- ✅ MAY: gRPC protocol, relationship-aware error handling

---

## Definition of "Exceeded"

**Minimum Passing Grade:** 100% MUST + 80% SHOULD + 50% MAY = **B+ grade**

**Exceeded Expectations:** 100% MUST + 100% SHOULD + 80% MAY = **A+ grade**

**Bonus Points (beyond MAY requirements):**
- Implement IF.armour.honeypot prototype (Phase 5, v4.1)
- Implement IF.armour.learner prototype (Phase 6, v4.2)
- Deploy to production (Docker image + Kubernetes)
- Achieve ≥90% test coverage (target is 80%)
- Scan time <0.1s (target is <0.2s)
- REST API ≥200 req/sec (target is 100 req/sec)

---

## Verification Checklist

Use this checklist to verify completion:

**Phase 1 (v3.1.1):**
- [ ] `git status` shows no cache files
- [ ] `grep "0\.[0-9]" src/IF.yologuard_v3.py | wc -l` ≤5
- [ ] New user installs in <5 minutes
- [ ] `gh issue list --label roadmap | wc -l` ≥6

**Phase 2 (v3.2):**
- [ ] `find src -name "*.py" | wc -l` ≥25
- [ ] `pytest --cov=src | grep TOTAL` ≥80%
- [ ] GitHub Actions badge is green
- [ ] `python3 benchmarks/run_leaky_repo_v3_philosophical_fast_v2.py` shows 107/96

**Phase 3 (v3.3):**
- [ ] `python3 harness/calibrate_weights.py` shows F1 ≥0.95
- [ ] `curl http://localhost:8082/health` returns JSON
- [ ] `ab -n 1000 -c 10 http://localhost:8082/scan` ≥100 req/sec

**Phase 4 (v4.0):**
- [ ] `if-armour yologuard --version` works
- [ ] README explains 3-pillar vision
- [ ] Old imports show deprecation warnings

**Phase 5 (IF.connect):**
- [ ] `IFMessage.to_dict()` / `from_dict()` round-trips correctly
- [ ] All scans include TTT provenance

---

## Handoff to GPT-5/Codex

**You have:**
- Clear requirements (MUST/SHOULD/MAY)
- Objective acceptance criteria (bash commands, expected outputs)
- Success definition ("exceeded" = A+ grade)

**Your mission:**
- Transform IF.yologuard v3.1 (production-ready) → IF.armour v4.0 (modular, calibrated, REST API, rebranded)
- Set foundation for IF.armour v5.0 (full IF.* integration: swarm, guard, optimise, search)

**Timeline:** 5 weeks maximum (4 weeks recommended to exceed expectations)

**Go build the future of autonomous AI security.** 🚀
