# 目录使用规范

**生成时间**: 2026-03-29 23:40 CST  
**目的**: 明确 `/var/www/myapp` 与 `/home/admin/biostructure-db` 的角色分工

---

## 1. 目录角色定义

### 1.1 `/var/www/myapp` - 生产运行目录

**角色**: **唯一生产运行路径**

**用途**:
- PM2 进程工作目录
- GitHub Actions 部署目标
- 线上服务代码
- 生产环境 `.env` 配置

**管理方式**:
- 由 GitHub Actions 自动部署
- 不应手动修改代码
- 可手动修改 `.env` (不提交)

**权限**:
- 所有者：`admin:admin`
- PM2 从此目录启动应用

---

### 1.2 `/home/admin/biostructure-db` - 开发工作目录

**角色**: **Git 仓库工作区**

**用途**:
- Git 提交和推送
- 代码开发和测试
- ops/ 文档编辑
- 脚本开发和测试

**管理方式**:
- 开发者手动操作
- 执行 `git commit` 和 `git push`
- 测试后同步到生产

**权限**:
- 所有者：`admin:admin`
- 不直接运行应用

---

## 2. 工作流程

### 2.1 标准开发流程

```
[开发] /home/admin/biostructure-db
  │
  ├─ 修改代码
  ├─ 测试验证
  ├─ git commit
  └─ git push origin main
       │
       ▼
[部署] GitHub Actions
  │
  ├─ 自动触发 workflow
  ├─ SSH 部署到 /var/www/myapp
  └─ PM2 重启应用
       │
       ▼
[运行] /var/www/myapp
  │
  └─ 生产环境运行
```

### 2.2 紧急修复流程

```
[紧急修复] /var/www/myapp
  │
  ├─ 直接修改代码 (不推荐)
  ├─ 验证修复
  └─ 同步回开发目录
       │
       ▼
[同步] /home/admin/biostructure-db
  │
  ├─ git pull
  ├─ 确认修改
  └─ git commit (记录紧急修复)
```

---

## 3. 目录同步

### 3.1 自动同步 (推荐)

通过 GitHub Actions 自动同步:
```bash
# 在开发目录
cd /home/admin/biostructure-db
git add .
git commit -m "feat: ..."
git push origin main
# GitHub Actions 自动部署到 /var/www/myapp
```

### 3.2 手动同步 (紧急情况下)

```bash
# 从开发目录同步到生产
rsync -av --exclude='.env' --exclude='node_modules' \
  /home/admin/biostructure-db/ /var/www/myapp/
cd /var/www/myapp
pm2 restart myapp
```

---

## 4. 禁止事项

| 操作 | 禁止原因 |
|------|----------|
| 在 `/var/www/myapp` 执行 `git commit` | 生产目录不应直接提交 |
| 在 `/home/admin/biostructure-db` 运行 PM2 | 避免路径分叉 |
| 手动修改 `/var/www/myapp` 代码后不同步 | 导致代码不一致 |
| 删除 `/home/admin/biostructure-db` | 丢失开发工作区 |

---

## 5. 清理建议

### 5.1 保留 `/home/admin/biostructure-db`

**理由**:
- Git 仓库工作区
- 开发测试环境
- ops/ 文档编辑场所

### 5.2 可选清理项

以下项目可考虑从开发目录清理:
- `node_modules/` (生产环境才需要)
- `.env` (生产配置，不应提交)

---

## 6. 验证命令

```bash
# 确认 PM2 运行路径
pm2 describe myapp | grep "script path"
# 应显示：/var/www/myapp/src/app.js

# 确认 Git 仓库位置
cd /home/admin/biostructure-db && git remote -v
# 应显示 GitHub 仓库地址

# 确认生产代码版本
cd /var/www/myapp && git log --oneline -1
# 应与 GitHub main 分支一致
```

---

**状态**: ✅ 已规范化  
**执行**: 保留两目录，明确分工
