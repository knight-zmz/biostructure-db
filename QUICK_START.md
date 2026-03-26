# 🚀 快速开始 - 发布到 GitHub

---

## ⚡ 3 分钟快速配置

### 步骤 1: 配置 Git 凭证 (选择一种方式)

**方式 A: SSH 密钥 (推荐，最安全)**
```bash
cd /var/www/myapp
./scripts/configure-git-auth.sh
# 选择选项 2 (SSH Key)
```

**方式 B: HTTPS + Token**
```bash
./scripts/configure-git-auth.sh
# 选择选项 1 (HTTPS + Token)
# 按提示配置 Fine-grained Token
```

---

### 步骤 2: 初始化 Git 仓库

```bash
./scripts/git-setup.sh <你的 GitHub 用户名>
# 例如：./scripts/git-setup.sh octocat
```

---

### 步骤 3: 在 GitHub 创建仓库

1. 访问：https://github.com/new
2. 仓库名：**biostructure-db**
3. 描述：Professional BioStructure Database
4. ✅ **Public** (开源)
5. 点击 "Create repository"

---

### 步骤 4: 推送代码

```bash
# 添加远程仓库 (替换 <your-username>)
git remote add origin https://github.com/<your-username>/biostructure-db.git

# 推送代码
git push -u origin main
```

---

### 步骤 5: 启用 GitHub Actions

1. 访问：https://github.com/<your-username>/biostructure-db/actions
2. 点击 "I understand my workflows, go ahead and enable them"

**完成！🎉** 现在每次 push 都会自动构建和测试。

---

## 🔐 安全配置 (重要)

### 创建 Fine-grained Token

**访问**: https://github.com/settings/tokens

**配置**:
```
Token type: Fine-grained
Repository access: Only 'biostructure-db'

Permissions:
  ✅ Contents: Read and write
  ✅ Actions: Read and write
  ✅ Metadata: Read only
  ❌ 其他所有：None
```

**有效期**: 90 天

---

## 📦 自动部署到服务器 (可选)

### 1. 生成 SSH 密钥

```bash
ssh-keygen -t ed25519 -C "github-actions"
```

### 2. 添加公钥到服务器

```bash
# 复制公钥
cat ~/.ssh/id_ed25519.pub

# 添加到服务器 authorized_keys
ssh admin@<服务器 IP> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
# 粘贴公钥
```

### 3. 在 GitHub 添加 Secrets

访问：https://github.com/<user>/biostructure-db/settings/secrets/actions/new

| Secret | Value |
|--------|-------|
| `DEPLOY_SSH_KEY` | SSH 私钥内容 |
| `DEPLOY_HOST` | 服务器 IP |
| `DEPLOY_USER` | `admin` |

---

## 📊 验证

### 检查 Actions 状态

```
https://github.com/<user>/biostructure-db/actions
```

应该看到:
- ✅ test.yml - 运行测试
- ✅ deploy.yml - 构建打包
- ✅ release.yml - (推送标签时触发)

### 查看部署日志

```
Actions > 选择运行 > 查看具体步骤
```

---

## 🔄 日常使用

### 推送代码

```bash
git add .
git commit -m "feat: 添加新功能"
git push
```

### 发布新版本

```bash
# 更新版本号 (package.json)
vim package.json

# 提交并打标签
git add package.json
git commit -m "📦 Release v1.1.0"
git tag v1.1.0
git push origin v1.1.0
```

### 查看构建状态

```
https://github.com/<user>/biostructure-db/actions
```

---

## 📚 完整文档

| 文档 | 说明 |
|------|------|
| `GITHUB_GUIDE.md` | GitHub 完整指南 |
| `PUBLISH.md` | 发布详细步骤 |
| `.github/SECURITY.md` | 安全配置 |
| `README.md` | 项目说明 |

---

## ❓ 常见问题

### Q: 推送时提示认证失败？
A: 检查 Token 是否正确配置，或改用 SSH

### Q: Actions 不运行？
A: 检查是否启用了 Actions (Settings > Actions)

### Q: 如何跳过 CI？
A: commit message 添加 `[skip ci]`

### Q: Token 过期了怎么办？
A: 重新生成 Token，更新凭证

---

## 🔗 有用的链接

- **GitHub 仓库**: https://github.com/<user>/biostructure-db
- **Actions**: https://github.com/<user>/biostructure-db/actions
- **Settings**: https://github.com/<user>/biostructure-db/settings
- **Tokens**: https://github.com/settings/tokens

---

**祝你发布顺利！有任何问题随时问。🦞**
