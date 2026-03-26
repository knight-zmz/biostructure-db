# 📦 发布到 GitHub 指南

## 前提条件

- ✅ GitHub 账号
- ✅ Git 已安装
- ✅ 本项目代码在 `/var/www/myapp/`

---

## 🚀 快速发布 (5 步)

### 步骤 1: 运行初始化脚本

```bash
cd /var/www/myapp
chmod +x scripts/git-setup.sh
./scripts/git-setup.sh <你的 GitHub 用户名>
```

例如：
```bash
./scripts/git-setup.sh octocat
```

### 步骤 2: 在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 仓库名：**biostructure-db**
3. 描述：Professional BioStructure Database (PDB + UniProt + Pfam)
4. ✅ 设为 **Public** (开源)
5. 点击 "Create repository"

### 步骤 3: 添加远程仓库并推送

```bash
# 替换 <your-username> 为你的 GitHub 用户名
git remote add origin https://github.com/<your-username>/biostructure-db.git
git push -u origin main
```

### 步骤 4: 启用 GitHub Actions

1. 访问：https://github.com/<your-username>/biostructure-db/actions
2. 点击 "I understand my workflows, go ahead and enable them"

### 步骤 5: 验证

推送后，GitHub Actions 会自动运行：
- ✅ 代码检查
- ✅ 依赖安装
- ✅ 构建打包
- ✅ 创建 artifact

---

## 🔐 配置自动部署 (可选)

如果想实现**推送到 GitHub 后自动部署到服务器**：

### 1. 生成 SSH 密钥

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy"
```

### 2. 添加公钥到服务器

```bash
# 复制公钥内容
cat ~/.ssh/id_ed25519.pub

# 添加到服务器 authorized_keys
ssh admin@<服务器 IP> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
# 粘贴公钥内容
```

### 3. 在 GitHub 添加 Secrets

访问：https://github.com/<your-username>/biostructure-db/settings/secrets/actions/new

添加以下 Secrets：

| Name | Value |
|------|-------|
| `DEPLOY_SSH_KEY` | SSH 私钥内容 (`cat ~/.ssh/id_ed25519`) |
| `DEPLOY_HOST` | 服务器 IP 地址 |
| `DEPLOY_USER` | 服务器用户名 (如 `admin`) |

---

## 📦 发布新版本

### 1. 更新版本号

```bash
# 编辑 package.json，更新 version 字段
vim package.json
```

### 2. 创建 Git 标签

```bash
git add package.json
git commit -m "📦 Release v1.0.1"
git tag v1.0.1
git push origin v1.0.1
```

### 3. 自动发布

推送标签后，GitHub Actions 会：
- ✅ 创建 Release
- ✅ 上传构建包
- ✅ 生成 Changelog

---

## 📊 GitHub Actions 工作流

### 已配置的工作流

| 文件 | 触发条件 | 功能 |
|------|----------|------|
| `test.yml` | Push/PR | 运行测试、代码检查 |
| `deploy.yml` | Push to main | 构建、打包、上传 artifact |
| `release.yml` | Push tag | 创建 GitHub Release |
| `auto-deploy.yml` | Push to main | 自动部署到服务器 |

---

## 🔗 有用的链接

- **仓库主页**: https://github.com/<your-username>/biostructure-db
- **Actions**: https://github.com/<your-username>/biostructure-db/actions
- **Releases**: https://github.com/<your-username>/biostructure-db/releases
- **Settings**: https://github.com/<your-username>/biostructure-db/settings

---

## 💡 提示

1. **开源协议**: 本项目使用 MIT 协议
2. **Badge**: 可以在 README 添加 GitHub Actions 状态徽章
3. **Issues**: 启用 GitHub Issues 收集反馈
4. **Discussions**: 启用 Discussions 进行社区讨论
5. **Wiki**: 启用 Wiki 编写详细文档

---

## ❓ 常见问题

### Q: 推送失败怎么办？
A: 检查远程仓库 URL 是否正确，确保有推送权限

### Q: Actions 不运行？
A: 检查是否启用了 Actions，查看仓库 Settings > Actions

### Q: 如何跳过某个 Actions？
A: 在 commit message 中添加 `[skip ci]`

### Q: 如何查看部署日志？
A: Actions > 选择运行 > 查看具体步骤日志

---

**祝你发布顺利！🎉**
