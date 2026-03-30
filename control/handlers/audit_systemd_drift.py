#!/usr/bin/env python3
"""
Handler: audit_systemd_drift

Audit systemd service/timer state vs control plane metadata.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
QUEUE_JSON = BASE_DIR / "control" / "queue.json"

def check_systemd_unit(unit_name: str) -> dict:
    """Check systemd unit status."""
    result = {"exists": False, "enabled": False, "active": False}
    
    try:
        # Check if unit exists
        cat_result = subprocess.run(
            ['systemctl', 'cat', unit_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        result["exists"] = cat_result.returncode == 0
        
        # Check if enabled
        enabled_result = subprocess.run(
            ['systemctl', 'is-enabled', unit_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        result["enabled"] = enabled_result.stdout.strip() == 'enabled'
        
        # Check if active
        active_result = subprocess.run(
            ['systemctl', 'is-active', unit_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        result["active"] = active_result.stdout.strip() == 'active'
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    try:
        result = {
            "handler": "audit_systemd_drift",
            "status": "success",
            "findings": {},
            "drift_detected": []
        }
        
        # Load queue.json
        with open(QUEUE_JSON, 'r', encoding='utf-8') as f:
            queue = json.load(f)
        
        # Check systemd units
        service_status = check_systemd_unit('openclaw-agent.service')
        timer_status = check_systemd_unit('openclaw-agent.timer')
        
        result["findings"]["service"] = service_status
        result["findings"]["timer"] = timer_status
        
        # Check control plane metadata
        timer_enabled_meta = queue.get('config', {}).get('timer_enabled', False)
        result["findings"]["metadata_timer_enabled"] = timer_enabled_meta
        
        # Check for drift
        systemd_timer_active = timer_status["enabled"] or timer_status["active"]
        if systemd_timer_active != timer_enabled_meta:
            result["drift_detected"].append({
                "type": "timer_enabled_mismatch",
                "systemd": systemd_timer_active,
                "metadata": timer_enabled_meta,
                "severity": "medium"
            })
        
        # Summary
        if result["drift_detected"]:
            result["message"] = f"Detected {len(result['drift_detected'])} drift issues"
            result["status"] = "warning"
        else:
            result["message"] = "Systemd and control plane metadata are in sync"
        
        # Write audit report
        audits_dir = BASE_DIR / "control" / "audits"
        audits_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = audits_dir / "systemd_drift_audit.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        result["report_file"] = str(report_file)
        result["audit_timestamp"] = datetime.now().isoformat()
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            "handler": "audit_systemd_drift",
            "status": "failed",
            "error": str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
