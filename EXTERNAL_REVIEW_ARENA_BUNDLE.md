# InfraFabric — Single‑File Review Bundle (Offline‑Friendly)

This file contains everything a reviewer needs in one place: instructions, evidence rules, output templates, schema JSON, sticky metrics, and core context excerpts. Use this if your environment has limited or no internet access.

—

## 1) Review Instructions (Arena Prompt)

Provide three outputs:
- Output 1: Model Identification (JSON)
- Output 2: Plain‑language review (200–500 words)
- Output 3: Structured JSON (use the schema in section 3)

Scope:
- GitHub repository (layout, style, contribution readiness)
- Birds‑eye (coherence, novelty, roadmap realism, plumbing correctness)
- Sections: IF.yologuard, IF.guard, IF.connect, IF.armour, IF.witness, IF.foundations/IF.vision

Focus Areas:
- Plumbing validation (REST first; defer gRPC/MQ). Is IFMessage sufficient?
- Philosophy → code → docs: trace claims to sources (cite path:line)
- Governance enforceability (guardian decisions → runtime runbook)
- Precision/testing: FP/precision claims, falsifiers, adversarial tests
- Risks: cycles, bottlenecks, security/privacy gaps

Evidence‑Binding Mandate (CRITICAL):
- For every Weakness, any score < 8/10, and any Critical Issue, include a direct, verifiable citation to a provided source.
- Format: prefer `path:line` (e.g., `code/yologuard/src/IF.yologuard_v3.py:763`). If section‑based, use `[Evidence: FILENAME.md, Section Heading]` and ensure the section text supports the claim.
- If no specific textual artifact can be found, do not make that criticism; state: "No significant flaws found in this area based on provided documents."
- All critiques must be falsifiable and grounded in observable evidence.

Output 1: Model Identification (JSON)
```json
{
  "model": "<e.g., GPT-5-High / Claude Opus / Gemini Ultra / Human>",
  "version": "<model/version if known>",
  "timestamp": "<ISO-8601>",
  "review_duration_minutes": 60
}
```

Output 2: Plain‑Language Review (200–500 words)
- Strengths (top 3)
- Concerns/Risks (top 3)
- Missed opportunities (novelty with rationale)
- Feasibility (what will slip)
- Verdict (proceed/pivot + why)

Output 3: Structured JSON (use schema below; omit unknowns)
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

## 2) Sticky Metrics (TTT‑Aligned)

- IF.yologuard: 107/96 + 42/42; Recall @ 1% FPR (clean corpus)
- IF.guard: 100% releases have decision JSON (with dissent if any)
- IF.connect: 100% messages validate; p95 latency budgets per level
- IF.armour.honeypot (planned): Honey‑challenge in CI (no exfil), manifest recorded
- IF.armour.learner (planned): ≥5 patterns synthesized; 0 falsifier regressions
- IF.witness: MARL entry + ≥1 falsifiable prediction per analysis
- IF.foundations/IF.vision: Philosophy→code link table exists with working citations

—

## 3) Structured JSON Schema (inline)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "InfraFabric External Review Schema",
  "type": "object",
  "required": ["review_id", "reviewer", "overall_rating", "repo_overview", "birds_eye", "components", "critical_issues", "recommendations", "final_verdict"],
  "properties": {
    "review_id": {"type": "string"},
    "timestamp": {"type": "string"},
    "reviewer": {"type": "object", "required": ["model", "version"], "properties": {"model": {"type": "string"}, "version": {"type": "string"}, "duration_minutes": {"type": "number"}}},
    "overall_rating": {"type": "number", "minimum": 0, "maximum": 1},
    "comment": {"type": "string"},
    "repo_overview": {"type": "object", "properties": {"layout_style_substance": {"type": "string"}, "strengths": {"type": "array", "items": {"type": "string"}}, "issues": {"type": "array", "items": {"type": "string"}}, "citations": {"type": "array", "items": {"type": "string"}}}},
    "birds_eye": {"type": "object", "properties": {"coherence": {"type": "string"}, "novelty": {"type": "string"}, "roadmap_feasibility": {"type": "string"}, "plumbing_validation": {"type": "string"}, "citations": {"type": "array", "items": {"type": "string"}}}},
    "components": {"type": "array", "items": {"type": "object", "required": ["name", "summary", "sticky_metric"], "properties": {"name": {"type": "string"}, "summary": {"type": "string"}, "architecture_rating": {"type": "number", "minimum": 0, "maximum": 1}, "maturity_rating": {"type": "number", "minimum": 0, "maximum": 1}, "sticky_metric": {"type": "string"}, "metrics": {"type": "object"}, "gaps": {"type": "array", "items": {"type": "string"}}, "citations": {"type": "array", "items": {"type": "string"}}}}},
    "critical_issues": {"type": "array", "items": {"type": "object", "required": ["severity", "description"], "properties": {"severity": {"type": "string", "enum": ["high", "medium", "low"]}, "category": {"type": "string"}, "description": {"type": "string"}, "impact": {"type": "string"}, "mitigation": {"type": "string"}, "citations": {"type": "array", "items": {"type": "string"}}}}},
    "recommendations": {"type": "array", "items": {"type": "object", "required": ["category", "priority", "description"], "properties": {"category": {"type": "string"}, "priority": {"type": "integer", "minimum": 1}, "description": {"type": "string"}, "rationale": {"type": "string"}, "effort_estimate": {"type": "string"}}}},
    "final_verdict": {"type": "object", "required": ["proceed", "confidence"], "properties": {"proceed": {"type": "boolean"}, "confidence": {"type": "number", "minimum": 0, "maximum": 1}, "conditions": {"type": "array", "items": {"type": "string"}}, "key_risks": {"type": "array", "items": {"type": "string"}}, "success_probability": {"type": "number", "minimum": 0, "maximum": 1}}}
  }
}
```

—

## 4) Key Context Excerpts (inline)

Yologuard CLI Help (excerpt)
```
usage: IF.yologuard_v3.py [-h] [--scan SCAN] [--json JSON_OUT]
                          [--out TEXT_OUT] [--sarif SARIF_OUT]
                          [--manifest MANIFEST_OUT] [--forensics]
                          [--graph-out GRAPH_OUT]
                          [--memory-state MEMORY_STATE] [--reset-memory]
                          [--pq-report PQ_REPORT] [--sbom SBOM_PATH]
                          [--error-threshold ERROR_THRESHOLD]
                          [--warn-threshold WARN_THRESHOLD]
                          [--mode {usable,component,both}] [--stats]
                          [--max-file-bytes MAX_FILE_BYTES]
                          [--profile {ci,ops,audit,research,forensics}]
                          [--demo]
```

Sticky Metrics (inline copy)
```
- IF.yologuard: 107/96 + 42/42; Recall @ 1% FPR
- IF.guard: decision JSON for 100% releases
- IF.connect: schema validation + p95 budgets per level
- IF.armour.honeypot: honey-challenge in CI (no exfil)
- IF.armour.learner: ≥5 patterns; 0 falsifier regressions
- IF.witness: MARL + falsifiable prediction
- IF.foundations/IF.vision: philosophy→code link table
```

—

## 5) Optional Runtime (local)
- Benchmark: run `code/yologuard/benchmarks/run_leaky_repo_v3_philosophical_fast_v2.py` (expect 107/96; 42/42)
- Forensics: run yologuard with `--profile forensics` (JSON/SARIF/graph/manifest/PQ)
- Head‑to‑head (requires `gitleaks` and `trufflehog`): `code/yologuard/harness/head2head.py`

Safety: No live validation or exfiltration; always redact.

—

End of bundle.
