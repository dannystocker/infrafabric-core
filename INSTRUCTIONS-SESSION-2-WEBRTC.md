# Instructions: Session 2 (WebRTC - Documentation & Test Support)

**Your Branch:** `claude/webrtc-agent-mesh-*`
**Coordination Branch:** `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`
**Your Role:** Documentation specialist for IF.governor and cross-session test support

---

## Polling Protocol

Run this script every 30 seconds to stay synchronized with the coordination branch:

```bash
#!/bin/bash
# Session 2 (WebRTC) - Phase 0 Coordination Polling Loop

SESSION_ID="session-2-webrtc"
MY_BRANCH=$(git branch --show-current)
COORD_BRANCH="claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"

echo "🚀 Session 2 (WebRTC): Documentation & Test Support"
echo "📍 My branch: $MY_BRANCH"
echo "📡 Polling: $COORD_BRANCH every 30 seconds"

while true; do
  # 1. Fetch latest coordination state
  git fetch origin $COORD_BRANCH --quiet 2>/dev/null

  # 2. Check task board for available tasks
  TASK_BOARD=$(git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md 2>/dev/null)

  # 3. Look for P0.5.2 (IF.governor docs) or P0.5.5 (production runbook)
  # 4. If blocked, pick filler task

  # 5. Update STATUS file
  cat > STATUS-SESSION-2-WEBRTC.yaml <<EOF
session: session-2-webrtc
status: polling
last_poll: $(date -Iseconds)
branch: $MY_BRANCH
current_task: ${CURRENT_TASK:-none}
EOF

  git add STATUS-SESSION-2-WEBRTC.yaml
  git commit -m "chore: Update session-2-webrtc status" --quiet 2>/dev/null || true
  git push origin $MY_BRANCH --quiet 2>/dev/null || true

  # 6. Wait 30 seconds before next poll
  sleep 30
done
```

---

## Your Phase 0 Tasks

### Primary Tasks (Documentation)

#### **P0.5.2: IF.governor Documentation** ⏳
**Blocked Until:** P0.2.6 (Integration tests) completed
**Deliverable:** `/home/user/infrafabric/docs/components/IF.GOVERNOR.md`
**Estimate:** 1h
**Model:** Haiku

**Milestones:**
- [ ] 25% - Architecture overview and capability registry guide started
- [ ] 50% - Policy configuration and budget management sections complete
- [ ] 75% - Circuit breaker tuning and troubleshooting added
- [ ] 100% - Example policies and complete review done

**Acceptance Criteria:**
- Architecture overview with component diagrams
- Capability registry guide (how to register swarms)
- Policy configuration (YAML format, options)
- Budget management (tracking, enforcement, reporting)
- Circuit breaker tuning (thresholds, reset procedures)
- Example policies for common scenarios

---

#### **P0.5.5: Production Runbook** ⏳
**Blocked Until:** All components complete (P0.1.5, P0.2.6, P0.3.6)
**Deliverable:** `/home/user/infrafabric/docs/PHASE-0-PRODUCTION-RUNBOOK.md`
**Estimate:** 2h
**Model:** Haiku

**Milestones:**
- [ ] 25% - Deployment procedures documented
- [ ] 50% - Monitoring setup and incident response complete
- [ ] 75% - Backup/restore and performance tuning added
- [ ] 100% - Security checklist and final review done

**Acceptance Criteria:**
- Deployment procedures (all 3 components)
- Monitoring setup (metrics, alerts, dashboards)
- Incident response procedures
- Backup/restore procedures
- Performance tuning guide
- Security checklist

---

## Filler Tasks When Blocked

Work on these tasks when waiting for dependencies to complete:

### **F2.1: Cross-Session Test Fixtures** 🔧
**Deliverable:** IFMessage mocks for all sessions
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Design IFMessage schema
- [ ] 50% - Create mocks for NDI, H.323, SIP, CLI sessions
- [ ] 75% - Add error scenarios and edge cases
- [ ] 100% - Testing and documentation

Build mock IFMessage data for:
- Task claim messages
- Task broadcast messages
- Blocker detection messages
- Help request messages
- All provider types (NDI, WebRTC, H.323, SIP)

---

### **F2.2: SDP Mock Data** 🔧
**Deliverable:** SDP mocks for integration tests
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Review SDP format requirements
- [ ] 50% - Create basic offer/answer mocks
- [ ] 75% - Add complex scenarios (multi-codec, ICE candidates)
- [ ] 100% - Validation and documentation

Create SDP mock data for:
- Basic audio/video offer
- Answer with codec negotiation
- ICE candidate gathering
- DTLS fingerprints
- Bundle/RTCP-mux scenarios

---

### **F2.3: Improve IF-IMPROVEMENTS-V1.1.md** 🔧
**Deliverable:** Updated improvements document with Phase 0 learnings
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Review current improvements document
- [ ] 50% - Document Phase 0 architectural improvements
- [ ] 75% - Add lessons learned and future recommendations
- [ ] 100% - Review and finalize

Add Phase 0 learnings:
- Real-time coordination benefits
- Capability-aware resource allocation wins
- WASM sandbox security improvements
- Performance metrics and cost savings

---

### **F2.4: Help Session 3 with H.323 Documentation** 🔧
**Deliverable:** Documentation support for Session 3
**Estimate:** 1h

**Milestones:**
- [ ] 25% - Review Session 3 documentation needs
- [ ] 50% - Provide H.323 protocol documentation
- [ ] 75% - Help with MCU configuration examples
- [ ] 100% - Review and finalize Session 3 deliverables

Support Session 3 with:
- H.323 protocol documentation
- MCU configuration examples
- Guardian council documentation
- Integration test scenarios

---

## Progress Reporting

Update `STATUS-SESSION-2-WEBRTC.yaml` every 15 minutes with:

```yaml
session: session-2-webrtc
current_task: P0.5.2
milestone: "50% - Policy configuration complete"
timestamp: 2025-11-12T14:30:00Z
branch: claude/webrtc-agent-mesh-*
blocked_on: P0.2.6
next_action: "Waiting for IF.governor integration tests"
```

---

## Success Criteria

**Session 2 (WebRTC) is complete when:**

- ✅ **P0.5.2:** IF.governor documentation is complete and reviewed
- ✅ **P0.5.5:** Production runbook is complete and covers all 3 components
- ✅ All example policies tested and verified
- ✅ Runbook procedures validated with actual deployments
- ✅ No blockers preventing Phase 0 completion
- ✅ At least 2 filler tasks completed while waiting for dependencies

**Quality Standards:**
- Documentation is operations-focused and actionable
- All procedures tested in practice
- Runbook follows incident response best practices
- Example policies cover common use cases
- Clear escalation paths defined

**Coordination Standards:**
- STATUS file updated every 15 minutes
- Blocked status reported immediately
- Filler tasks used when blocked (no idle time)
- Help offered to Session 3 when available

---

## Task Claiming Process

1. **Pull Latest Task Board:**
   ```bash
   git fetch origin $COORD_BRANCH
   git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md
   ```

2. **Claim Task (update STATUS):**
   ```yaml
   session: session-2-webrtc
   claiming: P0.5.2
   milestone: "0% - Starting task"
   timestamp: 2025-11-12T14:00:00Z
   ```

3. **Work on Task (update milestones):**
   - 25% checkpoint: Update STATUS
   - 50% checkpoint: Update STATUS
   - 75% checkpoint: Update STATUS

4. **Complete Task:**
   ```yaml
   session: session-2-webrtc
   completed: P0.5.2
   milestone: "100% - Complete"
   deliverable: /home/user/infrafabric/docs/components/IF.GOVERNOR.md
   tests_pass: true
   timestamp: 2025-11-12T15:30:00Z
   ```

5. **Immediately Claim Next Task or Filler Task**

---

## Notes

- **Model Preference:** Use Haiku for all documentation tasks (cost-effective)
- **Runbook Focus:** Production runbook should be operator-friendly
- **Policy Examples:** Include real-world scenarios (e.g., cost optimization, deadline-driven)
- **Collaboration:** Work closely with Session 3 on documentation consistency
- **Testing:** Validate all runbook procedures before marking complete

**Remember:** The production runbook is critical for Phase 0 handoff. Make it comprehensive and actionable!
