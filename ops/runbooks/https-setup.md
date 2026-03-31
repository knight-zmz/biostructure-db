# HTTPS Setup — 备案完成后接入

> ⏸️ 当前暂停（备案限制）

## 前置条件

- [ ] 备案完成
- [ ] 域名解析生效 (jlupdb.me → 101.200.53.98)
- [ ] 80 端口可公网访问

## Let's Encrypt

```bash
# certbot
sudo yum install -y certbot python3-certbot-nginx
sudo certbot --nginx -d jlupdb.me
sudo systemctl status certbot.timer

# 或 acme.sh
curl https://get.acme.sh | sh
acme.sh --register-account -m admin@jlupdb.me
acme.sh --issue -d jlupdb.me --webroot /usr/share/nginx/html
acme.sh --install-cert -d jlupdb.me \
  --key-file /etc/nginx/ssl/jlupdb.me.key \
  --fullchain-file /etc/nginx/ssl/jlupdb.me.pem \
  --reloadcmd "sudo systemctl reload nginx"
```

## Nginx 配置

```nginx
server {
    listen 80;
    server_name jlupdb.me;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name jlupdb.me;
    ssl_certificate /etc/nginx/ssl/jlupdb.me.pem;
    ssl_certificate_key /etc/nginx/ssl/jlupdb.me.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 验证

```bash
sudo nginx -t
sudo systemctl reload nginx
curl -I https://jlupdb.me
curl -I http://jlupdb.me  # should 301
```

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 403 | 80 被拦截 | 检查安全组 |
| DNS 失败 | 解析未生效 | 等待传播 |
| Nginx 失败 | 语法错误 | `nginx -t` |
| 443 不通 | 端口未开放 | 检查安全组 |
