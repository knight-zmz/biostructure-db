# 🔧 SSH 连接快速修复指南

## 问题：公钥已添加但 SSH 仍失败

### 立即排查步骤

**请在你的本地电脑执行以下命令**：

---

### 步骤 1: 验证公钥确实添加了

```bash
# 1. 密码登录服务器 (使用你的服务器密码)
ssh admin@101.200.53.98

# 2. 检查 authorized_keys 文件
cat ~/.ssh/authorized_keys

# 应该输出:
# ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE+tyfGxE+XHxEglQqwCR29eG8AgWpEedoZTk4eIWvM seetacloud-cursor

# 3. 检查权限
ls -la ~/.ssh/
# 应该看到:
# drwx------ 2 admin admin 4096 ... .ssh
# -rw------- 1 admin admin  ... authorized_keys

# 4. 如果权限不对，修复:
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# 5. 退出
exit
```

---

### 步骤 2: 测试 SSH 连接

```bash
# 使用私钥测试
ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no admin@101.200.53.98 "echo 成功"
```

**如果成功**：会输出 "成功"

**如果失败**：继续步骤 3

---

### 步骤 3: 检查服务器 SSH 配置

```bash
# 1. 密码登录服务器
ssh admin@101.200.53.98

# 2. 检查 SSH 配置
sudo cat /etc/ssh/sshd_config | grep -i "pubkey\|authorized"

# 应该看到:
# PubkeyAuthentication yes
# AuthorizedKeysFile .ssh/authorized_keys

# 3. 如果没有，编辑配置:
sudo nano /etc/ssh/sshd_config
# 添加或取消注释:
# PubkeyAuthentication yes
# AuthorizedKeysFile .ssh/authorized_keys

# 4. 重启 SSH 服务:
sudo systemctl restart sshd

# 5. 退出
exit
```

---

### 步骤 4: 检查 GitHub Secrets

访问：https://github.com/knight-zmz/biostructure-db/settings/secrets/actions

**验证 3 个 Secrets**:

1. **DEPLOY_SSH_KEY**:
   - 必须是**私钥**（不是公钥）
   - 运行 `cat ~/.ssh/id_ed25519` 获取
   - 包含 `-----BEGIN OPENSSH PRIVATE KEY-----`

2. **DEPLOY_HOST**: `101.200.53.98`

3. **DEPLOY_USER**: `admin` (或 `root` 如果用 root 用户)

---

### 步骤 5: 完整重置 (如果以上都失败)

```bash
# 1. 在服务器上完全重置 SSH
ssh admin@101.200.53.98
sudo rm -rf ~/.ssh
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 2. 重新添加公钥
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE+tyfGxE+XHxEglQqwCR29eG8AgWpEedoZTk4eIWvM seetacloud-cursor" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 3. 验证
cat ~/.ssh/authorized_keys
ls -la ~/.ssh/

# 4. 重启 SSH 服务
sudo systemctl restart sshd

# 5. 退出
exit

# 6. 测试
ssh -i ~/.ssh/id_ed25519 admin@101.200.53.98 "echo 成功"
```

---

## 🦞 快速诊断命令

**请执行并告诉我输出**：

```bash
# 1. 验证公钥添加
ssh admin@101.200.53.98 "cat ~/.ssh/authorized_keys"

# 2. 验证权限
ssh admin@101.200.53.98 "ls -la ~/.ssh/"

# 3. 验证 SSH 配置
ssh admin@101.200.53.98 "sudo cat /etc/ssh/sshd_config | grep -i pubkey"
```

---

## 常见问题

### Q: 找不到 authorized_keys 文件？
**A**: 公钥可能添加到了错误的目录，检查 `/home/admin/.ssh/authorized_keys`

### Q: 权限总是重置？
**A**: 可能是 SELinux 或其他安全策略，运行 `restorecon -R ~/.ssh`

### Q: SSH 服务没有运行？
**A**: `sudo systemctl status sshd` 检查状态，`sudo systemctl start sshd` 启动

---

## 下一步

执行完上述诊断后，告诉我：
1. `cat ~/.ssh/authorized_keys` 的输出
2. `ls -la ~/.ssh/` 的输出
3. SSH 测试是否成功

我会根据输出继续修复！

🦞 持续工作中...
