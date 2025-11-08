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

## Next Steps
- See docs/EXAMPLES for more scripts
- Use `--profile ci` for PR gating
- For deeper context, try `--profile forensics` to include graph/manifests
