# 📖 Runbook - 运维操作手册

**生成时间**: 2026-03-29 22:56 CST  
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

**下一步**: 创建 `ops/lessons_learned.md` 记录经验教训。
