#!/usr/bin/env python3
"""
Handler: p2_import_samples

Import selected PDB structures via API endpoint.

Uses the /api/import-samples endpoint to import pre-configured sample structures.

Output: JSON result with import status for each structure
"""

import json
import urllib.request
import sys

API_BASE = "http://localhost:3000"
IMPORT_ENDPOINT = "/api/import-samples"

def import_samples() -> dict:
    """Call API to import sample structures."""
    url = f"{API_BASE}{IMPORT_ENDPOINT}"
    
    try:
        req = urllib.request.Request(
            url,
            data=b'{}',
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=300) as response:
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
    print("Starting PDB sample import...")
    
    result = import_samples()
    
    if result["status"] != "success":
        print(json.dumps({
            "overall": "failed",
            "error": result.get("error", "Unknown error")
        }))
        sys.exit(1)
    
    # Parse import results
    import_data = result.get("data", {}).get("data", [])
    
    success_count = sum(1 for item in import_data if item.get("status") == "success")
    failed_count = len(import_data) - success_count
    
    output = {
        "overall": "success" if failed_count == 0 else "partial",
        "imported": success_count,
        "failed": failed_count,
        "details": import_data,
        "message": f"Imported {success_count}/{len(import_data)} structures"
    }
    
    print(json.dumps(output, indent=2))
    sys.exit(0 if failed_count == 0 else 1)

if __name__ == '__main__':
    main()
