# Logging — 日志管理

## PM2 日志

```bash
pm2 logs myapp
pm2 logs myapp --err
pm2 flush myapp
ls -la /home/admin/.pm2/logs/
```

## 系统日志

```bash
sudo journalctl -u postgresql -f
sudo journalctl -u redis -f
sudo journalctl -u openclaw-agent.service --since "1 hour ago"
```

## Nginx 日志

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Agent Loop 日志

```bash
tail -50 control/logs/agent-loop.log
```
