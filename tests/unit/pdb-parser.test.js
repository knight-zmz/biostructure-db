const assert = require('assert');
const PDBParser = require('../../src/utils/pdb-parser');

describe('PDBParser Tests', () => {
  let parser;

  beforeEach(() => {
    parser = new PDBParser();
  });

  describe('parse method', () => {
    it('should parse valid PDB content', () => {
      const pdbContent = `ATOM      1  N   ALA A   1      27.340  24.430   4.710  1.00  0.00           N  
ATOM      2  CA  ALA A   1      26.260  25.410   4.840  1.00  0.00           C  
ATOM      3  C   ALA A   1      26.910  26.630   5.370  1.00  0.00           C  
ATOM      4  O   ALA A   1      27.980  26.930   4.890  1.00  0.00           O  
TER
END`;

      const result = parser.parse(pdbContent);
      
      assert(result);
      assert.strictEqual(result.atoms.length, 4);
      assert.strictEqual(result.chains.length, 1);
    });

    it('should handle empty content', () => {
      const result = parser.parse('');
      assert(result);
      assert.strictEqual(result.atoms.length, 0);
    });

    it('should handle content with no atoms', () => {
      const result = parser.parse('HEADER    TEST\nEND');
      assert(result);
      assert.strictEqual(result.header.pdbId, '');
    });
  });

  describe('parseAtomLine method', () => {
    it('should parse ATOM line correctly', () => {
      const line = 'ATOM      1  N   ALA A   1      27.340  24.430   4.710  1.00  0.00           N';
      const atom = parser.parseAtomLine(line);
      
      assert.strictEqual(atom.serial, 1);
      assert.strictEqual(atom.name, 'N');
      assert.strictEqual(atom.resName, 'ALA');
      assert.strictEqual(atom.chain, 'A');
      assert.strictEqual(atom.resSeq, 1);
      assert.strictEqual(atom.x, 27.340);
      assert.strictEqual(atom.y, 24.430);
      assert.strictEqual(atom.z, 4.710);
    });
  });

  describe('toPDBFormat method', () => {
    it('should convert atoms back to PDB format', () => {
      const atoms = [
        { name: 'N', resName: 'ALA', chain: 'A', resSeq: 1, x: 27.340, y: 24.430, z: 4.710, element: 'N' }
      ];
      const pdb = parser.toPDBFormat(atoms);
      
      assert(pdb.includes('ATOM'));
      assert(pdb.includes('ALA'));
    });
  });

  describe('calculateRMSD method', () => {
    it('should calculate RMSD between two structures', () => {
      const atoms1 = [{ x: 0, y: 0, z: 0 }, { x: 1, y: 1, z: 1 }];
      const atoms2 = [{ x: 0, y: 0, z: 0 }, { x: 1, y: 1, z: 1 }];
      
      const rmsd = parser.calculateRMSD(atoms1, atoms2);
      assert.strictEqual(rmsd, 0);
    });

    it('should throw error for different length arrays', () => {
      const atoms1 = [{ x: 0, y: 0, z: 0 }];
      const atoms2 = [{ x: 0, y: 0, z: 0 }, { x: 1, y: 1, z: 1 }];
      
      assert.throws(() => parser.calculateRMSD(atoms1, atoms2));
    });
  });
});
