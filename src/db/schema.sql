-- 生物结构数据库 Schema v2.0
-- 参考：PDB + UniProt + Pfam 功能设计

-- ========== 核心结构表 ==========

-- 1. 结构主表 (增强版)
CREATE TABLE IF NOT EXISTS structures (
    pdb_id          VARCHAR(10) PRIMARY KEY,
    title           TEXT NOT NULL,
    resolution      FLOAT,
    method          VARCHAR(100),  -- X-RAY, NMR, EM
    organism_scientific_name VARCHAR(200),
    organism_tax_id   INT,
    organism_common_name VARCHAR(100),
    gene_name         VARCHAR(50),
    uniprot_ids       TEXT[],  -- 关联 UniProt ID 数组
    ec_number         VARCHAR(20),  -- 酶分类编号
    go_terms          TEXT[],  -- Gene Ontology 术语
    keywords          TEXT[],  -- 功能关键词
    deposit_date      DATE,
    release_date      DATE,
    revision_date     DATE,
    status            VARCHAR(20) DEFAULT 'active',
    description       TEXT,
    assembly_count    INT,  -- 组装体数量
    entity_count      INT,  -- 分子实体数量
    polymer_count     INT,  -- 聚合物数量
    molecule_weight   FLOAT,  -- 分子量 (kDa)
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 生物组装表 (Biological Assembly)
CREATE TABLE IF NOT EXISTS assemblies (
    assembly_id     SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    assembly_id_pdb INT NOT NULL,  -- PDB 中的组装 ID
    description     TEXT,
    method          VARCHAR(100),  -- 确定方法 (PISA, author 等)
    oligomeric_state VARCHAR(50),  -- 寡聚状态 (dimer, trimer 等)
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 分子实体表 (Entity)
CREATE TABLE IF NOT EXISTS entities (
    entity_id       SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    entity_id_pdb   INT NOT NULL,
    entity_type     VARCHAR(50) NOT NULL,  -- polymer/non-polymer/water
    polymer_type    VARCHAR(50),  -- protein/nucleic_acid
    description     TEXT,
    pdbx_description TEXT,
    formula         VARCHAR(200),
    formula_weight  FLOAT,
    molecule_count  INT,
    ec_number       VARCHAR(20),
    uniprot_id      VARCHAR(20)
);

-- 4. 多肽链表 (Polypeptide Chains)
CREATE TABLE IF NOT EXISTS polypeptides (
    poly_id         SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    entity_id       INT REFERENCES entities(entity_id),
    chain_id        VARCHAR(5) NOT NULL,
    pdbx_seq_one_letter_code TEXT,  -- 完整序列
    pdbx_seq_one_letter_code_can TEXT,  -- 标准序列
    length          INT,
    organism_scientific_name VARCHAR(200),
    gene_name       VARCHAR(50),
    uniprot_id      VARCHAR(20),
    uniprot_accession VARCHAR(20),
    ec_number       VARCHAR(20),
    engineered      BOOLEAN DEFAULT FALSE,  -- 是否工程改造
    fragment        VARCHAR(100),  -- 片段信息
    mutation        VARCHAR(100),  -- 突变信息
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 残基序列表 (带注释)
CREATE TABLE IF NOT EXISTS residues (
    residue_id      SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    chain_id        VARCHAR(5) NOT NULL,
    residue_num     INT NOT NULL,
    residue_name    VARCHAR(10) NOT NULL,
    residue_type    VARCHAR(20),  -- amino_acid / nucleotide / other
    uniprot_resnum  INT,  -- 对应 UniProt 的残基编号
    secondary_struct VARCHAR(20),  -- 二级结构类型
    accessible_surface_area FLOAT,  -- 可及表面积
    phi_angle       FLOAT,  -- 二面角
    psi_angle       FLOAT,
    is_modified     BOOLEAN DEFAULT FALSE,  -- 是否修饰残基
    modification    VARCHAR(50),  -- 修饰类型
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 原子坐标表 (增强版)
CREATE TABLE IF NOT EXISTS atoms (
    atom_id         SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    atom_name       VARCHAR(10) NOT NULL,
    atom_type       VARCHAR(10),
    chain_id        VARCHAR(5) NOT NULL,
    residue_num     INT NOT NULL,
    residue_name    VARCHAR(10) NOT NULL,
    x_coord         FLOAT NOT NULL,
    y_coord         FLOAT NOT NULL,
    z_coord         FLOAT NOT NULL,
    occupancy       FLOAT DEFAULT 1.0,
    b_factor        FLOAT DEFAULT 0.0,  -- 温度因子
    element         VARCHAR(5),
    charge          VARCHAR(5),
    alt_location    CHAR(1),  -- 替代位置
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 功能注释表 ==========

-- 7. 二级结构表
CREATE TABLE IF NOT EXISTS secondary_structures (
    ss_id           SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    chain_id        VARCHAR(5) NOT NULL,
    start_residue   INT NOT NULL,
    end_residue     INT NOT NULL,
    ss_type         VARCHAR(20) NOT NULL,  -- helix / sheet / turn
    ss_class        VARCHAR(20),  -- alpha / beta / 3-10 等
    length          INT,
    comment         TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 活性位点表 (Active Sites)
CREATE TABLE IF NOT EXISTS active_sites (
    site_id         SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    site_name       VARCHAR(50),
    site_type       VARCHAR(50),  -- active_site / binding_site / metal_site
    description     TEXT,
    residues        INT[],  -- 参与残基 ID 数组
    ligands         TEXT[],  -- 配体 ID 数组
    metal_ions      TEXT[],  -- 金属离子
    evidence        VARCHAR(100),  -- 证据来源
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. 配体表 (小分子)
CREATE TABLE IF NOT EXISTS ligands (
    ligand_id       SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    ligand_name     VARCHAR(50) NOT NULL,  -- 3 字母代码
    chem_comp_id    VARCHAR(50),  -- CCD ID
    smiles          TEXT,  -- SMILES 表达式
    inchi           TEXT,  -- InChI
    inchi_key       VARCHAR(100),  -- InChIKey
    formula         VARCHAR(100),
    formula_weight  FLOAT,
    charge          INT,
    is_drug         BOOLEAN DEFAULT FALSE,  -- 是否为药物分子
    pubchem_cid     INT,  -- PubChem CID
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. 金属离子表
CREATE TABLE IF NOT EXISTS metal_ions (
    metal_id        SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    metal_type      VARCHAR(10) NOT NULL,  -- ZN, FE, MG, CA 等
    chain_id        VARCHAR(5),
    residue_num     INT,
    coordination    TEXT,  -- 配位环境描述
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. 翻译后修饰表 (PTM)
CREATE TABLE IF NOT EXISTS ptms (
    ptm_id          SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    chain_id        VARCHAR(5) NOT NULL,
    residue_num     INT NOT NULL,
    residue_name    VARCHAR(10),
    ptm_type        VARCHAR(50) NOT NULL,  -- phosphorylation / glycosylation / acetylation 等
    ptm_name        VARCHAR(100),
    modified_residue VARCHAR(10),
    pubchem_cid     INT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 外部数据库关联表 ==========

-- 12. UniProt 关联表
CREATE TABLE IF NOT EXISTS uniprot_mappings (
    mapping_id      SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    uniprot_id      VARCHAR(20) NOT NULL,
    uniprot_accession VARCHAR(20),
    protein_name    VARCHAR(200),
    gene_name       VARCHAR(50),
    organism        VARCHAR(200),
    length          INT,
    mapping_start   INT,  -- PDB 映射起始
    mapping_end     INT,  -- PDB 映射结束
    coverage        FLOAT,  -- 序列覆盖率
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Pfam 结构域表
CREATE TABLE IF NOT EXISTS pfam_domains (
    pfam_id         SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    chain_id        VARCHAR(5),
    pfam_accession  VARCHAR(10) NOT NULL,  -- 如 PF00001
    pfam_id_short   VARCHAR(50),  -- 如 7tm_1
    pfam_name       VARCHAR(200),
    start_residue   INT,
    end_residue     INT,
    e_value         FLOAT,
    score           FLOAT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. 文献引用表
CREATE TABLE IF NOT EXISTS citations (
    citation_id     SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    citation_type   VARCHAR(20),  -- primary / secondary
    title           TEXT NOT NULL,
    journal         VARCHAR(200),
    journal_abbrev  VARCHAR(100),
    pub_year        INT,
    volume          VARCHAR(20),
    pages           VARCHAR(50),
    doi             VARCHAR(100),
    pmid            VARCHAR(20),  -- PubMed ID
    authors         TEXT[],  -- 作者数组
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 搜索索引表 ==========

-- 15. 序列搜索索引
CREATE TABLE IF NOT EXISTS sequence_index (
    seq_id          SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    chain_id        VARCHAR(5) NOT NULL,
    sequence        TEXT NOT NULL,  -- 氨基酸/核酸序列
    length          INT,
    sequence_hash   VARCHAR(64),  -- 序列哈希用于快速搜索
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 创建索引 ==========

-- 结构表索引
CREATE INDEX idx_structures_method ON structures(method);
CREATE INDEX idx_structures_organism ON structures(organism_scientific_name);
CREATE INDEX idx_structures_gene ON structures(gene_name);
CREATE INDEX idx_structures_uniprot ON structures USING GIN(uniprot_ids);
CREATE INDEX idx_structures_keywords ON structures USING GIN(keywords);
CREATE INDEX idx_structures_deposit_date ON structures(deposit_date);

-- 链和残基索引
CREATE INDEX idx_polypeptides_pdb ON polypeptides(pdb_id);
CREATE INDEX idx_polypeptides_uniprot ON polypeptides(uniprot_id);
CREATE INDEX idx_residues_pdb_chain ON residues(pdb_id, chain_id);
CREATE INDEX idx_atoms_pdb_chain ON atoms(pdb_id, chain_id);
CREATE INDEX idx_atoms_residue ON atoms(pdb_id, residue_num);

-- 功能注释索引
CREATE INDEX idx_active_sites_pdb ON active_sites(pdb_id);
CREATE INDEX idx_ligands_pdb ON ligands(pdb_id);
CREATE INDEX idx_ligands_name ON ligands(ligand_name);
CREATE INDEX idx_ptms_pdb ON ptms(pdb_id);

-- 外部关联索引
CREATE INDEX idx_uniprot_pdb ON uniprot_mappings(pdb_id);
CREATE INDEX idx_uniprot_accession ON uniprot_mappings(uniprot_accession);
CREATE INDEX idx_pfam_pdb ON pfam_domains(pdb_id);
CREATE INDEX idx_pfam_accession ON pfam_domains(pfam_accession);

-- 序列索引
CREATE INDEX idx_sequence_pdb ON sequence_index(pdb_id);
CREATE INDEX idx_sequence_hash ON sequence_index(sequence_hash);

-- ========== 创建视图 ==========

-- 结构统计视图
CREATE OR REPLACE VIEW structure_stats AS
SELECT 
    s.pdb_id,
    s.title,
    s.method,
    s.resolution,
    s.organism_scientific_name,
    s.gene_name,
    COUNT(DISTINCT a.atom_id) as atom_count,
    COUNT(DISTINCT r.residue_id) as residue_count,
    COUNT(DISTINCT p.poly_id) as chain_count,
    COUNT(DISTINCT l.ligand_id) as ligand_count,
    s.molecule_weight
FROM structures s
LEFT JOIN atoms a ON s.pdb_id = a.pdb_id
LEFT JOIN residues r ON s.pdb_id = r.pdb_id
LEFT JOIN polypeptides p ON s.pdb_id = p.pdb_id
LEFT JOIN ligands l ON s.pdb_id = l.pdb_id
GROUP BY s.pdb_id, s.title, s.method, s.resolution, 
         s.organism_scientific_name, s.gene_name, s.molecule_weight;

-- 配体统计视图
CREATE OR REPLACE VIEW ligand_stats AS
SELECT 
    l.ligand_name,
    COUNT(*) as structure_count,
    ARRAY_AGG(DISTINCT l.pdb_id) as pdb_ids
FROM ligands l
GROUP BY l.ligand_name
ORDER BY structure_count DESC;

-- 金属离子统计视图
CREATE OR REPLACE VIEW metal_ion_stats AS
SELECT 
    m.metal_type,
    COUNT(*) as structure_count,
    ARRAY_AGG(DISTINCT m.pdb_id) as pdb_ids
FROM metal_ions m
GROUP BY m.metal_type
ORDER BY structure_count DESC;

COMMENT ON TABLE structures IS '蛋白质/核酸结构主表 - 类似 PDB 核心表';
COMMENT ON TABLE polypeptides IS '多肽链信息 - 包含完整序列和 UniProt 关联';
COMMENT ON TABLE active_sites IS '活性位点和结合位点 - 功能注释核心';
COMMENT ON TABLE ligands IS '小分子配体 - 药物发现重要数据';
COMMENT ON TABLE ptms IS '翻译后修饰 - 磷酸化/糖基化等';
COMMENT ON TABLE uniprot_mappings IS '与 UniProt 数据库的映射关系';
COMMENT ON TABLE pfam_domains IS 'Pfam 蛋白质结构域注释';
