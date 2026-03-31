# Recovery — 失败恢复与回滚

## 应用启动失败

**症状**: `pm2 status` 显示 `errored` 或 `stopped`

```bash
pm2 logs myapp --lines 50    # 查看日志
lsof -i :3000                 # 检查端口
cd /var/www/myapp && npm ls --depth=0  # 检查依赖
node src/app.js               # 手动启动测试

# 恢复
pm2 stop myapp
cd /var/www/myapp && npm install --production
cat .env                      # 确认配置
pm2 start ecosystem.config.js
```

## 数据库连接失败

**症状**: `/api/health` 返回 `"database": "disconnected"`

```bash
sudo systemctl status postgresql       # 检查状态
ss -tlnp | grep 5432                   # 检查监听
psql -U myapp_user -d myapp -c "SELECT 1"  # 测试连接

# 恢复
sudo systemctl restart postgresql
sudo cat /var/lib/pgsql/data/pg_hba.conf | grep -v "^#"
bash scripts/init-db.sh
```

## GitHub Actions 部署失败

| 错误 | 原因 | 解决 |
|------|------|------|
| SSH 连接失败 | Secrets 配置错误 | 检查 DEPLOY_HOST, DEPLOY_USER, DEPLOY_SSH_KEY |
| PM2 重启失败 | 进程名不匹配 | 确认 pm2 restart myapp |
| 权限错误 | SSH 密钥权限 | 验证 authorized_keys |

```bash
# 手动回滚
cd /var/www/myapp
git log --oneline -5
git reset --hard <commit>
npm install --production
pm2 restart myapp
```

## 配置错误恢复

```bash
pm2 logs myapp --lines 30
cat /var/www/myapp/.env

# 恢复
cp /var/www/myapp/.env.example /var/www/myapp/.env
# 编辑填入正确配置
pm2 restart myapp --update-env
```

## 数据库回滚

```bash
pg_dump -U myapp_user -h 127.0.0.1 myapp > backup_$(date +%Y%m%d_%H%M%S).sql
psql -U myapp_user -h 127.0.0.1 -d myapp -f src/db/schema.sql
psql -U myapp_user -h 127.0.0.1 -d myapp -c '\dt'
```

## 应用无法启动（详细排查）

```bash
pm2 logs myapp --lines 100
lsof -i :3000
node --version
npm ls --depth=0
cd /home/admin/biostructure-db && node src/app.js
```

## Redis 连接失败

```bash
sudo systemctl status redis
ss -tlnp | grep 6379
redis-cli ping
sudo cat /etc/redis.conf | grep -E "bind|port"
```

## 内存不足

```bash
free -h
pm2 monit
pm2 restart myapp
# 编辑 ecosystem.config.js: max_memory_restart: '200M'
```
