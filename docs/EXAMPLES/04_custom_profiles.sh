#!/bin/bash
# Example 04: Compare different scan profiles (ci vs forensics)
#
# This example demonstrates:
# - The --profile ci preset (fast, strict)
# - The --profile forensics preset (comprehensive, slow)
# - Performance differences between profiles
# - When to use each profile
# - How to customize thresholds manually
#
# Profiles available: ci, ops, audit, research, forensics

set -euo pipefail

PROJECT_ROOT=$(git rev-parse --show-toplevel)
YOLOGUARD="${PROJECT_ROOT}/code/yologuard/src/IF.yologuard_v3.py"

# Create test directory
TEST_DIR=$(mktemp -d)
trap "rm -rf $TEST_DIR" EXIT

echo "=== IF.yologuard Profile Comparison ==="
echo ""

# Create a test repository with various files
mkdir -p "$TEST_DIR/src" "$TEST_DIR/config" "$TEST_DIR/tests" "$TEST_DIR/.git"

# Create test files with secrets at different entropy levels
cat > "$TEST_DIR/src/main.py" << 'EOF'
# High entropy token (likely secret)
token = "sk-proj-v0_8Yt7Q4_SiP9WkJqRxMnOpQrStUvWxYz1A2B3C4D5E6F7G8H9I0J1K2L3M"

# Medium entropy (ambiguous)
config_key = "my-app-config-key-v1"

# Database URL with credentials
db_url = "postgresql://admin:P@ssw0rd123!@db.example.com:5432/myapp"
EOF

cat > "$TEST_DIR/config/settings.json" << 'EOF'
{
  "api_endpoints": {
    "production": "https://api.example.com",
    "staging": "https://staging-api.example.com"
  },
  "credentials": {
    "webhook_secret": "whsec_0123456789abcdefghijklmnopqrstuv",
    "api_key": "ghp_16Character1234567890AbCdEfGhIjK"
  }
}
EOF

cat > "$TEST_DIR/tests/test_auth.py" << 'EOF'
import unittest

class TestAuth(unittest.TestCase):
    def test_login(self):
        # Test credentials (these might be detected)
        username = "testuser@example.com"
        password = "TestPass123!"
        # real_api_key = "sk-test-1234567890abcdefghijklmnop"
        self.assertTrue(True)
EOF

# Add some large files to test performance
for i in {1..5}; do
  dd if=/dev/zero of="$TEST_DIR/data_${i}.bin" bs=1M count=1 2>/dev/null
done

echo "Test directory structure:"
find "$TEST_DIR" -type f | head -15
echo ""

# Profile definitions
declare -A PROFILES
PROFILES=(
  ["ci"]="Fast, strict - for GitHub Actions, GitLab CI"
  ["ops"]="Operations - balance speed and coverage"
  ["audit"]="Compliance/audit - thorough with moderate thresholds"
  ["research"]="Research - detailed analysis, slower"
  ["forensics"]="Maximum coverage - comprehensive, slowest"
)

# Run scans with different profiles
echo "=== Running Scans with Different Profiles ==="
echo ""

for profile in ci forensics; do
  echo ">>> Profile: $profile"
  echo "    Description: ${PROFILES[$profile]}"
  echo ""

  START_TIME=$(date +%s%N)

  python3 "$YOLOGUARD" \
    --scan "$TEST_DIR" \
    --profile "$profile" \
    --json "${TEST_DIR}/scan_${profile}.json" \
    --sarif "${TEST_DIR}/scan_${profile}.sarif" \
    --stats 2>&1 | tee "${TEST_DIR}/output_${profile}.log"

  END_TIME=$(date +%s%N)
  DURATION_MS=$(( (END_TIME - START_TIME) / 1000000 ))

  echo ""
  echo "    Duration: ${DURATION_MS}ms"
  echo ""

  # Parse results
  if [ -f "${TEST_DIR}/scan_${profile}.json" ]; then
    python3 << PYEOF
import json
with open('${TEST_DIR}/scan_${profile}.json', 'r') as f:
    data = json.load(f)
    if 'detections' in data:
        detections = data['detections']
        errors = [d for d in detections if d.get('severity') == 'ERROR']
        warnings = [d for d in detections if d.get('severity') == 'WARNING']
        info = [d for d in detections if d.get('severity') == 'INFO']
        print(f'    Total detections: {len(detections)}')
        print(f'      - ERROR: {len(errors)}')
        print(f'      - WARNING: {len(warnings)}')
        print(f'      - INFO: {len(info)}')
PYEOF
  fi
  echo ""
done

echo "=== Profile Settings Reference ==="
echo ""
echo "Profile  | Error Threshold | Warn Threshold | Mode          | Use Case"
echo "---------|-----------------|----------------|---------------|----------------------------------"
echo "ci       | 0.75 (strict)   | 0.50           | both          | CI/CD, quick feedback"
echo "ops      | 0.70            | 0.45           | both          | Operations, production"
echo "audit    | 0.70            | 0.40           | both          | Compliance, audits"
echo "research | 0.60 (loose)    | 0.40           | both          | Research, analysis"
echo "forensics| 0.65            | 0.45           | both          | Deep investigation"
echo ""

echo "=== Output Comparison ==="
echo ""

if [ -f "${TEST_DIR}/scan_ci.json" ] && [ -f "${TEST_DIR}/scan_forensics.json" ]; then
  echo "CI Profile - First detection:"
  python3 -c "
import json
try:
    with open('${TEST_DIR}/scan_ci.json', 'r') as f:
        data = json.load(f)
        if data.get('detections'):
            det = data['detections'][0]
            print(f'  Category: {det.get(\"category\")}')
            print(f'  Severity: {det.get(\"severity\")}')
            print(f'  Score: {det.get(\"relationship_score\", det.get(\"score\"))}')
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null || echo "  Could not parse"
  echo ""

  echo "Forensics Profile - First detection:"
  python3 -c "
import json
try:
    with open('${TEST_DIR}/scan_forensics.json', 'r') as f:
        data = json.load(f)
        if data.get('detections'):
            det = data['detections'][0]
            print(f'  Category: {det.get(\"category\")}')
            print(f'  Severity: {det.get(\"severity\")}')
            print(f'  Score: {det.get(\"relationship_score\", det.get(\"score\"))}')
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null || echo "  Could not parse"
fi

echo ""
echo "=== When to Use Each Profile ==="
echo ""
echo "CI (--profile ci):"
echo "  - Fast execution (seconds)"
echo "  - GitHub Actions, GitLab CI, Jenkins"
echo "  - High threshold (0.75) = fewer false positives"
echo "  - Catches obvious secrets quickly"
echo "  - Ideal for: Pull request checks"
echo ""
echo "Forensics (--profile forensics):"
echo "  - Comprehensive scanning (minutes)"
echo "  - Deep security investigations"
echo "  - Lower threshold (0.65) = catches subtle patterns"
echo "  - Relationship-based validation"
echo "  - Ideal for: Post-incident analysis, compliance audits"
echo ""
echo "Custom Thresholds:"
echo "  - Override profiles with --error-threshold and --warn-threshold"
echo "  - Example: ultra-strict CI"
echo "    python3 code/yologuard/src/IF.yologuard_v3.py --scan . --profile ci --error-threshold 0.85 --warn-threshold 0.70"
echo ""

echo "=== SARIF File Size Comparison ==="
if [ -f "${TEST_DIR}/scan_ci.sarif" ]; then
  CI_SIZE=$(stat -f%z "${TEST_DIR}/scan_ci.sarif" 2>/dev/null || stat -c%s "${TEST_DIR}/scan_ci.sarif" 2>/dev/null || echo "?")
  echo "CI SARIF: $CI_SIZE bytes"
fi
if [ -f "${TEST_DIR}/scan_forensics.sarif" ]; then
  FORENSICS_SIZE=$(stat -f%z "${TEST_DIR}/scan_forensics.sarif" 2>/dev/null || stat -c%s "${TEST_DIR}/scan_forensics.sarif" 2>/dev/null || echo "?")
  echo "Forensics SARIF: $FORENSICS_SIZE bytes"
fi

echo ""
echo "=== Expected Output ==="
echo ""
echo "You should observe:"
echo ""
echo "1. Timing Comparison (duration in milliseconds):"
echo "   >>> Profile: ci"
echo "       Duration: ~500-1500ms"
echo "       Total detections: 4-6"
echo "   >>> Profile: forensics"
echo "       Duration: ~2000-5000ms (2-3x slower)"
echo "       Total detections: 6-10 (more detections)"
echo ""
echo "2. Detection Count Differences:"
echo "   CI Mode (strict, 0.75 threshold):"
echo "     - Total detections: ~4"
echo "     - ERROR: 2-3"
echo "     - WARNING: 1-2"
echo "     - INFO: 0"
echo ""
echo "   Forensics Mode (comprehensive, 0.65 threshold):"
echo "     - Total detections: ~8"
echo "     - ERROR: 3-4"
echo "     - WARNING: 3-4"
echo "     - INFO: 1-2"
echo ""
echo "3. Sample detection structure:"
echo "   {"
echo "     \"file_path\": \"src/main.py\","
echo "     \"line_number\": 2,"
echo "     \"category\": \"API Token\","
echo "     \"severity\": \"ERROR\","
echo "     \"relationship_score\": 0.92"
echo "   }"
echo ""
echo "4. SARIF file size comparison:"
echo "   CI SARIF: ~2000-5000 bytes"
echo "   Forensics SARIF: ~5000-15000 bytes (larger due to more detections)"
echo ""
echo ""
echo "=== What To Do If It Fails ==="
echo ""
echo "Issue: Both profiles show same number of detections"
echo "  → Verify --profile flag is being used: grep 'profile' command output"
echo "  → Check JSON files exist: ls -lah ${TEST_DIR}/scan_*.json"
echo "  → Forensics may not find more if thresholds overlap"
echo "  → Try creating a test directory with more files: add 10+ MB files"
echo ""
echo "Issue: Forensics profile is not slower than CI"
echo "  → Forensics needs larger test set to show time difference"
echo "  → Verify test directory size: du -sh $TEST_DIR"
echo "  → Try with actual source code repo (not small test files)"
echo ""
echo "Issue: Detection counts are zero or very low"
echo "  → Verify test files have actual secret patterns"
echo "  → Check if file encoding is valid: file ${TEST_DIR}/src/main.py"
echo "  → Re-run with --verbose to see why detections were skipped"
echo ""
echo "Issue: Profile settings don't match the reference table"
echo "  → Profiles may be customized in your installation"
echo "  → Check profile definitions: grep -r 'profile.*ci' code/yologuard/"
echo "  → List available profiles: python3 $YOLOGUARD --help | grep profile"
echo ""
echo "Issue: JSON parsing fails or structure is unexpected"
echo "  → Validate JSON: python3 -m json.tool < ${TEST_DIR}/scan_ci.json"
echo "  → Field names may vary by version: check 'severity' vs 'level'"
echo "  → Re-run with --format json-simple for cleaner output"
echo ""
echo "How to verify the example ran correctly:"
echo "  1. Both scan files exist: [ -f ${TEST_DIR}/scan_ci.json ] && echo 'CI JSON OK'"
echo "  2. Both are valid JSON: for f in ${TEST_DIR}/scan_*.json; do python3 -m json.tool < \$f > /dev/null && echo \$f; done"
echo "  3. Forensics found more: echo \"CI: \$(jq '.detections | length' ${TEST_DIR}/scan_ci.json) vs Forensics: \$(jq '.detections | length' ${TEST_DIR}/scan_forensics.json)\""
echo "  4. Timing shows difference: grep 'Duration:' output_*.log"
echo ""
