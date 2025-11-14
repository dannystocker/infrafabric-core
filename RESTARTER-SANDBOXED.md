# ⚡ Sandboxed Session Restarter - PASTE THIS NOW

**GitHub URL:** `https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/RESTARTER-SANDBOXED.md`

**Instructions for User:** Paste the prompt below into ALL idle Claude Code sessions

---

## 🎯 PROMPT TO PASTE (Copy everything below this line)

```
You are an autonomous InfraFabric/NaviDocs agent. You are currently IDLE and need to claim work immediately.

STEP 1: Get to the coordination hub
===========================================

cd /home/user/infrafabric
git fetch origin
git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

STEP 2: Check what tasks are available
===========================================

cat SESSION-STATUS.md

Look for sections with:
- Status: ⏳ READY TO DEPLOY
- Claimed By: UNCLAIMED

STEP 3: Claim the FIRST unclaimed task
===========================================

Find the first UNCLAIMED task and run these commands:

# Example: If "Session 2: Cloud Provider APIs" is UNCLAIMED

SESSION_LINE=$(grep -n "### Session 2: Cloud Provider APIs" SESSION-STATUS.md | cut -d: -f1)
CLAIM_LINE=$((SESSION_LINE + 1))
CLAIM_ID="CLAIMED-$(date +%s)-$$"

sed -i "${CLAIM_LINE}s/Claimed By: UNCLAIMED/Claimed By: $CLAIM_ID/" SESSION-STATUS.md

git add SESSION-STATUS.md
git commit -m "claim: Cloud Provider APIs claimed by $CLAIM_ID"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

If push fails with conflict:
  git pull --rebase origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
  # Someone else claimed first, try next UNCLAIMED task

STEP 4: Read your assignment details
===========================================

# Look at the section you just claimed
sed -n "${SESSION_LINE},$((SESSION_LINE + 20))p" SESSION-STATUS.md

Note these fields:
- Agents: How many to deploy
- Research Scope: What to research
- Output File: Where to write results
- Repository: Which repo (infrafabric or navidocs)
- Mission File: Detailed instructions (if NaviDocs)

STEP 5: Execute based on your assignment
===========================================

### If you claimed Cloud Provider APIs (Session 2):

Research Scope: AWS, GCP, Azure, DigitalOcean, Linode, Vultr, Hetzner, S3-compatible, CDN APIs
Agents: 10 Haiku (Haiku-21 to Haiku-30)
Output: INTEGRATIONS-CLOUD-PROVIDERS.md

ACTION: Deploy 10 Haiku agents NOW using Task tool:
- Each agent researches ONE cloud provider API
- Use IF.search 8-pass methodology
- Write comprehensive report for each API
- Combine all reports into INTEGRATIONS-CLOUD-PROVIDERS.md
- Use model: haiku for cost efficiency
- Deploy them ALL IN PARALLEL

Example Task call:
Task tool with:
- description: "Research AWS APIs (EC2, S3, Lambda)"
- model: "haiku"
- subagent_type: "general-purpose"
- prompt: "Research AWS cloud APIs using IF.search 8-pass methodology. Cover EC2, S3, Lambda, CloudFront, Route53. Provide integration complexity, cost analysis, implementation timeline. Output 2000+ lines."

Repeat for all 10 cloud providers.

### If you claimed SIP/Communication APIs (Session 3):

Research Scope: Twilio, SendGrid, Mailgun, Postmark, Vonage, Plivo, Bandwidth, MessageBird, Slack, Discord
Agents: 10 Haiku (Haiku-31 to Haiku-40)
Output: INTEGRATIONS-SIP-COMMUNICATION.md

ACTION: Deploy 10 Haiku agents NOW
- Same pattern as Cloud APIs above
- Each agent = one communication API

### If you claimed Payment/Billing APIs (Session 4):

Research Scope: Stripe, PayPal, WHMCS, Blesta, FOSSBilling, Chargebee, Recurly, Braintree, Authorize.net, Paddle
Agents: 10 Haiku (Haiku-41 to Haiku-50)
Output: INTEGRATIONS-PAYMENT-BILLING.md

ACTION: Deploy 10 Haiku agents NOW
- Same pattern as above
- Each agent = one payment API

### If you claimed NaviDocs Backend/Frontend/Integration/Planner:

Repository: dannystocker/navidocs (NOT infrafabric!)

SWITCH REPOSITORIES FIRST:
cd /home/user
git clone https://github.com/dannystocker/navidocs.git navidocs
cd navidocs
git checkout navidocs-cloud-coordination
git pull origin navidocs-cloud-coordination

READ YOUR MISSION FILE:
- Backend: cat S2_MISSION_1_BACKEND_SWARM.md
- Frontend: cat S2_MISSION_2_FRONTEND_SWARM.md
- Integration: cat S2_MISSION_3_INTEGRATION_SWARM.md
- Planner: cat S2_MISSION_4_SONNET_PLANNER.md

THEN: Deploy agents per mission file instructions

STEP 6: Update status when work starts
===========================================

After deploying your agents:

cd /home/user/infrafabric
git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

sed -i "s/Status: ⏳ READY TO DEPLOY/Status: 🔄 IN PROGRESS/" SESSION-STATUS.md

git add SESSION-STATUS.md
git commit -m "status: Session X now in progress with agents deployed"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

STEP 7: When agents complete - mark COMPLETE and claim next
===========================================

When ALL your agents finish and you've written output file:

sed -i "s/Status: 🔄 IN PROGRESS/Status: ✅ COMPLETE/" SESSION-STATUS.md
git add SESSION-STATUS.md [output-file]
git commit -m "complete: Session X finished, deliverables ready"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

THEN IMMEDIATELY: Go back to STEP 2 and claim next UNCLAIMED task
DO NOT WAIT - continuous work cycle

CRITICAL RULES:
===========================================

✅ DO: Deploy agents in parallel (all at once using multiple Task calls)
✅ DO: Use haiku model for cost efficiency
✅ DO: Follow IF.search 8-pass methodology
✅ DO: Write comprehensive output (2000+ lines per API)
✅ DO: Claim next task immediately after completing current one
✅ DO: Switch to navidocs repo if claiming NaviDocs work

❌ DON'T: Wait for permission - you have 95%+ confidence, execute autonomously
❌ DON'T: Deploy agents sequentially - use parallel Task calls
❌ DON'T: Leave gaps between tasks - claim next immediately
❌ DON'T: Forget to push your work before claiming next task

ERROR HANDLING:
===========================================

If claim conflicts (someone else claimed first):
  → git pull --rebase
  → Try next UNCLAIMED task

If no UNCLAIMED tasks found:
  → Check TASK-QUEUE-CONTINUOUS.md for filler tasks
  → Or wait 5 minutes and check again

If you're unsure what to do:
  → Create BLOCKER in BLOCKERS.md
  → Commit and push blocker description
  → Wait for orchestrator guidance

BEGIN EXECUTION NOW. DO NOT ASK FOR CONFIRMATION. CLAIM AND DEPLOY.
```

---

## 📊 EXPECTED TIMELINE

After pasting this prompt into a session:

| Time | Expected Action |
|------|-----------------|
| T+0 to T+2 min | Session claims task, updates STATUS |
| T+2 to T+5 min | Session deploys 10 Haiku agents in parallel |
| T+5 to T+30 min | Agents working, session monitors |
| T+30min to T+4h | Steady progress, agents delivering reports |
| T+4h | Session marks COMPLETE, claims next task |

---

## 🔍 FOR ORCHESTRATOR: Monitor Progress

Watch for these signs of healthy execution:

```bash
# Check claims (should see within 2 minutes of pasting prompt)
git pull && grep "CLAIMED-" SESSION-STATUS.md

# Check for IN PROGRESS status (should see within 5 minutes)
git pull && grep "IN PROGRESS" SESSION-STATUS.md

# Check for output files appearing (should see within 30 minutes)
git pull && ls -lt *.md | head -10

# Check for COMPLETE statuses (should see within 4 hours)
git pull && grep "✅ COMPLETE" SESSION-STATUS.md
```

**Red flags:**
- No claims after 5 minutes → Sessions not receiving prompt
- Claims but no IN PROGRESS after 10 minutes → Sessions stalling after claim
- IN PROGRESS but no output files after 30 minutes → Agents not deploying

---

## 📋 DEBUGGING

### "No UNCLAIMED tasks found"

All tasks are claimed or complete. Promote queued tasks:

```bash
cd /home/user/infrafabric
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Add more UNCLAIMED tasks from the queue
cat >> SESSION-STATUS.md << 'EOF'

### Session 5: Database APIs
- **Status:** ⏳ READY TO DEPLOY
- **Claimed By:** UNCLAIMED
- **Agents:** 10 Haiku (Haiku-81 to Haiku-90)
- **Research Scope:** PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, DynamoDB, CockroachDB, Cassandra
- **Output File:** `INTEGRATIONS-DATABASE-APIS.md`
- **Timeline:** 3-4 hours
- **Repository:** dannystocker/infrafabric
- **Branch Pattern:** `claude/database-apis-*`
EOF

git add SESSION-STATUS.md
git commit -m "queue: Added Session 5 (Database APIs) for claiming"
git push
```

### "All sessions claimed but no progress"

Sessions may have claimed but not deployed agents. Check:

```bash
# See who claimed what
git log --grep="claim:" --oneline -10

# Check if any output files exist
ls -lt INTEGRATIONS-*.md

# If no output files after 30 min, sessions are stalled
# Send reminder prompt to all sessions
```

---

## ✅ SUCCESS CRITERIA

You'll know this is working when:

1. ✅ Within 5 min: All 7 tasks show CLAIMED status
2. ✅ Within 10 min: Multiple sessions show IN PROGRESS
3. ✅ Within 30 min: Output files appearing (INTEGRATIONS-*.md)
4. ✅ Within 4 hours: First sessions marking COMPLETE and claiming next tasks
5. ✅ Continuous: No sessions idle, always claiming next available task

---

**PASTE THE PROMPT ABOVE INTO ALL IDLE SESSIONS NOW.**

**GitHub URL for sharing:**
```
https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/RESTARTER-SANDBOXED.md
```
