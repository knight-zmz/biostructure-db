#!/usr/bin/env python3
"""
Handler: sync_bridge_metadata

Syncs latest_summary.md metadata from queue.json (source of truth).
Only updates Pending count and Next Action fields.

Boundary: doc_consistency_fix
Risk level: low (derived view sync, no source truth change)
"""

import json
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
QUEUE_PATH = BASE_DIR / "control" / "queue.json"
SUMMARY_PATH = BASE_DIR / "control" / "reports" / "latest_summary.md"


def main():
    try:
        # Read queue.json (source of truth)
        if not QUEUE_PATH.exists():
            print(json.dumps({
                "handler": "sync_bridge_metadata",
                "status": "failed",
                "error": f"queue.json not found: {QUEUE_PATH}",
                "timestamp": datetime.now().isoformat()
            }))
            return
        
        with open(QUEUE_PATH, 'r', encoding='utf-8') as f:
            queue_data = json.load(f)
        
        # Extract pending count from runnable_now pool
        runnable_now = queue_data.get("task_pools", {}).get("runnable_now", [])
        pending_count = len(runnable_now)
        
        # Extract next action (first task in runnable_now by priority)
        # Tasks are already sorted by priority in queue.json
        next_action = ""
        if runnable_now:
            # Sort by priority (lower number = higher priority)
            sorted_tasks = sorted(runnable_now, key=lambda x: x.get("priority", 99))
            next_action = sorted_tasks[0].get("title", "")
        
        # Read current summary
        if not SUMMARY_PATH.exists():
            print(json.dumps({
                "handler": "sync_bridge_metadata",
                "status": "failed",
                "error": f"latest_summary.md not found: {SUMMARY_PATH}",
                "timestamp": datetime.now().isoformat()
            }))
            return
        
        with open(SUMMARY_PATH, 'r', encoding='utf-8') as f:
            summary_content = f.read()
        
        # Track changes
        changes = []
        old_pending = None
        old_next_action = None
        
        # Update Pending count
        pending_pattern = r'(\*\*Pending\*\*: )(\d+)'
        pending_match = re.search(pending_pattern, summary_content)
        if pending_match:
            old_pending = pending_match.group(2)
            if old_pending != str(pending_count):
                summary_content = re.sub(
                    pending_pattern,
                    f"\\g<1>{pending_count}",
                    summary_content
                )
                changes.append(f"Pending: {old_pending} → {pending_count}")
        
        # Update Next Action
        next_action_pattern = r'(## Next Action\n- )(.+?)(\n|$)'
        next_action_match = re.search(next_action_pattern, summary_content)
        if next_action_match:
            old_next_action = next_action_match.group(2)
            if old_next_action != next_action:
                summary_content = re.sub(
                    next_action_pattern,
                    f"\\g<1>{next_action}\\n",
                    summary_content
                )
                changes.append(f"Next Action: {old_next_action} → {next_action}")
        
        # Write updated summary
        with open(SUMMARY_PATH, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        # Build result
        result = {
            "handler": "sync_bridge_metadata",
            "status": "success" if changes else "no_changes_needed",
            "changes": changes,
            "source": {
                "pending_count": pending_count,
                "next_action": next_action
            },
            "target": str(SUMMARY_PATH),
            "timestamp": datetime.now().isoformat()
        }
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({
            "handler": "sync_bridge_metadata",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))


if __name__ == '__main__':
    main()
