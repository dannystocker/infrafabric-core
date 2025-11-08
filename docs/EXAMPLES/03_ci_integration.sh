#!/bin/bash
# Example 03: GitHub Actions CI/CD integration with IF.yologuard
#
# This example demonstrates how to:
# - Integrate IF.yologuard into GitHub Actions
# - Install dependencies in CI environment
# - Scan repository for secrets
# - Fail the workflow if ERROR-level secrets are found
# - Upload SARIF results to GitHub Security tab
# - Handle different exit codes
#
# This script mimics what would run in a GitHub Actions workflow.
# See .github/workflows/yologuard-scan.yml for the actual workflow.

set -euo pipefail

echo "=== IF.yologuard GitHub Actions Example ==="
echo ""
echo "This script demonstrates the CI/CD integration pattern."
echo "In a real GitHub Actions workflow, you would use:"
echo ""
echo "  name: Secret Detection"
echo "  on: [push, pull_request]"
echo "  jobs:"
echo "    scan:"
echo "      runs-on: ubuntu-latest"
echo "      steps:"
echo "        - uses: actions/checkout@v4"
echo "        - uses: actions/setup-python@v5"
echo "          with:"
echo "            python-version: '3.11'"
echo "        - name: Install dependencies"
echo "          run: python3 -m pip install -q --upgrade pip"
echo "        - name: Run secret scan"
echo "          run: |"
echo "            python3 code/yologuard/src/IF.yologuard_v3.py \\"
echo "              --scan . \\"
echo "              --profile ci \\"
echo "              --sarif scan.sarif \\"
echo "              --json scan.json \\"
echo "              --stats \\"
echo "              --error-threshold 0.75"
echo "        - name: Upload to GitHub Security"
echo "          uses: github/codeql-action/upload-sarif@v2"
echo "          if: always()"
echo "          with:"
echo "            sarif_file: scan.sarif"
echo ""

# Simulate the workflow locally
PROJECT_ROOT=$(git rev-parse --show-toplevel)
YOLOGUARD="${PROJECT_ROOT}/code/yologuard/src/IF.yologuard_v3.py"

# Create a minimal test repo
TEST_REPO=$(mktemp -d)
trap "rm -rf $TEST_REPO" EXIT

echo "=== Simulating GitHub Actions Environment ==="
echo "Working directory: $TEST_REPO"
echo ""

# Initialize test repo
cd "$TEST_REPO"
git init
git config user.email "test@example.com"
git config user.name "Test User"

# Create test files with secrets
mkdir -p src config
cat > src/main.py << 'EOF'
# AWS credentials accidentally committed
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# This should be caught
api_key = "sk-proj-1234567890abcdefghijklmnop"
EOF

cat > config/database.yml << 'EOF'
production:
  host: postgres.example.com
  user: admin
  password: SuperSecretPassword123!
EOF

cat > .gitignore << 'EOF'
.env
*.key
node_modules/
EOF

git add .
git commit -m "Initial commit"

echo "Test repository created with intentional secrets"
echo ""

echo "=== Step 1: Check Python Environment ==="
python3 --version
echo ""

echo "=== Step 2: Run Secret Scan (profile: ci) ==="
echo "Command: python3 $YOLOGUARD --scan . --profile ci --sarif scan.sarif --json scan.json --stats --error-threshold 0.75"
echo ""

# Run the scan
EXIT_CODE=0
python3 "$YOLOGUARD" \
  --scan . \
  --profile ci \
  --sarif scan.sarif \
  --json scan.json \
  --stats \
  --error-threshold 0.75 || EXIT_CODE=$?

echo ""
echo "=== Step 3: Check Exit Code ==="
echo "Exit code: $EXIT_CODE"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
  echo "✓ No ERROR-level secrets detected (scan passed)"
  SCAN_RESULT="PASSED"
elif [ $EXIT_CODE -eq 1 ]; then
  echo "✗ ERROR-level secrets found (scan failed)"
  SCAN_RESULT="FAILED"
elif [ $EXIT_CODE -eq 2 ]; then
  echo "⚠ WARNING-level secrets found (check thresholds)"
  SCAN_RESULT="WARNINGS"
else
  echo "? Unexpected exit code"
  SCAN_RESULT="ERROR"
fi

echo ""
echo "=== Step 4: SARIF Output (for GitHub Security tab) ==="
if [ -f scan.sarif ]; then
  echo "✓ scan.sarif created successfully"
  echo "First 30 lines:"
  head -30 scan.sarif
  echo "... (truncated)"
else
  echo "✗ scan.sarif not found"
fi

echo ""
echo "=== Step 5: JSON Output (for programmatic processing) ==="
if [ -f scan.json ]; then
  echo "✓ scan.json created successfully"
  python3 -c "
import json
with open('scan.json', 'r') as f:
    data = json.load(f)
    if 'detections' in data:
        print(f'Total detections: {len(data[\"detections\"])}')
        errors = [d for d in data['detections'] if d.get('severity') == 'ERROR']
        warnings = [d for d in data['detections'] if d.get('severity') == 'WARNING']
        print(f'  - ERROR: {len(errors)}')
        print(f'  - WARNING: {len(warnings)}')
" 2>/dev/null || echo "Could not parse JSON"
else
  echo "✗ scan.json not found"
fi

echo ""
echo "=== Step 6: Workflow Decision Logic ==="
echo ""
echo "In GitHub Actions, you would use:"
echo ""
echo "  - name: Fail if secrets found"
echo "    run: |"
echo "      python3 code/yologuard/src/IF.yologuard_v3.py --scan . --profile ci --sarif scan.sarif"
echo "      if [ \$? -ne 0 ]; then"
echo "        echo '::error::ERROR-level secrets detected'"
echo "        exit 1"
echo "      fi"
echo ""
echo "Or with JSON filtering:"
echo ""
echo "  - name: Check for critical secrets"
echo "    run: |"
echo "      ERRORS=\$(jq '[.detections[] | select(.severity == \"ERROR\")] | length' scan.json)"
echo "      if [ \$ERRORS -gt 0 ]; then"
echo "        echo \"Found \$ERRORS ERROR-level detections\""
echo "        exit 1"
echo "      fi"
echo ""

echo "=== Scan Result Summary ==="
echo "Status: $SCAN_RESULT"
echo "Exit Code: $EXIT_CODE"
echo "Outputs: scan.sarif, scan.json"
echo ""
echo "To upload to GitHub, use:"
echo "  gh code scanning upload scan.sarif --repository <owner>/<repo>"

echo ""
echo "=== Expected Output ==="
echo ""
echo "With the test secrets created above, you should see:"
echo ""
echo "1. Exit Code:"
echo "   - 0 = No errors (scan passed cleanly)"
echo "   - 1 = ERROR-level secrets found (workflow fails)"
echo "   - 2 = WARNING-level secrets found (check thresholds)"
echo ""
echo "2. JSON Output (scan.json structure):"
echo "   {"
echo "     \"scan_metadata\": {"
echo "       \"profile\": \"ci\","
echo "       \"error_threshold\": 0.75,"
echo "       \"total_files_scanned\": 4,"
echo "       \"scan_duration_ms\": 1234"
echo "     },"
echo "     \"detections\": ["
echo "       {"
echo "         \"file_path\": \"src/main.py\","
echo "         \"line_number\": 2,"
echo "         \"category\": \"AWS Access Key ID\","
echo "         \"severity\": \"ERROR\","
echo "         \"relationship_score\": 0.95,"
echo "         \"snippet\": \"AWS_ACCESS_KEY_ID = \\\"AKIA...\\\"\""
echo "       },"
echo "       {"
echo "         \"file_path\": \"config/database.yml\","
echo "         \"line_number\": 4,"
echo "         \"category\": \"Generic Password\","
echo "         \"severity\": \"WARNING\","
echo "         \"relationship_score\": 0.72"
echo "       }"
echo "     ]"
echo "   }"
echo ""
echo "3. SARIF Output Format:"
echo "   - Standard GitHub Code Scanning format"
echo "   - Can be uploaded to GitHub Security tab"
echo "   - Each detection becomes a SARIF 'result' object"
echo ""
echo "4. Sample stats output:"
echo "   Total detections: 2"
echo "   - ERROR: 1"
echo "   - WARNING: 1"
echo ""
echo ""
echo "=== What To Do If It Fails ==="
echo ""
echo "Issue: Exit code is not 0, 1, or 2"
echo "  → Check Python version: python3 --version (requires 3.8+)"
echo "  → Verify IF.yologuard installation: python3 -m pip show yologuard"
echo ""
echo "Issue: No detections found (empty JSON)"
echo "  → Verify test secrets were created: cat $TEST_REPO/src/main.py"
echo "  → Check file encoding: file $TEST_REPO/src/main.py"
echo "  → Try with --verbose flag to see scanning details"
echo ""
echo "Issue: SARIF file missing"
echo "  → Verify --sarif parameter in command"
echo "  → Check disk space: df -h"
echo "  → Check file permissions: ls -la $TEST_REPO/scan.sarif"
echo ""
echo "Issue: JSON is invalid or unparseable"
echo "  → Validate JSON: python3 -m json.tool < $TEST_REPO/scan.json"
echo "  → Check if scan.json contains errors: grep -i error $TEST_REPO/scan.json"
echo "  → Re-run with --format json-simple for cleaner output"
echo ""
echo "Issue: Scan exits with code 1 but no obvious secrets"
echo "  → Check threshold: error_threshold 0.75 is strict"
echo "  → Lower threshold for testing: --error-threshold 0.50"
echo "  → Review the 'relationship_score' field in JSON"
echo ""
echo "How to verify the example ran correctly:"
echo "  1. Check exit code: echo \$?"
echo "  2. Verify files exist: ls -lah scan.json scan.sarif"
echo "  3. Parse JSON: python3 -c \"import json; json.load(open('scan.json'))\" && echo 'Valid JSON'"
echo "  4. Count detections: jq '.detections | length' scan.json 2>/dev/null || echo 'jq not installed'"
echo ""
