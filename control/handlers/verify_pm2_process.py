#!/usr/bin/env python3
"""
Handler: verify_pm2_process

Read-only verification: check PM2 process 'myapp' is online.
Used for timer auto-trigger verification.
"""

import json
import sys
import subprocess
from datetime import datetime

def main():
    try:
        result = subprocess.run(
            ['pm2', 'jlist'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=15
        )

        if result.returncode != 0:
            print(json.dumps({
                "handler": "verify_pm2_process",
                "status": "failed",
                "error": f"pm2 jlist failed: {result.stderr}",
                "timestamp": datetime.now().isoformat()
            }))
            sys.exit(1)

        processes = json.loads(result.stdout) if result.stdout.strip() else []
        myapp = [p for p in processes if p.get('name') == 'myapp']

        if not myapp:
            print(json.dumps({
                "handler": "verify_pm2_process",
                "status": "failed",
                "error": "Process 'myapp' not found in PM2",
                "timestamp": datetime.now().isoformat()
            }))
            sys.exit(1)

        proc = myapp[0]
        pm_info = proc.get('pm2_env', {})
        status = pm_info.get('status', 'unknown')
        restart_time = pm_info.get('restart_time', 0)

        output = {
            "handler": "verify_pm2_process",
            "status": "success",
            "process": "myapp",
            "pm2_status": status,
            "restart_count": restart_time,
            "uptime_ms": pm_info.get('pm_uptime', 0),
            "timestamp": datetime.now().isoformat()
        }

        if status != 'online':
            output['status'] = 'failed'
            output['error'] = f"Process status is '{status}', expected 'online'"
            print(json.dumps(output))
            sys.exit(1)

        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({
            "handler": "verify_pm2_process",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
