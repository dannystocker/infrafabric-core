# IF.philosophy → Code Link Map (v1)

This map connects philosophy principles to concrete implementations across IF.* modules, with evidence-bound citations.

## Principles (Novice Aliases)
- Relationship Score (Wu Lun)
- Falsifiability (Popper)
- Duty (Kant)
- Interdependence (Nagarjuna/Fazang)
- Prudence (Stoic)
- Coherentism & Pragmatism (Quine/James)

## Link Table

| Principle | Novice alias | Module | Implementation | Evidence (path:line) | Sticky/Metric | Next improvement |
|---|---|---|---|---|---|---|
| Wu Lun | Relationship Score | IF.yologuard | Relationship scoring influences severity; relationships emitted in results | code/yologuard/src/IF.yologuard_v3.py:1007 (danger/structure), 1118 (graph), 1210 (provenance) | Maintain 107/96; 42/42; Recall@1%FPR | Cross-file closures (Indra Net) |
| Popper | Falsifiability | IF.guard | Decision artifacts + dissent enable falsification of proposals | schemas/decision/v1.0.schema.json:1, governance/examples/decision_example.json:1, governance/DECISION_DISSENT_RUNBOOK.md:1 | 100% decision JSON coverage | CI enforces decision JSON schema for releases |
| Kant | Duty / Safety | IF.yologuard | No live validation; redaction; sandbox-only structure checks | code/yologuard/src/IF.yologuard_v3.py:1096–1113 (structure/PQ), SECURITY.md:1 | Safety policy documented | Doc exceptions policy; unit tests for redaction |
| Nagarjuna/Fazang | Interdependence | IF.yologuard | Indra graph nodes/edges for relations/danger | code/yologuard/src/IF.yologuard_v3.py:1118–1236 | Graph exported in forensics | Severity boost on triangle closures (config↔key↔endpoint) |
| Stoic | Prudence / SLOs | IF.connect | Performance targets (p95/per-level) and async fallback semantics | docs/PERFORMANCE_TARGETS.md:1, IF_CONNECTIVITY_ARCHITECTURE.md:1 | Publish p95 per level | Manual perf job; async circuit breaker RFC |
| Coherentism/Pragmatism | Evidence + utility | IF.review | Evidence-Binding Mandate; reviewer JSON schema | EXTERNAL_REVIEW_ARENA_PROMPT.md: Evidence-Binding section, REVIEW_SCHEMA.json:1 | 100% evidence bound | Auto-check path:line citations (future lint) |

## Suggested Annotations (Optional)
- Extend messages/decisions with a `principles` array documenting which principles influenced the decision (see RFC below).

## Reading Map
- IF.vision (philosophical basis): papers/IF-vision.md:1
- IF.foundations (anti-hallucination & methodology): papers/IF-foundations.md:1
- IF.witness (meta-validation): papers/IF-witness.md:1

