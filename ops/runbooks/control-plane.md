# Control Plane — OpenClaw 控制平面

## 控制文件

| 文件 | 用途 |
|------|------|
| `control/queue.json` | 任务队列 |
| `control/runtime_state.json` | 运行时状态 |
| `control/paused.json` | 暂停任务 |
| `control/phase_policy.json` | 阶段策略 |
| `control/status.md` | 状态桥（外部消费） |

详细 schema: `control/README.md`

## 手动执行

```bash
cd /home/admin/biostructure-db
python3 control/agent_loop.py
tail -50 control/logs/agent-loop.log
cat control/status.md
```

## Timer 管理

```bash
scripts/test-timer-toggle.sh [on|off|status]
systemctl list-units --type=timer | grep openclaw
```

当前状态（2026-03-31）：
- `openclaw-agent.timer`: disabled（生产 timer，默认关闭）
- `openclaw-agent-test.timer`: enabled（测试 timer，20 分钟间隔，评估中）

## 相关文档

- `control/README.md` — 静态 schema 与结构
- `control/GIT_BOUNDARY.md` — Git 推送边界
- `control/SUMMARY_POLICY.md` — 总结策略
- `control/QUERY_PROTOCOL.md` — 状态查询协议

## 运行模式

HTTP 开发模式（备案期间）。
- IP 直连：http://101.200.53.98
- 域名：暂停（备案限制）
