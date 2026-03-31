# Service Management — 服务管理

## PostgreSQL

```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
sudo systemctl stop postgresql
sudo systemctl restart postgresql
psql -U myapp_user -d myapp -c "SELECT 1"
psql -U myapp_user -d myapp -c "\dt"
```

## Redis

```bash
sudo systemctl status redis
sudo systemctl start redis
sudo systemctl stop redis
sudo systemctl restart redis
redis-cli ping
redis-cli keys '*'
redis-cli flushall
```

## PM2

```bash
pm2 status
pm2 start ecosystem.config.js
pm2 restart myapp
pm2 stop myapp
pm2 logs myapp
pm2 monit
pm2 save
pm2 startup
```
