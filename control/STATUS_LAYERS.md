# 完成状态分层规范 v1.1

**生效日期**: 2026-03-30  
**适用范围**: OpenClaw Control Plane v1.2+  
**变更**: v1.1 - 落地到控制平面任务对象字段

---

## 机器可读字段结构

每个 completed 任务包含以下字段：

```json
{
  "status": "completed",
  "completed_at": "2026-03-30T23:55:00.000000",
  "verification": {
    "handler_success": true,
    "log_recorded": true,
    "runtime_state_updated": true,
    "verified": true
  },
  "git_state": "uncommitted"
}
```

## 状态定义（基于字段）

| 状态 | 机器判断 | 手动检查 |
|------|----------|----------|
| **pending** | `status != "completed"` | 任务在 pool 中等待 |
| **implemented** | handler 执行但 `verification.verified = false` | 文件已修改 |
| **verified** | `verification.verified = true` AND `git_state = "uncommitted"` | handler 成功 + 日志记录 |
| **committed** | `git_state = "committed"` | git commit 完成 |
| **done** | `verification.verified = true` AND `git_state = "committed"` | 完全完成 |

## git_state 值

| 值 | 含义 | 触发方式 |
|----|------|----------|
| `uncommitted` | handler 已完成但变更未提交到 Git | agent_loop 自动设置 |
| `committed` | 变更已提交到 Git | 外部 git workflow 设置 |
| `pushed` | 已推送到远端 | 外部 git workflow 设置 |

## 状态流转（代码级）

```
1. agent_loop 创建 completed 任务
   → verification.verified = true (handler_success + log_recorded + runtime_state_updated)
   → git_state = "uncommitted"

2. 外部 git workflow:
   git add + git commit → git_state = "committed"
   git push → git_state = "pushed"
```

## 防误报规则

1. **只有当 `verification.verified = true` AND `git_state = "committed"` 才能称为 done**
2. 不要把 `verification.verified = true` + `git_state = "uncommitted"` 称为 done
3. 在汇报前检查：`python3 -c "import json; ..."` 读取 verification 对象

---

## 审计检查清单

```bash
# 检查特定任务的 verification 和 git_state
python3 -c "
import json
with open('control/queue.json') as f:
    d = json.load(f)
for t in d.get('completed', [])[-5:]:
    v = t.get('verification', {})
    gs = t.get('git_state', 'uncommitted')
    verified = v.get('verified', False)
    done = verified and gs in ('committed', 'pushed')
    print(f'{t[\"id\"]}: verified={verified}, git_state={gs}, done={done}')
"
```

---

**版本**: v1.1  
**维护者**: OpenClaw Control Plane
