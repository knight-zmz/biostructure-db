/**
 * 生物信息学专用 API 模块
 * 参考：UniProt, Pfam, NCBI 功能设计
 */

const express = require('express');
const { Pool } = require('pg');

const router = express.Router();

const pool = new Pool({
  user: 'myapp_user',
  host: 'localhost',
  database: 'myapp',
  password: 'MyApp@2026',
  port: 5432,
});

/**
 * 1. 序列搜索 - 类似 UniProt
 * 支持精确匹配和模糊搜索
 */
router.get('/search/sequence', async (req, res) => {
  try {
    const { sequence, identity } = req.query;
    
    if (!sequence) {
      return res.json({ success: false, error: '请提供序列' });
    }
    
    // 精确匹配
    const exactMatch = await pool.query(
      `SELECT pdb_id, chain_id, sequence, length 
       FROM sequence_index 
       WHERE sequence = $1`,
      [sequence]
    );
    
    // 模糊搜索 (包含)
    const fuzzyMatch = await pool.query(
      `SELECT pdb_id, chain_id, sequence, length 
       FROM sequence_index 
       WHERE sequence ILIKE $1 
       LIMIT 50`,
      [`%${sequence}%`]
    );
    
    res.json({
      success: true,
      data: {
        exact: exactMatch.rows,
        fuzzy: fuzzyMatch.rows,
        query: sequence
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 2. 结构搜索 - 按实验方法、分辨率等
 */
router.get('/structure/:pdbId/full', async (req, res) => {
  try {
    const { pdbId } = req.params;
    
    // 结构基本信息
    const structure = await pool.query(
      'SELECT * FROM structures WHERE pdb_id = $1',
      [pdbId]
    );
    
    if (structure.rows.length === 0) {
      return res.json({ success: false, error: 'PDB ID 不存在' });
    }
    
    // 多肽链
    const chains = await pool.query(
      'SELECT * FROM polypeptides WHERE pdb_id = $1',
      [pdbId]
    );
    
    // 配体
    const ligands = await pool.query(
      'SELECT * FROM ligands WHERE pdb_id = $1',
      [pdbId]
    );
    
    // 金属离子
    const metals = await pool.query(
      'SELECT * FROM metal_ions WHERE pdb_id = $1',
      [pdbId]
    );
    
    // 活性位点
    const sites = await pool.query(
      'SELECT * FROM active_sites WHERE pdb_id = $1',
      [pdbId]
    );
    
    // PTM
    const ptms = await pool.query(
      'SELECT * FROM ptms WHERE pdb_id = $1',
      [pdbId]
    );
    
    // Pfam 结构域
    const pfam = await pool.query(
      'SELECT * FROM pfam_domains WHERE pdb_id = $1',
      [pdbId]
    );
    
    // 文献
    const citations = await pool.query(
      'SELECT * FROM citations WHERE pdb_id = $1',
      [pdbId]
    );
    
    res.json({
      success: true,
      data: {
        structure: structure.rows[0],
        chains: chains.rows,
        ligands: ligands.rows,
        metal_ions: metals.rows,
        active_sites: sites.rows,
        ptms: ptms.rows,
        pfam_domains: pfam.rows,
        citations: citations.rows
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 5. 获取 UniProt 映射信息
 */
router.get('/uniprot/:pdbId', async (req, res) => {
  try {
    const { pdbId } = req.params;
    const result = await pool.query(
      'SELECT * FROM uniprot_mappings WHERE pdb_id = $1',
      [pdbId]
    );
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 6. 获取配体结合信息
 */
router.get('/ligands/:pdbId', async (req, res) => {
  try {
    const { pdbId } = req.params;
    const result = await pool.query(
      `SELECT l.*, 
              ARRAY_AGG(DISTINCT a.atom_name) as interacting_atoms
       FROM ligands l
       LEFT JOIN atoms a ON l.pdb_id = a.pdb_id 
         AND a.residue_num IN (
           SELECT unnest(residues) FROM active_sites 
           WHERE pdb_id = $1 AND site_type = 'binding_site'
         )
       WHERE l.pdb_id = $1
       GROUP BY l.ligand_id`,
      [pdbId]
    );
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 7. 统计信息 (增强版)
});

/**
 * 8. 按生物体搜索
 */
router.get('/organism/:name', async (req, res) => {
  try {
    const { name } = req.params;
    const result = await pool.query(
      `SELECT pdb_id, title, resolution, method, gene_name, molecule_weight
       FROM structures
       WHERE organism_scientific_name ILIKE $1
       ORDER BY resolution ASC NULLS LAST
       LIMIT 100`,
      [`%${name}%`]
    );
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 9. 按基因名搜索
 */
router.get('/gene/:name', async (req, res) => {
  try {
    const { name } = req.params;
    const result = await pool.query(
      `SELECT pdb_id, title, resolution, organism_scientific_name, molecule_weight
       FROM structures
       WHERE gene_name ILIKE $1
       ORDER BY resolution ASC NULLS LAST
       LIMIT 100`,
      [`%${name}%`]
    );
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 10. 获取活性位点详情
 */
router.get('/activesite/:pdbId', async (req, res) => {
  try {
    const { pdbId } = req.params;
    const result = await pool.query(
      `SELECT s.*, 
              ARRAY_AGG(r.residue_name || r.residue_num) as residues
       FROM active_sites s
       LEFT JOIN residues r ON s.pdb_id = r.pdb_id 
         AND r.residue_id = ANY(s.residues)
       WHERE s.pdb_id = $1
       GROUP BY s.site_id`,
      [pdbId]
    );
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;

/**
 * 11. 获取统计信息
 */
router.get('/stats', async (req, res) => {
  try {
    const structures = await pool.query('SELECT COUNT(*) as count FROM structures');
    const atoms = await pool.query('SELECT COUNT(*) as count FROM atoms');
    const methods = await pool.query('SELECT method, COUNT(*) as count FROM structures WHERE method IS NOT NULL GROUP BY method');
    
    res.json({
      success: true,
      data: {
        totalStructures: parseInt(structures.rows[0].count),
        totalAtoms: parseInt(atoms.rows[0].count),
        methods: methods.rows
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 12. 获取详细统计信息
 */
router.get('/stats/detailed', async (req, res) => {
  try {
    const structures = await pool.query('SELECT COUNT(*) as total FROM structures');
    const atoms = await pool.query('SELECT COUNT(*) as total FROM atoms');
    const chains = await pool.query('SELECT COUNT(*) as total FROM chains');
    const methods = await pool.query('SELECT method, COUNT(*) as count FROM structures WHERE method IS NOT NULL GROUP BY method');
    const organisms = await pool.query('SELECT organism_scientific_name, COUNT(*) as count FROM structures WHERE organism_scientific_name IS NOT NULL GROUP BY organism_scientific_name ORDER BY count DESC LIMIT 10');
    
    let uniqueLigands = 0;
    try {
      const ligandsResult = await pool.query('SELECT COUNT(DISTINCT ligand_name) as total FROM ligands');
      uniqueLigands = parseInt(ligandsResult.rows[0].total);
    } catch (e) {
      // ligands table might not exist or be empty
    }
    
    res.json({
      success: true,
      data: {
        totalStructures: parseInt(structures.rows[0].total),
        totalAtoms: parseInt(atoms.rows[0].total),
        totalChains: parseInt(chains.rows[0].total),
        uniqueLigands: uniqueLigands,
        methods: methods.rows,
        topOrganisms: organisms.rows,
        lastUpdated: new Date().toISOString()
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 13. 获取数据库完整信息
 */
router.get('/info', async (req, res) => {
  try {
    const dbSize = await pool.query('SELECT pg_size_pretty(pg_database_size(current_database())) as size');
    const tableStats = await pool.query(`
      SELECT relname as table_name, n_live_tup as row_count
      FROM pg_stat_user_tables
      WHERE schemaname = 'public'
      ORDER BY n_live_tup DESC
      LIMIT 10
    `);
    const indexStats = await pool.query(`
      SELECT indexrelname as index_name, idx_scan as scans
      FROM pg_stat_user_indexes
      WHERE schemaname = 'public'
      ORDER BY idx_scan DESC
      LIMIT 10
    `);
    
    res.json({
      success: true,
      data: {
        databaseSize: dbSize.rows[0].size,
        tableStats: tableStats.rows,
        indexStats: indexStats.rows,
        serverTime: new Date().toISOString()
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 14. 获取序列比对信息
 */
router.get('/sequence/:pdbId/:chainId', async (req, res) => {
  try {
    const { pdbId, chainId } = req.params;
    const result = await pool.query(`
      SELECT s.pdb_id, s.chain_id, s.sequence, s.length,
             u.uniprot_id, u.gene_name, u.organism
      FROM sequence_index s
      LEFT JOIN uniprot_mappings u ON s.pdb_id = u.pdb_id
      WHERE s.pdb_id = $1 AND s.chain_id = $2
    `, [pdbId, chainId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ success: false, error: 'Sequence not found' });
    }
    
    res.json({ success: true, data: result.rows[0] });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 15. 获取二级结构信息
 */
router.get('/secondary/:pdbId', async (req, res) => {
  try {
    const { pdbId } = req.params;
    const result = await pool.query(`
      SELECT ss.ss_id, ss.pdb_id, ss.chain_letter, ss.start_residue, ss.end_residue, ss.ss_type, ss.description FROM secondary_structures ss WHERE ss.pdb_id = $1
    `, [pdbId]);
    
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 16. 获取 Pfam 结构域信息
 */
router.get('/pfam/:pdbId', async (req, res) => {
  try {
    const { pdbId } = req.params;
    const result = await pool.query(`
      SELECT pf.*, 
             u.uniprot_id, u.gene_name
      FROM pfam_domains pf
      LEFT JOIN uniprot_mappings u ON pf.pdb_id = u.pdb_id
      WHERE pf.pdb_id = $1
    `, [pdbId]);
    
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 17. 通用搜索
 */
router.get('/search/structure', async (req, res) => {
  try {
    const { q } = req.query;
    if (!q) {
      return res.status(400).json({ success: false, error: 'Search query required' });
    }
    
    const result = await pool.query(`
      SELECT pdb_id, title, resolution, method, gene_name, organism_scientific_name
      FROM structures
      WHERE pdb_id ILIKE $1 
         OR title ILIKE $1 
         OR gene_name ILIKE $1 
         OR organism_scientific_name ILIKE $1
      ORDER BY resolution ASC NULLS LAST
      LIMIT 50
    `, [`%${q}%`]);
    
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 18. 配体搜索
 */
router.get('/search/ligand', async (req, res) => {
  try {
    const { name } = req.query;
    if (!name) {
      return res.status(400).json({ success: false, error: 'Ligand name required' });
    }
    
    const result = await pool.query(`
      SELECT l.pdb_id, l.ligand_name, l.formula, l.weight,
             s.title, s.resolution, s.method
      FROM ligands l
      LEFT JOIN structures s ON l.pdb_id = s.pdb_id
      WHERE l.ligand_name ILIKE $1
      ORDER BY s.resolution ASC NULLS LAST
      LIMIT 50
    `, [`%${name}%`]);
    
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 19. 健康检查端点
 */
router.get('/health', async (req, res) => {
  try {
    const dbCheck = await pool.query('SELECT 1');
    const structureCount = await pool.query('SELECT COUNT(*) FROM structures');
    
    res.json({
      success: true,
      status: 'healthy',
      timestamp: new Date().toISOString(),
      database: 'connected',
      structures: parseInt(structureCount.rows[0].count),
      uptime: process.uptime()
    });
  } catch (err) {
    res.status(500).json({
      success: false,
      status: 'unhealthy',
      error: err.message
    });
  }
});
