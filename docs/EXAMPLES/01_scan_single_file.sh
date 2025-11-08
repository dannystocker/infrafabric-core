#!/usr/bin/env bash
# ==============================================================================
# Example 1: Scan a Single File for Secrets
# ==============================================================================
# This script demonstrates the basic IF.yologuard workflow:
#   1. Create a test file with a fake secret (AWS key format)
#   2. Run IF.yologuard scanner
#   3. Display results in JSON format
#   4. Clean up
#
# Expected output: Detects 1 high-confidence secret (AWS key format)
# ==============================================================================

set -euo pipefail

# Configuration
FILE="${1:-/tmp/example.txt}"
JSON_OUT="/tmp/scan.json"
REPO_ROOT=$(git rev-parse --show-toplevel)

echo "=============================================================================="
echo "IF.yologuard Single-File Scan Example"
echo "=============================================================================="
echo ""

# Step 1: Create test file with fake AWS secret
echo "Step 1: Creating test file with fake AWS key..."
echo "  File: $FILE"
printf "# AWS Configuration
aws_access_key = AKIAIOSFODNN7EXAMPLE
aws_secret = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region = us-east-1
" > "$FILE"
echo "  Status: Created"
echo ""

# Step 2: Run IF.yologuard scan
echo "Step 2: Running IF.yologuard scan..."
echo "  Command: python3 src/IF.yologuard_v3.py --scan '$FILE' --json '$JSON_OUT' --simple-output --stats"
echo ""

python3 "$REPO_ROOT/code/yologuard/src/IF.yologuard_v3.py" \
  --scan "$FILE" \
  --json "$JSON_OUT" \
  --format json-simple \
  --simple-output \
  --stats

echo ""
echo "Step 3: Displaying scan results..."
echo "  File: $JSON_OUT"
echo ""
echo "--- JSON Output ---"
cat "$JSON_OUT" | python3 -m json.tool 2>/dev/null || cat "$JSON_OUT"
echo ""

# Step 4: Clean up
echo "Step 4: Cleaning up test file..."
rm -f "$FILE"
echo "  Removed: $FILE"
echo ""

echo "=============================================================================="
echo "Example Complete"
echo "=============================================================================="
echo ""
echo "What happened:"
echo "  • IF.yologuard detected 1 AWS key format (AKIA* prefix)"
echo "  • Relationship score high: AWS_access_key + AWS_secret in same file"
echo "  • Classification: 'usable' (can be used immediately)"
echo "  • Severity: ERROR (requires action)"
echo ""
echo "For more details, see: docs/HELLO_W0RLD.md"
