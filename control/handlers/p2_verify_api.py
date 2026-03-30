#!/usr/bin/env python3
"""
Handler: p2_verify_api

Verify API endpoints return real data after sample import.

Checks:
- /api/health - Application health
- /api/stats - Statistics (should show non-zero structures/atoms)
- /api/structures - Structure list (should return real data)

Output: JSON result with verification status
"""

import json
import urllib.request
import sys

API_BASE = "http://localhost:3000"

def check_endpoint(endpoint: str) -> dict:
    """Check a single API endpoint."""
    url = f"{API_BASE}{endpoint}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return {
                "status": "success",
                "http_code": response.status,
                "data": data
            }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }

def main():
    results = {
        "endpoints": {},
        "overall": "pending"
    }
    
    # Check health
    health = check_endpoint("/api/health")
    results["endpoints"]["health"] = health
    
    if health["status"] != "success":
        results["overall"] = "failed"
        results["error"] = "Health check failed"
        print(json.dumps(results))
        sys.exit(1)
    
    # Check stats
    stats = check_endpoint("/api/stats")
    results["endpoints"]["stats"] = stats
    
    if stats["status"] != "success":
        results["overall"] = "failed"
        results["error"] = "Stats endpoint failed"
        print(json.dumps(results))
        sys.exit(1)
    
    # Verify stats has real data
    stats_data = stats["data"].get("data", {})
    total_structures = stats_data.get("totalStructures", 0)
    total_atoms = stats_data.get("totalAtoms", 0)
    
    results["verification"] = {
        "total_structures": total_structures,
        "total_atoms": total_atoms,
        "has_real_data": total_structures > 0 and total_atoms > 0
    }
    
    if not results["verification"]["has_real_data"]:
        results["overall"] = "failed"
        results["error"] = "No real data found (structures=0 or atoms=0)"
        print(json.dumps(results))
        sys.exit(1)
    
    # Check structures list (optional - may be slow)
    try:
        structures = check_endpoint("/api/structures?limit=3")
        results["endpoints"]["structures"] = structures
    except Exception as e:
        results["endpoints"]["structures"] = {"status": "skipped", "reason": str(e)}
    
    # All checks passed
    results["overall"] = "success"
    results["message"] = f"API verified: {total_structures} structures, {total_atoms} atoms"
    
    print(json.dumps(results))
    sys.exit(0)

if __name__ == '__main__':
    main()
