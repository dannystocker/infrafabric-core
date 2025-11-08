# Quick Start (5 Minutes)

## 1) Install
```
git clone https://github.com/dannystocker/infrafabric.git
cd infrafabric/code/yologuard
```

## 2) Run your first scan
```
# Create a tiny test file
printf "api_key=ghp_exampletoken1234567890
" > /tmp/example.txt

# Scan it (simple output + simple JSON)
python3 src/IF.yologuard_v3.py   --scan /tmp/example.txt   --simple-output   --json /tmp/results.json   --format json-simple   --stats
```

## 3) View results
```
cat /tmp/results.json
```

## Next Steps
- See docs/EXAMPLES for more scripts
- Use `--profile ci` for PR gating
- For deeper context, try `--profile forensics` to include graph/manifests
