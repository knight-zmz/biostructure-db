# 最小修复草案 - structure_stats 与 authors

**生成时间**: 2026-03-30T22:45:00+08:00  
**审计范围**: src/app.js, src/db/schema.sql  
**目标**: 不改 schema 的代码级兼容修复

---

## 1. structure_stats 最小修复草案

### 引用位置
| 文件 | 行号 | API 端点 | 用途 |
|------|------|----------|------|
| src/app.js | 111-112 | `GET /api/compare` | 获取两个结构的对比数据 |
| src/app.js | 229, 237 | `GET /api/structures` | 结构列表（分页/筛选） |
| src/app.js | 348 | `GET /api/search` | 结构搜索 |

### 影响端点
1. `/api/compare?pdb1=XXX&pdb2=YYY`
2. `/api/structures?page=1&limit=10&method=X-RAY...`
3. `/api/search?q=insulin&method=X-RAY`

### 当前问题本质
`structure_stats` 表在 schema.sql 中不存在，但代码中多处查询该表。

**实际使用的字段**:
- `pdb_id` ✓ (structures 表有)
- `resolution` ✓ (structures 表有)
- `method` ✓ (structures 表有)
- `deposit_date` ✓ (structures 表有)
- `chain_count` ✗ (需计算)
- `atom_count` ✗ (需计算)

### 不改 schema 的最小 patch

**方案**: 将 `structure_stats` 查询替换为 `structures` 表 + 聚合子查询

**修复代码示例** (`/api/compare`):
```javascript
// Before (structure_stats)
const [s1, s2] = await Promise.all([
  pool.query('SELECT * FROM structure_stats WHERE pdb_id = $1', [pdb1]),
  pool.query('SELECT * FROM structure_stats WHERE pdb_id = $1', [pdb2])
]);

// After (structures + computed counts)
const [s1, s2] = await Promise.all([
  pool.query(`
    SELECT s.*, 
           (SELECT COUNT(DISTINCT chain_id) FROM polypeptides WHERE pdb_id = $1) as chain_count,
           (SELECT COUNT(*) FROM atoms WHERE pdb_id = $1) as atom_count
    FROM structures s WHERE s.pdb_id = $1`, [pdb1]),
  pool.query(`
    SELECT s.*, 
           (SELECT COUNT(DISTINCT chain_id) FROM polypeptides WHERE pdb_id = $1) as chain_count,
           (SELECT COUNT(*) FROM atoms WHERE pdb_id = $1) as atom_count
    FROM structures s WHERE s.pdb_id = $1`, [pdb2])
]);
```

**修复代码示例** (`/api/structures` 列表):
```javascript
// Before
const countResult = await pool.query(
  `SELECT COUNT(*) FROM structure_stats WHERE ${where.join(' AND ')}`, params
);

// After
const countResult = await pool.query(
  `SELECT COUNT(*) FROM structures WHERE ${where.join(' AND ')}`, params
);

// For the main query, add computed counts:
const result = await pool.query(`
  SELECT s.*, 
         (SELECT COUNT(DISTINCT chain_id) FROM polypeptides WHERE pdb_id = s.pdb_id) as chain_count,
         (SELECT COUNT(*) FROM atoms WHERE pdb_id = s.pdb_id) as atom_count
  FROM structures s 
  WHERE ${where.join(' AND ')} 
  ORDER BY ${sortCol} ${sortOrder} ${nullsClause} 
  LIMIT $${paramIdx++} OFFSET $${paramIdx}`, params
);
```

**修复代码示例** (`/api/search`):
```javascript
// Before
let query = 'SELECT * FROM structure_stats WHERE 1=1';

// After
let query = `
  SELECT s.*, 
         (SELECT COUNT(DISTINCT chain_id) FROM polypeptides WHERE pdb_id = s.pdb_id) as chain_count,
         (SELECT COUNT(*) FROM atoms WHERE pdb_id = s.pdb_id) as atom_count
  FROM structures s WHERE 1=1`;
```

### 是否需要新增表/视图
**否** - 完全可以用现有表 + 聚合查询替代

### 推荐方案
**代码修复方案**（无需 schema 变更）:
1. 将 `structure_stats` 替换为 `structures` 表
2. `chain_count` 通过 `COUNT(DISTINCT chain_id) FROM polypeptides` 计算
3. `atom_count` 通过 `COUNT(*) FROM atoms` 计算

### 风险级别
**🟡 中** - 原因:
- 聚合查询可能比直接表查询慢（但数据量小时可忽略）
- 需要修改 3 个 API 端点的查询语句
- 不影响 API 响应格式（保持向后兼容）

### 是否仍需用户裁决
**否** - 可直接执行代码修复

---

## 2. authors 最小修复草案

### 引用位置
| 文件 | 行号 | API 端点 | 用途 |
|------|------|----------|------|
| src/app.js | 265 | `GET /api/structures/:pdbId` | 获取结构详情时返回作者列表 |
| src/app.js | 280 | `GET /api/structures/:pdbId` | 将作者数据加入响应 |
| src/app.js | 441 | `POST /api/import/:pdbId` | 注释说明暂不存储作者 |

### 影响端点
1. `/api/structures/:pdbId` - 结构详情

### 当前问题本质
代码期望独立的 `authors` 表（有 pdb_id, name, order_num 字段），但 schema 中作者信息存储在 `structures.authors TEXT[]` 数组字段中。

**代码期望的查询**:
```sql
SELECT name FROM authors WHERE pdb_id = $1 ORDER BY order_num
-- 返回：[{name: "Smith, J."}, {name: "Doe, A."}]
```

**Schema 实际存储**:
```sql
SELECT authors FROM structures WHERE pdb_id = $1
-- 返回：["Smith, J.", "Doe, A."] (TEXT[] 数组)
```

### 不改 schema 的最小 patch

**方案**: 修改代码读取 `structures.authors` 字段并转换为期望格式

**修复代码示例** (`/api/structures/:pdbId`):
```javascript
// Before (separate authors table)
const authors = await pool.query(
  'SELECT name FROM authors WHERE pdb_id = $1 ORDER BY order_num', 
  [pdbId]
);

res.json({
  ...structure.rows[0],
  authors: authors.rows,  // [{name: "..."}, {name: "..."}]
  // ...
});

// After (TEXT[] field)
const structure = await pool.query(
  'SELECT * FROM structures WHERE pdb_id = $1', 
  [pdbId]
);

// Transform TEXT[] to expected format
const authorsArray = structure.rows[0].authors || [];
const authorsFormatted = authorsArray.map((name, index) => ({
  name: name,
  order_num: index + 1
}));

res.json({
  ...structure.rows[0],
  authors: authorsFormatted,  // [{name: "...", order_num: 1}, ...]
  // ...
});
```

**删除遗留代码** (`POST /api/import/:pdbId`):
```javascript
// 删除第 441 行附近的注释和作者插入逻辑
// 因为作者信息已经在 structures.authors 字段中
```

### 是否需要新增独立表
**否** - 使用现有 `structures.authors TEXT[]` 字段即可

### 推荐方案
**代码修复方案**（无需 schema 变更）:
1. 移除对独立 `authors` 表的查询
2. 从 `structures.authors` TEXT[] 字段读取
3. 转换为 API 响应期望的格式（带 order_num）

### 风险级别
**🟢 低** - 原因:
- 只影响 1 个 API 端点
- 响应格式保持兼容（甚至增加 order_num 字段）
- 不需要数据库迁移

### 是否仍需用户裁决
**否** - 可直接执行代码修复

---

## 3. 综合推荐

### 两个问题的共同特点
| 特点 | structure_stats | authors |
|------|-----------------|---------|
| 是否需要新增表 | 否 | 否 |
| 是否可只改代码 | 是 | 是 |
| 影响端点数 | 3 | 1 |
| 风险级别 | 中 | 低 |
| 推荐执行 | ✅ 直接修复 | ✅ 直接修复 |

### 推荐执行顺序
1. **先修复 authors** (🟢 低风险，1 个端点)
2. **再修复 structure_stats** (🟡 中风险，3 个端点)

### 预计工作量
- authors 修复：~10 行代码修改
- structure_stats 修复：~30 行代码修改
- 总计：~40 行代码修改，无 schema 变更

### 可生成的 patch 文件
- `patches/001-fix-authors-text-array.patch`
- `patches/002-fix-structure-stats-queries.patch`

---

## 4. 结论

**两个问题都可以通过纯代码修复解决，无需 schema 变更，无需用户裁决。**

**建议**: 直接生成 handler 执行修复，不要暂停等待用户确认。
