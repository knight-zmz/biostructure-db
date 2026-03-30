#!/usr/bin/env python3
"""
Handler: audit_table_references

Audit table reference inconsistencies between app code and schema.
Analyzes chains vs polypeptides, structure_stats missing table, authors design.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
SCHEMA_FILE = SRC_DIR / "db" / "schema.sql"
AUDITS_DIR = BASE_DIR / "control" / "audits"

# Ensure audits directory exists
AUDITS_DIR.mkdir(parents=True, exist_ok=True)

def get_schema_tables() -> set:
    """Extract table names from schema.sql."""
    tables = set()
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match CREATE TABLE IF NOT EXISTS tablename
    matches = re.findall(r'CREATE TABLE IF NOT EXISTS (\w+)', content)
    tables.update(matches)
    
    return tables

def find_table_references(filepath: Path, table_name: str) -> list:
    """Find all references to a table in a file."""
    references = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        # Look for FROM table, INTO table, JOIN table
        patterns = [
            rf'FROM\s+{table_name}\b',
            rf'INTO\s+{table_name}\b',
            rf'JOIN\s+{table_name}\b',
            rf"'[^']*{table_name}[^']*'"  # String references
        ]
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                references.append({
                    "line": i,
                    "content": line.strip()[:100]
                })
                break
    
    return references

def audit_chains_polypeptides() -> dict:
    """Audit chains vs polypeptides table naming."""
    schema_tables = get_schema_tables()
    
    result = {
        "audit_type": "chains_vs_polypeptides",
        "schema_has_chains": "chains" in schema_tables,
        "schema_has_polypeptides": "polypeptides" in schema_tables,
        "code_references": [],
        "recommendation": "",
        "risk_level": ""
    }
    
    # Find all references to "chains" in app.js
    app_js = SRC_DIR / "app.js"
    if app_js.exists():
        chains_refs = find_table_references(app_js, "chains")
        result["code_references"] = chains_refs
        result["chains_query_count"] = len(chains_refs)
    
    # Analysis
    if "polypeptides" in schema_tables and "chains" not in schema_tables:
        result["recommendation"] = "Replace 'chains' with 'polypeptides' in app.js queries"
        result["risk_level"] = "low"
        result["fix_type"] = "search_and_replace"
        result["files_to_modify"] = ["src/app.js"]
    elif "chains" in schema_tables:
        result["recommendation"] = "No fix needed - chains table exists"
        result["risk_level"] = "none"
    
    return result

def audit_structure_stats() -> dict:
    """Audit structure_stats table usage."""
    schema_tables = get_schema_tables()
    
    result = {
        "audit_type": "structure_stats",
        "schema_has_structure_stats": "structure_stats" in schema_tables,
        "code_references": [],
        "recommendation": "",
        "risk_level": ""
    }
    
    # Find all references to "structure_stats" in app.js
    app_js = SRC_DIR / "app.js"
    if app_js.exists():
        stats_refs = find_table_references(app_js, "structure_stats")
        result["code_references"] = stats_refs
        result["structure_stats_query_count"] = len(stats_refs)
    
    # Analysis
    if "structure_stats" not in schema_tables:
        if len(result["code_references"]) > 0:
            result["recommendation"] = "Either: (A) Add structure_stats table to schema, or (B) Remove legacy code from app.js"
            result["risk_level"] = "medium"
            result["options"] = {
                "option_a": {
                    "action": "Add structure_stats table to schema",
                    "impact": "Requires schema migration",
                    "complexity": "medium"
                },
                "option_b": {
                    "action": "Remove structure_stats queries from app.js",
                    "impact": "May break /api/compare endpoint",
                    "complexity": "low"
                }
            }
            result["preferred_option"] = "option_b - Check if structure_stats data can be derived from structures table"
    else:
        result["recommendation"] = "No fix needed - structure_stats table exists"
        result["risk_level"] = "none"
    
    return result

def audit_authors_design() -> dict:
    """Audit authors table vs TEXT[] field design."""
    schema_tables = get_schema_tables()
    
    result = {
        "audit_type": "authors_design",
        "schema_has_authors_table": "authors" in schema_tables,
        "code_references": [],
        "recommendation": "",
        "risk_level": ""
    }
    
    # Find all references to "authors" in app.js
    app_js = SRC_DIR / "app.js"
    if app_js.exists():
        authors_refs = find_table_references(app_js, "authors")
        result["code_references"] = authors_refs
        result["authors_query_count"] = len(authors_refs)
    
    # Check if structures table has authors field
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_content = f.read()
    
    has_authors_field = 'authors' in schema_content and 'structures' in schema_content
    
    # Analysis
    if "authors" not in schema_tables and len(result["code_references"]) > 0:
        result["recommendation"] = "Code expects separate authors table, but schema uses structures.authors TEXT[]"
        result["risk_level"] = "medium"
        result["options"] = {
            "option_a": {
                "action": "Create separate authors table",
                "impact": "Requires schema migration and data migration",
                "complexity": "high"
            },
            "option_b": {
                "action": "Update app.js to use structures.authors field",
                "impact": "Code change only",
                "complexity": "low"
            }
        }
        result["preferred_option"] = "option_b - Keep simple design with TEXT[] unless complex author queries needed"
    else:
        result["recommendation"] = "Design is consistent"
        result["risk_level"] = "none"
    
    return result

def main():
    try:
        # Run all audits
        chains_audit = audit_chains_polypeptides()
        stats_audit = audit_structure_stats()
        authors_audit = audit_authors_design()
        
        # Generate combined report
        report = {
            "audit_date": datetime.now().isoformat(),
            "audits": {
                "chains_polypeptides": chains_audit,
                "structure_stats": stats_audit,
                "authors_design": authors_audit
            },
            "summary": {
                "total_issues": sum([
                    1 if chains_audit["risk_level"] != "none" else 0,
                    1 if stats_audit["risk_level"] != "none" else 0,
                    1 if authors_audit["risk_level"] != "none" else 0
                ]),
                "low_risk": sum([
                    1 if chains_audit["risk_level"] == "low" else 0,
                    1 if stats_audit["risk_level"] == "low" else 0,
                    1 if authors_audit["risk_level"] == "low" else 0
                ]),
                "medium_risk": sum([
                    1 if chains_audit["risk_level"] == "medium" else 0,
                    1 if stats_audit["risk_level"] == "medium" else 0,
                    1 if authors_audit["risk_level"] == "medium" else 0
                ])
            }
        }
        
        # Write report
        report_file = AUDITS_DIR / "schema_code_consistency_audit.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Also write markdown summary
        md_file = AUDITS_DIR / "schema_code_consistency_audit.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# Schema vs Code Consistency Audit\n\n")
            f.write(f"**Date**: {report['audit_date']}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Total issues: {report['summary']['total_issues']}\n")
            f.write(f"- Low risk: {report['summary']['low_risk']}\n")
            f.write(f"- Medium risk: {report['summary']['medium_risk']}\n\n")
            
            f.write("## chains vs polypeptides\n\n")
            f.write(f"- Schema has 'chains': {chains_audit['schema_has_chains']}\n")
            f.write(f"- Schema has 'polypeptides': {chains_audit['schema_has_polypeptides']}\n")
            f.write(f"- Code references: {chains_audit.get('chains_query_count', 0)}\n")
            f.write(f"- Recommendation: {chains_audit['recommendation']}\n")
            f.write(f"- Risk: {chains_audit['risk_level']}\n\n")
            
            f.write("## structure_stats\n\n")
            f.write(f"- Schema has table: {stats_audit['schema_has_structure_stats']}\n")
            f.write(f"- Code references: {stats_audit.get('structure_stats_query_count', 0)}\n")
            f.write(f"- Recommendation: {stats_audit['recommendation']}\n\n")
            
            f.write("## authors design\n\n")
            f.write(f"- Schema has authors table: {authors_audit['schema_has_authors_table']}\n")
            f.write(f"- Code references: {authors_audit.get('authors_query_count', 0)}\n")
            f.write(f"- Recommendation: {authors_audit['recommendation']}\n")
        
        result = {
            "handler": "audit_table_references",
            "status": "success",
            "message": f"Audit complete: {report['summary']['total_issues']} issues found",
            "report_file": str(report_file),
            "markdown_summary": str(md_file),
            "audits": report["audits"]
        }
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            "handler": "audit_table_references",
            "status": "failed",
            "error": str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
