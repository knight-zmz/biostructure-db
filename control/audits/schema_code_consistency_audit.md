# Schema vs Code Consistency Audit

**Date**: 2026-03-30T22:26:02.722463

## Summary

- Total issues: 3
- Low risk: 1
- Medium risk: 2

## chains vs polypeptides

- Schema has 'chains': False
- Schema has 'polypeptides': True
- Code references: 3
- Recommendation: Replace 'chains' with 'polypeptides' in app.js queries
- Risk: low

## structure_stats

- Schema has table: False
- Code references: 5
- Recommendation: Either: (A) Add structure_stats table to schema, or (B) Remove legacy code from app.js

## authors design

- Schema has authors table: False
- Code references: 1
- Recommendation: Code expects separate authors table, but schema uses structures.authors TEXT[]
