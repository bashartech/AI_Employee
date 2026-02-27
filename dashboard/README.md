# AI Employee Vault - Enhanced Dashboard

## 🎨 Enhanced Features (v2.0)

### New Features Added:
- ✅ **Real-time System Monitoring** - CPU, Memory, Disk usage with live updates
- ✅ **Interactive Charts** - Activity timeline and task distribution charts using Chart.js
- ✅ **Live Activity Feed** - Real-time updates of system activities
- ✅ **Watcher Status Indicators** - Visual status for all watchers (Gmail, WhatsApp, LinkedIn, Orchestrator)
- ✅ **Enhanced Task Management** - Quick approve/reject with modal dialogs
- ✅ **Analytics Dashboard** - Hourly and daily task completion analytics
- ✅ **Professional Animations** - Smooth transitions, pulse effects, and loading states
- ✅ **Responsive Design** - Works on desktop, tablet, and mobile
- ✅ **Dark Theme** - Professional terminal-style dark theme
- ✅ **Quick Actions** - Refresh, download logs, settings buttons

### Visual Enhancements:
- 🎯 Modern card-based layout
- 📊 Real-time progress bars with animations
- 🌈 Color-coded task types (Email, WhatsApp, LinkedIn)
- ✨ Glow effects and smooth transitions
- 📈 Interactive charts with Chart.js
- 🔄 Auto-refresh every 30 seconds
- 💫 Pulse indicators for active components

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd dashboard
pip install -r requirements.txt
```

### 2. Start the Dashboard

```bash
python app.py
```

### 3. Access Dashboard

Open your browser and navigate to:
```
http://localhost:5000
```

## 📊 Dashboard Sections

### Left Sidebar
- **Logo & Branding** - AI Employee Vault v2.0
- **Autonomy Level** - Current automation mode with progress indicator
- **Memory Banks** - Interactive cards showing task counts
- **Workflow Pipeline** - Visual pipeline with active stage indicators
- **Active Skills** - Animated progress bars for each skill type
- **System Resources** - Real-time CPU, Memory, Disk monitoring with uptime

### Center Panel
- **Header** - System time and operational status
- **Quick Stats Cards** - Today's tasks, success rate, weekly stats, total processed
- **Activity Chart** - 24-hour task completion timeline (line chart)
- **Distribution Chart** - Task type breakdown (doughnut chart)
- **Task Lists** - Tabbed interface for all task folders

### Right Sidebar
- **Watcher Status** - Real-time status with online/offline indicators
- **Live Activity Feed** - Scrolling feed of recent activities
- **Quick Actions** - Refresh, download logs, settings buttons

## 🎯 API Endpoints

### Overview & Statistics
- `GET /api/overview` - Complete dashboard statistics
- `GET /api/system/metrics` - System resource usage (CPU, Memory, Disk)
- `GET /api/activity/recent` - Recent activity logs (last 50)

### Analytics
- `GET /api/analytics/hourly` - Hourly task completion (last 24 hours)
- `GET /api/analytics/daily` - Daily task breakdown (last 7 days)

### Task Management
- `GET /api/tasks/<folder>` - Get tasks from specific folder
- `GET /api/task/<filename>` - Get detailed task information
- `POST /api/task/approve` - Approve task (move to Approved)
- `POST /api/task/reject` - Reject task (move to Rejected)
- `POST /api/task/move` - Move task between folders
- `POST /api/task/edit` - Edit task content

### Utilities
- `GET /api/logs/download` - Download activity logs as text file

## 🎨 Customization

### Colors
Edit `static/css/style.css` and modify CSS variables:
```css
:root {
    --cyan: #00D4FF;      /* Primary accent */
    --blue: #1E90FF;      /* Secondary accent */
    --green: #00FF88;     /* Success color */
    --red: #FF4444;       /* Error color */
    --yellow: #FFD700;    /* Warning color */
    --purple: #9D4EDD;    /* Info color */
}
```

### Refresh Intervals
Edit `static/js/dashboard.js`:
```javascript
// Dashboard refresh (default: 30 seconds)
refreshInterval = setInterval(refreshDashboard, 30000);

// Activity feed (default: 10 seconds)
activityInterval = setInterval(loadRecentActivity, 10000);

// System metrics (default: 5 seconds)
systemMetricsInterval = setInterval(loadSystemMetrics, 5000);
```

### Port Configuration
Edit `app.py`:
```python
# Change port from 5000 to 8080
app.run(debug=True, host='0.0.0.0', port=8080)
```

## 🔧 Troubleshooting

### Charts not showing?
Make sure Chart.js CDN is accessible:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

### CORS errors?
Flask-CORS is enabled by default. If issues persist:
```bash
pip install flask-cors
```

### System metrics not updating?
Ensure `psutil` is installed:
```bash
pip install psutil
```

### Port already in use?
Change the port in `app.py` or kill the process:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

## 📱 Responsive Design

### Professional Multi-Device Support:
The dashboard is fully responsive and optimized for all screen sizes with smooth transitions and touch-friendly interactions.

### Device Breakpoints:
- **Large Desktop (1600px+)**: Full 3-column layout with all features visible
- **Desktop (1200px-1400px)**: Narrower sidebars, 2-column stats grid
- **Laptop (992px-1200px)**: Compact sidebars, single-column charts
- **Tablet Landscape (768px-992px)**: Left sidebar + center content, right sidebar hidden
- **Tablet Portrait (600px-768px)**: Center content only, both sidebars hidden
- **Mobile (480px-600px)**: Single column, compact spacing, optimized font sizes
- **Small Mobile (320px-480px)**: Ultra-compact layout for small screens

### Responsive Features:
- **Flexible Grid Layout**: Uses CSS Grid with minmax() for smooth scaling
- **Touch-Friendly**: All buttons meet 44px minimum tap target size
- **Text Wrapping**: Proper word-wrap and overflow handling on all text elements
- **Smooth Scrolling**: Hardware-accelerated scrolling with -webkit-overflow-scrolling
- **Auto-Fit Grids**: Stats and charts automatically adjust column count
- **Hidden Sidebars**: Sidebars hide on smaller screens to maximize content space
- **Optimized Typography**: Font sizes scale appropriately for each breakpoint
- **Touch Gestures**: Swipeable tabs, scrollable sections with momentum
- **No Horizontal Scroll**: All content properly constrained within viewport
- **Adaptive Charts**: Chart heights adjust for optimal viewing on each device

### Mobile Optimizations:
- Touch-friendly buttons with proper tap targets (44px minimum)
- Swipeable tab navigation
- Optimized modal dialogs (95% width on mobile, 100% on small screens)
- Reduced padding and spacing for compact layouts
- Larger touch areas for all interactive elements
- Disabled text selection on buttons (-webkit-tap-highlight-color: transparent)
- Smooth momentum scrolling on iOS devices

## 🎯 Performance

### Optimization Features:
- **Lazy Loading**: Tasks loaded on demand
- **Debounced Updates**: Prevents excessive API calls
- **Efficient Rendering**: Only updates changed elements
- **Cached Data**: Reduces server load
- **Smooth Animations**: Hardware-accelerated CSS

### Resource Usage:
- **Memory**: ~50MB (typical)
- **CPU**: <5% (idle), ~10% (active)
- **Network**: ~1KB/s (polling)

## 🔐 Security Notes

### Default Configuration:
- Runs on `localhost` only
- No authentication required (local use)
- CORS enabled for API access

### Production Deployment:
1. **Add Authentication**: Implement login system
2. **Use HTTPS**: Configure SSL certificates
3. **Rate Limiting**: Prevent API abuse
4. **Input Validation**: Sanitize all inputs
5. **Environment Variables**: Store secrets securely

### Example: Add Basic Auth
```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == 'admin' and password == 'secret':
        return username

@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')
```

## 🚀 Cloud Deployment (Platinum Tier)

### Deploy on Oracle Cloud Free Tier:

1. **Setup VM** (from Platinum guide)
2. **Install Dependencies**:
```bash
cd ~/ai-employee-cloud/dashboard
pip install -r requirements.txt
```

3. **Create Systemd Service**:
```bash
sudo nano /etc/systemd/system/dashboard.service
```

```ini
[Unit]
Description=AI Employee Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-employee-cloud/dashboard
Environment="PATH=/home/ubuntu/ai-employee-cloud/venv/bin"
ExecStart=/home/ubuntu/ai-employee-cloud/venv/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Enable and Start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable dashboard
sudo systemctl start dashboard
```

5. **Configure Nginx** (optional):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. **Access Dashboard**:
```
http://<PUBLIC_IP>:5000
```

## 📊 Analytics Features

### Activity Chart
- **Type**: Line chart
- **Data**: Hourly task completion (last 24 hours)
- **Updates**: Real-time with smooth animations
- **Interaction**: Hover to see exact counts

### Distribution Chart
- **Type**: Doughnut chart
- **Data**: Task breakdown by type (Email, WhatsApp, LinkedIn, Other)
- **Updates**: Real-time
- **Interaction**: Click legend to toggle types

### Future Analytics:
- Weekly/Monthly trends
- Success rate over time
- Average response time
- Peak activity hours
- Task type predictions

## 🎓 Usage Tips

### Best Practices:
1. **Keep Dashboard Open**: Monitor in real-time while working
2. **Check Pending Regularly**: Avoid approval backlogs
3. **Review Before Approving**: Always read drafted responses
4. **Monitor System Resources**: Ensure optimal performance
5. **Download Logs Periodically**: Keep audit trail

### Keyboard Shortcuts:
- `Esc` - Close modal
- `Ctrl+R` - Refresh page
- `F12` - Open developer tools

### Workflow Integration:
1. Monitor dashboard for new tasks
2. Review in Pending Approval
3. Approve/reject from dashboard
4. Verify completion in activity feed

## 🐛 Known Issues

### Windows-Specific:
- Watcher detection may be approximate
- Emoji rendering in some terminals
- File path handling with spaces

### Solutions:
- Use forward slashes in paths
- Ensure UTF-8 encoding
- Run as administrator if needed

## 📈 Roadmap

### v2.1 (Planned):
- [ ] WebSocket support for real-time updates
- [ ] Task editing from dashboard
- [ ] Bulk operations (approve/reject multiple)
- [ ] Advanced filtering and search
- [ ] Export reports (CSV, PDF)

### v2.2 (Future):
- [ ] Email notifications
- [ ] Slack/Discord integration
- [ ] Custom dashboards
- [ ] Role-based access control
- [ ] API rate limiting

## 📞 Support

### Getting Help:
1. Check this README
2. Review browser console (F12)
3. Check Flask terminal output
4. Verify folder structure
5. Test API endpoints manually

### Common Solutions:
- **Restart Flask**: `Ctrl+C` then `python app.py`
- **Clear Browser Cache**: `Ctrl+Shift+Delete`
- **Reinstall Dependencies**: `pip install -r requirements.txt --force-reinstall`

## 📝 Version History

- **v2.0** (2026-02-27): Enhanced dashboard with charts, animations, system monitoring
- **v1.0** (2026-02-16): Initial release with basic task management

---

**🚀 Ready for Platinum Tier deployment!**

This enhanced dashboard provides professional monitoring and management for your AI Employee Vault automation system, suitable for both local development and cloud production environments.

## Features

### 📊 Real-Time Monitoring
- **Live task counts** across all folders
- **Watcher status** - See which automation watchers are running
- **Auto-refresh** every 30 seconds
- **Task breakdown** by type (WhatsApp, Email, LinkedIn)

### 📥 Task Management
- **Needs Action** - View incoming tasks requiring processing
- **Pending Approval** - Review AI-generated responses
- **Approved** - See tasks ready for execution
- **Recent History** - Track completed tasks

### ⚡ Interactive Actions
- **View task details** - Click any task to see full content
- **Approve/Reject** - One-click approval from dashboard
- **Real-time updates** - Changes reflect immediately
- **Priority indicators** - High-priority tasks highlighted

### 🎨 User Interface
- **Clean, modern design** with color-coded task types
- **Responsive layout** - Works on desktop and mobile
- **Modal dialogs** - View full task details without leaving page
- **Toast notifications** - Instant feedback on actions

## Quick Start

### 1. Start the Dashboard

**Option A: Double-click the batch file**
```
start_dashboard.bat
```

**Option B: Run manually**
```bash
cd dashboard
python app.py
```

### 2. Open in Browser

Navigate to: **http://localhost:5000**

The dashboard will automatically load and start monitoring your tasks.

## Dashboard Sections

### Watcher Status
Shows which automation watchers are currently running:
- 📱 **WhatsApp** - `whatsapp_watcher_node.js`
- 📧 **Gmail** - `gmail_watcher.py`
- 💼 **LinkedIn** - `engine/watcher_linkedin.py`

**Status Indicators:**
- ✓ Running (Green) - Watcher is active
- ✗ Stopped (Red) - Watcher is not running

### Overview Cards

**Needs Action** (Yellow)
- Total tasks requiring processing
- Breakdown by platform

**Pending Approval** (Blue)
- AI-generated responses awaiting review
- Breakdown by platform

**Approved** (Green)
- Tasks ready to execute
- Breakdown by platform

**Done Today** (Purple)
- Tasks completed today
- Total completed tasks

### Task Lists

Each section shows:
- **Task type** (WhatsApp/Email/LinkedIn)
- **Priority** (High priority flagged with 🔴)
- **Preview** (From/To/Subject)
- **Action buttons** (View/Approve/Reject)

## Using the Dashboard

### Viewing Task Details

1. Click **👁️ View** button on any task
2. Modal opens with full task content
3. See original message and drafted response
4. Close modal or take action

### Approving Tasks

**From Task List:**
1. Click **✓ Approve** button
2. Confirm approval
3. Task moves to Approved folder
4. Dashboard refreshes automatically

**From Modal:**
1. Open task details
2. Click **✓ Approve** in modal footer
3. Task approved and modal closes

### Rejecting Tasks

**From Task List:**
1. Click **✗ Reject** button
2. Confirm rejection
3. Task moves to Rejected folder
4. Dashboard refreshes automatically

**From Modal:**
1. Open task details
2. Click **✗ Reject** in modal footer
3. Task rejected and modal closes

### Manual Refresh

Click **🔄 Refresh** button in header to manually update all data.

**Auto-refresh:** Dashboard automatically refreshes every 30 seconds.

## Workflow Integration

### Complete Automation Flow

1. **Watcher detects message** → Creates task in `Needs Action/`
2. **Dashboard shows new task** → Yellow card count increases
3. **Process with Claude Code** → "Process tasks"
4. **Review in dashboard** → Task appears in `Pending Approval/`
5. **Approve from dashboard** → Click ✓ Approve button
6. **Execute with Claude Code** → "Execute approved actions"
7. **View in history** → Task appears in `Recent History`

### Using Dashboard with Claude Code

**Step 1: Monitor Dashboard**
- Keep dashboard open in browser
- Watch for new tasks in Needs Action

**Step 2: Process Tasks**
```
Tell Claude Code: "Process tasks"
```

**Step 3: Review in Dashboard**
- Check Pending Approval section
- Click View to see drafted responses
- Click Approve or Reject

**Step 4: Execute Approved**
```
Tell Claude Code: "Execute approved actions"
```

**Step 5: Verify Completion**
- Check Recent History section
- Verify task moved to Done

## Keyboard Shortcuts

- **Esc** - Close modal
- **Ctrl+R** - Refresh page (manual)

## Troubleshooting

### Dashboard won't start

**Error: "Address already in use"**
- Another process is using port 5000
- Solution: Close other Flask apps or change port in `app.py`

**Error: "Module not found"**
```bash
pip install flask pyyaml markdown2
```

### Tasks not showing

**Check folder structure:**
```
AI_Employee_Vault/
├── Needs Action/
├── Pending Approval/
├── Approved/
└── Done/
```

**Verify files exist:**
```bash
ls "Needs Action/"
ls "Pending Approval/"
```

### Watcher status always shows "Stopped"

**Note:** Watcher detection is approximate on Windows.

**To verify manually:**
```bash
# Check for Node.js (WhatsApp)
tasklist | findstr node.exe

# Check for Python (Gmail/LinkedIn)
tasklist | findstr python.exe
```

### Actions not working

**Check console for errors:**
- Press F12 in browser
- Check Console tab for JavaScript errors
- Check Network tab for failed API calls

**Verify Flask is running:**
- Terminal should show "Running on http://0.0.0.0:5000"
- No error messages in terminal

## API Endpoints

The dashboard uses these REST API endpoints:

- `GET /` - Dashboard HTML page
- `GET /api/overview` - Overview statistics
- `GET /api/tasks/<folder>` - Tasks from specific folder
- `GET /api/task/<filename>` - Task details
- `POST /api/task/approve` - Approve task
- `POST /api/task/reject` - Reject task
- `POST /api/task/move` - Move task between folders

## Customization

### Change Auto-Refresh Interval

Edit `dashboard/static/js/dashboard.js`:
```javascript
// Change from 30 seconds to 60 seconds
refreshInterval = setInterval(refreshDashboard, 60000);
```

### Change Port

Edit `dashboard/app.py`:
```python
# Change from 5000 to 8080
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Customize Colors

Edit `dashboard/static/css/style.css`:
```css
:root {
    --primary: #2563eb;  /* Change primary color */
    --success: #10b981;  /* Change success color */
    /* ... */
}
```

## Security Notes

- Dashboard runs on **localhost only** by default
- No authentication required (local use)
- For remote access, add authentication
- Don't expose to public internet without security

## Performance

- **Lightweight** - Minimal resource usage
- **Fast** - Instant task loading
- **Scalable** - Handles hundreds of tasks
- **Efficient** - Only loads visible data

## Browser Compatibility

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ⚠️ Internet Explorer (Not supported)

## Mobile Support

Dashboard is fully responsive and works on:
- 📱 Smartphones
- 📱 Tablets
- 💻 Laptops
- 🖥️ Desktops

## Tips & Best Practices

1. **Keep dashboard open** while working with automation
2. **Check Pending Approval regularly** to avoid backlogs
3. **Use priority indicators** to handle urgent tasks first
4. **Review task details** before approving
5. **Monitor watcher status** to ensure automation is running
6. **Check Recent History** to verify completions

## Future Enhancements

Potential features for future versions:
- [ ] Real-time WebSocket updates
- [ ] Task editing from dashboard
- [ ] Bulk approve/reject
- [ ] Advanced filtering and search
- [ ] Analytics and charts
- [ ] Email notifications
- [ ] Dark mode toggle
- [ ] Task scheduling
- [ ] Export to CSV/PDF

## Support

For issues or questions:
1. Check this README
2. Review console logs (F12 in browser)
3. Check Flask terminal output
4. Verify folder structure and file permissions

## Version

**Version:** 1.0.0
**Created:** 2026-02-16
**Last Updated:** 2026-02-16

---

**Enjoy your AI Employee Vault Dashboard! 🚀**
