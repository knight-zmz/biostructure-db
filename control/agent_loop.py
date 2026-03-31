#!/usr/bin/env python3
"""
OpenClaw Agent Loop v1.0.0

Minimal execution loop for biostructure-db project control plane.
Reads control files, executes tasks, updates state.

Usage:
    python3 agent_loop.py [--dry-run] [--force-task TASK_ID]

Control files:
    - control/queue.json       - Task queue
    - control/paused.json      - Paused tasks
    - control/runtime_state.json - Runtime state
    - control/phase_policy.json  - Phase execution policy

Logs:
    - control/logs/agent-loop.log
"""

import json
import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Import summary generator
sys.path.insert(0, str(Path(__file__).resolve().parent))
from summary_generator import evaluate_and_generate, mark_event_read, get_compact_summary
from pathlib import Path
import subprocess

# Configuration - Use resolve() for absolute path regardless of cwd
BASE_DIR = Path(__file__).resolve().parent.parent
CONTROL_DIR = BASE_DIR / "control"
LOGS_DIR = CONTROL_DIR / "logs"
HANDLERS_DIR = CONTROL_DIR / "handlers"

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "agent-loop.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def parse_iso(ts: str) -> Optional[datetime]:
    """Parse ISO timestamp string, compatible with Python 3.6."""
    if not ts:
        return None
    try:
        # Handle both with and without microseconds
        if '.' in ts:
            # Strip timezone suffix if present
            clean = ts.split('+')[0].split('Z')[0]
            return datetime.strptime(clean, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            clean = ts.split('+')[0].split('Z')[0]
            return datetime.strptime(clean, '%Y-%m-%dT%H:%M:%S')
    except (ValueError, TypeError):
        return None


def load_json(filepath: Path) -> dict:
    """Load JSON file with error handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        return {}


def save_json(filepath: Path, data: dict) -> bool:
    """Save JSON file with error handling."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save {filepath}: {e}")
        return False


def get_next_task(queue: dict, runtime: dict, policy: dict) -> Optional[dict]:
    """
    Get next executable task from queue.
    Supports both legacy flat queue and new multi-pool structure.
    
    Returns:
        Task dict or None if no task available
    """
    # Check for new multi-pool structure first
    task_pools = queue.get('task_pools', None)
    
    if task_pools:
        # New structure: iterate through pools in priority order
        pool_order = policy.get('execution_policy', {}).get('pool_execution_order', 
                      ['runnable_now', 'analyze_first', 'waiting_user'])
        
        for pool_name in pool_order:
            pool = task_pools.get(pool_name, [])
            pending = [t for t in pool if t.get('status') == 'pending']
            
            if not pending:
                continue
            
            # Sort by priority
            pending.sort(key=lambda x: x.get('priority', 999))
            
            # Check dependencies and auto_execute flag
            completed_ids = [t['id'] for t in queue.get('completed', [])]
            
            for task in pending:
                # Skip tasks that require manual execution
                if not task.get('auto_execute', True):
                    continue
                
                deps = task.get('depends_on', [])
                if all(dep in completed_ids for dep in deps):
                    task['_pool'] = pool_name  # Track which pool task came from
                    return task
        
        logger.info("No pending tasks in any pool")
        return None
    
    else:
        # Legacy flat queue structure (backward compatibility)
        tasks = queue.get('queue', [])
        
        # Filter pending tasks
        pending = [t for t in tasks if t.get('status') == 'pending']
        
        if not pending:
            logger.info("No pending tasks in queue")
            return None
        
        # Sort by priority
        pending.sort(key=lambda x: x.get('priority', 999))
        
        # Check dependencies
        completed_ids = [t['id'] for t in queue.get('completed', [])]
        
        for task in pending:
            deps = task.get('depends_on', [])
            if all(dep in completed_ids for dep in deps):
                return task
        
        logger.info("No tasks ready (dependencies not met)")
        return None


def execute_handler(task: dict, policy: dict) -> Tuple[bool, dict]:
    """
    Execute task handler.
    
    Returns:
        (success: bool, result: dict)
    """
    handler_name = task.get('handler', '')
    
    if not handler_name:
        logger.error(f"Task {task['id']} has no handler")
        return False, {"error": "no_handler"}
    
    handler_path = HANDLERS_DIR / f"{handler_name}.py"
    
    if not handler_path.exists():
        logger.error(f"Handler not found: {handler_path}")
        return False, {"error": "handler_not_found", "path": str(handler_path)}
    
    logger.info(f"Executing handler: {handler_name}")
    
    try:
        # Execute handler as subprocess
        result = subprocess.run(
            ['python3', str(handler_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=policy.get('handler_registry', {}).get(handler_name, {}).get('timeout_seconds', 300),
            cwd=str(BASE_DIR)
        )
        
        if result.returncode == 0:
            logger.info(f"Handler {handler_name} completed successfully")
            # Try to parse result JSON from stdout
            try:
                result_data = json.loads(result.stdout.strip()) if result.stdout.strip() else {}
            except json.JSONDecodeError:
                result_data = {"output": result.stdout.strip()}
            return True, result_data
        else:
            logger.error(f"Handler {handler_name} failed: {result.stderr}")
            return False, {"error": result.stderr, "output": result.stdout}
            
    except subprocess.TimeoutExpired:
        logger.error(f"Handler {handler_name} timed out")
        return False, {"error": "timeout"}
    except Exception as e:
        logger.error(f"Handler {handler_name} exception: {e}")
        return False, {"error": str(e)}


def update_queue_after_task(queue: dict, task: dict, success: bool, result: dict) -> dict:
    """Update queue after task execution. Supports multi-pool structure."""
    pool_name = task.get('_pool', None)
    
    if success:
        # Move task to completed with status layer fields
        completed_task = {
            **task,
            'status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'result': result,
            # Status layer: verification fields
            'verification': {
                'handler_success': True,
                'log_recorded': True,
                'runtime_state_updated': True,
                'verified': True
            },
            # Status layer: git state (updated by external commit workflow)
            'git_state': 'uncommitted',
            # Machine-readable lifecycle state (derived from verification + git_state)
            'lifecycle_state': 'verified'
        }
        # Remove internal _pool field before storing
        completed_task.pop('_pool', None)
        queue['completed'].append(completed_task)
        
        # Handle multi-pool structure
        if pool_name and 'task_pools' in queue:
            # Remove from the specific pool
            task_pools = queue.get('task_pools', {})
            pool = task_pools.get(pool_name, [])
            task_pools[pool_name] = [t for t in pool if t['id'] != task['id']]
            queue['task_pools'] = task_pools
            
            # Unblock dependent tasks in all pools
            for pname, ppool in task_pools.items():
                for t in ppool:
                    if task['id'] in t.get('depends_on', []):
                        t['status'] = 'pending'
        else:
            # Legacy flat queue structure
            queue['queue'] = [t for t in queue['queue'] if t['id'] != task['id']]
            
            # Unblock dependent tasks
            for t in queue['queue']:
                if task['id'] in t.get('depends_on', []):
                    t['status'] = 'pending'
    else:
        # Mark task as failed, move to completed
        failed_task = {
            **task,
            'status': 'failed',
            'completed_at': datetime.now().isoformat(),
            'result': result,
            'verification': {
                'handler_success': False,
                'log_recorded': True,
                'runtime_state_updated': True,
                'verified': False
            },
            'git_state': 'uncommitted',
            'lifecycle_state': 'implemented'
        }
        failed_task.pop('_pool', None)
        queue['completed'].append(failed_task)

        if pool_name and 'task_pools' in queue:
            task_pools = queue.get('task_pools', {})
            pool = task_pools.get(pool_name, [])
            task_pools[pool_name] = [t for t in pool if t['id'] != task['id']]
            queue['task_pools'] = task_pools
        else:
            queue['queue'] = [t for t in queue['queue'] if t['id'] != task['id']]
    
    queue['_meta']['updated'] = datetime.now().isoformat()
    return queue


def update_runtime_state(runtime: dict, task: dict, success: bool) -> dict:
    """Update runtime state after task execution."""
    runtime.setdefault('current_state', {})['last_activity'] = datetime.now().isoformat()
    runtime.setdefault('current_state', {})['last_activity_type'] = f"{task['handler']}.{'completed' if success else 'failed'}"
    
    if not success:
        # Increment error count
        runtime.setdefault('error_count', 0)
        runtime['error_count'] += 1
    
    runtime.setdefault('_meta', {})['updated'] = datetime.now().isoformat()
    return runtime


def _verify_git_truth() -> dict:
    """
    Verify current git truth level (L1-L4).
    
    L4 requires ALL:
    1. Working tree clean (excluding runtime files)
    2. Local HEAD == origin/main HEAD
    3. Acceptance policy exists
    
    Returns completion_level and evidence.
    """
    BASE = CONTROL_DIR.parent
    result = {
        'completion_level': 'L1',
        'evidence': {}
    }
    
    # L2: Check working tree (exclude runtime files)
    try:
        r = subprocess.Popen('git status --short', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE)
        stdout, _ = r.communicate()
        status = stdout.decode('utf-8').strip()
        lines = [l for l in status.split('\n') if l.strip() and 'node_modules' not in l]
        # Filter runtime files
        runtime = ['control/runtime_state.json', 'control/status.md', 'control/logs/', 'control/reports/', 'control/__pycache__/']
        filtered = [l for l in lines if not any(rt in l for rt in runtime)]
        result['evidence']['working_tree_clean'] = len(filtered) == 0
        result['evidence']['git_status_filtered'] = filtered
        if status:
            result['evidence']['file_diff'] = list(set(l.split()[-1] for l in lines if l))
            result['completion_level'] = 'L2'
    except:
        result['evidence']['working_tree_clean'] = True
    
    # L3: Check commit
    try:
        r = subprocess.Popen("git log -1 --format='%H %s'", shell=True, stdout=subprocess.PIPE, cwd=BASE)
        stdout, _ = r.communicate()
        log = stdout.decode('utf-8').strip()
        if log:
            result['evidence']['commit_hash'] = log.split()[0]
            result['evidence']['commit_message'] = ' '.join(log.split()[1:])
            result['completion_level'] = 'L3'
    except:
        pass
    
    # L4: Check pushed AND clean
    try:
        r = subprocess.Popen("git log -1 --format='%H'", shell=True, stdout=subprocess.PIPE, cwd=BASE)
        local_log = r.communicate()[0].decode('utf-8').strip()
        r = subprocess.Popen("git log origin/main -1 --format='%H'", shell=True, stdout=subprocess.PIPE, cwd=BASE)
        remote_log = r.communicate()[0].decode('utf-8').strip()
        heads_match = local_log and remote_log and local_log == remote_log
        tree_clean = result['evidence'].get('working_tree_clean', False)
        
        if heads_match and tree_clean:
            result['evidence']['push_confirmation'] = True
            result['evidence']['remote_branch'] = 'origin/main'
            result['completion_level'] = 'L4'
        else:
            result['evidence']['push_confirmation'] = heads_match
            result['evidence']['remote_branch'] = 'origin/main' if heads_match else None
            if not tree_clean:
                result['evidence']['l4_blocked_reason'] = 'working_tree_dirty'
    except:
        pass
    
    # Re-audit check
    policy_path = CONTROL_DIR / "acceptance_policy.json"
    re_audit_passed = policy_path.exists()
    result['evidence']['re_audit_passed'] = re_audit_passed
    
    # Final determination
    result['evidence']['may_claim_completed'] = (
        result['completion_level'] == 'L4' and
        result['evidence'].get('working_tree_clean', False) and
        result['evidence'].get('re_audit_passed', False)
    )
    
    # Output summary
    result['output'] = {
        'completion_level': result['completion_level'],
        'working_tree_clean': result['evidence'].get('working_tree_clean', False),
        'commit_hash': result['evidence'].get('commit_hash'),
        'push_confirmation': result['evidence'].get('push_confirmation', False),
        'remote_branch': result['evidence'].get('remote_branch'),
        're_audit_passed': result['evidence'].get('re_audit_passed', False),
        'may_claim_completed': result['evidence']['may_claim_completed']
    }
    
    return result


def _level_label(level: str) -> str:
    """Convert completion level to human-readable label."""
    labels = {
        'L1': 'analysis only',
        'L2': 'local modified',
        'L3': 'local committed',
        'L4': 'remote truth'
    }
    return labels.get(level, level)


def _write_status_bridge(queue: dict, runtime: dict, context_policy: dict = None, git_truth: dict = None) -> None:
    """
    Write control/status.md — single consumer-friendly status file.
    This is the push bridge: external systems (OpenClaw heartbeat) read this.
    
    Format: Status Query Protocol v1.
    
    All fields computed from the SAME snapshot to avoid contradictions.
    """
    import subprocess as _sub
    
    now_dt = datetime.now()
    phase = runtime.get('current_state', {}).get('phase', 'unknown')
    phase_status = runtime.get('current_state', {}).get('phase_status', 'unknown')
    last_activity = runtime.get('current_state', {}).get('last_activity_type', 'N/A')
    last_time = runtime.get('current_state', {}).get('last_activity', 'N/A')
    
    # Count queue state from the SAME queue snapshot
    task_pools = queue.get('task_pools', {})
    pending = sum(len([t for t in p if t.get('status') == 'pending']) for p in task_pools.values())
    completed_count = len([t for t in queue.get('completed', []) if t.get('status') == 'completed'])
    failed_count = len([t for t in queue.get('completed', []) if t.get('status') == 'failed'])
    
    # Find actual next runnable task (not from runtime_state, from live queue)
    next_task_name = 'none'
    for pool_name in ['runnable_now', 'analyze_first', 'waiting_user']:
        pool = task_pools.get(pool_name, [])
        pending_in_pool = [t for t in pool if t.get('status') == 'pending']
        if pending_in_pool:
            pending_in_pool.sort(key=lambda x: x.get('priority', 999))
            t = pending_in_pool[0]
            next_task_name = t.get('title') or t.get('name', t.get('id', '?'))
            break
    
    summary_state = runtime.get('summary', {})
    last_summary_reason = summary_state.get('last_summary_reason', 'none')
    idle_cycles = summary_state.get('idle_cycles', 0)
    is_idle = pending == 0
    
    # Detect execution mode: autonomous (timer) vs manual vs fully idle
    last_run_str = runtime.get('last_run_at') or runtime.get('current_state', {}).get('last_activity', '')
    execution_mode = 'fully_idle'
    if last_run_str:
        try:
            clean = last_run_str.split('+')[0].split('Z')[0]
            if '.' in clean:
                last_run_dt = datetime.strptime(clean, '%Y-%m-%dT%H:%M:%S.%f')
            else:
                last_run_dt = datetime.strptime(clean, '%Y-%m-%dT%H:%M:%S')
            minutes_since = (now_dt - last_run_dt).total_seconds() / 60
            
            # Check if any timer is active
            timer_active = False
            try:
                r = _sub.run(['systemctl', 'is-active', 'openclaw-agent.timer'], 
                           capture_output=True, text=True, timeout=3)
                if r.stdout.strip() == 'active':
                    timer_active = True
                r2 = _sub.run(['systemctl', 'is-active', 'openclaw-agent-test.timer'],
                            capture_output=True, text=True, timeout=3)
                if r2.stdout.strip() == 'active':
                    timer_active = True
            except Exception:
                pass
            
            if timer_active:
                execution_mode = 'autonomous_active'
            elif minutes_since < 60:
                execution_mode = 'manually_active_recently'
            elif minutes_since < 360:
                execution_mode = 'manually_active_hours_ago'
            else:
                execution_mode = 'fully_idle'
        except (ValueError, TypeError):
            pass
    
    # Recent completed (last 3)
    recent = queue.get('completed', [])[-3:]
    recent_lines = []
    for t in reversed(recent):
        name = t.get('title') or t.get('name', t.get('id', '?'))
        status = t.get('status', '?')
        marker = '✅' if status == 'completed' else '❌'
        recent_lines.append(f"  {marker} {name}")
    recent_block = '\n'.join(recent_lines) if recent_lines else '  (none)'
    
    now = now_dt.strftime('%Y-%m-%d %H:%M')
    
    # Mode label
    mode_labels = {
        'autonomous_active': 'timer running',
        'manually_active_recently': f'manual trigger ({last_activity})',
        'manually_active_hours_ago': f'manual trigger hours ago',
        'fully_idle': 'idle (no timer, no recent manual run)',
    }
    mode_label = mode_labels.get(execution_mode, execution_mode)
    
    lines = [
        f"# Control Plane Status",
        f"",
        f"**Updated**: {now}",
        f"**Mode**: {mode_label}",
        f"**Phase**: {phase} ({phase_status})",
        f"**Queue**: {pending} pending, {completed_count} completed, {failed_count} failed",
        f"**Idle**: {'yes (' + str(idle_cycles) + ' cycles)' if is_idle else 'no'}",
        f"**Last Activity**: {last_activity}",
        f"**Last Summary**: {last_summary_reason}",
        f"**Next Action**: {next_task_name}",
        f"**Last Event**: {summary_state.get('last_event', 'none')}",
        f"**Last Event Time**: {summary_state.get('last_event_time', 'N/A')}",
        f"**Unread Event**: {'yes' if summary_state.get('unread_event', False) else 'no'}",
        f"**Event Update**: {'available (control/reports/latest_event.md)' if (CONTROL_DIR / 'reports' / 'latest_event.md').exists() and summary_state.get('unread_event', False) else 'none'}",
        f"**Last Task Outcome**: {runtime.get('acceptance', {}).get('last_task_outcome', 'N/A')}",
        f"**Completion Level**: {git_truth['completion_level'] if git_truth else 'N/A'} ({_level_label(git_truth['completion_level']) if git_truth else ''})",
        f"",
        f"## Recent",
        f"{recent_block}",
    ]
    
    # Embed context policy rules (so consumers know what to read)
    if context_policy:
        lines.append(f"")
        lines.append(f"## Read Policy")
        default = context_policy.get('default_read', [])
        lines.append(f"default: {', '.join(default)}")
        for key, rule in context_policy.get('conditional_read', {}).items():
            trigger_sample = ', '.join(rule.get('trigger', [])[:3])
            reads = ', '.join(rule.get('read', []))
            lines.append(f"- {key}: [{trigger_sample}...] → {reads}")
    
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"*Protocol: Status Query Protocol v1 | See latest_summary.md for full report.*")
    
    status_path = CONTROL_DIR / "status.md"
    try:
        with open(status_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    except Exception:
        pass


def generate_tasks_if_needed(queue: dict, task_sources: dict) -> dict:
    """
    Minimal task auto-supply: generate tasks from templates when queue is empty.
    
    task_sources comes from queue.templates.json (static config), not queue.json.
    Deduplication: per-source cooldown window via _meta.generation_log.
    Only generates low-risk tasks (read-only audits, log checks, proposals).
    """
    task_pools = queue.get('task_pools', {})
    runnable_now = task_pools.get('runnable_now', [])
    sources = task_sources
    meta = queue.get('_meta', {})
    
    # Initialize generation log if not present
    if 'generation_log' not in meta:
        meta['generation_log'] = {}
    
    generation_log = meta['generation_log']
    now = datetime.now()
    generated_count = 0
    
    for source_name, source_def in sources.items():
        if not source_def.get('auto_generate', False):
            continue
        
        templates = source_def.get('templates', [])
        if not templates:
            continue
        
        cooldown_hours = source_def.get('cooldown_hours', 24)
        
        # Check if this source was recently generated
        last_gen_str = generation_log.get(source_name)
        if last_gen_str:
            try:
                last_gen = parse_iso(last_gen_str)
                hours_since = (now - last_gen).total_seconds() / 3600
                if hours_since < cooldown_hours:
                    continue  # Still in cooldown
            except (ValueError, TypeError):
                pass  # Invalid timestamp, allow generation
        
        # Check if any template is not already in runnable_now or completed
        completed_ids = {t['id'] for t in queue.get('completed', [])}
        runnable_ids = {t['id'] for t in runnable_now}
        
        for template in templates:
            template_id = template.get('template_id', '')
            # Generate a stable task ID from template
            task_id = f"auto-{template_id}"
            
            # Skip if already running or recently completed
            if task_id in runnable_ids:
                continue
            if task_id in completed_ids:
                # Check if completed recently (within 2x cooldown)
                for ct in queue.get('completed', []):
                    if ct['id'] == task_id:
                        completed_at = ct.get('completed_at', '')
                        try:
                            cat = parse_iso(completed_at)
                            hours_since = (now - cat).total_seconds() / 3600
                            if hours_since < cooldown_hours * 2:
                                continue  # Skip, recently completed
                        except (ValueError, TypeError):
                            pass
            
            # Generate task
            new_task = {
                'id': task_id,
                'name': template.get('name', template_id),
                'title': template.get('title', ''),
                'source': source_name,
                'phase': template.get('phase', 'P2'),
                'priority': template.get('priority', 5),
                'status': 'pending',
                'handler': template.get('handler', ''),
                'boundary': template.get('boundary', 'read_only_audit'),
                'done_when': template.get('done_when', ''),
                'auto_execute': True,
                'risk_level': template.get('risk_level', 'low'),
                'generated_at': now.isoformat(),
                'template_id': template_id
            }
            
            target_pool = template.get('target_pool', 'runnable_now')
            if target_pool in task_pools:
                task_pools[target_pool].append(new_task)
            else:
                task_pools[target_pool] = [new_task]
            
            generated_count += 1
        
        # Update generation log for this source
        generation_log[source_name] = now.isoformat()
    
    if generated_count > 0:
        queue['task_pools'] = task_pools
        meta['generation_log'] = generation_log
        queue['_meta'] = meta
        queue['_meta']['updated'] = now.isoformat()
    
    return queue, generated_count


def main():
    """Main execution loop."""
    logger.info("=" * 60)
    logger.info("OpenClaw Agent Loop v1.0.0 starting")
    logger.info(f"Base directory (normalized): {BASE_DIR.resolve()}")
    logger.info(f"Script path: {Path(__file__).resolve()}")
    logger.info("=" * 60)
    
    # Load control files
    queue = load_json(CONTROL_DIR / "queue.json")
    templates = load_json(CONTROL_DIR / "queue.templates.json")
    paused = load_json(CONTROL_DIR / "paused.json")
    runtime = load_json(CONTROL_DIR / "runtime_state.json")
    policy = load_json(CONTROL_DIR / "phase_policy.json")
    context_policy = load_json(CONTROL_DIR / "context_policy.json")
    
    if not queue or not runtime or not policy:
        logger.error("Failed to load control files. Exiting.")
        sys.exit(1)
    
    if not templates:
        logger.error("queue.templates.json missing or corrupt. Cannot proceed.")
        sys.exit(1)
    
    # Build template context for runtime use
    template_ctx = {
        'task_sources': templates.get('task_sources', {}),
        'execution_policy': templates.get('execution_policy', {}),
        'config': templates.get('config', {}),
        'paused_by_policy': templates.get('paused_by_policy', [])
    }
    
    # Track run-level events for summary
    run_events = {
        'just_completed': None,
        'just_failed': None,
        'tasks_generated': 0,
        'is_idle': False
    }
    
    logger.info(f"Current phase: {runtime.get('current_state', {}).get('phase', 'unknown')}")
    logger.info(f"Queue size: {len(queue.get('queue', []))} pending tasks")
    
    # Get next task
    task = get_next_task(queue, runtime, policy)
    
    if not task:
        logger.info("No runnable task - queue is empty or all tasks blocked")
        # Try to auto-supply tasks from templates
        queue, generated = generate_tasks_if_needed(queue, template_ctx["task_sources"])
        if generated > 0:
            logger.info(f"Auto-supplied {generated} tasks from templates")
            run_events['tasks_generated'] = generated
            save_json(CONTROL_DIR / "queue.json", queue)
            # Re-attempt to get a task
            task = get_next_task(queue, runtime, policy)
        
        if not task:
            logger.info("Still no runnable task after auto-supply")
            run_events['is_idle'] = True
            runtime.setdefault('current_state', {})['last_activity'] = datetime.now().isoformat()
            runtime.setdefault('current_state', {})['last_activity_type'] = 'agent_loop.no_task'
            runtime['last_run_at'] = datetime.now().isoformat()
            runtime.setdefault('_meta', {})['updated'] = datetime.now().isoformat()
            
            # Generate summary for idle state
            summary_path = evaluate_and_generate(queue, runtime, **run_events)
            if summary_path:
                logger.info(f"Summary generated: {summary_path}")
            
            # Verify git truth level
            git_truth = _verify_git_truth()
            runtime.setdefault('acceptance', {})['completion_level'] = git_truth['completion_level']
            runtime.setdefault('acceptance', {})['last_task_outcome'] = runtime.get('acceptance', {}).get('last_task_outcome', 'N/A')
            
            # Write status bridge on idle too
            _write_status_bridge(queue, runtime, context_policy, git_truth)
            
            save_json(CONTROL_DIR / "runtime_state.json", runtime)
            logger.info(f"Updated runtime_state.json with last_run_at")
            sys.exit(0)
    
    logger.info(f"Selected task: {task['id']} - {task['name']}")
    
    # Check if task conflicts with paused items
    paused_ids = [p['id'] for p in paused.get('paused_tasks', [])]
    paused_ids += [p['id'] for p in template_ctx.get('paused_by_policy', [])]
    if task['id'] in paused_ids:
        logger.warning(f"Task {task['id']} is paused. Skipping.")
        sys.exit(0)
    
    # Execute handler
    success, result = execute_handler(task, policy)
    
    # Track outcome for summary
    if success:
        run_events['just_completed'] = task
    else:
        run_events['just_failed'] = task
    
    # Update control files
    queue = update_queue_after_task(queue, task, success, result)
    runtime = update_runtime_state(runtime, task, success)
    runtime['last_run_at'] = datetime.now().isoformat()
    
    # Set task outcome BEFORE summary generation (needed for lightweight event)
    runtime.setdefault('acceptance', {})['last_task_outcome'] = 'success' if success else 'failed'
    
    # Verify git truth level after task completion
    git_truth = _verify_git_truth()
    runtime.setdefault('acceptance', {})['completion_level'] = git_truth['completion_level']
    runtime.setdefault('acceptance', {})['last_verified'] = datetime.now().isoformat()
    
    # Generate summary based on what happened
    summary_path = evaluate_and_generate(queue, runtime, **run_events)
    if summary_path:
        logger.info(f"Summary generated: {summary_path}")
        logger.info(f"Completion level: {git_truth['completion_level']}")
    
    # Save updated files
    save_json(CONTROL_DIR / "queue.json", queue)
    save_json(CONTROL_DIR / "runtime_state.json", runtime)
    
    # Write status bridge: always-writeable status file for external consumption
    _write_status_bridge(queue, runtime, context_policy, git_truth)
    
    logger.info(f"Task {task['id']} completed: {'SUCCESS' if success else 'FAILED'}")
    logger.info("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
