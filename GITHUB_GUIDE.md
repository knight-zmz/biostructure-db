# 📦 GitHub 发布与自动化部署完整方案

---

## ⚠️ 重要说明

### 我的能力限制

**❌ 我不能做的：**
1. **不能登录你的 GitHub 账号** - 这涉及安全问题
2. **不能直接推送代码** - 需要你的授权
3. **不能访问 GitHub API** - 需要 Token

**✅ 我能做的：**
1. **创建所有配置文件** - GitHub Actions、CI/CD
2. **生成完整文档** - README、发布指南
3. **编写自动化脚本** - 你只需执行

**🔐 安全原则：**
- 你的 GitHub 凭证（密码、Token）**永远不要告诉我**
- 敏感操作（登录、push）**由你亲自执行**
- 我只创建配置文件和脚本

---

## 🚀 完整自动化方案

### 已创建的文件

```
/var/www/myapp/
├── .github/
│   └── workflows/
│       ├── test.yml          # 自动测试
│       ├── deploy.yml        # 自动构建
│       ├── release.yml       # 自动发布
│       └── auto-deploy.yml   # 自动部署到服务器
├── scripts/
│   ├── git-setup.sh          # Git 初始化
│   └── publish-to-github.sh  # 发布检查
├── package.json              # NPM 配置 (含 repository)
├── PUBLISH.md                # 发布指南
└── .gitignore                # Git 忽略文件
```

---

## 📋 发布步骤 (5 分钟)

### 1️⃣ 运行检查脚本
```bash
cd /var/www/myapp
./scripts/publish-to-github.sh
```

### 2️⃣ 初始化 Git
```bash
./scripts/git-setup.sh <你的 GitHub 用户名>
# 例如：./scripts/git-setup.sh octocat
```

### 3️⃣ 在 GitHub 创建仓库
1. 访问 https://github.com/new
2. 仓库名：`biostructure-db`
3. 设为 **Public** (开源)
4. 点击 "Create repository"

### 4️⃣ 推送代码
```bash
# 替换 <your-username> 为你的 GitHub 用户名
git remote add origin https://github.com/<your-username>/biostructure-db.git
git push -u origin main
```

### 5️⃣ 启用 Actions
1. 访问：https://github.com/<your-username>/biostructure-db/actions
2. 点击 "I understand my workflows, go ahead and enable them"

---

## 🔄 自动化功能

### GitHub Actions 工作流

| 工作流 | 触发条件 | 功能 |
|--------|----------|------|
| **test.yml** | Push/PR | 运行测试、代码检查 |
| **deploy.yml** | Push to main | 构建、打包、上传 artifact |
| **release.yml** | Push tag | 创建 GitHub Release |
| **auto-deploy.yml** | Push to main | 自动部署到服务器 |

### 自动部署流程

```
你 push 代码
    ↓
GitHub Actions 触发
    ↓
运行测试 ✅
    ↓
构建打包 ✅
    ↓
SSH 部署到服务器 ✅
    ↓
PM2 重启应用 ✅
    ↓
部署完成！
```

---

## 🔐 配置自动部署到服务器

### 1. 生成 SSH 密钥
```bash
ssh-keygen -t ed25519 -C "github-actions-deploy"
```

### 2. 添加公钥到服务器
```bash
# 复制公钥
cat ~/.ssh/id_ed25519.pub

# 添加到服务器
ssh admin@<服务器 IP> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
# 粘贴公钥内容
```

### 3. 在 GitHub 添加 Secrets
访问：https://github.com/<your-username>/biostructure-db/settings/secrets/actions/new

| Secret Name | Value |
|-------------|-------|
| `DEPLOY_SSH_KEY` | SSH 私钥 (`cat ~/.ssh/id_ed25519`) |
| `DEPLOY_HOST` | 服务器 IP 地址 |
| `DEPLOY_USER` | 服务器用户名 |

---

## 📦 发布新版本

### 语义化版本
```bash
# 更新 package.json 版本号
vim package.json

# 提交并打标签
git add package.json
git commit -m "📦 Release v1.1.0"
git tag v1.1.0
git push origin v1.1.0
```

### 自动 Release
推送标签后，GitHub Actions 会：
- ✅ 创建 GitHub Release
- ✅ 上传构建包 (.tar.gz)
- ✅ 生成 Changelog

---

## 📊 GitHub 仓库功能

### 建议启用的功能

| 功能 | 用途 | 启用方式 |
|------|------|----------|
| **Issues** | 问题追踪 | Settings > Features |
| **Discussions** | 社区讨论 | Settings > Features |
| **Wiki** | 文档 | Settings > Features |
| **Projects** | 项目管理 | Projects tab |
| **Actions** | CI/CD | 自动启用 |

### README 徽章

```markdown
[![Test](https://github.com/<user>/biostructure-db/actions/workflows/test.yml/badge.svg)](https://github.com/<user>/biostructure-db/actions/workflows/test.yml)
[![Deploy](https://github.com/<user>/biostructure-db/actions/workflows/deploy.yml/badge.svg)](https://github.com/<user>/biostructure-db/actions/workflows/deploy.yml)
[![Release](https://img.shields.io/github/v/release/<user>/biostructure-db)](https://github.com/<user>/biostructure-db/releases)
```

---

## 🛠️ 维护与更新

### 日常维护
```bash
# 查看 Actions 运行状态
https://github.com/<user>/biostructure-db/actions

# 查看部署日志
Actions > 选择运行 > 查看日志

# 本地测试
npm test

# 更新依赖
npm update
```

### 故障排除

| 问题 | 解决方案 |
|------|----------|
| Push 失败 | 检查远程仓库 URL |
| Actions 不运行 | 检查是否启用 Actions |
| 部署失败 | 检查 SSH 密钥和 Secrets |
| 测试失败 | 查看测试日志 |

---

## 📚 相关文档

- `PUBLISH.md` - 详细发布指南
- `README.md` - 项目说明
- `SUMMARY.md` - 系统总结
- `.github/workflows/*.yml` - Actions 配置

---

## 💡 最佳实践

1. **频繁提交** - 小步快跑
2. **语义化版本** - v1.0.0, v1.1.0, v2.0.0
3. **PR 审查** - 重要改动走 Pull Request
4. **标签管理** - 每个 Release 打标签
5. **Changelog** - 记录每次变更
6. **分支策略** - main (生产), develop (开发)

---

## 🔗 有用的链接

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [语义化版本](https://semver.org/)
- [SSH 密钥指南](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [npm 发布指南](https://docs.npmjs.com/packages-and-modules/contributing-packages-to-the-registry)

---

**现在你可以按照步骤发布到 GitHub 了！🚀**

有任何问题随时问我！🦞
