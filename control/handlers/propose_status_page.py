#!/usr/bin/env python3
"""
Handler: propose_status_page

Generate structure proposal for /status page.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def main():
    try:
        result = {
            "handler": "propose_status_page",
            "status": "success",
            "proposal": {
                "page": "/status",
                "title": "System Status",
                "sections": [
                    {
                        "name": "API Health",
                        "endpoint": "/api/health",
                        "display": ["status", "database", "uptime"]
                    },
                    {
                        "name": "Database Statistics",
                        "endpoint": "/api/stats",
                        "display": ["totalStructures", "totalAtoms", "methods"]
                    },
                    {
                        "name": "System Metrics",
                        "source": "control/audits/api_performance_baseline.md",
                        "display": ["response_time", "error_rate"]
                    },
                    {
                        "name": "Control Plane Status",
                        "source": "control/runtime_state.json",
                        "display": ["phase", "phase_status", "last_activity"]
                    }
                ],
                "refresh_interval": "30s",
                "auto_refresh": True
            },
            "implementation_notes": [
                "Create public/status.html with embedded JavaScript for auto-refresh",
                "Use fetch() to poll /api/health and /api/stats endpoints",
                "Display uptime in human-readable format (days, hours, minutes)",
                "Add visual indicators (green/yellow/red) for health status"
            ]
        }
        
        # Write proposal
        audits_dir = BASE_DIR / "control" / "audits"
        audits_dir.mkdir(parents=True, exist_ok=True)
        
        proposal_file = audits_dir / "status_page_proposal.json"
        with open(proposal_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        result["proposal_file"] = str(proposal_file)
        result["message"] = "Status page structure proposal generated"
        result["audit_timestamp"] = datetime.now().isoformat()
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            "handler": "propose_status_page",
            "status": "failed",
            "error": str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
