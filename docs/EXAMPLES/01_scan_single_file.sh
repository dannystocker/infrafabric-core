#!/usr/bin/env bash
set -euo pipefail
FILE=${1:-/tmp/example.txt}
printf "password=example123
" > "$FILE"
python3 $(git rev-parse --show-toplevel)/code/yologuard/src/IF.yologuard_v3.py \n  --scan "$FILE" --simple-output --json /tmp/scan.json --format json-simple --stats
cat /tmp/scan.json
