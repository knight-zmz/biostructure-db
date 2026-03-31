# Control Plane Status

**Updated**: 2026-03-31 14:51
**Mode**: manual trigger (audit_pm2_logs.completed)
**Phase**: P2_DATA_CONTENT (in_progress)
**Queue**: 4 pending, 61 completed, 4 failed
**Idle**: no
**Last Activity**: audit_pm2_logs.completed
**Last Summary**: batch_summary
**Next Action**: 审计 README 与 ops 文档一致性

## Recent
  ✅ PM2 日志异常巡检
  ✅ 验证 API 健康状态
  ✅ 验证 PM2 进程健康状态

## Read Policy
default: control/status.md
- status_query: [当前状态, status, 队列...] → control/status.md, control/runtime_state.json, control/queue.json
- detailed_summary: [详细总结, summary, 最近失败...] → control/status.md, control/reports/latest_summary.md
- handler_debug: [handler, 处理器, 脚本错误...] → control/status.md, control/logs/agent-loop.log
- schema_reference: [schema, 字段, 结构...] → control/README.md
- deploy_ops: [部署, deploy, 启动...] → ops/runbook.md
- project_overview: [项目状态, 阶段, 阻塞...] → ops/project_state.md

---
*Protocol: Status Query Protocol v1 | See latest_summary.md for full report.*