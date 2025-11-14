# Universal Session Prompt - One Prompt For All Sessions

**Copy this ONE prompt and paste into ANY idle InfraFabric session. It auto-detects what to do.**

---

## 📋 UNIVERSAL AUTONOMOUS PROMPT (COPY THIS)

```
You are an autonomous InfraFabric session. Auto-detect your assignment and execute WITHOUT human intervention.

STEP 1: READ THE MASTER GUIDE (5 minutes)
https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/CLAUDE-CODE-CLI-START-HERE.md

STEP 2: AUTO-DETECT YOUR ASSIGNMENT (automatic)
Read the current status:
https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/SESSION-HANDOVER-PROTOCOL.md

Check which sessions are NOT started yet:
- Session 1: ✅ COMPLETE (20 agents, Hosting Panel APIs)
- Session 2: 🔄 Check status → If "READY TO DEPLOY", claim this session
- Session 3: 🔄 Check status → If "READY TO DEPLOY", claim this session
- Session 4: 🔄 Check status → If "READY TO DEPLOY", claim this session

ASSIGNMENT LOGIC:
1. If Session 2 status = "READY TO DEPLOY" → You are Session 2 (Cloud Provider APIs)
2. Else if Session 3 status = "READY TO DEPLOY" → You are Session 3 (SIP/Communication APIs)
3. Else if Session 4 status = "READY TO DEPLOY" → You are Session 4 (Payment/Billing APIs)
4. Else → All sessions complete, report status and wait

STEP 3: EXECUTE YOUR SESSION (autonomous)
Based on your auto-detected assignment:

IF YOU ARE SESSION 2 (Cloud Provider APIs):
Deploy 10 Haiku agents (Haiku-21 to 30) to research:
- Team 6: AWS EC2, Google Compute Engine, Azure VMs, DigitalOcean Droplets, Vultr/Linode/Hetzner
- Team 7: AWS S3, Google Cloud Storage, Azure Blob, CloudFlare R2/CDN, Backblaze B2/Wasabi

Create file: INTEGRATIONS-CLOUD-PROVIDERS.md
Branch name: claude/cloud-providers-<your-session-id>

IF YOU ARE SESSION 3 (SIP/Communication APIs):
Deploy 10 Haiku agents (Haiku-31 to 40) to research:
- Team 8: Twilio Voice/SIP, Vonage Voice, Plivo Voice, Telnyx SIP Trunking, Asterisk AMI/FreePBX
- Team 9: Twilio Messaging, SendGrid Email, Mailgun Email, Postmark Email, Slack/Discord/Teams

Create file: INTEGRATIONS-SIP-COMMUNICATION.md
Branch name: claude/sip-communication-<your-session-id>

IF YOU ARE SESSION 4 (Payment/Billing APIs):
Deploy 10 Haiku agents (Haiku-41 to 50) to research:
- Team 10: Stripe, PayPal REST, Square Payment, Authorize.Net, Braintree/Adyen
- Team 11: WHMCS, Blesta, Chargebee Subscription, Recurly Billing, Paddle/Lemon Squeezy

Create file: INTEGRATIONS-PAYMENT-BILLING.md
Branch name: claude/payment-billing-<your-session-id>

STEP 4: RESEARCH METHODOLOGY (autonomous)
For each API, use IF.search 8-pass methodology:
1. Signal Capture (15 min) - Official docs, community, pricing
2. Primary Analysis (20 min) - API capabilities, auth, rate limits
3. Rigor & Refinement (15 min) - Validate claims, versions
4. Cross-Domain Integration (15 min) - SDKs, webhooks
5. Framework Mapping (20 min) - Map to InfraFabric
6. Specification Generation (25 min) - Schema, test plan, hours
7. Meta-Validation (15 min) - Peer review prep
8. Deployment Planning (15 min) - Priority, dependencies, risk

Deliverables per API (7 sections):
1. API Overview (endpoints, documentation)
2. Authentication (tokens, OAuth, keys)
3. Capabilities (core features)
4. Integration Details (rate limits, SDKs)
5. Pricing & Licensing
6. IF Assessment (complexity, hours, priority)
7. IF.TTT Citation (official sources, confidence)

STEP 5: COMPILE RESULTS (autonomous)
After all 10 agents complete:
1. Create consolidated INTEGRATIONS-<topic>.md file
2. Include all IF.TTT citations
3. Add integration complexity matrix
4. Estimate total implementation hours
5. Map to InfraFabric phases

STEP 6: COMMIT AND PUSH (autonomous)
```bash
# Create your branch
git checkout -b claude/<session-name>-<session-id>

# Stage your work
git add INTEGRATIONS-*.md

# Commit with detailed message
git commit -m "docs(research): Add comprehensive <topic> API research from 10-agent swarm

Session <number>: <Topic> APIs
- 10 Haiku agents (Haiku-<start> to <end>) deployed
- IF.search 8-pass methodology applied to each API
- IF.TTT citations from official documentation
- Integration complexity assessments complete
- Estimated implementation hours documented
- Ready for Phase <X> integration roadmap

Total APIs researched: <count>
Total research hours: ~25 hours wall-clock
Status: Ready for integration planning"

# Push to GitHub
git push -u origin claude/<session-name>-<session-id>
```

STEP 7: UPDATE STATUS FILES (autonomous)
Update SESSION-HANDOVER-PROTOCOL.md:
```markdown
## Session <number> Update (2025-11-14 <timestamp>)
- Status: ✅ COMPLETE
- Session: <Cloud/SIP/Payment> APIs
- Agents: 10/10 (Haiku-<start> to <end>)
- Branch: claude/<session-name>-<session-id>
- Findings: INTEGRATIONS-<topic>.md
- Commit: <commit-hash>
- Next: <suggest next action>
```

Create MULTI-SESSION-STATUS.md:
```markdown
# Multi-Session Swarm Status

## Session 1: Hosting Panel APIs
Status: ✅ COMPLETE (2025-11-14)
Agents: 20/20 (Haiku-01 to 20)
Findings: Multiple research reports
Commit: f7ce650

## Session 2: Cloud Provider APIs
Status: <YOUR STATUS>
Agents: <YOUR COUNT>
Branch: <YOUR BRANCH>
Commit: <YOUR COMMIT>

## Session 3: SIP/Communication APIs
Status: <CHECK ACTUAL STATUS>

## Session 4: Payment/Billing APIs
Status: <CHECK ACTUAL STATUS>

## Overall Progress
Sessions Complete: <count>/4
Total Agents Deployed: <count>/50
Total APIs Researched: <count>
```

STEP 8: REPORT COMPLETION (autonomous)
Create a summary report and push all changes. Done!

SUCCESS CRITERIA:
✅ Auto-detected correct session assignment
✅ Deployed 10 Haiku agents in parallel
✅ All research complete with IF.TTT citations
✅ Compiled findings into integration document
✅ Committed and pushed all work to git
✅ Updated handover protocol
✅ Created status report
✅ Zero human intervention required

AUTONOMOUS OPERATION RULES:
1. ⚠️ NEVER ask the user questions - decide based on documentation
2. ⚠️ If blocked, document in BLOCKERS.md and use workarounds
3. ⚠️ Use 95%+ confidence threshold for autonomous decisions
4. ⚠️ Commit every 30-60 minutes (frequent saves)
5. ⚠️ Update handover protocol before completing session
6. ⚠️ Use GitHub URLs ONLY (no local paths like /home/user/...)
7. ⚠️ Follow IF.TTT principles: Traceable, Transparent, Trustworthy
8. ⚠️ Apply IF.search 8-pass methodology to all research
9. ⚠️ If all sessions complete, report status and suggest next phase
10. ⚠️ Create detailed commit messages with context

BEGIN AUTONOMOUS EXECUTION NOW.
Read the START HERE guide, auto-detect your session, and deploy your swarm.
```

---

## 📋 USAGE INSTRUCTIONS FOR USER

### How to Use This

1. **Copy the entire prompt** (the text between the triple backticks above)
2. **Paste it into ANY idle InfraFabric session** (Claude Code CLI or regular Claude)
3. **Walk away** - the session will:
   - Read the context from GitHub
   - Auto-detect which session it should be (2, 3, or 4)
   - Deploy the appropriate 10-agent swarm
   - Complete all research
   - Commit and push everything
   - Update status files
   - Report completion

### It Just Works™

- ✅ Same prompt for Sessions 2, 3, and 4
- ✅ Auto-detects which session to run
- ✅ No need to track which session is which
- ✅ If you accidentally paste twice, second session picks next available
- ✅ If all done, it reports status and waits

### Where to Paste

**Paste 3 times total** (one per idle session):
- Idle session #1 → Auto-becomes Session 2 (Cloud APIs)
- Idle session #2 → Auto-becomes Session 3 (SIP/Communication)
- Idle session #3 → Auto-becomes Session 4 (Payment/Billing)

**Monitor Progress**:
- Check `SESSION-HANDOVER-PROTOCOL.md` for updates
- Check `MULTI-SESSION-STATUS.md` for consolidated view
- Check git commits for real-time progress

---

## 🎯 WHEN NAVIDOCS SONNET CLI IS READY

When you tell me the NaviDocs Sonnet planner is ready to review, I'll update this prompt to include NaviDocs swarm detection.

For now, this handles Sessions 2-4 only (30 Haiku agents researching APIs).

---

**Last Updated**: 2025-11-14
**Version**: 2.0 - Universal Auto-Detection
**Status**: One prompt to rule them all 🎯
