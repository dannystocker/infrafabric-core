# Instructions: Session 3 (H.323 - Documentation & MCU Support)

**Your Branch:** `claude/h323-guardian-council-*`
**Coordination Branch:** `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`
**Your Role:** Documentation specialist for IF.chassis and H.323 testing support

---

## Polling Protocol

Run this script every 30 seconds to stay synchronized with the coordination branch:

```bash
#!/bin/bash
# Session 3 (H.323) - Phase 0 Coordination Polling Loop

SESSION_ID="session-3-h323"
MY_BRANCH=$(git branch --show-current)
COORD_BRANCH="claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"

echo "🚀 Session 3 (H.323): Documentation & MCU Support"
echo "📍 My branch: $MY_BRANCH"
echo "📡 Polling: $COORD_BRANCH every 30 seconds"

while true; do
  # 1. Fetch latest coordination state
  git fetch origin $COORD_BRANCH --quiet 2>/dev/null

  # 2. Check task board for available tasks
  TASK_BOARD=$(git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md 2>/dev/null)

  # 3. Look for P0.5.3 (IF.chassis docs)
  # 4. If blocked, pick filler task

  # 5. Update STATUS file
  cat > STATUS-SESSION-3-H323.yaml <<EOF
session: session-3-h323
status: polling
last_poll: $(date -Iseconds)
branch: $MY_BRANCH
current_task: ${CURRENT_TASK:-none}
EOF

  git add STATUS-SESSION-3-H323.yaml
  git commit -m "chore: Update session-3-h323 status" --quiet 2>/dev/null || true
  git push origin $MY_BRANCH --quiet 2>/dev/null || true

  # 6. Wait 30 seconds before next poll
  sleep 30
done
```

---

## Your Phase 0 Tasks

### Primary Tasks (Documentation)

#### **P0.5.3: IF.chassis Documentation** ⏳
**Blocked Until:** P0.3.6 (Security audit tests) completed
**Deliverable:** `/home/user/infrafabric/docs/components/IF.CHASSIS.md`
**Estimate:** 1h
**Model:** Haiku

**Milestones:**
- [ ] 25% - Architecture overview and WASM compilation guide started
- [ ] 50% - Resource limits configuration and SLO definition complete
- [ ] 75% - Security best practices and troubleshooting added
- [ ] 100% - Example service contracts and complete review done

**Acceptance Criteria:**
- Architecture overview (WASM sandbox design)
- WASM compilation guide (how to build swarm modules)
- Resource limits configuration (CPU, memory, API rate limiting)
- SLO definition guide (setting performance targets)
- Security best practices (credential scoping, isolation)
- Example service contracts (capability definitions)

---

## Filler Tasks When Blocked

Work on these tasks when waiting for dependencies to complete:

### **F3.1: Improve H.323 Production Runbook** 🔧
**Deliverable:** Updated `/home/user/infrafabric/docs/H323-PRODUCTION-RUNBOOK.md`
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Review current H.323 runbook
- [ ] 50% - Add Phase 0 integration notes
- [ ] 75% - Update troubleshooting with new components
- [ ] 100% - Review and finalize updates

Improvements:
- Add IF.coordinator integration for H.323 swarms
- Update resource management with IF.governor
- Add IF.chassis security considerations
- Update monitoring and alerting

---

### **F3.2: MCU Configuration Templates** 🔧
**Deliverable:** MCU config templates for testing
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Identify common MCU configurations
- [ ] 50% - Create templates for 2-way, 4-way, 8-way conferences
- [ ] 75% - Add advanced scenarios (cascading, recording)
- [ ] 100% - Testing and documentation

Create templates for:
- Basic 2-way point-to-point
- 4-way multipoint conference
- 8-way conference with transcoding
- Cascading MCU configurations
- Recording and streaming setups

---

### **F3.3: Guardian Council Test Data** 🔧
**Deliverable:** Test scenarios for Guardian council
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Design Guardian council test scenarios
- [ ] 50% - Create test data for voting scenarios
- [ ] 75% - Add edge cases (split votes, abstentions)
- [ ] 100% - Validation and documentation

Build test data for:
- Basic voting scenarios
- Tie-breaking scenarios
- Consensus building
- Escalation paths
- Quality assessment

---

### **F3.4: Help Session 1 with NDI Documentation** 🔧
**Deliverable:** Documentation support for Session 1
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Review Session 1 documentation needs
- [ ] 50% - Provide NDI protocol documentation
- [ ] 75% - Help with witness integration examples
- [ ] 100% - Review and finalize Session 1 deliverables

Support Session 1 with:
- NDI protocol documentation
- Witness integration examples
- Stream management examples
- Migration guide assistance

---

## Progress Reporting

Update `STATUS-SESSION-3-H323.yaml` every 15 minutes with:

```yaml
session: session-3-h323
current_task: P0.5.3
milestone: "50% - Resource limits configuration complete"
timestamp: 2025-11-12T14:30:00Z
branch: claude/h323-guardian-council-*
blocked_on: P0.3.6
next_action: "Waiting for IF.chassis security audit"
```

---

## Success Criteria

**Session 3 (H.323) is complete when:**

- ✅ **P0.5.3:** IF.chassis documentation is complete and reviewed
- ✅ All WASM compilation examples tested and verified
- ✅ Security best practices validated by Session 4
- ✅ Service contract examples cover common patterns
- ✅ No blockers preventing Phase 0 completion
- ✅ At least 2 filler tasks completed while waiting for dependencies

**Quality Standards:**
- Documentation is security-focused and comprehensive
- All WASM examples compile and run
- Resource limit configurations tested
- SLO definitions follow industry best practices
- Clear security guidelines for swarm developers

**Coordination Standards:**
- STATUS file updated every 15 minutes
- Blocked status reported immediately
- Filler tasks used when blocked (no idle time)
- Help offered to Session 1 when available

---

## Task Claiming Process

1. **Pull Latest Task Board:**
   ```bash
   git fetch origin $COORD_BRANCH
   git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md
   ```

2. **Claim Task (update STATUS):**
   ```yaml
   session: session-3-h323
   claiming: P0.5.3
   milestone: "0% - Starting task"
   timestamp: 2025-11-12T14:00:00Z
   ```

3. **Work on Task (update milestones):**
   - 25% checkpoint: Update STATUS
   - 50% checkpoint: Update STATUS
   - 75% checkpoint: Update STATUS

4. **Complete Task:**
   ```yaml
   session: session-3-h323
   completed: P0.5.3
   milestone: "100% - Complete"
   deliverable: /home/user/infrafabric/docs/components/IF.CHASSIS.md
   tests_pass: true
   timestamp: 2025-11-12T15:30:00Z
   ```

5. **Immediately Claim Next Task or Filler Task**

---

## Notes

- **Model Preference:** Use Haiku for all documentation tasks (cost-effective)
- **Security Focus:** IF.chassis docs should emphasize security isolation
- **WASM Expertise:** Include practical WASM compilation guidance
- **Collaboration:** Work with Session 4 on security validation
- **Testing:** All code examples must compile and run successfully

**Remember:** IF.chassis security is critical for production safety. Document all security boundaries clearly!
