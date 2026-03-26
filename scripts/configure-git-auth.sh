#!/bin/bash
# 安全配置 Git 凭证脚本

echo "🔐 Git 凭证安全配置"
echo "===================="
echo ""

# 检查
if ! command -v git &> /dev/null; then
    echo "❌ Git 未安装"
    exit 1
fi

# 配置 Git 用户信息
echo "📝 配置 Git 用户信息"
echo ""

read -p "请输入你的 GitHub 用户名：" GITHUB_USER
read -p "请输入你的邮箱：" GIT_EMAIL

git config --global user.name "$GITHUB_USER"
git config --global user.email "$GIT_EMAIL"

echo "✅ Git 用户信息已配置"
echo "   用户：$GITHUB_USER"
echo "   邮箱：$GIT_EMAIL"
echo ""

# 选择认证方式
echo "🔑 选择认证方式:"
echo ""
echo "1️⃣  HTTPS + Personal Access Token (推荐新手)"
echo "2️⃣  SSH Key (推荐，更安全)"
echo "3️⃣  Git Credential Manager (最简单)"
echo ""

read -p "请选择 (1/2/3): " AUTH_METHOD

case $AUTH_METHOD in
    1)
        echo ""
        echo "📋 HTTPS + Token 配置步骤:"
        echo ""
        echo "1. 访问：https://github.com/settings/tokens"
        echo "2. 选择 'Fine-grained tokens'"
        echo "3. 点击 'Generate new token'"
        echo "4. 配置:"
        echo "   - Repository access: Only 'biostructure-db'"
        echo "   - Permissions: Contents (R/W), Actions (R/W)"
        echo "   - Expiration: 90 days"
        echo "5. 复制生成的 Token"
        echo ""
        echo "6. 配置凭证存储:"
        git config --global credential.helper store
        echo "   ✅ 已启用凭证存储"
        echo ""
        echo "7. 下次 push 时输入:"
        echo "   Username: $GITHUB_USER"
        echo "   Password: <粘贴你的 Token>"
        echo ""
        ;;
    
    2)
        echo ""
        echo "🔑 SSH Key 配置步骤:"
        echo ""
        echo "1. 生成 SSH 密钥:"
        read -p "   现在生成？(y/n): " GENERATE_SSH
        
        if [ "$GENERATE_SSH" = "y" ]; then
            ssh-keygen -t ed25519 -C "$GIT_EMAIL"
            echo ""
            echo "2. 查看公钥内容:"
            cat ~/.ssh/id_ed25519.pub
            echo ""
            echo "3. 复制上面的公钥，访问:"
            echo "   https://github.com/settings/keys"
            echo "   点击 'New SSH key'"
            echo "   粘贴公钥内容"
            echo ""
            
            echo "4. 测试 SSH 连接:"
            read -p "   现在测试？(y/n): " TEST_SSH
            
            if [ "$TEST_SSH" = "y" ]; then
                ssh -T git@github.com
            fi
        fi
        echo ""
        ;;
    
    3)
        echo ""
        echo "📦 Git Credential Manager 配置:"
        echo ""
        echo "1. 安装 GCM:"
        echo "   访问：https://github.com/GitCredentialManager/git-credential-manager"
        echo ""
        echo "2. 配置:"
        git config --global credential.helper /usr/bin/git-credential-manager
        echo "   ✅ 已配置 GCM"
        echo ""
        echo "3. 下次 push 时会自动弹出登录窗口"
        echo ""
        ;;
    
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

# 验证配置
echo ""
echo "===================="
echo "✅ 配置完成！"
echo ""
echo "验证配置:"
echo "  git config --global user.name"
echo "  git config --global user.email"
echo "  git config --global credential.helper"
echo ""
echo "下一步:"
echo "  1. 在 GitHub 创建仓库：https://github.com/new"
echo "  2. 运行：./scripts/git-setup.sh $GITHUB_USER"
echo "  3. 推送代码到 GitHub"
echo ""
