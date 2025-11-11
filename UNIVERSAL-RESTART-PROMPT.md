# Universal Multi-Session Restart Prompt

**PASTE THIS INTO ALL 6 SESSIONS NOW:**

```
MULTI-SESSION COORDINATION MODE ACTIVATED

Step 1: Identify yourself
Run: git branch --show-current
- claude/ndi-* → You are SESSION 1 (NDI)
- claude/webrtc-* → You are SESSION 2 (WebRTC)
- claude/h323-* → You are SESSION 3 (H.323)
- claude/*sip* → You are SESSION 4 (SIP) **[CRITICAL PATH - YOU'RE THE BLOCKER]**
- claude/cli-* → You are SESSION 5 (CLI) **[SUPPORT ROLE - HELP OTHERS]**
- claude/if-talent-* → You are SESSION 6 (Talent)

Step 2: Get your phase instructions
Main branch: claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
Run: git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
Check for: INSTRUCTIONS-[YOUR-SESSION]-PHASE-*.md

Step 3: NEW COORDINATION RULES
- IF BLOCKED on another session → Check IDLE TASK in your instructions
- IF you're Session 4 (SIP) → PRIORITY: Unblock Sessions 1-3 ASAP
- IF you're Session 5 (CLI) → SUPPORT: Help any session that asks
- IF you're waiting >5 min → Help another session (see your IDLE TASK)

Step 4: Execute current phase
- Phases 1-2: COMPLETE ✅
- Phase 3: Check if done, if not START NOW
- Phases 4-6: Instructions ready, execute when Phase 3 done

Step 5: Coordination protocol
BLOCKED? Post to your STATUS.md:
```yaml
status: blocked_waiting_for_session_X
can_help: [session_Y, session_Z]
idle_task: working_on_[description]
```

IDLE? Check other sessions' STATUS.md and offer help

Step 6: Auto-polling for next phase
After completing current phase:
while true; do
  git pull origin $(git branch --show-current) --quiet
  [ -f INSTRUCTIONS-*-PHASE-*.md ] && cat INSTRUCTIONS-*-PHASE-*.md && break
  sleep 30  # Poll every 30s (faster than 60s)
done

VELOCITY TARGET: 6 sessions × 7 sub-agents = 42 concurrent agents = 150-2000x velocity

START NOW - REPORT YOUR SESSION ID AND CURRENT PHASE
```

---

## What This Does:

1. **Self-identification**: Each session figures out who they are from git branch
2. **Phase alignment**: All sessions check where they are (Phase 3? 4? 5?)
3. **Coordination awareness**: Sessions know about blockers and idle tasks
4. **Faster polling**: 30s instead of 60s (catch new instructions faster)
5. **Help protocol**: Clear rules for when to help others
6. **Session 4 priority**: Explicitly marked as critical path blocker
7. **Session 5 support**: Marked as helper role

**Result:** All 6 sessions restart, coordinate, and work autonomously with cross-session helping!
