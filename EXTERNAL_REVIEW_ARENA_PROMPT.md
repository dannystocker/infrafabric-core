# InfraFabric — External Review Prompt (LLM Arena Paste)

Use this single prompt to run an independent, static-first review of InfraFabric. If your environment cannot run code, perform a documentation/code reading review; if it can, the Optional Runtime section provides reproducible commands.

—

## Repository
- GitHub (master): https://github.com/dannystocker/infrafabric

## Quick Access (GitHub-only links)
- Connectivity architecture: https://github.com/dannystocker/infrafabric/blob/master/IF_CONNECTIVITY_ARCHITECTURE.md
- Session handoff: https://github.com/dannystocker/infrafabric/blob/master/SESSION_HANDOFF_2025-11-08_IF-ARMOUR.md
- Yologuard README: https://github.com/dannystocker/infrafabric/blob/master/code/yologuard/README.md
- Yologuard CLI (detector): https://github.com/dannystocker/infrafabric/blob/master/code/yologuard/src/IF.yologuard_v3.py
- Guardian handoff: https://github.com/dannystocker/infrafabric/blob/master/code/yologuard/integration/GUARDIAN_HANDOFF_v3.1_IEF.md
- External review results: https://github.com/dannystocker/infrafabric/blob/master/code/yologuard/EXTERNAL_REVIEW_RESULTS.md
- External review update (delta): https://github.com/dannystocker/infrafabric/blob/master/code/yologuard/EXTERNAL_REVIEW_UPDATE.md
- Papers index: https://github.com/dannystocker/infrafabric/tree/master/papers
- Sticky metrics: https://github.com/dannystocker/infrafabric/blob/master/STICKY_METRICS.md
- Review schema (JSON): https://github.com/dannystocker/infrafabric/blob/master/REVIEW_SCHEMA.json

—

## Your Mission
Provide two outputs:
1) Plain-language review (concise, 200–500 words)
2) Structured JSON review (machine-readable, per schema below)

Static review is acceptable (no code execution). If you can run code, see Optional Runtime below.

—

## Evaluation Scope
- GitHub repository itself (layout, style, contribution readiness)
- Birds-eye (coherence, novelty, roadmap realism, plumbing correctness)
- Section-by-section components:
  - IF.yologuard (v3.1.1): detection engine, IEF, TTT, PQ (experimental)
  - IF.guard: governance artifacts and decision flow
  - IF.connect: 5-level connectivity (function→module→service→module→ecosystem)
  - IF.armour (suite): honeypot/learner roadmaps
  - IF.witness: meta-validation (MARL, epistemic swarms)
  - IF.foundations / IF.vision: philosophy → code mapping

—

## Focus Areas
- Plumbing validation: Is IF.connect sequencing realistic (REST first; gRPC/MQ later)? Is the IFMessage concept sufficient?
- Philosophy → code → docs: Are claims traceable to code and documentation (cite path:line)?
- Governance: Does IF.guard translate to enforceable operations? Identify missing runbook elements.
- Testing/precision: Are FP/precision claims reproducible or at least plausibly packaged to reproduce?
- Risks: Circular dependencies, latency bottlenecks, security or privacy gaps.

—

## Sticky Metrics (TTT-aligned)
- IF.yologuard: Benchmark invariants (107/96; 42/42) + Recall @ 1% FPR on clean corpus
- IF.guard: 100% releases have decision JSON (with dissent if any)
- IF.connect: 100% messages validate; p95 latency budgets declared per level
- IF.armour.honeypot (planned): Honey-challenge in CI (no exfil), manifest recorded
- IF.armour.learner (planned): ≥5 patterns synthesized, 0 regressions on falsifiers
- IF.witness: MARL entry + at least one falsifiable prediction per analysis
- IF.foundations/IF.vision: Philosophy→code link table exists with working citations

—

## Output 1: Model Identification (JSON)
```json
{
  "model": "<e.g., GPT-5-High / Claude Opus / Gemini Ultra / Human>",
  "version": "<model/version if known>",
  "timestamp": "<ISO-8601>",
  "review_duration_minutes": 60
}
```

—

## Output 2: Plain-Language Review (200–500 words)
Address:
- Strengths (top 3)
- Concerns/Risks (top 3)
- Missed opportunities (novelty with rationale)
- Feasibility of roadmap (what will slip)
- Verdict (proceed/pivot + why)

—

## Output 3: Structured JSON (paste this object)
Use the schema fields exactly (omit what you can’t fill). Cite files as `path:line`.

```json
{
  "review_id": "<unique-id>",
  "timestamp": "<ISO-8601>",
  "reviewer": {"model": "<name>", "version": "<ver>", "duration_minutes": 60},
  "overall_rating": 0.0,
  "comment": "short comment",
  "repo_overview": {
    "layout_style_substance": "...",
    "strengths": ["..."],
    "issues": ["..."],
    "citations": ["README.md:1"]
  },
  "birds_eye": {
    "coherence": "...",
    "novelty": "...",
    "roadmap_feasibility": "...",
    "plumbing_validation": "...",
    "citations": ["IF_CONNECTIVITY_ARCHITECTURE.md:1"]
  },
  "components": [
    {
      "name": "IF.yologuard",
      "summary": "...",
      "architecture_rating": 0.0,
      "maturity_rating": 0.0,
      "sticky_metric": "107/96; 42/42; Recall@1%FPR",
      "metrics": {},
      "gaps": ["..."],
      "citations": ["code/yologuard/src/IF.yologuard_v3.py:763"]
    }
  ],
  "critical_issues": [
    {"severity": "high", "category": "reproducibility", "description": "...", "impact": "...", "mitigation": "...", "citations": ["..."]}
  ],
  "recommendations": [
    {"category": "must-fix", "priority": 1, "description": "...", "rationale": "...", "effort_estimate": "hours/days"}
  ],
  "final_verdict": {
    "proceed": true,
    "confidence": 0.0,
    "conditions": ["..."],
    "key_risks": ["..."],
    "success_probability": 0.0
  }
}
```

—

## Optional Runtime (only if you can run code)
- Benchmark (expect 107/96; 42/42):
  - `bash code/yologuard/repro/run_benchmark.sh`
- Forensics profile (JSON + SARIF + graph + manifest + PQ):
  - `bash code/yologuard/repro/run_forensics.sh`
- Head‑to‑head (requires `gitleaks` and `trufflehog` in PATH via pipx):
  - `bash code/yologuard/repro/run_head2head.sh`

Safety boundaries:
- No live validation or exfiltration. Always redact. Limit to local repo.

—

## Review Quality Bar
- Cite claims to exact files (path:line) where possible
- Separate poetic motivation from technical requirements
- Flag heuristics and over-precision explicitly
- Be critical but constructive; deliver actionable recommendations

—

## Submission Format
Reply with three blocks:
1) Output 1 JSON (Model Identification)
2) Output 2 (Plain-language review)
3) Output 3 JSON (Structured review)

Thank you for your rigorous review.
