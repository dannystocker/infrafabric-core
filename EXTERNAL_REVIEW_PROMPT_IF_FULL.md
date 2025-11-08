# InfraFabric — Full Independent External Review Prompt (Master Project)

Audience: GPT‑5‑High, Claude Opus/Sonnet, Gemini Ultra, human experts (security, software architecture, research methods, governance).

Objective: Produce a rigorous, independent review of the entire InfraFabric repository (master branch), grounded in verifiable artifacts, with actionable recommendations and a standardized JSON output for aggregation.

Quick Access Links (GitHub):
- Repo root: https://github.com/dannystocker/infrafabric
- Connectivity architecture: https://github.com/dannystocker/infrafabric/blob/master/IF_CONNECTIVITY_ARCHITECTURE.md
- Session handoff: https://github.com/dannystocker/infrafabric/blob/master/SESSION_HANDOFF_2025-11-08_IF-ARMOUR.md
- Yologuard main README: https://github.com/dannystocker/infrafabric/blob/master/code/yologuard/README.md
- Yologuard detector (CLI): https://github.com/dannystocker/infrafabric/blob/master/code/yologuard/src/IF.yologuard_v3.py
- Guardian handoff: https://github.com/dannystocker/infrafabric/blob/master/code/yologuard/integration/GUARDIAN_HANDOFF_v3.1_IEF.md
- External review results: https://github.com/dannystocker/infrafabric/blob/master/code/yologuard/EXTERNAL_REVIEW_RESULTS.md
- External review update: https://github.com/dannystocker/infrafabric/blob/master/code/yologuard/EXTERNAL_REVIEW_UPDATE.md
- Papers index: https://github.com/dannystocker/infrafabric/tree/master/papers

Instructions:
1) Clone and read.
   - Repo: https://github.com/dannystocker/infrafabric (branch: master)
   - Explore the full tree. Pay special attention to:
     - Repository docs at root (README.md, START-HERE.md, QUICKSTART.md, IF_CONNECTIVITY_ARCHITECTURE.md, SESSION_HANDOFF_*.md)
     - papers/ (IF‑vision, IF‑foundations, IF‑armour, IF‑witness, dossier)
     - code/yologuard/ (src/, benchmarks/, harness/, integration/, docs/)
     - annexes/, docs/, guardians/, examples/, simulations/
2) Cross‑reference philosophy → code → documentation.
   - For every philosophical claim (Wu Lun, TTT, IEF, IF.connect levels, IF.guard council), identify the corresponding code paths and documentation references.
   - Cite exact files with line anchors (path:line) where feasible.
3) Evaluate at three levels:
   - GitHub repository itself: layout, style, structure, contribution readiness.
   - Birds‑eye (InfraFabric as a whole): coherence, architectural completeness, roadmap realism, novelty.
   - Section‑by‑section: each major component (see “Components” below).
4) Validate planned “plumbing”.
   - Review IF.connect 5‑level framework (function→module→service→module→ecosystem) for over/under‑engineering; recommend sequencing (REST/gRPC/MQ) and message schema sufficiency (IFMessage).
5) Provide “sticky metrics”.
   - For each component, define 1 non‑negotiable “sticky metric” that guides devs (objective, repeatable, aligns with TTT values).
6) Output format: two deliverables
   - Plain‑language report (2–4 pages) with findings and rationale.
   - Structured JSON using REVIEW_SCHEMA.json (root) — include citations at path:line.

Components to review:
- IF.yologuard (v3.1.1) — detection engine, IEF, TTT, PQ (experimental)
- IF.guard — guardian handoff, governance process
- IF.connect — connectivity architecture (Level 0–4)
- IF.armour (suite vision) — honeypot (planned), learner (planned)
- IF.witness — meta‑validation methodology (MARL, epistemic swarm)
- IF.foundations/IF.vision — philosophy and architectural groundings

Evidence & Repro steps (yologuard):
- Benchmark: `python3 code/yologuard/benchmarks/run_leaky_repo_v3_philosophical_fast_v2.py` (expect 107/96; 42/42)
- Forensics profile: `python3 code/yologuard/src/IF.yologuard_v3.py --scan code/yologuard/benchmarks/leaky-repo --profile forensics --json ief.json --sarif ief.sarif --graph-out indra.json --manifest ief.manifest --pq-report pq.json --stats`
- Head‑to‑head (optional): `python3 code/yologuard/harness/head2head.py --config code/yologuard/harness/corpus_config.json --workdir /tmp/yolo-corpus --json code/yologuard/reports/<ts>/head2head.json --md code/yologuard/reports/<ts>/head2head.md`

Deliverables (paste back into a PR comment or a new file under `code/yologuard/reviews/`):
- OUTPUT 1: Model ID (JSON)
- OUTPUT 2: Plain‑language report (2–4 pages)
- OUTPUT 3: Structured JSON review (REVIEW_SCHEMA.json)

Quality bar:
- Cite everything (paths + lines). Mark any aspirational claims as such. Prefer empirical validation to assertions.
- Be critical. Identify circular dependencies, latency bottlenecks, security risks, over‑precise heuristics, and missing tests.

Thank you for your thorough review.
