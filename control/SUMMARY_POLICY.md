# Summary Policy

## Entry Points

| File | 用途 | 更新频率 |
|---|---|---|
| `control/status.md` | 轻量状态（推送桥入口） | 每次 loop |
| `control/reports/latest_summary.md` | 完整总结报告 | 有触发事件时 |

## Default Read Context

只读以下文件生成状态回答：

1. `control/status.md`
2. `control/runtime_state.json`
3. `control/queue.json`
4. `control/reports/latest_summary.md`

## NOT Default

- `control/reports/summary_*.md` — 仅调试
- `control/logs/agent-loop.log` — 仅排障
- `control/audits/*.json` — 仅分析

## Trigger Rules

| 触发器 | 条件 | 抑制 |
|---|---|---|
| `daily_digest` | 每天首次 ≥8AM | 每天一次 |
| `task_failed` | 任务失败 | 30min 冷却 |
| `queue_drained` | 队列清空 | 30min 冷却 |
| `batch_summary` | 每完成 3 个任务 | 计数器归零 |
| `supply_summary` | auto-supply 后 | 30min 冷却 |
| `idle_cycles_exceeded` | 连续空跑 8 次 | 30min 冷却 |

## status.md Format

```
# Control Plane Status
**Updated**: {timestamp}
**Phase**: {phase} ({phase_status})
**Queue**: {N} pending, {N} completed, {N} failed
**Idle**: {yes/no} {N cycles}
**Last Activity**: {activity_type}
**Last Summary**: {reason}
**Next Action**: {description}

## Recent
{last 3 tasks with ✅/❌}
```
