# OpenClaw Control Plane v1.2 - Task Supply System

**Version**: 1.2.0  
**Frozen**: 2026-03-30  
**Project**: biostructure-db  
**Feature**: Task Supply System v1.2 - Multi-pool queue with auto-generated tasks

---

## 1. Canonical Paths

All paths are resolved relative to the project root (`/home/admin/biostructure-db`).

| File | Canonical Path | Purpose |
|------|----------------|---------|
| `queue.json` | `control/queue.json` | Task queue (pending/completed) |
| `runtime_state.json` | `control/runtime_state.json` | Runtime state & phase progress |
| `paused.json` | `control/paused.json` | Paused tasks (ICP filing, etc.) |
| `phase_policy.json` | `control/phase_policy.json` | Phase execution policies |
| `agent_loop.py` | `control/agent_loop.py` | Main execution loop |
| `agent-loop.log` | `control/logs/agent-loop.log` | Execution log |
| `handlers/` | `control/handlers/` | Handler scripts (`.py` only) |

**Handler Type**: `.py` (Python 3) — `.sh` handlers are deprecated and removed.

---

## 2. queue.json Schema

```json
{
  "_meta": {
    "description": "OpenClaw Control Plane - Task Queue",
    "version": "1.0.0",
    "updated": "ISO8601 timestamp"
  },
  "current_phase": "P2_DATA_CONTENT",
  "queue": [
    {
      "id": "unique-task-id",
      "name": "task_name",
      "description": "Human-readable description",
      "phase": "P2",
      "priority": 1,
      "status": "pending|blocked|failed",
      "handler": "handler_name (matches file in handlers/)",
      "created": "ISO8601 timestamp",
      "depends_on": ["other-task-id"],  // optional
      "error": "error message"  // only if failed
    }
  ],
  "completed": [
    {
      "id": "unique-task-id",
      "name": "task_name",
      "description": "...",
      "phase": "P2",
      "priority": 1,
      "status": "completed",
      "handler": "handler_name",
      "created": "ISO8601 timestamp",
      "completed_at": "ISO8601 timestamp",
      "result": { ... }  // handler output
    }
  ],
  "config": {
    "max_queue_size": 10,
    "auto_advance": true,
    "stop_on_error": true
  }
}
```

**Key Fields**:
- `queue`: Array of pending tasks (sorted by priority)
- `completed`: Array of completed tasks (append-only)
- `current_phase`: Current active phase identifier

---

## 3. runtime_state.json Schema

```json
{
  "_meta": {
    "updated": "ISO8601 timestamp"
  },
  "current_state": {
    "phase": "P2_DATA_CONTENT",
    "phase_status": "in_progress|completed|blocked",
    "phase_started": "ISO8601 timestamp",
    "last_activity": "ISO8601 timestamp",
    "last_activity_type": "handler_name.completed|agent_loop.no_task"
  },
  "phase_progress": {
    "P1_ENGINEERING": {
      "status": "completed|deployed_pending_verification|in_progress",
      "completed_tasks": ["task1", "task2"],
      "verification_tasks": ["verify1"],
      "started": "ISO8601 timestamp"
    },
    "P2_DATA_CONTENT": {
      "status": "in_progress|not_started",
      "completed_tasks": ["task1"],
      "pending_tasks": [],
      "started": "ISO8601 timestamp"
    },
    "P3_MAINTENANCE": {
      "status": "not_started",
      "tasks": ["task1", "task2"]
    }
  },
  "next_default_action": {
    "action": "handler_name",
    "description": "...",
    "auto_execute": true,
    "requires_user_confirm": false
  },
  "stop_conditions": {
    "phase_boundary": true,
    "paused_task_conflict": true,
    "error_threshold": 3,
    "user_interrupt": true
  },
  "system_health": {
    "last_check": "ISO8601 timestamp",
    "api_status": "healthy|degraded|down",
    "database_status": "connected|disconnected",
    "pm2_status": "online|offline",
    "backup_status": "configured|pending",
    "monitoring_status": "configured|pending"
  },
  "last_run_at": "ISO8601 timestamp|null",
  "error_count": 0
}
```

**Key Fields**:
- `current_state.phase`: Current active phase
- `current_state.last_activity`: Last loop execution timestamp
- `current_state.last_activity_type`: Type of last activity
- `last_run_at`: Last loop run timestamp (updated every run)
- `error_count`: Consecutive error counter (reset on success)

---

## 4. paused.json Schema

```json
{
  "_meta": {
    "description": "OpenClaw Control Plane - Paused Tasks",
    "version": "1.0.0",
    "updated": "ISO8601 timestamp"
  },
  "paused_tasks": [
    {
      "id": "unique-paused-id",
      "name": "Human-readable name",
      "reason": "Why this task is paused",
      "paused_at": "ISO8601 timestamp",
      "paused_by": "user_decision|agent_wait_decision",
      "resume_condition": "Condition to resume (e.g., 'ICP filing completed')",
      "resume_action": "What to do when resumed",
      "related_files": ["ops/runbook.md#section"],
      "priority_on_resume": "high|medium|low"
    }
  ],
  "config": {
    "review_paused_every": "7d",
    "notify_on_resume_condition_met": true
  }
}
```

**Current Paused Tasks**:
1. `https-certificate` - HTTPS/SSL (ICP filing restriction)
2. `domain-access` - jlupdb.me domain (ICP filing restriction)
3. `large-scale-import` - Large PDB import (awaiting user decision)

---

## 5. phase_policy.json Schema

```json
{
  "_meta": {
    "description": "OpenClaw Control Plane - Phase Execution Policy",
    "version": "1.0.0",
    "updated": "ISO8601 timestamp"
  },
  "phase_definitions": {
    "P0_COLD_START": {
      "description": "...",
      "status": "completed|in_progress|not_started",
      "completed_at": "ISO8601 timestamp|null",
      "auto_advance": true|false,
      "must_stop_on_complete": true|false,
      "requires_user_confirm_next": true|false
    },
    "P1_ENGINEERING": { ... },
    "P2_DATA_CONTENT": { ... },
    "P3_MAINTENANCE": { ... }
  },
  "execution_rules": {
    "default_behavior": "auto_execute_within_phase",
    "stop_boundaries": [
      "phase_transition",
      "paused_task_conflict",
      "error_threshold_exceeded",
      "user_interrupt"
    ],
    "error_handling": {
      "max_retries": 3,
      "retry_delay_seconds": 60,
      "stop_on_consecutive_errors": 3
    },
    "logging": {
      "log_every_action": true,
      "log_to": "control/logs/agent-loop.log",
      "include_timestamps": true,
      "include_state_changes": true
    }
  },
  "handler_registry": {
    "handler_name": {
      "description": "...",
      "phase": "P2",
      "timeout_seconds": 300,
      "retry_on_network_error": true
    }
  }
}
```

---

## 6. Handler Interface

**Location**: `control/handlers/<handler_name>.py`

**Requirements**:
- Must be executable Python 3 script
- Must output JSON to stdout on success
- Must exit with code 0 on success, non-zero on failure
- Must not depend on current working directory

**Minimal Handler Template**:
```python
#!/usr/bin/env python3
import json
import sys

def main():
    result = {
        "handler": "handler_name",
        "status": "success",
        "message": "Description of what was done"
    }
    print(json.dumps(result))
    sys.exit(0)

if __name__ == '__main__':
    main()
```

---

## 7. agent_loop.py Execution Flow

1. Load all 4 JSON control files
2. Get next pending task (by priority, respecting dependencies)
3. Check if task is paused → skip if so
4. Execute handler (`control/handlers/<handler>.py`)
5. Update queue (move task to completed or mark failed)
6. Update runtime_state (last_activity, last_run_at)
7. Write log entry
8. Exit (0 on success, 1 on failure)

**No Task Case**:
- Log "No runnable task"
- Update runtime_state.last_run_at
- Exit 0

---

## 8. Systemd Integration

**Service**: `systemd/openclaw-agent.service`
- Type: oneshot
- WorkingDirectory: `/home/admin/biostructure-db`
- ExecStart: `/usr/bin/python3 /home/admin/biostructure-db/control/agent_loop.py`

### Timer Dual Mode

| Mode | Timer File | Schedule | Use Case |
|------|-----------|----------|----------|
| **Production** | `openclaw-agent.timer` | Every 15 min (8:00-20:00) | Daily autonomous operation |
| **Test** | `openclaw-agent-test.timer` | Every 2 min (all day) | Session-level verification |

**Switch Modes**:
```bash
# Check current status
./scripts/timer-toggle.sh status

# Switch to production
./scripts/timer-toggle.sh prod

# Switch to test (for quick verification)
./scripts/timer-toggle.sh test
```

**Deploy Sequence**:
```bash
sudo cp systemd/openclaw-agent.* /etc/systemd/system/
sudo cp systemd/openclaw-agent-test.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable openclaw-agent.timer
sudo systemctl start openclaw-agent.timer
```

---

## 9. Task Supply System v1.2

The control plane now features an autonomous task supply system that continuously generates and manages tasks.

### Task Pools

| Pool | Purpose | Auto-execute |
|------|---------|--------------|
| `runnable_now` | Ready-to-execute tasks | Yes |
| `analyze_first` | Tasks requiring analysis before action | No |
| `waiting_user` | Tasks awaiting user decision | No |
| `paused_by_policy` | Tasks paused by policy boundaries | No |

### Task Sources

| Source | Description | Frequency |
|--------|-------------|-----------|
| `repo_audit_tasks` | Code/docs/schema consistency audits | Every 7 days |
| `log_triage_tasks` | PM2/app/systemd log anomaly detection | Every 24 hours |
| `drift_sync_tasks` | State consistency between control plane components | Every 7 days |
| `roadmap_tasks` | Feature enhancements and content expansion | On demand |

### Execution Flow

1. Agent loop checks `runnable_now` pool first
2. Executes tasks with `auto_execute: true` in priority order
3. Moves completed tasks to `completed` array
4. Falls back to `analyze_first` if `runnable_now` is empty
5. Respects `stop_boundaries` and `error_handling` policies

---

**Status**: v1.2 Task Supply System Active (2026-03-30)
