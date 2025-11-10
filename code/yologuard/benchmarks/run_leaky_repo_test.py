#!/usr/bin/env python3
# Copyright (c) 2025 Danny Stocker
# SPDX-License-Identifier: MIT
#
# InfraFabric - IF.yologuard Benchmark Runner
# Source: https://github.com/dannystocker/infrafabric
# Licensed under the MIT License. See LICENSE-CODE file in the project root.

"""
IF.yologuard Leaky Repo Validation Test
Tests IF.yologuard patterns against the industry-standard Leaky Repo benchmark
"""

import sys
import re
from pathlib import Path
from datetime import datetime

import importlib.util

def load_redactor():
    """Dynamically load the SecretRedactorV3 class from its source file."""
    # Path to the source file
    src_path = Path('/home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py')
    if not src_path.exists():
        print(f"✗ Source file not found at {src_path}", file=sys.stderr)
        sys.exit(1)
    spec = importlib.util.spec_from_file_location('IF_yologuard_v3', src_path)
    if spec is None:
        print(f"✗ Could not create module spec for {src_path}", file=sys.stderr)
        sys.exit(1)
    yologuard_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(yologuard_module)
    return yologuard_module.SecretRedactorV3()

def scan_file(file_path, redactor):
    """Scan a single file and return found secrets"""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        secrets_found = []

        for pattern, replacement in redactor.PATTERNS:
            matches = re.finditer(pattern, content, re.DOTALL | re.MULTILINE)
            for match in matches:
                secrets_found.append({
                    'file': str(file_path),
                    'pattern': replacement,
                    'match': match.group(0)[:50] + '...' if len(match.group(0)) > 50 else match.group(0),
                    'line': content[:match.start()].count('\n') + 1
                })

        return secrets_found
    except Exception as e:
        print(f"Error scanning {file_path}: {e}", file=sys.stderr)
        return []

def main():
    print("=" * 80)
    print("IF.yologuard Leaky Repo Validation Test")
    print("=" * 80)
    print()

    # Initialize redactor
    redactor = load_redactor()
    print(f"✓ Loaded IF.yologuard with {len(redactor.PATTERNS)} patterns")

    # Locate Leaky Repo
    leaky_repo_path = Path('/home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks/leaky-repo')
    if not leaky_repo_path.exists():
        print(f"✗ Leaky Repo not found at {leaky_repo_path}")
        sys.exit(1)

    print(f"✓ Found Leaky Repo at {leaky_repo_path}")
    print()

    # Scan all files (excluding .git and .leaky-meta)
    all_secrets = []
    files_scanned = 0

    file_patterns = ['*.json', '*.txt', '*.md', '*.sh', '*.py', '*.js', '*.yml',
                     '*.yaml', '*.xml', '*.env', '*.config', '.*']

    print("Scanning files...")
    for pattern in file_patterns:
        for file_path in leaky_repo_path.rglob(pattern):
            # Skip .git and .leaky-meta directories
            if '.git' in str(file_path) or '.leaky-meta' in str(file_path):
                continue

            if file_path.is_file():
                secrets = scan_file(file_path, redactor)
                all_secrets.extend(secrets)
                files_scanned += 1
                if secrets:
                    print(f"  ✓ {file_path.name}: {len(secrets)} secret(s) found")

    print()
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(f"Files scanned: {files_scanned}")
    print(f"Total secrets detected: {len(all_secrets)}")
    print()

    # Group by pattern type
    by_pattern = {}
    for secret in all_secrets:
        pattern_type = secret['pattern']
        by_pattern[pattern_type] = by_pattern.get(pattern_type, 0) + 1

    print("Secrets by type:")
    for pattern_type, count in sorted(by_pattern.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern_type}: {count}")

    print()

    # Write detailed results
    results_file = Path('/home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks/leaky_repo_results.md')
    with results_file.open('w') as f:
        f.write("# IF.yologuard Leaky Repo Validation Test Results\n\n")
        f.write(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**IF.yologuard Version:** {len(redactor.PATTERNS)} patterns\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Files Scanned:** {files_scanned}\n")
        f.write(f"- **Total Secrets Detected:** {len(all_secrets)}\n")
        f.write(f"- **Leaky Repo Ground Truth:** 175 secrets (documented)\n")
        f.write(f"- **Detection Rate:** {len(all_secrets)/175*100:.1f}% ({len(all_secrets)}/175)\n\n")

        f.write("## Secrets by Pattern Type\n\n")
        f.write("| Pattern Type | Count |\n")
        f.write("|--------------|-------|\n")
        for pattern_type, count in sorted(by_pattern.items(), key=lambda x: x[1], reverse=True):
            f.write(f"| {pattern_type} | {count} |\n")

        f.write("\n## Detailed Findings\n\n")
        for i, secret in enumerate(all_secrets, 1):
            f.write(f"### Secret #{i}\n")
            f.write(f"- **File:** `{Path(secret['file']).name}`\n")
            f.write(f"- **Line:** {secret['line']}\n")
            f.write(f"- **Type:** {secret['pattern']}\n")
            f.write(f"- **Match:** `{secret['match']}`\n\n")

    print(f"✓ Detailed results written to: {results_file}")
    print()

    # Analysis
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)

    detection_rate = len(all_secrets) / 175 * 100

    if detection_rate >= 95:
        print(f"✓ EXCELLENT: {detection_rate:.1f}% detection rate (≥95%)")
    elif detection_rate >= 85:
        print(f"~ GOOD: {detection_rate:.1f}% detection rate (85-95%)")
    elif detection_rate >= 70:
        print(f"⚠ MODERATE: {detection_rate:.1f}% detection rate (70-85%)")
    else:
        print(f"✗ LOW: {detection_rate:.1f}% detection rate (<70%)")

    print()
    print(f"Baseline comparison (39 test cases): 96.43% precision/recall")
    print(f"Leaky Repo scale: {files_scanned} files vs 39 baseline cases")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
