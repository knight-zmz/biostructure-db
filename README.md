# 🧬 BioStructure DB - 专业生物结构数据库

参考 **PDB + UniProt + Pfam** 设计的生物信息学数据库系统。

---

## 📦 技术栈

| 组件 | 技术 |
|------|------|
| **数据库** | PostgreSQL 13.23 (15 张表) |
| **后端** | Node.js + Express |
| **前端** | HTML5 + 3Dmol.js |
| **Web 服务器** | Nginx |
| **进程管理** | PM2 |

---

## 🗄️ 数据库设计 (参考主流数据库)

### 核心表 (类似 PDB)
- `structures` - 结构主表 (分辨率、实验方法、生物体)
- `polypeptides` - 多肽链 (完整序列、UniProt 关联)
- `residues` - 残基序列 (带二级结构注释)
- `atoms` - 原子坐标 (3D 结构)

### 功能注释表 (类似 UniProt)
- `active_sites` - 活性位点/结合位点
- `ptms` - 翻译后修饰 (磷酸化/糖基化)
- `ligands` - 小分子配体 (类似 PubChem)
- `metal_ions` - 金属离子

### 外部关联表
- `uniprot_mappings` - UniProt 数据库映射
- `pfam_domains` - Pfam 蛋白质结构域
- `citations` - 文献引用 (PubMed 关联)

---

## 🔌 API 接口

### 基础 API
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/structures` | GET | 获取结构列表 |
| `/api/structures/:pdbId` | GET | 获取结构详情 |
| `/api/structures/:pdbId/atoms` | GET | 获取原子坐标 |
| `/api/import/:pdbId` | POST | 从 RCSB 导入 |

### 生物信息学 API (新增)
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/bio/search/sequence` | GET | 序列搜索 |
| `/api/bio/search/structure` | GET | 结构搜索 (分辨率/方法) |
| `/api/bio/search/ligand` | GET | 配体搜索 |
| `/api/bio/structure/:pdbId/full` | GET | 完整结构信息 |
| `/api/bio/uniprot/:pdbId` | GET | UniProt 映射 |
| `/api/bio/organism/:name` | GET | 按生物体搜索 |
| `/api/bio/gene/:name` | GET | 按基因名搜索 |
| `/api/bio/activesite/:pdbId` | GET | 活性位点详情 |
| `/api/bio/stats/detailed` | GET | 详细统计 |

---

## 🎨 前端功能

### 核心功能
- ✅ 结构列表展示
- ✅ 实时搜索 (PDB ID/名称)
- ✅ 3D 分子可视化 (3Dmol.js)
- ✅ 多种显示样式

### 生物信息学功能 (新增)
- ✅ 从 RCSB 导入真实结构
- ✅ 按生物体搜索 (如：Homo sapiens)
- ✅ 按基因名搜索 (如：TP53, BRCA1)
- ✅ 配体结合信息展示
- ✅ 活性位点注释
- ✅ 翻译后修饰展示
- ✅ 统计仪表盘

---

## 📊 示例数据

```sql
-- 导入示例结构
POST /api/import-samples

-- 导入单个 PDB
POST /api/import/1CRN
```

### 已包含的示例
- **1CRN** - Crambin (植物蛋白)
- **1UBQ** - 泛素 (人类)
- **1TIM** - 磷酸丙糖异构酶
- **1BNA** - DNA 十二聚体
- **4HHB** - 血红蛋白

---

## 🔐 数据库连接

```
Host: localhost
Port: 5432
Database: myapp
User: myapp_user
Password: MyApp@2026
```

---

## 🚀 使用示例

### 1. 序列搜索
```bash
curl "http://<IP>/api/bio/search/sequence?sequence=PLA"
```

### 2. 按基因名搜索
```bash
curl "http://<IP>/api/bio/gene/TP53"
```

### 3. 按生物体搜索
```bash
curl "http://<IP>/api/bio/organism/Homo%20sapiens"
```

### 4. 获取完整结构信息
```bash
curl "http://<IP>/api/bio/structure/1CRN/full"
```

### 5. 查看 UniProt 映射
```bash
curl "http://<IP>/api/bio/uniprot/1CRN"
```

---

## 📁 项目目录

```
/var/www/myapp/
├── app.js              # Express 主应用
├── bioapi.js           # 生物信息学 API 模块
├── pdb-parser.js       # PDB 文件解析器
├── mcp-server.js       # MCP 服务器 (AI 直接访问)
├── package.json        # Node.js 依赖
├── schema.sql          # 基础数据库 Schema
├── schema_v2.sql       # 增强版 Schema
├── public/
│   └── index.html      # 前端页面
└── README.md           # 本文档

~/.openclaw/workspace/skills/biostructure-db/
├── SKILL.md            # 技能定义
├── import-samples.sh   # 批量导入脚本
├── export-data.sh      # 数据导出脚本
└── sequence_tools.py   # 序列分析工具
```

---

## 🌐 访问地址

- **前端**: http://<服务器 IP>/
- **API**: http://<服务器 IP>/api/bio/stats/detailed

---

## 💡 可扩展功能

1. **AlphaFold DB 集成** - 导入预测结构
2. **BLAST 序列比对** - 集成 NCBI BLAST
3. **结构比对** - RMSD 计算
4. **分子对接** - AutoDock Vina 集成
5. **通路可视化** - KEGG/Reactome 集成
6. **变异效应预测** - SIFT/PolyPhen

---

## 📚 参考数据库

| 数据库 | URL | 用途 |
|--------|-----|------|
| PDB | https://www.rcsb.org | 蛋白质 3D 结构 |
| UniProt | https://www.uniprot.org | 蛋白质序列/功能 |
| Pfam | https://www.ebi.ac.uk/interpro | 蛋白质结构域 |
| PubChem | https://pubchem.ncbi.nlm.nih.gov | 小分子化合物 |
| NCBI | https://www.ncbi.nlm.nih.gov | 综合生物信息 |

---

**Built with 🦞 OpenClaw | 参考 PDB + UniProt + Pfam 设计**
