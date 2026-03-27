#!/bin/bash
# 服务健康检查
echo "=== BioStructure DB 健康检查 ==="
echo "时间: $(date)"

# PM2 状态
echo ""
echo "PM2 状态:"
pm2 jlist 2>/dev/null | python3 -c "import sys,json; apps=json.load(sys.stdin); [print(f'  {a[\"name\"]}: {a[\"pm2_env\"][\"status\"]} (uptime: {a[\"pm2_env\"][\"pm_uptime\"]}, restarts: {a[\"pm2_env\"][\"restart_time\"]})') for a in apps]" 2>/dev/null

# API 检查
echo ""
echo "API 端点检查:"
for endpoint in "/" "/api/stats" "/api/structures" "/api/bio/health"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000${endpoint}" 2>/dev/null)
  echo "  ${endpoint}: ${code}"
done

# 数据库检查
echo ""
echo "数据库状态:"
psql -U myapp_user -d myapp -c "SELECT 'structures' as tbl, COUNT(*) as cnt FROM structures UNION ALL SELECT 'atoms', COUNT(*) FROM atoms UNION ALL SELECT 'residues', COUNT(*) FROM residues;" 2>/dev/null

# 域名检查
echo ""
echo "域名状态:"
code=$(curl -s -o /dev/null -w "%{http_code}" https://jlupdb.me/ 2>/dev/null)
echo "  https://jlupdb.me/: ${code}"

echo ""
echo "检查完成"
