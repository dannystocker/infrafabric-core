# S² MCP Bridge Quick Start

**Single command to copy/paste into each agent (all 9 sessions)**

---

## Single-Command Installer

### For Linux/WSL/Mac (All Agents):

```bash
curl -fsSL https://raw.githubusercontent.com/dannystocker/mcp-multiagent-bridge/main/scripts/install.sh 2>/dev/null | bash || { cd /tmp && git clone https://github.com/dannystocker/mcp-multiagent-bridge.git && cd mcp-multiagent-bridge && pip install -q mcp>=1.0.0 && mkdir -p ~/.config/claude && echo "{\"mcpServers\":{\"bridge\":{\"command\":\"python3\",\"args\":[\"$(pwd)/claude_bridge_secure.py\"]}}}" > ~/.config/claude/claude.json && echo "✅ MCP Bridge installed at: $(pwd)" && echo "📝 Config: ~/.config/claude/claude.json" && echo "🔄 Restart Claude Code to load MCP server"; }
```

**What this does:**
1. Tries official installer script (if available)
2. Falls back to manual installation
3. Clones bridge to `/tmp/mcp-multiagent-bridge`
4. Installs Python MCP library
5. Creates Claude config at `~/.config/claude/claude.json`
6. Prints success message

**Expected output:**
```
✅ MCP Bridge installed at: /tmp/mcp-multiagent-bridge
📝 Config: ~/.config/claude/claude.json
🔄 Restart Claude Code to load MCP server
```

---

## Agent Deployment Map

| Agent | Type | Location | Role | ID |
|-------|------|----------|------|-----|
| **This session** | Orchestrator | Cloud | Coordinator | `s2-orchestrator` |
| **Cloud Session 1** | Worker | Cloud Machine 1 | Backend Dev | `worker-1-backend` |
| **Cloud Session 2** | Worker | Cloud Machine 2 | Frontend Dev | `worker-2-frontend` |
| **Cloud Session 3** | Worker | Cloud Machine 3 | Testing | `worker-3-tests` |
| **Cloud Session 4** | Worker | Cloud Machine 4 | Documentation | `worker-4-docs` |
| **Cloud Session 5** | Worker | Cloud Machine 5 | Deployment | `worker-5-deploy` |
| **Cloud Session 6** | Worker | Cloud Machine 6 | Review | `worker-6-review` |
| **WSL Claude CLI** | Worker | Your WSL | Local Development | `worker-7-wsl-cli` |
| **WSL Codex** | Worker | Your WSL | Code Generation | `worker-8-wsl-codex` |

---

## Step-by-Step Setup

### Step 1: Install on All Agents (5 minutes)

**Copy this into each of the 9 sessions:**
```bash
# Paste the single-command installer above into each terminal
```

**Verify installation:**
```bash
python3 /tmp/mcp-multiagent-bridge/test_security.py
```

Expected: All tests pass ✅

---

### Step 2: Orchestrator Creates Conversations (2 minutes)

**In THIS session (orchestrator), paste:**

```
I need to create 8 conversations for S² coordination using the MCP bridge.

For each worker (1-8):
  1. Use the MCP tool: create_conversation
     - my_role: "s2-orchestrator"
     - partner_role: "worker-{1-8}-{role}"

  2. After creating each conversation, save the credentials to:
     /tmp/s2-worker-{1-8}-credentials.json

     Format:
     {
       "conversation_id": "conv_...",
       "worker_id": "{1-8}",
       "worker_role": "{role}",
       "coordinator_token": "token_...",
       "worker_token": "token_...",
       "created_at": "timestamp",
       "expires_at": "timestamp"
     }

  3. Display a summary table when complete:
     | Worker | Conversation ID | Role | Status |
     |--------|----------------|------|--------|
     | 1 | conv_... | backend | ✅ Created |
     ...

Worker roles:
- worker-1-backend
- worker-2-frontend
- worker-3-tests
- worker-4-docs
- worker-5-deploy
- worker-6-review
- worker-7-wsl-cli
- worker-8-wsl-codex
```

---

### Step 3: Distribute Credentials to Workers (1 minute)

**Option A: Git commit (TTT compliant)**
```bash
cd /home/user/infrafabric
git add /tmp/s2-worker-*.json
git commit -m "chore(s2): Add MCP bridge credentials for 8 workers"
git push
```

Then each worker pulls and reads their credentials file.

**Option B: Direct paste (faster for testing)**

For each worker session, paste this:

**Worker 1 (Backend):**
```
My MCP bridge credentials are:
conversation_id: [from /tmp/s2-worker-1-credentials.json]
worker_token: [from file]

I'll use these to join the S² coordination conversation.
```

(Repeat for workers 2-8 with their respective credentials)

---

### Step 4: Workers Join and Send Acknowledgment (1 minute)

**Each worker session paste:**
```
I'm joining the S² coordination as worker-{1-8}-{role}.

1. Use MCP tool: check_messages
   (This authenticates me using my worker token)

2. If I see a task assignment, use MCP tool: send_to_partner
   - message: "Worker {1-8} ({role}): Joined and ready"
   - action_type: "status_update"

3. Report: "✅ Joined conversation [conv_id]"
```

---

### Step 5: Orchestrator Monitors (Continuous)

**In orchestrator session, paste:**
```
Monitor all 8 worker conversations:

Every 30 seconds for next 5 minutes:
  For each conversation (1-8):
    Use MCP tool: check_messages

    Log any new messages to a table:
    | Time | Worker | Message | Type |
    |------|--------|---------|------|
    | HH:MM:SS | 1 | "Joined and ready" | status_update |
    ...

  After 5 minutes, show summary:
  - Workers online: X/8
  - Messages received: count
  - Average response time: seconds
```

---

## Quick Communication Test

### Orchestrator → Workers (Broadcast Task)

**Orchestrator paste:**
```
Send test task to all workers:

For each worker (1-8):
  Use MCP tool: send_to_partner
  - message: {
      "type": "test_task",
      "task_id": "s2-comms-test",
      "description": "Reply with 'ACK from worker-{1-8}'",
      "priority": "P2"
    }
  - action_type: "task_assignment"

Then monitor responses for 2 minutes.
```

### Workers → Orchestrator (Acknowledge)

**Each worker paste:**
```
Use MCP tool: check_messages

If I see task_id "s2-comms-test":
  Use MCP tool: send_to_partner
  - message: "ACK from worker-{1-8}-{role}"
  - action_type: "acknowledgment"

Report: "✅ Test task acknowledged"
```

---

## Expected Results

### Installation Phase
- ✅ 9 agents installed bridge
- ✅ All security tests pass
- ✅ Config files created

### Conversation Phase
- ✅ 8 conversations created
- ✅ Credentials saved and distributed
- ✅ Git commit with TTT audit trail

### Communication Phase
- ✅ All 8 workers join
- ✅ Orchestrator receives 8 "ready" messages
- ✅ Test task: 8/8 acknowledgments

### Performance Metrics
- Latency: <5ms average
- Reliability: 100% delivery
- Concurrency: 9 agents, zero conflicts

---

## Troubleshooting

### Issue: "MCP tool not available"

**Solution:**
```bash
# Verify bridge is running
ps aux | grep claude_bridge_secure.py

# Check config
cat ~/.config/claude/claude.json

# Restart Claude Code to reload MCP server
```

### Issue: "Authentication failed"

**Solution:**
```bash
# Check token in credentials file
cat /tmp/s2-worker-{1-8}-credentials.json

# Verify conversation hasn't expired (3-hour TTL)
# Create new conversation if needed
```

### Issue: "Rate limit exceeded"

**Solution:**
```bash
# Edit rate limiter settings
cd /tmp/mcp-multiagent-bridge
# Increase limits in rate_limiter.py:
# "minute": (100, timedelta(minutes=1))  # Increased from 10 to 100
```

### Issue: "Worker not responding"

**Solution:**
```bash
# Check if worker session is polling
# Worker must actively use check_messages() every 10-30 seconds

# The bridge is PULL-based, not PUSH
# Workers won't see messages unless they poll
```

---

## CLI Management Commands

### View All Conversations
```bash
python3 /tmp/mcp-multiagent-bridge/bridge_cli.py list
```

### View Specific Conversation
```bash
python3 /tmp/mcp-multiagent-bridge/bridge_cli.py show conv_abc123
```

### View Audit Log
```bash
python3 /tmp/mcp-multiagent-bridge/bridge_cli.py audit conv_abc123
```

### Inspect Database
```bash
sqlite3 /tmp/claude_bridge_*.db "SELECT * FROM messages ORDER BY created_at;"
```

---

## Next Steps After Setup

1. **Run Test Protocol:** See `S2-MCP-BRIDGE-TEST-PROTOCOL.md`
2. **Production Deployment:** Increase rate limits, set up monitoring
3. **Guardian Integration:** Use YOLO mode for approval workflows
4. **Scaling Test:** Try 16+ agents to find limits

---

**Quick Start Version:** 1.0
**Last Updated:** 2025-11-13
**Full Test Protocol:** `/home/user/infrafabric/docs/S2-MCP-BRIDGE-TEST-PROTOCOL.md`
