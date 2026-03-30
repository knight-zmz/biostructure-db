#!/bin/bash
#
# 数据库自动备份脚本
# 用途：备份 PostgreSQL 数据库到本地，保留最近 7 天
# 用法：bash scripts/backup-db.sh
#

set -e

# 配置
DB_NAME="myapp"
DB_USER="myapp_user"
DB_HOST="127.0.0.1"
BACKUP_DIR="/home/admin/backups"
RETENTION_DAYS=7
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${DATE}.sql.gz"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

echo "=== 数据库备份开始 ==="
echo "时间：$(date)"
echo "数据库：${DB_NAME}"
echo "备份文件：${BACKUP_FILE}"

# 执行备份（使用 pg_dump）
PGPASSWORD="MyApp@2026" pg_dump -h "$DB_HOST" -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

# 验证备份文件
if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✅ 备份成功：${BACKUP_SIZE}"
else
    echo "❌ 备份失败：文件为空或不存在"
    exit 1
fi

# 清理旧备份（保留最近 N 天）
echo "清理 ${RETENTION_DAYS} 天前的旧备份..."
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete

# 列出当前备份
echo ""
echo "当前备份列表:"
ls -lh "$BACKUP_DIR"/${DB_NAME}_*.sql.gz 2>/dev/null | tail -10 || echo "无备份文件"

echo ""
echo "=== 数据库备份完成 ==="
