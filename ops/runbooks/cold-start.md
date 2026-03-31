# Cold Start — 新服务器首次启动

## 前置条件

- OS: Alibaba Cloud Linux / CentOS
- 已安装: PostgreSQL, Redis, Node.js, PM2, Nginx

## 步骤

```bash
# 1. 确认依赖
which psql redis-cli pm2 node

# 2. 配置 PostgreSQL 认证
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

## 验证清单

- [ ] `pg_isready` → OK
- [ ] `redis-cli ping` → PONG
- [ ] `pm2 status` → myapp online
- [ ] `curl /api/health` → healthy
- [ ] `curl http://101.200.53.98` → 响应
