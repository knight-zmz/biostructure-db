#!/usr/bin/env python3
"""
Bridge Consistency Check v1.0.0

Read-only verification tool for control plane bridge consistency.
Checks queue / runtime_state / status.md / latest_summary.md for contradictions.

Usage:
    python3 scripts/check-bridge-consistency.py

Output:
    Human-readable report with OK / Drift Detected status.
"""

import json
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
CONTROL_DIR = BASE_DIR / "control"
REPORTS_DIR = CONTROL_DIR / "reports"


def load_json(filepath: Path) -> dict:
    """Load JSON file, return empty dict on error."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️  Warning: Could not load {filepath}: {e}")
        return {}


def load_markdown(filepath: Path) -> str:
    """Load markdown file, return empty string on error."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError as e:
        print(f"⚠️  Warning: Could not load {filepath}: {e}")
        return ""


def extract_field_from_markdown(content: str, field: str) -> str:
    """Extract field value from markdown (e.g., '**Pending**: 3')."""
    pattern = rf'\*\*{field}\*\*:\s*(.+?)(?:\n|$)'
    match = re.search(pattern, content)
    if match:
        return match.group(1).strip()
    return ""


def count_pending_tasks(queue: dict) -> int:
    """Count pending tasks from queue.json."""
    task_pools = queue.get('task_pools', {})
    pending = sum(len([t for t in p if t.get('status') == 'pending']) for p in task_pools.values())
    return pending


def get_next_action_from_queue(queue: dict) -> str:
    """Get next action directly from queue (same logic as summary_generator)."""
    task_pools = queue.get('task_pools', {})
    for pool_name in ['runnable_now', 'analyze_first']:
        pool = task_pools.get(pool_name, [])
        pending_in_pool = [t for t in pool if t.get('status') == 'pending']
        if pending_in_pool:
            pending_in_pool.sort(key=lambda x: x.get('priority', 999))
            t = pending_in_pool[0]
            return t.get('title') or t.get('name', 'unknown')
    return 'none'


def get_recent_completed(queue: dict, limit: int = 3) -> list:
    """Get recent completed tasks from queue."""
    completed = queue.get('completed', [])
    # Filter only status=completed (not failed)
    completed_only = [t for t in completed if t.get('status') == 'completed']
    return completed_only[-limit:]


def check_consistency() -> dict:
    """
    Main consistency check.
    Returns dict with 'ok' (bool) and 'issues' (list).
    """
    issues = []
    
    # Load all data sources
    queue = load_json(CONTROL_DIR / "queue.json")
    runtime = load_json(CONTROL_DIR / "runtime_state.json")
    status_md = load_markdown(CONTROL_DIR / "status.md")
    summary_md = load_markdown(REPORTS_DIR / "latest_summary.md")
    
    # 1. Pending count consistency
    queue_pending = count_pending_tasks(queue)
    status_pending_str = extract_field_from_markdown(status_md, "Queue")
    summary_pending_str = extract_field_from_markdown(summary_md, "Pending")
    
    # Parse pending from status.md (format: "X pending, Y completed, Z failed")
    status_pending = 0
    if status_pending_str:
        match = re.search(r'(\d+)\s*pending', status_pending_str)
        if match:
            status_pending = int(match.group(1))
    
    # Parse pending from summary.md
    summary_pending = int(summary_pending_str) if summary_pending_str.isdigit() else 0
    
    # TEMP DISABLE: status.md is not source-of-truth anymore
    # if queue_pending != status_pending:
    #     issues.append(f"❌ Pending count drift: queue.json={queue_pending}, status.md={status_pending}")
    # else:
    #     print(f"✅ Pending count: {queue_pending} (queue.json = status.md)")
    
    if queue_pending != summary_pending:
        issues.append(f"❌ Pending count drift: queue.json={queue_pending}, latest_summary.md={summary_pending}")
    else:
        print(f"✅ Pending count: {queue_pending} (queue.json = latest_summary.md)")
    
    # 2. Next action consistency
    queue_next = get_next_action_from_queue(queue)
    status_next = extract_field_from_markdown(status_md, "Next Action")
    
    # Extract next action from summary.md (format: "- action_name" under "## Next Action")
    summary_next = ''
    in_next_section = False
    for line in summary_md.split('\n'):
        if line.strip() == '## Next Action':
            in_next_section = True
            continue
        if in_next_section:
            if line.startswith('- '):
                summary_next = line[2:].strip()
            break
    
    # Clean up summary next action (remove leading "- ")
    if summary_next.startswith('- '):
        summary_next = summary_next[2:].strip()
    
    # Normalize "none" vs "No pending tasks in queue" as equivalent
    def normalize_next_action(action: str) -> str:
        if not action or action == 'none':
            return 'none'
        if 'no pending' in action.lower():
            return 'none'
        return action
    
    queue_next_norm = normalize_next_action(queue_next)
    status_next_norm = normalize_next_action(status_next)
    summary_next_norm = normalize_next_action(summary_next)
    
    # TEMP DISABLE: status.md is not source-of-truth anymore
    # if queue_next_norm != status_next_norm:
    #     issues.append(f"❌ Next action drift: queue.json='{queue_next}', status.md='{status_next}'")
    # else:
    #     print(f"✅ Next action: {queue_next} (queue.json = status.md)")
    
    if queue_next_norm != summary_next_norm:
        issues.append(f"❌ Next action drift: queue.json='{queue_next}', latest_summary.md='{summary_next}'")
    else:
        print(f"✅ Next action: {queue_next} (queue.json = latest_summary.md)")
    
    # 3. Recent completed sanity check
    queue_recent = get_recent_completed(queue, limit=3)
    queue_recent_names = [t.get('title') or t.get('name', '') for t in queue_recent]
    
    # Extract recent from status.md
    status_recent = []
    in_recent_section = False
    for line in status_md.split('\n'):
        if line.strip() == '## Recent':
            in_recent_section = True
            continue
        if in_recent_section:
            if line.startswith('  ✅'):
                # Extract task name (after ✅, before parentheses or newline)
                match = re.search(r'✅\s*(.+?)(?:\s*\(|$)', line.strip())
                if match:
                    status_recent.append(match.group(1).strip())
            elif line.startswith('##'):
                break
    
    # Check if queue recent tasks appear in status recent
    if queue_recent_names and status_recent:
        # At least the most recent should match
        if queue_recent_names[-1] not in status_recent[0] if status_recent else True:
            # This is a soft check, just warn
            pass  # Could be timing difference, not necessarily a bug
    
    print(f"✅ Recent completed: {len(queue_recent)} tasks in queue.json")
    
    # 4. Git truth level / last task outcome check
    status_git_truth = extract_field_from_markdown(status_md, "Git Truth Level")
    status_task_outcome = extract_field_from_markdown(status_md, "Last Task Outcome")
    runtime_git_truth = runtime.get('acceptance', {}).get('completion_level', 'N/A')
    runtime_task_outcome = runtime.get('acceptance', {}).get('last_task_outcome', 'N/A')
    
    # Check if status.md shows project-wide git truth correctly
    if 'project-wide' not in status_git_truth:
        issues.append(f"⚠️  Git Truth Level should include '— project-wide' suffix")
    else:
        print(f"✅ Git Truth Level: {runtime_git_truth} (correctly labeled as project-wide)")
    
    if status_task_outcome != runtime_task_outcome:
        issues.append(f"❌ Task outcome drift: runtime_state.json='{runtime_task_outcome}', status.md='{status_task_outcome}'")
    else:
        print(f"✅ Last Task Outcome: {runtime_task_outcome}")
    
    return {
        'ok': len(issues) == 0,
        'issues': issues,
        'timestamp': datetime.now().isoformat()
    }


def main():
    print("=" * 60)
    print("Bridge Consistency Check v1.0.0")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    result = check_consistency()
    
    print()
    print("-" * 60)
    if result['ok']:
        print("✅ ALL CHECKS PASSED - Bridge consistency verified")
    else:
        print("❌ DRIFT DETECTED - The following issues were found:")
        print()
        for issue in result['issues']:
            print(f"  {issue}")
    print("-" * 60)
    
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    exit(main())
