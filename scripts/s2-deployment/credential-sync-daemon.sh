#!/bin/bash
# Automated credential sync daemon for S² workers
# Pulls latest credentials from git every 60 seconds
#
# Usage: ./credential-sync-daemon.sh <worker_id>

WORKER_ID="${1:-}"
GIT_REPO="/home/user/infrafabric"
BRANCH="claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"
SYNC_INTERVAL=60
LOG_FILE="/tmp/s2-credential-sync.log"

if [ -z "$WORKER_ID" ]; then
  echo "Usage: $0 <worker_id>"
  echo "Example: $0 1  (for worker-1)"
  exit 1
fi

echo "🔄 Starting S² credential sync daemon for Worker-$WORKER_ID" | tee -a "$LOG_FILE"
echo "📂 Git repo: $GIT_REPO" | tee -a "$LOG_FILE"
echo "🌿 Branch: $BRANCH" | tee -a "$LOG_FILE"

# Find keepalive daemon script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEEPALIVE_SCRIPT="$SCRIPT_DIR/keepalive-daemon.sh"

while true; do
  cd "$GIT_REPO" || exit 1

  # Fetch latest from remote
  git fetch origin "$BRANCH" >> "$LOG_FILE" 2>&1

  # Check if new credentials available
  LOCAL_HASH=$(git rev-parse HEAD)
  REMOTE_HASH=$(git rev-parse origin/"$BRANCH" 2>/dev/null || echo "$LOCAL_HASH")

  if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] 📥 New credentials detected, pulling..." | tee -a "$LOG_FILE"

    git pull origin "$BRANCH" >> "$LOG_FILE" 2>&1

    # Load my credentials
    CRED_FILE="$GIT_REPO/credentials/s2-worker-${WORKER_ID}-credentials.json"

    if [ -f "$CRED_FILE" ]; then
      echo "[$TIMESTAMP] ✅ Credentials loaded from: $CRED_FILE" | tee -a "$LOG_FILE"

      # Extract conversation_id and token (requires jq)
      if command -v jq &> /dev/null; then
        CONV_ID=$(jq -r '.conversation_id' "$CRED_FILE")
        WORKER_TOKEN=$(jq -r '.worker_token' "$CRED_FILE")

        echo "[$TIMESTAMP] 🔑 Conversation ID: $CONV_ID" | tee -a "$LOG_FILE"

        # Start keep-alive daemon with new credentials
        pkill -f keepalive-daemon  # Stop old daemon
        "$KEEPALIVE_SCRIPT" "$CONV_ID" "$WORKER_TOKEN" &

        echo "[$TIMESTAMP] 🚀 Keep-alive daemon started with new credentials" | tee -a "$LOG_FILE"
      else
        echo "[$TIMESTAMP] ⚠️  jq not installed, cannot parse credentials" | tee -a "$LOG_FILE"
        echo "[$TIMESTAMP] 💡 Install jq: sudo apt-get install -y jq" | tee -a "$LOG_FILE"
      fi
    else
      echo "[$TIMESTAMP] ⚠️  Credentials file not found: $CRED_FILE" | tee -a "$LOG_FILE"
    fi
  fi

  sleep $SYNC_INTERVAL
done
