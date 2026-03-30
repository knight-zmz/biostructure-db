#!/bin/bash
#
# 基础监控脚本 - 记录系统指标
# 用途：采集关键指标并记录到日志文件，用于趋势分析和告警
# 用法：bash scripts/monitor.sh
#

set -e

# 配置
LOG_DIR="/home/admin/logs"
METRICS_LOG="${LOG_DIR}/metrics.log"
ALERT_LOG="${LOG_DIR}/alerts.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 创建日志目录
mkdir -p "$LOG_DIR"

# 采集指标
echo "=== 监控指标采集 ===" 

# 1. 系统负载
LOAD_1=$(cat /proc/loadavg | awk '{print $1}')
LOAD_5=$(cat /proc/loadavg | awk '{print $2}')
LOAD_15=$(cat /proc/loadavg | awk '{print $3}')

# 2. 内存使用
MEM_TOTAL=$(free -m | grep Mem | awk '{print $2}')
MEM_USED=$(free -m | grep Mem | awk '{print $3}')
MEM_PERCENT=$(awk "BEGIN {printf \"%.1f\", ($MEM_USED/$MEM_TOTAL)*100}")

# 3. 磁盘使用
DISK_TOTAL=$(df -m / 2>/dev/null | tail -1 | awk '{print $2}')
DISK_USED=$(df -m / 2>/dev/null | tail -1 | awk '{print $3}')
DISK_PERCENT=$(df / 2>/dev/null | tail -1 | awk '{print $5}' | tr -d '%')

# 4. 服务状态
NGINX_STATUS=$(systemctl is-active nginx 2>/dev/null || echo "inactive")
POSTGRES_STATUS=$(systemctl is-active postgresql 2>/dev/null || echo "inactive")
PM2_STATUS=$(pm2 status myapp 2>/dev/null | grep -q "online" && echo "online" || echo "offline")

# 5. API 健康
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health 2>/dev/null || echo "000")

# 6. 数据库连接
DB_STATUS=$(PGPASSWORD="MyApp@2026" psql -h 127.0.0.1 -U myapp_user -d myapp -c "SELECT 1" &>/dev/null && echo "connected" || echo "disconnected")

# 记录指标
METRIC_LINE="${TIMESTAMP} | load:${LOAD_1} | mem:${MEM_PERCENT}% | disk:${DISK_PERCENT}% | nginx:${NGINX_STATUS} | pg:${POSTGRES_STATUS} | pm2:${PM2_STATUS} | api:${API_STATUS} | db:${DB_STATUS}"
echo "$METRIC_LINE" >> "$METRICS_LOG"

echo "✅ 指标已记录：${METRIC_LINE}"

# 告警检查
ALERTS=()

# CPU 负载告警（1 分钟负载 > 4）
if (( $(echo "$LOAD_1 > 4" | bc -l) )); then
    ALERTS+=("⚠️  高负载：${LOAD_1}")
fi

# 内存告警（> 85%）
MEM_PERCENT_INT=${MEM_PERCENT%.*}
if [ "$MEM_PERCENT_INT" -gt 85 ]; then
    ALERTS+=("⚠️  高内存：${MEM_PERCENT}%")
fi

# 磁盘告警（> 90%）
if [ "$DISK_PERCENT" -gt 90 ]; then
    ALERTS+=("⚠️  高磁盘：${DISK_PERCENT}%")
fi

# 服务告警
[ "$NGINX_STATUS" != "active" ] && ALERTS+=("❌ Nginx 已停止")
[ "$POSTGRES_STATUS" != "active" ] && ALERTS+=("❌ PostgreSQL 已停止")
[ "$PM2_STATUS" != "online" ] && ALERTS+=("❌ PM2 应用离线")
[ "$API_STATUS" != "200" ] && ALERTS+=("❌ API 异常：${API_STATUS}")
[ "$DB_STATUS" != "connected" ] && ALERTS+=("❌ 数据库断开")

# 记录告警
if [ ${#ALERTS[@]} -gt 0 ]; then
    echo ""
    echo "🚨 发现告警:"
    for alert in "${ALERTS[@]}"; do
        echo "  $alert"
        echo "${TIMESTAMP} | $alert" >> "$ALERT_LOG"
    done
else
    echo "✅ 无告警"
fi

echo ""
echo "=== 监控完成 ==="
