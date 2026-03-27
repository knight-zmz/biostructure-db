const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
const path = require('path');
const PDBParser = require('./utils/pdb-parser');
const axios = require('axios');
const bioapi = require('./api/bioapi');
const cache = require('./utils/redis-cache');

const app = express();
const PORT = process.env.PORT || 3000;

// 数据库连接池
const pool = new Pool({
  user: 'myapp_user',
  host: 'localhost',
  database: 'myapp',
  password: 'MyApp@2026',
  port: 5432,
});

// 初始化 Redis 缓存
cache.connect().catch(err => console.warn('Redis 启动失败:', err.message));

// 中间件
app.use(cors());
app.use(express.json());

// 静态文件服务 - 带缓存控制
const publicPath = path.resolve(__dirname, '../public');
app.use(express.static(publicPath, {
  maxAge: '1d',
  etag: true,
  lastModified: true
}));

// 挂载生物信息学 API
app.use('/api/bio', bioapi);

// 根路径重定向到 index.html
app.get('/', (req, res) => {
  res.setHeader('Cache-Control', 'public, max-age=3600');
  res.sendFile(path.join(publicPath, 'index.html'));
});

// 启用 gzip 压缩中间件
const compression = (req, res, next) => {
  const acceptEncoding = req.headers['accept-encoding'];
  if (!acceptEncoding || !acceptEncoding.includes('gzip')) {
    return next();
  }
  
  res.setHeader('Content-Encoding', 'gzip');
  next();
};

// 对静态文件应用压缩（如果存在.gz 版本）
app.use((req, res, next) => {
  if (req.path.endsWith('.html') || req.path.endsWith('.js') || req.path.endsWith('.css')) {
    const gzPath = publicPath + req.path + '.gz';
    const fs = require('fs');
    if (fs.existsSync(gzPath)) {
      res.setHeader('Content-Encoding', 'gzip');
      res.setHeader('Vary', 'Accept-Encoding');
      return res.sendFile(gzPath);
    }
  }
  next();
});

// 缓存中间件 - 为 GET 请求添加缓存
const cacheMiddleware = (ttl = 300) => async (req, res, next) => {
  if (req.method !== 'GET') {
    return next();
  }

  const key = `cache:${req.originalUrl}`;
  const cached = await cache.get(key);
  
  if (cached) {
    res.setHeader('X-Cache', 'HIT');
    return res.json(cached);
  }

  // 重写 res.json 以捕获响应并缓存
  const originalJson = res.json;
  res.json = (data) => {
    cache.set(key, data, ttl);
    res.setHeader('X-Cache', 'MISS');
    return originalJson.call(res, data);
  };

  next();
};

// API 路由

// 1. 获取所有结构列表 (带缓存 + 分页 + 筛选)
app.get('/api/structures', cacheMiddleware(600), async (req, res) => {
  try {
    const { page = 1, limit = 20, method, sort = 'pdb_id', order = 'asc', minRes, maxRes } = req.query;
    const offset = (parseInt(page) - 1) * parseInt(limit);

    let where = ['1=1'];
    let params = [];
    let paramIdx = 1;

    if (method) {
      where.push(`method = $${paramIdx++}`);
      params.push(method);
    }
    if (minRes) {
      where.push(`resolution >= $${paramIdx++}`);
      params.push(parseFloat(minRes));
    }
    if (maxRes) {
      where.push(`resolution <= $${paramIdx++}`);
      params.push(parseFloat(maxRes));
    }

    const allowedSorts = ['pdb_id', 'resolution', 'method', 'deposit_date'];
    const sortCol = allowedSorts.includes(sort) ? sort : 'pdb_id';
    const sortOrder = order === 'desc' ? 'DESC' : 'ASC';
    const nullsClause = sortCol === 'resolution' ? 'NULLS LAST' : '';

    const countResult = await pool.query(
      `SELECT COUNT(*) FROM structure_stats WHERE ${where.join(' AND ')}`,
      params
    );

    params.push(parseInt(limit));
    params.push(offset);

    const result = await pool.query(
      `SELECT * FROM structure_stats WHERE ${where.join(' AND ')} ORDER BY ${sortCol} ${sortOrder} ${nullsClause} LIMIT $${paramIdx++} OFFSET $${paramIdx}`,
      params
    );

    res.json({
      success: true,
      data: result.rows,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: parseInt(countResult.rows[0].count),
        totalPages: Math.ceil(parseInt(countResult.rows[0].count) / parseInt(limit))
      }
    });
  } catch (err) {
    console.error("Error fetching structures:", err);
    res.status(500).json({ success: false, error: "Internal server error" });
  }
});

// 2. 获取单个结构详情 (带缓存 - 增强版含配体/序列/二级结构)
app.get('/api/structures/:pdbId', cacheMiddleware(600), async (req, res) => {
  try {
    const { pdbId } = req.params;
    const structure = await pool.query('SELECT * FROM structures WHERE pdb_id = $1', [pdbId]);
    if (structure.rows.length === 0) {
      return res.status(404).json({ success: false, error: 'PDB ID not found' });
    }
    const authors = await pool.query('SELECT name FROM authors WHERE pdb_id = $1 ORDER BY order_num', [pdbId]);
    const chains = await pool.query('SELECT * FROM chains WHERE pdb_id = $1', [pdbId]);
    const citations = await pool.query('SELECT * FROM citations WHERE pdb_id = $1', [pdbId]);
    const ligands = await pool.query('SELECT * FROM ligands WHERE pdb_id = $1', [pdbId]);
    const sequences = await pool.query('SELECT * FROM sequence_index WHERE pdb_id = $1', [pdbId]);
    const ss = await pool.query('SELECT * FROM secondary_structures WHERE pdb_id = $1', [pdbId]);
    const atomStats = await pool.query(
      'SELECT COUNT(*) as atom_count, MIN(x_coord) as min_x, MAX(x_coord) as max_x, MIN(y_coord) as min_y, MAX(y_coord) as max_y, MIN(z_coord) as min_z, MAX(z_coord) as max_z FROM atoms WHERE pdb_id = $1',
      [pdbId]
    );

    res.json({
      success: true,
      data: {
        ...structure.rows[0],
        authors: authors.rows,
        chains: chains.rows,
        citations: citations.rows,
        ligands: ligands.rows,
        sequences: sequences.rows,
        secondary_structures: ss.rows,
        atom_stats: atomStats.rows[0]
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 3. 获取原子坐标 (用于 3D 可视化)
app.get('/api/structures/:pdbId/atoms', async (req, res) => {
  try {
    const { pdbId } = req.params;
    const { chain } = req.query;
    
    let query = 'SELECT * FROM atoms WHERE pdb_id = $1';
    const params = [pdbId];
    
    if (chain) {
      query += ' AND chain_letter = $2';
      params.push(chain);
    }
    
    const result = await pool.query(query, params);
    res.json({ success: true, data: result.rows, count: result.rows.length });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 4. 获取残基序列
app.get('/api/structures/:pdbId/residues', async (req, res) => {
  try {
    const { pdbId } = req.params;
    const result = await pool.query(
      'SELECT * FROM residues WHERE pdb_id = $1 ORDER BY chain_letter, residue_num',
      [pdbId]
    );
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 5. 获取二级结构
app.get('/api/structures/:pdbId/secondary-structure', async (req, res) => {
  try {
    const { pdbId } = req.params;
    const result = await pool.query(
      'SELECT * FROM secondary_structures WHERE pdb_id = $1',
      [pdbId]
    );
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 6. 搜索结构
app.get('/api/search', async (req, res) => {
  try {
    const { q, method, minResolution } = req.query;
    
    let query = 'SELECT * FROM structure_stats WHERE 1=1';
    const params = [];
    let paramCount = 0;
    
    if (q) {
      paramCount++;
      query += ` AND (title ILIKE $${paramCount} OR pdb_id ILIKE $${paramCount})`;
      params.push(`%${q}%`);
    }
    
    if (method) {
      paramCount++;
      query += ` AND method ILIKE $${paramCount}`;
      params.push(`%${method}%`);
    }
    
    if (minResolution) {
      paramCount++;
      query += ` AND resolution <= $${paramCount}`;
      params.push(parseFloat(minResolution));
    }
    
    const result = await pool.query(query, params);
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 7. 统计信息
app.get('/api/stats', async (req, res) => {
  try {
    const totalStructures = await pool.query('SELECT COUNT(*) FROM structures');
    const totalAtoms = await pool.query('SELECT COUNT(*) FROM atoms');
    const methods = await pool.query('SELECT method, COUNT(*) FROM structures GROUP BY method');
    
    res.json({
      success: true,
      data: {
        totalStructures: parseInt(totalStructures.rows[0].count),
        totalAtoms: parseInt(totalAtoms.rows[0].count),
        methods: methods.rows
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 8. 上传新结构 (简化版)
app.post('/api/structures', async (req, res) => {
  try {
    const { pdb_id, title, resolution, method, organism, description } = req.body;
    
    const result = await pool.query(
      `INSERT INTO structures (pdb_id, title, resolution, method, organism, description)
       VALUES ($1, $2, $3, $4, $5, $6)
       ON CONFLICT (pdb_id) DO UPDATE SET
         title = EXCLUDED.title,
         resolution = EXCLUDED.resolution,
         method = EXCLUDED.method,
         organism = EXCLUDED.organism,
         description = EXCLUDED.description,
         updated_at = CURRENT_TIMESTAMP
       RETURNING *`,
      [pdb_id, title, resolution, method, organism, description]
    );
    
    res.json({ success: true, data: result.rows[0] });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 9. 从 RCSB PDB 导入结构
app.post('/api/import/:pdbId', async (req, res) => {
  try {
    const { pdbId } = req.params;
    const parser = new PDBParser();
    
    // 从 RCSB 下载 PDB 文件
    const url = `https://files.rcsb.org/download/${pdbId}.pdb`;
    const response = await axios.get(url, { timeout: 10000 });
    const parsed = parser.parse(response.data);
    
    // 插入结构信息
    await pool.query(
      `INSERT INTO structures (pdb_id, title, resolution, method, deposit_date, description)
       VALUES ($1, $2, $3, $4, CURRENT_DATE, $5)
       ON CONFLICT (pdb_id) DO NOTHING`,
      [pdbId, parsed.header.title || pdbId, parsed.header.resolution, parsed.header.method, 'Imported from RCSB PDB']
    );
    
    // 插入作者
    for (let i = 0; i < parsed.header.authors.length; i++) {
      await pool.query(
        `INSERT INTO authors (pdb_id, name, order_num) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING`,
        [pdbId, parsed.header.authors[i], i + 1]
      );
    }
    
    // 插入链
    for (const chain of parsed.chains) {
      await pool.query(
        `INSERT INTO chains (pdb_id, chain_letter, description) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING`,
        [pdbId, chain, `Chain ${chain}`]
      );
    }
    
    // 插入原子坐标 (限制数量以防过大)
    const maxAtoms = 10000;
    const atomsToInsert = parsed.atoms.slice(0, maxAtoms);
    
    for (const atom of atomsToInsert) {
      await pool.query(
        `INSERT INTO atoms (pdb_id, atom_name, atom_type, chain_letter, residue_num, residue_name, x_coord, y_coord, z_coord, element)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)`,
        [pdbId, atom.name, atom.name.charAt(0), atom.chain, atom.resSeq, atom.resName, atom.x, atom.y, atom.z, atom.element]
      );
    }
    
    // 插入残基
    const residues = [];
    for (const atom of parsed.atoms) {
      const key = `${atom.chain}-${atom.resSeq}-${atom.resName}`;
      if (!residues.includes(key)) {
        residues.push(key);
        await pool.query(
          `INSERT INTO residues (pdb_id, chain_letter, residue_num, residue_name, residue_type) 
           VALUES ($1, $2, $3, $4, $5) ON CONFLICT DO NOTHING`,
          [pdbId, atom.chain, atom.resSeq, atom.resName, 'amino_acid']
        );
      }
    }
    
    res.json({ 
      success: true, 
      data: { 
        pdbId, 
        atomsImported: atomsToInsert.length,
        totalAtoms: parsed.atoms.length,
        chains: parsed.chains,
        truncated: parsed.atoms.length > maxAtoms
      } 
    });
  } catch (err) {
    res.status(500).json({ 
      success: false, 
      error: err.message,
      hint: 'PDB ID 可能不存在或网络错误'
    });
  }
});

// 10. 批量导入示例结构
app.post('/api/import-samples', async (req, res) => {
  try {
    const samplePdbs = ['1CRN', '1UBQ', '7ZNT', '6VXX', '1A4Y'];
    const results = [];
    
    for (const pdbId of samplePdbs) {
      try {
        const parser = new PDBParser();
        const url = `https://files.rcsb.org/download/${pdbId}.pdb`;
        const response = await axios.get(url, { timeout: 10000 });
        const parsed = parser.parse(response.data);
        
        await pool.query(
          `INSERT INTO structures (pdb_id, title, resolution, method, deposit_date)
           VALUES ($1, $2, $3, $4, CURRENT_DATE)
           ON CONFLICT (pdb_id) DO NOTHING`,
          [pdbId, parsed.header.title || pdbId, parsed.header.resolution, parsed.header.method]
        );
        
        // 插入少量原子用于展示
        const atomsToInsert = parsed.atoms.slice(0, 100);
        for (const atom of atomsToInsert) {
          await pool.query(
            `INSERT INTO atoms (pdb_id, atom_name, chain_letter, residue_num, residue_name, x_coord, y_coord, z_coord, element)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
            [pdbId, atom.name, atom.chain, atom.resSeq, atom.resName, atom.x, atom.y, atom.z, atom.element]
          );
        }
        
        results.push({ pdbId, status: 'success', atoms: atomsToInsert.length });
      } catch (err) {
        results.push({ pdbId, status: 'failed', error: err.message });
      }
    }
    
    res.json({ success: true, data: results });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 11. 缓存统计信息
app.get('/api/cache/stats', async (req, res) => {
  try {
    const stats = await cache.getStats();
    res.json({ success: true, data: stats });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 12. 清除缓存
app.delete('/api/cache/clear', async (req, res) => {
  try {
    const { pattern } = req.query;
    if (pattern) {
      await cache.delPattern(pattern);
    } else {
      await cache.delPattern('cache:*');
    }
    res.json({ success: true, message: '缓存已清除' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});


// 10. 获取最近沉积的结构
app.get('/api/structures/recent/list', cacheMiddleware(300), async (req, res) => {
  try {
    const { limit = 8 } = req.query;
    const result = await pool.query(
      'SELECT pdb_id, title, method, resolution, deposit_date, gene_name, organism_scientific_name FROM structures ORDER BY deposit_date DESC NULLS LAST LIMIT $1',
      [parseInt(limit)]
    );
    res.json({ success: true, data: result.rows });
  } catch (err) {
    console.error('Error fetching recent structures:', err);
    res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

// 11. 搜索自动补全
app.get('/api/search/suggest', async (req, res) => {
  try {
    const { q, limit = 10 } = req.query;
    if (!q || q.length < 1) {
      return res.json({ success: true, data: [] });
    }
    const pattern = `${q.toUpperCase()}%`;
    const result = await pool.query(
      `SELECT pdb_id, title, gene_name FROM structures WHERE UPPER(pdb_id) LIKE $1 OR UPPER(gene_name) LIKE $1 OR UPPER(title) LIKE $2 LIMIT $3`,
      [pattern, `%${q.toUpperCase()}%`, parseInt(limit)]
    );
    res.json({ success: true, data: result.rows });
  } catch (err) {
    console.error('Error in search suggest:', err);
    res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`🧬 BioStructure DB API running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/api/stats`);
  console.log(`💾 Redis Cache: ${cache.enabled ? 'Enabled' : 'Disabled'}`);
});
