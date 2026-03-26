#!/bin/bash
# 一键发布到 GitHub

echo "🧬 BioStructure DB - GitHub 发布助手"
echo "======================================"
echo ""

# 检查
echo "📋 系统检查..."

# 检查 Git
if ! command -v git &> /dev/null; then
    echo "❌ Git 未安装"
    echo "安装：yum install git -y"
    exit 1
fi
echo "✅ Git: $(git --version)"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi
echo "✅ Node.js: $(node -v)"

# 检查 PM2
if ! command -v pm2 &> /dev/null; then
    echo "⚠️  PM2 未安装 (可选)"
else
    echo "✅ PM2: $(pm2 -v)"
fi

echo ""
echo "📦 项目文件:"
echo "  - app.js: $(test -f app.js && echo '✅' || echo '❌')"
echo "  - bioapi.js: $(test -f bioapi.js && echo '✅' || echo '❌')"
echo "  - pdb-parser.js: $(test -f pdb-parser.js && echo '✅' || echo '❌')"
echo "  - mcp-server.js: $(test -f mcp-server.js && echo '✅' || echo '❌')"
echo "  - public/index.html: $(test -f public/index.html && echo '✅' || echo '❌')"
echo "  - .github/workflows/: $(test -d .github/workflows && echo '✅' || echo '❌')"

echo ""
echo "======================================"
echo "✅ 所有文件已准备就绪！"
echo ""
echo "下一步："
echo ""
echo "1️⃣ 运行 Git 初始化脚本:"
echo "   ./scripts/git-setup.sh <你的 GitHub 用户名>"
echo ""
echo "2️⃣ 在 GitHub 创建仓库:"
echo "   https://github.com/new"
echo "   仓库名：biostructure-db"
echo ""
echo "3️⃣ 推送代码:"
echo "   git remote add origin https://github.com/<用户名>/biostructure-db.git"
echo "   git push -u origin main"
echo ""
echo "4️⃣ 查看完整指南:"
echo "   cat PUBLISH.md"
echo ""
echo "======================================"
