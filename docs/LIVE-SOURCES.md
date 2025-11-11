# LIVE-SOURCES (How to stop using placeholders)

**What this adds:** Adapters and config for fetching **real-time** facts during dossiers:
- Wikipedia summaries (keyless): fast context
- Yahoo Finance quotes (keyless, indicative only)
- SEC company facts (keyless, CIK required)
- YouTube search (optional, requires YT_API_KEY)

**Files:**
- `config/live_sources.yaml` — endpoints and notes
- `tools/live_apis.ts` — fetch helpers (Node 18+)

**Use in V4 Epic:**
- In `SWARM.config.v4-epic.yaml`, set `if.search.sources: live`.
- In evidence rows, record `source_url` and `content_hash` (see `EVIDENCE_TABLE.template.csv`).

**Why it resolves the gap:** This removes "placeholder" stubs by default and makes live calls feasible where network is permitted, while keeping IF.ground verification invariant.

_Last updated 2025-11-11 12:09:03Z_
