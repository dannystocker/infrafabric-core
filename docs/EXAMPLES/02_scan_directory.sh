#!/usr/bin/env bash
set -euo pipefail
DIR=${1:-$(git rev-parse --show-toplevel)/code/yologuard/benchmarks/leaky-repo}
python3 $(git rev-parse --show-toplevel)/code/yologuard/src/IF.yologuard_v3.py \n  --scan "$DIR" --profile ci --stats
