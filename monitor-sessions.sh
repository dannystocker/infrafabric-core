#!/bin/bash
# Session Progress Monitor - Updates every 60 seconds

COORD_BRANCH="claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   📊 InfraFabric S² Session Monitor - Starting..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

while true; do
    clear
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   📊 InfraFabric S² Session Monitor"
    echo "   ⏰ $(date '+%Y-%m-%d %H:%M:%S')"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Fetch latest from all branches
    echo "🔄 Fetching latest updates..."
    git fetch --all --quiet 2>/dev/null || echo "⚠️  Git fetch failed"
    echo ""

    # Check each session branch for STATUS files
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "SESSION STATUS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Session 1 - NDI
    SESSION_1_BRANCH=$(git branch -r | grep "ndi-witness-streaming" | head -1 | xargs)
    if [ -n "$SESSION_1_BRANCH" ]; then
        STATUS_1=$(git show $SESSION_1_BRANCH:STATUS-SESSION-1.yaml 2>/dev/null || echo "status: not_started")
        echo "📌 Session 1 (NDI): $(echo "$STATUS_1" | grep "status:" | head -1)"
        CURRENT_1=$(echo "$STATUS_1" | grep "current_task:" | head -1)
        if [ -n "$CURRENT_1" ]; then
            echo "   └─ $CURRENT_1"
        fi
    else
        echo "📌 Session 1 (NDI): ⏸️  Not started yet"
    fi
    echo ""

    # Session 2 - WebRTC
    SESSION_2_BRANCH=$(git branch -r | grep "webrtc-agent-mesh" | head -1 | xargs)
    if [ -n "$SESSION_2_BRANCH" ]; then
        STATUS_2=$(git show $SESSION_2_BRANCH:STATUS-SESSION-2.yaml 2>/dev/null || echo "status: not_started")
        echo "📌 Session 2 (WebRTC): $(echo "$STATUS_2" | grep "status:" | head -1)"
        CURRENT_2=$(echo "$STATUS_2" | grep "current_task:" | head -1)
        if [ -n "$CURRENT_2" ]; then
            echo "   └─ $CURRENT_2"
        fi
    else
        echo "📌 Session 2 (WebRTC): ⏸️  Not started yet"
    fi
    echo ""

    # Session 3 - H.323
    SESSION_3_BRANCH=$(git branch -r | grep "h323-guardian-council" | head -1 | xargs)
    if [ -n "$SESSION_3_BRANCH" ]; then
        STATUS_3=$(git show $SESSION_3_BRANCH:STATUS-SESSION-3.yaml 2>/dev/null || echo "status: not_started")
        echo "📌 Session 3 (H.323): $(echo "$STATUS_3" | grep "status:" | head -1)"
        CURRENT_3=$(echo "$STATUS_3" | grep "current_task:" | head -1)
        if [ -n "$CURRENT_3" ]; then
            echo "   └─ $CURRENT_3"
        fi
    else
        echo "📌 Session 3 (H.323): ⏸️  Not started yet"
    fi
    echo ""

    # Session 4 - SIP
    SESSION_4_BRANCH=$(git branch -r | grep "sip-escalate-integration" | head -1 | xargs)
    if [ -n "$SESSION_4_BRANCH" ]; then
        STATUS_4=$(git show $SESSION_4_BRANCH:STATUS-SESSION-4.yaml 2>/dev/null || echo "status: not_started")
        echo "📌 Session 4 (SIP): $(echo "$STATUS_4" | grep "status:" | head -1)"
        CURRENT_4=$(echo "$STATUS_4" | grep "current_task:" | head -1)
        if [ -n "$CURRENT_4" ]; then
            echo "   └─ $CURRENT_4"
        fi
    else
        echo "📌 Session 4 (SIP): ⏸️  Not started yet"
    fi
    echo ""

    # Session 5 - CLI (CRITICAL)
    SESSION_5_BRANCH=$(git branch -r | grep "cli-witness-optimise" | head -1 | xargs)
    if [ -n "$SESSION_5_BRANCH" ]; then
        STATUS_5=$(git show $SESSION_5_BRANCH:STATUS-SESSION-5.yaml 2>/dev/null || echo "status: not_started")
        echo "📌 Session 5 (CLI) ⚡ CRITICAL: $(echo "$STATUS_5" | grep "status:" | head -1)"
        CURRENT_5=$(echo "$STATUS_5" | grep "current_task:" | head -1)
        if [ -n "$CURRENT_5" ]; then
            echo "   └─ $CURRENT_5"
        fi
        # Check if P0.1.1 is complete (unblocks Session 7)
        if echo "$STATUS_5" | grep -q "completed.*P0.1.1"; then
            echo "   ✅ P0.1.1 COMPLETE - Session 7 unblocked!"
        fi
    else
        echo "📌 Session 5 (CLI) ⚡ CRITICAL: ⏸️  Not started yet - BLOCKING SESSION 7!"
    fi
    echo ""

    # Session 7 - IF.bus
    SESSION_7_BRANCH=$(git branch -r | grep "if-bus-sip-adapters" | head -1 | xargs)
    if [ -n "$SESSION_7_BRANCH" ]; then
        STATUS_7=$(git show $SESSION_7_BRANCH:STATUS-SESSION-7.yaml 2>/dev/null || echo "status: not_started")
        echo "📌 Session 7 (IF.bus): $(echo "$STATUS_7" | grep "status:" | head -1)"
        CURRENT_7=$(echo "$STATUS_7" | grep "current_task:" | head -1)
        if [ -n "$CURRENT_7" ]; then
            echo "   └─ $CURRENT_7"
        fi
        # Check if blocked on P0.1.1
        if echo "$STATUS_7" | grep -q "blocked.*P0.1.1"; then
            echo "   ⏸️  Waiting for Session 5 to complete P0.1.1"
        fi
    else
        echo "📌 Session 7 (IF.bus): ⏸️  Not started yet"
    fi
    echo ""

    # Check coordination branch for task board updates
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TASK BOARD STATUS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    TASK_BOARD=$(git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md 2>/dev/null)

    AVAILABLE=$(echo "$TASK_BOARD" | grep -c "🔵 AVAILABLE" || echo "0")
    CLAIMED=$(echo "$TASK_BOARD" | grep -c "🟡 CLAIMED" || echo "0")
    COMPLETED=$(echo "$TASK_BOARD" | grep -c "🟢 COMPLETED" || echo "0")
    BLOCKED=$(echo "$TASK_BOARD" | grep -c "🔴 BLOCKED" || echo "0")

    echo "🔵 Available:  $AVAILABLE tasks"
    echo "🟡 Claimed:    $CLAIMED tasks"
    echo "🟢 Completed:  $COMPLETED tasks"
    echo "🔴 Blocked:    $BLOCKED tasks"
    echo ""

    # Calculate progress
    TOTAL=54
    PROGRESS_PCT=$((COMPLETED * 100 / TOTAL))
    echo "📊 Overall Progress: $COMPLETED/$TOTAL tasks ($PROGRESS_PCT%)"

    # Show progress bar
    BAR_LENGTH=50
    FILLED=$((PROGRESS_PCT * BAR_LENGTH / 100))
    printf "["
    for i in $(seq 1 $FILLED); do printf "█"; done
    for i in $(seq $((FILLED+1)) $BAR_LENGTH); do printf "░"; done
    printf "] $PROGRESS_PCT%%\n"
    echo ""

    # Check for issues/alerts
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "ALERTS & ISSUES"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    ALERTS=0

    # Check if Session 5 hasn't started (blocks Session 7)
    if [ -z "$SESSION_5_BRANCH" ]; then
        echo "⚠️  ALERT: Session 5 (CLI) not started - blocking Session 7!"
        ALERTS=$((ALERTS+1))
    fi

    # Check if any session has been blocked for >5 minutes
    # (Would need timestamp tracking in STATUS files)

    # Check if any task has errors
    if echo "$TASK_BOARD" | grep -q "❌ ERROR"; then
        echo "🔴 ERROR: Some tasks have errors - check task board!"
        ALERTS=$((ALERTS+1))
    fi

    if [ $ALERTS -eq 0 ]; then
        echo "✅ No alerts - all systems nominal"
    fi
    echo ""

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Next update in 60 seconds... (Ctrl+C to stop)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    sleep 60
done
