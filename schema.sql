-- 生物结构数据库 Schema (类似 PDB)

-- 1. 结构主表
CREATE TABLE IF NOT EXISTS structures (
    pdb_id          VARCHAR(10) PRIMARY KEY,
    title           TEXT NOT NULL,
    resolution      FLOAT,
    method          VARCHAR(100),
    organism        VARCHAR(200),
    deposit_date    DATE,
    release_date    DATE,
    status          VARCHAR(20) DEFAULT 'active',
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 作者表
CREATE TABLE IF NOT EXISTS authors (
    author_id       SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    order_num       INT NOT NULL,
    UNIQUE(pdb_id, order_num)
);

-- 3. 链表
CREATE TABLE IF NOT EXISTS chains (
    chain_id        SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    chain_letter    CHAR(1) NOT NULL,
    description     TEXT,
    UNIQUE(pdb_id, chain_letter)
);

-- 4. 残基表
CREATE TABLE IF NOT EXISTS residues (
    residue_id      SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    chain_letter    CHAR(1) NOT NULL,
    residue_num     INT NOT NULL,
    residue_name    VARCHAR(10) NOT NULL,
    residue_type    VARCHAR(20)  -- amino_acid / nucleotide / other
);

-- 5. 原子坐标表 (核心表)
CREATE TABLE IF NOT EXISTS atoms (
    atom_id         SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    atom_name       VARCHAR(10) NOT NULL,
    atom_type       VARCHAR(10),  -- C, N, O, S, etc.
    chain_letter    CHAR(1) NOT NULL,
    residue_num     INT NOT NULL,
    residue_name    VARCHAR(10) NOT NULL,
    x_coord         FLOAT NOT NULL,
    y_coord         FLOAT NOT NULL,
    z_coord         FLOAT NOT NULL,
    occupancy       FLOAT DEFAULT 1.0,
    b_factor        FLOAT DEFAULT 0.0,
    element         VARCHAR(5)
);

-- 6. 配体表
CREATE TABLE IF NOT EXISTS ligands (
    ligand_id       SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    ligand_name     VARCHAR(50) NOT NULL,
    smiles          TEXT,
    formula         VARCHAR(100),
    weight          FLOAT
);

-- 7. 二级结构表
CREATE TABLE IF NOT EXISTS secondary_structures (
    ss_id           SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    chain_letter    CHAR(1) NOT NULL,
    start_residue   INT NOT NULL,
    end_residue     INT NOT NULL,
    ss_type         VARCHAR(20) NOT NULL,  -- helix / sheet / turn
    description     TEXT
);

-- 8. 引用表
CREATE TABLE IF NOT EXISTS citations (
    citation_id     SERIAL PRIMARY KEY,
    pdb_id          VARCHAR(10) REFERENCES structures(pdb_id) ON DELETE CASCADE,
    title           TEXT NOT NULL,
    journal         VARCHAR(200),
    pub_year        INT,
    doi             VARCHAR(100),
    pmid            VARCHAR(20)
);

-- 创建索引
CREATE INDEX idx_atoms_pdb ON atoms(pdb_id);
CREATE INDEX idx_atoms_chain ON atoms(pdb_id, chain_letter);
CREATE INDEX idx_residues_pdb ON residues(pdb_id);
CREATE INDEX idx_structures_method ON structures(method);
CREATE INDEX idx_structures_date ON structures(deposit_date);

-- 创建视图：结构统计
CREATE OR REPLACE VIEW structure_stats AS
SELECT 
    s.pdb_id,
    s.title,
    s.method,
    s.resolution,
    COUNT(DISTINCT a.atom_id) as atom_count,
    COUNT(DISTINCT r.residue_id) as residue_count,
    COUNT(DISTINCT c.chain_id) as chain_count
FROM structures s
LEFT JOIN atoms a ON s.pdb_id = a.pdb_id
LEFT JOIN residues r ON s.pdb_id = r.pdb_id
LEFT JOIN chains c ON s.pdb_id = c.pdb_id
GROUP BY s.pdb_id, s.title, s.method, s.resolution;

