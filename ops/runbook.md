# 📖 Runbook - 运维操作手册

**生成时间**: 2026-03-29 22:56 CST  
**更新时间**: 2026-03-30 12:47 CST  
**项目**: biostructure-db  
**版本**: 1.0.0

---

## 1. 快速启动 (冷启动后)

### 1.1 首次启动 (新服务器)

```bash
# 1. 确认依赖已安装
which psql redis-cli pm2

# 2. 配置 PostgreSQL 认证 (首次启动必需)
cd /var/www/myapp
sudo bash scripts/configure-pg_hba.sh

# 3. 启动数据库
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 4. 初始化数据库
bash scripts/init-db.sh

# 5. 启动 Redis
sudo systemctl start redis
sudo systemctl enable redis

# 6. 启动应用
cd /var/www/myapp
pm2 start ecosystem.config.js
pm2 save
pm2 startup

# 7. 验证
curl http://localhost:3000/api/health
```

### 1.2 常规启动 (已配置环境)

```bash
# 1. 启动数据库
sudo systemctl start postgresql

# 2. 启动 Redis
sudo systemctl start redis

# 3. 启动应用
cd /var/www/myapp
pm2 start ecosystem.config.js
pm2 save

# 4. 验证
curl http://localhost:3000/api/health
```

---

## 3. 失败恢复与回滚

### 3.1 应用启动失败

**症状**: `pm2 status` 显示 `errored` 或 `stopped`

**诊断步骤**:
```bash
# 1. 查看日志
pm2 logs myapp --lines 50

# 2. 检查端口占用
lsof -i :3000

# 3. 检查依赖
cd /var/www/myapp && npm ls --depth=0

# 4. 手动启动测试
node src/app.js
```

**恢复步骤**:
```bash
# 1. 停止失败进程
pm2 stop myapp

# 2. 重新安装依赖
cd /var/www/myapp
npm install --production

# 3. 检查 .env 配置
cat .env

# 4. 重启应用
pm2 start ecosystem.config.js
pm2 logs myapp --lines 20
```

---

### 3.2 数据库连接失败

**症状**: `/api/health` 返回 `"database": "disconnected"`

**诊断步骤**:
```bash
# 1. 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 2. 检查监听端口
ss -tlnp | grep 5432

# 3. 测试连接
psql -U myapp_user -h 127.0.0.1 -d myapp -c "SELECT 1"
```

**恢复步骤**:
```bash
# 1. 重启 PostgreSQL
sudo systemctl restart postgresql

# 2. 检查 pg_hba.conf
sudo cat /var/lib/pgsql/data/pg_hba.conf | grep -v "^#"

# 3. 重新初始化 (如需要)
bash scripts/init-db.sh
```

---

### 3.3 GitHub Actions 部署失败

**症状**: Workflow 显示红色 ❌

**诊断步骤**:
1. 访问 https://github.com/knight-zmz/biostructure-db/actions
2. 点击失败的 workflow run
3. 查看失败步骤日志

**常见问题**:

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| SSH 连接失败 | Secrets 配置错误 | 检查 `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY` |
| PM2 重启失败 | 进程名不匹配 | 确认 `pm2 restart myapp` 中的名称 |
| 权限错误 | SSH 密钥权限 | 验证密钥格式和公钥已添加到 authorized_keys |

**手动回滚**:
```bash
# 1. 查看 Git 历史
cd /var/www/myapp
git log --oneline -5

# 2. 回滚到上一版本
git reset --hard <上一版本 commit>

# 3. 重新安装依赖
npm install --production

# 4. 重启应用
pm2 restart myapp
```

---

### 3.4 配置错误恢复

**症状**: 应用启动后立即崩溃

**诊断步骤**:
```bash
# 1. 查看 PM2 日志
pm2 logs myapp --lines 30

# 2. 检查 .env 文件
cat /var/www/myapp/.env

# 3. 验证环境变量
node -e "require('dotenv').config(); console.log(process.env.DB_PASSWORD ? 'DB_PASSWORD OK' : 'DB_PASSWORD MISSING')"
```

**恢复步骤**:
```bash
# 1. 从备份恢复 .env
cp /var/www/myapp/.env.example /var/www/myapp/.env
# 然后编辑填入正确配置

# 2. 重启应用
pm2 restart myapp --update-env
```

---

### 3.5 数据库回滚

**场景**: schema 更新导致问题

**步骤**:
```bash
# 1. 备份当前数据
pg_dump -U myapp_user -h 127.0.0.1 myapp > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 恢复 schema
psql -U myapp_user -h 127.0.0.1 -d myapp -f src/db/schema.sql

# 3. 验证
psql -U myapp_user -h 127.0.0.1 -d myapp -c '\dt'
```

---

## 4. 服务管理

### PostgreSQL

```bash
# 状态
sudo systemctl status postgresql

# 启动/停止/重启
sudo systemctl start postgresql
sudo systemctl stop postgresql
sudo systemctl restart postgresql

# 连接测试
psql -U myapp_user -d myapp -c "SELECT 1"

# 查看数据库
psql -U myapp_user -d myapp -c "\dt"

# 备份
pg_dump -U myapp_user myapp > backup.sql

# 恢复
psql -U myapp_user myapp < backup.sql
```

### Redis

```bash
# 状态
sudo systemctl status redis

# 启动/停止/重启
sudo systemctl start redis
sudo systemctl stop redis
sudo systemctl restart redis

# 连接测试
redis-cli ping

# 查看键
redis-cli keys '*'

# 清空缓存
redis-cli flushall
```

### PM2 (应用)

```bash
# 状态
pm2 status

# 启动
pm2 start ecosystem.config.js

# 重启
pm2 restart myapp

# 停止
pm2 stop myapp

# 查看日志
pm2 logs myapp

# 监控
pm2 monit

# 保存配置
pm2 save

# 开机启动
pm2 startup
```

---

## 3. 数据库操作

### 初始化数据库

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 创建用户
CREATE USER myapp_user WITH PASSWORD 'MyApp@2026';

# 创建数据库
CREATE DATABASE myapp OWNER myapp_user;

# 授权
GRANT ALL PRIVILEGES ON DATABASE myapp TO myapp_user;

# 退出
\q

# 导入 schema
psql -U myapp_user -d myapp -f /home/admin/biostructure-db/src/db/schema.sql
```

### 日常维护

```bash
# 查看表大小
psql -U myapp_user -d myapp -c "
SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename)) 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(tablename) DESC;"

# 清理空表
psql -U myapp_user -d myapp -c "VACUUM ANALYZE;"

# 重建索引
psql -U myapp_user -d myapp -c "REINDEX DATABASE myapp;"
```

---

## 4. 应用部署

### 手动部署

```bash
cd /home/admin/biostructure-db

# 拉取最新代码
git pull origin main

# 安装依赖
npm install --production

# 重启应用
pm2 restart myapp

# 验证
curl http://localhost:3000/api/health
```

### GitHub Actions 自动部署

1. Push 到 main 分支
2. GitHub Actions 自动触发
3. SSH 部署到服务器
4. PM2 重启应用

**Secrets 配置**:
- `DEPLOY_SSH_KEY`: 部署私钥
- `DEPLOY_HOST`: 服务器 IP
- `DEPLOY_USER`: 部署用户

---

## 5. 故障排查

### 应用无法启动

```bash
# 检查 PM2 日志
pm2 logs myapp --lines 100

# 检查端口占用
lsof -i :3000

# 检查 Node 版本
node --version

# 检查依赖
npm ls --depth=0

# 手动启动测试
cd /home/admin/biostructure-db
node src/app.js
```

### 数据库连接失败

```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 检查监听端口
ss -tlnp | grep 5432

# 检查 pg_hba.conf
sudo cat /var/lib/pgsql/data/pg_hba.conf

# 测试连接
psql -U myapp_user -d myapp -h localhost

# 检查用户权限
psql -U postgres -c "\du myapp_user"
```

### Redis 连接失败

```bash
# 检查 Redis 状态
sudo systemctl status redis

# 检查监听端口
ss -tlnp | grep 6379

# 测试连接
redis-cli ping

# 检查配置
sudo cat /etc/redis.conf | grep -E "bind|port"
```

### 内存不足

```bash
# 查看内存使用
free -h

# 查看 PM2 进程
pm2 monit

# 重启应用释放内存
pm2 restart myapp

# 调整 PM2 内存限制
# 编辑 ecosystem.config.js: max_memory_restart: '200M'
```

---

## 6. 健康检查

### 自动化脚本

```bash
#!/bin/bash
# scripts/health-check.sh

echo "=== 健康检查 ==="

# 检查 PostgreSQL
if pg_isready -U myapp_user -d myapp > /dev/null; then
    echo "✅ PostgreSQL: OK"
else
    echo "❌ PostgreSQL: FAILED"
fi

# 检查 Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: OK"
else
    echo "❌ Redis: FAILED"
fi

# 检查应用
if curl -s http://localhost:3000/api/health | grep -q "healthy"; then
    echo "✅ Application: OK"
else
    echo "❌ Application: FAILED"
fi

# 检查 PM2
pm2 status | grep -q "online" && echo "✅ PM2: OK" || echo "❌ PM2: FAILED"
```

### 健康检查端点

```bash
curl http://localhost:3000/api/health | jq
```

**预期响应**:
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2026-03-29T...",
  "database": "connected",
  "structures": 108,
  "uptime": 12345,
  "memory": {...},
  "version": "1.0.0"
}
```

---

## 7. 日志管理

### PM2 日志

```bash
# 查看日志
pm2 logs myapp

# 查看错误日志
pm2 logs myapp --err

# 清空日志
pm2 flush myapp

# 日志位置
ls -la /home/admin/.pm2/logs/
```

### 系统日志

```bash
# PostgreSQL 日志
sudo journalctl -u postgresql -f

# Redis 日志
sudo journalctl -u redis -f

# Nginx 日志 (如果安装)
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 8. 备份与恢复

### 数据库备份

```bash
# 手动备份
pg_dump -U myapp_user myapp > /home/admin/backups/myapp-$(date +%Y%m%d).sql

# 自动备份 (cron)
# 0 2 * * * pg_dump -U myapp_user myapp > /home/admin/backups/myapp-$(date +\%Y\%m\%d).sql
```

### 备份恢复

```bash
# 恢复数据库
psql -U myapp_user myapp < /home/admin/backups/myapp-20260329.sql
```

---

## 9. 安全注意事项

1. **不要提交 .env 文件** - 已加入 .gitignore
2. **定期更新密码** - 数据库密码建议定期更换
3. **配置防火墙** - 只开放必要端口 (80, 443, 22)
4. **监控异常登录** - 检查 /var/log/secure
5. **定期更新系统** - `sudo dnf update -y`

---

## 10. 常用命令速查

```bash
# 应用状态
pm2 status && pm2 monit

# 数据库状态
sudo systemctl status postgresql && pg_isready

# Redis 状态
sudo systemctl status redis && redis-cli ping

# 磁盘空间
df -h

# 内存使用
free -h

# 端口占用
ss -tlnp | grep -E "3000|5432|6379|80"

# 进程查看
ps aux | grep -E "node|postgres|redis"

# 日志查看
pm2 logs --lines 50
```

---

## 11. 数据库备份与恢复

### 11.1 自动备份配置

**备份脚本**: `scripts/backup-db.sh`

**备份策略**:
- 频率：每日凌晨 2 点
- 保留期：7 天
- 格式：gzip 压缩
- 位置：`/home/admin/backups/`

**Cron 配置**:
```bash
# 查看当前 cron 任务
crontab -l

# 备份任务（已配置）
0 2 * * * /home/admin/biostructure-db/scripts/backup-db.sh >> /home/admin/backups/backup.log 2>&1
```

### 11.2 手动备份

```bash
# 执行备份脚本
bash /home/admin/biostructure-db/scripts/backup-db.sh

# 或直接使用 pg_dump
PGPASSWORD="MyApp@2026" pg_dump -h 127.0.0.1 -U myapp_user myapp | gzip > backup_$(date +%Y%m%d).sql.gz
```

### 11.3 备份恢复

```bash
# 1. 停止应用（可选，避免写入冲突）
pm2 stop myapp

# 2. 解压备份文件
gunzip -c /home/admin/backups/myapp_20260330.sql.gz > restore.sql

# 3. 恢复数据库
psql -h 127.0.0.1 -U myapp_user -d myapp -f restore.sql

# 4. 重启应用
pm2 start myapp

# 5. 验证
curl http://localhost:3000/api/health
```

### 11.4 备份管理

```bash
# 查看备份列表
ls -lh /home/admin/backups/

# 查看备份日志
tail -20 /home/admin/backups/backup.log

# 手动清理旧备份
find /home/admin/backups -name "myapp_*.sql.gz" -mtime +7 -delete
```

---

## 12. 监控与告警

### 12.1 监控脚本

**监控脚本**: `scripts/monitor.sh`

**采集指标**:
- 系统负载 (1/5/15 分钟)
- 内存使用率
- 磁盘使用率
- 服务状态 (Nginx/PostgreSQL/PM2)
- API 健康状态
- 数据库连接状态

**采集频率**: 每 10 分钟

**日志位置**:
- 指标日志：`/home/admin/logs/metrics.log`
- 告警日志：`/home/admin/logs/alerts.log`

### 12.2 告警阈值

| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| CPU 负载 (1 分钟) | > 4 | ⚠️ 警告 |
| 内存使用率 | > 85% | ⚠️ 警告 |
| 磁盘使用率 | > 90% | ⚠️ 警告 |
| Nginx 服务 | inactive | ❌ 严重 |
| PostgreSQL 服务 | inactive | ❌ 严重 |
| PM2 应用 | offline | ❌ 严重 |
| API 状态 | != 200 | ❌ 严重 |
| 数据库连接 | disconnected | ❌ 严重 |

### 12.3 查看监控

```bash
# 查看最新指标
tail -10 /home/admin/logs/metrics.log

# 查看告警历史
cat /home/admin/logs/alerts.log

# 实时监控系统状态
watch -n 5 'bash /home/admin/biostructure-db/scripts/health-check.sh'
```

### 12.4 健康检查脚本

```bash
# 运行健康检查
bash /home/admin/biostructure-db/scripts/health-check.sh

# 或查看 cron 日志
tail -20 /home/admin/logs/health-check.log
```

### 12.5 ECS 自带监控（补充）

**阿里云 ECS 控制台** 提供基础资源监控:
- CPU 使用率
- 内存使用率
- 磁盘 I/O
- 网络流量

**访问路径**: 阿里云控制台 → ECS → 实例 → 监控图表

**建议**: 结合 ECS 监控（资源层）+ 项目监控（应用层）进行全方位监控。

---

**下一步**: 创建 `ops/lessons_learned.md` 记录经验教训。

---

## 13. 备案完成后 HTTPS 接入指南

> ⏸️ 当前状态：暂停（备案限制）
> 备案完成后按以下步骤恢复 HTTPS 接入

### 11.1 方案选择

**推荐方案**: Let's Encrypt 自动化证书（免费、自动续期）

**备选方案**: 阿里云免费 SSL 证书（控制台申请、手动部署）

### 11.2 Let's Encrypt 接入步骤

**前提条件**:
- [ ] 备案已完成
- [ ] 域名解析已生效 (jlupdb.me → 101.200.53.98)
- [ ] Nginx 已安装并运行
- [ ] 80 端口可公网访问

**步骤**:

```bash
# 1. 安装 certbot（如未安装）
sudo yum install -y certbot python3-certbot-nginx

# 2. 申请证书（自动配置 Nginx）
sudo certbot --nginx -d jlupdb.me

# 3. 验证自动续期
sudo systemctl status certbot.timer
```

**或使用 acme.sh（更轻量）**:

```bash
# 1. 安装 acme.sh
curl https://get.acme.sh | sh

# 2. 注册账户
source ~/.bashrc
acme.sh --register-account -m admin@jlupdb.me

# 3. 申请证书
acme.sh --issue -d jlupdb.me --webroot /usr/share/nginx/html

# 4. 安装证书
acme.sh --install-cert -d jlupdb.me \
  --key-file /etc/nginx/ssl/jlupdb.me.key \
  --fullchain-file /etc/nginx/ssl/jlupdb.me.pem \
  --reloadcmd "sudo systemctl reload nginx"
```

### 11.3 Nginx HTTPS 配置

**配置文件**: `/etc/nginx/conf.d/jlupdb.conf`

```nginx
# HTTP → HTTPS 重定向
server {
    listen 80;
    server_name jlupdb.me;
    return 301 https://$server_name$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name jlupdb.me;

    ssl_certificate /etc/nginx/ssl/jlupdb.me.pem;
    ssl_certificate_key /etc/nginx/ssl/jlupdb.me.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 11.4 验证步骤

```bash
# 1. 测试 Nginx 配置
sudo nginx -t

# 2. 重载 Nginx
sudo systemctl reload nginx

# 3. 验证 HTTPS 访问
curl -I https://jlupdb.me

# 4. 验证 HTTP 重定向
curl -I http://jlupdb.me

# 5. 在线验证（SSL Labs）
# https://www.ssllabs.com/ssltest/analyze.html?d=jlupdb.me
```

### 11.5 证书续期

**Let's Encrypt 证书有效期**: 90 天

**自动续期**（certbot）:
```bash
# 已配置定时任务，自动续期
sudo systemctl status certbot.timer
```

**手动续期**（acme.sh）:
```bash
# acme.sh 自动续期（已配置 cron）
acme.sh --list  # 查看已安装证书
```

### 11.6 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 证书申请失败（403） | 80 端口被拦截 | 检查安全组、WAF 配置 |
| DNS 验证失败 | 解析未生效 | 等待 DNS 传播或检查解析配置 |
| Nginx 重载失败 | 配置语法错误 | `nginx -t` 检查配置 |
| HTTPS 无法访问 | 443 端口未开放 | 检查安全组规则 |

---

## 14. 本地控制平面 (OpenClaw Control Plane v1)

**状态**: ✅ 已初始化 (2026-03-30)

**用途**: 自动化任务调度与执行，减少人工干预

### 14.1 控制文件

| 文件 | 用途 |
|------|------|
| `control/queue.json` | 任务队列（当前/待执行任务） |
| `control/paused.json` | 暂停任务（HTTPS/域名等备案限制项） |
| `control/runtime_state.json` | 运行时状态（当前阶段/进度） |
| `control/phase_policy.json` | 阶段执行策略（自动/手动规则） |

### 14.2 执行循环

**脚本**: `control/agent_loop.py`

**职责**:
1. 读取控制文件
2. 获取下一个可执行任务
3. 调用对应 handler
4. 更新队列和状态
5. 写入日志 (`control/logs/agent-loop.log`)

**Handlers** (`control/handlers/`):
- `p2_select_samples` - 选择 PDB 样例
- `p2_import_samples` - 导入样例数据
- `p2_verify_api` - 验证 API 返回真实数据
- `p2_update_docs` - 更新文档

### 14.3 手动执行

```bash
# 测试运行（dry-run）
cd /home/admin/biostructure-db
python3 control/agent_loop.py

# 查看日志
tail -f control/logs/agent-loop.log

# 查看当前队列
cat control/queue.json | jq '.queue'

# 查看运行时状态
cat control/runtime_state.json | jq '.current_state'
```

### 14.4 Systemd 调度（可选）

**Service**: `systemd/openclaw-agent.service`  
**Timer**: `systemd/openclaw-agent.timer`

**调度频率**: 每 15 分钟（8:00-20:00）

**启用步骤**（验证后执行）:
```bash
# 1. 复制配置文件
sudo cp systemd/openclaw-agent.service /etc/systemd/system/
sudo cp systemd/openclaw-agent.timer /etc/systemd/system/

# 2. 重载 systemd
sudo systemctl daemon-reload

# 3. 测试运行
sudo systemctl start openclaw-agent.service
sudo systemctl status openclaw-agent.service

# 4. 启用定时任务
sudo systemctl enable openclaw-agent.timer
sudo systemctl start openclaw-agent.timer

# 5. 验证
systemctl list-timers | grep openclaw
```

### 14.5 暂停任务

当前暂停项（见 `control/paused.json`）:
- HTTPS/SSL 证书配置（备案限制）
- jlupdb.me 域名公网访问（备案限制）
- 大规模数据导入（等待用户裁决）

---

## 15. 当前运行模式说明

**模式**: HTTP 开发模式（备案期间）

**访问方式**:
- IP 直连：http://101.200.53.98 ✅
- 域名：暂停使用（备案限制）

**配置状态**:
- Nginx 80 端口 → PM2 3000 端口 ✅
- 443 端口：暂未配置 ⏸️

**注意事项**:
- 当前仅支持 HTTP 访问
- 生产数据建议定期备份
- 备案完成后立即恢复 HTTPS
