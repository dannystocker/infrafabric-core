# Glossary (Beginner-Friendly)

Welcome to the IF.yologuard glossary! This guide explains technical terms in plain language.

---

## Core Concepts

**Secret**
A sensitive piece of information that should be kept private (like a password, API key, or access token). If leaked, attackers can misuse them.

**Detection**
When IF.yologuard finds something that looks like a secret in your code.

**Pattern**
A rule that describes what a specific type of secret looks like. For example, AWS keys always start with "AKIA" followed by 16 characters.

**Severity**
How serious a detection is:
- **ERROR**: High-confidence secret that should be fixed immediately
- **WARN**: Possible secret or component that needs review
- **INFO**: Low-confidence finding for investigation

---

## Simple Terms → Technical Terms

**Relationship Score**
When secrets appear together in the same file, they're more likely to be real. IF.yologuard calculates a "relationship score" (0.0 to 1.0) to measure how connected the secrets are. Higher scores mean stronger evidence that the secrets are real and related.

Technical note: This uses the Wu Lun (五倫) framework from Confucian philosophy (朋友=friends, 夫婦=partners, etc.).

**Extra Checks** → IEF (Immuno-Epistemic Forensics)
Additional validation steps to verify a secret is real:
- Structure checks (is this JWT formatted correctly?)
- Entropy analysis (does this have enough randomness?)
- Context validation (does this make sense in this file?)

**Audit Trail** → TTT (Traceability•Trust•Transparency)
Tracking where each detection came from:
- Which commit introduced it?
- What's the file hash?
- When was it detected?

**Future-Proof Crypto** → PQ (Post-Quantum)
Experimental checks for cryptographic keys that might be vulnerable when quantum computers become practical.

---

## Detection Classification

**Usable Secret**
A complete, ready-to-use credential (e.g., `password=MySecret123`). These are the highest priority to fix.

**Component**
Part of a secret or a related string that might indicate a problem (e.g., just the field name `password=` without the value). Lower urgency but still worth reviewing.

---

## Output Formats

**JSON** (JavaScript Object Notation)
Machine-readable format with all detection details. Good for integrating with other tools.

**SARIF** (Static Analysis Results Interchange Format)
Industry-standard format for security findings. GitHub can display these in the Security tab.

**Simple Output** (`--simple-output`)
Human-friendly one-line-per-detection format:
```
simple: config.py:42 [ERROR] AWS_ACCESS_KEY
```

**JSON Simple** (`--format json-simple`)
Minimal JSON with only essential fields (file, line, pattern, severity).

---

## Scanning Profiles

**CI Profile** (`--profile ci`)
Fast, conservative scanning for pull request checks. Only reports high-confidence secrets.

**OPS Profile** (`--profile ops`)
Balanced scanning for security operations monitoring.

**AUDIT Profile** (`--profile audit`)
Thorough scanning for compliance audits. Includes more findings to review.

**RESEARCH Profile** (`--profile research`)
Maximum sensitivity for research and deep investigations.

**FORENSICS Profile** (`--profile forensics`)
Enables all validation layers and generates detailed forensic graphs.

---

## Command Line Flags (Beginner-Friendly)

`--scan <path>`
What to scan (file or directory).

`--json <file>`
Save results as JSON.

`--sarif <file>`
Save results in SARIF format (for GitHub integration).

`--simple-output`
Print friendly one-line summaries to terminal.

`--format json-simple`
Use simplified JSON (fewer fields, easier to read).

`--profile <name>`
Use a preset configuration (ci, ops, audit, research, forensics).

`--mode <type>`
Filter results:
- `usable`: Only complete secrets
- `component`: Only partial/components
- `both`: Everything (default)

`--stats`
Print a summary of what was scanned.

---

## Advanced Concepts (Optional Reading)

**Entropy**
A measure of randomness. Real secrets have high entropy (look random), while fake examples or placeholders have low entropy.

**Base64 Encoding**
A way to represent binary data as text. Secrets are often Base64-encoded, so IF.yologuard automatically decodes and scans inside.

**Regex (Regular Expression)**
A pattern-matching language used to describe what secrets look like. For example: `AKIA[A-Z0-9]{16}` matches AWS access keys.

**Wu Lun (五倫) - Five Relationships**
Confucian philosophy that measures connection strength:
- 朋友 (péng yǒu) = Friends (0.85) - credentials together
- 夫婦 (fū fù) = Partners (0.75) - key + value pairs
- 父子 (fù zǐ) = Parent-child (0.65) - config + secret
- 君臣 (jūn chén) = Ruler-subject (0.55) - service + credential
- 兄弟 (xiōng dì) = Siblings (0.45) - related secrets

**IEF (Immuno-Epistemic Forensics)**
Inspired by the immune system's pattern recognition. Three validation layers:
1. **Danger Signals**: High entropy, suspicious patterns
2. **Structure Checks**: Valid JWT, PEM, or other formats
3. **Indra Graph**: Relationship network between findings

**TTT (Traceability•Trust•Transparency)**
Provenance tracking for each detection:
- **Traceability**: Which commit, file, line?
- **Trust**: Verified file hashes, signed manifests
- **Transparency**: Full audit trail, reproducible results

---

## Need Help?

- **Quick Start**: [docs/QUICK_START.md](QUICK_START.md)
- **Examples**: [docs/EXAMPLES/](EXAMPLES/)
- **Full Documentation**: [code/yologuard/README.md](../code/yologuard/README.md)
- **Visual Guides**: [docs/VISUALS/](VISUALS/)

---

**Evidence Citations:**
- Patterns defined: [code/yologuard/src/IF.yologuard_v3.py:121-298](../code/yologuard/src/IF.yologuard_v3.py)
- CLI arguments: [code/yologuard/src/IF.yologuard_v3.py:763-784](../code/yologuard/src/IF.yologuard_v3.py)
- Wu Lun scoring: [code/yologuard/src/IF.yologuard_v3.py:391-450](../code/yologuard/src/IF.yologuard_v3.py)
- Profile presets: [code/yologuard/src/IF.yologuard_v3.py:794-836](../code/yologuard/src/IF.yologuard_v3.py)
