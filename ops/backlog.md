# 📋 Backlog - 待办事项清单

**生成时间**: 2026-03-29 22:56 CST  
**更新时间**: 2026-03-30 13:35 CST  
**当前阶段**: P1 已部署待验证，等待 P2 阶段切换确认  
**优先级**: 🔴 紧急 | 🟡 重要 | 🟢 可选

---

## ✅ 已完成闭环 (P0)

### 1-7. 基础环境
- [x] 安装 PostgreSQL 13+ ✅
- [x] 安装 Redis 6+ ✅
- [x] 安装 PM2 ✅
- [x] 创建环境变量文件 ✅
- [x] 启动应用并验证健康检查 ✅
- [x] SSH 公钥授权 ✅
- [x] 安装 rsync ✅

### 8. GitHub Actions 部署
- [x] 创建 deploy.yml 工作流文件 ✅
- [x] SSH 公钥已添加到服务器 authorized_keys ✅
- [x] workflow 已触发 (连续 3 次推送均触发) ✅
- [x] SSH 连接已建立 ✅
- [x] 安装 rsync (✅ 已安装 3.1.3) ✅
- [x] 验证 Deploy via SSH 步骤通过 ✅
- [x] 验证 Restart PM2 步骤执行 ✅
- [x] 验证自动部署流程 ✅

**验收标准**: push 到 main 分支后自动部署并重启 PM2  
**状态**: ✅ **已完成** (2026-03-30 00:29)  
**复验**: ✅ **已通过** (2026-03-30 00:38, 第二次复验)

**验证证据**:
- PM2 restarts: 1→2→4 (连续 2 次自动重启)
- PM2 uptime: 46s (最新启动)
- PM2 日志：00:38:09 启动记录
- 测试文件：`/var/www/myapp/.github_deploy_test_3.md` 存在
- 健康检查：`/api/health` 返回 healthy

**部署验证历史**:
| 测试 | 提交 | 时间 | restarts | 结果 |
|------|------|------|----------|------|
| 测试 1 | 9121d66 | 23:35 | 1→1 | 🔴 失败 (rsync not found) |
| 测试 2 | dc430c7 | 00:28 | 1→2 | ✅ 成功 (rsync 安装后) |
| 测试 3 | fc5599e | 00:37 | 2→4 | ✅ 成功 (复验通过) |

---

## 🟡 P1 - 工程完善 (已实现，待运行验证)

### 9. 配置数据库自动备份 🟡
- [x] 创建备份脚本 `scripts/backup-db.sh` ✅
- [x] 配置 cron 定时任务 (每日 2:00) ✅
- [x] 设置备份保留策略 (7 天) ✅
- [x] 测试备份流程 ✅
- [ ] 运行验证：观察 7 天备份周期 ⏳

**验收标准**: 每天自动备份，可恢复  
**状态**: 🟡 **已部署，待运行验证** (2026-03-30 12:45)

**验证证据**:
- 备份脚本：`/home/admin/biostructure-db/scripts/backup-db.sh`
- 备份文件：`/home/admin/backups/myapp_20260330_124555.sql.gz` (5.2K)
- Cron 任务：`0 2 * * *` 每日执行
- 备份日志：`/home/admin/backups/backup.log`

**待验证事项**:
- ⏳ 连续 7 天自动备份是否稳定执行
- ⏳ 备份文件是否按保留策略清理
- ⏳ 恢复流程是否可用 (需手动测试)

### 10. 配置基础监控告警 🟡
- [x] 创建监控脚本 `scripts/monitor.sh` ✅
- [x] 配置 cron 定时采集 (每 10 分钟) ✅
- [x] 配置告警阈值 ✅
- [x] 告警日志记录 ✅
- [ ] 运行验证：观察告警触发机制 ⏳

**验收标准**: 服务异常时及时告警  
**状态**: 🟡 **已部署，待运行验证** (2026-03-30 12:46)

**验证证据**:
- 监控脚本：`/home/admin/biostructure-db/scripts/monitor.sh`
- 指标日志：`/home/admin/logs/metrics.log`
- 告警日志：`/home/admin/logs/alerts.log`
- Cron 任务：`*/10 * * * *` 每 10 分钟采集
- 当前状态：所有服务正常，无告警

**待验证事项**:
- ⏳ 告警阈值触发是否准确
- ⏳ 告警日志是否正确记录
- ⏳ 长期运行是否稳定 (无内存泄漏/资源占用)

---

## 🟡 P2 - 数据与内容建设 (首轮验证完成)

### 11. 样例数据导入 🟡
- [x] 准备示例 PDB 数据 (1CRN, 1UBQ, 7ZNT, 6VXX, 1A4Y) ✅
- [x] 测试导入脚本 (`/api/import-samples`) ✅
- [x] 验证数据导入流程 ✅
- [x] 验证 API 返回数据 ✅
- [x] 验证单条导入 (`/api/import/:pdbId`) ✅
- [ ] 修复 atoms 表重复导入问题 ⏳

**验收标准**: API 返回非零结构数  
**状态**: 🟡 **基本成立** (首轮验证通过)

**验证证据**:
- 导入结构：6 个 (1CRN, 1UBQ, 7ZNT, 6VXX, 1A4Y, 1TIM)
- 总原子数：4240
- 实验方法：X-RAY DIFFRACTION (5), ELECTRON MICROSCOPY (1)
- API 端点：`/api/stats` 返回真实数据
- 数据库表：structures, atoms, polypeptides, residues 均有数据

**发现问题**:
- ⚠️ atoms 表无唯一约束，重复导入会导致数据翻倍
- ⚠️ polypeptides/residues 在批量导入中未插入（仅单条导入有）
- ℹ️ 建议：后续添加 (pdb_id, atom_name, chain_id, residue_num, x_coord, y_coord, z_coord) 唯一约束

### 12. API/页面内容完善 🔄
- [ ] 补充 API 端点文档
- [ ] 完善前端展示
- [ ] 添加使用示例

**验收标准**: 用户可通过文档调用 API  
**状态**: 🔄 **待开始**

---

## 🟢 P3 - 后续维护

### 13. Node.js 版本升级 (20→22)
- [ ] 更新 `.github/workflows/deploy.yml` Node.js 版本
- [ ] 验证兼容性
- [ ] 更新 `package.json` engines 字段

**验收标准**: GitHub Actions 使用 Node.js 22  
**状态**: ⏳ **未开始** (当前为警告，非阻塞，2026-04-30 EOL)

### 14. 历史文档归档
- [ ] 创建 `docs/archive/` 目录
- [ ] 移动历史文档到归档目录
- [ ] 更新 README.md 文档导航

**验收标准**: 根目录只保留必要文档  
**状态**: ⏳ **未开始**

### ⏸️ 暂停任务（备案完成后恢复）

### 15. HTTPS 接入
- [ ] 备案完成后申请 Let's Encrypt 证书
- [ ] 配置 Nginx 443 端口
- [ ] 配置 HTTP→HTTPS 重定向

**验收标准**: https://jlupdb.me 可正常访问  
**状态**: ⏸️ **暂停** (ICP 备案限制)
