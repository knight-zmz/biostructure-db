# Runbook Index

Operational runbooks for biostructure-db.  
Sub-runbooks: `ops/runbooks/`

---

## Quick Start (已配置环境)

```bash
sudo systemctl start postgresql
sudo systemctl start redis
cd /var/www/myapp && pm2 start ecosystem.config.js && pm2 save
curl http://localhost:3000/api/health
```

Cold start (新服务器): → `ops/runbooks/cold-start.md`

---

## Runbook Index

| Runbook | 内容 |
|---------|------|
| [cold-start.md](runbooks/cold-start.md) | 新服务器首次启动 |
| [recovery.md](runbooks/recovery.md) | 失败恢复、回滚、故障排查 |
| [service-mgmt.md](runbooks/service-mgmt.md) | PostgreSQL / Redis / PM2 管理 |
| [db-ops.md](runbooks/db-ops.md) | 数据库初始化与日常维护 |
| [deploy.md](runbooks/deploy.md) | 手动部署、GitHub Actions、systemd |
| [logging.md](runbooks/logging.md) | PM2 / 系统 / Nginx 日志 |
| [backup.md](runbooks/backup.md) | 数据库备份与恢复 |
| [monitoring.md](runbooks/monitoring.md) | 监控、告警、健康检查 |
| [https-setup.md](runbooks/https-setup.md) | HTTPS 接入（备案后） |
| [control-plane.md](runbooks/control-plane.md) | OpenClaw 控制平面操作 |

---

## 常用命令速查

```bash
# 状态
pm2 status && pg_isready && redis-cli ping

# 重启
pm2 restart myapp && sudo systemctl restart postgresql

# 健康
curl http://localhost:3000/api/health | jq '.status'

# 日志
pm2 logs myapp --lines 20

# 磁盘/内存
df -h && free -h

# 端口
ss -tlnp | grep -E "3000|5432|6379|80"

# 控制平面
cat control/status.md
scripts/test-timer-toggle.sh status
```

---

## 安全

- `.env` 不提交（已在 .gitignore）
- 防火墙只开 80, 443, 22
- 定期 `sudo dnf update -y`
- 监控 `/var/log/secure`
