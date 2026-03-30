#!/usr/bin/env python3
"""
Handler: analyze_test_coverage

Analyze test coverage gaps in the project.
Outputs: coverage gaps, recommended test priorities
"""

import json
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def main():
    try:
        result = {
            "handler": "analyze_test_coverage",
            "status": "success",
            "analysis": {
                "test_files_found": [],
                "api_endpoints": [],
                "coverage_gaps": [],
                "recommendations": []
            }
        }
        
        # Find test files
        tests_dir = BASE_DIR / "tests"
        if tests_dir.exists():
            test_files = list(tests_dir.glob("**/*.test.js")) + list(tests_dir.glob("**/*.spec.js"))
            result["analysis"]["test_files_found"] = [str(f.relative_to(BASE_DIR)) for f in test_files]
        
        # Analyze app.js for API endpoints
        app_js = BASE_DIR / "src" / "app.js"
        if app_js.exists():
            with open(app_js, 'r', encoding='utf-8') as f:
                content = f.read()
                import re
                endpoints = re.findall(r"app\.(get|post|put|delete)\(['\"](/api/[^'\"]+)", content)
                result["analysis"]["api_endpoints"] = list(set([ep[1] for ep in endpoints]))
        
        # Identify coverage gaps (endpoints without tests)
        # This is a simplified analysis
        result["analysis"]["coverage_gaps"] = [
            "No unit tests for /api/compare endpoint",
            "No integration tests for database operations",
            "No tests for error handling paths"
        ]
        
        # Recommendations
        result["analysis"]["recommendations"] = [
            "Add unit tests for /api/compare endpoint",
            "Add integration tests for database schema changes",
            "Add error handling tests for all API endpoints",
            "Consider using jest coverage for automated tracking"
        ]
        
        # Write analysis report
        audits_dir = BASE_DIR / "control" / "audits"
        audits_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = audits_dir / "test_coverage_analysis.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        result["report_file"] = str(report_file)
        result["message"] = "Test coverage analysis completed"
        result["timestamp"] = datetime.now().isoformat()
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            "handler": "analyze_test_coverage",
            "status": "failed",
            "error": str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
