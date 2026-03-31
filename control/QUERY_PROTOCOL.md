# Status Query Protocol v1

## 触发条件

当用户询问以下内容时执行此协议：
- "当前状态" / "status"
- "最近做了什么" / "有什么进展"
- "为什么静默" / "卡在哪"
- "队列情况" / "有没有任务"
- 任何对控制平面运行状态的直接询问

## 读取顺序（固定）

| 顺序 | 文件 | 用途 |
|------|------|------|
| 1 | `control/status.md` | 轻量状态概要 |
| 2 | `control/runtime_state.json` | 机器状态 |
| 3 | `control/queue.json` | 队列详情 |
| 4 | `control/reports/latest_summary.md` | 完整总结 |

**禁止**：先扫 logs、先自由叙述、先执行新任务再汇报。

## 输出模板

```
## 控制平面状态

**Phase**: {phase} ({phase_status})
**Queue**: {pending} pending / {completed} completed / {failed} failed
**Idle**: {yes/no} {if yes: idle N cycles}
**Last Activity**: {activity_type} at {time}
**Last Summary**: {reason}
**Next Action**: {next_action}

### Recent
{last 3 completed/failed tasks with ✅/❌}

### Notes
{only if: failures, phase boundary, or error accumulation}
```

## 判断规则

| 情况 | 处理 |
|------|------|
| status.md `Updated` 差 >30min | timer 未运行，提示用户 |
| `Idle: yes` | 报告空闲原因（queue 空 / cooldown） |
| `failed > 0` 且有新失败 | Notes 中列出 |
| `pending > 0` | 报告待处理数 |
| heartbeat 触发且无更新 | HEARTBEAT_OK |

## 不属于此协议

- 功能开发讨论
- 代码审查
- 部署操作
- 排障（先读 status.md 定位范围，再读 logs）
