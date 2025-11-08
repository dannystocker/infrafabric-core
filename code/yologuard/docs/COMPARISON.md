# IF.yologuard vs Existing Tools (High-Level)

This is a qualitative, transparent comparison. Measurements are pending a formal benchmark suite.

- Scope: static secret detection on code repos
- Modes: usable-only vs component-inclusive
- Output: CI-friendly formats (SARIF), severities, and classifications

| Capability | IF.yologuard | GitHub Advanced Security (secret scanning) | TruffleHog | GitGuardian |
|-----------|---------------|---------------------------------------------|------------|-------------|
| Pattern library | ~78 variants across core categories | Large vendor set | Strong regex + entropy | Strong vendor patterns |
| Entropy/decode | Yes (Shannon + Base64/hex + JSON/XML values) | N/A (internal) | Yes | Yes |
| Relationship scoring (Wu Lun) | Yes (user-pass, key-endpoint, token-session, cert-authority, metadata-sibling) | Partial (validation-dependent) | No | No |
| Component detection | Yes (mode selectable) | Yes (e.g., AWS key IDs) | Mixed | Yes |
| Usable-only mode | Yes (mode selectable) | Varies | Varies | Varies |
| SARIF output | Yes | Yes | Via wrappers | Yes (enterprise) |
| CLI flags (thresholds/modes) | Yes | Limited | Yes | Yes |
| Guardian governance | Yes (integration example) | No | No | No |
| CI workflow (example) | Yes (GitHub Actions included) | N/A | N/A | N/A |

### Our Measured Numbers (Initial)

- Standard dataset: 107/96 (component-inclusive), 95/96 usable-only; 42/42 coverage
- Performance (host repo snapshot): ~116 files/sec, ~3.55 MB/sec (includes benchmark data)
- Public corpus (requests, flask): scanned 349 files, 73 detections total (tests/examples may contribute); avg ~454 files/sec

Competitor numbers: pending shared testbed runs.

Notes:
- IF.yologuard emphasizes contextual relationships to reduce noise and explain severity.
- Component vs usable reporting is disambiguated by `--mode` and documented in summaries.
- Pending head-to-head recall/precision/perf numbers will be published once the FP corpus and perf harness are run on shared datasets.
