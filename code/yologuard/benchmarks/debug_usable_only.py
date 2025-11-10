#!/usr/bin/env python3
"""
Forensic debug: Count usable vs component detections
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "yologuard_v3",
    str(Path(__file__).resolve().parents[1] / 'src' / 'IF.yologuard_v3.py')
)
yologuard_v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yologuard_v3)
SecretRedactorV3 = yologuard_v3.SecretRedactorV3

LEAKY_REPO_PATH = Path(__file__).resolve().parent / 'leaky-repo'
EXCLUDE_DIRS = {'.git', '.leaky-meta'}

redactor = SecretRedactorV3()

total_detections = 0
usable_count = 0
component_count = 0
component_details = []

all_files = [
    f for f in LEAKY_REPO_PATH.rglob('*')
    if f.is_file() and not any(exc in f.parts for exc in EXCLUDE_DIRS)
]

for file_path in sorted(all_files):
    secrets = redactor.scan_file(file_path)

    for secret in secrets:
        total_detections += 1
        classification = secret.get('classification', 'usable')

        if classification == 'component':
            component_count += 1
            rel_path = str(file_path.relative_to(LEAKY_REPO_PATH))
            component_details.append(f"{rel_path}:{secret['line']} - {secret['pattern']}")
        else:
            usable_count += 1

print("=" * 80)
print("USABLE vs COMPONENT CLASSIFICATION")
print("=" * 80)
print()
print(f"Total detections (deduplicated): {total_detections}")
print(f"Usable secrets:                  {usable_count}")
print(f"Component patterns:              {component_count}")
print()
print(f"Usable recall:     {usable_count}/96 = {usable_count/96*100:.2f}%")
print(f"Component recall:  {total_detections}/96 = {total_detections/96*100:.2f}%")
print()
print("=" * 80)
print("COMPONENT PATTERNS DETECTED:")
print("=" * 80)
for detail in component_details:
    print(f"  {detail}")
print()
print(f"Total components: {len(component_details)}")
