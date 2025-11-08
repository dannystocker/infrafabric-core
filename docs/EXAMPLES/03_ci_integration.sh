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
