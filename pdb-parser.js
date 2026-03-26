/**
 * PDB 文件解析器 - 解析 Protein Data Bank 格式文件
 * 基于 PDB 文件格式规范：https://www.wwpdb.org/documentation/file-format
 */

class PDBParser {
  /**
   * 解析 PDB 文件内容
   * @param {string} content - PDB 文件原始内容
   * @returns {Object} 解析后的结构数据
   */
  parse(content) {
    const lines = content.split('\n');
    const result = {
      header: { pdbId: '', title: '', authors: [], method: '', resolution: null },
      atoms: [],
      residues: [],
      chains: new Set(),
      ligands: [],
      secondaryStructures: []
    };

    for (const line of lines) {
      const recordType = line.substring(0, 6).trim();
      
      switch (recordType) {
        case 'HEADER':
          result.header.pdbId = line.substring(62, 66).trim();
          break;
        case 'TITLE':
          result.header.title += line.substring(10, 70).trim();
          break;
        case 'AUTHOR':
          const authors = line.substring(10, 70).trim().split(',');
          result.header.authors.push(...authors.map(a => a.trim()).filter(a => a));
          break;
        case 'EXPDTA':
          result.header.method = line.substring(10, 70).trim();
          break;
        case 'REMARK':
          const remarkNum = line.substring(7, 10).trim();
          if (remarkNum === '2' || remarkNum === '3') {
            const resMatch = line.match(/RESOLUTION[\s\.]+([\d\.]+)/);
            if (resMatch) {
              result.header.resolution = parseFloat(resMatch[1]);
            }
          }
          break;
        case 'ATOM':
        case 'HETATM':
          const atom = this.parseAtomLine(line);
          result.atoms.push(atom);
          result.chains.add(atom.chain);
          break;
        case 'HELIX':
          result.secondaryStructures.push({
            type: 'helix',
            chain: line.substring(19, 20),
            startRes: parseInt(line.substring(21, 25)),
            endRes: parseInt(line.substring(33, 37)),
            length: parseInt(line.substring(38, 40))
          });
          break;
        case 'SHEET':
          result.secondaryStructures.push({
            type: 'sheet',
            chain: line.substring(21, 22),
            startRes: parseInt(line.substring(22, 26)),
            endRes: parseInt(line.substring(33, 37))
          });
          break;
        case 'HET':
          const ligand = {
            name: line.substring(7, 10).trim(),
            chain: line.substring(12, 13),
            residueNum: parseInt(line.substring(14, 18))
          };
          result.ligands.push(ligand);
          break;
      }
    }

    result.chains = Array.from(result.chains);
    result.header.title = result.header.title.trim();
    
    return result;
  }

  /**
   * 解析 ATOM/HETATM 记录行
   */
  parseAtomLine(line) {
    return {
      serial: parseInt(line.substring(6, 11)),
      name: line.substring(12, 16).trim(),
      altLoc: line.substring(16, 17),
      resName: line.substring(17, 20).trim(),
      chain: line.substring(21, 22),
      resSeq: parseInt(line.substring(22, 26)),
      iCode: line.substring(26, 27),
      x: parseFloat(line.substring(30, 38)),
      y: parseFloat(line.substring(38, 46)),
      z: parseFloat(line.substring(46, 54)),
      occupancy: parseFloat(line.substring(54, 60)) || 1.0,
      tempFactor: parseFloat(line.substring(60, 66)) || 0.0,
      element: line.substring(76, 78).trim(),
      charge: line.substring(78, 80).trim(),
      recordType: line.substring(0, 6).trim()
    };
  }

  /**
   * 将原子数据转换为 PDB 格式字符串
   */
  toPDBFormat(atoms) {
    return atoms.map((atom, i) => {
      return `ATOM  ${String(i + 1).padStart(5)}  ${atom.name.padStart(4)} ${atom.resName.padStart(3)} ${atom.chain}${String(atom.resSeq).padStart(4)}    ${String(atom.x).padStart(8).slice(0, 8)}${String(atom.y).padStart(8).slice(0, 8)}${String(atom.z).padStart(8).slice(0, 8)}  1.00  0.00           ${atom.element || 'C'}`;
    }).join('\n');
  }

  /**
   * 从 RCSB PDB 下载结构
   */
  async fetchFromRCSB(pdbId) {
    const url = `https://files.rcsb.org/download/${pdbId}.pdb`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch PDB ${pdbId}: ${response.statusText}`);
    }
    const content = await response.text();
    return this.parse(content);
  }

  /**
   * 计算 RMSD (均方根偏差)
   */
  calculateRMSD(atoms1, atoms2) {
    if (atoms1.length !== atoms2.length) {
      throw new Error('Atom arrays must have same length');
    }
    
    let sum = 0;
    for (let i = 0; i < atoms1.length; i++) {
      const dx = atoms1[i].x - atoms2[i].x;
      const dy = atoms1[i].y - atoms2[i].y;
      const dz = atoms1[i].z - atoms2[i].z;
      sum += dx * dx + dy * dy + dz * dz;
    }
    
    return Math.sqrt(sum / atoms1.length);
  }
}

module.exports = PDBParser;
