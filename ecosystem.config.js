require('dotenv').config();

module.exports = {
  apps: [{
    name: 'myapp',
    script: 'src/app.js',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '200M',
    restart_delay: 3000,
    max_restarts: 50,
    min_uptime: '10s',
    env: {
      NODE_ENV: process.env.NODE_ENV || 'production',
      PORT: process.env.PORT || 3000,
      DB_HOST: process.env.DB_HOST || '127.0.0.1',
      DB_PORT: process.env.DB_PORT || 5432,
      DB_NAME: process.env.DB_NAME || 'myapp',
      DB_USER: process.env.DB_USER || 'myapp_user',
      DB_PASSWORD: process.env.DB_PASSWORD,
      REDIS_HOST: process.env.REDIS_HOST || '127.0.0.1',
      REDIS_PORT: process.env.REDIS_PORT || 6379
    },
    error_file: process.env.PM2_ERROR_LOG || '/home/admin/.pm2/logs/myapp-error.log',
    out_file: process.env.PM2_OUT_LOG || '/home/admin/.pm2/logs/myapp-out.log',
    merge_logs: true,
    time: true
  }]
};
