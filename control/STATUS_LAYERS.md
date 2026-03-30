# 完成状态分层规范 v1.2

**生效日期**: 2026-03-30  
**适用范围**: OpenClaw Control Plane v1.2+

---

## 机器可读状态字段

每个 completed/failed 任务包含以下字段：

```json
{
  "status": "completed",
  "completed_at": "2026-03-31T00:06:04.357",
  "verification": {
    "handler_success": true,
    "log_recorded": true,
    "runtime_state_updated": true,
    "verified": true
  },
  "git_state": "uncommitted",
  "lifecycle_state": "verified"
}
```

## lifecycle_state 派生规则

由 agent_loop 自动计算，**只读字段**：

| lifecycle_state | 计算条件 |
|----------------|---------|
| `pending` | 任务尚未执行（在 pool 中） |
| `implemented` | handler 执行过，但 `verification.verified = false`（失败） |
| `verified` | `verification.verified = true` AND `git_state = "uncommitted"` |
| `committed` | `git_state = "committed"`（需外部 git workflow 更新） |
| `done` | `verification.verified = true` AND `git_state in ("committed", "pushed")` |

## git_state 值

| 值 | 含义 | 设置方式 |
|----|------|---------|
| `uncommitted` | handler 完成但变更未提交 | agent_loop 自动设置 |
| `committed` | 已 git commit | 外部 git workflow |
| `pushed` | 已 git push | 外部 git workflow |

## 判断 "done" 的机器方法

```python
v = task.get('verification', {})
gs = task.get('git_state', 'uncommitted')
is_done = v.get('verified', False) and gs in ('committed', 'pushed')
```

## 快速审计

```bash
python3 -c "
import json
with open('control/queue.json') as f:
    d = json.load(f)
for t in d['completed'][-5:]:
    lc = t.get('lifecycle_state', '?')
    gs = t.get('git_state', '?')
    print(f\"{t['id']}: lifecycle={lc}, git={gs}\")
"
```

---

**版本**: v1.2  
**维护者**: OpenClaw Control Plane
