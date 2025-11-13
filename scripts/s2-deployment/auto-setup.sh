#!/bin/bash
# S² Universal Auto-Setup Script
# Single command to paste in ANY session (orchestrator or worker)
# Auto-detects role and handles everything

set -e

echo "🚀 S² MCP Bridge Universal Setup Starting..."

# Step 1: Install MCP Bridge
echo "📦 Installing MCP Bridge..."
cd /tmp
if [ ! -d "mcp-multiagent-bridge" ]; then
  git clone -q https://github.com/dannystocker/mcp-multiagent-bridge.git
fi
cd mcp-multiagent-bridge
pip install -q mcp>=1.0.0
mkdir -p ~/.config/claude
echo "{\"mcpServers\":{\"bridge\":{\"command\":\"python3\",\"args\":[\"$(pwd)/claude_bridge_secure.py\"]}}}" > ~/.config/claude/claude.json
echo "✅ MCP Bridge installed"

# Step 2: Pull deployment scripts
echo "📥 Pulling deployment scripts from git..."
cd /home/user/infrafabric
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null || true
git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null || git checkout -b claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null || true
chmod +x scripts/s2-deployment/*.sh scripts/s2-deployment/*.py 2>/dev/null || true
echo "✅ Deployment scripts ready"

# Step 3: Detect role (orchestrator or worker)
echo ""
echo "❓ Is this the ORCHESTRATOR session? (y/n)"
read -r IS_ORCHESTRATOR

if [[ "$IS_ORCHESTRATOR" =~ ^[Yy]$ ]]; then
  echo ""
  echo "🎯 ORCHESTRATOR MODE"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "📋 NEXT STEPS (paste into this Claude session):"
  echo ""
  cat << 'EOF'
Create 8 conversations using MCP bridge and save credentials:

For workers 1-8, use create_conversation tool with:
- my_role: "s2-orchestrator"
- partner_role: "worker-{n}-{role}"

Roles: backend, frontend, tests, docs, deploy, review, wsl-cli, cloud-codex

Save each to: credentials/s2-worker-{n}-credentials.json

Then run:
cd /home/user/infrafabric
git add credentials/s2-worker-*.json
git commit -m "chore(s2): Add worker credentials"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
scripts/s2-deployment/watchdog-monitor.sh &
echo "✅ Orchestrator ready - workers can now join"
EOF
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

else
  echo ""
  echo "👷 WORKER MODE"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "What is your worker ID? (1-8)"
  read -r WORKER_ID

  if [[ ! "$WORKER_ID" =~ ^[1-8]$ ]]; then
    echo "❌ Invalid worker ID. Must be 1-8"
    exit 1
  fi

  echo "🔄 Worker-$WORKER_ID starting auto-sync..."
  echo ""

  # Install jq if needed
  if ! command -v jq &> /dev/null; then
    echo "📦 Installing jq..."
    sudo apt-get update -qq && sudo apt-get install -y jq -qq
  fi

  # Background credential sync loop
  (
    while true; do
      cd /home/user/infrafabric
      git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy 2>/dev/null || true

      CRED_FILE="credentials/s2-worker-${WORKER_ID}-credentials.json"

      if [ -f "$CRED_FILE" ]; then
        CONV_ID=$(jq -r '.conversation_id' "$CRED_FILE" 2>/dev/null || echo "")
        WORKER_TOKEN=$(jq -r '.worker_token' "$CRED_FILE" 2>/dev/null || echo "")

        if [ -n "$CONV_ID" ] && [ -n "$WORKER_TOKEN" ] && [ "$CONV_ID" != "null" ]; then
          # Kill old daemon if running
          pkill -f "keepalive-daemon.sh.*$WORKER_ID" 2>/dev/null || true

          # Start keep-alive daemon
          scripts/s2-deployment/keepalive-daemon.sh "$CONV_ID" "$WORKER_TOKEN" &

          echo "✅ Worker-$WORKER_ID connected!"
          echo "📋 Conversation: $CONV_ID"
          echo "📝 Logs: tail -f /tmp/mcp-keepalive.log"
          echo ""
          echo "🎉 Setup complete! This worker will now stay synced automatically."
          break
        fi
      fi

      echo "⏳ Waiting for credentials from orchestrator... (retry in 10s)"
      sleep 10
    done
  ) &

  echo "🔄 Background sync started (PID: $!)"
  echo "💡 This will auto-connect when orchestrator creates credentials"
fi

echo ""
echo "✅ S² Setup Complete!"
