# 完成状态分层规范 v1.0

**生效日期**: 2026-03-30  
**适用范围**: OpenClaw Control Plane v1.2+

---

## 状态定义

| 状态 | 定义 | 判断标准 |
|------|------|----------|
| **implemented** | 代码/配置已修改 | 文件已修改并保存 |
| **verified** | 功能已验证通过 | handler 执行成功 + 日志记录 + runtime_state 更新 |
| **committed** | 变更已提交到 Git | git commit 完成 |
| **done** | 已完成（可交付） | verified + committed |

---

## 状态流转

```
implemented → verified → committed → done
     ↓            ↓           ↓
  (未验证)    (未提交)    (未推送)
```

---

## 使用规则

1. **只有 `done` 才能称为"已完成"**
   - 不要将 `implemented` 称为"已完成"
   - 不要将 `verified` 称为"已完成"（如果还未 committed）
   - 不要将 `committed` 称为"已完成"（如果还未 verified）

2. **汇报时必须明确状态**
   - ✅ done: "已完成并提交"
   - 🟡 verified: "已验证，待提交"
   - 🟠 implemented: "已实现，待验证"
   - ⏳ pending: "待执行"

3. **queue.json 中的任务状态**
   - `pending`: 待执行
   - `completed`: 已执行（需要检查是否 verified + committed）

4. **防误报机制**
   - 在汇报"已完成"前，必须检查：
     - [ ] handler 执行成功（exit_code=0）
     - [ ] runtime_state.json 已更新
     - [ ] agent-loop.log 有执行记录
     - [ ] git commit 已完成
     - [ ] git push 已完成（如适用）

---

## 示例

### 正确表述
- "supply-001 已 done（verified + committed）"
- "supply-003 已 verified，待 commit"
- "analyze-001 已 implemented，待 verify"

### 错误表述
- "已完成"（未说明是哪个状态层级）
- "已激活"（模糊表述）
- "可持续自治运行"（未经验证的断言）

---

## 审计检查清单

在宣布"已完成"前，必须完成以下检查：

```bash
# 1. 检查 handler 执行
tail -n 20 control/logs/agent-loop.log | grep "completed: SUCCESS"

# 2. 检查 runtime_state 更新
python3 -c "import json; d=json.load(open('control/runtime_state.json')); print(d['current_state']['last_activity_type'])"

# 3. 检查 git 状态
git status --short
git log --oneline -1

# 4. 检查远端同步
git status | grep "Your branch is up to date"
```

---

**版本**: v1.0  
**维护者**: OpenClaw Control Plane
