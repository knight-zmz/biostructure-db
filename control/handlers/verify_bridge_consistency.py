#!/usr/bin/env python3
"""
Handler: verify_bridge_consistency

Read-only verification: check bridge consistency across control plane files.
Calls scripts/check-bridge-consistency.py and reports results.

Boundary: read_only_verification
Risk level: low (no modifications)
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Project root
SCRIPT_PATH = BASE_DIR / "scripts" / "check-bridge-consistency.py"


def main():
    if not SCRIPT_PATH.exists():
        print(json.dumps({
            "handler": "verify_bridge_consistency",
            "status": "failed",
            "error": f"Script not found: {SCRIPT_PATH}",
            "timestamp": datetime.now().isoformat()
        }))
        sys.exit(1)
    
    try:
        # Run the consistency check script (Python 3.6 compatible)
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=30,
            cwd=str(BASE_DIR)
        )
        
        # Parse output to extract key metrics
        output_lines = result.stdout.strip().split('\n')
        checks_passed = result.returncode == 0
        issues = []
        
        for line in output_lines:
            if '❌' in line and 'DRIFT' not in line:
                issues.append(line.strip())
        
        # Build handler result
        handler_result = {
            "handler": "verify_bridge_consistency",
            "status": "success" if checks_passed else "drift_detected",
            "checks_passed": checks_passed,
            "issues_count": len(issues),
            "issues": issues[:5],  # Limit to first 5 issues
            "full_output": result.stdout.strip(),
            "timestamp": datetime.now().isoformat()
        }
        
        print(json.dumps(handler_result, ensure_ascii=False, indent=2))
        sys.exit(0 if checks_passed else 1)
        
    except subprocess.TimeoutExpired:
        print(json.dumps({
            "handler": "verify_bridge_consistency",
            "status": "failed",
            "error": "Timeout expired (30s)",
            "timestamp": datetime.now().isoformat()
        }))
        sys.exit(1)
        
    except Exception as e:
        print(json.dumps({
            "handler": "verify_bridge_consistency",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))
        sys.exit(1)


if __name__ == '__main__':
    main()
