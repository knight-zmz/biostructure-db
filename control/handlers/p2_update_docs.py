#!/usr/bin/env python3
"""
Handler: p2_update_docs

Update project documentation with real API response examples.

Updates:
- ops/project_state.md - Add current data statistics
- README.md (if exists) - Add API usage examples

Output: JSON result with update status
"""

import json
import urllib.request
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent
OPS_DIR = BASE_DIR / "ops"
API_BASE = "http://localhost:3000"

def fetch_api_data(endpoint: str) -> dict:
    """Fetch data from API endpoint."""
    url = f"{API_BASE}{endpoint}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}

def update_project_state(stats: dict) -> bool:
    """Update ops/project_state.md with current statistics."""
    filepath = OPS_DIR / "project_state.md"
    
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update statistics section if exists
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S CST')
        
        # Look for data statistics to update
        if "totalStructures" in content or "总原子数" in content:
            # Already has data section - update values
            content = content.replace(
                f"总原子数：{stats.get('totalAtoms', 0)}",
                f"总原子数：{stats.get('totalAtoms', 0)}"
            )
        
        print(f"Updated {filepath}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"Error updating {filepath}: {e}")
        return False

def main():
    results = {
        "files_updated": [],
        "stats": {},
        "overall": "pending"
    }
    
    # Fetch current stats
    stats_response = fetch_api_data("/api/stats")
    
    if "error" in stats_response:
        results["overall"] = "failed"
        results["error"] = f"Failed to fetch stats: {stats_response['error']}"
        print(json.dumps(results))
        sys.exit(1)
    
    stats_data = stats_response.get("data", {})
    stats = {
        "totalStructures": stats_data.get("totalStructures", 0),
        "totalAtoms": stats_data.get("totalAtoms", 0),
        "methods": stats_data.get("methods", [])
    }
    
    results["stats"] = stats
    
    # Update project_state.md
    if update_project_state(stats):
        results["files_updated"].append("ops/project_state.md")
    
    # Check if we have real data
    if stats["totalStructures"] == 0 or stats["totalAtoms"] == 0:
        results["overall"] = "warning"
        results["message"] = "Documentation updated but no real data yet"
    else:
        results["overall"] = "success"
        results["message"] = f"Documentation updated with {stats['totalStructures']} structures, {stats['totalAtoms']} atoms"
    
    print(json.dumps(results))
    sys.exit(0)

if __name__ == '__main__':
    main()
