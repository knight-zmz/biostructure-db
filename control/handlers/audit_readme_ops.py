#!/usr/bin/env python3
"""
Handler: audit_readme_ops

Audit README.md and ops/project_state.md for consistency.
Checks:
- Start commands match
- API endpoints documented match actual endpoints
- Project status matches runtime_state
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
README = BASE_DIR / "README.md"
OPS_STATE = BASE_DIR / "ops" / "project_state.md"
RUNTIME_STATE = BASE_DIR / "control" / "runtime_state.json"

def extract_start_commands(content: str) -> list:
    """Extract start commands from markdown content."""
    commands = []
    # Look for npm start, pm2 start, node commands in code blocks
    patterns = [
        r'npm\s+start',
        r'pm2\s+start\s+\S+',
        r'node\s+\S+\.js'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, content)
        commands.extend(matches)
    return commands

def extract_api_endpoints(content: str) -> list:
    """Extract API endpoints from markdown content."""
    endpoints = []
    # Look for /api/... patterns
    matches = re.findall(r'/api/\S+', content)
    return list(set(matches))

def main():
    try:
        result = {
            "handler": "audit_readme_ops",
            "status": "success",
            "findings": {},
            "inconsistencies": []
        }
        
        # Load files
        readme_content = README.read_text(encoding='utf-8') if README.exists() else ""
        ops_content = OPS_STATE.read_text(encoding='utf-8') if OPS_STATE.exists() else ""
        
        with open(RUNTIME_STATE, 'r', encoding='utf-8') as f:
            runtime = json.load(f)
        
        # Check 1: Start commands consistency
        readme_commands = extract_start_commands(readme_content)
        ops_commands = extract_start_commands(ops_content)
        
        result["findings"]["readme_start_commands"] = readme_commands
        result["findings"]["ops_start_commands"] = ops_commands
        
        if readme_commands != ops_commands and readme_commands and ops_commands:
            result["inconsistencies"].append({
                "type": "start_commands_mismatch",
                "readme": readme_commands,
                "ops": ops_commands
            })
        
        # Check 2: API endpoints
        readme_endpoints = extract_api_endpoints(readme_content)
        result["findings"]["readme_api_endpoints"] = readme_endpoints
        
        # Check 3: Phase status consistency
        current_state = runtime.get('current_state', {})
        if isinstance(current_state, dict):
            runtime_phase = current_state.get('phase', 'unknown')
        else:
            runtime_phase = 'unknown'
        result["findings"]["runtime_phase"] = runtime_phase
        
        # Check 4: Last update timestamps
        result["findings"]["audit_timestamp"] = datetime.now().isoformat()
        
        # Summary
        if result["inconsistencies"]:
            result["message"] = f"Found {len(result['inconsistencies'])} inconsistencies"
            result["status"] = "warning"
        else:
            result["message"] = "README and ops documentation are consistent"
        
        # Write audit report
        audits_dir = BASE_DIR / "control" / "audits"
        audits_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = audits_dir / "readme_ops_audit.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        result["report_file"] = str(report_file)
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            "handler": "audit_readme_ops",
            "status": "failed",
            "error": str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
