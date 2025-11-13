# S² Single-Command Installation

Copy/paste ONE command per machine. Zero follow-up required.
**Each machine is separate - no shared filesystem.**

---

## For WORKERS (One command per worker - NO follow-up needed)

### Worker 1 - Backend (Cloud Machine 2)
```bash
cd /tmp && git clone -q https://github.com/dannystocker/mcp-multiagent-bridge.git 2>/dev/null || (cd mcp-multiagent-bridge && git pull) && cd mcp-multiagent-bridge && pip install -q mcp>=1.0.0 && mkdir -p ~/.config/claude && echo '{"mcpServers":{"bridge":{"command":"python3","args":["'$(pwd)'/claude_bridge_secure.py"]}}}' > ~/.config/claude/claude.json && cd /tmp && git clone -q https://github.com/dannystocker/infrafabric.git 2>/dev/null || (cd infrafabric && git pull) && cd infrafabric && git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null && chmod +x scripts/s2-deployment/*.sh scripts/s2-deployment/*.py 2>/dev/null && (sudo apt-get install -y jq -qq 2>/dev/null || brew install jq 2>/dev/null || true) && nohup bash -c 'WORKER_ID=1; while true; do cd /tmp/infrafabric && git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null; if [ -f credentials/s2-worker-${WORKER_ID}-credentials.json ]; then CONV_ID=$(jq -r .conversation_id credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); TOKEN=$(jq -r .worker_token credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); if [ -n "$CONV_ID" ] && [ "$CONV_ID" != "null" ] && [ -n "$TOKEN" ]; then pkill -f "keepalive-daemon.*${WORKER_ID}" 2>/dev/null; scripts/s2-deployment/keepalive-daemon.sh "$CONV_ID" "$TOKEN" & echo "[$(date)] Worker-${WORKER_ID} connected: $CONV_ID" | tee -a /tmp/s2-worker.log; break; fi; fi; echo "[$(date)] Waiting for orchestrator credentials..." >> /tmp/s2-sync.log; sleep 15; done' > /tmp/s2-sync.log 2>&1 & echo "✅ Worker-1 auto-sync started (PID: $!) - Logs: tail -f /tmp/s2-sync.log"
```

### Worker 2 - Frontend (Cloud Machine 3)
```bash
cd /tmp && git clone -q https://github.com/dannystocker/mcp-multiagent-bridge.git 2>/dev/null || (cd mcp-multiagent-bridge && git pull) && cd mcp-multiagent-bridge && pip install -q mcp>=1.0.0 && mkdir -p ~/.config/claude && echo '{"mcpServers":{"bridge":{"command":"python3","args":["'$(pwd)'/claude_bridge_secure.py"]}}}' > ~/.config/claude/claude.json && cd /tmp && git clone -q https://github.com/dannystocker/infrafabric.git 2>/dev/null || (cd infrafabric && git pull) && cd infrafabric && git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null && chmod +x scripts/s2-deployment/*.sh scripts/s2-deployment/*.py 2>/dev/null && (sudo apt-get install -y jq -qq 2>/dev/null || brew install jq 2>/dev/null || true) && nohup bash -c 'WORKER_ID=2; while true; do cd /tmp/infrafabric && git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null; if [ -f credentials/s2-worker-${WORKER_ID}-credentials.json ]; then CONV_ID=$(jq -r .conversation_id credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); TOKEN=$(jq -r .worker_token credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); if [ -n "$CONV_ID" ] && [ "$CONV_ID" != "null" ] && [ -n "$TOKEN" ]; then pkill -f "keepalive-daemon.*${WORKER_ID}" 2>/dev/null; scripts/s2-deployment/keepalive-daemon.sh "$CONV_ID" "$TOKEN" & echo "[$(date)] Worker-${WORKER_ID} connected: $CONV_ID" | tee -a /tmp/s2-worker.log; break; fi; fi; echo "[$(date)] Waiting for orchestrator credentials..." >> /tmp/s2-sync.log; sleep 15; done' > /tmp/s2-sync.log 2>&1 & echo "✅ Worker-2 auto-sync started (PID: $!) - Logs: tail -f /tmp/s2-sync.log"
```

### Worker 3 - Tests (Cloud Machine 4)
```bash
cd /tmp && git clone -q https://github.com/dannystocker/mcp-multiagent-bridge.git 2>/dev/null || (cd mcp-multiagent-bridge && git pull) && cd mcp-multiagent-bridge && pip install -q mcp>=1.0.0 && mkdir -p ~/.config/claude && echo '{"mcpServers":{"bridge":{"command":"python3","args":["'$(pwd)'/claude_bridge_secure.py"]}}}' > ~/.config/claude/claude.json && cd /tmp && git clone -q https://github.com/dannystocker/infrafabric.git 2>/dev/null || (cd infrafabric && git pull) && cd infrafabric && git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null && chmod +x scripts/s2-deployment/*.sh scripts/s2-deployment/*.py 2>/dev/null && (sudo apt-get install -y jq -qq 2>/dev/null || brew install jq 2>/dev/null || true) && nohup bash -c 'WORKER_ID=3; while true; do cd /tmp/infrafabric && git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null; if [ -f credentials/s2-worker-${WORKER_ID}-credentials.json ]; then CONV_ID=$(jq -r .conversation_id credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); TOKEN=$(jq -r .worker_token credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); if [ -n "$CONV_ID" ] && [ "$CONV_ID" != "null" ] && [ -n "$TOKEN" ]; then pkill -f "keepalive-daemon.*${WORKER_ID}" 2>/dev/null; scripts/s2-deployment/keepalive-daemon.sh "$CONV_ID" "$TOKEN" & echo "[$(date)] Worker-${WORKER_ID} connected: $CONV_ID" | tee -a /tmp/s2-worker.log; break; fi; fi; echo "[$(date)] Waiting for orchestrator credentials..." >> /tmp/s2-sync.log; sleep 15; done' > /tmp/s2-sync.log 2>&1 & echo "✅ Worker-3 auto-sync started (PID: $!) - Logs: tail -f /tmp/s2-sync.log"
```

### Worker 4 - Docs (Cloud Machine 5)
```bash
cd /tmp && git clone -q https://github.com/dannystocker/mcp-multiagent-bridge.git 2>/dev/null || (cd mcp-multiagent-bridge && git pull) && cd mcp-multiagent-bridge && pip install -q mcp>=1.0.0 && mkdir -p ~/.config/claude && echo '{"mcpServers":{"bridge":{"command":"python3","args":["'$(pwd)'/claude_bridge_secure.py"]}}}' > ~/.config/claude/claude.json && cd /tmp && git clone -q https://github.com/dannystocker/infrafabric.git 2>/dev/null || (cd infrafabric && git pull) && cd infrafabric && git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null && chmod +x scripts/s2-deployment/*.sh scripts/s2-deployment/*.py 2>/dev/null && (sudo apt-get install -y jq -qq 2>/dev/null || brew install jq 2>/dev/null || true) && nohup bash -c 'WORKER_ID=4; while true; do cd /tmp/infrafabric && git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null; if [ -f credentials/s2-worker-${WORKER_ID}-credentials.json ]; then CONV_ID=$(jq -r .conversation_id credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); TOKEN=$(jq -r .worker_token credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); if [ -n "$CONV_ID" ] && [ "$CONV_ID" != "null" ] && [ -n "$TOKEN" ]; then pkill -f "keepalive-daemon.*${WORKER_ID}" 2>/dev/null; scripts/s2-deployment/keepalive-daemon.sh "$CONV_ID" "$TOKEN" & echo "[$(date)] Worker-${WORKER_ID} connected: $CONV_ID" | tee -a /tmp/s2-worker.log; break; fi; fi; echo "[$(date)] Waiting for orchestrator credentials..." >> /tmp/s2-sync.log; sleep 15; done' > /tmp/s2-sync.log 2>&1 & echo "✅ Worker-4 auto-sync started (PID: $!) - Logs: tail -f /tmp/s2-sync.log"
```

### Worker 5 - Deploy (Cloud Machine 6)
```bash
cd /tmp && git clone -q https://github.com/dannystocker/mcp-multiagent-bridge.git 2>/dev/null || (cd mcp-multiagent-bridge && git pull) && cd mcp-multiagent-bridge && pip install -q mcp>=1.0.0 && mkdir -p ~/.config/claude && echo '{"mcpServers":{"bridge":{"command":"python3","args":["'$(pwd)'/claude_bridge_secure.py"]}}}' > ~/.config/claude/claude.json && cd /tmp && git clone -q https://github.com/dannystocker/infrafabric.git 2>/dev/null || (cd infrafabric && git pull) && cd infrafabric && git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null && chmod +x scripts/s2-deployment/*.sh scripts/s2-deployment/*.py 2>/dev/null && (sudo apt-get install -y jq -qq 2>/dev/null || brew install jq 2>/dev/null || true) && nohup bash -c 'WORKER_ID=5; while true; do cd /tmp/infrafabric && git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null; if [ -f credentials/s2-worker-${WORKER_ID}-credentials.json ]; then CONV_ID=$(jq -r .conversation_id credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); TOKEN=$(jq -r .worker_token credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); if [ -n "$CONV_ID" ] && [ "$CONV_ID" != "null" ] && [ -n "$TOKEN" ]; then pkill -f "keepalive-daemon.*${WORKER_ID}" 2>/dev/null; scripts/s2-deployment/keepalive-daemon.sh "$CONV_ID" "$TOKEN" & echo "[$(date)] Worker-${WORKER_ID} connected: $CONV_ID" | tee -a /tmp/s2-worker.log; break; fi; fi; echo "[$(date)] Waiting for orchestrator credentials..." >> /tmp/s2-sync.log; sleep 15; done' > /tmp/s2-sync.log 2>&1 & echo "✅ Worker-5 auto-sync started (PID: $!) - Logs: tail -f /tmp/s2-sync.log"
```

### Worker 6 - Review (Cloud Machine 7)
```bash
cd /tmp && git clone -q https://github.com/dannystocker/mcp-multiagent-bridge.git 2>/dev/null || (cd mcp-multiagent-bridge && git pull) && cd mcp-multiagent-bridge && pip install -q mcp>=1.0.0 && mkdir -p ~/.config/claude && echo '{"mcpServers":{"bridge":{"command":"python3","args":["'$(pwd)'/claude_bridge_secure.py"]}}}' > ~/.config/claude/claude.json && cd /tmp && git clone -q https://github.com/dannystocker/infrafabric.git 2>/dev/null || (cd infrafabric && git pull) && cd infrafabric && git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null && chmod +x scripts/s2-deployment/*.sh scripts/s2-deployment/*.py 2>/dev/null && (sudo apt-get install -y jq -qq 2>/dev/null || brew install jq 2>/dev/null || true) && nohup bash -c 'WORKER_ID=6; while true; do cd /tmp/infrafabric && git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null; if [ -f credentials/s2-worker-${WORKER_ID}-credentials.json ]; then CONV_ID=$(jq -r .conversation_id credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); TOKEN=$(jq -r .worker_token credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); if [ -n "$CONV_ID" ] && [ "$CONV_ID" != "null" ] && [ -n "$TOKEN" ]; then pkill -f "keepalive-daemon.*${WORKER_ID}" 2>/dev/null; scripts/s2-deployment/keepalive-daemon.sh "$CONV_ID" "$TOKEN" & echo "[$(date)] Worker-${WORKER_ID} connected: $CONV_ID" | tee -a /tmp/s2-worker.log; break; fi; fi; echo "[$(date)] Waiting for orchestrator credentials..." >> /tmp/s2-sync.log; sleep 15; done' > /tmp/s2-sync.log 2>&1 & echo "✅ Worker-6 auto-sync started (PID: $!) - Logs: tail -f /tmp/s2-sync.log"
```

### Worker 7 - WSL CLI (Your Local WSL)
```bash
cd /tmp && git clone -q https://github.com/dannystocker/mcp-multiagent-bridge.git 2>/dev/null || (cd mcp-multiagent-bridge && git pull) && cd mcp-multiagent-bridge && pip install -q mcp>=1.0.0 && mkdir -p ~/.config/claude && echo '{"mcpServers":{"bridge":{"command":"python3","args":["'$(pwd)'/claude_bridge_secure.py"]}}}' > ~/.config/claude/claude.json && cd /tmp && git clone -q https://github.com/dannystocker/infrafabric.git 2>/dev/null || (cd infrafabric && git pull) && cd infrafabric && git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null && chmod +x scripts/s2-deployment/*.sh scripts/s2-deployment/*.py 2>/dev/null && (sudo apt-get install -y jq -qq 2>/dev/null || brew install jq 2>/dev/null || true) && nohup bash -c 'WORKER_ID=7; while true; do cd /tmp/infrafabric && git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null; if [ -f credentials/s2-worker-${WORKER_ID}-credentials.json ]; then CONV_ID=$(jq -r .conversation_id credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); TOKEN=$(jq -r .worker_token credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); if [ -n "$CONV_ID" ] && [ "$CONV_ID" != "null" ] && [ -n "$TOKEN" ]; then pkill -f "keepalive-daemon.*${WORKER_ID}" 2>/dev/null; scripts/s2-deployment/keepalive-daemon.sh "$CONV_ID" "$TOKEN" & echo "[$(date)] Worker-${WORKER_ID} connected: $CONV_ID" | tee -a /tmp/s2-worker.log; break; fi; fi; echo "[$(date)] Waiting for orchestrator credentials..." >> /tmp/s2-sync.log; sleep 15; done' > /tmp/s2-sync.log 2>&1 & echo "✅ Worker-7 auto-sync started (PID: $!) - Logs: tail -f /tmp/s2-sync.log"
```

### Worker 8 - Cloud Codex (Cloud Machine 8)
```bash
cd /tmp && git clone -q https://github.com/dannystocker/mcp-multiagent-bridge.git 2>/dev/null || (cd mcp-multiagent-bridge && git pull) && cd mcp-multiagent-bridge && pip install -q mcp>=1.0.0 && mkdir -p ~/.config/claude && echo '{"mcpServers":{"bridge":{"command":"python3","args":["'$(pwd)'/claude_bridge_secure.py"]}}}' > ~/.config/claude/claude.json && cd /tmp && git clone -q https://github.com/dannystocker/mcp-multiagent-bridge.git 2>/dev/null || (cd infrafabric && git pull) && cd infrafabric && git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null && chmod +x scripts/s2-deployment/*.sh scripts/s2-deployment/*.py 2>/dev/null && (sudo apt-get install -y jq -qq 2>/dev/null || brew install jq 2>/dev/null || true) && nohup bash -c 'WORKER_ID=8; while true; do cd /tmp/infrafabric && git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null; if [ -f credentials/s2-worker-${WORKER_ID}-credentials.json ]; then CONV_ID=$(jq -r .conversation_id credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); TOKEN=$(jq -r .worker_token credentials/s2-worker-${WORKER_ID}-credentials.json 2>/dev/null); if [ -n "$CONV_ID" ] && [ "$CONV_ID" != "null" ] && [ -n "$TOKEN" ]; then pkill -f "keepalive-daemon.*${WORKER_ID}" 2>/dev/null; scripts/s2-deployment/keepalive-daemon.sh "$CONV_ID" "$TOKEN" & echo "[$(date)] Worker-${WORKER_ID} connected: $CONV_ID" | tee -a /tmp/s2-worker.log; break; fi; fi; echo "[$(date)] Waiting for orchestrator credentials..." >> /tmp/s2-sync.log; sleep 15; done' > /tmp/s2-sync.log 2>&1 & echo "✅ Worker-8 auto-sync started (PID: $!) - Logs: tail -f /tmp/s2-sync.log"
```

---

## What Each Command Does

1. **Clones MCP bridge** to `/tmp/mcp-multiagent-bridge`
2. **Installs MCP bridge** and configures Claude Code
3. **Clones infrafabric repo** to `/tmp/infrafabric` (separate machine!)
4. **Checks out the deployment branch**
5. **Makes scripts executable**
6. **Installs jq** (JSON parser)
7. **Starts background loop** that:
   - Polls git every 15 seconds for new credentials
   - When credentials appear, auto-starts keep-alive daemon
   - Logs connection to `/tmp/s2-worker.log`
   - Stops polling once connected

---

## Check Status

**On any worker:**
```bash
# Check if connected
tail -f /tmp/s2-worker.log

# Check sync loop
tail -f /tmp/s2-sync.log

# Check keep-alive daemon
tail -f /tmp/mcp-keepalive.log
```

---

## Summary

✅ **Each command is completely self-contained**
✅ **Each worker clones infrafabric repo independently to `/tmp/infrafabric`**
✅ **Workers auto-poll for credentials every 15 seconds**
✅ **Zero follow-up commands needed after paste**

**Key fix:** Workers now clone `infrafabric` to `/tmp/infrafabric` on their own machine, so they have independent access to scripts and credentials via git!
