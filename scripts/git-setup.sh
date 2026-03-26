#!/bin/bash
# Git 初始化与自动部署脚本
# 使用方法：./scripts/git-setup.sh <your-github-username>

set -e

GITHUB_USER="${1:-}"
REPO_NAME="biostructure-db"

echo "🧬 BioStructure DB - Git 初始化脚本"
echo "===================================="

if [ -z "$GITHUB_USER" ]; then
    echo "用法：$0 <your-github-username>"
    echo "例如：$0 octocat"
    exit 1
fi

echo "GitHub 用户：$GITHUB_USER"
echo "仓库名称：$REPO_NAME"
echo ""

# 检查 Git 是否安装
if ! command -v git &> /dev/null; then
    echo "❌ Git 未安装，请先安装 Git"
    exit 1
fi

# 初始化 Git 仓库
echo "📦 初始化 Git 仓库..."
git init -b main

# 创建 .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
package-lock.json

# Environment
.env
.env.local
.env.*.local

# Logs
logs/
*.log
npm-debug.log*

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# Coverage
coverage/
.nyc_output/

# Build
dist/
build/
*.tar.gz

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite

# Secrets
*.pem
*.key
EOF

echo "✅ 创建 .gitignore"

# 添加所有文件
git add .
echo "✅ 添加文件到 Git"

# 首次提交
git commit -m "🎉 Initial commit: BioStructure DB v1.0.0

Features:
- PostgreSQL database (15 tables)
- RESTful API (20+ endpoints)
- MCP Server for AI access
- 3D molecular visualization
- OpenClaw skills
- GitHub Actions CI/CD

Reference: PDB + UniProt + Pfam + PubChem"

echo "✅ 首次提交完成"
echo ""

# 创建 GitHub 仓库的说明
echo "===================================="
echo "下一步操作："
echo ""
echo "1️⃣ 在 GitHub 创建新仓库:"
echo "   访问：https://github.com/new"
echo "   仓库名：$REPO_NAME"
echo "   描述：Professional BioStructure Database (PDB + UniProt + Pfam)"
echo "   ✅ Public (开源)"
echo "   ✅ Add README (可选)"
echo ""
echo "2️⃣ 添加远程仓库:"
echo "   git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git"
echo ""
echo "3️⃣ 推送代码:"
echo "   git push -u origin main"
echo ""
echo "4️⃣ 启用 GitHub Actions:"
echo "   访问：https://github.com/$GITHUB_USER/$REPO_NAME/actions"
echo "   点击 'I understand my workflows, go ahead and enable them'"
echo ""
echo "5️⃣ (可选) 配置自动部署到服务器:"
echo "   在 Settings > Secrets and variables > Actions 添加:"
echo "   - DEPLOY_SSH_KEY: SSH 私钥"
echo "   - DEPLOY_HOST: 服务器 IP"
echo "   - DEPLOY_USER: 服务器用户"
echo ""
echo "===================================="
echo ""
echo "💡 提示：现在可以执行步骤 2-3 推送代码到 GitHub"
