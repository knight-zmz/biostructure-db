# 🧬 BioStructure DB - 完整系统总结

**专业生物结构数据库系统** - 参考 PDB + UniProt + Pfam + PubChem 设计

---

## 📦 完整技术栈

| 层级 | 组件 | 说明 |
|------|------|------|
| **数据库** | PostgreSQL 13.23 | 15 张表，支持数组/GIN 索引 |
| **后端** | Node.js + Express | RESTful API + MCP Server |
| **前端** | HTML5 + 3Dmol.js | 3D 分子可视化 |
| **Web 服务器** | Nginx | 反向代理 |
| **进程管理** | PM2 | 自动重启/监控 |
| **技能** | OpenClaw Skills | 可复用技能包 |
| **MCP** | Model Context Protocol | AI 直接访问数据库 |

---

## 🗄️ 数据库架构 (15 张表)

### 核心表 (PDB 风格)
- `structures` - 结构主表
- `polypeptides` - 多肽链 + 完整序列
- `residues` - 残基注释
- `atoms` - 原子坐标
- `assemblies` - 生物组装体
- `entities` - 分子实体

### 功能注释 (UniProt 风格)
- `active_sites` - 活性位点/结合位点
- `ptms` - 翻译后修饰
- `secondary_structures` - 二级结构
- `ligands` - 小分子配体 (PubChem 风格)
- `metal_ions` - 金属离子

### 外部关联
- `uniprot_mappings` - UniProt 映射
- `pfam_domains` - Pfam 结构域
- `citations` - 文献引用 (PubMed)
- `sequence_index` - 序列搜索索引

---

## 🔌 API 接口 (20+ 端点)

### 基础 API
```bash
GET  /api/structures                     # 结构列表
GET  /api/structures/:pdbId              # 结构详情
GET  /api/structures/:pdbId/atoms        # 原子坐标
POST /api/import/:pdbId                  # 从 RCSB 导入
POST /api/import-samples                 # 批量导入示例
```

### 生物信息学 API (/api/bio)
```bash
# 搜索
GET  /api/bio/search/sequence            # 序列搜索
GET  /api/bio/search/structure           # 结构搜索 (多条件)
GET  /api/bio/search/ligand              # 配体搜索

# 详情
GET  /api/bio/structure/:pdbId/full      # 完整结构信息
GET  /api/bio/uniprot/:pdbId             # UniProt 映射
GET  /api/bio/ligands/:pdbId             # 配体结合
GET  /api/bio/activesite/:pdbId          # 活性位点

# 分类浏览
GET  /api/bio/organism/:name             # 按生物体搜索
GET  /api/bio/gene/:name                 # 按基因名搜索

# 统计
GET  /api/bio/stats/detailed             # 详细统计
```

### MCP Server (AI 直接访问)
```javascript
// 工具列表
tools/list

// 工具调用
tools/call {
  name: "search_structures",
  arguments: { gene: "TP53", max_resolution: 2.0 }
}

tools/call {
  name: "get_structure_details",
  arguments: { pdb_id: "1CRN" }
}

tools/call {
  name: "search_sequence",
  arguments: { sequence: "PLAQ", exact: true }
}

tools/call {
  name: "get_stats"
}

tools/call {
  name: "search_ligands",
  arguments: { name: "ATP" }
}
```

---

## 🛠️ 技能工具 (~/.openclaw/workspace/skills/biostructure-db/)

### 1. 批量导入脚本
```bash
./import-samples.sh
# 导入 10 个示例结构
```

### 2. 数据导出脚本
```bash
./export-data.sh
# 导出为 CSV:
# - structures.csv
# - polypeptides.csv
# - ligands.csv
# - active_sites.csv
# - ptms.csv
# - uniprot_mappings.csv
# - pfam_domains.csv
```

### 3. 序列分析工具
```bash
# 计算分子量
python3 sequence_tools.py weight "PLAQ"

# 计算序列相似度
python3 sequence_tools.py similarity "PLAQ" "PLAA"

# 统计氨基酸组成
python3 sequence_tools.py count "PLAQ"
```

---

## 🎨 前端功能

### 核心功能
- ✅ 结构列表展示
- ✅ 实时搜索
- ✅ 3D 分子可视化 (3Dmol.js)
- ✅ 多种显示样式 (卡通/棍状/球棍/表面)

### 高级功能
- ✅ 高级搜索面板
  - 按基因名搜索
  - 按生物体搜索
  - 按实验方法筛选
  - 按分辨率筛选
- ✅ 从 RCSB 导入
- ✅ 批量导入示例

---

## 📊 使用示例

### 1. 导入结构
```bash
# 单个导入
curl -X POST http://localhost/api/import/1CRN

# 批量导入
curl -X POST http://localhost/api/import-samples

# 或使用脚本
cd ~/.openclaw/workspace/skills/biostructure-db
./import-samples.sh
```

### 2. 搜索结构
```bash
# 按基因名
curl "http://localhost/api/bio/gene/TP53"

# 按生物体
curl "http://localhost/api/bio/organism/Homo%20sapiens"

# 组合搜索
curl "http://localhost/api/bio/search/structure?method=X-RAY&maxRes=2.0&gene=kinase"
```

### 3. 获取完整信息
```bash
curl "http://localhost/api/bio/structure/1CRN/full"
```

返回:
```json
{
  "structure": {...},
  "chains": [...],
  "ligands": [...],
  "metal_ions": [...],
  "active_sites": [...],
  "ptms": [...],
  "pfam_domains": [...],
  "citations": [...]
}
```

### 4. 序列分析
```bash
# 计算分子量
python3 sequence_tools.py weight "MTEYKLVVVGAGGVGKSALTIQLIQ"
# 输出：{"molecular_weight": 3333.8, ...}

# 导出数据库
./export-data.sh
```

### 5. MCP 查询 (AI 使用)
```javascript
// AI 可以直接调用
const result = await mcp.call('search_structures', {
  gene: 'BRCA1',
  max_resolution: 2.5
});
```

---

## 🌐 访问地址

| 服务 | 地址 |
|------|------|
| **前端** | http://<服务器 IP>/ |
| **API** | http://<服务器 IP>/api/bio/stats/detailed |
| **MCP** | `node /var/www/myapp/mcp-server.js` |

---

## 📚 参考的生物数据库

| 数据库 | 借鉴功能 | 实现表/功能 |
|--------|----------|-------------|
| **PDB** | 3D 结构、实验方法 | structures, atoms, assemblies |
| **UniProt** | 序列注释、功能 | polypeptides, active_sites, ptms |
| **Pfam** | 结构域 | pfam_domains |
| **PubChem** | 小分子 | ligands (SMILES, InChI) |
| **NCBI** | 分类学、基因 | organism_scientific_name, gene_name |

---

## 🚀 可扩展功能

### 短期
- [ ] AlphaFold DB 集成
- [ ] SMILES 搜索
- [ ] 序列比对 (Clustal Omega)
- [ ] RMSD 计算
- [ ] 导出 PDB/mmCIF

### 中期
- [ ] BLAST 集成
- [ ] InterProScan
- [ ] STRING PPI 网络
- [ ] KEGG 通路
- [ ] 分子对接 (AutoDock)

### 长期
- [ ] AlphaFold2 本地部署
- [ ] MD 模拟 (GROMACS)
- [ ] 自由能计算
- [ ] 虚拟筛选
- [ ] 机器学习预测

---

## 💡 生物学家使用场景

### 场景 1: 查找特定蛋白的所有结构
```bash
# 搜索 TP53
GET /api/bio/gene/TP53

# 搜索人类来源
GET /api/bio/organism/Homo%20sapiens
```

### 场景 2: 分析酶的活性位点
```bash
# 获取活性位点
GET /api/bio/activesite/1CRN

# 获取配体结合信息
GET /api/bio/ligands/1CRN
```

### 场景 3: 研究翻译后修饰
```bash
# 获取完整结构 (包含 PTM)
GET /api/bio/structure/1CRN/full
```

### 场景 4: 药物发现
```bash
# 搜索含特定配体的结构
GET /api/bio/search/ligand?name=ATP

# 搜索结合位点
GET /api/bio/activesite/4HHB
```

---

## 🎯 系统优势

1. **专业性强** - 参考主流生物数据库设计
2. **功能完整** - 15 张表覆盖结构/序列/功能
3. **易于扩展** - 模块化设计
4. **性能优化** - PostgreSQL 索引 + 视图
5. **用户友好** - 3D 可视化 + 高级搜索
6. **AI 友好** - MCP Server 支持
7. **可复用** - OpenClaw Skills

---

## 📖 相关文档

- `/var/www/myapp/README.md` - 基础文档
- `/var/www/myapp/FEATURES.md` - 功能详情
- `/var/www/myapp/schema_v2.sql` - 数据库 Schema
- `~/.openclaw/workspace/skills/biostructure-db/SKILL.md` - 技能定义

---

**Built with 🦞 OpenClaw**

**参考设计**: PDB + UniProt + Pfam + PubChem + MCP
