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
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: '/home/admin/.pm2/logs/myapp-error.log',
    out_file: '/home/admin/.pm2/logs/myapp-out.log',
    merge_logs: true,
    time: true
  }]
};
