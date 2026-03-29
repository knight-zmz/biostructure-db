# 📊 Project State - 项目状态盘点

**生成时间**: 2026-03-29 22:56 CST  
**更新时间**: 2026-03-30 00:00 CST  
**项目**: biostructure-db  
**版本**: 1.0.0  
**当前阶段**: 文档一致性收口 (Round 5)

---

## 0. 当前状态总览

### 0.1 已完成闭环

| 闭环项 | 状态 | 验证时间 |
|--------|------|----------|
| PostgreSQL 安装与初始化 | ✅ 已验证 | 2026-03-29 22:59 |
| Redis 安装与启动 | ✅ 已验证 | 2026-03-29 23:00 |
| PM2 安装与配置 | ✅ 已验证 | 2026-03-29 23:01 |
| 环境变量配置 (.env/.env.example) | ✅ 已验证 | 2026-03-29 23:19 |
| 代码移除硬编码密码 | ✅ 已验证 | 2026-03-29 23:37 |
| 移除 fallback 默认密码 | ✅ 已验证 | 2026-03-29 23:37 |
| 应用健康检查 | ✅ 已验证 | 持续通过 |
| 目录规范明确 | ✅ 已验证 | 2026-03-29 23:40 |
| 失败恢复文档 | ✅ 已验证 | 2026-03-29 23:45 |
| pg_hba.conf 配置脚本 | ✅ 已验证 | 2026-03-29 23:38 |
| SSH 公钥授权 | ✅ 已验证 | 2026-03-29 23:51 |

### 0.2 未完成闭环

| 闭环项 | 状态 | 阻塞原因 |
|--------|------|----------|
| GitHub Secrets 配置 | 🔴 尚未解决 | 需用户在 GitHub Settings 配置 |
| GitHub Actions 完整部署 | 🔴 尚未解决 | 依赖 Secrets 配置 |
| 自动部署后 PM2 重启 | 🔴 尚未解决 | 依赖上述两项 |

### 0.3 当前最大阻塞

**🔴 GitHub Secrets 未配置**

**需要配置的 Secrets**:

| Secret 名 | 用途 | 获取方式 |
|----------|------|----------|
| `DEPLOY_SSH_KEY` | SSH 私钥 | `cat ~/.ssh/biostructure_db_deploy` |
| `DEPLOY_HOST` | 服务器公网 IP | 阿里云 ECS 控制台 |
| `DEPLOY_USER` | SSH 用户 | `admin` (固定值) |

**已修复项**:
- ✅ SSH 公钥已添加到 `~/.ssh/authorized_keys` (2026-03-29 23:51)

**影响**: GitHub Actions 无法 SSH 连接到服务器，部署流程失败

**配置位置**: https://github.com/knight-zmz/biostructure-db/settings/secrets/actions

### 0.4 下一轮优先事项

1. 🔴 用户配置 GitHub Secrets (DEPLOY_SSH_KEY, DEPLOY_HOST, DEPLOY_USER)
2. 🔴 重新触发 GitHub Actions 部署测试
3. 🔴 验证 PM2 自动重启
4. 🟡 同步所有文档到生产目录
5. 🟡 清理历史过时文档

---

## 1. 项目概述

**定位**: 专业生物结构数据库 - 参考 PDB + UniProt + Pfam 设计

**核心功能**:
- PDB 结构存储与查询
- 原子坐标管理
- 序列搜索
- 3D 分子可视化
- RESTful API

**运行环境**:
- **生产路径**: `/var/www/myapp`
- **开发路径**: `/home/admin/biostructure-db`
- **进程管理**: PM2
- **数据库**: PostgreSQL 13.23
- **缓存**: Redis 6.2.20 (可选)

---

## 2. 目录结构

```
biostructure-db/
├── src/
│   ├── app.js                 # 主应用入口 (使用环境变量)
│   ├── mcp-server.js          # MCP 服务器 (使用环境变量)
│   ├── api/
│   │   └── bioapi.js          # 生物 API 实现 (使用环境变量)
│   ├── db/
│   │   └── schema.sql         # 数据库 schema (支持幂等执行)
│   ├── middleware/            # 中间件目录
│   └── utils/
│       ├── pdb-parser.js      # PDB 解析器
│       └── redis-cache.js     # Redis 缓存工具 (使用环境变量)
├── public/                    # 静态文件
├── tests/unit/                # 单元测试
├── scripts/                   # 运维脚本
│   ├── init-db.sh             # 数据库初始化 (幂等)
│   ├── configure-pg_hba.sh    # pg_hba.conf 配置
│   └── ...
├── .github/workflows/
│   └── deploy.yml             # GitHub Actions 部署
├── ops/                       # 运维文档 (13 个文件)
├── .env                       # 环境变量配置 (不提交)
├── .env.example               # 配置模板 (可提交)
├── ecosystem.config.js        # PM2 配置 (使用 dotenv)
└── package.json               # 项目配置
```

---

## 3. 技术栈详情

### 后端依赖 (package.json)

| 依赖 | 版本 | 用途 |
|------|------|------|
| express | ^4.18.2 | Web 框架 |
| pg | ^8.11.3 | PostgreSQL 客户端 |
| ioredis | ^5.10.1 | Redis 客户端 |
| axios | ^1.6.0 | HTTP 客户端 |
| cors | ^2.8.5 | CORS 中间件 |
| dotenv | ^17.3.1 | 环境变量加载 |

### 开发依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| jest | ^29.7.0 | 测试框架 |
| eslint | ^8.50.0 | 代码检查 |
| prettier | ^3.0.0 | 代码格式化 |

### 引擎要求

```json
"engines": {
  "node": ">=20.0.0"
}
```

**当前环境**: Node v24.14.0 ✅ 满足要求

---

## 4. 数据库 Schema

**文件**: `src/db/schema.sql` (336 行)

**表数量**: 15 个核心表

| 表名 | 用途 |
|------|------|
| structures | 结构主表 |
| assemblies | 生物组装表 |
| entities | 分子实体表 |
| polypeptides | 多肽链 |
| residues | 残基表 |
| atoms | 原子坐标表 (核心) |
| ligands | 配体表 |
| secondary_structures | 二级结构表 |
| active_sites | 活性位点 |
| pfam_domains | Pfam 结构域 |
| uniprot_mappings | UniProt 映射 |
| sequence_index | 序列索引 |
| citations | 引用文献 |
| ptms | 翻译后修饰 |
| metal_ions | 金属离子 |

**特性**:
- ✅ 所有 CREATE TABLE 使用 `IF NOT EXISTS`
- ✅ 所有 CREATE INDEX 使用 `IF NOT EXISTS`
- ✅ 支持重复执行 (幂等)

---

## 5. 配置状态

### 5.1 环境变量 (.env)

```bash
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=myapp
DB_USER=myapp_user
DB_PASSWORD=MyApp@2026
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
NODE_ENV=production
PORT=3000
```

### 5.2 代码配置方式

**src/app.js** (第 14-22 行):
```javascript
if (!process.env.DB_PASSWORD) {
  throw new Error('DB_PASSWORD environment variable is required');
}

const pool = new Pool({
  user: process.env.DB_USER || 'myapp_user',
  host: process.env.DB_HOST || '127.0.0.1',
  database: process.env.DB_NAME || 'myapp',
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT || 5432,
});
```

**状态**: ✅ 无硬编码密码，使用环境变量

### 5.3 PM2 配置 (ecosystem.config.js)

```javascript
require('dotenv').config();

module.exports = {
  apps: [{
    name: 'myapp',
    script: 'src/app.js',
    env: {
      NODE_ENV: process.env.NODE_ENV || 'production',
      PORT: process.env.PORT || 3000,
      DB_HOST: process.env.DB_HOST,
      DB_PASSWORD: process.env.DB_PASSWORD,
      // ...
    }
  }]
};
```

---

## 6. 运行状态

| 组件 | 状态 | 验证命令 |
|------|------|----------|
| PostgreSQL 13.23 | ✅ 运行中 | `pg_isready` |
| Redis 6.2.20 | ✅ 运行中 | `redis-cli ping` |
| PM2 6.0.14 | ✅ 运行中 | `pm2 list` |
| 应用 (myapp) | ✅ online | `curl /api/health` |

**当前进程**:
```
│ id │ name  │ status  │ uptime │ restarts │
│ 0  │ myapp │ online  │ 16m    │ 1        │
```

**健康检查**:
```json
{"success":true,"status":"healthy","database":"connected"}
```

---

## 7. 部署状态

### 7.1 部署路径

| 项目 | 路径 | 状态 |
|------|------|------|
| 生产运行目录 | `/var/www/myapp` | ✅ 一致 |
| 开发工作目录 | `/home/admin/biostructure-db` | ✅ 保留 |
| GitHub Actions 目标 | `/var/www/myapp` | ✅ 一致 |
| PM2 工作目录 | `/var/www/myapp` | ✅ 一致 |

### 7.2 GitHub Actions 状态

| 验证项 | 状态 | 说明 |
|--------|------|------|
| workflow 文件 | ✅ 已配置 | `.github/workflows/deploy.yml` |
| SSH 公钥授权 | ✅ 已修复 | 已添加到 authorized_keys |
| Secrets 配置 | 🔴 未配置 | 需用户手动配置 |
| 部署闭环 | 🔴 未验证 | 依赖 Secrets |

---

## 8. 文档体系 (ops/)

| 文件 | 用途 | 状态 |
|------|------|------|
| `project_state.md` | 项目总状态 | ✅ 已更新 |
| `backlog.md` | 待办事项 | ✅ 已更新 |
| `runbook.md` | 运维手册 | ✅ 已更新 |
| `COLD_START_ACCEPTANCE.md` | 冷启动验收 | ✅ 完成 |
| `NORMALIZATION_REPORT.md` | 规范化收口 | ✅ 完成 |
| `VERIFICATION_REPORT.md` | 结果验证 | ✅ 完成 |
| `GITHUB_ACTIONS 闭环验证报告.md` | 部署验证 | ✅ 完成 |
| `DIRECTORY_POLICY.md` | 目录规范 | ✅ 完成 |
| `bootstrap_assessment.md` | 环境盘点 | ✅ 完成 |
| `lessons_learned.md` | 经验教训 | ✅ 完成 |
| `gap_analysis.md` | 缺口分析 | ✅ 完成 |
| `install_order.md` | 安装顺序 | ✅ 完成 |
| `minimum_startup_path.md` | 启动路径 | ✅ 完成 |

**总计**: 13 个文档

---

## 9. 脚本工具 (scripts/)

| 脚本 | 用途 | 状态 |
|------|------|------|
| `init-db.sh` | 数据库初始化 (幂等) | ✅ 完成 |
| `configure-pg_hba.sh` | pg_hba.conf 配置 | ✅ 完成 |
| `health-check.sh` | 健康检查 | ✅ 已有 |
| `test-api.sh` | API 测试 | ✅ 已有 |
| `auto-push.sh` | 自动推送 | ✅ 已有 |

---

## 10. 项目健康度评估

| 维度 | 状态 | 评分 |
|------|------|------|
| 代码完整性 | ✅ 完整 | 5/5 |
| 依赖安装 | ✅ 已完成 | 5/5 |
| 文档完整性 | ✅ 丰富 (13 个 ops 文档) | 5/5 |
| 测试覆盖 | ⚠️ 基础 (2 个单元测试) | 3/5 |
| 环境就绪 | ✅ PostgreSQL+Redis+PM2 | 5/5 |
| 配置规范化 | ✅ 环境变量 + 无硬编码 | 5/5 |
| 部署链路 | ⏳ Secrets 待配置 | 3/5 |

**综合评分**: 31/35 (89%)

---

## 11. 风险清单

| 风险 | 等级 | 状态 |
|------|------|------|
| GitHub Secrets 未配置 | 🔴 高 | 阻塞部署闭环 |
| 无 Nginx 反向代理 | 🟢 低 | 可选，非必需 |
| 无自动备份 | 🟡 中 | 建议配置 |
| 无监控告警 | 🟡 中 | 建议配置 |
| 历史文档混乱 | 🟢 低 | 可归档清理 |

**已消除风险**:
- ✅ 数据库密码硬编码 (已移除)
- ✅ fallback 默认密码 (已移除)
- ✅ SSH 公钥未授权 (已修复)
- ✅ pg_hba.conf 手动配置 (已脚本化)
- ✅ 配置无 .env 文件 (已创建)

---

## 12. 下一步优先事项

### 🔴 P0: 用户配置 GitHub Secrets

访问 https://github.com/knight-zmz/biostructure-db/settings/secrets/actions 配置:
- `DEPLOY_SSH_KEY` = `cat ~/.ssh/biostructure_db_deploy`
- `DEPLOY_HOST` = 服务器公网 IP
- `DEPLOY_USER` = `admin`

### 🔴 P0: 验证部署闭环

```bash
# 推送测试提交
echo "# Deploy Test $(date)" > .github_deploy_test_3.md
git add . && git commit -m "test: deploy verification 3" && git push

# 等待 90 秒
sleep 90

# 验证 PM2 重启
pm2 describe myapp | grep restarts  # 应从 1 变为 2
```

### 🟡 P1: 文档同步

```bash
cp /home/admin/biostructure-db/ops/*.md /var/www/myapp/ops/
```

### 🟡 P1: 历史文档归档

```bash
mkdir -p docs/archive
mv DEPLOY_*.md UPGRADE_*.md WEEKLY_PLAN.md docs/archive/
```

---

**最后更新**: 2026-03-30 00:00 CST  
**状态**: ✅ 文档一致性已收敛  
**最大阻塞**: 🔴 GitHub Secrets 配置待用户完成
