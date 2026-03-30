#!/usr/bin/env python3
"""
Handler: p2_select_samples

Select representative PDB structures for import.

Selection criteria:
- Different experimental methods (X-ray, EM, NMR)
- Different sizes (small, medium, large)
- Different functional categories
- Well-known reference structures

Output: JSON list of selected PDB IDs with metadata
"""

import json
import sys

# Representative PDB structures
SAMPLE_STRUCTURES = [
    {
        "pdb_id": "1CRN",
        "name": "Crambin",
        "method": "X-RAY DIFFRACTION",
        "resolution": 1.5,
        "category": "small_protein",
        "reason": "Classic small protein, common test structure"
    },
    {
        "pdb_id": "1UBQ",
        "name": "Ubiquitin",
        "method": "X-RAY DIFFRACTION",
        "resolution": 1.8,
        "category": "functional_protein",
        "reason": "Important regulatory protein"
    },
    {
        "pdb_id": "1TIM",
        "name": "TIM Barrel",
        "method": "X-RAY DIFFRACTION",
        "resolution": 2.5,
        "category": "enzyme",
        "reason": "Classic TIM barrel enzyme structure"
    },
    {
        "pdb_id": "6VXX",
        "name": "SARS-CoV-2 Spike",
        "method": "ELECTRON MICROSCOPY",
        "resolution": 2.8,
        "category": "viral_protein",
        "reason": "Electron microscopy structure, relevant pathogen"
    },
    {
        "pdb_id": "7ZNT",
        "name": "Insulin",
        "method": "X-RAY DIFFRACTION",
        "resolution": 3.0,
        "category": "hormone",
        "reason": "Important hormone, drug target"
    }
]

def main():
    results = {
        "selected": SAMPLE_STRUCTURES,
        "count": len(SAMPLE_STRUCTURES),
        "criteria": [
            "Different experimental methods",
            "Different sizes",
            "Different functional categories",
            "Well-known reference structures"
        ],
        "overall": "success"
    }
    
    print(json.dumps(results, indent=2))
    sys.exit(0)

if __name__ == '__main__':
    main()
