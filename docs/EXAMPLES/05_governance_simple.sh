#!/bin/bash
# Example 05: Simple Decision Governance Example
#
# This example demonstrates:
# - Creating a basic decision record following IF.guard governance
# - Relating decisions to detection results
# - JSON schema validation for decisions
# - Simple audit trail for secret handling decisions
#
# The decision schema is located in: schemas/decision/v1.0.schema.json
# Available decision types: APPROVE, REJECT, CONDITIONAL
#
# GOVERNANCE REFERENCES:
# - Full dissent handling process: governance/DECISION_DISSENT_RUNBOOK.md
# - Dissent escalation outcomes: governance/DECISION_DISSENT_RUNBOOK.md#dissent-escalation-outcomes
# - Example decision artifact: governance/examples/decision_example.json

set -euo pipefail

PROJECT_ROOT=$(git rev-parse --show-toplevel)
YOLOGUARD="${PROJECT_ROOT}/code/yologuard/src/IF.yologuard_v3.py"
DECISION_SCHEMA="${PROJECT_ROOT}/schemas/decision/v1.0.schema.json"

echo "=== IF.guard Simple Governance Example ==="
echo ""
echo "This example shows how to:"
echo "1. Run a secret scan"
echo "2. Create a decision record"
echo "3. Document your governance choices"
echo ""

# Create test directory
TEST_DIR=$(mktemp -d)
trap "rm -rf $TEST_DIR" EXIT

# Create a test file with a secret
cat > "$TEST_DIR/config.py" << 'EOF'
# Application configuration
DATABASE_URL = "postgresql://admin:SuperSecret123@localhost:5432/app"
API_KEY = "sk-proj-1234567890abcdefghijklmnop"
EOF

echo "=== Step 1: Run Secret Scan ==="
echo ""
python3 "$YOLOGUARD" \
  --scan "$TEST_DIR" \
  --profile ci \
  --json "${TEST_DIR}/scan_results.json" \
  --stats

echo ""
echo "=== Step 2: Review Scan Results ==="
python3 << 'PYEOF'
import json
import os

scan_file = os.environ.get('TEST_DIR', '/tmp') + '/scan_results.json'
try:
    with open(scan_file, 'r') as f:
        data = json.load(f)
        detections = data.get('detections', [])
        print(f"Found {len(detections)} detections:")
        for i, det in enumerate(detections[:3], 1):
            print(f"  {i}. {det.get('category')} - Severity: {det.get('severity')}")
            print(f"     Location: {det.get('file_path')}:{det.get('line_number', '?')}")
            print(f"     Confidence: {det.get('relationship_score', '?')}")
except Exception as e:
    print(f"Error reading scan: {e}")
PYEOF

echo ""
echo "=== Step 3: Create Decision Record ==="
echo ""

# Generate a decision ID
DECISION_ID="decision-$(date +%s)"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SUBMITTER="${USER:-automated-scan}"

echo "Creating decision: $DECISION_ID"
echo "Timestamp: $TIMESTAMP"
echo "Submitter: $SUBMITTER"
echo ""

# Create a decision record (this represents a governance choice)
DECISION_FILE="${TEST_DIR}/decision_${DECISION_ID}.json"

cat > "$DECISION_FILE" << EOF
{
  "id": "$DECISION_ID",
  "timestamp": "$TIMESTAMP",
  "submitter": "$SUBMITTER",
  "decision": "CONDITIONAL",
  "dissent": [],
  "notes": "Approved deployment after secrets rotation. Database password and API key have been invalidated and rotated. Both credentials are now obsolete and pose no risk."
}
EOF

echo "Decision record created: $DECISION_FILE"
echo ""
echo "=== Decision Content ==="
cat "$DECISION_FILE" | python3 -m json.tool

echo ""
echo "=== Step 4: Link Decision to Detection ==="
echo ""

# Show how decisions relate to detections
cat > "${TEST_DIR}/decision_mapping.json" << 'EOF'
{
  "governance_record": {
    "decision_id": "decision-timestamp",
    "applies_to_scan_id": "scan-results",
    "affected_detections": [
      {
        "detection_id": 1,
        "category": "PostgreSQL Credentials",
        "action_taken": "secret_rotated",
        "mitigation": "Credentials changed in database, old credentials invalidated"
      },
      {
        "detection_id": 2,
        "category": "API Key",
        "action_taken": "secret_rotated",
        "mitigation": "API key revoked and reissued"
      }
    ],
    "overall_decision": "CONDITIONAL",
    "conditions_met": [
      "All detected secrets have been rotated",
      "Old credentials are invalidated",
      "No exposure risk identified in logs",
      "Deployment can proceed"
    ],
    "review_date": "2025-11-08",
    "next_review": "2025-12-08"
  }
}
EOF

echo "Decision mapping created (governance_mapping.json)"
echo ""
cat "${TEST_DIR}/decision_mapping.json" | python3 -m json.tool | head -40
echo ""

echo "=== Step 5: Schema Validation ==="
echo ""

if [ -f "$DECISION_SCHEMA" ]; then
  echo "✓ Decision schema found: $DECISION_SCHEMA"
  echo ""
  echo "Schema requirements:"
  python3 << PYEOF
import json
with open("$DECISION_SCHEMA", 'r') as f:
    schema = json.load(f)
    print(f"  Title: {schema.get('title')}")
    print(f"  Required fields: {schema.get('required', [])}")
    props = schema.get('properties', {})
    print(f"  Valid decision values: {props.get('decision', {}).get('enum', [])}")
PYEOF

  echo ""
  echo "Validating decision against schema:"
  python3 << PYEOF
import json
import sys

try:
    from jsonschema import validate, ValidationError
    has_jsonschema = True
except ImportError:
    has_jsonschema = False

# Load schema and decision
with open("$DECISION_SCHEMA", 'r') as f:
    schema = json.load(f)

with open("$DECISION_FILE", 'r') as f:
    decision = json.load(f)

if has_jsonschema:
    try:
        validate(instance=decision, schema=schema)
        print("  ✓ Decision validates against schema")
        print(f"    - ID: {decision['id']}")
        print(f"    - Decision: {decision['decision']}")
        print(f"    - Dissent count: {len(decision.get('dissent', []))}")
        if decision.get('dissent'):
            print(f"    - Dissenters: {', '.join(decision['dissent'])}")
            print("    → See escalation outcomes: governance/DECISION_DISSENT_RUNBOOK.md#dissent-escalation-outcomes")
    except ValidationError as e:
        print(f"  ✗ Validation failed: {e.message}")
        sys.exit(1)
else:
    # Manual validation
    print("  ✓ Decision file exists and is valid JSON")
    print(f"    - ID: {decision['id']}")
    print(f"    - Decision: {decision['decision']}")
    print(f"    - Dissent count: {len(decision.get('dissent', []))}")
    print("    (Install jsonschema for full validation: pip install jsonschema)")

PYEOF
else
  echo "✗ Schema not found at $DECISION_SCHEMA"
fi

echo ""
echo "=== Step 6: Audit Trail ==="
echo ""

# Simulated audit trail
cat > "${TEST_DIR}/audit_log.json" << 'EOF'
{
  "audit_events": [
    {
      "timestamp": "2025-11-08T10:00:00Z",
      "event_type": "scan_completed",
      "scanner": "IF.yologuard v3",
      "detections_found": 2,
      "profile_used": "ci"
    },
    {
      "timestamp": "2025-11-08T10:05:00Z",
      "event_type": "review_started",
      "reviewer": "security-team",
      "action": "Reviewing detected secrets"
    },
    {
      "timestamp": "2025-11-08T10:30:00Z",
      "event_type": "remediation_completed",
      "action": "All secrets rotated and invalidated",
      "affected_systems": ["database", "api"]
    },
    {
      "timestamp": "2025-11-08T10:35:00Z",
      "event_type": "decision_recorded",
      "decision": "CONDITIONAL",
      "decision_id": "decision-1731059700",
      "allowed_next_action": "deploy"
    }
  ]
}
EOF

echo "Audit trail:"
python3 << PYEOF
import json
with open("${TEST_DIR}/audit_log.json", 'r') as f:
    audit = json.load(f)
    for event in audit['audit_events']:
        print(f"  [{event['timestamp']}] {event['event_type']}")
        if 'action' in event:
            print(f"    → {event['action']}")
PYEOF

echo ""
echo "=== Summary: Governance Workflow ==="
echo ""
echo "1. SCAN      - Run IF.yologuard to find secrets"
echo "2. REVIEW    - Security team evaluates findings"
echo "3. REMEDIATE - Secrets are rotated/invalidated"
echo "4. DECIDE    - Create formal decision record"
echo "5. DOCUMENT  - Link decision to detections"
echo "6. AUDIT     - Maintain trail for compliance"
echo ""
echo "Files created:"
echo "  - decision_*.json          : Governance decision record"
echo "  - decision_mapping.json    : Maps decisions to detections"
echo "  - audit_log.json          : Audit trail for compliance"
echo ""
echo "Decision types:"
echo "  - APPROVE     : Accept risk after remediation"
echo "  - REJECT      : Cannot deploy, more work needed"
echo "  - CONDITIONAL : Can deploy IF conditions met"
echo ""
echo "Submitter: Record who made the decision (user, automation, bot)"
echo "Dissent:   Array of dissenting votes (if any)"
echo "Notes:     Explain your reasoning and conditions"
