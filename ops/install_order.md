# 📦 最小依赖安装顺序

**生成时间**: 2026-03-29 22:57 CST  
**原则**: 按需安装，不预装未来可能用到的工具

---

## 安装顺序

### 阶段 1: 数据库层 (必须)

#### 1.1 PostgreSQL

```bash
# 安装
sudo dnf install -y postgresql-server postgresql-contrib

# 初始化数据库
sudo postgresql-setup --initdb

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 验证
pg_isready
```

**验证命令**:
```bash
$ pg_isready
/var/run/postgresql:5432 - accepting connections
```

#### 1.2 创建数据库与用户

```bash
# 切换到 postgres 用户执行
sudo -u postgres psql <<EOF
CREATE USER myapp_user WITH PASSWORD 'MyApp@2026';
CREATE DATABASE myapp OWNER myapp_user;
GRANT ALL PRIVILEGES ON DATABASE myapp TO myapp_user;
\q
EOF

# 导入 schema
psql -U myapp_user -d myapp -f /home/admin/biostructure-db/src/db/schema.sql
```

**验证命令**:
```bash
$ psql -U myapp_user -d myapp -c "\dt"
# 应显示 18 个表
```

---

### 阶段 2: 缓存层 (必须)

#### 2.1 Redis

```bash
# 安装
sudo dnf install -y redis

# 启动服务
sudo systemctl start redis
sudo systemctl enable redis

# 验证
redis-cli ping
```

**验证命令**:
```bash
$ redis-cli ping
PONG
```

**注**: Redis 失败时应用可降级运行 (缓存功能失效)。

---

### 阶段 3: 进程管理 (必须)

#### 3.1 PM2

```bash
# 全局安装
sudo npm install -g pm2

# 验证
pm2 --version

# 配置开机启动 (可选，生产环境推荐)
pm2 startup
pm2 save
```

**验证命令**:
```bash
$ pm2 --version
# 显示版本号
```

---

### 阶段 4: 应用启动 (验证)

#### 4.1 启动应用

```bash
cd /home/admin/biostructure-db

# 使用 PM2 启动
pm2 start ecosystem.config.js

# 验证
pm2 status
curl http://localhost:3000/api/health
```

**预期响应**:
```json
{
  "success": true,
  "status": "healthy",
  "database": "connected",
  ...
}
```

---

### 阶段 5: Web 服务器 (可选)

#### 5.1 Nginx

**仅在需要反向代理或 HTTPS 时安装**:

```bash
# 安装
sudo dnf install -y nginx

# 启动
sudo systemctl start nginx
sudo systemctl enable nginx

# 配置反向代理
sudo cat > /etc/nginx/conf.d/myapp.conf <<EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# 验证配置
sudo nginx -t

# 重载
sudo systemctl reload nginx
```

**验证命令**:
```bash
$ curl http://localhost/api/health
# 应返回健康状态
```

---

## 不安装的工具 (本轮)

以下工具本轮**不安装**，避免无差别预装:

| 工具 | 原因 |
|------|------|
| docker-compose | 项目当前无 Dockerfile，无需容器化 |
| Python 升级 | 项目主要使用 Node.js，Python 脚本非必需 |
| Go/Java | 项目技术栈不涉及 |
| Maven/Gradle | 非 Java 项目 |
| certbot | HTTPS 配置延后，本轮仅验证 HTTP |
| fail2ban | 安全加固延后 |
| 监控系统 | 基础运行验证后再配置 |

---

## 安装脚本 (一键执行)

创建 `scripts/install-deps.sh`:

```bash
#!/bin/bash
set -e

echo "=== 安装 biostructure-db 依赖 ==="

# PostgreSQL
echo "[1/4] 安装 PostgreSQL..."
sudo dnf install -y postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Redis
echo "[2/4] 安装 Redis..."
sudo dnf install -y redis
sudo systemctl start redis
sudo systemctl enable redis

# PM2
echo "[3/4] 安装 PM2..."
sudo npm install -g pm2

# 数据库初始化
echo "[4/4] 初始化数据库..."
sudo -u postgres psql <<EOF
CREATE USER myapp_user WITH PASSWORD 'MyApp@2026';
CREATE DATABASE myapp OWNER myapp_user;
GRANT ALL PRIVILEGES ON DATABASE myapp TO myapp_user;
EOF

psql -U myapp_user -d myapp -f /home/admin/biostructure-db/src/db/schema.sql

echo "=== 依赖安装完成 ==="
echo "运行以下命令启动应用:"
echo "  cd /home/admin/biostructure-db"
echo "  pm2 start ecosystem.config.js"
echo "  pm2 logs myapp"
```

---

## 验证清单

安装完成后执行:

```bash
# 1. PostgreSQL
pg_isready && echo "✅ PostgreSQL OK" || echo "❌ PostgreSQL FAILED"

# 2. Redis
redis-cli ping > /dev/null && echo "✅ Redis OK" || echo "❌ Redis FAILED"

# 3. PM2
pm2 --version > /dev/null && echo "✅ PM2 OK" || echo "❌ PM2 FAILED"

# 4. 数据库连接
psql -U myapp_user -d myapp -c "SELECT 1" > /dev/null && echo "✅ DB Connection OK" || echo "❌ DB Connection FAILED"

# 5. Schema 导入
psql -U myapp_user -d myapp -c "SELECT COUNT(*) FROM structures" > /dev/null && echo "✅ Schema OK" || echo "❌ Schema FAILED"

# 6. 应用启动 (手动)
cd /home/admin/biostructure-db
pm2 start ecosystem.config.js
sleep 3
curl -s http://localhost:3000/api/health | grep -q "healthy" && echo "✅ Application OK" || echo "❌ Application FAILED"
```

---

## 资源预估

| 组件 | 磁盘占用 | 内存占用 |
|------|----------|----------|
| PostgreSQL | ~200MB | ~50MB |
| Redis | ~10MB | ~5MB |
| PM2 | ~50MB | ~20MB |
| 应用 | ~100MB | ~100MB |
| **总计** | **~360MB** | **~175MB** |

**当前可用资源**: 磁盘 24GB, 内存 965MB  
**结论**: 资源充足 ✅

---

**下一步**: 判断项目的最小启动路径。
