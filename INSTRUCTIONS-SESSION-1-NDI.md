# Instructions: Session 1 (NDI - Documentation & Witness)

**Your Branch:** `claude/ndi-witness-streaming-*`
**Coordination Branch:** `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`
**Your Role:** Documentation specialist and testing support for Phase 0 components

---

## Polling Protocol

Run this script every 30 seconds to stay synchronized with the coordination branch:

```bash
#!/bin/bash
# Session 1 (NDI) - Phase 0 Coordination Polling Loop

SESSION_ID="session-1-ndi"
MY_BRANCH=$(git branch --show-current)
COORD_BRANCH="claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"

echo "🚀 Session 1 (NDI): Documentation & Testing Support"
echo "📍 My branch: $MY_BRANCH"
echo "📡 Polling: $COORD_BRANCH every 30 seconds"

while true; do
  # 1. Fetch latest coordination state
  git fetch origin $COORD_BRANCH --quiet 2>/dev/null

  # 2. Check task board for available tasks
  TASK_BOARD=$(git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md 2>/dev/null)

  # 3. Look for P0.5.1 (IF.coordinator docs) or P0.5.4 (migration guide)
  # 4. If blocked, pick filler task

  # 5. Update STATUS file
  cat > STATUS-SESSION-1-NDI.yaml <<EOF
session: session-1-ndi
status: polling
last_poll: $(date -Iseconds)
branch: $MY_BRANCH
current_task: ${CURRENT_TASK:-none}
EOF

  git add STATUS-SESSION-1-NDI.yaml
  git commit -m "chore: Update session-1-ndi status" --quiet 2>/dev/null || true
  git push origin $MY_BRANCH --quiet 2>/dev/null || true

  # 6. Wait 30 seconds before next poll
  sleep 30
done
```

---

## Your Phase 0 Tasks

### Primary Tasks (Documentation)

#### **P0.5.1: IF.coordinator Documentation** ⏳
**Blocked Until:** P0.1.5 (Integration tests) completed
**Deliverable:** `/home/user/infrafabric/docs/components/IF.COORDINATOR.md`
**Estimate:** 1h
**Model:** Haiku

**Milestones:**
- [ ] 25% - Architecture overview written
- [ ] 50% - API reference and configuration guide complete
- [ ] 75% - Deployment instructions and troubleshooting added
- [ ] 100% - Example usage and complete review done

**Acceptance Criteria:**
- Architecture overview with diagrams
- Complete API reference
- Configuration guide (etcd/NATS setup)
- Deployment instructions
- Troubleshooting guide
- Example usage scenarios

---

#### **P0.5.4: Migration Guide (git→etcd)** ⏳
**Blocked Until:** P0.1.5 (Integration tests) completed
**Deliverable:** `/home/user/infrafabric/docs/MIGRATION-GIT-TO-ETCD.md`
**Estimate:** 2h
**Model:** Haiku

**Milestones:**
- [ ] 25% - Step-by-step migration process documented
- [ ] 50% - Rollback procedures and testing checklist complete
- [ ] 75% - Performance comparison data added
- [ ] 100% - Troubleshooting section and review complete

**Acceptance Criteria:**
- Step-by-step migration process
- Rollback procedures
- Testing checklist
- Performance comparison (git polling vs etcd)
- Troubleshooting common issues

---

## Filler Tasks When Blocked

Work on these tasks when waiting for dependencies to complete:

### **F1.1: Improve S² Architecture Docs** 🔧
**Deliverable:** Updates to `docs/SWARM-OF-SWARMS-ARCHITECTURE.md`
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Read current architecture docs
- [ ] 50% - Identify Phase 0 integration points
- [ ] 75% - Draft Phase 0 coordination section
- [ ] 100% - Review and finalize updates

Add Phase 0 integration notes:
- How IF.coordinator replaces git polling
- How IF.governor manages swarm resources
- How IF.chassis provides isolation

---

### **F1.2: IF.witness Hash Chain Example** 🔧
**Deliverable:** Example hash chain for coordination events
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Design example coordination events
- [ ] 50% - Create hash chain structure
- [ ] 75% - Add verification examples
- [ ] 100% - Documentation complete

Create example showing:
- Task claim event
- Task execution event
- Task completion event
- Hash chain verification

---

### **F1.3: Test Fixtures for Session 2** 🔧
**Deliverable:** IFMessage mocks for WebRTC testing
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Review WebRTC IFMessage requirements
- [ ] 50% - Create basic message mocks
- [ ] 75% - Add edge cases and error scenarios
- [ ] 100% - Testing and documentation

Build mock data for:
- SDP offer/answer messages
- ICE candidate messages
- Error scenarios
- WebRTC state transitions

---

### **F1.4: Review NOVICE-ONBOARDING.md** 🔧
**Deliverable:** Improved onboarding documentation
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Read and analyze current onboarding docs
- [ ] 50% - Identify gaps and improvement areas
- [ ] 75% - Draft improvements
- [ ] 100% - Review and finalize

Improvements:
- Add Phase 0 concepts explanation
- Simplify technical jargon
- Add more examples
- Create quick-start guide

---

## Progress Reporting

Update `STATUS-SESSION-1-NDI.yaml` every 15 minutes with:

```yaml
session: session-1-ndi
current_task: P0.5.1
milestone: "50% - API reference complete"
timestamp: 2025-11-12T14:30:00Z
branch: claude/ndi-witness-streaming-*
blocked_on: null
next_action: "Working on deployment instructions"
```

---

## Success Criteria

**Session 1 (NDI) is complete when:**

- ✅ **P0.5.1:** IF.coordinator documentation is complete and reviewed
- ✅ **P0.5.4:** Migration guide (git→etcd) is complete and reviewed
- ✅ All documentation follows consistent format and style
- ✅ All code examples tested and verified
- ✅ No blockers preventing other sessions from progress
- ✅ At least 2 filler tasks completed while waiting for dependencies

**Quality Standards:**
- Documentation is clear and beginner-friendly
- All commands and examples are tested
- Diagrams included where helpful
- Troubleshooting sections cover common issues
- Cross-references to other Phase 0 components

**Coordination Standards:**
- STATUS file updated every 15 minutes
- Blocked status reported immediately
- Filler tasks used when blocked (no idle time)
- Help offered to other sessions when available

---

## Task Claiming Process

1. **Pull Latest Task Board:**
   ```bash
   git fetch origin $COORD_BRANCH
   git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md
   ```

2. **Claim Task (update STATUS):**
   ```yaml
   session: session-1-ndi
   claiming: P0.5.1
   milestone: "0% - Starting task"
   timestamp: 2025-11-12T14:00:00Z
   ```

3. **Work on Task (update milestones):**
   - 25% checkpoint: Update STATUS
   - 50% checkpoint: Update STATUS
   - 75% checkpoint: Update STATUS

4. **Complete Task:**
   ```yaml
   session: session-1-ndi
   completed: P0.5.1
   milestone: "100% - Complete"
   deliverable: /home/user/infrafabric/docs/components/IF.COORDINATOR.md
   tests_pass: true
   timestamp: 2025-11-12T15:30:00Z
   ```

5. **Immediately Claim Next Task or Filler Task**

---

## Notes

- **Model Preference:** Use Haiku for all documentation tasks (cost-effective)
- **Documentation Style:** Follow existing docs/components/ format
- **Code Examples:** Test all code snippets before including
- **Diagrams:** Use Mermaid or ASCII art for architecture diagrams
- **Help Protocol:** Monitor Session 2 and 3 STATUS files, offer documentation help if they struggle

**Remember:** Documentation quality directly impacts Phase 0 handoff success. Make it production-ready!
