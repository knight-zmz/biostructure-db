# Git Boundary Rules

## MUST push (code/config)

| Category | Files |
|---|---|
| Agent loop | `control/agent_loop.py`, `control/summary_generator.py` |
| Handlers | `control/handlers/*.py` |
| Task templates | `control/queue.json` → `task_sources` / `task_pools` 定义 |
| Phase policy | `control/phase_policy.json`, `control/paused.json` |
| Control docs | `control/README.md`, `control/*.md` |
| Systemd | `/etc/systemd/system/openclaw-agent*.service`, `*.timer` |
| Ops docs | `ops/project_state.md`, `ops/backlog.md`, `ops/runbook.md` |
| Scripts | `scripts/*.sh` |
| Gitignore | `.gitignore` |

## MUST NOT push (runtime state)

| Category | Files | Reason |
|---|---|---|
| Runtime state | `control/runtime_state.json` | 每次 loop 更新 |
| Queue runtime | `control/queue.json` → `completed` 数组 | 执行历史，频繁变更 |
| Reports | `control/reports/` | 自动生成 |
| Audits | `control/audits/*.json` | 每次审计重新生成 |
| Logs | `control/logs/` | 运行日志 |
| Cache | `control/__pycache__/` | Python 编译产物 |

## Gitignore

```
control/reports/
control/audits/*.json
control/logs/
control/__pycache__/
*.pyc
.env
node_modules/
```
