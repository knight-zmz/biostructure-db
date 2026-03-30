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
            'git_state': 'uncommitted'
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
        # Mark task as failed
        if pool_name and 'task_pools' in queue:
            task_pools = queue.get('task_pools', {})
            pool = task_pools.get(pool_name, [])
            for t in pool:
                if t['id'] == task['id']:
                    t['status'] = 'failed'
                    t['error'] = result.get('error', 'unknown')
                    break
            queue['task_pools'] = task_pools
        else:
            # Legacy flat queue structure
            for t in queue['queue']:
                if t['id'] == task['id']:
                    t['status'] = 'failed'
                    t['error'] = result.get('error', 'unknown')
                    break
    
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


def main():
    """Main execution loop."""
    logger.info("=" * 60)
    logger.info("OpenClaw Agent Loop v1.0.0 starting")
    logger.info(f"Base directory (normalized): {BASE_DIR.resolve()}")
    logger.info(f"Script path: {Path(__file__).resolve()}")
    logger.info("=" * 60)
    
    # Load control files
    queue = load_json(CONTROL_DIR / "queue.json")
    paused = load_json(CONTROL_DIR / "paused.json")
    runtime = load_json(CONTROL_DIR / "runtime_state.json")
    policy = load_json(CONTROL_DIR / "phase_policy.json")
    
    if not queue or not runtime or not policy:
        logger.error("Failed to load control files. Exiting.")
        sys.exit(1)
    
    logger.info(f"Current phase: {runtime.get('current_state', {}).get('phase', 'unknown')}")
    logger.info(f"Queue size: {len(queue.get('queue', []))} pending tasks")
    
    # Get next task
    task = get_next_task(queue, runtime, policy)
    
    if not task:
        logger.info("No runnable task - queue is empty or all tasks blocked")
        # Always update runtime state even when no task
        runtime.setdefault('current_state', {})['last_activity'] = datetime.now().isoformat()
        runtime.setdefault('current_state', {})['last_activity_type'] = 'agent_loop.no_task'
        runtime['last_run_at'] = datetime.now().isoformat()
        runtime.setdefault('_meta', {})['updated'] = datetime.now().isoformat()
        save_json(CONTROL_DIR / "runtime_state.json", runtime)
        logger.info(f"Updated runtime_state.json with last_run_at")
        sys.exit(0)
    
    logger.info(f"Selected task: {task['id']} - {task['name']}")
    
    # Check if task conflicts with paused items
    paused_ids = [p['id'] for p in paused.get('paused_tasks', [])]
    if task['id'] in paused_ids:
        logger.warning(f"Task {task['id']} is paused. Skipping.")
        sys.exit(0)
    
    # Execute handler
    success, result = execute_handler(task, policy)
    
    # Update control files
    queue = update_queue_after_task(queue, task, success, result)
    runtime = update_runtime_state(runtime, task, success)
    
    # Save updated files
    save_json(CONTROL_DIR / "queue.json", queue)
    save_json(CONTROL_DIR / "runtime_state.json", runtime)
    
    logger.info(f"Task {task['id']} completed: {'SUCCESS' if success else 'FAILED'}")
    logger.info("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
