# Quick Start (5 Minutes)

## 1) Install
```
git clone https://github.com/dannystocker/infrafabric.git
cd infrafabric/code/yologuard
```

## 2) Run your first scan
```
# Create a tiny test file
printf "api_key=ghp_exampletoken1234567890\n" > /tmp/example.txt

# Beginner mode: simple output + simple JSON + CI profile
python3 src/IF.yologuard_v3.py \
  --scan /tmp/example.txt \
  --beginner-mode \
  --json /tmp/results.json \
  --stats

# Or explicitly (simple output + simple JSON)
python3 src/IF.yologuard_v3.py \
  --scan /tmp/example.txt \
  --simple-output \
  --json /tmp/results.json \
  --format json-simple \
  --stats
```

## 3) View results
```
cat /tmp/results.json
```

## Visual Guides

Want to understand how IF.yologuard works? Check out our visual documentation:

### Architecture & Concepts
- **[Architecture Overview](VISUALS/architecture_simple.md)** - System design with Mermaid diagrams
  - Three-pillar architecture (detection → deception → learning)
  - Complete data flow from code to security action
  - Key design principles explained visually

### How It Works
- **[Detection Pipeline](VISUALS/how_detection_works.md)** - Step-by-step detection process
  - Stage-by-stage explanation (file read → pattern match → entropy → relationships → validation)
  - Detailed examples at each stage
  - Decision points and severity determination

### Choosing the Right Settings
- **[Profiles Explained](VISUALS/profiles_explained.md)** - Profile comparison and selection
  - CI, OPS, AUDIT, and RESEARCH profiles compared
  - Decision tree for choosing the right profile
  - Performance characteristics and use cases

## Next Steps
- See docs/EXAMPLES for more scripts
- Use `--profile ci` for PR gating
- For deeper context, try `--profile forensics` to include graph/manifests

---

## Message Contract (IFMessage v1.0)

IFMessage is the universal detection format used throughout the InfraFabric ecosystem. It provides a standardized way for detection agents (like IF.yologuard) to communicate security findings to processing agents (like IF.guard) and other downstream systems.

### Purpose

The IFMessage contract ensures:
- **Consistency**: All detections use the same structure regardless of source
- **Interoperability**: Different detection tools can be swapped without changing the processing pipeline
- **Traceability**: Each message carries metadata for debugging and audit trails
- **Extensibility**: Optional fields allow rich context without breaking compatibility

### Simple Example

Here's a minimal IFMessage showing a detected AWS credential in source code:

```json
{
  "id": "msg-001",
  "timestamp": "2025-11-08T12:00:00Z",
  "level": 1,
  "source": "IF.yologuard",
  "destination": "IF.guard",
  "version": "1.0",
  "traceId": "trace-abc",
  "payload": {
    "file": "benchmarks/leaky-repo/.netrc",
    "pattern": "AWS_SECRET_REDACTED",
    "line": 12,
    "severity": "ERROR"
  }
}
```

### Key Fields

- **id**: Unique identifier for this message (format: `msg-NNN`)
- **timestamp**: RFC 3339 datetime of detection
- **level**: Connectivity level (1 = function-to-function, 2 = module-to-module)
- **source/destination**: Agent names (e.g., `IF.yologuard`, `IF.guard`)
- **version**: Contract version (currently `1.0`)
- **traceId**: Optional correlation ID for distributed tracing
- **payload**: Detection data (file, pattern, line number, severity, and optional enrichment fields)

### Learn More

- **Schema Definition**: See `schemas/ifmessage/v1.0.schema.json` for the complete specification
- **Example Messages**: Check `messages/examples/` for ERROR, WARN, and forensics examples
- **Validation**: Use `scripts/validate_message.py <schema> <message.json>` to validate new messages
