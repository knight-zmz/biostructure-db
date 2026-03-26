# 🔧 部署失败修复指南

## ❌ 失败原因

**SSH 公钥未添加到服务器**

GitHub Actions 尝试通过 SSH 部署到服务器，但服务器没有授权 GitHub 的 SSH 密钥。

---

## ✅ 修复方案 (3 步完成)

### 步骤 1: 添加 SSH 公钥到服务器

**在你的本地电脑上执行**:

```bash
# 方法 1: 一键命令
ssh admin@101.200.53.98 "mkdir -p ~/.ssh && echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE+tyfGxE+XHxEglQqwCR29eG8AgWpEedoZTk4eIWvM seetacloud-cursor' >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

**方法 2: 手动操作**

1. 登录服务器：
   ```bash
   ssh admin@101.200.53.98
   # 输入你的服务器密码
   ```

2. 创建 SSH 目录：
   ```bash
   mkdir -p ~/.ssh
   ```

3. 添加公钥：
   ```bash
   nano ~/.ssh/authorized_keys
   ```

4. 粘贴公钥：
   ```
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE+tyfGxE+XHxEglQqwCR29eG8AgWpEedoZTk4eIWvM seetacloud-cursor
   ```

5. 保存退出：
   - 按 `Ctrl+O`
   - 按 `Enter`
   - 按 `Ctrl+X`

6. 设置权限：
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

7. 退出服务器：
   ```bash
   exit
   ```

---

### 步骤 2: 配置 GitHub Secrets

**访问**: https://github.com/knight-zmz/biostructure-db/settings/secrets/actions

**添加 3 个 Secrets**:

1. **DEPLOY_SSH_KEY**:
   - 在你的本地电脑运行：`cat ~/.ssh/id_ed25519`
   - 复制完整输出 (包括 BEGIN 和 END)
   - 在 GitHub 页面点击 "New repository secret"
   - Name: `DEPLOY_SSH_KEY`
   - Value: 粘贴私钥内容
   - 点击 "Add secret"

2. **DEPLOY_HOST**:
   - Name: `DEPLOY_HOST`
   - Value: `101.200.53.98`

3. **DEPLOY_USER**:
   - Name: `DEPLOY_USER`
   - Value: `admin`

---

### 步骤 3: 测试部署

1. 访问：https://github.com/knight-zmz/biostructure-db/actions
2. 点击左侧的 **🚀 Auto Deploy to Server**
3. 点击 **Run workflow**
4. 选择 **main** 分支
5. 点击 **Run workflow**
6. 等待 2-3 分钟
7. 查看是否成功 (绿色勾)

---

## 🔍 验证部署

部署成功后，访问：
- **前端**: http://101.200.53.98/
- **API**: http://101.200.53.98/api/stats

应该能看到更新后的页面！

---

## 📝 常见问题

### Q: 找不到 Settings 选项？
**A**: 确保你是仓库所有者或有管理员权限

### Q: SSH 连接仍然失败？
**A**: 检查：
- 公钥是否正确复制 (包括 ssh-ed25519 前缀)
- authorized_keys 文件权限是否正确 (600)
- .ssh 目录权限是否正确 (700)
- 服务器 SSH 服务是否运行：`sudo systemctl status sshd`

### Q: GitHub Actions 仍然失败？
**A**: 检查：
- Secrets 是否正确配置 (名称完全匹配)
- 私钥格式是否正确 (包括 BEGIN 和 END 行)
- 服务器防火墙是否允许 SSH (端口 22)

---

## 🦞 小龙虾提示

**完成步骤 1 后告诉我**，我会立即测试 SSH 连接并继续部署！

**当前状态**: 持续工作中，等待 SSH 公钥配置...
