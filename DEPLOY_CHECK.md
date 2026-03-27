# GitHub 部署检查清单

## ✅ 已完成

### 1. SSH 密钥配置
- [x] SSH 公钥已添加到 GitHub
- [x] 部署用户：`root`
- [x] 服务器地址：`101.200.53.98`

### 2. GitHub Actions 工作流
- [x] `auto-deploy.yml` - 完整部署流程
- [x] `deploy-simple.yml` - 简化部署流程 (新增)
- [x] 已推送到 GitHub (39cebd3)

### 3. GitHub Secrets (需要你确认)
访问：https://github.com/knight-zmz/biostructure-db/settings/secrets/actions

必需 Secrets:
```
DEPLOY_SSH_KEY: <SSH 私钥内容>
DEPLOY_HOST: 101.200.53.98
DEPLOY_USER: root (已在脚本中硬编码)
DEPLOY_PORT: 22
```

---

## 🚀 测试部署

### 方式 1: 推送代码自动触发
```bash
# 任何推送到 main 的提交都会触发部署
git commit -m "test deploy" && git push
```

### 方式 2: 手动触发
1. 访问：https://github.com/knight-zmz/biostructure-db/actions
2. 选择 "🚀 Simple Deploy"
3. 点击 "Run workflow"

---

## 📊 部署日志

查看实时日志:
https://github.com/knight-zmz/biostructure-db/actions

---

## 🔧 故障排查

### 如果部署失败:

1. **检查 SSH 连接**:
```bash
# 在 GitHub Actions 中测试
ssh -i ~/.ssh/id_ed25519 root@101.200.53.98 "echo success"
```

2. **检查 Secrets 配置**:
- 确保 `DEPLOY_SSH_KEY` 是完整的私钥
- 确保 `DEPLOY_HOST` 正确

3. **检查服务器权限**:
```bash
# 在服务器上执行
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

---

## ✅ 当前状态

| 项目 | 状态 |
|------|------|
| Git 推送 | ✅ 成功 (39cebd3) |
| SSH 配置 | ✅ root 用户 |
| GitHub Actions | ⏳ 等待 Secrets |
| 自动同步 | ✅ 每 30 分钟 |

