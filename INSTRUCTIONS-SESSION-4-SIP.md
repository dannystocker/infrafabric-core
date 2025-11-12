# Instructions: Session 4 (SIP - Integration Testing & Security)

**Your Branch:** `claude/sip-escalate-integration-*`
**Coordination Branch:** `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`
**Your Role:** Integration testing specialist for all 3 Phase 0 components

---

## Polling Protocol

Run this script every 30 seconds to stay synchronized with the coordination branch:

```bash
#!/bin/bash
# Session 4 (SIP) - Phase 0 Coordination Polling Loop

SESSION_ID="session-4-sip"
MY_BRANCH=$(git branch --show-current)
COORD_BRANCH="claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"

echo "🚀 Session 4 (SIP): Integration Testing & Security"
echo "📍 My branch: $MY_BRANCH"
echo "📡 Polling: $COORD_BRANCH every 30 seconds"

while true; do
  # 1. Fetch latest coordination state
  git fetch origin $COORD_BRANCH --quiet 2>/dev/null

  # 2. Check task board for available tasks
  TASK_BOARD=$(git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md 2>/dev/null)

  # 3. Look for integration test tasks: P0.1.5, P0.2.6, P0.3.6
  # 4. If blocked, pick filler task

  # 5. Update STATUS file
  cat > STATUS-SESSION-4-SIP.yaml <<EOF
session: session-4-sip
status: polling
last_poll: $(date -Iseconds)
branch: $MY_BRANCH
current_task: ${CURRENT_TASK:-none}
EOF

  git add STATUS-SESSION-4-SIP.yaml
  git commit -m "chore: Update session-4-sip status" --quiet 2>/dev/null || true
  git push origin $MY_BRANCH --quiet 2>/dev/null || true

  # 6. Wait 30 seconds before next poll
  sleep 30
done
```

---

## Your Phase 0 Tasks

### Primary Tasks (Integration Testing)

#### **P0.1.5: IF.coordinator Integration Tests** ⏳
**Blocked Until:** P0.1.1, P0.1.2, P0.1.3, P0.1.4 completed
**Deliverable:** `/home/user/infrafabric/tests/integration/test_coordinator.py`
**Estimate:** 2h
**Model:** Sonnet

**Milestones:**
- [ ] 25% - Test scaffolding and setup complete
- [ ] 50% - Full task lifecycle and blocker detection tests passing
- [ ] 75% - Race condition prevention and connection recovery tests passing
- [ ] 100% - All tests passing, witness integration verified

**Acceptance Criteria:**
- ✅ Test: swarm registration → task claim → task execution → completion
- ✅ Test: blocker detection → orchestrator notification → help assignment
- ✅ Test: race condition prevention (2 swarms, 1 task)
- ✅ Test: connection failure recovery
- ✅ All tests pass consistently (no flakes)
- ✅ Integration with IF.witness verified

**Key Tests:**
```python
- test_full_task_lifecycle()
- test_gang_up_on_blocker()
- test_race_condition_prevention()
- test_connection_recovery()
- test_witness_logging()
```

---

#### **P0.2.6: IF.governor Integration Tests** ⏳
**Blocked Until:** P0.2.1, P0.2.2, P0.2.3, P0.2.4, P0.2.5 completed
**Deliverable:** `/home/user/infrafabric/tests/integration/test_governor.py`
**Estimate:** 2h
**Model:** Sonnet

**Milestones:**
- [ ] 25% - Test scaffolding and swarm registration tests complete
- [ ] 50% - Capability matching and budget enforcement tests passing
- [ ] 75% - Circuit breaker and help request tests passing
- [ ] 100% - All tests passing, policy violations verified

**Acceptance Criteria:**
- ✅ Test: capability matching with various swarm profiles
- ✅ Test: budget enforcement and circuit breaker
- ✅ Test: help request with qualified swarms
- ✅ Test: help request with no qualified swarms (escalation)
- ✅ Test: policy violation prevention
- ✅ All tests pass consistently

**Key Tests:**
```python
- test_capability_matching()
- test_budget_enforcement()
- test_circuit_breaker_trip()
- test_gang_up_on_blocker()
- test_policy_violation_prevention()
```

---

#### **P0.3.6: IF.chassis Security Audit Tests** ⏳
**Blocked Until:** P0.3.1, P0.3.2, P0.3.3, P0.3.4, P0.3.5 completed
**Deliverable:** `/home/user/infrafabric/tests/security/test_chassis.py`
**Estimate:** 2h
**Model:** Sonnet

**Milestones:**
- [ ] 25% - Security test scaffolding and isolation tests complete
- [ ] 50% - Resource limit and credential tests passing
- [ ] 75% - Rate limiting and sandbox escape tests passing
- [ ] 100% - All security tests passing, vulnerabilities documented

**Acceptance Criteria:**
- ✅ Test: WASM cannot access filesystem
- ✅ Test: WASM cannot make network calls
- ✅ Test: Memory limit enforced (OOM killed)
- ✅ Test: CPU limit enforced (timeout)
- ✅ Test: Credential expiration prevents access
- ✅ All security tests pass (zero vulnerabilities)

**Key Tests:**
```python
- test_wasm_cannot_access_filesystem()
- test_wasm_cannot_make_network_calls()
- test_memory_limit_enforcement()
- test_cpu_limit_enforcement()
- test_credential_expiration()
- test_api_rate_limiting()
```

---

## Filler Tasks When Blocked

Work on these tasks when waiting for component implementation:

### **F4.1: Integration Test Scaffolding** 🔧
**Deliverable:** Test framework for all integration tests
**Estimate:** 2h

**Milestones:**
- [ ] 25% - Setup pytest configuration and fixtures
- [ ] 50% - Create base test classes and utilities
- [ ] 75% - Add mock implementations for dependencies
- [ ] 100% - Framework tested and documented

Pre-build test infrastructure:
- pytest configuration with async support
- Fixture factories for components
- Mock event bus implementation
- Test utilities (timing, assertions)

---

### **F4.2: Regression Test Data** 🔧
**Deliverable:** Test data for all components
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Design test data schemas
- [ ] 50% - Create coordinator test data (tasks, swarms)
- [ ] 75% - Create governor test data (capabilities, policies)
- [ ] 100% - Create chassis test data (WASM modules, contracts)

Build comprehensive test data:
- Sample tasks and swarms
- Capability profiles
- Resource policies
- WASM modules (simple, malicious)

---

### **F4.3: Mock Implementations** 🔧
**Deliverable:** Mock components for early testing
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Create mock EventBus
- [ ] 50% - Create mock IFCoordinator
- [ ] 75% - Create mock IFGovernor
- [ ] 100% - Create mock IFChassis

Build mocks for:
- EventBus (in-memory implementation)
- IFCoordinator (basic claim/broadcast)
- IFGovernor (simple matching)
- IFChassis (fake WASM execution)

---

### **F4.4: Security Requirements Review** 🔧
**Deliverable:** Security requirements documentation
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Review IF.coordinator security requirements
- [ ] 50% - Review IF.governor security requirements
- [ ] 75% - Review IF.chassis security requirements
- [ ] 100% - Document security test plan

Security review for:
- IF.coordinator: CAS race conditions, auth
- IF.governor: Budget bypass attempts, policy violations
- IF.chassis: Sandbox escapes, resource exhaustion

---

### **F4.5: Code Review Assistance** 🔧
**Deliverable:** Code reviews for other sessions
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Review Session 5 CLI code
- [ ] 50% - Review Session 7 component implementations
- [ ] 75% - Provide feedback and suggestions
- [ ] 100% - Follow up on code review issues

Provide code reviews for:
- Session 5: CLI commands and tests
- Session 7: Component implementations
- Focus on testability, error handling, edge cases

---

## Progress Reporting

Update `STATUS-SESSION-4-SIP.yaml` every 15 minutes with:

```yaml
session: session-4-sip
current_task: P0.1.5
milestone: "50% - Task lifecycle and blocker tests passing"
timestamp: 2025-11-12T14:30:00Z
branch: claude/sip-escalate-integration-*
blocked_on: P0.1.4
next_action: "Waiting for coordinator latency tests"
tests_passed: 3
tests_failed: 0
```

---

## Success Criteria

**Session 4 (SIP) is complete when:**

- ✅ **P0.1.5:** All IF.coordinator integration tests pass consistently
- ✅ **P0.2.6:** All IF.governor integration tests pass consistently
- ✅ **P0.3.6:** All IF.chassis security tests pass (zero vulnerabilities)
- ✅ No test flakes (100% reliable test suite)
- ✅ All security vulnerabilities documented and mitigated
- ✅ Test coverage >80% for all components
- ✅ At least 3 filler tasks completed while waiting for dependencies

**Quality Standards:**
- All tests are deterministic (no race conditions)
- Tests run fast (<30s total for all integration tests)
- Clear test documentation and failure messages
- Security tests cover OWASP top 10 for WASM
- Integration tests verify witness logging

**Coordination Standards:**
- STATUS file updated every 15 minutes
- Blocked status reported immediately
- Filler tasks used when blocked (no idle time)
- Test failures reported to component owners immediately

---

## Task Claiming Process

1. **Pull Latest Task Board:**
   ```bash
   git fetch origin $COORD_BRANCH
   git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md
   ```

2. **Claim Task (update STATUS):**
   ```yaml
   session: session-4-sip
   claiming: P0.1.5
   milestone: "0% - Starting task"
   timestamp: 2025-11-12T14:00:00Z
   ```

3. **Work on Task (update milestones):**
   - 25% checkpoint: Update STATUS with tests_passed count
   - 50% checkpoint: Update STATUS with tests_passed count
   - 75% checkpoint: Update STATUS with tests_passed count

4. **Complete Task:**
   ```yaml
   session: session-4-sip
   completed: P0.1.5
   milestone: "100% - Complete"
   deliverable: /home/user/infrafabric/tests/integration/test_coordinator.py
   tests_pass: true
   tests_passed: 5
   tests_failed: 0
   timestamp: 2025-11-12T16:00:00Z
   ```

5. **Immediately Claim Next Task or Filler Task**

---

## Notes

- **Model Preference:** Use Sonnet for all integration and security tests (quality critical)
- **Test Quality:** Tests must be deterministic and fast
- **Security Focus:** Zero tolerance for security vulnerabilities
- **Collaboration:** Report bugs to Sessions 5 and 7 immediately
- **Coverage:** Aim for >80% code coverage on all components

**Remember:** Your integration tests are the final quality gate before Phase 0 handoff. Make them comprehensive!
