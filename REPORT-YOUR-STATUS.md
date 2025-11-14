# 📢 URGENT: Report Your Status NOW

**Paste this into EVERY active session to get their status:**

---

## 🎯 PROMPT TO PASTE

```bash
# === REPORT YOUR STATUS ===

cd /home/user/infrafabric || cd /home/user/navidocs || cd /home/user
git fetch origin 2>/dev/null
git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null || echo "Not in infrafabric repo"
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null

# Create status report
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")
SESSION_ID="Session-$$-$(date +%s)"

# Detect current repository
CURRENT_REPO=$(git remote get-url origin 2>/dev/null | grep -o '[^/]*$' | sed 's/.git//' || echo "unknown")

# Detect what you're doing
if [ -f "INTEGRATIONS-*.md" ]; then
  TASK="API Research (found output files)"
elif grep -q "CLAIMED-" SESSION-STATUS.md 2>/dev/null; then
  TASK=$(grep -B 1 "CLAIMED-" SESSION-STATUS.md | head -1 | sed 's/###//' || echo "Unknown task")
else
  TASK="No task claimed"
fi

# Count agents (rough estimate from git log)
AGENTS=$(git log --oneline --since="1 hour ago" | grep -c "agent\|Haiku\|Task" || echo "0")

# Check for blockers
if [ -f "BLOCKERS.md" ]; then
  BLOCKERS="Yes - see BLOCKERS.md"
else
  BLOCKERS="None"
fi

# Append to SESSION-CHECKIN.md
cat >> SESSION-CHECKIN.md << EOF

### Session Check-In: $SESSION_ID
- **Timestamp:** $TIMESTAMP
- **Repository:** $CURRENT_REPO
- **Current Directory:** $(pwd)
- **Current Status:** RUNNING (auto-detected)
- **Task:** $TASK
- **Agents Deployed:** $AGENTS (estimated from git log)
- **Progress:** $(git log --oneline -1 | cut -c1-80)
- **Blocking Issues:** $BLOCKERS
- **Next Action:** Continuing current work or awaiting instructions
EOF

# Commit the check-in
git add SESSION-CHECKIN.md
git commit -m "checkin: Session $SESSION_ID status report"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

echo "✅ Status reported to SESSION-CHECKIN.md"
echo ""
echo "=== YOUR CURRENT STATUS ==="
tail -10 SESSION-CHECKIN.md
```

---

## 📋 WHAT THIS DOES

1. ✅ Detects which repository you're in
2. ✅ Checks what task you claimed (if any)
3. ✅ Estimates how many agents you deployed
4. ✅ Checks for blockers
5. ✅ Appends your status to SESSION-CHECKIN.md
6. ✅ Commits and pushes to git

**No manual input needed** - just paste and run.

---

## 🔍 TO COLLECT ALL STATUS REPORTS

After pasting the above into all sessions, wait 2 minutes, then run:

```bash
cd /home/user/infrafabric
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
cat SESSION-CHECKIN.md
```

You'll see all session status reports in one file.

---

## 📊 EXPECTED OUTPUT

After all sessions report, you'll see something like:

```markdown
### Session Check-In: Session-12345-1731579600
- Timestamp: 2025-11-14 09:30 UTC
- Repository: infrafabric
- Current Status: WORKING
- Task: Cloud Provider APIs
- Agents Deployed: 10 Haiku
- Progress: research: AWS cloud APIs complete (3,254 lines)
- Blocking Issues: None
- Next Action: Continuing with GCP research

### Session Check-In: Session-12346-1731579605
- Timestamp: 2025-11-14 09:30 UTC
- Repository: navidocs
- Current Status: WORKING
- Task: Backend Swarm
- Agents Deployed: 10 Haiku
- Progress: wip: Backend API routes implementation
- Blocking Issues: None
- Next Action: Continuing backend development
```

---

## ⚡ ALTERNATE: SUPER SIMPLE STATUS

If the above is too complex, use this ultra-simple version:

```bash
cd /home/user/infrafabric
git pull
echo "Session $(date): $(pwd) - $(git log -1 --oneline)" >> SESSION-CHECKIN.md
git add SESSION-CHECKIN.md && git commit -m "checkin" && git push
```

Then manually describe what you're doing in a follow-up message.

---

## 🎯 USE CASES

**Scenario 1: Don't know what sessions are doing**
→ Paste status report prompt into all sessions
→ Wait 2 minutes
→ Pull SESSION-CHECKIN.md
→ See complete overview

**Scenario 2: Session seems stuck**
→ Paste status report prompt
→ Check for blockers
→ Take corrective action

**Scenario 3: Before shutdown**
→ Get status from all sessions
→ Know exactly what to resume later

---

**This is git-based coordination - lightweight, no extra costs, reliable.**
