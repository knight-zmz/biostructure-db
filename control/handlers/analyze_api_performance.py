#!/usr/bin/env python3
"""
Handler: analyze_api_performance

Analyze API performance baseline.
Outputs: response times, error rates, bottlenecks
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
import urllib.request

BASE_DIR = Path(__file__).resolve().parent.parent.parent
API_BASE = "http://localhost:3000"

def measure_endpoint(endpoint: str, iterations: int = 3) -> dict:
    """Measure response time for an endpoint."""
    times = []
    errors = 0
    
    for i in range(iterations):
        try:
            start = time.time()
            urllib.request.urlopen(f"{API_BASE}{endpoint}", timeout=5)
            elapsed = (time.time() - start) * 1000  # ms
            times.append(elapsed)
        except Exception as e:
            errors += 1
    
    if times:
        return {
            "avg_ms": round(sum(times) / len(times), 2),
            "min_ms": round(min(times), 2),
            "max_ms": round(max(times), 2),
            "errors": errors
        }
    else:
        return {
            "avg_ms": None,
            "min_ms": None,
            "max_ms": None,
            "errors": errors
        }

def main():
    try:
        result = {
            "handler": "analyze_api_performance",
            "status": "success",
            "analysis": {
                "endpoints_tested": [],
                "baseline": {},
                "bottlenecks": [],
                "recommendations": []
            }
        }
        
        # Test key endpoints
        endpoints = [
            "/api/health",
            "/api/stats",
            "/api/structures?limit=5"
        ]
        
        for endpoint in endpoints:
            metrics = measure_endpoint(endpoint)
            result["analysis"]["endpoints_tested"].append(endpoint)
            result["analysis"]["baseline"][endpoint] = metrics
        
        # Identify bottlenecks
        for ep, metrics in result["analysis"]["baseline"].items():
            if metrics["avg_ms"] and metrics["avg_ms"] > 500:
                result["analysis"]["bottlenecks"].append({
                    "endpoint": ep,
                    "avg_ms": metrics["avg_ms"],
                    "severity": "high" if metrics["avg_ms"] > 1000 else "medium"
                })
        
        # Recommendations
        result["analysis"]["recommendations"] = [
            "Monitor /api/stats response time as data grows",
            "Consider caching for frequently accessed endpoints",
            "Add database query optimization if response times exceed 500ms",
            "Set up alerting for response times > 1000ms"
        ]
        
        # Write analysis report
        audits_dir = BASE_DIR / "control" / "audits"
        audits_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = audits_dir / "api_performance_baseline.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        result["report_file"] = str(report_file)
        result["message"] = "API performance baseline analysis completed"
        result["timestamp"] = datetime.now().isoformat()
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            "handler": "analyze_api_performance",
            "status": "failed",
            "error": str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
