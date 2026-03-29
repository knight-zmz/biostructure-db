# 📊 Project State - 项目状态盘点

**生成时间**: 2026-03-29 22:56 CST  
**项目**: biostructure-db  
**版本**: 1.0.0

---

## 1. 项目概述

**定位**: 专业生物结构数据库 - 参考 PDB + UniProt + Pfam 设计

**核心功能**:
- PDB 结构存储与查询
- 原子坐标管理
- 序列搜索
- 3D 分子可视化
- RESTful API

---

## 2. 目录结构

```
biostructure-db/
├── src/
│   ├── app.js                 # 主应用入口 (21KB)
│   ├── mcp-server.js          # MCP 服务器
│   ├── api/
│   │   └── bioapi.js          # 生物 API 实现
│   ├── db/
│   │   └── schema.sql         # 数据库 schema (13KB)
│   ├── middleware/            # 中间件目录
│   └── utils/
│       ├── pdb-parser.js      # PDB 解析器
│       └── redis-cache.js     # Redis 缓存工具
├── public/
│   ├── index.html             # 主页面 (55KB)
│   ├── index.html.bak         # 备份
│   ├── index.html.gz          # 压缩版
│   ├── viewer.html            # 3D 查看器
│   └── pages/                 # 子页面
├── tests/
│   └── unit/
│       ├── api.test.js
│       └── pdb-parser.test.js
├── scripts/                   # 运维脚本 (15 个)
├── docs/                      # 文档
├── .github/
│   └── workflows/
│       └── deploy.yml         # GitHub Actions 部署
├── node_modules/              # 依赖 (92 个包)
├── package.json               # 项目配置
├── package-lock.json          # 依赖锁定
├── ecosystem.config.js        # PM2 配置
├── schema.sql                 # 根目录 schema 副本
├── jest.config.js             # Jest 测试配置
├── .eslintrc.json             # ESLint 配置
├── .prettierrc                # Prettier 配置
└── ops/                       # 运维文档 (新建)
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

### 开发依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| jest | ^29.7.0 | 测试框架 |
| eslint | ^8.50.0 | 代码检查 |
| prettier | ^3.0.0 | 代码格式化 |
| nodemon | ^3.0.0 | 开发热重载 |

### 引擎要求

```json
"engines": {
  "node": ">=20.0.0"
}
```

**当前环境**: Node v24.14.0 ✅ 满足要求

---

## 4. 数据库 Schema (18 表)

从 `src/db/schema.sql` 确认:

| 表名 | 用途 |
|------|------|
| structures | 结构主表 (PDB ID, 标题，分辨率等) |
| authors | 作者表 |
| chains | 肽链表 |
| residues | 残基表 |
| atoms | 原子坐标表 (核心) |
| ligands | 配体表 |
| secondary_structures | 二级结构表 |
| ... | (其他 11 个表) |

**注**: 完整 schema 需查看 `src/db/schema.sql`

---

## 5. API 端点清单

从 `src/app.js` 提取:

### 基础 API
- `GET /api/health` - 健康检查
- `GET /api/docs` - API 文档
- `GET /api/stats` - 统计概览
- `GET /api/structures` - 结构列表
- `GET /api/structures/:pdbId` - 结构详情
- `GET /api/structures/:pdbId/atoms` - 原子坐标
- `GET /api/structures/:pdbId/residues` - 残基序列
- `GET /api/structures/:pdbId/secondary-structure` - 二级结构
- `GET /api/structures/recent/list` - 最近沉积
- `GET /api/search` - 搜索结构
- `GET /api/search/suggest` - 搜索补全
- `POST /api/structures` - 创建/更新结构
- `POST /api/import/:pdbId` - 从 RCSB 导入
- `POST /api/import-samples` - 批量导入示例
- `GET /api/compare` - 结构对比
- `GET /api/cache/stats` - 缓存统计
- `DELETE /api/cache/clear` - 清除缓存

### 生物 API (/api/bio/*)
- `GET /api/bio/stats` - 统计概览
- `GET /api/bio/stats/detailed` - 详细统计
- `GET /api/bio/info` - 数据库信息
- `GET /api/bio/search/sequence` - 序列搜索
- `GET /api/bio/structure/:pdbId/full` - 完整结构
- `GET /api/bio/uniprot/:pdbId` - UniProt 映射
- `GET /api/bio/ligands/:pdbId` - 配体信息
- `GET /api/bio/organism/:name` - 按生物体搜索
- `GET /api/bio/gene/:name` - 按基因搜索
- `GET /api/bio/activesite/:pdbId` - 活性位点
- `GET /api/bio/pfam/:pdbId` - Pfam 结构域
- `GET /api/bio/secondary/:pdbId` - 二级结构
- `GET /api/bio/search/structure` - 通用搜索
- `GET /api/bio/search/ligand` - 配体搜索
- `GET /api/bio/health` - 健康检查

---

## 6. 现有文档清单

| 文件 | 用途 |
|------|------|
| README.md | 项目说明 |
| QUICK_START.md | 快速开始 |
| DEPLOY_CHECK.md | 部署检查 |
| DEPLOYMENT_STATUS.md | 部署状态 (历史) |
| DEPLOYMENT_SUCCESS.md | 部署成功记录 |
| DOMAIN_CONFIG.md | 域名配置 |
| DOMAIN_SETUP.md | 域名设置 |
| FEATURES.md | 功能列表 |
| ACCESS_GUIDE.md | 访问指南 |
| CONTRIBUTING.md | 贡献指南 |
| GITHUB_GUIDE.md | GitHub 指南 |
| SSH_TROUBLESHOOTING.md | SSH 故障排除 |
| UPGRADE_2026-03-27.md | 升级记录 |
| UPGRADE_REPORT.md | 升级报告 |
| WEEKLY_PLAN.md | 周计划 |
| WORK_STATE.json | 工作状态 |
| ... | (更多历史文档) |

---

## 7. 运维脚本清单 (scripts/)

| 脚本 | 用途 |
|------|------|
| auto-check-and-fix.sh | 自动检查修复 |
| auto-improve.sh | 自动改进 |
| autonomous-worker.sh | 自主工作 |
| auto-push.sh | 自动推送 |
| auto-sync-github.sh | GitHub 同步 |
| batch-import.sh | 批量导入 |
| configure-git-auth.sh | Git 认证配置 |
| db-maintenance.sh | 数据库维护 |
| git-setup.sh | Git 设置 |
| health-check.sh | 健康检查 |
| import-pdb-batch.sh | PDB 批量导入 |
| import-pdb.sh | PDB 导入 |
| install-gh.sh | 安装 GitHub CLI |
| optimize-db.sql | 数据库优化 |
| publish-to-github.sh | 发布到 GitHub |
| service-health.sh | 服务健康检查 |
| test-api.sh | API 测试 |

---

## 8. 配置状态

### PM2 配置 (ecosystem.config.js)

```javascript
{
  name: 'myapp',
  script: 'src/app.js',
  instances: 1,
  autorestart: true,
  max_memory_restart: '200M',
  env: {
    NODE_ENV: 'production',
    PORT: 3000
  }
}
```

### 数据库配置 (硬编码在 app.js)

```javascript
{
  user: 'myapp_user',
  host: 'localhost',
  database: 'myapp',
  password: 'MyApp@2026',
  port: 5432
}
```

### Redis 配置 (redis-cache.js)

```javascript
{
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379
}
```

---

## 9. 测试覆盖

| 测试文件 | 内容 |
|----------|------|
| tests/unit/api.test.js | API 测试 |
| tests/unit/pdb-parser.test.js | PDB 解析器测试 |

**测试命令**: `npm test` (Jest)

---

## 10. 历史部署信息

从历史文档提取:

- **在线演示**: https://jlupdb.me (需验证)
- **曾部署状态**: Nginx + PM2 + PostgreSQL + Redis
- **数据规模**: 108 个结构，740,010 个原子
- **部署目标**: `/var/www/myapp`

**注意**: 当前服务器为重装后的干净 ECS，上述为历史记录。

---

## 11. 项目健康度评估

| 维度 | 状态 | 评分 |
|------|------|------|
| 代码完整性 | ✅ 完整 | 5/5 |
| 依赖安装 | ✅ 已完成 | 5/5 |
| 文档完整性 | ✅ 丰富 | 5/5 |
| 测试覆盖 | ⚠️ 基础 | 3/5 |
| 环境就绪 | ❌ 缺失 DB/Redis | 2/5 |
| 部署链路 | ⚠️ 需验证 | 3/5 |

**综合评分**: 23/30 (77%)

---

## 12. 风险点

1. **数据库配置硬编码** - 密码明文在代码中
2. **无 .env 文件** - 配置无法灵活调整
3. **无容器化** - 依赖手动安装
4. **历史文档与实际不符** - 需清理更新

---

**下一步**: 创建 `ops/backlog.md` 记录待办事项。
