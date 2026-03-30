#!/usr/bin/env python3
"""
Handler: sync_control_state

Sync control plane state files with actual systemd state.
Updates queue.json config.timer_enabled to match systemd timer status.
"""

import json
import subprocess
import sys
from pathlib import Path

CONTROL_DIR = Path(__file__).resolve().parent.parent
QUEUE_JSON = CONTROL_DIR / "queue.json"

def check_systemd_timer() -> bool:
    """Check if openclaw-agent.timer is enabled and active."""
    try:
        # Check if enabled
        result = subprocess.run(
            ['systemctl', 'is-enabled', 'openclaw-agent.timer'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        is_enabled = result.stdout.strip() == 'enabled'
        
        # Check if active
        result = subprocess.run(
            ['systemctl', 'is-active', 'openclaw-agent.timer'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        is_active = result.stdout.strip() == 'active'
        
        return is_enabled or is_active  # Either is fine
    except Exception:
        return False

def main():
    try:
        # Read queue.json
        with open(QUEUE_JSON, 'r', encoding='utf-8') as f:
            queue = json.load(f)
        
        # Check actual systemd state
        systemd_timer_active = check_systemd_timer()
        
        # Update timer_enabled to match
        current_value = queue.get('config', {}).get('timer_enabled', False)
        
        if current_value == systemd_timer_active:
            result = {
                "handler": "sync_control_state",
                "status": "success",
                "message": f"No sync needed - timer_enabled already {current_value}"
            }
        else:
            queue.setdefault('config', {})['timer_enabled'] = systemd_timer_active
            
            # Write updated queue.json
            with open(QUEUE_JSON, 'w', encoding='utf-8') as f:
                json.dump(queue, f, indent=2, ensure_ascii=False)
            
            result = {
                "handler": "sync_control_state",
                "status": "success",
                "message": f"Synced timer_enabled: {current_value} → {systemd_timer_active}",
                "systemd_timer_active": systemd_timer_active
            }
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            "handler": "sync_control_state",
            "status": "failed",
            "error": str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
