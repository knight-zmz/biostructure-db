# 🚀 最小启动路径 (Minimum Startup Path)

**生成时间**: 2026-03-29 22:57 CST  
**目标**: 用最少的步骤让应用跑起来

---

## 最可能的第一条运行路线

```
安装 PostgreSQL → 初始化数据库 → 安装 Redis → 安装 PM2 → 启动应用 → 验证健康
```

### 详细步骤

#### Step 1: 安装 PostgreSQL (5 分钟)

```bash
sudo dnf install -y postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**验证**: `pg_isready` 应返回 accepting connections

---

#### Step 2: 创建数据库与用户 (2 分钟)

```bash
sudo -u postgres psql <<EOF
CREATE USER myapp_user WITH PASSWORD 'MyApp@2026';
CREATE DATABASE myapp OWNER myapp_user;
GRANT ALL PRIVILEGES ON DATABASE myapp TO myapp_user;
EOF
```

**验证**: `psql -U myapp_user -d myapp -c "SELECT 1"` 应返回成功

---

#### Step 3: 导入 Schema (1 分钟)

```bash
cd /home/admin/biostructure-db
psql -U myapp_user -d myapp -f src/db/schema.sql
```

**验证**: `psql -U myapp_user -d myapp -c "\dt"` 应显示 18 个表

---

#### Step 4: 安装 Redis (3 分钟)

```bash
sudo dnf install -y redis
sudo systemctl start redis
sudo systemctl enable redis
```

**验证**: `redis-cli ping` 应返回 PONG

---

#### Step 5: 安装 PM2 (2 分钟)

```bash
sudo npm install -g pm2
```

**验证**: `pm2 --version` 应显示版本号

---

#### Step 6: 启动应用 (1 分钟)

```bash
cd /home/admin/biostructure-db
pm2 start ecosystem.config.js
pm2 save
```

**验证**: `pm2 status` 应显示 myapp 为 online

---

#### Step 7: 验证健康检查 (1 分钟)

```bash
curl http://localhost:3000/api/health | jq
```

**预期响应**:
```json
{
  "success": true,
  "status": "healthy",
  "database": "connected",
  "structures": 0,
  "uptime": ...,
  "memory": {...}
}
```

---

## 当前不确定项

| 不确定项 | 影响 | 验证方法 |
|----------|------|----------|
| PostgreSQL 版本兼容性 | 可能导致 schema 导入失败 | 安装后检查版本 |
| Redis 配置是否需要修改 | 默认配置可能不满足需求 | 启动后测试连接 |
| 端口 3000 是否被占用 | 应用可能无法启动 | `lsof -i :3000` 检查 |
| node_modules 完整性 | 依赖可能损坏或缺失 | `npm ls` 验证 |
| PM2 日志目录权限 | 日志可能无法写入 | 启动后检查日志 |
| 防火墙规则 | 外部可能无法访问 | `firewall-cmd --list-all` |

---

## 最大阻塞 (Blockers)

### 🔴 阻塞 1: PostgreSQL 安装失败

**可能原因**:
- dnf 源配置问题
- 磁盘空间不足
- 系统包冲突

**应对方案**:
```bash
# 检查 dnf 源
dnf repolist

# 清理缓存
dnf clean all

# 重试安装
dnf install -y postgresql-server
```

---

### 🔴 阻塞 2: 数据库权限问题

**可能原因**:
- pg_hba.conf 配置限制
- 用户创建失败

**应对方案**:
```bash
# 检查 pg_hba.conf
sudo cat /var/lib/pgsql/data/pg_hba.conf | grep -v "^#"

# 临时允许本地信任连接
sudo sed -i 's/ident/trust/g' /var/lib/pgsql/data/pg_hba.conf
sudo systemctl restart postgresql
```

---

### 🟡 阻塞 3: Redis 启动失败

**可能原因**:
- 端口 6379 被占用
- 配置文件错误

**应对方案**:
```bash
# 检查端口
ss -tlnp | grep 6379

# 检查日志
sudo journalctl -u redis -f

# 应用可降级运行 (缓存失效)
```

---

### 🟡 阻塞 4: 应用启动失败

**可能原因**:
- 端口 3000 被占用
- 依赖缺失
- 代码错误

**应对方案**:
```bash
# 检查端口
lsof -i :3000

# 检查依赖
npm ls --depth=0

# 查看日志
pm2 logs myapp --lines 50

# 手动启动调试
node src/app.js
```

---

## 成功标准

应用成功启动的标志:

1. ✅ `pm2 status` 显示 myapp 为 online
2. ✅ `curl http://localhost:3000/api/health` 返回 `"status": "healthy"`
3. ✅ `curl http://localhost:3000/api/stats` 返回统计数据
4. ✅ `curl http://localhost:3000/` 返回 index.html
5. ✅ PM2 日志无 ERROR 级别错误

---

## 失败回滚

如果启动失败，按以下顺序排查:

```bash
# 1. 检查服务状态
sudo systemctl status postgresql
sudo systemctl status redis
pm2 status

# 2. 检查日志
pm2 logs myapp --lines 100
sudo journalctl -u postgresql -n 50
sudo journalctl -u redis -n 50

# 3. 检查端口
ss -tlnp | grep -E "3000|5432|6379"

# 4. 检查资源
free -h
df -h

# 5. 重启服务
sudo systemctl restart postgresql
sudo systemctl restart redis
pm2 restart myapp
```

---

## 预计时间

| 步骤 | 预计时间 |
|------|----------|
| PostgreSQL 安装 | 5 分钟 |
| 数据库初始化 | 3 分钟 |
| Redis 安装 | 3 分钟 |
| PM2 安装 | 2 分钟 |
| 应用启动与验证 | 5 分钟 |
| **总计** | **~18 分钟** |

---

## 下一步行动

1. 执行上述最小启动路径
2. 验证所有成功标准
3. 如有失败，按回滚步骤排查
4. 成功后更新 `ops/project_state.md`

---

**文档状态**: 待执行  
**执行优先级**: 🔴 最高
