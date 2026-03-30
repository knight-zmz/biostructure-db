#!/usr/bin/env python3
"""
Handler: fix_authors_code

Fix authors table reference to use structures.authors TEXT[] field.
Modifies:
- Line 265: Remove separate authors query
- Line 280: Transform TEXT[] to expected format
- Line 441: Remove legacy comment about authors
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
            lines = content.split('\n')
        
        changes_made = []
        
        # Fix 1: Replace authors query with TEXT[] extraction (around line 265)
        # Find and replace the authors query pattern
        old_authors_query = "const authors = await pool.query('SELECT name FROM authors WHERE pdb_id = $1 ORDER BY order_num', [pdbId]);"
        new_authors_logic = """// Extract authors from structures.authors TEXT[] field
    const authorsArray = structure.rows[0].authors || [];
    const authorsFormatted = authorsArray.map((name, index) => ({
      name: name,
      order_num: index + 1
    }));"""
        
        if old_authors_query in content:
            content = content.replace(old_authors_query, new_authors_logic)
            changes_made.append("Replaced authors query with TEXT[] extraction")
        
        # Fix 2: Update authors reference in response (around line 280)
        # Change from authors.rows to authorsFormatted
        old_authors_response = "authors: authors.rows,"
        new_authors_response = "authors: authorsFormatted,"
        
        if old_authors_response in content:
            content = content.replace(old_authors_response, new_authors_response)
            changes_made.append("Updated response to use authorsFormatted")
        
        # Fix 3: Remove legacy comment about authors (around line 441)
        old_comment = "// 作者信息暂不存储（schema 中无 authors 字段）"
        if old_comment in content:
            content = content.replace(old_comment, "// 作者信息存储在 structures.authors TEXT[] 字段")
            changes_made.append("Updated authors comment")
        
        # Fix 4: Remove chains query that uses wrong table name (should be polypeptides)
        # This is related to the chains/polypeptides fix
        old_chains_query = "const chains = await pool.query('SELECT * FROM chains WHERE pdb_id = $1', [pdbId]);"
        new_chains_query = "const chains = await pool.query('SELECT * FROM polypeptides WHERE pdb_id = $1', [pdbId]);"
        
        if old_chains_query in content:
            content = content.replace(old_chains_query, new_chains_query)
            changes_made.append("Fixed chains → polypeptides table reference")
        
        if not changes_made:
            result = {
                "handler": "fix_authors_code",
                "status": "success",
                "message": "No changes needed - code already updated"
            }
        else:
            # Write updated app.js
            with open(APP_JS, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result = {
                "handler": "fix_authors_code",
                "status": "success",
                "message": f"Fixed {len(changes_made)} issues",
                "changes": changes_made,
                "file_modified": str(APP_JS)
            }
        
        print(result)
        sys.exit(0)
        
    except Exception as e:
        print({
            "handler": "fix_authors_code",
            "status": "failed",
            "error": str(e)
        })
        sys.exit(1)

if __name__ == '__main__':
    main()
