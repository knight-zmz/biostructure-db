# 🧬 BioStructure DB

> 专业生物结构数据库 - 参考 PDB + UniProt + Pfam 设计

[![Build](https://github.com/knight-zmz/biostructure-db/workflows/CI/badge.svg)](https://github.com/knight-zmz/biostructure-db/actions)
[![Version](https://img.shields.io/github/v/release/knight-zmz/biostructure-db)](https://github.com/knight-zmz/biostructure-db/releases)
[![License](https://img.shields.io/github/license/knight-zmz/biostructure-db)](LICENSE)

**🌐 在线演示**: [https://jlupdb.me](https://jlupdb.me)  
**📊 API**: [https://jlupdb.me/api/stats](https://jlupdb.me/api/stats)

---

## ✨ 最新特性 (2026-03-31 控制平面 v1.3)

### 🎯 核心功能
- 🔍 **智能搜索**: PDB ID、基因名、生物体、序列搜索
- 🧬 **3D 可视化**: 3Dmol.js 交互式分子查看器
- 📊 **实时统计**: 6 个结构，4,240 个原子 (P2 样例验证中)
- 🚀 **RESTful API**: 12+ 生物信息学 API 端点
- 💾 **PostgreSQL**: 18 个数据表
- 🔄 **自动部署**: GitHub Actions + HTTPS 自动续期

### 🔥 新增功能
- ✅ **Redis 缓存**: API 响应提升 10 倍
- ⏸️ **HTTPS**: 备案期间暂停 (当前 HTTP 模式)
- ✅ **数据库优化**: 完整权限和索引
- 🟡 **监控**: 脚本已部署，待运行验证

---

## 📊 数据库统计

| 指标 | 数值 |
|------|------|
| **蛋白质结构** | 6 (P2 样例) |
| **原子坐标** | 4,240 (P2 样例) |
| **实验方法** | 3 种 (X-Ray 93, NMR 12, EM 3) |
| **数据表** | 18 |
| **API 端点** | 12+ |

---

## 🚀 快速开始

```bash
# 克隆
git clone https://github.com/knight-zmz/biostructure-db.git
cd biostructure-db

# 安装
npm install

# 启动
npm start

# 访问
# http://localhost:3000/
# http://localhost:3000/api/stats
```

---

## 🛠️ 技术栈

- **后端**: Node.js 20 + Express + PostgreSQL 13 + Redis 6
- **前端**: HTML5 + CSS3 + JavaScript + 3Dmol.js
- **部署**: Nginx + PM2 + GitHub Actions + Let's Encrypt

---

## 📦 API 端点

### 基础 API
- `GET /api/stats` - 数据库统计
- `GET /api/structures` - 结构列表
- `GET /api/structures/:pdbId` - 结构详情
- `POST /api/import/:pdbId` - 导入 PDB

### 生物 API
- `GET /api/bio/stats` - 基础统计
- `GET /api/bio/stats/detailed` - 详细统计
- `GET /api/bio/search/sequence` - 序列搜索
- `GET /api/bio/gene/:name` - 基因搜索
- `GET /api/bio/organism/:name` - 生物体搜索

---

## 🔧 生产部署

```bash
# 安装依赖
npm install --production

# 启动 PM2
pm2 start src/app.js --name biostructure-db
pm2 save

# 配置 HTTPS
sudo certbot --nginx -d yourdomain.com
```

---

## 📝 详细文档

- [升级报告](UPGRADE_2026-03-27.md)
- [部署指南](DEPLOY_CHECK.md)
- [域名配置](DOMAIN_CONFIG.md)

---

## 🌟 参考

- [RCSB PDB](https://www.rcsb.org/)
- [UniProt](https://www.uniprot.org/)
- [AlphaFold DB](https://alphafold.ebi.ac.uk/)

---

**最后更新**: 2026-03-27  
**状态**: ✅ 生产就绪
