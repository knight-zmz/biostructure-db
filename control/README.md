# OpenClaw Control Plane v1.3

Static specification for the control plane structure, schemas, and interfaces.

Related docs: `GIT_BOUNDARY.md` | `SUMMARY_POLICY.md` | `QUERY_PROTOCOL.md` | `STATUS_LAYERS.md`

---

## 1. Canonical Paths

All paths relative to project root (`/home/admin/biostructure-db`).

| File | Path | Purpose |
|------|------|---------|
| `queue.json` | `control/queue.json` | Task queue |
| `runtime_state.json` | `control/runtime_state.json` | Runtime state & phase progress |
| `paused.json` | `control/paused.json` | Paused tasks |
| `phase_policy.json` | `control/phase_policy.json` | Phase execution policies |
| `agent_loop.py` | `control/agent_loop.py` | Main execution loop |
| `summary_generator.py` | `control/summary_generator.py` | Summary generation |
| `status.md` | `control/status.md` | Status bridge (external consumption) |
| `handlers/` | `control/handlers/` | Handler scripts (`.py` only) |
| `reports/` | `control/reports/` | Summary reports output |
| `logs/` | `control/logs/` | Execution logs |

---

## 2. queue.json Schema

Multi-pool structure with task sources and execution policy.

```json
{
  "_meta": {
    "version": "1.3.0",
    "updated": "ISO8601",
    "task_supply_system": "v1.3",
    "generation_log": {
      "source_name": "ISO8601"
    }
  },
  "current_phase": "P2_DATA_CONTENT",

  "task_pools": {
    "runnable_now": [
      {
        "id": "auto-template-id",
        "name": "task_name",
        "title": "Human-readable title",
        "source": "source_name",
        "phase": "P2",
        "priority": 5,
        "status": "pending",
        "handler": "handler_name",
        "boundary": "read_only_audit",
        "done_when": "Completion criteria",
        "auto_execute": true,
        "risk_level": "low",
        "generated_at": "ISO8601",
        "template_id": "template-id"
      }
    ],
    "analyze_first": [],
    "waiting_user": [],
    "paused_by_policy": [
      {
        "id": "task-id",
        "name": "name",
        "reason": "why paused",
        "resume_condition": "condition"
      }
    ]
  },

  "completed": [
    {
      "id": "task-id",
      "name": "task_name",
      "phase": "P2",
      "status": "completed|failed",
      "completed_at": "ISO8601",
      "result": {},
      "verification": {
        "handler_success": true,
        "log_recorded": true,
        "runtime_state_updated": true,
        "verified": true
      },
      "git_state": "uncommitted",
      "lifecycle_state": "verified|implemented"
    }
  ],

  "task_sources": {
    "source_name": {
      "description": "Source purpose",
      "auto_generate": true,
      "generation_frequency_hours": 24,
      "cooldown_hours": 1,
      "templates": [
        {
          "template_id": "template-id",
          "name": "task_name",
          "title": "Title",
          "phase": "P2",
          "priority": 5,
          "target_pool": "runnable_now",
          "handler": "handler_name",
          "boundary": "read_only_audit",
          "done_when": "criteria",
          "risk_level": "low"
        }
      ]
    }
  },

  "execution_policy": {
    "default_behavior": "auto_execute_runnable_now",
    "pool_execution_order": ["runnable_now", "analyze_first", "waiting_user"],
    "stop_boundaries": ["phase_transition", "error_threshold_exceeded", "user_interrupt"]
  },

  "config": {
    "max_queue_size": 20,
    "auto_advance": true,
    "stop_on_error": true,
    "timer_enabled": false,
    "task_supply_enabled": true
  }
}
```

### Pool priority

`runnable_now` → `analyze_first` → `waiting_user`. Tasks with `auto_execute: true` run first, sorted by `priority` (lower = higher priority).

### Task lifecycle

```
pending → [handler executes] → completed|failed → completed[] with verification + lifecycle_state
```

---

## 3. runtime_state.json Schema

```json
{
  "_meta": { "updated": "ISO8601" },
  "current_state": {
    "phase": "P2_DATA_CONTENT",
    "phase_status": "in_progress|completed|blocked",
    "phase_started": "ISO8601",
    "last_activity": "ISO8601",
    "last_activity_type": "handler_name.completed|agent_loop.no_task"
  },
  "phase_progress": {
    "P1_ENGINEERING": { "status": "...", "completed_tasks": [] },
    "P2_DATA_CONTENT": { "status": "...", "completed_tasks": [], "pending_tasks": [] },
    "P3_MAINTENANCE": { "status": "not_started", "tasks": [] }
  },
  "next_default_action": {
    "action": "none|handler_name",
    "description": "...",
    "auto_execute": false
  },
  "stop_conditions": {
    "phase_boundary": true,
    "error_threshold": 3,
    "user_interrupt": true
  },
  "system_health": {
    "api_status": "healthy|degraded|down",
    "database_status": "connected|disconnected",
    "pm2_status": "online|offline"
  },
  "summary": {
    "last_summary_at": "ISO8601|null",
    "last_summary_reason": "string",
    "idle_cycles": 0,
    "reports_generated": 0,
    "daily_digest_last_date": "YYYY-MM-DD",
    "completed_since_last_summary": 0
  },
  "last_run_at": "ISO8601|null",
  "error_count": 0
}
```

---

## 4. paused.json Schema

```json
{
  "paused_tasks": [
    {
      "id": "unique-id",
      "name": "Human-readable",
      "reason": "why paused",
      "paused_at": "ISO8601",
      "resume_condition": "condition"
    }
  ]
}
```

---

## 5. phase_policy.json Schema

```json
{
  "phase_definitions": {
    "P0_COLD_START": { "status": "completed" },
    "P1_ENGINEERING": { "status": "..." },
    "P2_DATA_CONTENT": { "status": "in_progress" },
    "P3_MAINTENANCE": { "status": "not_started" }
  },
  "execution_rules": {
    "default_behavior": "auto_execute_within_phase",
    "stop_boundaries": ["phase_transition", "error_threshold_exceeded", "user_interrupt"],
    "error_handling": { "max_retries": 3, "stop_on_consecutive_errors": 3 }
  },
  "handler_registry": {
    "handler_name": { "timeout_seconds": 300 }
  }
}
```

---

## 6. Handler Interface

**Location**: `control/handlers/<name>.py`

- Executable Python 3 script
- JSON to stdout on success
- Exit 0 on success, non-zero on failure
- CWD-independent

```python
#!/usr/bin/env python3
import json, sys
def main():
    print(json.dumps({"handler": "name", "status": "success"}))
    sys.exit(0)
if __name__ == '__main__': main()
```

---

## 7. Execution Flow

1. Load `queue.json`, `runtime_state.json`, `paused.json`, `phase_policy.json`
2. Find next task in pool priority order (`runnable_now` → `analyze_first`)
3. Skip if paused
4. Execute handler
5. Update queue (→ completed with verification)
6. Update runtime_state
7. Generate summary if triggered
8. Write `status.md` bridge
9. Save all files

**Empty queue**: auto-supply from task_sources → re-check → if still empty, record idle.

---

## 8. Systemd Units

| Unit | Type | Schedule | Default |
|------|------|----------|---------|
| `openclaw-agent.service` | oneshot | — | disabled |
| `openclaw-agent.timer` | timer | 15min (8-20h) | disabled |
| `openclaw-agent-test.timer` | timer | 20min | disabled |

Toggle: `scripts/test-timer-toggle.sh [on|off|status]`
