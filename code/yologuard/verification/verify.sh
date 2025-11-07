#!/bin/bash
# Copyright (c) 2025 Danny Stocker
# SPDX-License-Identifier: MIT
#
# InfraFabric - IF.yologuard Verification Script
# Source: https://github.com/dannystocker/infrafabric
# Licensed under the MIT License. See LICENSE-CODE file in the project root.
#
# Runs the test suite and compares against expected output

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_DIR/src"
BENCHMARK_DIR="$PROJECT_DIR/benchmarks"

echo "=== IF.yologuard v3 Verification ==="
echo "Running test suite..."

cd "$BENCHMARK_DIR"
python3 run_leaky_repo_v3_philosophical_fast_v2.py --output-json results.json

echo "Tests complete. Comparing results..."
echo "Expected to detect 95-96 secrets from Leaky Repo"

if [ -f results.json ]; then
    python3 << 'PYEOF'
import json
with open('results.json') as f:
    results = json.load(f)
    detected = len([r for r in results if r.get('severity') in ['HIGH', 'CRITICAL']])
    print(f"Detected: {detected} secrets")
    if detected >= 95:
        print("SUCCESS: Verification passed")
        exit(0)
    else:
        print("FAILED: Too few secrets detected")
        exit(1)
PYEOF
fi
