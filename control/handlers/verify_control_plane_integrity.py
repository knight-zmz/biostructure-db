#!/usr/bin/env python3
"""
Handler: verify_control_plane_integrity

Read-only verification: check control plane files exist and are valid JSON.
Zero-dependency, safe for timer verification.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONTROL_DIR = BASE_DIR / "control"

REQUIRED_FILES = [
    "queue.json",
    "runtime_state.json",
    "phase_policy.json",
    "paused.json"
]

def main():
    try:
        checks = []
        all_ok = True

        for fname in REQUIRED_FILES:
            fpath = CONTROL_DIR / fname
            exists = fpath.exists()
            size = fpath.stat().st_size if exists else 0
            valid_json = False

            if exists and size > 0:
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        json.load(f)
                    valid_json = True
                except json.JSONDecodeError:
                    valid_json = False

            ok = exists and size > 0 and valid_json
            if not ok:
                all_ok = False

            checks.append({
                "file": fname,
                "exists": exists,
                "size": size,
                "valid_json": valid_json,
                "ok": ok
            })

        result = {
            "handler": "verify_control_plane_integrity",
            "status": "success" if all_ok else "failed",
            "checks": checks,
            "all_ok": all_ok,
            "timestamp": datetime.now().isoformat()
        }

        print(json.dumps(result))
        sys.exit(0 if all_ok else 1)

    except Exception as e:
        print(json.dumps({
            "handler": "verify_control_plane_integrity",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
