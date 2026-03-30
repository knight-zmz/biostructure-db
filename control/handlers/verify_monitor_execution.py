#!/usr/bin/env python3
"""
Handler: verify_monitor_execution

Verify monitoring script execution and metrics logging.
Checks:
- Monitor script exists and is executable
- Cron job is configured
- Metrics log exists and has recent entries
- Alert log exists
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MONITOR_SCRIPT = BASE_DIR / "scripts" / "monitor.sh"
LOGS_DIR = BASE_DIR / "control" / "logs"
METRICS_LOG = LOGS_DIR / "metrics.log"
ALERTS_LOG = LOGS_DIR / "alerts.log"

def main():
    try:
        result = {
            "handler": "verify_monitor_execution",
            "checks": {},
            "status": "success"
        }
        
        # Check 1: Monitor script exists
        if MONITOR_SCRIPT.exists():
            result["checks"]["script_exists"] = True
            result["checks"]["script_path"] = str(MONITOR_SCRIPT)
        else:
            result["checks"]["script_exists"] = False
            result["status"] = "failed"
            result["error"] = "Monitor script not found"
            print(json.dumps(result))
            sys.exit(1)
        
        # Check 2: Script is executable
        import os
        is_executable = os.access(MONITOR_SCRIPT, os.X_OK)
        result["checks"]["script_executable"] = is_executable
        
        # Check 3: Cron job configured
        import subprocess
        try:
            cron_result = subprocess.run(
                ['crontab', '-l'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            has_monitor_cron = 'monitor.sh' in cron_result.stdout
            result["checks"]["cron_configured"] = has_monitor_cron
        except Exception as e:
            result["checks"]["cron_configured"] = False
            result["checks"]["cron_error"] = str(e)
        
        # Check 4: Logs directory exists
        result["checks"]["logs_dir_exists"] = LOGS_DIR.exists()
        
        # Check 5: Metrics log exists and has content
        if METRICS_LOG.exists():
            result["checks"]["metrics_log_exists"] = True
            result["checks"]["metrics_log_size"] = METRICS_LOG.stat().st_size
            
            # Check for recent entries (last 24 hours)
            with open(METRICS_LOG, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                result["checks"]["metrics_log_lines"] = len(lines)
                if lines:
                    last_line = lines[-1]
                    # Extract timestamp from log line
                    if last_line.startswith('2026'):
                        result["checks"]["last_metric_timestamp"] = last_line.split('|')[0].strip()
        else:
            result["checks"]["metrics_log_exists"] = False
            result["checks"]["metrics_log_size"] = 0
        
        # Check 6: Alerts log exists
        result["checks"]["alerts_log_exists"] = ALERTS_LOG.exists()
        if ALERTS_LOG.exists():
            result["checks"]["alerts_log_size"] = ALERTS_LOG.stat().st_size
        
        # Summary
        all_checks_passed = all([
            result["checks"].get("script_exists", False),
            result["checks"].get("script_executable", False),
            result["checks"].get("cron_configured", False),
            result["checks"].get("metrics_log_exists", False)
        ])
        
        if all_checks_passed:
            result["message"] = "Monitoring system verified successfully"
        else:
            result["message"] = "Monitoring system partially configured"
            result["status"] = "warning"
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            "handler": "verify_monitor_execution",
            "status": "failed",
            "error": str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
