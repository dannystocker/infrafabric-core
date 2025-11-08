# Call for External Reviewers (InfraFabric)

We are seeking independent reviews from security engineers, software architects, governance/process experts, and research methodologists.

What to review:
- Whole repo (master): layout, style, contribution readiness
- Birds‑eye architecture: coherence, novelty, roadmap realism
- Sections: IF.yologuard, IF.guard, IF.connect, IF.armour (honeypot/learner plans), IF.witness, IF.foundations/IF.vision, papers

How to review:
1) Read EXTERNAL_REVIEW_PROMPT_IF_FULL.md and use REVIEW_SCHEMA.json
2) Reproduce key metrics (see STICKY_METRICS.md; yologuard benchmark and forensics profile)
3) File your review as:
   - Plain‑language report (2–4 pages)
   - Structured JSON using REVIEW_SCHEMA.json
4) Submit via PR under `code/yologuard/reviews/<date>_<reviewer>/` (include your JSON and MD)

Artifacts to help (Raw links where possible):
- Review prompt (raw): https://raw.githubusercontent.com/dannystocker/infrafabric/refs/heads/master/EXTERNAL_REVIEW_PROMPT_IF_FULL.md
- JSON schema (raw): https://raw.githubusercontent.com/dannystocker/infrafabric/refs/heads/master/REVIEW_SCHEMA.json
- Sticky metrics (raw): https://raw.githubusercontent.com/dannystocker/infrafabric/refs/heads/master/STICKY_METRICS.md
- Yologuard update (raw): https://raw.githubusercontent.com/dannystocker/infrafabric/refs/heads/master/code/yologuard/EXTERNAL_REVIEW_UPDATE.md
- Yologuard external results (raw): https://raw.githubusercontent.com/dannystocker/infrafabric/refs/heads/master/code/yologuard/EXTERNAL_REVIEW_RESULTS.md
- Yologuard guardian handoff (raw): https://raw.githubusercontent.com/dannystocker/infrafabric/refs/heads/master/code/yologuard/integration/GUARDIAN_HANDOFF_v3.1_IEF.md

Ethical boundaries:
- No live credential validation; no data exfiltration
- Redaction required in public artifacts

Thank you for strengthening IF with rigorous feedback.
