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
router.get('/search/structure', async (req, res) => {
  try {
    const { method, minRes, maxRes, organism, gene } = req.query;
    
    let conditions = ['1=1'];
    const params = [];
    let paramCount = 0;
    
    if (method) {
      paramCount++;
      conditions.push(`method ILIKE $${paramCount}`);
      params.push(`%${method}%`);
    }
    
    if (minRes) {
      paramCount++;
      conditions.push(`resolution >= $${paramCount}`);
      params.push(parseFloat(minRes));
    }
    
    if (maxRes) {
      paramCount++;
      conditions.push(`resolution <= $${paramCount}`);
      params.push(parseFloat(maxRes));
    }
    
    if (organism) {
      paramCount++;
      conditions.push(`organism_scientific_name ILIKE $${paramCount}`);
      params.push(`%${organism}%`);
    }
    
    if (gene) {
      paramCount++;
      conditions.push(`gene_name ILIKE $${paramCount}`);
      params.push(`%${gene}%`);
    }
    
    const query = `SELECT * FROM structure_stats WHERE ${conditions.join(' AND ')} LIMIT 100`;
    const result = await pool.query(query, params);
    
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 3. 配体搜索 - 类似 PubChem
 */
router.get('/search/ligand', async (req, res) => {
  try {
    const { name, formula } = req.query;
    
    let query = 'SELECT * FROM ligands WHERE 1=1';
    const params = [];
    let paramCount = 0;
    
    if (name) {
      paramCount++;
      query += ` AND (ligand_name ILIKE $${paramCount} OR chem_comp_id ILIKE $${paramCount})`;
      params.push(`%${name}%`);
    }
    
    if (formula) {
      paramCount++;
      query += ` AND formula ILIKE $${paramCount}`;
      params.push(`%${formula}%`);
    }
    
    query += ' LIMIT 50';
    const result = await pool.query(query, params);
    
    res.json({ success: true, data: result.rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 4. 获取结构详情 (完整版)
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
 */
router.get('/stats/detailed', async (req, res) => {
  try {
    const totalStructures = await pool.query('SELECT COUNT(*) FROM structures');
    const totalChains = await pool.query('SELECT COUNT(*) FROM polypeptides');
    const totalLigands = await pool.query('SELECT COUNT(DISTINCT ligand_name) FROM ligands');
    const methods = await pool.query('SELECT method, COUNT(*) as count FROM structures GROUP BY method');
    const topLigands = await pool.query('SELECT * FROM ligand_stats LIMIT 10');
    const topMetals = await pool.query('SELECT * FROM metal_ion_stats LIMIT 10');
    
    res.json({
      success: true,
      data: {
        totalStructures: parseInt(totalStructures.rows[0].count),
        totalChains: parseInt(totalChains.rows[0].count),
        uniqueLigands: parseInt(totalLigands.rows[0].count),
        methods: methods.rows,
        top_ligands: topLigands.rows,
        top_metals: topMetals.rows
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
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
    const structures = await pool.query('SELECT COUNT(*) as "totalStructures" FROM structures');
    const atoms = await pool.query('SELECT COUNT(*) as "totalAtoms" FROM atoms');
    const methods = await pool.query('SELECT method, COUNT(*) as count FROM structures WHERE method IS NOT NULL GROUP BY method');
    
    res.json({
      success: true,
      data: {
        totalStructures: parseInt(structures.rows[0].totalstructures),
        totalAtoms: parseInt(atoms.rows[0].totalatoms),
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
    const structures = await pool.query('SELECT COUNT(*) as "totalStructures" FROM structures');
    const atoms = await pool.query('SELECT COUNT(*) as "totalAtoms" FROM atoms');
    const methods = await pool.query('SELECT method, COUNT(*) as count FROM structures WHERE method IS NOT NULL GROUP BY method');
    const organisms = await pool.query('SELECT organism_scientific_name, COUNT(*) as count FROM structures WHERE organism_scientific_name IS NOT NULL GROUP BY organism_scientific_name ORDER BY count DESC LIMIT 10');
    
    res.json({
      success: true,
      data: {
        totalStructures: parseInt(structures.rows[0].totalstructures),
        totalAtoms: parseInt(atoms.rows[0].totalatoms),
        methods: methods.rows,
        topOrganisms: organisms.rows,
        lastUpdated: new Date().toISOString()
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});
