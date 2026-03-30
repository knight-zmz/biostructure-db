#!/usr/bin/env python3
"""
Handler: verify_backup_execution

Verify backup script execution and cron job status.
Checks:
- Backup script exists and is executable
- Cron job is configured
- Backup files exist
- Backup log entries recorded
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKUP_SCRIPT = BASE_DIR / "scripts" / "backup-db.sh"
BACKUP_DIR = Path("/home/admin/backups")
BACKUP_LOG = BACKUP_DIR / "backup.log"

def main():
    try:
        result = {
            "handler": "verify_backup_execution",
            "checks": {},
            "status": "success"
        }
        
        # Check 1: Backup script exists
        if BACKUP_SCRIPT.exists():
            result["checks"]["script_exists"] = True
            result["checks"]["script_path"] = str(BACKUP_SCRIPT)
        else:
            result["checks"]["script_exists"] = False
            result["status"] = "failed"
            result["error"] = "Backup script not found"
            print(json.dumps(result))
            sys.exit(1)
        
        # Check 2: Script is executable
        import os
        is_executable = os.access(BACKUP_SCRIPT, os.X_OK)
        result["checks"]["script_executable"] = is_executable
        
        # Check 3: Cron job configured
        try:
            cron_result = subprocess.run(
                ['crontab', '-l'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            has_backup_cron = 'backup-db.sh' in cron_result.stdout
            result["checks"]["cron_configured"] = has_backup_cron
        except Exception as e:
            result["checks"]["cron_configured"] = False
            result["checks"]["cron_error"] = str(e)
        
        # Check 4: Backup files exist
        if BACKUP_DIR.exists():
            backup_files = list(BACKUP_DIR.glob("myapp_*.sql.gz"))
            result["checks"]["backup_files_count"] = len(backup_files)
            result["checks"]["backup_files_exist"] = len(backup_files) > 0
            if backup_files:
                result["checks"]["latest_backup"] = str(max(backup_files, key=lambda p: p.stat().st_mtime))
        else:
            result["checks"]["backup_files_exist"] = False
            result["checks"]["backup_files_count"] = 0
        
        # Check 5: Backup log exists
        result["checks"]["backup_log_exists"] = BACKUP_LOG.exists()
        if BACKUP_LOG.exists():
            result["checks"]["backup_log_size"] = BACKUP_LOG.stat().st_size
        
        # Summary
        all_checks_passed = all([
            result["checks"].get("script_exists", False),
            result["checks"].get("script_executable", False),
            result["checks"].get("cron_configured", False),
            result["checks"].get("backup_files_exist", False)
        ])
        
        if all_checks_passed:
            result["message"] = "Backup system verified successfully"
        else:
            result["message"] = "Backup system partially configured"
            result["status"] = "warning"
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            "handler": "verify_backup_execution",
            "status": "failed",
            "error": str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
