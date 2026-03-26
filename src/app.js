const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
const path = require('path');
const PDBParser = require('./pdb-parser');
const axios = require('axios');
const bioapi = require('./bioapi');

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

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// 挂载生物信息学 API
app.use('/api/bio', bioapi);

// API 路由

// 1. 获取所有结构列表
app.get('/api/structures', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM structure_stats ORDER BY pdb_id');
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 2. 获取单个结构详情
app.get('/api/structures/:pdbId', async (req, res) => {
  try {
    const { pdbId } = req.params;
    const structure = await pool.query('SELECT * FROM structures WHERE pdb_id = $1', [pdbId]);
    const authors = await pool.query('SELECT name FROM authors WHERE pdb_id = $1 ORDER BY order_num', [pdbId]);
    const chains = await pool.query('SELECT * FROM chains WHERE pdb_id = $1', [pdbId]);
    const citations = await pool.query('SELECT * FROM citations WHERE pdb_id = $1', [pdbId]);
    
    res.json({
      success: true,
      data: {
        ...structure.rows[0],
        authors: authors.rows,
        chains: chains.rows,
        citations: citations.rows
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

// 启动服务器
app.listen(PORT, () => {
  console.log(`🧬 BioStructure DB API running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/api/stats`);
});
