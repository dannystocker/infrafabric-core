# Instructions: Session 6 (Talent - Reserved / Standby)

**Your Branch:** `claude/talent-*`
**Coordination Branch:** `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`
**Your Role:** Standby support - Not actively used in Phase 0

---

## Phase 0 Status

**Session 6 (Talent) is NOT actively used in Phase 0.**

Phase 0 focuses on fixing 3 critical production bugs (IF.coordinator, IF.governor, IF.chassis) using Sessions 1, 2, 3, 4, 5, and 7.

Session 6 is reserved for future phases (Phases 1-6) where provider integrations will be implemented.

---

## Polling Protocol

**You do not need to run a polling loop for Phase 0.**

However, if you want to monitor progress, you can check the coordination branch:

```bash
#!/bin/bash
# Session 6 (Talent) - Phase 0 Monitoring (STANDBY MODE)

COORD_BRANCH="claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"

echo "📡 Session 6 (Talent): STANDBY MODE - Not active in Phase 0"
echo "🔍 Monitoring coordination branch for awareness only"

# Pull latest coordination state
git fetch origin $COORD_BRANCH --quiet 2>/dev/null
git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md

echo ""
echo "Phase 0 Sessions Active: 1-NDI, 2-WebRTC, 3-H.323, 4-SIP, 5-CLI, 7-IF.bus"
echo "Session 6 (Talent) will be activated in Phases 1-6 for provider integrations"
```

---

## Your Phase 0 Tasks

**None assigned for Phase 0.**

Session 6 will be used in future phases for:
- **Phase 1:** NDI provider integration
- **Phase 2:** WebRTC provider integration
- **Phase 3:** H.323 provider integration
- **Phase 4:** SIP provider integration
- **Phase 5:** Video matrix routing
- **Phase 6:** End-to-end testing

---

## What You Can Do During Phase 0

While not assigned active tasks, you can:

1. **Monitor Progress:** Watch other sessions' STATUS files
2. **Prepare for Phase 1:** Study NDI provider integration requirements
3. **Learn Architecture:** Review Phase 0 component designs
4. **Offer Help:** If other sessions struggle, offer assistance
5. **Documentation:** Improve general architecture documentation

---

## Filler Tasks (Optional)

If you want to contribute during Phase 0:

### **Read Phase 0 Documentation**
- Study `PHASE-0-COORDINATION-MATRIX.md`
- Study `PHASE-0-TASK-BOARD.md`
- Review component architecture

### **Prepare for Phase 1**
- Read NDI integration requirements
- Review existing NDI code (`providers/ndi/`)
- Study IF.coordinator API for task claiming

### **Help Other Sessions**
- Monitor STATUS files for "help_wanted: true"
- Offer code review support
- Assist with testing

### **Improve Documentation**
- Review `SWARM-OF-SWARMS-ARCHITECTURE.md`
- Improve `NOVICE-ONBOARDING.md`
- Create Phase 1 preparation guide

---

## Progress Reporting

**Not required for Phase 0.**

If you choose to monitor or help, you can optionally create:

```yaml
# STATUS-SESSION-6-TALENT.yaml
session: session-6-talent
status: standby
phase: phase-0
assigned_tasks: none
monitoring: true
timestamp: 2025-11-12T14:30:00Z
notes: "Standby mode - Preparing for Phase 1 NDI integration"
```

---

## Success Criteria

**Session 6 (Talent) Phase 0 is complete when:**

- ✅ Phase 0 completes successfully (no action required from Session 6)
- ✅ Ready to begin Phase 1 NDI integration
- ✅ Familiar with Phase 0 component architecture
- ✅ (Optional) Contributed to documentation or helped other sessions

---

## Activation for Phase 1

Session 6 will be activated when:
1. Phase 0 is complete (all 3 bugs fixed)
2. `INTEGRATION-ROADMAP-POST-GPT5-REVIEW.md` updated to mark Phase 0 complete
3. Phase 1 (NDI integration) begins

At that point, you'll receive:
- **New INSTRUCTIONS file:** `INSTRUCTIONS-SESSION-6-PHASE-1.md`
- **New task board:** `PHASE-1-TASK-BOARD.md`
- **Active task assignments:** NDI witness implementation, stream management, etc.

---

## Notes

- **Phase 0 Timeline:** 6-8 hours wall-clock
- **Phase 0 Cost:** $360-450
- **Phase 0 Sessions:** 1, 2, 3, 4, 5, 7 (NOT Session 6)
- **Your Next Phase:** Phase 1 NDI integration

**Enjoy the break! You'll be busy in Phase 1-6!** 🎉

---

## Contact Points

If you notice any issues during Phase 0 monitoring:

- **Critical bugs:** Alert coordination branch immediately
- **Session stuck:** Offer help via STATUS file
- **Documentation issues:** Create filler task to fix

**Standby mode doesn't mean idle - stay aware and ready to jump in if needed!**
