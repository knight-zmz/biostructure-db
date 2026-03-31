# Database Operations — 数据库操作

## 初始化

```bash
sudo -u postgres psql
CREATE USER myapp_user WITH PASSWORD 'MyApp@2026';
CREATE DATABASE myapp OWNER myapp_user;
GRANT ALL PRIVILEGES ON DATABASE myapp TO myapp_user;
\q

psql -U myapp_user -d myapp -f /home/admin/biostructure-db/src/db/schema.sql
```

## 日常维护

```bash
# 查看表大小
psql -U myapp_user -d myapp -c "
SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename)) 
FROM pg_tables WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(tablename) DESC;"

# 清理
psql -U myapp_user -d myapp -c "VACUUM ANALYZE;"

# 重建索引
psql -U myapp_user -d myapp -c "REINDEX DATABASE myapp;"
```
