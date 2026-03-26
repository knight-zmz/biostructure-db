# 🧬 BioStructure DB - 功能特性总结

参考 **PDB + UniProt + Pfam** 设计的专业生物结构数据库

---

## ✅ 已实现功能

### 🗄️ 数据库层 (PostgreSQL)

#### 核心表结构 (15 张表)
| 表名 | 参考 | 用途 |
|------|------|------|
| `structures` | PDB | 结构主表 (分辨率/方法/生物体) |
| `polypeptides` | UniProt | 多肽链 + 完整序列 |
| `residues` | PDB | 残基序列 + 二级结构 |
| `atoms` | PDB | 原子坐标 (3D 结构) |
| `assemblies` | PDB | 生物组装体 |
| `entities` | PDB | 分子实体 |
| `secondary_structures` | PDB | 二级结构注释 |
| `active_sites` | UniProt | 活性位点/结合位点 |
| `ligands` | PubChem | 小分子配体 |
| `metal_ions` | PDB | 金属离子 |
| `ptms` | UniProt | 翻译后修饰 |
| `uniprot_mappings` | UniProt | 外部数据库关联 |
| `pfam_domains` | Pfam | 蛋白质结构域 |
| `citations` | PubMed | 文献引用 |
| `sequence_index` | BLAST | 序列搜索索引 |

---

### 🔌 API 层 (Node.js + Express)

#### 基础 API
```bash
GET  /api/structures              # 结构列表
GET  /api/structures/:pdbId       # 结构详情
GET  /api/structures/:pdbId/atoms # 原子坐标
POST /api/import/:pdbId           # 从 RCSB 导入
POST /api/import-samples          # 批量导入示例
```

#### 生物信息学 API (bioapi.js)
```bash
# 搜索功能
GET  /api/bio/search/sequence     # 序列搜索
GET  /api/bio/search/structure    # 结构搜索 (分辨率/方法/生物体/基因)
GET  /api/bio/search/ligand       # 配体搜索

# 详情查询
GET  /api/bio/structure/:pdbId/full    # 完整结构信息
GET  /api/bio/uniprot/:pdbId           # UniProt 映射
GET  /api/bio/ligands/:pdbId           # 配体结合信息
GET  /api/bio/activesite/:pdbId        # 活性位点详情

# 分类浏览
GET  /api/bio/organism/:name    # 按生物体搜索
GET  /api/bio/gene/:name        # 按基因名搜索

# 统计
GET  /api/bio/stats/detailed    # 详细统计信息
```

---

### 🎨 前端功能

#### 核心功能
- ✅ 结构列表展示 (卡片式)
- ✅ 实时搜索 (PDB ID/名称)
- ✅ 3D 分子可视化 (3Dmol.js)
- ✅ 多种显示样式 (卡通/棍状/球棍/表面)
- ✅ 响应式设计

#### 生物信息学功能
- ✅ 从 RCSB PDB 导入真实结构
- ✅ 高级搜索面板
  - 按基因名搜索 (如：TP53, BRCA1)
  - 按生物体搜索 (如：Homo sapiens)
  - 按实验方法筛选
  - 按分辨率范围筛选
- ✅ 批量导入示例结构
- ✅ 统计仪表盘

---

## 🧪 使用示例

### 1. 导入真实蛋白质结构
```bash
# 导入单个 PDB
curl -X POST http://<IP>/api/import/1CRN

# 导入示例包
curl -X POST http://<IP>/api/import-samples
```

### 2. 按基因名搜索
```bash
curl "http://<IP>/api/bio/gene/TP53"
```

### 3. 按生物体搜索
```bash
curl "http://<IP>/api/bio/organism/Homo%20sapiens"
```

### 4. 高级组合搜索
```bash
curl "http://<IP>/api/bio/search/structure?method=X-RAY&maxRes=2.0&gene=kinase"
```

### 5. 获取完整结构信息
```bash
curl "http://<IP>/api/bio/structure/1CRN/full"
```

返回数据包含:
- 结构基本信息
- 多肽链序列
- 配体信息
- 金属离子
- 活性位点
- 翻译后修饰
- Pfam 结构域
- 文献引用

---

## 📊 数据库统计

```bash
curl http://<IP>/api/bio/stats/detailed
```

返回:
- 总结构数
- 总链数
- 独特配体数
- 实验方法分布
- Top 配体
- Top 金属离子

---

## 🔬 生物学家使用场景

### 场景 1: 查找特定蛋白的所有结构
```bash
# 搜索 TP53 基因的所有结构
GET /api/bio/gene/TP53

# 结果包含：PDB ID、分辨率、实验方法、生物体
```

### 场景 2: 分析酶的活性位点
```bash
# 获取活性位点信息
GET /api/bio/activesite/1CRN

# 结果包含：参与残基、配体、金属离子
```

### 场景 3: 查找含特定配体的结构
```bash
# 搜索含 ATP 的结构
GET /api/bio/search/ligand?name=ATP

# 获取配体结合详情
GET /api/bio/ligands/1CRN
```

### 场景 4: 研究翻译后修饰
```bash
# 获取 PTM 信息 (包含在完整结构中)
GET /api/bio/structure/1CRN/full

# 返回磷酸化、糖基化等修饰信息
```

### 场景 5: 序列相似性搜索
```bash
# 搜索包含特定序列片段的结构
GET /api/bio/search/sequence?sequence=PLAQ

# 返回精确匹配和模糊匹配结果
```

---

## 🚀 可扩展功能

### 短期 (可直接实现)
1. **AlphaFold DB 集成** - 导入预测结构
2. **SMILES 搜索** - 按化学结构搜索配体
3. **序列比对** - 集成 Clustal Omega
4. **RMSD 计算** - 结构比对
5. **导出功能** - 下载 PDB/mmCIF 格式

### 中期 (需要外部集成)
1. **BLAST 集成** - NCBI BLAST 序列比对
2. **InterProScan** - 蛋白质功能位点预测
3. **STRING API** - 蛋白互作网络
4. **KEGG 通路** - 代谢通路可视化
5. **分子对接** - AutoDock Vina 集成

### 长期 (高级功能)
1. **AI 预测** - AlphaFold2 本地部署
2. **MD 模拟** - GROMACS 集成
3. **自由能计算** - 结合亲和力预测
4. **药物筛选** - 虚拟筛选平台
5. **机器学习** - 功能预测模型

---

## 📚 参考数据库

| 数据库 | 特点 | 借鉴功能 |
|--------|------|----------|
| **PDB** | 蛋白质 3D 结构 | 原子坐标、实验方法、组装体 |
| **UniProt** | 蛋白质序列/功能 | 序列注释、PTM、活性位点 |
| **Pfam** | 蛋白质结构域 | HMM 模型、结构域注释 |
| **PubChem** | 小分子化合物 | 化学结构、生物活性 |
| **NCBI** | 综合数据库 | 分类学、基因关联 |

---

## 🎯 系统优势

1. **专业性强** - 参考主流生物数据库设计
2. **功能完整** - 覆盖结构/序列/功能注释
3. **易于扩展** - 模块化设计，API 清晰
4. **性能优化** - PostgreSQL 索引 + 视图
5. **用户友好** - 3D 可视化 + 高级搜索

---

## 💻 技术亮点

- ✅ 自研 PDB 解析器 (pdb-parser.js)
- ✅ RCSB PDB API 集成
- ✅ 3Dmol.js 分子可视化
- ✅ 生物信息学专用 API 模块
- ✅ PostgreSQL 高级特性 (数组/GIN 索引)
- ✅ PM2 进程管理
- ✅ Nginx 反向代理

---

**Built with 🦞 OpenClaw**

**参考设计**: PDB + UniProt + Pfam + PubChem
