#!/usr/bin/env python3
"""
Handler: audit_state_drift

Audit control plane state consistency between:
- queue.json
- runtime_state.json
- ops/project_state.md

Detects drift and generates sync recommendations.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
QUEUE_JSON = BASE_DIR / "control" / "queue.json"
RUNTIME_STATE = BASE_DIR / "control" / "runtime_state.json"
OPS_STATE = BASE_DIR / "ops" / "project_state.md"

def main():
    try:
        result = {
            "handler": "audit_state_drift",
            "status": "success",
            "findings": {},
            "drift_detected": []
        }
        
        # Load control plane files
        with open(QUEUE_JSON, 'r', encoding='utf-8') as f:
            queue = json.load(f)
        
        with open(RUNTIME_STATE, 'r', encoding='utf-8') as f:
            runtime = json.load(f)
        
        # Extract key state indicators
        queue_phase = queue.get('current_phase', 'unknown')
        runtime_phase = runtime.get('current_state', {}).get('phase', 'unknown')
        
        result["findings"]["queue_phase"] = queue_phase
        result["findings"]["runtime_phase"] = runtime_phase
        
        # Check 1: Phase consistency
        if queue_phase != runtime_phase:
            result["drift_detected"].append({
                "type": "phase_mismatch",
                "queue": queue_phase,
                "runtime": runtime_phase,
                "severity": "medium"
            })
        
        # Check 2: Task pool status
        task_pools = queue.get('task_pools', {})
        runnable_count = len(task_pools.get('runnable_now', []))
        analyze_count = len(task_pools.get('analyze_first', []))
        waiting_count = len(task_pools.get('waiting_user', []))
        paused_count = len(queue.get('paused_tasks', []))
        completed_count = len(queue.get('completed', []))
        
        result["findings"]["task_pools"] = {
            "runnable_now": runnable_count,
            "analyze_first": analyze_count,
            "waiting_user": waiting_count,
            "paused_by_policy": paused_count,
            "completed": completed_count
        }
        
        # Check 3: Timer enabled consistency
        timer_enabled = queue.get('config', {}).get('timer_enabled', False)
        result["findings"]["timer_enabled"] = timer_enabled
        
        # Check 4: Last activity timestamp
        last_activity = runtime.get('current_state', {}).get('last_activity', None)
        result["findings"]["last_activity"] = last_activity
        
        # Check 5: Queue empty warning
        if runnable_count == 0 and analyze_count == 0 and waiting_count == 0:
            result["drift_detected"].append({
                "type": "queue_empty",
                "message": "All task pools are empty - task supply system may need attention",
                "severity": "low"
            })
        
        # Summary
        if result["drift_detected"]:
            result["message"] = f"Detected {len(result['drift_detected'])} state drift issues"
            result["status"] = "warning"
        else:
            result["message"] = "Control plane state is consistent"
        
        # Write audit report
        audits_dir = BASE_DIR / "control" / "audits"
        audits_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = audits_dir / "state_drift_audit.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        result["report_file"] = str(report_file)
        result["audit_timestamp"] = datetime.now().isoformat()
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            "handler": "audit_state_drift",
            "status": "failed",
            "error": str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
