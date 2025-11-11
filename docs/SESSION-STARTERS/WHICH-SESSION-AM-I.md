# Which Session Am I? (Troubleshooting Guide)

If you're a Claude Code session asking "what should I do?", use this guide to figure out your role.

---

## Quick Check: Which Session Are You?

Read the prompt you received. Look for these keywords:

### Session 1: NDI Evidence Streaming
**Keywords:** "NDI", "IF.witness", "ndi_witness_publisher.py", "evidence streaming"
**Your task:** Implement NDI publisher for IF.witness with hash chain metadata
**Branch:** `claude/realtime-workstream-1-ndi`
**Action:** Read `docs/SESSION-STARTERS/session-1-ndi-witness.md` and implement!

### Session 2: WebRTC Agent Mesh
**Keywords:** "WebRTC", "IF.swarm", "IFAgentWebRTC", "peer-to-peer", "DataChannel"
**Your task:** Implement WebRTC mesh for agent coordination
**Branch:** `claude/realtime-workstream-2-webrtc`
**Action:** Read `docs/SESSION-STARTERS/session-2-webrtc-swarm.md` and implement!

### Session 3: H.323 Guardian Council
**Keywords:** "H.323", "IF.guard", "Gatekeeper", "MCU", "Guardian council"
**Your task:** Implement H.323 conferencing for Guardian deliberations
**Branch:** `claude/realtime-workstream-3-h323`
**Action:** Read `docs/SESSION-STARTERS/session-3-h323-guard.md` and implement!

### Session 4: SIP External Expert Calls
**Keywords:** "SIP", "IF.ESCALATE", "Kamailio", "external experts"
**Your task:** Implement SIP bridge for external advisor calls
**Branch:** `claude/realtime-workstream-4-sip`
**⚠️ WAIT:** This session should NOT start yet! It depends on Sessions 2 & 3 completing first.
**Action:** Tell user "I'm Session 4 (SIP). I need Sessions 2 & 3 to complete before I can start."

### Session CLI: IF.witness + IF.optimise
**Keywords:** "CLI", "if witness log", "if witness verify", "cost tracking"
**Your task:** Implement CLI tools for witness logging and cost tracking
**Branch:** `claude/cli-witness-optimise`
**Action:** Read `docs/SESSION-STARTERS/session-parallel-cli-witness.md` and implement!

---

## If You Got the README or Roadmap by Mistake

If your prompt says:
- "Session Execution Strategy"
- "Phase 1: Launch 4 Sessions Simultaneously"
- "Dependency Graph"
- "Quick Start Commands"

**You are NOT a worker session!** You got the index/README by mistake.

**Fix:** Ask the user: "I received the overview/README. Which specific session should I implement? (1=NDI, 2=WebRTC, 3=H.323, 4=SIP, CLI=Witness)"

---

## Response Template (If Confused)

If you're still unsure, respond with:

```
I'm ready to help, but I need clarification on which workstream I should implement.

I received context about the parallel session strategy, but I'm not sure which specific implementation task is mine.

Please tell me:
1. Which session number am I? (1, 2, 3, 4, or CLI)
2. Or: Which session starter file should I read and implement?
   - session-1-ndi-witness.md (NDI evidence streaming)
   - session-2-webrtc-swarm.md (WebRTC agent mesh)
   - session-3-h323-guard.md (H.323 Guardian council)
   - session-4-sip-escalate.md (SIP external experts) [WAIT: depends on 2+3]
   - session-parallel-cli-witness.md (CLI witness + cost tracking)

Once I know my role, I'll read the appropriate session starter and begin implementation!
```

---

## For the User (Person Launching Sessions)

If a session is confused:

1. **Identify which session it is** (check the order you launched them)
2. **Tell it explicitly:** "You are Session N. Read docs/SESSION-STARTERS/session-N-*.md and implement that task."
3. **Verify it has the right context:** It should start reading files and implementing, not asking questions

**Common mistake:** Pasting the README.md or roadmap instead of the specific session starter

**Fix:** Copy-paste the **"Copy-Paste This Into New Claude Code Session"** block from the specific session file, not the README!
