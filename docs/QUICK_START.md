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

## Beginner Cheatsheet

**Essential Flags:**
- `--scan <path>` - What to scan
- `--json <file>` - Save results as JSON
- `--simple-output` - Human-friendly one-line output
- `--format json-simple` - Minimal JSON (file, line, severity, pattern)
- `--profile ci` - Fast, conservative (PR checks)

**Severity Levels:**
- **ERROR** - Fix immediately (high-confidence secret)
- **WARN** - Review manually (may be false positive)
- **INFO** - Investigate (low confidence)

**Common Patterns Detected:**
- AWS keys (AKIA...), GitHub tokens, passwords, private keys, API credentials

**Quick Decision Tree:**
```
Found a secret?
  ├─ ERROR severity → Rotate credentials immediately
  ├─ WARN severity → Manual review required
  └─ INFO severity → Investigate context
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

## Troubleshooting Common Issues

1. **"python3: command not found"**
   - Install Python 3.8+: https://python.org/downloads
   - Verify: `python3 --version`

2. **"No such file or directory"**
   - Use absolute paths: `/home/user/project/file.txt`
   - Check file exists: `ls -la <path>`

3. **"Permission denied"**
   - Make file readable: `chmod +r file.txt`
   - Check directory permissions

4. **"No detections found" (but secrets exist)**
   - Try: `--profile forensics` (more sensitive)
   - Check file isn't binary (automatically skipped)
   - Verify secret format matches patterns

5. **"Too many false positives"**
   - Use: `--profile ci` (conservative)
   - Filter by severity: focus on ERROR only
   - Check context of WARN detections

6. **"JSON parsing error"**
   - Validate JSON: `python3 -m json.tool results.json`
   - Check for trailing commas

7. **"Binary file skipped"**
   - Expected for .db, .png, .pdf files
   - Use text-based config files instead

8. **"Scan too slow"**
   - Use: `--profile ci` (faster)
   - Reduce: `--max-file-bytes 5000000`
   - Scan smaller directories first

9. **"Import error / Module not found"**
   - No dependencies needed (stdlib only)
   - Check Python version >= 3.8

10. **"Unexpected output format"**
    - Use: `--json results.json` for structured output
    - Or: `--sarif results.sarif` for GitHub Security
    - Or: `--simple-output` for human-friendly lines

## Next Steps
- See docs/EXAMPLES for more scripts
- Use `--profile ci` for PR gating
- For deeper context, try `--profile forensics` to include graph/manifests
