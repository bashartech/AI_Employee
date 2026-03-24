module.exports = {
  apps: [
    {
      name: 'orchestrator',
      script: 'python3',
      args: 'engine/orchestrator.py',
      cwd: '/home/AI_Employee',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        PATH: '/home/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      error_file: '/home/AI_Employee/Logs/orchestrator.err',
      out_file: '/home/AI_Employee/Logs/orchestrator.out',
      log_file: '/home/AI_Employee/Logs/orchestrator.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'execute-approved',
      script: 'python3',
      args: 'execute_approved.py',
      cwd: '/home/AI_Employee',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        PATH: '/home/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      error_file: '/home/AI_Employee/Logs/execute_approved.err',
      out_file: '/home/AI_Employee/Logs/execute_approved.out',
      log_file: '/home/AI_Employee/Logs/execute_approved.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'gmail-watcher',
      script: 'python3',
      args: 'gmail_watcher.py',
      cwd: '/home/AI_Employee',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        PATH: '/home/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      error_file: '/home/AI_Employee/Logs/gmail_watcher.err',
      out_file: '/home/AI_Employee/Logs/gmail_watcher.out',
      log_file: '/home/AI_Employee/Logs/gmail_watcher.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'dashboard',
      script: 'python3',
      args: 'dashboard/app.py',
      cwd: '/home/AI_Employee',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        PORT: '5000',
        PATH: '/home/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      error_file: '/home/AI_Employee/Logs/dashboard.err',
      out_file: '/home/AI_Employee/Logs/dashboard.out',
      log_file: '/home/AI_Employee/Logs/dashboard.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};
