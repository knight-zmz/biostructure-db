# 🔐 安全配置指南

## GitHub Token 权限配置

### 推荐的 Token 设置

**1. 创建 Fine-grained Token**

访问：https://github.com/settings/tokens/new

**2. 仓库访问限制**

```
Repository access
─────────────────
○ All repositories
● Only select repositories

Selected repositories:
  ✓ biostructure-db
```

**3. 权限设置 (最小权限原则)**

```
Account permissions
───────────────────
✓ Contents        Read and write
✓ Actions         Read and write  
✓ Metadata        Read only

All other permissions: None ❌
```

**4. Token 有效期**

```
Expiration: 90 days
✅ Enable expiration
✅ Receive email notifications 30 days before expiration
```

---

## 🔑 在服务器配置 Token

### 方法 1: 使用 Git Credential Manager (推荐)

```bash
# 第一次 push 时会提示输入
git push -u origin main
# 输入你的 GitHub 用户名和 Token
```

### 方法 2: 使用 Credential Helper

```bash
# 配置凭证存储
git config --global credential.helper store

# 第一次 push 输入凭证
git push
# 输入：https://<username>:<token>@github.com
```

### 方法 3: 使用 SSH (最安全)

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "github-deploy"

# 添加公钥到 GitHub
# https://github.com/settings/keys

# 测试连接
ssh -T git@github.com
```

---

## ⚠️ 安全注意事项

### ✅ 推荐做法

1. **使用 Fine-grained Token** - 限制到特定仓库
2. **设置过期时间** - 90 天或更短
3. **定期轮换** - 到期前更新
4. **使用 SSH** - 比 Token 更安全
5. **最小权限** - 只给必要的权限

### ❌ 不推荐做法

1. ❌ 使用 Classic Token (权限太广)
2. ❌ 永不过期的 Token
3. ❌ 给所有仓库权限
4. ❌ 在代码中硬编码 Token
5. ❌ 提交 `.env` 或凭证文件到 Git

---

## 📦 GitHub Actions Secrets 配置

### 自动部署需要的 Secrets

访问：`https://github.com/<user>/biostructure-db/settings/secrets/actions`

| Secret Name | Value | 说明 |
|-------------|-------|------|
| `DEPLOY_SSH_KEY` | SSH 私钥 | 用于 SSH 部署到服务器 |
| `DEPLOY_HOST` | 服务器 IP | 你的阿里云服务器 IP |
| `DEPLOY_USER` | 用户名 | 如 `admin` |

### 添加 Secret 步骤

1. 访问仓库 Settings > Secrets and variables > Actions
2. 点击 "New repository secret"
3. 输入 Name 和 Value
4. 点击 "Add secret"

---

## 🔍 验证配置

### 检查 Token 权限

```bash
# 测试推送权限
git push

# 测试 Actions 权限
# 推送后查看 Actions 是否触发
# https://github.com/<user>/biostructure-db/actions
```

### 检查 SSH 连接

```bash
# 测试 SSH
ssh -T git@github.com
# 应该看到：Hi <username>! You've successfully authenticated
```

---

## 🚨 应急响应

### 如果 Token 泄露

1. **立即撤销**
   - https://github.com/settings/tokens
   - 找到泄露的 Token
   - 点击 "Revoke"

2. **创建新 Token**
   - 重新按照上述步骤创建
   - 更新服务器上的配置

3. **检查日志**
   - 查看是否有异常活动
   - https://github.com/settings/security-log

---

## 📚 相关文档

- [GitHub Fine-grained Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [SSH 密钥配置](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

---

**安全提示：永远不要在代码中提交 Token 或密码！**
