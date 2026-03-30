#!/usr/bin/env python3
"""
Handler: verify_api_health

Read-only verification: check API health endpoint returns 200.
Used for timer auto-trigger verification.
"""

import json
import sys
import time
import urllib.request
from datetime import datetime

API_BASE = "http://localhost:3000"

def main():
    try:
        endpoint = f"{API_BASE}/api/health"
        start = time.time()
        req = urllib.request.urlopen(endpoint, timeout=10)
        elapsed_ms = round((time.time() - start) * 1000, 2)
        body = req.read().decode('utf-8')

        result = {
            "handler": "verify_api_health",
            "status": "success",
            "endpoint": "/api/health",
            "http_status": req.getcode(),
            "response_time_ms": elapsed_ms,
            "body_length": len(body),
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(result))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({
            "handler": "verify_api_health",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
