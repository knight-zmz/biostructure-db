# 🌐 域名配置指南

## 📋 当前状态

**公网 IP**: 101.200.53.98  
**当前访问**: http://101.200.53.98/  
**目标**: https://your-domain.com

---

## 1️⃣ 购买域名

### 推荐注册商

| 注册商 | 网址 | 特点 |
|--------|------|------|
| **阿里云** | https://wanwang.aliyun.com | 国内首选，备案方便 |
| **腾讯云** | https://cloud.tencent.com/domain | 价格实惠 |
| **Namecheap** | https://namecheap.com | 国际品牌，隐私保护 |
| **GoDaddy** | https://godaddy.com | 全球最大 |

### 推荐域名

**首选 (.com/.cn):**
```
biostructure.cn      ¥65/年
pdb-cloud.com        ¥60/年
biopro.cn            ¥65/年
structuredb.cn       ¥65/年
```

**备选 (.io/.tech):**
```
biodb.io             ¥200/年
structure.tech       ¥80/年
protein.io           ¥200/年
```

**建议**: 优先选择 `.cn` 或 `.com`，简短易记

---

## 2️⃣ DNS 解析配置

### 阿里云 DNS 配置

**步骤:**
1. 登录阿里云控制台
2. 进入 **域名解析 DNS**
3. 点击你的域名
4. 添加解析记录

**添加 A 记录:**
```
记录类型：A
主机记录：@
记录值：101.200.53.98
TTL: 10 分钟
```

**添加 www 记录:**
```
记录类型：CNAME
主机记录：www
记录值：your-domain.com
TTL: 10 分钟
```

### 腾讯云 DNS 配置

**步骤:**
1. 登录腾讯云控制台
2. 进入 **DNS 解析**
3. 点击你的域名
4. 添加记录

**配置同上**

---

## 3️⃣ 验证解析

### 等待生效
DNS 解析通常需要 5-30 分钟生效

### 测试方法

**方法 1: ping 测试**
```bash
ping your-domain.com
# 应该返回：101.200.53.98
```

**方法 2: nslookup**
```bash
nslookup your-domain.com
# 应该返回：101.200.53.98
```

**方法 3: 浏览器访问**
```
http://your-domain.com
```

---

## 4️⃣ 配置 HTTPS

### 告诉我域名后，我会自动:

1. **安装 Certbot**
   ```bash
   yum install certbot python3-certbot-nginx -y
   ```

2. **申请证书**
   ```bash
   certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

3. **配置自动续期**
   ```bash
   certbot renew --dry-run
   ```

4. **验证 HTTPS**
   ```
   https://your-domain.com
   ```

### 证书信息
- **类型**: Let's Encrypt (免费)
- **有效期**: 90 天
- **自动续期**: 每 60 天自动续期
- **成本**: ¥0

---

## 5️⃣ 配置完成后

### 访问地址变更

**之前:**
```
http://101.200.53.98/
```

**之后:**
```
https://your-domain.com
https://www.your-domain.com
```

### API 地址变更

**之前:**
```
http://101.200.53.98/api/stats
```

**之后:**
```
https://your-domain.com/api/stats
```

---

## 6️⃣ 备案 (可选)

### 如果域名在国内注册

**需要备案:**
- 使用国内服务器
- 面向国内用户访问

**备案流程:**
1. 登录阿里云备案系统
2. 提交备案申请
3. 等待审核 (7-20 天)
4. 获得备案号

**不需要备案:**
- 使用国外服务器
- 仅内部使用

---

## 📊 配置检查清单

### 购买前
- [ ] 选择域名
- [ ] 检查可用性
- [ ] 完成支付

### 购买后
- [ ] 添加 DNS 解析 (A 记录)
- [ ] 添加 www 解析 (CNAME)
- [ ] 等待 DNS 生效 (5-30 分钟)
- [ ] 测试 ping 解析
- [ ] 告诉我域名

### 配置 HTTPS
- [ ] 安装 Certbot
- [ ] 申请证书
- [ ] 配置 Nginx
- [ ] 测试 HTTPS 访问
- [ ] 配置自动续期

### 完成后
- [ ] 更新 GitHub 仓库
- [ ] 更新文档
- [ ] 通知用户

---

## 🎯 快速开始

### 最简单的流程

**1. 购买域名 (5 分钟)**
```
访问：https://wanwang.aliyun.com/domain
搜索：biostructure
购买：biostructure.cn (¥65/年)
```

**2. 配置 DNS (5 分钟)**
```
登录阿里云控制台
进入域名解析
添加 A 记录：@ → 101.200.53.98
```

**3. 告诉我域名**
```
在对话中告诉我你的域名
我会自动配置 HTTPS
```

**4. 完成!**
```
等待 10 分钟 DNS 生效
访问：https://your-domain.com
```

---

## 📞 需要帮助？

**常见问题:**

**Q: DNS 多久生效？**
A: 通常 5-30 分钟，最长 24 小时

**Q: 证书多久续期？**
A: 每 90 天自动续期

**Q: 需要备案吗？**
A: 国内服务器需要，国外不需要

**Q: 多个域名怎么办？**
A: 可以配置多个域名指向同一个 IP

---

**准备好域名后告诉我，我会立即配置 HTTPS！** 🦞
