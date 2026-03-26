#!/bin/bash
# 自动检查和修复脚本
# 每小时运行一次，持续改进

set -e

echo "🦞 BioStructure DB - 自动检查和修复"
echo "======================================"
echo ""
echo "时间：$(date)"
echo ""

# 1. 检查服务状态
echo "1️⃣ 检查服务状态..."
echo ""

# Nginx
if systemctl is-active --quiet nginx; then
    echo "  ✅ Nginx: Running"
else
    echo "  ❌ Nginx: Stopped - 正在重启..."
    sudo systemctl start nginx
fi

# PostgreSQL
if systemctl is-active --quiet postgresql; then
    echo "  ✅ PostgreSQL: Running"
else
    echo "  ❌ PostgreSQL: Stopped - 正在重启..."
    sudo systemctl start postgresql
fi

# PM2
if pm2 status myapp | grep -q "online"; then
    echo "  ✅ PM2 (myapp): Running"
else
    echo "  ❌ PM2 (myapp): Stopped - 正在重启..."
    pm2 start app.js --name myapp
fi

echo ""

# 2. 检查数据库连接
echo "2️⃣ 检查数据库连接..."
if sudo -u postgres psql -d myapp -c "SELECT 1" &>/dev/null; then
    echo "  ✅ 数据库连接：正常"
else
    echo "  ❌ 数据库连接：失败 - 正在修复..."
    sudo systemctl restart postgresql
fi

# 3. 检查 API
echo ""
echo "3️⃣ 检查 API 可用性..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/stats)
if [ "$response" = "200" ]; then
    echo "  ✅ API: 正常 (HTTP $response)"
else
    echo "  ❌ API: 异常 (HTTP $response) - 正在重启..."
    pm2 restart myapp
fi

# 4. 检查磁盘空间
echo ""
echo "4️⃣ 检查磁盘空间..."
disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    echo "  ✅ 磁盘使用：${disk_usage}%"
else
    echo "  ⚠️ 磁盘使用：${disk_usage}% - 需要清理"
fi

# 5. 检查内存
echo ""
echo "5️⃣ 检查内存使用..."
mem_usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ "$mem_usage" -lt 80 ]; then
    echo "  ✅ 内存使用：${mem_usage}%"
else
    echo "  ⚠️ 内存使用：${mem_usage}% - 需要优化"
fi

# 6. GitHub 同步 (如果网络允许)
echo ""
echo "6️⃣ GitHub 同步..."
cd /var/www/myapp
if git status --short &>/dev/null; then
    changes=$(git status --short | wc -l)
    if [ "$changes" -gt 0 ]; then
        echo "  ⚠️ 发现 $changes 个更改 - 准备推送..."
        git add -A
        git commit -m "🤖 Auto-sync: $(date '+%Y-%m-%d %H:%M')"
        
        for i in 1 2 3; do
            echo "  尝试推送 $i/3..."
            if git push origin main 2>/dev/null; then
                echo "  ✅ 推送成功"
                break
            else
                echo "  ⚠️ 推送失败，等待 10 秒..."
                sleep 10
            fi
        done
    else
        echo "  ✅ 没有更改"
    fi
else
    echo "  ⚠️ Git 仓库异常"
fi

# 7. 备份数据库
echo ""
echo "7️⃣ 数据库备份..."
backup_dir="/var/backups/myapp"
mkdir -p "$backup_dir"
backup_file="$backup_dir/backup-$(date +%Y%m%d-%H%M%S).sql"
if sudo -u postgres pg_dump myapp > "$backup_file" 2>/dev/null; then
    echo "  ✅ 备份完成：$backup_file"
    # 保留最近 7 天的备份
    find "$backup_dir" -name "*.sql" -mtime +7 -delete
    echo "  ✅ 清理旧备份 (保留 7 天)"
else
    echo "  ❌ 备份失败"
fi

# 8. 清理日志
echo ""
echo "8️⃣ 清理日志..."
sudo find /var/log/nginx -name "*.log" -size +100M -exec truncate -s 0 {} \;
echo "  ✅ 日志清理完成"

# 9. 生成报告
echo ""
echo "9️⃣ 生成健康报告..."
curl -s http://localhost/api/bio/stats/detailed | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'  📊 结构总数：{d[\"data\"][\"totalStructures\"]}')
print(f'  🔬 实验方法：{len(d[\"data\"][\"methods\"])} 种')
" 2>/dev/null || echo "  ⚠️ 无法获取统计"

echo ""
echo "======================================"
echo "✅ 自动检查完成！"
echo ""
echo "下次检查：1 小时后"
echo ""

# 记录日志
echo "$(date): 自动检查完成" >> /var/log/biostructure-check.log
