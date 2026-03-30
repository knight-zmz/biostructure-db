#!/usr/bin/env python3
"""
Handler: fix_package_json

Fix package.json entry point to match actual file structure.
Changes:
- main: "app.js" → "src/app.js"
- scripts.start: "node app.js" → "node src/app.js"
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PACKAGE_JSON = BASE_DIR / "package.json"

def main():
    try:
        # Read package.json
        with open(PACKAGE_JSON, 'r', encoding='utf-8') as f:
            package = json.load(f)
        
        changes_made = []
        
        # Fix main entry
        if package.get('main') == 'app.js':
            package['main'] = 'src/app.js'
            changes_made.append('main: app.js → src/app.js')
        
        # Fix scripts.start
        if package.get('scripts', {}).get('start') == 'node app.js':
            package['scripts']['start'] = 'node src/app.js'
            changes_made.append('scripts.start: node app.js → node src/app.js')
        
        if not changes_made:
            result = {
                "handler": "fix_package_json",
                "status": "success",
                "message": "No changes needed - package.json already correct"
            }
        else:
            # Write updated package.json
            with open(PACKAGE_JSON, 'w', encoding='utf-8') as f:
                json.dump(package, f, indent=2, ensure_ascii=False)
            
            result = {
                "handler": "fix_package_json",
                "status": "success",
                "message": f"Fixed {len(changes_made)} entries",
                "changes": changes_made
            }
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            "handler": "fix_package_json",
            "status": "failed",
            "error": str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
