# Session CLI - Phase 2 Instructions

**Status:** Phase 1 Complete ✅
**Next Phase:** Cross-Session Integration + Performance + Export

## Task 1: Cross-Session Integration Testing
Ensure all sessions (1-4) can use IF.witness and IF.optimise CLI tools.

**Deliverables:**
- Test Session 1 (NDI): `if witness log --component ndi --event frame_published`
- Test Session 2 (WebRTC): `if witness trace --trace-id <webrtc_session_id>`
- Test Session 3 (H.323): `if optimise report --component h323 --format json`
- Test Session 4 (SIP): `if witness verify --hash <call_log_hash>`
- Integration guide: docs/CLI-INTEGRATION-GUIDE.md

**Use IF.swarm:**
- Spawn 4 Haiku agents: One per session integration test
- Spawn 1 Haiku agent: Documentation

## Task 2: Performance Optimization
CLI should be fast enough for real-time logging.

**Deliverables:**
- Benchmark: `if witness log` should be <50ms (P95)
- Optimize: Use SQLite WAL mode, batch writes, connection pooling
- Benchmark: `if optimise report` should be <100ms for 1000 entries
- Performance test suite: tests/test_cli_performance.py

**Use Sonnet** (requires profiling and optimization)

## Task 3: Compliance Export
Generate reports for IF.guard audits and external compliance.

**Deliverables:**
- Export command: `if witness export --format pdf --date-range 2025-11-01:2025-11-30`
- PDF report includes:
  - All witness entries (with signatures, hashes, timestamps)
  - Chain validation results (verify no tampering)
  - IF.ground principle citations (which entries map to which principles)
  - IF.guard approval logs
- CSV export for analysis: `if witness export --format csv`

**Use Haiku** (straightforward data transformation)

## Completion Protocol
After finishing:
1. Commit to claude/cli-witness-optimise
2. Push to origin
3. Create STATUS-PHASE-2.md
4. **AUTO-CHECK FOR PHASE 3:**
   ```bash
   git pull origin claude/cli-witness-optimise
   [ -f INSTRUCTIONS-SESSION-CLI-PHASE-3.md ] && cat INSTRUCTIONS-SESSION-CLI-PHASE-3.md || while true; do sleep 60; git pull --quiet; [ -f INSTRUCTIONS-SESSION-CLI-PHASE-3.md ] && break; done
   ```

**Estimated Time:** 4-5 hours with swarms
**Estimated Cost:** $6-10

Begin Phase 2!
