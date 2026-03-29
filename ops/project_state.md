# 📊 Project State - 项目状态盘点

**生成时间**: 2026-03-29 22:56 CST  
**更新时间**: 2026-03-30 00:38 CST  
**项目**: biostructure-db  
**版本**: 1.0.0  
**当前阶段**: 部署闭环已建立，进入工程完善阶段

---

## 0. 当前状态总览

### 0.1 已完成闭环

| 闭环项 | 状态 | 验证时间 | 复验 |
|--------|------|----------|------|
| PostgreSQL 安装与初始化 | ✅ 已验证 | 2026-03-29 22:59 | - |
| Redis 安装与启动 | ✅ 已验证 | 2026-03-29 23:00 | - |
| PM2 安装与配置 | ✅ 已验证 | 2026-03-29 23:01 | - |
| 环境变量配置 (.env/.env.example) | ✅ 已验证 | 2026-03-29 23:19 | - |
| 代码移除硬编码密码 | ✅ 已验证 | 2026-03-29 23:37 | - |
| 移除 fallback 默认密码 | ✅ 已验证 | 2026-03-29 23:37 | - |
| SSH 公钥授权 | ✅ 已验证 | 2026-03-29 23:51 | - |
| rsync 安装 | ✅ 已验证 | 2026-03-30 00:27 | - |
| GitHub Actions 部署闭环 | ✅ 已验证 | 2026-03-30 00:29 | ✅ 复验通过 (00:38) |
| 应用健康检查 | ✅ 已验证 | 持续通过 | - |
| 目录规范明确 | ✅ 已验证 | 2026-03-29 23:40 | - |
| 失败恢复文档 | ✅ 已验证 | 2026-03-29 23:45 | - |
| pg_hba.conf 配置脚本 | ✅ 已验证 | 2026-03-29 23:38 | - |

### 0.2 后续维护项

| 项目 | 优先级 | 说明 |
|------|--------|------|
| Node.js 20 deprecation | 🟢 低 | GitHub Actions 使用 Node.js 20 (2026-04-30 EOL)，当前为警告非阻塞 |
| 历史文档归档 | 🟢 低 | 根目录 30+ 历史文档可归档到 docs/archive/ |

### 0.3 当前最大阻塞

**✅ 无阻塞项**

**部署闭环状态**: ✅ 已建立并复验通过 (连续 2 次成功)

### 0.4 下一阶段优先事项

1. 🟡 配置数据库自动备份
2. 🟡 配置基础监控告警
3. 🟢 样例数据导入 / 数据源接入准备
4. 🟢 可选：升级 Node.js 版本 (20→22)

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
| workflow 文件 | ✅ 已验证 | `.github/workflows/deploy.yml` 存在 |
| SSH 公钥授权 | ✅ 已验证 | 已添加到 `~/.ssh/authorized_keys` |
| workflow 触发 | ✅ 已验证 | 连续 3 次推送均触发 |
| SSH 连接 | ✅ 已验证 | SSH 已建立 (日志确认) |
| Deploy via SSH | ✅ 已验证 | rsync 3.1.3 已安装，部署成功 |
| Restart PM2 | ✅ 已验证 | PM2 restarts=4 |
| 部署闭环 | ✅ 已验证 | 连续 2 次复验成功 |

**部署验证历史**:
| 测试 | 提交 | 时间 | restarts | 结果 |
|------|------|------|----------|------|
| 测试 1 | 9121d66 | 23:35 | 1→1 | 🔴 失败 (rsync not found) |
| 测试 2 | dc430c7 | 00:28 | 1→2 | ✅ 成功 (rsync 安装后) |
| 测试 3 | fc5599e | 00:37 | 2→4 | ✅ 成功 (复验通过) |

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
| 部署链路 | 🔴 候选原因待定位 | 3/5 |

**综合评分**: 31/35 (89%)

---

## 11. 风险清单

| 风险 | 等级 | 状态 |
|------|------|------|
| Node.js 20 deprecation 警告 | 🟢 低 | 后续维护项，当前为警告非阻塞 |
| 无自动备份 | 🟡 中 | 建议配置 (下一阶段 P1) |
| 无监控告警 | 🟡 中 | 建议配置 (下一阶段 P1) |
| 历史文档混乱 | 🟢 低 | 可归档清理 (后续维护) |

**已消除风险**:
- ✅ 数据库密码硬编码 (已移除)
- ✅ fallback 默认密码 (已移除)
- ✅ SSH 公钥未授权 (已修复)
- ✅ pg_hba.conf 手动配置 (已脚本化)
- ✅ 配置无 .env 文件 (已创建)
- ✅ GitHub Secrets 配置 (SSH 已连接，说明配置正确)
- ✅ 服务器缺少 rsync (已安装 3.1.3)
- ✅ GitHub Actions 部署闭环 (已验证并复验)

---

## 12. 下一阶段优先事项

### 🟡 P1: 工程完善 (建议配置)

1. **配置数据库自动备份**
   - 创建备份脚本
   - 配置 cron 定时任务
   - 设置备份保留策略 (7 天)
   - 优先级：中

2. **配置基础监控告警**
   - PM2 监控 (`pm2 monit`)
   - 系统资源监控 (CPU/内存/磁盘)
   - 服务宕机告警
   - 优先级：中

### 🟢 P2: 数据准备 (可选)

3. **样例数据导入 / 数据源接入准备**
   - 准备示例 PDB 数据
   - 测试导入脚本
   - 验证 API 返回数据
   - 优先级：低

### 🟢 P3: 后续维护

4. **Node.js 版本升级** (20→22)
   - GitHub Actions 使用 Node.js 20 (2026-04-30 EOL)
   - 当前为警告，非阻塞
   - 建议后续升级到 Node.js 22 LTS
   - 优先级：低

5. **历史文档归档**
   - 根目录 30+ 历史文档归档到 `docs/archive/`
   - 优先级：低
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
