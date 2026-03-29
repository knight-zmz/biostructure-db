# GitHub Actions 部署闭环验证报告

**验证时间**: 2026-03-29 23:50 CST  
**验证人**: AI Agent (单主控模式)  
**验证方法**: 多维度证据链交叉验证

---

## 1. 验证设计

### 1.1 测试推送

**提交**: `9121d66 test: trigger GitHub Actions deploy verification`  
**推送时间**: 2026-03-29 23:35:55 CST  
**推送分支**: `main`  
**测试文件**: `.github_deploy_test.md`

### 1.2 预期行为链

```
推送 → GitHub Actions 触发 → SSH 部署 → PM2 重启 → 健康检查通过
  │         │              │          │           │
  │         │              │          │           └─ 验证点 5
  │         │              │          └─ 验证点 4
  │         │              └─ 验证点 3
  │         └─ 验证点 2
  └─ 验证点 1
```

---

## 2. 逐项验证结果

### 验证点 1: 文件已部署到生产目录

**检查**: `ls -la /var/www/myapp/.github_deploy_test.md`

**结果**:
```
-rw-rw-r-- 1 admin admin 461 Mar 29 23:35 /var/www/myapp/.github_deploy_test.md
```

**结论**: ✅ **已验证**

**说明**: 文件存在于生产目录，但**不能单独证明**是 GitHub Actions 部署的（可能是其他同步方式）。

---

### 验证点 2: Workflow 实际触发并完成

**检查方法**: GitHub Actions 页面日志

**当前证据**:
- 推送已确认：`git log` 显示 commit `9121d66` 已推送到 origin
- 无法从服务器端直接验证 GitHub Actions 执行状态

**结论**: ⏳ **仍待验证** (需访问 GitHub 网页确认)

---

### 验证点 3: Deploy via SSH 步骤成功

**检查方法**: PM2 日志中的重启记录

**证据**:
```bash
$ pm2 logs myapp --lines 50 | grep "2026-03-29T23:3[5-9]"
0|myapp    | 2026-03-29T23:37:34: 🧬 BioStructure DB API running on port 3000
```

**分析**:
- 23:35:55 推送
- 23:37:34 应用启动 (这是我们手动执行 `pm2 restart myapp --update-env` 的时间)
- 23:35-23:37 之间**无其他重启记录**

**结论**: ⏳ **仍待验证** (无法区分是手动重启还是自动重启)

---

### 验证点 4: Restart PM2 步骤成功

**检查**: `pm2 describe myapp | grep restarts`

**结果**:
```
│ restarts          │ 1                                     │
│ uptime            │ 13m                                   │
```

**分析**:
- restarts = 1 (我们手动重启的那次)
- 如果 GitHub Actions 成功执行，restarts 应该 = 2

**结论**: ⏳ **仍待验证** (重启次数与手动操作一致，无额外重启)

---

### 验证点 5: 健康检查对应部署后实例

**检查**: `curl http://localhost:3000/api/health`

**结果**:
```json
{"success":true,"status":"healthy","uptime":157s}
```

**结论**: ✅ **已验证** (应用健康，但无法证明是部署后的实例)

---

## 3. 问题根因分析

### 3.1 SSH 密钥配置检查

**服务器部署密钥**:
```bash
$ cat ~/.ssh/biostructure_db_deploy.pub
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFQ2m9wlN5m/DXkJ0uQcqOZ2Ui6RCvTXVfMI7+B9EuJT
```

**授权密钥列表**:
```bash
$ cat ~/.ssh/authorized_keys
ecdsa-sha2-nistp521 AAAAE2VjZHNhLXNoYTItbmlzdHA1MjEAAAAIbmlzdHA1MjEAAACFBAGtegeXclq+7SeivMK49FZyB09e+MWUHXDJdpMCq/4Gjnxp2CZECH/j3qLQ+QbWVVLfZxWh6t7taDPeDf4dbbkkcQH9UiZxIMn1OkzSb0kceSJEKUD0fNJWTZF0kAeZwsi8E/zaKtjIWcqccN+bUVMPuW32xpl/9sXJrtr3BB/xPhA83Q== swas-imported-key
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE+YtyfGxE+XHxEglQqwCR29eG8AgWpEedoZTk4eIWvM seetacloud-cursor
```

**比对结果**:
```bash
$ grep -F "$(cat ~/.ssh/biostructure_db_deploy.pub | awk '{print $2}')" ~/.ssh/authorized_keys
# (无结果)
```

**结论**: 🔴 **部署公钥未添加到 authorized_keys**

---

### 3.2 问题链路推断

```
GitHub Actions 触发
       │
       ▼
Deploy via SSH 步骤
       │
       ├─ 使用 secrets.DEPLOY_SSH_KEY (私钥在 GitHub)
       │
       ▼
尝试 SSH 连接到服务器
       │
       ├─ 服务器检查 authorized_keys
       │  └─ ❌ 未找到匹配的公钥
       │
       ▼
SSH 连接失败
       │
       ▼
Deploy 步骤失败
       │
       ▼
Restart PM2 步骤不执行 (前置步骤失败)
```

---

### 3.3 文件为何出现在生产目录

**推断**: 文件出现在 `/var/www/myapp` 但不是通过 GitHub Actions 部署

**可能原因**:
1. 我们手动执行了 `cp` 命令同步文件
2. 之前的某次手动操作

**证据**:
```bash
# 我们确实执行了文件同步
$ cp ops/*.md /var/www/myapp/ops/
```

**结论**: 文件存在**不能证明** GitHub Actions 闭环成功

---

## 4. 严格分级结论

| 验证项 | 等级 | 证据 |
|--------|------|------|
| 测试文件推送到 GitHub | ✅ 已验证 | `git push` 成功，commit `9121d66` |
| 测试文件存在于生产目录 | ✅ 已验证 | `ls -la` 确认文件存在 |
| Workflow 实际触发 | ⏳ 仍待验证 | 需查看 GitHub Actions 页面 |
| Deploy via SSH 成功 | 🔴 尚未解决 | SSH 公钥未授权，连接会失败 |
| Restart PM2 执行 | 🔴 尚未解决 | 前置步骤失败，此步骤不执行 |
| PM2 重启归因于部署 | 🔴 尚未解决 | 当前重启是手动操作 |
| 健康检查通过 | ✅ 已验证 | `/api/health` 返回 healthy |
| **完整部署闭环** | 🔴 **尚未解决** | SSH 密钥未配置 |

---

## 5. 问题定位

### 5.1 根本原因

**SSH 公钥未授权到服务器**

部署密钥对 (`biostructure_db_deploy`) 已生成，但公钥未添加到 `~/.ssh/authorized_keys`，导致 GitHub Actions 无法 SSH 连接。

### 5.2 次要原因

**GitHub Secrets 配置状态未知**

即使 SSH 密钥配置正确，还需确认以下 Secrets 已配置:
- `DEPLOY_SSH_KEY` - 私钥内容
- `DEPLOY_HOST` - 服务器公网 IP
- `DEPLOY_USER` - SSH 用户 (admin)

---

## 6. 修复步骤

### 6.1 立即可执行的修复 (无需用户介入)

```bash
# 1. 将部署公钥添加到 authorized_keys
cat ~/.ssh/biostructure_db_deploy.pub >> ~/.ssh/authorized_keys

# 2. 验证添加成功
grep "biostructure-db-deploy" ~/.ssh/authorized_keys

# 3. 测试 SSH 连接 (从服务器本地测试)
ssh -i ~/.ssh/biostructure_db_deploy admin@localhost "echo SSH OK"
```

### 6.2 需要用户介入的修复

**在 GitHub 仓库 Settings→Secrets and variables→Actions 配置**:

| Secret 名 | 值 | 获取方式 |
|----------|-----|----------|
| `DEPLOY_SSH_KEY` | 私钥内容 | `cat ~/.ssh/biostructure_db_deploy` |
| `DEPLOY_HOST` | 服务器公网 IP | 阿里云 ECS 控制台查看 |
| `DEPLOY_USER` | `admin` | 固定值 |

---

## 7. 验证计划

### 7.1 修复后验证步骤

```bash
# 1. 添加公钥
cat ~/.ssh/biostructure_db_deploy.pub >> ~/.ssh/authorized_keys

# 2. 创建新的测试提交
echo "# Deploy Test 2 $(date)" > .github_deploy_test_2.md
git add . && git commit -m "test: deploy verification 2" && git push

# 3. 等待 60 秒让 GitHub Actions 执行

# 4. 检查 PM2 日志
pm2 logs myapp --lines 20 | grep "2026-03-29T23:5"

# 5. 检查重启次数
pm2 describe myapp | grep restarts
# 应从 1 变为 2

# 6. 验证新文件
ls -la /var/www/myapp/.github_deploy_test_2.md
```

### 7.2 成功判据

- [ ] PM2 restarts 从 1 增加到 2
- [ ] PM2 日志显示新的启动记录 (时间戳在推送后 1-2 分钟)
- [ ] 新测试文件存在于生产目录
- [ ] 健康检查通过

---

## 8. 证据链完整性评估

| 证据类型 | 状态 | 说明 |
|----------|------|------|
| 推送证据 | ✅ 完整 | git log 确认 |
| 文件存在证据 | ✅ 完整 | ls 确认 |
| Workflow 执行证据 | ❌ 缺失 | 需 GitHub 网页 |
| SSH 连接证据 | ❌ 缺失 | 密钥未配置 |
| PM2 重启证据 | ⚠️ 不完整 | 无法区分手动/自动 |
| 健康检查证据 | ✅ 完整 | curl 确认 |

**整体评估**: 🔴 **证据链不完整**，无法证明闭环成功

---

**报告状态**: ✅ 完成  
**闭环状态**: 🔴 尚未解决  
**根本原因**: SSH 公钥未授权  
**修复优先级**: 🔴 P0 (立即可修复)
