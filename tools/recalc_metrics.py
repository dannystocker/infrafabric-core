#!/usr/bin/env python3
import re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
violations = []
for path in ROOT.rglob("*.md"):
    if path.name.startswith(("README_FOR_CLAUDE", "BIBLIOGRAPHY")):
        continue
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"\b(\d{1,3}(?:\.\d+)?)%\b", text):
        idx = m.start()
        window = text[max(0, idx-30):idx+30]
        # require a footnote marker or method hint nearby
        if not re.search(r"(CAGR|Δ%|uplift|\[\^calc\])", window):
            violations.append(f"{path}:{m.group(0)} at {idx}")
if violations:
    print("Metric method missing near percentage values:")
    print("\n".join(violations))
    sys.exit(1)
print("OK: All percentage values have method context.")
