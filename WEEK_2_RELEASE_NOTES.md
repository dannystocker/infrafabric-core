# Week 2 Release Notes (Draft)

Date: 2025-11-08
Status: Draft by A10 (Coordinator)

## Highlights
- Beginner docs aligned; time-to-first-scan <5 minutes confirmed
- Reproducibility bundle finalized (commit hash + hyperparams + FP precision)
- IFMessage v1.0 schema validated in CI (pending workflow merge, see A6 PR)
- Governance dissent runbook and example shipped
- Visuals verified (Mermaid) in GitHub UI

## Changes
- docs: Quick Start, Glossary, FAQ updated
- examples: 5 runnable scripts (single file, directory, CI, profiles, governance)
- schemas: IFMessage and Decision v1.0 + validator
- governance: dissent runbook + example JSON
- rfcs: Honeypot Falsification Protocol (v0.1)

## Benchmarks
- Leaky Repo fast benchmark: 107/96, coverage 42/42, ~0.1s

## CI Enforcement
- PR: (A6) enable `.github/workflows/review.yml` (IFMessage + Decision JSON validation)
- Status: pending merge; staging copy in `docs/ci/review.yml`

## Next
- Collect beginner feedback
- Prepare Week 3: minimal perf job demonstration; async fallback prototype docs

