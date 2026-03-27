# GitHub 自动部署配置指南

## ✅ 已完成配置

### 1. Git 远程仓库
- **URL**: https://github.com/knight-zmz/biostructure-db.git
- **分支**: main
- **状态**: ✅ 已推送最新代码 (64be760)

### 2. 自动同步脚本
- **路径**: `scripts/auto-sync-github.sh`
- **Cron**: 每 30 分钟自动同步
- **日志**: `/var/www/myapp/github-sync.log`

### 3. .gitignore
- 已配置忽略 node_modules/, coverage/, *.log 等

---

## ⚠️ 需要配置的 GitHub Secrets

访问：https://github.com/knight-zmz/biostructure-db/settings/secrets/actions

### 必需 Secrets:

```
DEPLOY_SSH_KEY: <服务器 SSH 私钥>
DEPLOY_HOST: <服务器 IP 或域名>
DEPLOY_USER: <SSH 用户名>
DEPLOY_PORT: 22
```

### 生成 SSH 密钥对 (在服务器上):

```bash
# 生成密钥
ssh-keygen -t ed25519 -C "github-actions" -f /home/admin/.ssh/github_actions

# 显示公钥 (复制到 GitHub Deploy Keys)
cat /home/admin/.ssh/github_actions.pub

# 显示私钥 (复制到 GitHub Secrets)
cat /home/admin/.ssh/github_actions
```

### 配置 GitHub Deploy Keys:

1. 访问：https://github.com/knight-zmz/biostructure-db/settings/keys
2. 点击 "Add deploy key"
3. Title: `GitHub Actions Deploy`
4. Key: 粘贴公钥内容
5. 勾选 "Allow write access"
6. 点击 "Add key"

---

## 🔄 自动工作流

### GitHub Actions 触发条件:
- ✅ Push 到 main 分支
- ✅ 手动触发 (workflow_dispatch)

### 部署流程:
1. 代码推送到 GitHub
2. GitHub Actions 自动运行测试
3. 测试通过后 SSH 部署到服务器
4. PM2 自动重启应用

---

## 📊 当前状态

| 项目 | 状态 |
|------|------|
| Git 远程仓库 | ✅ 已配置 |
| 本地推送 | ✅ 成功 (64be760) |
| 自动同步脚本 | ✅ 每 30 分钟 |
| GitHub Actions | ⚠️ 需要配置 Secrets |
| SSH 密钥 | ⚠️ 需要生成 |

---

## 🚀 快速测试

```bash
# 手动触发同步
cd /var/www/myapp && bash scripts/auto-sync-github.sh

# 查看同步日志
tail -20 /var/www/myapp/github-sync.log

# 检查 GitHub Actions
访问：https://github.com/knight-zmz/biostructure-db/actions
```
