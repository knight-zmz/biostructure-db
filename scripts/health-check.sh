#!/bin/bash
# 系统健康检查脚本

echo "🦞 BioStructure DB - 健康检查"
echo "=============================="
echo ""

# 检查 Nginx
echo -n "Nginx: "
if systemctl is-active --quiet nginx; then
    echo "✅ Running"
else
    echo "❌ Stopped"
    sudo systemctl start nginx
fi

# 检查 PostgreSQL
echo -n "PostgreSQL: "
if systemctl is-active --quiet postgresql; then
    echo "✅ Running"
else
    echo "❌ Stopped"
    sudo systemctl start postgresql
fi

# 检查 PM2
echo -n "PM2 (myapp): "
if pm2 status myapp | grep -q "online"; then
    echo "✅ Running"
else
    echo "❌ Stopped"
    pm2 start app.js --name myapp
fi

# 检查端口
echo ""
echo "端口检查:"
echo -n "  80 (HTTP): "
netstat -tln | grep -q ":80" && echo "✅ 开放" || echo "❌ 未开放"

echo -n "  3000 (Node): "
netstat -tln | grep -q ":3000" && echo "✅ 开放" || echo "❌ 未开放"

echo -n "  5432 (PostgreSQL): "
netstat -tln | grep -q ":5432" && echo "✅ 开放" || echo "❌ 未开放"

# 检查磁盘
echo ""
echo "磁盘使用:"
df -h / | tail -1 | awk '{print "  已用:", $3, "/", "总计:", $2, "(", $5, ")"}'

# 检查内存
echo ""
echo "内存使用:"
free -h | grep Mem | awk '{print "  已用:", $3, "/", "总计:", $2}'

# 测试 API
echo ""
echo "API 测试:"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/stats)
if [ "$response" = "200" ]; then
    echo "  ✅ API 正常 (HTTP $response)"
else
    echo "  ❌ API 异常 (HTTP $response)"
fi

# 检查数据库连接
echo ""
echo "数据库测试:"
if sudo -u postgres psql -d myapp -c "SELECT 1" &>/dev/null; then
    echo "  ✅ 数据库连接正常"
else
    echo "  ❌ 数据库连接失败"
fi

echo ""
echo "=============================="
echo "健康检查完成！"
echo ""
echo "访问地址：http://101.200.53.98/"
echo "GitHub: https://github.com/knight-zmz/biostructure-db"
