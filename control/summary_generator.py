#!/usr/bin/env python3
"""
Summary Generator v1.0.0

Minimal summary/report layer for the control plane.
Generates human-readable summaries at controlled intervals.

Trigger reasons:
  - queue_drained: all tasks in a batch completed
  - task_batch_completed: N tasks completed in this run
  - task_failed: a task failed
  - idle_cycles_exceeded: too many consecutive no-task runs
  - new_tasks_generated: auto-supply created new tasks (after idle)
  - daily_digest: periodic daily summary

Suppression rules:
  - idle: only report on first idle + every N-th cycle (default 8 = ~2 hours at 15min timer)
  - same reason: don't report same reason twice within cooldown (default 30 min)
  - daily_digest: only once per day
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

CONTROL_DIR = Path('/home/admin/biostructure-db/control')
REPORTS_DIR = CONTROL_DIR / "reports"
LATEST_SUMMARY = REPORTS_DIR / "latest_summary.md"

# --- Suppression thresholds ---
IDLE_REPORT_EVERY_N_CYCLES = 8   # ~2 hours at 15-min timer
SAME_REASON_COOLDOWN_MINUTES = 30
DAILY_DIGEST_HOUR = 8  # Generate daily digest at 8 AM


def _parse_iso(ts: str) -> Optional[datetime]:
    """Parse ISO timestamp string, compatible with Python 3.6."""
    if not ts:
        return None
    try:
        if '.' in ts:
            clean = ts.split('+')[0].split('Z')[0]
            return datetime.strptime(clean, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            clean = ts.split('+')[0].split('Z')[0]
            return datetime.strptime(clean, '%Y-%m-%dT%H:%M:%S')
    except (ValueError, TypeError):
        return None


def load_json(filepath: Path) -> dict:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json(filepath: Path, data: dict) -> bool:
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def _get_summary_state(runtime: dict) -> dict:
    """Get or initialize summary tracking state."""
    if 'summary' not in runtime:
        runtime['summary'] = {
            'last_summary_at': None,
            'last_summary_reason': None,
            'idle_cycles': 0,
            'reports_generated': 0,
            'daily_digest_last_date': None,
            'completed_since_last_summary': 0
        }
    ss = runtime['summary']
    ss.setdefault('completed_since_last_summary', 0)
    return ss


def _should_suppress(reason: str, summary_state: dict) -> bool:
    """Check if summary should be suppressed based on reason and cooldown."""
    now = datetime.now()
    
    # Daily digest: only once per day
    if reason == 'daily_digest':
        last_date = summary_state.get('daily_digest_last_date')
        today = now.strftime('%Y-%m-%d')
        if last_date == today:
            return True
        return False
    
    # Same-reason cooldown
    last_reason = summary_state.get('last_summary_reason')
    last_time_str = summary_state.get('last_summary_at')
    
    if last_reason == reason and last_time_str:
        try:
            last_time = _parse_iso(last_time_str)
            minutes_since = (now - last_time).total_seconds() / 60
            if minutes_since < SAME_REASON_COOLDOWN_MINUTES:
                return True
        except (ValueError, TypeError):
            pass
    
    # Idle-specific: only report every N cycles
    if reason == 'idle_cycles_exceeded':
        idle_cycles = summary_state.get('idle_cycles', 0)
        if idle_cycles % IDLE_REPORT_EVERY_N_CYCLES != 0:
            return True
    
    return False


def _count_queue(queue: dict) -> Dict[str, int]:
    """Count tasks by status across all pools."""
    counts = {'pending': 0, 'completed': 0, 'failed': 0}
    
    # Multi-pool structure
    task_pools = queue.get('task_pools', {})
    for pool_name, tasks in task_pools.items():
        for t in tasks:
            status = t.get('status', 'unknown')
            if status in counts:
                counts[status] += 1
    
    # Completed tasks
    for t in queue.get('completed', []):
        status = t.get('status', 'unknown')
        if status in counts:
            counts[status] += 1
    
    return counts


def _get_recent_tasks(queue: dict, status: str, limit: int = 5) -> List[dict]:
    """Get most recent tasks by status."""
    tasks = []
    for t in queue.get('completed', []):
        if t.get('status') == status:
            tasks.append(t)
    # Sort by completed_at descending
    tasks.sort(key=lambda x: x.get('completed_at', ''), reverse=True)
    return tasks[:limit]


def _get_system_health() -> Dict[str, str]:
    """Quick system health check."""
    health = {}
    try:
        import subprocess
        # PM2 status
        r = subprocess.run(['pm2', 'list', '--no-color'], capture_output=True, text=True, timeout=5)
        health['pm2'] = 'online' if 'online' in r.stdout else 'degraded'
    except Exception:
        health['pm2'] = 'unknown'
    return health


def generate_summary(
    reason: str,
    queue: dict,
    runtime: dict,
    extra_context: Optional[Dict] = None
) -> Optional[str]:
    """
    Generate a summary report if not suppressed.
    
    Returns:
        Path to generated summary file, or None if suppressed.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    summary_state = _get_summary_state(runtime)
    
    # Check suppression
    if _should_suppress(reason, summary_state):
        return None
    
    now = datetime.now()
    timestamp = now.isoformat()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M')
    
    # Gather data
    phase = runtime.get('current_state', {}).get('phase', 'unknown')
    phase_status = runtime.get('current_state', {}).get('phase_status', 'unknown')
    last_activity = runtime.get('current_state', {}).get('last_activity', 'N/A')
    last_activity_type = runtime.get('current_state', {}).get('last_activity_type', 'N/A')
    
    queue_counts = _count_queue(queue)
    pending_count = queue_counts['pending']
    completed_count = queue_counts['completed']
    failed_count = queue_counts['failed']
    
    recent_completed = _get_recent_tasks(queue, 'completed', limit=5)
    recent_failed = _get_recent_tasks(queue, 'failed', limit=3)
    
    idle_cycles = summary_state.get('idle_cycles', 0)
    
    # Next action
    next_action = runtime.get('next_default_action', {})
    next_desc = next_action.get('description', 'No pending action')
    
    # Reason labels
    reason_labels = {
        'queue_drained': '🗑️ Queue Drained',
        'batch_summary': '📋 Batch Summary (3 tasks)',
        'task_failed': '❌ Task Failed',
        'idle_cycles_exceeded': '⏸️ Idle Cycles Exceeded',
        'supply_summary': '🔄 Tasks Auto-Supplied',
        'daily_digest': '📊 Daily Digest'
    }
    reason_label = reason_labels.get(reason, reason)
    
    # Build markdown
    lines = []
    lines.append(f"# Control Plane Summary")
    lines.append(f"")
    lines.append(f"**Generated**: {date_str} {time_str}")
    lines.append(f"**Trigger**: {reason_label}")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## Phase Status")
    lines.append(f"- **Current Phase**: {phase} ({phase_status})")
    lines.append(f"- **Last Activity**: {last_activity_type}")
    lines.append(f"- **Last Activity Time**: {last_activity}")
    lines.append(f"")
    lines.append(f"## Queue Overview")
    lines.append(f"- **Pending**: {pending_count}")
    lines.append(f"- **Completed**: {completed_count}")
    lines.append(f"- **Failed**: {failed_count}")
    lines.append(f"- **Idle Cycles**: {idle_cycles}")
    lines.append(f"")
    
    if recent_completed:
        lines.append(f"## Recently Completed")
        for t in recent_completed:
            name = t.get('title') or t.get('name', t.get('id', 'unknown'))
            completed_at = t.get('completed_at', 'N/A')
            handler = t.get('handler', '')
            lines.append(f"- ✅ {name} ({handler}) — {completed_at}")
        lines.append(f"")
    
    if recent_failed:
        lines.append(f"## Recently Failed")
        for t in recent_failed:
            name = t.get('title') or t.get('name', t.get('id', 'unknown'))
            result = t.get('result', {})
            error = result.get('error', 'unknown error')
            lines.append(f"- ❌ {name} — {error}")
        lines.append(f"")
    
    lines.append(f"## Next Action")
    lines.append(f"- {next_desc}")
    lines.append(f"")
    
    if extra_context:
        lines.append(f"## Context")
        for k, v in extra_context.items():
            lines.append(f"- **{k}**: {v}")
        lines.append(f"")
    
    lines.append(f"---")
    lines.append(f"*Generated by summary_generator v1.0.0*")
    
    content = '\n'.join(lines)
    
    # Write latest_summary.md
    with open(LATEST_SUMMARY, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Write timestamped historical file
    ts_filename = f"summary_{now.strftime('%Y%m%d_%H%M%S')}_{reason}.md"
    ts_path = REPORTS_DIR / ts_filename
    with open(ts_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Update summary state
    summary_state['last_summary_at'] = timestamp
    summary_state['last_summary_reason'] = reason
    summary_state['reports_generated'] = summary_state.get('reports_generated', 0) + 1
    
    if reason == 'daily_digest':
        summary_state['daily_digest_last_date'] = date_str
    
    runtime['summary'] = summary_state
    runtime.setdefault('_meta', {})['updated'] = timestamp
    
    return str(LATEST_SUMMARY)


def evaluate_and_generate(
    queue: dict,
    runtime: dict,
    just_completed: Optional[dict] = None,
    just_failed: Optional[dict] = None,
    tasks_generated: int = 0,
    is_idle: bool = False
) -> Optional[str]:
    """
    Evaluate current state and decide whether to generate a summary.
    
    Summary rules (v1.3):
      - daily_digest: once per day at hour >= 8
      - task_failed: every failure (with same-reason cooldown)
      - queue_drained: when queue empties out
      - batch_summary: every 3 completed tasks
      - supply_summary: after auto-supply generates new tasks
      - idle_cycles_exceeded: every 8 idle cycles (~80 min at 10-min timer)
    
    Call this at the end of each agent_loop run.
    
    Returns:
        Path to generated summary, or None if suppressed/no action needed.
    """
    summary_state = _get_summary_state(runtime)
    now = datetime.now()
    
    # --- Daily digest check (highest priority) ---
    hour = now.hour
    if hour >= DAILY_DIGEST_HOUR:
        last_date = summary_state.get('daily_digest_last_date')
        today = now.strftime('%Y-%m-%d')
        if last_date != today:
            result = generate_summary('daily_digest', queue, runtime)
            if result:
                return result
    
    # --- Task failed → always report ---
    if just_failed:
        result = generate_summary('task_failed', queue, runtime, {
            'failed_task': just_failed.get('name', just_failed.get('id', 'unknown')),
            'error': just_failed.get('result', {}).get('error', 'unknown')
        })
        if result:
            return result
    
    # --- Tasks completed this run ---
    if just_completed:
        # Check if queue is now drained
        task_pools = queue.get('task_pools', {})
        pending_in_pools = sum(
            len([t for t in pool if t.get('status') == 'pending'])
            for pool in task_pools.values()
        )
        
        if pending_in_pools == 0:
            # Queue drained — always report
            result = generate_summary('queue_drained', queue, runtime, {
                'last_completed': just_completed.get('name', just_completed.get('id', 'unknown'))
            })
            if result:
                return result
        else:
            # Batch check: report every 3 completions
            completed_since = summary_state.get('completed_since_last_summary', 0) + 1
            summary_state['completed_since_last_summary'] = completed_since
            runtime['summary'] = summary_state
            
            if completed_since >= 3:
                summary_state['completed_since_last_summary'] = 0
                runtime['summary'] = summary_state
                result = generate_summary('batch_summary', queue, runtime, {
                    'batch_size': completed_since,
                    'remaining': pending_in_pools
                })
                if result:
                    return result
            # Otherwise: silent (don't report every single task)
    
    # --- New tasks generated (supply) ---
    if tasks_generated > 0:
        result = generate_summary('supply_summary', queue, runtime, {
            'tasks_generated': tasks_generated
        })
        # Reset idle counter on supply
        summary_state['idle_cycles'] = 0
        runtime['summary'] = summary_state
        if result:
            return result
    
    # --- Idle tracking ---
    if is_idle:
        summary_state['idle_cycles'] = summary_state.get('idle_cycles', 0) + 1
        runtime['summary'] = summary_state
        
        # Only generate summary at threshold intervals
        if summary_state['idle_cycles'] % IDLE_REPORT_EVERY_N_CYCLES == 0:
            result = generate_summary('idle_cycles_exceeded', queue, runtime)
            if result:
                return result
    
    return None
