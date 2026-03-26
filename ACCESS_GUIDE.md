# 🌐 访问配置指南

## 🎯 当前状态

✅ **本地访问**: 正常工作
- http://localhost/ - 前端页面
- http://localhost/api/stats - API 统计
- http://localhost/api/bio/stats/detailed - 生物 API

⚠️ **公网访问**: 需要配置阿里云安全组

---

## 📋 配置步骤 (只需 1 次)

### 步骤 1: 登录阿里云控制台

访问：https://ecs.console.aliyun.com

### 步骤 2: 找到你的实例

1. 在左侧菜单选择 **实例与镜像** > **实例**
2. 找到你的服务器 (地域：根据你的选择)
3. 点击实例 ID

### 步骤 3: 配置安全组

1. 点击 **本实例安全组** 标签
2. 点击安全组 ID
3. 点击 **手动添加** 规则

### 步骤 4: 添加入站规则

**规则 1: HTTP (必需)**
```
优先级：1
策略：允许
协议类型：TCP
端口范围：80/80
授权对象：0.0.0.0/0
描述：允许 HTTP 访问
```

**规则 2: HTTPS (建议)**
```
优先级：1
策略：允许
协议类型：TCP
端口范围：443/443
授权对象：0.0.0.0/0
描述：允许 HTTPS 访问
```

**规则 3: PostgreSQL (可选，仅开发环境)**
```
优先级：1
策略：允许
协议类型：TCP
端口范围：5432/5432
授权对象：你的本地 IP/32
描述：数据库远程访问
```

### 步骤 5: 保存并等待生效

- 点击 **保存**
- 等待 1-2 分钟生效

---

## 🎉 访问你的生物数据库

### 配置完成后

**1. 获取公网 IP**
- 在阿里云控制台查看
- 或在服务器运行：`curl ifconfig.me`

**2. 访问前端**
```
http://<你的公网 IP>/
```

**3. 测试 API**
```bash
# 统计信息
curl http://<你的公网 IP>/api/stats

# 生物 API
curl http://<你的公网 IP>/api/bio/stats/detailed

# 结构列表
curl http://<你的公网 IP>/api/structures
```

---

## 🔍 故障排除

### 问题 1: 无法访问

**检查清单**:
- [ ] 安全组规则已添加
- [ ] 规则已保存并生效 (等待 2 分钟)
- [ ] 公网 IP 正确
- [ ] Nginx 运行中：`systemctl status nginx`

**解决**:
```bash
# 重启 Nginx
sudo systemctl restart nginx

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/error.log
```

### 问题 2: 404 错误

**检查**:
```bash
# 查看 Nginx 配置
cat /etc/nginx/conf.d/myapp.conf

# 测试配置
sudo nginx -t

# 重新加载
sudo nginx -s reload
```

### 问题 3: API 返回错误

**检查**:
```bash
# 查看 PM2 进程
pm2 status

# 查看应用日志
pm2 logs myapp

# 重启应用
pm2 restart myapp
```

---

## 📊 服务监控

### 实时日志
```bash
# 应用日志
pm2 logs myapp --lines 100

# Nginx 访问日志
sudo tail -f /var/log/nginx/access.log

# PostgreSQL 日志
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### 性能监控
```bash
# CPU 和内存
htop

# 磁盘使用
df -h

# 网络流量
iftop
```

---

## 🔐 安全建议

### 生产环境配置

1. **配置 HTTPS**
   ```bash
   # 安装 Certbot
   sudo yum install certbot python3-certbot-nginx -y
   
   # 获取证书
   sudo certbot --nginx -d your-domain.com
   ```

2. **限制数据库访问**
   - 只允许特定 IP 访问 5432 端口
   - 使用强密码

3. **定期备份**
   ```bash
   # 数据库备份
   pg_dump -U myapp_user myapp > backup-$(date +%Y%m%d).sql
   ```

4. **更新系统**
   ```bash
   sudo yum update -y
   ```

---

## 📞 需要帮助？

### 服务器信息
- **内网 IP**: 172.25.42.100
- **系统**: Alibaba Cloud Linux 3
- **位置**: 阿里云

### 文档
- **部署状态**: `/var/www/myapp/DEPLOYMENT_STATUS.md`
- **项目文档**: `/var/www/myapp/README.md`
- **GitHub**: https://github.com/knight-zmz/biostructure-db

---

**配置完成后即可通过公网访问！** 🦞
