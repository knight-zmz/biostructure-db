-- 数据库优化脚本
-- 1. 删除重复索引
DROP INDEX IF EXISTS idx_atoms_residue;
DROP INDEX IF EXISTS idx_structures_date;

-- 2. 添加缺失的索引
-- 结构表搜索优化
CREATE INDEX IF NOT EXISTS idx_structures_title ON structures USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_structures_organism ON structures(organism) WHERE organism IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_structures_resolution ON structures(resolution) WHERE resolution IS NOT NULL;

-- 原子表查询优化
CREATE INDEX IF NOT EXISTS idx_atoms_element ON atoms(element);
CREATE INDEX IF NOT EXISTS idx_atoms_residue_name ON atoms(pdb_id, residue_name);

-- 残基表优化
CREATE INDEX IF NOT EXISTS idx_residues_name ON residues(pdb_id, residue_name);

-- 配体表优化
CREATE INDEX IF NOT EXISTS idx_ligands_formula ON ligands(formula) WHERE formula IS NOT NULL;

-- 3. 更新表统计信息
ANALYZE structures;
ANALYZE atoms;
ANALYZE residues;
ANALYZE chains;
ANALYZE ligands;
ANALYZE authors;

-- 4. 创建复合索引用于常用查询
CREATE INDEX IF NOT EXISTS idx_atoms_pdb_chain_residue ON atoms(pdb_id, chain_letter, residue_num);
CREATE INDEX IF NOT EXISTS idx_residues_pdb_chain_num ON residues(pdb_id, chain_letter, residue_num);

-- 5. 优化结构统计视图
CREATE OR REPLACE VIEW structure_stats AS
SELECT 
    s.pdb_id,
    s.title,
    s.method,
    s.resolution,
    s.organism_scientific_name,
    s.gene_name,
    COALESCE(atom_counts.atom_count, 0) as atom_count,
    COALESCE(residue_counts.residue_count, 0) as residue_count,
    COALESCE(chain_counts.chain_count, 0) as chain_count
FROM structures s
LEFT JOIN (
    SELECT pdb_id, COUNT(*) as atom_count 
    FROM atoms 
    GROUP BY pdb_id
) atom_counts ON s.pdb_id = atom_counts.pdb_id
LEFT JOIN (
    SELECT pdb_id, COUNT(*) as residue_count 
    FROM residues 
    GROUP BY pdb_id
) residue_counts ON s.pdb_id = residue_counts.pdb_id
LEFT JOIN (
    SELECT pdb_id, COUNT(*) as chain_count 
    FROM chains 
    GROUP BY pdb_id
) chain_counts ON s.pdb_id = chain_counts.pdb_id;

-- 6. 添加注释
COMMENT ON TABLE structures IS '蛋白质结构主表';
COMMENT ON TABLE atoms IS '原子坐标表（核心数据）';
COMMENT ON TABLE residues IS '残基信息表';
COMMENT ON COLUMN atoms.x_coord IS 'X坐标（埃）';
COMMENT ON COLUMN atoms.y_coord IS 'Y坐标（埃）';
COMMENT ON COLUMN atoms.z_coord IS 'Z坐标（埃）';
COMMENT ON COLUMN atoms.b_factor IS 'B因子（温度因子）';
COMMENT ON COLUMN structures.resolution IS '分辨率（埃）';
