#!/bin/bash
# PostgreSQL pg_hba.conf 配置脚本
# 配置 md5 认证以允许密码登录
# 需要 sudo 权限

set -e

PG_HBA="/var/lib/pgsql/data/pg_hba.conf"

echo "=== PostgreSQL pg_hba.conf 配置 ==="

# 检查文件是否存在
if [ ! -f "$PG_HBA" ]; then
    echo "❌ pg_hba.conf 不存在：$PG_HBA"
    exit 1
fi

# 备份原文件
BACKUP="${PG_HBA}.bak.$(date +%Y%m%d_%H%M%S)"
sudo cp "$PG_HBA" "$BACKUP"
echo "✅ 已备份：$BACKUP"

# 修改 local 连接为 md5
sudo sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' "$PG_HBA"

# 修改 host 连接为 md5
sudo sed -i 's/host    all             all             127.0.0.1\/32            ident/host    all             all             127.0.0.1\/32            md5/' "$PG_HBA"
sudo sed -i 's/host    all             all             ::1\/128                 ident/host    all             all             ::1\/128                 md5/' "$PG_HBA"

echo "✅ pg_hba.conf 已更新"

# 重启 PostgreSQL
echo "🔄 重启 PostgreSQL..."
sudo systemctl restart postgresql

# 验证
sleep 2
if sudo systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL 重启成功"
else
    echo "❌ PostgreSQL 重启失败，恢复备份..."
    sudo cp "$BACKUP" "$PG_HBA"
    sudo systemctl restart postgresql
    exit 1
fi

echo ""
echo "=== 配置完成 ==="
echo "验证命令:"
echo "  psql -U myapp_user -h 127.0.0.1 -d myapp -c 'SELECT 1'"
