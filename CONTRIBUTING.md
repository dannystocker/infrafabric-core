# Contributing to InfraFabric

Welcome! This guide helps you get started quickly.

## Quick Setup
```
git clone https://github.com/dannystocker/infrafabric.git
cd infrafabric
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -V
```

## First Run (Yologuard demo)
```
cd code/yologuard
python3 src/IF.yologuard_v3.py --demo
```

## Easy Contributions
- docs: fix typos, add examples under docs/EXAMPLES/
- patterns: propose new safe patterns
- tests: add adversarial cases under code/yologuard/harness/adversarial

## Standards
- Evidence‑binding: cite `path:line` for all critical claims in docs
- Conventional commits; small, focused PRs
- No secrets or corpus duplication in commits

## CI
- PRs validate IFMessage samples and decision example JSONs

Thanks for contributing!
