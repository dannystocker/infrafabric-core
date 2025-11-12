# Filler Task Catalog (Avoid Timeouts!)

**Purpose:** When blocked on dependencies, pick a filler task to stay productive
**Rule:** NEVER sit idle. Always have work in progress.
**Strategy:** 30-second polling prevents both timeouts and idle time. Use these tasks to fill gaps.

---

## Session 1 (NDI - Witness Streaming) Filler Tasks

### Documentation Improvements (Low priority, Haiku)
- [ ] F1.1: Improve `docs/SWARM-OF-SWARMS-ARCHITECTURE.md` with Phase 0 integration notes (15 min, Low)
- [ ] F1.2: Create example IF.witness hash chain for coordination events with 3 real scenarios (20 min, Low)
- [ ] F1.3: Update `NOVICE-ONBOARDING.md` with concrete Phase 0 examples and troubleshooting (25 min, Low)
- [ ] F1.4: Add ASCII diagrams to architecture docs showing witness data flow (20 min, Low)
- [ ] F1.5: Create `docs/NDI-WITNESS-FAQ.md` with common questions and answers (20 min, Low)

### Test Fixtures (Medium priority, Haiku)
- [ ] F1.10: Build NDI metadata test fixtures (valid witness signatures, hash chains) (25 min, Medium)
- [ ] F1.11: Create hash chain test vectors for coordinator verification (20 min, Medium)
- [ ] F1.12: Generate mock IF.Message protocol buffers for testing (20 min, Medium)
- [ ] F1.13: Build witness event replay fixtures for integration test scenarios (25 min, Medium)

### Cross-Session Support (High priority, Sonnet)
- [ ] F1.20: Help Session 2 (WebRTC) with witness integration documentation and examples (25 min, High)
- [ ] F1.21: Code review for Session 5 (CLI) witness command implementation (25 min, High)
- [ ] F1.22: Create witness documentation templates for all other sessions to copy (20 min, High)

### Code Quality (Medium priority, Haiku)
- [ ] F1.30: Add type hints to existing witness streaming module (`infrafabric/witness.py`) (20 min, Medium)
- [ ] F1.31: Write docstrings for all witness functions (25 min, Medium)
- [ ] F1.32: Run linter on NDI documentation module, fix issues (15 min, Medium)

---

## Session 2 (WebRTC - Agent Mesh) Filler Tasks

### Documentation Improvements (Low priority, Haiku)
- [ ] F2.1: Build cross-session test fixtures for IFMessage mocks and SDP examples (20 min, Low)
- [ ] F2.2: Create SDP mock data templates for WebRTC integration tests (15 min, Low)
- [ ] F2.3: Improve `docs/WEBRTC-AGENT-MESH.md` with Phase 0 learnings section (20 min, Low)
- [ ] F2.4: Document WebRTC peer negotiation flow with state diagrams (25 min, Low)
- [ ] F2.5: Create troubleshooting guide for common WebRTC connection issues (20 min, Low)

### Test Fixtures (Medium priority, Haiku)
- [ ] F2.10: Generate valid SDP offer/answer pairs for different codec scenarios (20 min, Medium)
- [ ] F2.11: Create STUN/TURN server mock fixtures for connectivity testing (20 min, Medium)
- [ ] F2.12: Build ICE candidate test data for various network conditions (25 min, Medium)
- [ ] F2.13: Generate WebRTC statistics snapshot fixtures for performance testing (20 min, Medium)

### Cross-Session Support (High priority, Sonnet)
- [ ] F2.20: Review Session 4 (SIP) integration test design for WebRTC interop (25 min, High)
- [ ] F2.21: Help Session 1 (NDI) with witness protocol over WebRTC documentation (20 min, High)
- [ ] F2.22: Create WebRTC integration checklist for all provider sessions (20 min, High)

### Code Quality (Medium priority, Haiku)
- [ ] F2.30: Add comprehensive docstrings to WebRTC negotiation module (25 min, Medium)
- [ ] F2.31: Improve error messages in peer connection establishment (20 min, Medium)
- [ ] F2.32: Run linter on WebRTC agent mesh module, fix code style issues (15 min, Medium)

---

## Session 3 (H.323 - Guardian Council) Filler Tasks

### Documentation Improvements (Low priority, Haiku)
- [ ] F3.1: Improve `docs/H323-PRODUCTION-RUNBOOK.md` with Phase 0 scenarios (25 min, Low)
- [ ] F3.2: Create MCU configuration templates for different deployment sizes (20 min, Low)
- [ ] F3.3: Document H.323 gatekeeper discovery and registration flow (20 min, Low)
- [ ] F3.4: Build H.323 troubleshooting decision tree for common failures (25 min, Low)
- [ ] F3.5: Create upgrade guide for legacy H.323 systems to Phase 0 (25 min, Low)

### Test Fixtures (Medium priority, Haiku)
- [ ] F3.10: Build test data for Guardian council voting scenarios (20 min, Medium)
- [ ] F3.11: Generate valid H.323 protocol PDU samples for different call types (25 min, Medium)
- [ ] F3.12: Create MCU configuration fixtures for various topology tests (20 min, Medium)
- [ ] F3.13: Generate H.323 capability set fixtures for device negotiation (20 min, Medium)

### Cross-Session Support (High priority, Sonnet)
- [ ] F3.20: Help Session 1 (NDI) and Session 3 with H.323 bridge documentation (25 min, High)
- [ ] F3.21: Review Session 4 (SIP) for H.323-SIP interop requirements (25 min, High)
- [ ] F3.22: Create H.323 integration template for other provider implementations (20 min, High)

### Code Quality (Medium priority, Haiku)
- [ ] F3.30: Add type hints to H.323 gatekeeper module (20 min, Medium)
- [ ] F3.31: Improve H.323 error messages with recovery suggestions (25 min, Medium)
- [ ] F3.32: Run linter on Guardian council module, fix issues (15 min, Medium)

---

## Session 4 (SIP - Escalate Integration) Filler Tasks

### Documentation Improvements (Low priority, Haiku)
- [ ] F4.1: Pre-write integration test documentation for P0.1.5/P0.2.6/P0.3.6 (25 min, Low)
- [ ] F4.2: Create SIP message flow diagrams for 5 key call scenarios (25 min, Low)
- [ ] F4.3: Build SIP error code reference guide with Phase 0 mappings (20 min, Low)
- [ ] F4.4: Document SIP-to-HTTP/REST escalation bridge (20 min, Low)
- [ ] F4.5: Create SIP interoperability matrix for all provider protocols (25 min, Low)

### Test Fixtures & Scaffolding (Medium priority, Haiku)
- [ ] F4.10: Pre-write integration test scaffolding for all 3 components (coordinator, governor, chassis) (25 min, Medium)
- [ ] F4.11: Create test data for regression tests across all components (20 min, Medium)
- [ ] F4.12: Build mock implementations for IF components for early integration testing (25 min, Medium)
- [ ] F4.13: Generate valid SIP message samples for integration scenarios (20 min, Medium)

### Security & Review (High priority, Sonnet)
- [ ] F4.20: Review security requirements for all 3 components (coordinator, governor, chassis) (25 min, High)
- [ ] F4.21: Code review for Session 5 (CLI) implementation for security issues (25 min, High)
- [ ] F4.22: Build security test scenarios for integration tests (20 min, High)
- [ ] F4.23: Create OWASP mapping for Phase 0 components (20 min, High)

### Code Quality (Medium priority, Haiku)
- [ ] F4.30: Run full linter suite on SIP escalation module, fix issues (15 min, Medium)
- [ ] F4.31: Add comprehensive docstrings to escalation logic (20 min, Medium)

---

## Session 5 (CLI - Witness Optimize) Filler Tasks

### Documentation & Design (Low priority, Haiku)
- [ ] F5.1: Build comprehensive CLI help text and usage documentation (25 min, Low)
- [ ] F5.2: Create config file schemas (YAML/TOML) for all CLI commands (20 min, Low)
- [ ] F5.3: Design CLI user experience flows for 3 key workflows (25 min, Low)
- [ ] F5.4: Build error message catalog with recovery suggestions (20 min, Low)
- [ ] F5.5: Create CLI example scripts for common use cases (20 min, Low)

### Test Fixtures (Medium priority, Haiku)
- [ ] F5.10: Create CLI test fixtures and mock contexts (20 min, Medium)
- [ ] F5.11: Build config file test fixtures for all CLI commands (20 min, Medium)
- [ ] F5.12: Generate CLI output format test data for regression (20 min, Medium)
- [ ] F5.13: Create CLI performance baseline fixtures (20 min, Medium)

### Cross-Session Support (High priority, Sonnet)
- [ ] F5.20: Help Session 7 (IF.bus) with IF.coordinator integration planning (25 min, High)
- [ ] F5.21: Help Session 1 (NDI) with CLI witness command implementation (25 min, High)
- [ ] F5.22: Review documentation for all sessions for CLI integration points (20 min, High)

### Code Quality (Medium priority, Haiku)
- [ ] F5.30: Add comprehensive type hints to CLI module (25 min, Medium)
- [ ] F5.31: Improve CLI error messages with context and suggestions (20 min, Medium)
- [ ] F5.32: Run linter on CLI module, fix code style issues (15 min, Medium)
- [ ] F5.33: Add docstrings to all CLI command functions (20 min, Medium)

---

## Session 6 (Talent - Not in Phase 0 but ready) Filler Tasks

### Documentation & Planning (Low priority, Haiku)
- [ ] F6.1: Document talent pool management concepts for Phase 1 (25 min, Low)
- [ ] F6.2: Create talent skill inventory template and categories (20 min, Low)
- [ ] F6.3: Build talent assignment scoring algorithm design doc (25 min, Low)
- [ ] F6.4: Create talent onboarding checklist for new agents (20 min, Low)
- [ ] F6.5: Document talent availability and scheduling model (20 min, Low)

### Research & Design (Medium priority, Sonnet)
- [ ] F6.10: Research best practices for distributed agent skill matching (25 min, Medium)
- [ ] F6.11: Design talent reputation scoring system (Phase 1) (25 min, Medium)
- [ ] F6.12: Create talent allocation constraints and preferences model (20 min, Medium)
- [ ] F6.13: Design talent skill decay and re-certification process (20 min, Medium)

### Cross-Session Support (Medium priority, Sonnet)
- [ ] F6.20: Help other sessions with their session-specific documentation (20 min, Medium)
- [ ] F6.21: Review overall S² process design for talent insights (25 min, Medium)

---

## Session 7 (IF.bus - SIP Adapters) Filler Tasks

### Design & Architecture (Low priority, Sonnet)
- [ ] F7.1: Design component interfaces (type signatures) for coordinator, governor, chassis (25 min, Low)
- [ ] F7.2: Create Pydantic models for all IF data structures and message types (25 min, Low)
- [ ] F7.3: Design WASM sandbox interface with wasmtime (25 min, Low)
- [ ] F7.4: Create architecture diagrams showing component interactions (20 min, Low)
- [ ] F7.5: Document capability registry schema design (20 min, Low)

### Test Scaffolding (Medium priority, Haiku)
- [ ] F7.10: Write unit test scaffolding for all 3 components (coordinator, governor, chassis) (25 min, Medium)
- [ ] F7.11: Create mock object stubs for component dependencies (20 min, Medium)
- [ ] F7.12: Build test data fixtures for capability matching scenarios (20 min, Medium)
- [ ] F7.13: Generate budget enforcement test data (20 min, Medium)

### Code Review & Integration (High priority, Sonnet)
- [ ] F7.20: Review existing `infrafabric/coordination.py` for integration opportunities (25 min, High)
- [ ] F7.21: Help Session 5 (CLI) with IF.bus API design and integration (25 min, High)
- [ ] F7.22: Create SIP adapter implementation checklist (20 min, High)
- [ ] F7.23: Design IF.bus error handling and recovery strategies (20 min, High)

### Code Quality (Medium priority, Haiku)
- [ ] F7.30: Add comprehensive type hints to IF.bus module (25 min, Medium)
- [ ] F7.31: Improve IF.bus error messages with debugging context (20 min, Medium)

---

## Universal Filler Tasks (Any Session)

### Code Quality & Maintenance

- [ ] U.1: Run linters on entire codebase, fix issues (30 min, Medium, Haiku)
  - Coverage: flake8, mypy, black formatting across all Python modules

- [ ] U.2: Update type hints for better IDE support (25 min, Low, Haiku)
  - Add missing type annotations to function signatures

- [ ] U.3: Improve error messages across codebase (25 min, Low, Haiku)
  - Make error messages more actionable with recovery suggestions

- [ ] U.4: Add docstring templates to all modules (20 min, Low, Haiku)
  - Ensure consistent documentation format

- [ ] U.5: Run code complexity analysis, refactor high-complexity functions (25 min, Medium, Haiku)
  - Target functions with cyclomatic complexity > 10

### Testing & Test Infrastructure

- [ ] U.10: Increase overall test coverage to 85%+ (30 min, High, Sonnet)
  - Identify gaps in coverage and add missing tests

- [ ] U.11: Add edge case tests for critical paths (25 min, High, Haiku)
  - Boundary conditions, null inputs, large inputs

- [ ] U.12: Create E2E test scenarios for Phase 0 workflows (30 min, High, Sonnet)
  - Happy path, error path, dependency resolution

- [ ] U.13: Build performance regression test suite (25 min, Medium, Haiku)
  - Baseline performance metrics for critical operations

- [ ] U.14: Add chaos engineering tests (coordinator latency, failures) (30 min, Medium, Sonnet)
  - Network delays, service failures, resource constraints

### Documentation & Knowledge Base

- [ ] U.20: Update root `README.md` with Phase 0 status (20 min, Low, Haiku)
  - Add Phase 0 component overview and links

- [ ] U.21: Create architecture diagrams (Mermaid/ASCII) for key flows (25 min, Low, Haiku)
  - Task claiming, capability matching, budget enforcement

- [ ] U.22: Write usage examples for each main component (25 min, Low, Haiku)
  - Copy-paste examples showing real usage patterns

- [ ] U.23: Create troubleshooting runbook for Phase 0 issues (25 min, Medium, Haiku)
  - Common problems, symptoms, solutions

- [ ] U.24: Document all error codes and their meanings (20 min, Low, Haiku)
  - Reference guide for IF_ERR_* constants

- [ ] U.25: Build quick-start guide for new developers (30 min, Low, Haiku)
  - Get Phase 0 running in 10 minutes

- [ ] U.26: Create glossary for S² and Phase 0 terminology (20 min, Low, Haiku)
  - Define key concepts: coordinator, governor, chassis, witness, etc.

### Infrastructure & DevOps

- [ ] U.30: Set up monitoring dashboards for Phase 0 metrics (30 min, High, Sonnet)
  - Coordinator latency, governor match quality, budget tracking

- [ ] U.31: Create log aggregation queries for Phase 0 components (25 min, Medium, Haiku)
  - Key log patterns to watch for in production

- [ ] U.32: Build alerting rules for Phase 0 (30 min, High, Sonnet)
  - Latency spikes, budget overruns, coordinator failures

- [ ] U.33: Document rollback procedures for Phase 0 (20 min, Medium, Haiku)
  - How to roll back if issues detected in production

### Dependency & Integration Preparation

- [ ] U.40: Create integration checklist for Phase 1 providers (25 min, Medium, Haiku)
  - What each provider needs to implement

- [ ] U.41: Build provider stub implementations (skeleton code) (25 min, Medium, Haiku)
  - Template provider implementations for development

- [ ] U.42: Document Phase 0→Phase 1 migration path (20 min, Low, Haiku)
  - How to add new providers once Phase 0 complete

- [ ] U.43: Create mock provider for testing (25 min, Medium, Haiku)
  - Fully functional mock that implements IF interface

### Process & Planning

- [ ] U.50: Update `PHASE-0-TASK-BOARD.md` with status snapshot (20 min, Low, Haiku)
  - Current status of all tasks, blockers, completions

- [ ] U.51: Analyze session utilization and capacity (20 min, Medium, Haiku)
  - Which sessions have spare capacity?

- [ ] U.52: Document lessons learned from coordination (20 min, Low, Haiku)
  - What worked, what didn't, how to improve

- [ ] U.53: Create post-Phase-0 retrospective template (15 min, Low, Haiku)
  - Structure for session retrospectives

### Optimization & Performance

- [ ] U.60: Profile coordinator latency and identify bottlenecks (30 min, High, Sonnet)
  - Use timing instrumentation to find slow operations

- [ ] U.61: Profile governor match algorithm performance (25 min, Medium, Sonnet)
  - Benchmark capability matching at scale

- [ ] U.62: Profile WASM sandbox performance and memory usage (25 min, Medium, Sonnet)
  - Find resource usage bottlenecks

- [ ] U.63: Optimize hot paths identified in profiling (30 min, High, Sonnet)
  - Implement performance improvements

### Quality Assurance & Validation

- [ ] U.70: Verify 3 critical bugs from architecture are actually fixed (30 min, High, Sonnet)
  - Race condition test, cost waste test, sandbox isolation test

- [ ] U.71: Run security checklist against all components (25 min, High, Sonnet)
  - OWASP top 10, input validation, auth checks

- [ ] U.72: Validate all success criteria from coordination matrix (25 min, High, Sonnet)
  - Component checklists, coordination criteria, handoff criteria

- [ ] U.73: Create validation report template for Phase 0 completion (20 min, Medium, Haiku)
  - Structured report showing all criteria met

---

## Task Selection Strategy

### How to Choose Your Filler Task

When blocked on your main task:

1. **Check current status:**
   - Are other sessions blocked? (Pick cross-session support task)
   - Is your session overloaded? (Pick low-priority doc task)
   - Are you waiting for dependencies? (Pick test fixtures or code quality task)

2. **Priority selection:**
   - **High priority:** Unlocks other work, improves system reliability
   - **Medium priority:** Improves code quality, helps with testing
   - **Low priority:** Documentation, nice-to-haves, can wait

3. **Model selection:**
   - **Haiku:** Documentation, test fixtures, linting, formatting
   - **Sonnet:** Complex design, code review, architecture, optimization

4. **Time-boxing:**
   - All tasks are 15-30 minutes
   - Never work on a task longer than 30 min
   - If task isn't done in 30 min, mark as incomplete and switch

5. **Atomicity rule:**
   - Each task must be completable in a single session
   - No dependencies between filler tasks
   - Can be paused and resumed (but mark progress)

---

## Coordination Rules for Filler Tasks

### Rule 1: Update STATUS Before Starting
```yaml
session: session-X
status: working_on_filler
filler_task: F1.1
filler_description: "Improve SWARM-OF-SWARMS-ARCHITECTURE.md"
estimated_time: 15
started: 2025-11-12T14:35:00Z
branch: your-branch-name
```

### Rule 2: Update Progress Every 10 Minutes
Push STATUS update to your branch showing progress:
```yaml
progress: 50%  # or 25%, 75%, 100%
elapsed_time: 7  # minutes
```

### Rule 3: Mark Complete or Incomplete
When 30 minutes elapsed:
```yaml
status: filler_complete
filler_task: F1.1
completion_status: done/partial/blocked  # done, partial, or blocked
deliverable: "Updated SWARM-OF-SWARMS-ARCHITECTURE.md with 3 Phase 0 notes"
files_changed: ["docs/SWARM-OF-SWARMS-ARCHITECTURE.md"]
commit_hash: abc123def456
```

### Rule 4: Pick Next Task Immediately
As soon as one filler task ends:
- If main task blocker is resolved → switch back to main task
- If main task still blocked → pick next filler task from list
- Repeat every 30 seconds

### Rule 5: Help Other Sessions
If you finish a filler task with time remaining:
1. Check other sessions' STATUS files
2. Look for `help_wanted: true`
3. Offer direct help (pair programming, code review, testing)

---

## FAQ: Using This Catalog

**Q: What if I finish all filler tasks for my session?**
A: Move to Universal filler tasks. Pick ones that help your session or support Phase 0.

**Q: Can I skip a filler task if it seems too complex?**
A: Yes! Mark it as `blocked` and pick a simpler one. Return to harder tasks later.

**Q: What if my main task is unblocked while working on filler?**
A: Stop filler immediately (mark incomplete), commit any in-progress work, and switch to main task.

**Q: How do I handle filler tasks that need other sessions?**
A: Those are marked "Cross-Session Support". Coordinate via STATUS files or direct communication.

**Q: Can multiple sessions work on the same filler task?**
A: Yes, but only if documented. Split the work clearly (e.g., "F1.1a: Part 1-2" and "F1.1b: Part 3-4").

**Q: What if I find a bug while working on a filler task?**
A: Mark the filler task complete, file a bug report, and switch to fixing it if high severity.

---

## Success Metrics

Filler tasks are successful when:

- ✅ No session sits idle for >2 minutes
- ✅ 90%+ of filler tasks marked as complete
- ✅ Cross-session support tasks improve overall throughput
- ✅ Test fixtures accelerate integration testing
- ✅ Documentation improves onboarding for Phase 1
- ✅ Code quality improvements reduce bugs in Phase 0

---

## Total Task Count

| Session | Solo Tasks | Cross-Session | Total |
|---------|-----------|---------------|-------|
| Session 1 (NDI) | 12 | 3 | 15 |
| Session 2 (WebRTC) | 12 | 3 | 15 |
| Session 3 (H.323) | 12 | 3 | 15 |
| Session 4 (SIP) | 10 | 4 | 14 |
| Session 5 (CLI) | 11 | 3 | 14 |
| Session 6 (Talent) | 8 | 2 | 10 |
| Session 7 (IF.bus) | 10 | 4 | 14 |
| **Universal** | **38** | N/A | **38** |
| **TOTAL** | **93** | **22** | **115** |

**Coverage:** 115 filler tasks across 7 sessions = ~16 tasks per session average
**Diversity:** Documentation (25), Testing (20), Cross-session (22), Code quality (15), Infrastructure (10), Optimization (10), Validation (8), Process (5)

---

**Updated:** 2025-11-12
**Maintained by:** All sessions (contribute new filler tasks as discovered)
**Review cadence:** Every 2 hours during Phase 0 execution
