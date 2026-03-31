# Project State

**Updated**: 2026-03-31  
**Project**: biostructure-db  
**Phase**: Control Plane v1.3 — Task Supply + Summary Layer  

---

## 1. Current Phase

Control plane v1.3 operational. Task auto-supply verified end-to-end.  
Summary/report layer active. Status query protocol established.

**Next major milestone**: Test timer operational, evaluating sustained autonomous operation  
(test timer enabled: every 20 min, 2026-03-31 20:29; prod timer paused by design)

---

## 2. Completed Milestones

| Milestone | Status |
|---|---|
| PostgreSQL + Redis + PM2 | ✅ Verified |
| GitHub Actions deploy pipeline | ✅ Verified (2x) |
| Nginx reverse proxy (HTTP 80→3000) | ✅ Verified |
| Environment config (no hardcoded secrets) | ✅ Verified |
| Control plane v1.3 (queue + summary + protocol) | ✅ Verified |
| Task auto-supply (generate → execute → drain → regenerate) | ✅ Verified |
| Database backup script + cron | ✅ Verified (daily 2am, backup exists, log shows success) |
| Monitoring script + cron | ✅ Verified (10-min采集，告警触发正常， outage detected 23:50-06:00) |

---

## 3. Blockers

**None active.**

**Known pause**:
- HTTPS: blocked by ICP filing. HTTP-only until filing completes.

---

## 4. Active Risks

| Risk | Level |
|---|---|
| Backup cron | ✅ Verified (daily 2am execution confirmed) |
| Monitoring cron | ✅ Verified (alert system functional) |
| Node.js 20 deprecation (2026-04-30 EOL) | 🟢 Low |
| Test timer evaluation | 🟡 In progress (20min interval, monitoring stability) |

---

## 5. Next Priorities

### P1 — Verification
1. ✅ Backup cron verified (daily 2am execution confirmed)
2. ✅ Monitoring cron verified (alert system functional)

### P2 — Content & Data
3. Sample data import / data source preparation
4. API endpoint and page content completion

### P3 — Maintenance
5. Node.js 20 → 22 upgrade (before 2026-04-30)

---

## 6. Access

- **URL**: http://101.200.53.98 (IP direct)
- **Domain**: jlupdb.me (paused, ICP filing)
- **Dev path**: `/home/admin/biostructure-db`
- **Prod path**: `/var/www/myapp`
