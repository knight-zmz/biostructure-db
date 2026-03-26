#!/bin/bash
# GitHub 自动同步脚本
# 定期自动推送更新到 GitHub

set -e

echo "🦞 BioStructure DB - GitHub 自动同步"
echo "======================================"
echo ""

cd /var/www/myapp

# 检查 Git 配置
if ! git config user.name > /dev/null 2>&1; then
    echo "⚠️  Git 用户未配置，正在配置..."
    git config --global user.name "OpenClaw Bio"
    git config --global user.email "bio@openclaw.local"
fi

# 检查更改
echo "📋 检查更改..."
git status --short

if [ -z "$(git status --short)" ]; then
    echo "✅ 没有更改，跳过推送"
else
    echo ""
    echo "📝 发现更改，准备推送..."
    
    # 添加所有更改
    git add -A
    
    # 提交
    git commit -m "🤖 Auto-sync: $(date '+%Y-%m-%d %H:%M')"
    
    # 推送到 GitHub (尝试 3 次)
    for i in 1 2 3; do
        echo ""
        echo "🔄 推送尝试 $i/3..."
        if git push origin main; then
            echo "✅ 推送成功！"
            break
        else
            echo "⚠️ 推送失败，等待 10 秒后重试..."
            sleep 10
        fi
    done
fi

echo ""
echo "======================================"
echo "同步完成！"
echo ""
echo "GitHub: https://github.com/knight-zmz/biostructure-db"
