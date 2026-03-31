# Deploy — 应用部署

## 手动部署

```bash
cd /home/admin/biostructure-db
git pull origin main
npm install --production
pm2 restart myapp
curl http://localhost:3000/api/health
```

## GitHub Actions 自动部署

1. Push to `main`
2. Actions 自动触发
3. SSH 部署到服务器
4. PM2 重启

**Secrets**: `DEPLOY_SSH_KEY`, `DEPLOY_HOST`, `DEPLOY_USER`

## Systemd Unit 部署

```bash
sudo cp systemd/openclaw-agent.* /etc/systemd/system/
sudo cp systemd/openclaw-agent-test.timer /etc/systemd/system/
sudo systemctl daemon-reload
```

## Timer 切换

```bash
scripts/test-timer-toggle.sh [on|off|status]
```
