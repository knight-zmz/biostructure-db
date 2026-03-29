#!/bin/bash
# 数据库初始化脚本
# 支持重复执行（幂等）

set -e

# 从环境变量读取配置
DB_HOST=${DB_HOST:-127.0.0.1}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-myapp}
DB_USER=${DB_USER:-myapp_user}
DB_PASSWORD=${DB_PASSWORD:-MyApp@2026}

export PGPASSWORD=$DB_PASSWORD

echo "=== 数据库初始化 ==="
echo "主机：${DB_HOST}:${DB_PORT}"
echo "数据库：${DB_NAME}"
echo "用户：${DB_USER}"

# 检查数据库连接
echo "[1/3] 检查数据库连接..."
if ! psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT 1" > /dev/null 2>&1; then
    echo "❌ 数据库连接失败"
    exit 1
fi
echo "✅ 数据库连接成功"

# 检查表是否已存在
echo "[2/3] 检查现有表..."
TABLE_COUNT=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")
echo "当前表数量：${TABLE_COUNT}"

# 执行 schema (支持重复执行)
echo "[3/3] 执行 schema.sql..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEMA_FILE="${SCRIPT_DIR}/../src/db/schema.sql"
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ 找不到 schema 文件：$SCHEMA_FILE"
    exit 1
fi
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$SCHEMA_FILE"

# 验证
echo ""
echo "=== 初始化完成 ==="
TABLE_COUNT=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")
echo "最终表数量：${TABLE_COUNT}"
echo ""
echo "验证命令:"
echo "  psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -c '\\dt'"
