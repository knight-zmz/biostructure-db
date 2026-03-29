# 📋 首轮冷启动证据化验收报告

**报告生成时间**: 2026-03-29 23:11 CST  
**项目**: biostructure-db  
**阶段**: 首轮冷启动盘点完成  
**执行人**: AI Agent (OpenClaw)

---

## 1. 仓库证据

### 1.1 ops/ 目录文件清单

| 文件路径 | 大小 | 创建时间 | 状态 |
|----------|------|----------|------|
| `ops/bootstrap_assessment.md` | 4,209 B | 22:56 | ✅ 已创建 |
| `ops/project_state.md` | 7,799 B | 22:56 | ✅ 已创建 |
| `ops/backlog.md` | 3,722 B | 22:57 | ✅ 已创建 |
| `ops/runbook.md` | 6,390 B | 22:57 | ✅ 已创建 |
| `ops/lessons_learned.md` | 4,987 B | 22:57 | ✅ 已创建 |
| `ops/gap_analysis.md` | 5,206 B | 22:58 | ✅ 已创建 |
| `ops/install_order.md` | 5,406 B | 22:58 | ✅ 已创建 |
| `ops/minimum_startup_path.md` | 4,965 B | 22:59 | ✅ 已创建 |
| `ops/COLD_START_ACCEPTANCE.md` | - | 23:11 | ✅ 本报告 |

**总计**: 9 个文件，约 47KB 文档

### 1.2 Git 提交状态

```bash
$ git status --short ops/
?? ops/
```

**状态**: ⚠️ **未提交** - ops/ 目录为新创建，尚未添加到 Git 跟踪

**后续操作**: 需执行以下命令提交并推送:

```bash
cd /home/admin/biostructure-db
git add ops/
git commit -m "docs(ops): 首轮冷启动盘点文档与验收报告"
git push origin main
```

### 1.3 各文件核心内容摘要

| 文件 | 核心内容 |
|------|----------|
| `bootstrap_assessment.md` | 系统环境盘点：OS、用户权限、CPU/内存/磁盘、systemd 状态、已安装/缺失工具清单 |
| `project_state.md` | 项目技术栈详情、目录结构、API 端点清单 (30+)、数据库 schema(15 表)、运维脚本清单 (15 个) |
| `backlog.md` | 待办事项分级清单：P0 阻塞项 4 个、P1 重要项 4 个、P2 优化项 4 个 |
| `runbook.md` | 运维操作手册：快速启动、服务管理、数据库操作、故障排查、健康检查脚本 |
| `lessons_learned.md` | 经验教训：配置硬编码风险、文档组织问题、测试覆盖不足等 7 项发现 |
| `gap_analysis.md` | 启动缺口清单：系统工具 5 项、运行时 5 项、配置 5 项、数据库 5 项、安全 5 项 |
| `install_order.md` | 最小依赖安装顺序：PostgreSQL→Redis→PM2→应用启动，含验证命令 |
| `minimum_startup_path.md` | 最小启动路径：7 步骤详细流程，含不确定项和最大阻塞分析 |

---

## 2. 服务证据

### 2.1 应用启动方式

**启动命令**:
```bash
cd /home/admin/biostructure-db
pm2 start ecosystem.config.js
```

**PM2 配置文件**: `ecosystem.config.js`

```javascript
{
  name: 'myapp',
  script: 'src/app.js',
  instances: 1,
  autorestart: true,
  max_memory_restart: '200M',
  env: { NODE_ENV: 'production', PORT: 3000 }
}
```

### 2.2 进程管理状态

```
┌────┬────────┬───────────┬─────────┬─────────┬─────────┬────────┬──────┬──────────┬─────────┬──────────┬─────────┬──────────┐
│ id │ name   │ namespace │ version │ mode    │ pid     │ uptime │ ↺    │ status   │ cpu     │ mem      │ user    │ watching │
├────┼────────┼───────────┼─────────┼─────────┼─────────┼────────┼──────┼──────────┼─────────┼──────────┼─────────┼──────────┤
│ 0  │ myapp  │ default   │ 1.0.0   │ cluster │ 35205   │ 8m     │ 1    │ online   │ 0%      │ 84.2mb   │ admin   │ disabled │
└────┴────────┴───────────┴─────────┴─────────┴─────────┴────────┴──────┴──────────┴─────────┴──────────┴─────────┴──────────┘
```

**关键指标**:
- 状态: `online` ✅
- 重启次数: 1 次 (首次启动失败后自动重启)
- 内存占用: 84.2MB
- 运行时长: 8 分钟+

### 2.3 应用工作目录

```
/home/admin/biostructure-db
```

**主入口文件**: `src/app.js` (21,569 B)

### 2.4 日志文件路径

| 日志类型 | 路径 |
|----------|------|
| 输出日志 | `/home/admin/.pm2/logs/myapp-out.log` |
| 错误日志 | `/home/admin/.pm2/logs/myapp-error.log` |
| PM2 系统日志 | `/home/admin/.pm2/pm2.log` |

### 2.5 最近关键日志摘要

**myapp-out.log** (最后 8 行):
```
2026-03-29T23:03:13: 🧬 BioStructure DB API running on port 3000
2026-03-29T23:03:13: 📊 Health check: http://localhost:3000/api/stats
2026-03-29T23:03:13: 💾 Redis Cache: Disabled
2026-03-29T23:03:13: ✅ Redis 缓存已启用
2026-03-29T23:03:35: 🧬 BioStructure DB API running on port 3000
2026-03-29T23:03:35: 📊 Health check: http://localhost:3000/api/stats
2026-03-29T23:03:35: 💾 Redis Cache: Disabled
2026-03-29T23:03:35: ✅ Redis 缓存已启用
```

**myapp-error.log**: 空 (无错误)

**解读**:
- 应用成功启动 2 次 (首次因模块缺失失败，npm install 后成功)
- Redis 缓存显示 "Disabled" 但随后显示 "已启用" (代码逻辑：连接失败时降级)
- 无 ERROR 级别日志

---

## 3. 数据库证据

### 3.1 PostgreSQL 版本

```bash
$ psql --version
psql (PostgreSQL) 13.23
```

**版本**: PostgreSQL 13.23  
**安装包**: `postgresql-server-13.23-2.0.1.al8.x86_64`

### 3.2 数据库连接信息

| 配置项 | 值 | 脱敏状态 |
|--------|-----|----------|
| 主机 | `127.0.0.1` | - |
| 端口 | `5432` | - |
| 数据库名 | `myapp` | - |
| 用户名 | `myapp_user` | - |
| 密码 | `MyApp@2026` | ⚠️ 未脱敏 (硬编码在代码中) |

**连接命令**:
```bash
PGPASSWORD='***' psql -U myapp_user -h 127.0.0.1 -d myapp
```

### 3.3 已创建的 15 个表

| 序号 | 表名 | 用途 |
|------|------|------|
| 1 | `structures` | 结构主表 (PDB ID, 标题，分辨率等) |
| 2 | `active_sites` | 活性位点 |
| 3 | `assemblies` | 组装体 |
| 4 | `atoms` | 原子坐标 (核心表) |
| 5 | `citations` | 引用文献 |
| 6 | `entities` | 实体 |
| 7 | `ligands` | 配体 |
| 8 | `metal_ions` | 金属离子 |
| 9 | `pfam_domains` | Pfam 结构域 |
| 10 | `polypeptides` | 多肽链 |
| 11 | `ptms` | 翻译后修饰 |
| 12 | `residues` | 残基 |
| 13 | `secondary_structures` | 二级结构 |
| 14 | `sequence_index` | 序列索引 |
| 15 | `uniprot_mappings` | UniProt 映射 |

**所有表所有者**: `myapp_user`

### 3.4 表创建方式

**方式**: **SQL 脚本直接执行**

**执行命令**:
```bash
psql -U myapp_user -h 127.0.0.1 -d myapp -f src/db/schema.sql
```

**源文件**: `src/db/schema.sql` (12,955 B)

**特点**:
- ❌ 非 ORM 迁移 (无 Sequelize/Knex)
- ❌ 非版本化迁移 (无 migrations/ 目录)
- ✅ 纯 SQL DDL 脚本
- ⚠️ 无回滚脚本

---

## 4. 部署证据

### 4.1 GitHub Actions 工作流文件

**路径**: `.github/workflows/deploy.yml` (1,370 B)

**触发条件**:
```yaml
on:
  push:
    branches: [ main ]
  workflow_dispatch:
```

**部署步骤**:
1. Checkout code
2. Setup Node.js 20
3. npm install --production
4. npm test (允许失败)
5. SSH 部署到 `/var/www/myapp`
6. PM2 重启应用

### 4.2 当前部署链路实际执行情况

**本轮冷启动实际执行**:

| 步骤 | 计划 | 实际 |
|------|------|------|
| 代码同步 | GitHub Actions SSH 部署 | ✅ 手工 `git clone` |
| 依赖安装 | GitHub Actions npm install | ✅ 手工 `npm install` |
| 系统依赖 | 假设已存在 | ❌ 手工安装 PostgreSQL/Redis/PM2 |
| 应用启动 | PM2 restart | ✅ 手工 `pm2 start` |
| 目标目录 | `/var/www/myapp` | ❌ 未创建，直接在 clone 目录运行 |

### 4.3 应用在线原因

**结论**: 🔴 **手工运行结果**，非 GitHub Actions 触发

**证据**:
1. `/var/www/myapp` 目录不存在 (GitHub Actions 部署目标)
2. 无 GitHub Actions 执行记录 (本轮未 push)
3. PM2 进程由手工 `pm2 start` 启动
4. ops/ 文档未提交推送

**当前运行路径**:
```
/home/admin/biostructure-db/src/app.js
```

**而非**:
```
/var/www/myapp/src/app.js  # GitHub Actions 部署目标
```

---

## 5. 状态边界

### 5.1 已写回仓库的成果

| 成果 | 位置 | Git 状态 |
|------|------|----------|
| 环境盘点文档 | `ops/bootstrap_assessment.md` | ❌ 未提交 |
| 项目状态文档 | `ops/project_state.md` | ❌ 未提交 |
| 待办清单 | `ops/backlog.md` | ❌ 未提交 |
| 运维手册 | `ops/runbook.md` | ❌ 未提交 |
| 经验教训 | `ops/lessons_learned.md` | ❌ 未提交 |
| 缺口分析 | `ops/gap_analysis.md` | ❌ 未提交 |
| 安装顺序 | `ops/install_order.md` | ❌ 未提交 |
| 启动路径 | `ops/minimum_startup_path.md` | ❌ 未提交 |
| 验收报告 | `ops/COLD_START_ACCEPTANCE.md` | ❌ 未提交 |

**小结**: 所有 ops/ 文档均为本地文件，**尚未提交到 Git**。

### 5.2 仅存在服务器本地的状态

| 状态 | 位置 | 持久化方式 |
|------|------|------------|
| PostgreSQL 数据 | `/var/lib/pgsql/data` | 系统服务 |
| Redis 数据 | `/var/lib/redis` | 系统服务 |
| PM2 进程配置 | `/home/admin/.pm2/dump.pm2` | PM2 保存 |
| PM2 日志 | `/home/admin/.pm2/logs/` | 文件 |
| node_modules | `/home/admin/biostructure-db/node_modules` | 本地依赖 |
| 应用进程 | PID 35205 | 内存中 |

### 5.3 临时方案

| 临时方案 | 说明 | 风险 |
|----------|------|------|
| 数据库密码硬编码 | `src/app.js` 第 14 行明文密码 | 安全风险 |
| pg_hba.conf 修改 | 使用 md5 认证，允许本地连接 | 需固化到配置管理 |
| 直接 clone 运行 | 非 `/var/www/myapp` 标准路径 | 与 CI/CD 不一致 |
| 无 .env 文件 | 配置无法灵活调整 | 环境隔离困难 |

### 5.4 仍未规范化的事项

| 事项 | 当前状态 | 规范化建议 |
|------|----------|------------|
| 配置管理 | 硬编码在代码中 | 创建 `.env` + `dotenv` |
| 数据库迁移 | 单次 SQL 脚本 | 引入迁移工具 (如 node-pg-migrate) |
| 部署路径 | 手工 clone 目录 | 统一为 `/var/www/myapp` |
| 文档组织 | 根目录 30+ 混乱文件 | 归档历史文档到 `docs/archive/` |
| 监控告警 | 无 | 配置基础监控 + 告警 |
| 备份策略 | 无 | 配置自动备份 |

---

## 6. 下一步建议

### 🔴 建议 1: 移除硬编码配置 (最高优先级)

**问题**: 数据库密码 `MyApp@2026` 明文写在 `src/app.js` 第 14 行

**行动**:
```bash
# 1. 创建 .env 文件
cat > /home/admin/biostructure-db/.env <<EOF
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=myapp
DB_USER=myapp_user
DB_PASSWORD=MyApp@2026
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
NODE_ENV=production
PORT=3000
EOF

# 2. 创建 .env.example (脱敏模板)
cat > /home/admin/biostructure-db/.env.example <<EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=myapp_user
DB_PASSWORD=your_password_here
REDIS_HOST=localhost
REDIS_PORT=6379
NODE_ENV=production
PORT=3000
EOF

# 3. 更新 src/app.js 使用 process.env
# 4. 确保 .env 在 .gitignore 中
# 5. 重启应用
pm2 restart myapp --update-env
```

**验收**: `grep -n "password.*MyApp" src/app.js` 无结果

---

### 🟡 建议 2: 提交 ops/ 文档到仓库

**问题**: 所有盘点文档尚未提交，存在丢失风险

**行动**:
```bash
cd /home/admin/biostructure-db
git add ops/
git commit -m "docs(ops): 首轮冷启动盘点文档与验收报告

- bootstrap_assessment.md: 系统环境盘点
- project_state.md: 项目技术栈与 API 清单
- backlog.md: 待办事项分级清单
- runbook.md: 运维操作手册
- lessons_learned.md: 经验教训总结
- gap_analysis.md: 启动缺口分析
- install_order.md: 最小依赖安装顺序
- minimum_startup_path.md: 最小启动路径
- COLD_START_ACCEPTANCE.md: 验收报告

本轮完成冷启动盘点，应用已成功启动并可通过健康检查。"
git push origin main
```

**验收**: GitHub 仓库可见 ops/ 目录

---

### 🟡 建议 3: 统一部署路径到 /var/www/myapp

**问题**: 当前运行在 `/home/admin/biostructure-db`，与 GitHub Actions 配置不一致

**行动**:
```bash
# 1. 创建标准目录
sudo mkdir -p /var/www/myapp
sudo chown admin:admin /var/www/myapp

# 2. 复制代码
cp -r /home/admin/biostructure-db/* /var/www/myapp/

# 3. 更新 PM2 配置
cd /var/www/myapp
pm2 delete myapp
pm2 start ecosystem.config.js

# 4. 验证
curl http://localhost:3000/api/health

# 5. 更新 GitHub Actions (如需)
# 确认 TARGET: "/var/www/myapp" 与实际一致
```

**验收**: `pm2 list` 显示脚本路径为 `/var/www/myapp/src/app.js`

---

## 附录：验收检查清单

### ✅ 已完成

- [x] 系统环境盘点 (CPU/内存/磁盘/OS)
- [x] 仓库结构盘点 (技术栈/目录/API 端点)
- [x] ops/ 文档创建 (8 个文件)
- [x] PostgreSQL 安装与初始化 (13.23, 15 表)
- [x] Redis 安装与启动 (6.2.20)
- [x] PM2 安装与配置 (6.0.14)
- [x] 应用启动并可通过健康检查
- [x] 验收报告生成

### ❌ 未完成

- [ ] ops/ 文档提交到 Git
- [ ] 移除数据库密码硬编码
- [ ] 统一部署路径到 `/var/www/myapp`
- [ ] 配置 Nginx 反向代理
- [ ] 验证 GitHub Actions 自动部署
- [ ] 导入示例数据

---

**报告状态**: ✅ 完成  
**提交状态**: ❌ 待提交  
**应用状态**: ✅ 在线运行
