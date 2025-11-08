#!/bin/bash
# Example 02: Scan entire directory recursively with JSON and SARIF output
#
# This example demonstrates how to:
# - Scan an entire directory tree recursively
# - Use the --profile ci for fast, CI-friendly scanning
# - Output to both JSON and SARIF formats
# - Filter detections by severity level
#
# Prerequisites: python3, IF.yologuard_v3.py in code/yologuard/src/

set -euo pipefail

# Get the project root
PROJECT_ROOT=$(git rev-parse --show-toplevel)
YOLOGUARD="${PROJECT_ROOT}/code/yologuard/src/IF.yologuard_v3.py"

# Create a temporary test directory with sample files
TEST_DIR=$(mktemp -d)
trap "rm -rf $TEST_DIR" EXIT

echo "Creating test directory: $TEST_DIR"

# Create test files with various secret patterns
mkdir -p "$TEST_DIR/src" "$TEST_DIR/config" "$TEST_DIR/.env"

# File 1: Source file with embedded API key
cat > "$TEST_DIR/src/api.py" << 'EOF'
# API Client
api_key = "sk-abc123def456ghi789jkl"  # OpenAI API key
database_url = "postgresql://user:SuperSecret123!@localhost:5432/mydb"
EOF

# File 2: Configuration with credentials
cat > "$TEST_DIR/config/settings.json" << 'EOF'
{
  "database": {
    "user": "admin",
    "password": "MyP@ssw0rd!2025"
  },
  "api": {
    "key": "ghp_abcdefghijklmnopqrstuvwxyz1234567890"
  }
}
EOF

# File 3: Environment-like file
cat > "$TEST_DIR/.env.example" << 'EOF'
# Database credentials
DB_USER=postgres
DB_PASSWORD=CorrectHorseBatteryStaple123
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
EOF

# File 4: Clean file (no secrets)
cat > "$TEST_DIR/src/README.md" << 'EOF'
# My Application

This is a simple application that does nothing malicious.
See the documentation for details.
EOF

echo ""
echo "=== Test Files Created ==="
find "$TEST_DIR" -type f -exec echo "  {}" \;

echo ""
echo "=== Running Scan with --profile ci (fast, CI-friendly) ==="
echo "Command: python3 $YOLOGUARD --scan $TEST_DIR --profile ci --json scan.json --sarif scan.sarif --stats"
echo ""

# Run the scan with ci profile (optimized for CI/CD pipelines)
python3 "$YOLOGUARD" \
  --scan "$TEST_DIR" \
  --profile ci \
  --json "${TEST_DIR}/scan.json" \
  --sarif "${TEST_DIR}/scan.sarif" \
  --stats

echo ""
echo "=== JSON Output (scan.json) ==="
if [ -f "${TEST_DIR}/scan.json" ]; then
  cat "${TEST_DIR}/scan.json" | python3 -m json.tool | head -50
  echo "... (truncated)"
else
  echo "No detections found (scan.json not created)"
fi

echo ""
echo "=== SARIF Output (scan.sarif) - First 50 lines ==="
if [ -f "${TEST_DIR}/scan.sarif" ]; then
  head -50 "${TEST_DIR}/scan.sarif"
  echo "... (truncated)"
else
  echo "No SARIF output generated"
fi

echo ""
echo "=== Filter by Severity Level ==="
echo ""
echo "To filter JSON output by severity in your own scripts, you can use jq:"
echo "  jq '.detections[] | select(.severity == \"ERROR\")' scan.json"
echo "  jq '.detections[] | select(.severity == \"WARNING\")' scan.json"
echo ""
echo "Example filtering out low-severity warnings:"
echo "  jq '.detections[] | select(.severity != \"INFO\")' scan.json"
echo ""

# Show example of what filtered output looks like (if we have a scan.json)
if [ -f "${TEST_DIR}/scan.json" ]; then
  echo "=== Actual Filtered Results (ERROR only) ==="
  python3 << PYEOF
import json
try:
    with open('${TEST_DIR}/scan.json', 'r') as f:
        data = json.load(f)
        if 'detections' in data:
            errors = [d for d in data['detections'] if d.get('severity') == 'ERROR']
            if errors:
                print(f'Found {len(errors)} ERROR detections:')
                for det in errors[:3]:
                    print(f'  - {det.get("category", "unknown")}: {det.get("message", "no message")[:60]}...')
            else:
                print('No ERROR detections found')
except Exception as e:
    print(f'Could not parse: {e}')
PYEOF
fi

echo ""
echo "=== Summary ==="
echo "The --profile ci preset uses:"
echo "  - error_threshold: 0.75 (strict)"
echo "  - warn_threshold: 0.50"
echo "  - mode: both (usable + components)"
echo "  - Output: fast, minimal context"
echo ""
echo "This is ideal for GitHub Actions, GitLab CI, Jenkins, etc."
echo "Example GitHub Actions usage:"
echo "  python3 code/yologuard/src/IF.yologuard_v3.py --scan . --profile ci --sarif scan.sarif"
echo "  gh code scanning upload scan.sarif --repository \${{ github.repository }}"
