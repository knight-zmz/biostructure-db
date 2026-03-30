#!/bin/bash
# timer-toggle.sh - Switch between OpenClaw timer modes
# Usage: ./scripts/timer-toggle.sh [prod|test|status]

set -e

PROD_TIMER="openclaw-agent.timer"
TEST_TIMER="openclaw-agent-test.timer"
SERVICE="openclaw-agent.service"

case "${1:-status}" in
    prod|production)
        echo "=== Switching to PRODUCTION mode ==="
        sudo systemctl stop $TEST_TIMER 2>/dev/null || true
        sudo systemctl disable $TEST_TIMER 2>/dev/null || true
        sudo systemctl daemon-reload
        sudo systemctl enable $PROD_TIMER
        sudo systemctl start $PROD_TIMER
        echo "Production timer enabled (8:00-20:00 every 15 min)"
        systemctl status $PROD_TIMER --no-pager | head -8
        ;;
    test)
        echo "=== Switching to TEST mode ==="
        sudo systemctl stop $PROD_TIMER 2>/dev/null || true
        sudo systemctl disable $PROD_TIMER 2>/dev/null || true
        sudo systemctl daemon-reload
        sudo systemctl enable $TEST_TIMER
        sudo systemctl start $TEST_TIMER
        echo "Test timer enabled (every 2 min)"
        systemctl status $TEST_TIMER --no-pager | head -8
        ;;
    status)
        echo "=== Timer Status ==="
        echo "--- Production ---"
        systemctl status $PROD_TIMER --no-pager 2>/dev/null | head -8 || echo "  (inactive)"
        echo ""
        echo "--- Test ---"
        systemctl status $TEST_TIMER --no-pager 2>/dev/null | head -8 || echo "  (inactive)"
        echo ""
        systemctl list-timers --all 2>/dev/null | grep -i openclaw || echo "No openclaw timers active"
        ;;
    *)
        echo "Usage: $0 [prod|test|status]"
        exit 1
        ;;
esac
