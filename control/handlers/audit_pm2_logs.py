#!/usr/bin/env python3
"""
Handler: audit_pm2_logs

Scan PM2 logs for anomalies, errors, and warnings.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import re

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PM2_OUT_LOG = Path("/home/admin/.pm2/logs/myapp-out.log")
PM2_ERR_LOG = Path("/home/admin/.pm2/logs/myapp-error.log")

def analyze_log_file(log_path: Path) -> dict:
    """Analyze a log file for anomalies."""
    result = {
        "exists": log_path.exists(),
        "size": 0,
        "lines": 0,
        "errors": [],
        "warnings": [],
        "error_count": 0,
        "warning_count": 0
    }
    
    if not log_path.exists():
        return result
    
    result["size"] = log_path.stat().st_size
    
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        result["lines"] = len(lines)
        
        for i, line in enumerate(lines[-100:], max(1, len(lines)-99)):  # Last 100 lines
            line_lower = line.lower()
            if 'error' in line_lower or 'fail' in line_lower or 'exception' in line_lower:
                result["errors"].append({"line": i, "content": line.strip()[:200]})
                result["error_count"] += 1
            elif 'warn' in line_lower or 'warning' in line_lower:
                result["warnings"].append({"line": i, "content": line.strip()[:200]})
                result["warning_count"] += 1
    
    return result

def main():
    try:
        result = {
            "handler": "audit_pm2_logs",
            "status": "success",
            "findings": {},
            "anomalies": []
        }
        
        # Analyze both log files
        out_analysis = analyze_log_file(PM2_OUT_LOG)
        err_analysis = analyze_log_file(PM2_ERR_LOG)
        
        result["findings"]["stdout_log"] = out_analysis
        result["findings"]["stderr_log"] = err_analysis
        
        # Check for anomalies
        total_errors = out_analysis["error_count"] + err_analysis["error_count"]
        total_warnings = out_analysis["warning_count"] + err_analysis["warning_count"]
        
        result["findings"]["total_errors"] = total_errors
        result["findings"]["total_warnings"] = total_warnings
        
        if total_errors > 0:
            result["anomalies"].append({
                "type": "errors_detected",
                "count": total_errors,
                "severity": "medium" if total_errors < 10 else "high",
                "recent_errors": out_analysis["errors"][-5:] + err_analysis["errors"][-5:]
            })
        
        if total_warnings > 5:
            result["anomalies"].append({
                "type": "frequent_warnings",
                "count": total_warnings,
                "severity": "low"
            })
        
        # Summary
        if result["anomalies"]:
            result["message"] = f"Found {len(result['anomalies'])} anomalies in PM2 logs"
            result["status"] = "warning" if total_errors == 0 else "attention_needed"
        else:
            result["message"] = "PM2 logs are clean - no significant anomalies"
        
        # Write audit report
        audits_dir = BASE_DIR / "control" / "audits"
        audits_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = audits_dir / "pm2_logs_audit.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        result["report_file"] = str(report_file)
        result["audit_timestamp"] = datetime.now().isoformat()
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            "handler": "audit_pm2_logs",
            "status": "failed",
            "error": str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
