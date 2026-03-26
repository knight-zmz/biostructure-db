#!/bin/bash
# 手动安装 GitHub CLI

echo "📦 安装 GitHub CLI..."
echo ""

# 下载最新版本
VERSION="2.40.1"
URL="https://github.com/cli/cli/releases/download/v${VERSION}/gh_${VERSION}_linux_amd64.tar.gz"

echo "下载 GitHub CLI v${VERSION}..."
cd /tmp
wget -q "$URL" -O gh.tar.gz

if [ $? -ne 0 ]; then
    echo "❌ 下载失败"
    exit 1
fi

echo "解压..."
tar xzf gh.tar.gz
mv gh_${VERSION}_linux_amd64 gh-cli

echo "安装到 /usr/local/bin..."
sudo cp -r gh-cli/* /usr/local/
sudo chmod +x /usr/local/bin/gh

# 清理
rm -rf gh.tar.gz gh-cli

echo ""
echo "✅ 安装完成！"
echo ""
gh --version

echo ""
echo "📋 使用示例:"
echo "  gh auth login          # 登录 GitHub"
echo "  gh repo create         # 创建仓库"
echo "  gh repo view           # 查看仓库"
echo "  gh issue list          # 查看 Issues"
