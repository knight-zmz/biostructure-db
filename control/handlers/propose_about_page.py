#!/usr/bin/env python3
"""
Handler: propose_about_page

Generate structure proposal for /about page.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def main():
    try:
        result = {
            "handler": "propose_about_page",
            "status": "success",
            "proposal": {
                "page": "/about",
                "title": "About BioStructure DB",
                "sections": [
                    {
                        "name": "Project Overview",
                        "content_source": "README.md",
                        "display": ["description", "core_features"]
                    },
                    {
                        "name": "Technical Stack",
                        "content_source": "README.md",
                        "display": ["backend", "database", "cache", "deployment"]
                    },
                    {
                        "name": "Data Sources",
                        "content": [
                            "PDB (Protein Data Bank)",
                            "UniProt",
                            "Pfam"
                        ]
                    },
                    {
                        "name": "API Documentation",
                        "link": "/api/docs"
                    },
                    {
                        "name": "System Status",
                        "link": "/status"
                    },
                    {
                        "name": "GitHub Repository",
                        "link": "https://github.com/knight-zmz/biostructure-db"
                    }
                ]
            },
            "implementation_notes": [
                "Create public/about.html with static content from README.md",
                "Include project description and core features",
                "List technical stack with version information",
                "Add links to API docs, status page, and GitHub",
                "Consider adding a changelog section linked to GitHub releases"
            ]
        }
        
        # Write proposal
        audits_dir = BASE_DIR / "control" / "audits"
        audits_dir.mkdir(parents=True, exist_ok=True)
        
        proposal_file = audits_dir / "about_page_proposal.json"
        with open(proposal_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        result["proposal_file"] = str(proposal_file)
        result["message"] = "About page structure proposal generated"
        result["audit_timestamp"] = datetime.now().isoformat()
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            "handler": "propose_about_page",
            "status": "failed",
            "error": str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
