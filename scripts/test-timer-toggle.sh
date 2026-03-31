#!/bin/bash
# Toggle test timer on/off for debugging sessions
# Usage: ./scripts/test-timer-toggle.sh [on|off|status]

ACTION="${1:-status}"

case "$ACTION" in
    on)
        sudo systemctl start openclaw-agent-test.timer
        echo "✅ Test timer ENABLED"
        systemctl list-timers openclaw-agent-test.timer --no-pager 2>/dev/null
        ;;
    off)
        sudo systemctl stop openclaw-agent-test.timer
        echo "🛑 Test timer DISABLED (still installed, just not triggering)"
        ;;
    status)
        echo "=== Test Timer ===" 
        systemctl is-active openclaw-agent-test.timer 2>/dev/null
        systemctl list-timers openclaw-agent-test.timer --no-pager 2>/dev/null
        echo ""
        echo "=== Prod Timer ==="
        systemctl is-active openclaw-agent.timer 2>/dev/null
        ;;
    *)
        echo "Usage: $0 [on|off|status]"
        exit 1
        ;;
esac
