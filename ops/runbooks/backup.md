# Backup — 数据库备份与恢复

## 自动备份

**脚本**: `scripts/backup-db.sh`  
**频率**: 每日 02:00  
**保留**: 7 天  
**位置**: `/home/admin/backups/`

```bash
crontab -l  # 查看 cron
```

## 手动备份

```bash
bash /home/admin/biostructure-db/scripts/backup-db.sh

# 或直接
PGPASSWORD="MyApp@2026" pg_dump -h 127.0.0.1 -U myapp_user myapp | gzip > backup_$(date +%Y%m%d).sql.gz
```

## 恢复

```bash
pm2 stop myapp
gunzip -c /home/admin/backups/myapp_20260330.sql.gz > restore.sql
psql -h 127.0.0.1 -U myapp_user -d myapp -f restore.sql
pm2 start myapp
curl http://localhost:3000/api/health
```

## 管理

```bash
ls -lh /home/admin/backups/
tail -20 /home/admin/backups/backup.log
find /home/admin/backups -name "myapp_*.sql.gz" -mtime +7 -delete
```
