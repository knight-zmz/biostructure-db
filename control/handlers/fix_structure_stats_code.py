#!/usr/bin/env python3
"""
Handler: fix_structure_stats_code

Fix structure_stats table references to use structures table + computed counts.
Modifies:
- /api/compare endpoint (lines 111-112)
- /api/structures endpoint (lines 229, 237)
- /api/search endpoint (line 348)
"""

import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_JS = BASE_DIR / "src" / "app.js"

def main():
    try:
        # Read app.js
        with open(APP_JS, 'r', encoding='utf-8') as f:
            content = f.read()
        
        changes_made = []
        original_content = content
        
        # Fix 1: /api/compare endpoint - replace structure_stats queries
        # Pattern: pool.query('SELECT * FROM structure_stats WHERE pdb_id = $1', [pdb1/pdb2])
        compare_old_1 = "pool.query('SELECT * FROM structure_stats WHERE pdb_id = $1', [pdb1.toUpperCase()])"
        compare_old_2 = "pool.query('SELECT * FROM structure_stats WHERE pdb_id = $1', [pdb2.toUpperCase()])"
        
        compare_new_1 = """pool.query(`
      SELECT s.*, 
             (SELECT COUNT(DISTINCT chain_id) FROM polypeptides WHERE pdb_id = $1) as chain_count,
             (SELECT COUNT(*) FROM atoms WHERE pdb_id = $1) as atom_count
      FROM structures s WHERE s.pdb_id = $1`, [pdb1.toUpperCase()])"""
        
        compare_new_2 = """pool.query(`
      SELECT s.*, 
             (SELECT COUNT(DISTINCT chain_id) FROM polypeptides WHERE pdb_id = $1) as chain_count,
             (SELECT COUNT(*) FROM atoms WHERE pdb_id = $1) as atom_count
      FROM structures s WHERE s.pdb_id = $1`, [pdb2.toUpperCase()])"""
        
        if compare_old_1 in content:
            content = content.replace(compare_old_1, compare_new_1)
            changes_made.append("Fixed /api/compare query for pdb1")
        
        if compare_old_2 in content:
            content = content.replace(compare_old_2, compare_new_2)
            changes_made.append("Fixed /api/compare query for pdb2")
        
        # Fix 2: /api/structures list - replace COUNT query
        count_old = "`SELECT COUNT(*) FROM structure_stats WHERE ${where.join(' AND ')} `"
        count_new = "`SELECT COUNT(*) FROM structures WHERE ${where.join(' AND ')} `"
        
        if count_old in content:
            content = content.replace(count_old, count_new)
            changes_made.append("Fixed /api/structures COUNT query")
        
        # Fix 3: /api/structures list - replace main SELECT query
        # This is more complex, need to add subqueries for chain_count and atom_count
        select_old = "`SELECT * FROM structure_stats WHERE ${where.join(' AND ')} ORDER BY ${sortCol} ${sortOrder} ${nullsClause} LIMIT $${paramIdx++} OFFSET $${paramIdx} `"
        select_new = """`SELECT s.*, 
         (SELECT COUNT(DISTINCT chain_id) FROM polypeptides WHERE pdb_id = s.pdb_id) as chain_count,
         (SELECT COUNT(*) FROM atoms WHERE pdb_id = s.pdb_id) as atom_count
  FROM structures s 
  WHERE ${where.join(' AND ')} 
  ORDER BY ${sortCol} ${sortOrder} ${nullsClause} 
  LIMIT $${paramIdx++} OFFSET $${paramIdx} `"""
        
        if select_old in content:
            content = content.replace(select_old, select_new)
            changes_made.append("Fixed /api/structures SELECT query")
        
        # Fix 4: /api/search endpoint
        search_old = "let query = 'SELECT * FROM structure_stats WHERE 1=1'"
        search_new = """let query = `
  SELECT s.*, 
         (SELECT COUNT(DISTINCT chain_id) FROM polypeptides WHERE pdb_id = s.pdb_id) as chain_count,
         (SELECT COUNT(*) FROM atoms WHERE pdb_id = s.pdb_id) as atom_count
  FROM structures s WHERE 1=1`"""
        
        if search_old in content:
            content = content.replace(search_old, search_new)
            changes_made.append("Fixed /api/search query")
        
        # Also fix chains → polypeptides in /api/compare
        chains_old = "pool.query('SELECT * FROM chains WHERE pdb_id = $1'"
        chains_new = "pool.query('SELECT * FROM polypeptides WHERE pdb_id = $1'"
        
        if chains_old in content:
            content = content.replace(chains_old, chains_new)
            changes_made.append("Fixed chains → polypeptides in /api/compare")
        
        if not changes_made:
            result = {
                "handler": "fix_structure_stats_code",
                "status": "success",
                "message": "No changes needed - code already updated"
            }
        else:
            # Write updated app.js
            with open(APP_JS, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result = {
                "handler": "fix_structure_stats_code",
                "status": "success",
                "message": f"Fixed {len(changes_made)} structure_stats references",
                "changes": changes_made,
                "file_modified": str(APP_JS),
                "endpoints_fixed": ["/api/compare", "/api/structures", "/api/search"]
            }
        
        print(result)
        sys.exit(0)
        
    except Exception as e:
        print({
            "handler": "fix_structure_stats_code",
            "status": "failed",
            "error": str(e)
        })
        sys.exit(1)

if __name__ == '__main__':
    main()
