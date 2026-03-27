#!/bin/bash
# 数据库维护脚本 - 定期运行
echo "=== BioStructure DB 维护 ==="
echo "时间: $(date)"

# 1. 更新统计信息
psql -U myapp_user -d myapp -c "ANALYZE;" 2>/dev/null
echo "统计信息已更新"

# 2. 清理死元组
sudo -u postgres vacuumdb -d myapp -z 2>/dev/null
echo "VACUUM ANALYZE 完成"

# 3. 检查表大小
echo ""
echo "=== 数据库大小 ==="
psql -U myapp_user -d myapp -c "SELECT tablename, pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS size FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size('public.'||tablename) DESC LIMIT 10;" 2>/dev/null

echo ""
echo "维护完成: $(date)"
