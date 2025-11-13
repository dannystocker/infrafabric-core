# S² Multi-Machine Deployment Scripts

**Architecture:** 9 agents on **separate machines** (no shared file access)
**Coordination:** Git repo + MCP Bridge

---

## Critical Architecture Notes

### Machine Topology
1. **Orchestrator** - Cloud Machine 1 (this session)
2. **Worker-1 (Backend)** - Cloud Machine 2
3. **Worker-2 (Frontend)** - Cloud Machine 3
4. **Worker-3 (Tests)** - Cloud Machine 4
5. **Worker-4 (Docs)** - Cloud Machine 5
6. **Worker-5 (Deploy)** - Cloud Machine 6
7. **Worker-6 (Review)** - Cloud Machine 7
8. **Worker-7 (WSL CLI)** - Your local WSL
9. **Worker-8 (Cloud Codex)** - Cloud Machine 8

### No Shared Filesystem
- ❌ Machines **DO NOT** share `/tmp` or any local directories
- ✅ Machines **DO** share access to `dannystocker/infrafabric` git repo
- ✅ All scripts must be committed to git and pulled by each machine
- ✅ All credentials distributed via git commits

---

## Installation Instructions

### Step 1: Install on ALL 9 Machines

**On each machine (orchestrator + 8 workers), run:**

```bash
# 1. Clone or pull latest from git
cd /home/user/infrafabric
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# 2. Install MCP bridge (single command)
curl -fsSL https://raw.githubusercontent.com/dannystocker/mcp-multiagent-bridge/main/scripts/install.sh 2>/dev/null | bash || { cd /tmp && git clone https://github.com/dannystocker/mcp-multiagent-bridge.git && cd mcp-multiagent-bridge && pip install -q mcp>=1.0.0 && mkdir -p ~/.config/claude && echo "{\"mcpServers\":{\"bridge\":{\"command\":\"python3\",\"args\":[\"$(pwd)/claude_bridge_secure.py\"]}}}" > ~/.config/claude/claude.json && echo "✅ MCP Bridge installed at: $(pwd)" && echo "📝 Config: ~/.config/claude/claude.json" && echo "🔄 Restart Claude Code to load MCP server"; }

# 3. Make deployment scripts executable
chmod +x scripts/s2-deployment/*.sh
chmod +x scripts/s2-deployment/*.py

# 4. Verify installation
python3 /tmp/mcp-multiagent-bridge/test_security.py
```

**Expected output:**
```
✅ MCP Bridge installed at: /tmp/mcp-multiagent-bridge
📝 Config: ~/.config/claude/claude.json
🔄 Restart Claude Code to load MCP server
✅ All security tests pass
```

---

### Step 2: Orchestrator Creates Conversations

**On Orchestrator Machine (Cloud Machine 1), paste into Claude session:**

```
I need to create 8 conversations for S² coordination using the MCP bridge.

For each worker (1-8):
  1. Use the MCP tool: create_conversation
     - my_role: "s2-orchestrator"
     - partner_role: "worker-{1-8}-{role}"

  2. After creating each conversation, save the credentials to:
     credentials/s2-worker-{1-8}-credentials.json

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

Worker roles:
- worker-1-backend
- worker-2-frontend
- worker-3-tests
- worker-4-docs
- worker-5-deploy
- worker-6-review
- worker-7-wsl-cli
- worker-8-cloud-codex
```

**After conversations created:**

```bash
# Commit credentials to git so all machines can access
cd /home/user/infrafabric
git add credentials/s2-worker-*.json
git commit -m "chore(s2): Add MCP bridge credentials for 8 workers"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
```

---

### Step 3: Workers Pull Credentials and Start Keep-Alive

**On each worker machine (2-8), run:**

```bash
# Pull latest credentials from git
cd /home/user/infrafabric
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Determine worker ID based on machine
# (You'll need to set this manually based on which machine this is)
export WORKER_ID=1  # Change to 1, 2, 3, 4, 5, 6, 7, or 8

# Extract credentials
CONV_ID=$(jq -r '.conversation_id' credentials/s2-worker-${WORKER_ID}-credentials.json)
WORKER_TOKEN=$(jq -r '.worker_token' credentials/s2-worker-${WORKER_ID}-credentials.json)

# Start keep-alive daemon
scripts/s2-deployment/keepalive-daemon.sh "$CONV_ID" "$WORKER_TOKEN" &

echo "✅ Worker-$WORKER_ID keep-alive daemon started"
echo "📋 Conversation ID: $CONV_ID"
```

---

### Step 4: Orchestrator Starts Watchdog

**On Orchestrator Machine (Cloud Machine 1), run:**

```bash
cd /home/user/infrafabric
scripts/s2-deployment/watchdog-monitor.sh &

echo "🐕 External watchdog started"
tail -f /tmp/mcp-watchdog.log
```

---

## Script Reference

### For All Machines

- **`install-mcp-bridge.sh`** - Single-command installer (automated in Step 1)
- **`check-messages.py`** - Check for new messages from MCP bridge

### For Worker Machines (2-8)

- **`keepalive-daemon.sh`** - Background polling to prevent idle sessions
- **`keepalive-client.py`** - Python client for heartbeat updates
- **`credential-sync-daemon.sh`** - Auto-pull credentials from git every 60s
- **`fs-watcher.sh`** - Filesystem watcher for push notifications (optional)

### For Orchestrator Machine (1)

- **`watchdog-monitor.sh`** - Monitor all workers for heartbeat freshness
- **`reassign-tasks.py`** - Reassign tasks from silent workers

---

## Troubleshooting

### Issue: "Credentials file not found"

**Cause:** Worker machine hasn't pulled latest from git

**Solution:**
```bash
cd /home/user/infrafabric
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
ls credentials/s2-worker-*.json  # Verify files exist
```

### Issue: "Keep-alive daemon not starting"

**Cause:** Scripts not executable or credentials malformed

**Solution:**
```bash
chmod +x scripts/s2-deployment/*.sh
chmod +x scripts/s2-deployment/*.py

# Verify credentials valid JSON
jq '.' credentials/s2-worker-1-credentials.json
```

### Issue: "Workers not seeing messages"

**Cause:** Keep-alive daemon not polling, or conversation expired

**Solution:**
```bash
# Check if daemon is running
ps aux | grep keepalive-daemon

# Check daemon logs
tail -f /tmp/mcp-keepalive.log

# Restart daemon
pkill -f keepalive-daemon
scripts/s2-deployment/keepalive-daemon.sh "$CONV_ID" "$WORKER_TOKEN" &
```

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                Git Repo (Shared Access)                  │
│           dannystocker/infrafabric                       │
│                                                          │
│  • Scripts in scripts/s2-deployment/                     │
│  • Credentials in credentials/                           │
│  • All machines pull from this repo                      │
└──────────────────┬───────────────────────────────────────┘
                   │
       ┌───────────┴───────────┬───────────┬───────────┐
       │                       │           │           │
┌──────▼──────┐  ┌─────▼──────┐  ┌───▼───┐  ┌───▼──────┐
│ Cloud       │  │ Cloud      │  │ Cloud │  │ Cloud    │
│ Machine 1   │  │ Machine 2  │  │ Mach 3│  │ Mach 4   │
│             │  │            │  │       │  │          │
│Orchestrator │  │ Worker-1   │  │Worker2│  │ Worker-3 │
│             │  │ (Backend)  │  │(Front)│  │ (Tests)  │
└─────────────┘  └────────────┘  └───────┘  └──────────┘

       │                       │           │           │
       └───────────┬───────────┴───────────┴───────────┘
                   │
       ┌───────────┴───────────┬───────────┬───────────┐
       │                       │           │           │
┌──────▼──────┐  ┌─────▼──────┐  ┌───▼───┐  ┌───▼──────┐
│ Cloud       │  │ Cloud      │  │ Cloud │  │ Your WSL │
│ Machine 5   │  │ Machine 6  │  │ Mach 7│  │ (Local)  │
│             │  │            │  │       │  │          │
│ Worker-4    │  │ Worker-5   │  │Worker6│  │ Worker-7 │
│ (Docs)      │  │ (Deploy)   │  │(Review)│ │(CLI Dev) │
└─────────────┘  └────────────┘  └───────┘  └──────────┘

                                  ┌──────────┐
                                  │ Cloud    │
                                  │Machine 8 │
                                  │          │
                                  │ Worker-8 │
                                  │ (Codex)  │
                                  └──────────┘
```

**Key Points:**
- Each machine pulls scripts from git independently
- Credentials distributed via git commits
- Keep-alive daemons run locally on each worker machine
- External watchdog runs on orchestrator machine
- No shared filesystem required

---

**Version:** 1.0
**Last Updated:** 2025-11-13
**Test Protocol:** See `/home/user/infrafabric/docs/S2-MCP-BRIDGE-TEST-PROTOCOL-V2.md`
