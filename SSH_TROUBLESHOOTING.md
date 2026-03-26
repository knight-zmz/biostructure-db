# 🔧 SSH 连接问题诊断

## 问题：SSH 公钥添加后仍然连接失败

### 可能原因

1. **公钥格式不正确**
   - 可能只复制了部分公钥
   - 可能包含了额外的空格或换行

2. **文件权限问题**
   - `~/.ssh` 目录权限不是 700
   - `~/.ssh/authorized_keys` 权限不是 600

3. **SSH 配置问题**
   - 服务器 SSH 配置禁止公钥认证
   - authorized_keys 文件路径不正确

4. **用户不匹配**
   - 公钥添加到了错误的用户目录
   - 应该使用 root 用户而不是 admin

---

## 解决方案

### 方案 1: 使用密码登录验证

**在你的本地电脑执行**:

```bash
# 1. 密码登录服务器
ssh admin@101.200.53.98
# 输入你的服务器密码

# 2. 检查 authorized_keys 文件
cat ~/.ssh/authorized_keys

# 3. 如果没有输出或文件不存在
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE+tyfGxE+XHxEglQqwCR29eG8AgWpEedoZTk4eIWvM seetacloud-cursor' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# 4. 验证
cat ~/.ssh/authorized_keys

# 5. 退出
exit
```

---

### 方案 2: 使用 root 用户

如果 admin 用户不行，尝试 root 用户：

```bash
# 1. 登录 root 用户
ssh root@101.200.53.98
# 输入 root 密码

# 2. 添加公钥
mkdir -p ~/.ssh
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE+tyfGxE+XHxEglQqwCR29eG8AgWpEedoZTk4eIWvM seetacloud-cursor' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# 3. 更新 GitHub Secrets
# DEPLOY_USER: root
```

---

### 方案 3: 检查 SSH 配置

```bash
# 登录服务器后执行
sudo cat /etc/ssh/sshd_config | grep -i "pubkey\|authorized"

# 应该看到:
# PubkeyAuthentication yes
# AuthorizedKeysFile .ssh/authorized_keys
```

---

## 快速测试

**在你的本地电脑执行**:

```bash
# 测试公钥是否生效
ssh -i ~/.ssh/id_ed25519 admin@101.200.53.98 "echo '成功'"
```

如果仍然失败，请：

1. 检查公钥是否正确复制（完整的一行）
2. 检查文件权限（700 和 600）
3. 尝试使用 root 用户
4. 检查服务器 SSH 日志：`sudo tail /var/log/secure`

---

## GitHub Secrets 验证

确保 Secrets 配置正确：

1. **DEPLOY_SSH_KEY**: 
   - 必须是私钥（不是公钥）
   - 包含 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----`
   - 没有额外的空格或换行

2. **DEPLOY_HOST**: `101.200.53.98`（没有空格）

3. **DEPLOY_USER**: `admin` 或 `root`（根据实际用户）

---

## 继续工作

在修复 SSH 问题的同时，项目继续运行：

- ✅ 服务正常运行
- ✅ API 正常响应
- ✅ 数据库正常连接
- ⏳ 等待 SSH 配置完成

**访问**: http://101.200.53.98/
