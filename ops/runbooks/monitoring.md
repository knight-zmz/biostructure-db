# Monitoring — 监控与告警

## 健康检查

```bash
bash /home/admin/biostructure-db/scripts/health-check.sh
curl http://localhost:3000/api/health | jq
```

## 监控脚本

**脚本**: `scripts/monitor.sh`  
**频率**: 每 10 分钟  
**日志**: `/home/admin/logs/metrics.log`, `/home/admin/logs/alerts.log`

```bash
tail -10 /home/admin/logs/metrics.log
cat /home/admin/logs/alerts.log
```

## 告警阈值

| 指标 | 阈值 | 级别 |
|------|------|------|
| CPU 1min load | > 4 | ⚠️ |
| 内存使用率 | > 85% | ⚠️ |
| 磁盘使用率 | > 90% | ⚠️ |
| Nginx | inactive | ❌ |
| PostgreSQL | inactive | ❌ |
| PM2 应用 | offline | ❌ |
| API 状态 | != 200 | ❌ |

## ECS 监控（补充）

阿里云控制台 → ECS → 实例 → 监控图表（CPU/内存/磁盘/网络）
