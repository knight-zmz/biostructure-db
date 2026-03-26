# 🚀 云端部署状态

## ✅ 已完成

### 服务状态
- ✅ **Nginx** - 运行中 (端口 80)
- ✅ **Node.js API** - 运行中 (端口 3000)
- ✅ **PostgreSQL** - 运行中 (端口 5432)
- ✅ **PM2** - 进程管理正常

### 访问测试
- ✅ 静态页面：http://localhost/
- ✅ REST API：http://localhost/api/stats
- ✅ 生物 API：http://localhost/api/bio/stats/detailed

### GitHub 部署
- ✅ 仓库：https://github.com/knight-zmz/biostructure-db
- ✅ 代码已推送 (2 commits, 19 files)
- ✅ GitHub Actions 配置完成

---

## 🌐 访问方式

### 本地访问
```
http://localhost/
http://localhost/api/stats
http://localhost/api/bio/stats/detailed
```

### 公网访问
**需要配置阿里云安全组**

1. **登录阿里云控制台**
2. **进入 ECS 实例管理**
3. **配置安全组规则**
4. **添加入站规则**:
   ```
   端口范围：80/80
   授权对象：0.0.0.0/0
   优先级：1
   ```

### 公网访问地址 (配置后)
```
http://<你的公网 IP>/
```

---

## 📊 服务器信息

| 项目 | 值 |
|------|-----|
| 内网 IP | 172.25.42.100 |
| 操作系统 | Alibaba Cloud Linux 3 |
| CPU | 查看阿里云控制台 |
| 内存 | 1.8GB |
| 磁盘 | 40GB (已用 14GB) |

---

## 🔧 服务管理命令

```bash
# 查看服务状态
pm2 status
systemctl status nginx
systemctl status postgresql

# 重启服务
pm2 restart myapp
systemctl restart nginx
systemctl restart postgresql

# 查看日志
pm2 logs myapp
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 数据库操作
sudo -u postgres psql -d myapp
```

---

## 📁 项目位置

```
/var/www/myapp/
├── app.js              # 主应用
├── bioapi.js           # 生物 API
├── pdb-parser.js       # PDB 解析器
├── mcp-server.js       # MCP 服务器
├── public/index.html   # 前端页面
├── schema_v2.sql       # 数据库 Schema
└── README.md           # 文档
```

---

## ⚠️ 需要配置的项目

### 1. 阿里云安全组 (必需)
- 开放端口 80 (HTTP)

### 2. HTTPS 配置 (建议)
- 配置 Let's Encrypt 证书
- 开放端口 443

### 3. 数据库远程访问 (可选)
- 如需远程访问 PostgreSQL
- 开放端口 5432
- 修改 pg_hba.conf

---

## 🎯 当前状态

**本地访问**: ✅ 正常
**公网访问**: ⚠️ 需要配置安全组
**数据库**: ✅ 正常
**API 服务**: ✅ 正常

---

**部署完成！配置安全组后即可通过公网访问！** 🦞
