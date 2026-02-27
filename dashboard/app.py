"""
AI Employee Vault - Interactive Dashboard
Flask web application for managing automation tasks
Enhanced for Platinum Tier with real-time monitoring
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from pathlib import Path
import yaml
import re
from datetime import datetime, timedelta
import subprocess
import shutil
import psutil
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Paths
BASE_DIR = Path(__file__).parent.parent
NEEDS_ACTION = BASE_DIR / "Needs Action"
PENDING_APPROVAL = BASE_DIR / "Pending Approval"
APPROVED = BASE_DIR / "Approved"
DONE = BASE_DIR / "Done"
REJECTED = BASE_DIR / "Rejected"
SEND_QUEUE = BASE_DIR / "Send_Queue"
DASHBOARD_MD = BASE_DIR / "Dashboard.md"
LOGS_DIR = BASE_DIR / "logs"

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)


def parse_markdown_file(filepath):
    """Parse markdown file with YAML frontmatter"""
    try:
        content = filepath.read_text(encoding='utf-8')

        # Extract YAML frontmatter if exists
        frontmatter = {}
        body = content

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                except:
                    pass

        # Determine task type from filename
        filename = filepath.name
        task_type = 'unknown'
        if filename.startswith('WHATSAPP'):
            task_type = 'whatsapp'
        elif filename.startswith('EMAIL'):
            task_type = 'email'
        elif filename.startswith('LINKEDIN'):
            task_type = 'linkedin'
        elif filename.startswith('APPROVAL_send_whatsapp'):
            task_type = 'whatsapp_approval'
        elif filename.startswith('APPROVAL_send_email'):
            task_type = 'email_approval'
        elif filename.startswith('LINKEDIN_POST'):
            task_type = 'linkedin_post'

        # Extract key information from body
        lines = body.split('\n')
        title = lines[0].strip('# ') if lines else filename

        # Extract metadata from markdown
        metadata = {
            'from': None,
            'to': None,
            'subject': None,
            'priority': 'normal',
            'received': None,
        }

        for line in lines:
            if line.startswith('**From:**'):
                metadata['from'] = line.replace('**From:**', '').strip()
            elif line.startswith('**To:**'):
                metadata['to'] = line.replace('**To:**', '').strip()
            elif line.startswith('**Subject:**'):
                metadata['subject'] = line.replace('**Subject:**', '').strip()
            elif line.startswith('**Priority:**'):
                priority_text = line.replace('**Priority:**', '').strip()
                if '🔴' in priority_text or 'HIGH' in priority_text:
                    metadata['priority'] = 'high'
            elif line.startswith('**Received:**'):
                metadata['received'] = line.replace('**Received:**', '').strip()

        return {
            'filename': filename,
            'filepath': str(filepath),
            'type': task_type,
            'title': title,
            'frontmatter': frontmatter,
            'body': body,
            'metadata': metadata,
            'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
        }
    except Exception as e:
        return {
            'filename': filepath.name,
            'filepath': str(filepath),
            'type': 'error',
            'title': filepath.name,
            'error': str(e)
        }


def get_tasks_from_folder(folder_path):
    """Get all tasks from a folder"""
    tasks = []
    if folder_path.exists():
        for file in folder_path.glob('*.md'):
            if file.name != 'Dashboard.md':
                task = parse_markdown_file(file)
                tasks.append(task)

    # Sort by modified time (newest first)
    tasks.sort(key=lambda x: x.get('modified', ''), reverse=True)
    return tasks


def check_watcher_status():
    """Check which watchers are currently running"""
    status = {
        'whatsapp': False,
        'gmail': False,
        'linkedin': False
    }

    try:
        # Check for running processes (Windows)
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        output = result.stdout.lower()

        # Check for Node.js processes (WhatsApp watcher)
        if 'node.exe' in output:
            # Try to check if whatsapp_watcher_node.js is running
            status['whatsapp'] = True

        # Check for Python processes (Gmail and LinkedIn watchers)
        if 'python.exe' in output:
            # Assume watchers might be running
            status['gmail'] = True
            status['linkedin'] = True

    except Exception as e:
        print(f"Error checking watcher status: {e}")

    return status


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/overview')
def api_overview():
    """Get overview statistics with enhanced metrics"""
    needs_action = get_tasks_from_folder(NEEDS_ACTION)
    pending_approval = get_tasks_from_folder(PENDING_APPROVAL)
    approved = get_tasks_from_folder(APPROVED)
    done = get_tasks_from_folder(DONE)

    # Count by type
    def count_by_type(tasks):
        counts = {'whatsapp': 0, 'email': 0, 'linkedin': 0, 'other': 0}
        for task in tasks:
            task_type = task['type']
            if 'whatsapp' in task_type:
                counts['whatsapp'] += 1
            elif 'email' in task_type:
                counts['email'] += 1
            elif 'linkedin' in task_type:
                counts['linkedin'] += 1
            else:
                counts['other'] += 1
        return counts

    # Get today's completed tasks
    today = datetime.now().date()
    done_today = [t for t in done if datetime.fromisoformat(t['modified']).date() == today]

    # Get this week's completed tasks
    week_ago = datetime.now() - timedelta(days=7)
    done_this_week = [t for t in done if datetime.fromisoformat(t['modified']) > week_ago]

    # Calculate success rate (approved vs rejected)
    rejected = get_tasks_from_folder(REJECTED)
    total_processed = len(done) + len(rejected)
    success_rate = (len(done) / total_processed * 100) if total_processed > 0 else 100

    return jsonify({
        'needs_action': {
            'total': len(needs_action),
            'by_type': count_by_type(needs_action)
        },
        'pending_approval': {
            'total': len(pending_approval),
            'by_type': count_by_type(pending_approval)
        },
        'approved': {
            'total': len(approved),
            'by_type': count_by_type(approved)
        },
        'done_today': len(done_today),
        'done_this_week': len(done_this_week),
        'done_total': len(done),
        'rejected_total': len(rejected),
        'success_rate': round(success_rate, 1),
        'watchers': check_watcher_status(),
        'system': get_system_metrics()
    })


@app.route('/api/system/metrics')
def api_system_metrics():
    """Get real-time system metrics"""
    return jsonify(get_system_metrics())


def get_system_metrics():
    """Get system resource usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(BASE_DIR))

        return {
            'cpu': {
                'percent': round(cpu_percent, 1),
                'cores': psutil.cpu_count()
            },
            'memory': {
                'percent': round(memory.percent, 1),
                'used_gb': round(memory.used / (1024**3), 2),
                'total_gb': round(memory.total / (1024**3), 2)
            },
            'disk': {
                'percent': round(disk.percent, 1),
                'used_gb': round(disk.used / (1024**3), 2),
                'total_gb': round(disk.total / (1024**3), 2)
            },
            'uptime': get_system_uptime()
        }
    except Exception as e:
        return {
            'cpu': {'percent': 0, 'cores': 0},
            'memory': {'percent': 0, 'used_gb': 0, 'total_gb': 0},
            'disk': {'percent': 0, 'used_gb': 0, 'total_gb': 0},
            'uptime': 'Unknown'
        }


def get_system_uptime():
    """Get system uptime"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        return f"{days}d {hours}h {minutes}m"
    except:
        return "Unknown"


@app.route('/api/activity/recent')
def api_recent_activity():
    """Get recent activity logs"""
    activities = []

    # Get recent files from all folders
    folders = [
        (NEEDS_ACTION, 'needs_action', 'New task detected'),
        (PENDING_APPROVAL, 'pending_approval', 'Awaiting approval'),
        (APPROVED, 'approved', 'Task approved'),
        (DONE, 'done', 'Task completed'),
        (REJECTED, 'rejected', 'Task rejected')
    ]

    for folder, folder_type, action in folders:
        if folder.exists():
            for file in folder.glob('*.md'):
                if file.name != 'Dashboard.md':
                    stat = file.stat()
                    activities.append({
                        'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'type': folder_type,
                        'action': action,
                        'filename': file.name,
                        'size': stat.st_size
                    })

    # Sort by timestamp (newest first)
    activities.sort(key=lambda x: x['timestamp'], reverse=True)

    # Return last 50 activities
    return jsonify({'activities': activities[:50]})


@app.route('/api/analytics/hourly')
def api_hourly_analytics():
    """Get hourly task completion analytics"""
    done_tasks = get_tasks_from_folder(DONE)

    # Group by hour for last 24 hours
    hourly_data = {}
    now = datetime.now()

    for i in range(24):
        hour = (now - timedelta(hours=i)).strftime('%H:00')
        hourly_data[hour] = 0

    for task in done_tasks:
        task_time = datetime.fromisoformat(task['modified'])
        if (now - task_time).total_seconds() < 86400:  # Last 24 hours
            hour = task_time.strftime('%H:00')
            if hour in hourly_data:
                hourly_data[hour] += 1

    # Convert to array format
    hours = sorted(hourly_data.keys(), reverse=True)
    data = [hourly_data[h] for h in hours]

    return jsonify({
        'labels': hours,
        'data': data
    })


@app.route('/api/analytics/daily')
def api_daily_analytics():
    """Get daily task completion analytics for last 7 days"""
    done_tasks = get_tasks_from_folder(DONE)

    # Group by day for last 7 days
    daily_data = {}
    now = datetime.now()

    for i in range(7):
        day = (now - timedelta(days=i)).strftime('%Y-%m-%d')
        daily_data[day] = {'email': 0, 'whatsapp': 0, 'linkedin': 0, 'other': 0}

    for task in done_tasks:
        task_time = datetime.fromisoformat(task['modified'])
        if (now - task_time).total_seconds() < 604800:  # Last 7 days
            day = task_time.strftime('%Y-%m-%d')
            if day in daily_data:
                task_type = task['type']
                if 'email' in task_type:
                    daily_data[day]['email'] += 1
                elif 'whatsapp' in task_type:
                    daily_data[day]['whatsapp'] += 1
                elif 'linkedin' in task_type:
                    daily_data[day]['linkedin'] += 1
                else:
                    daily_data[day]['other'] += 1

    # Convert to array format
    days = sorted(daily_data.keys())

    return jsonify({
        'labels': days,
        'email': [daily_data[d]['email'] for d in days],
        'whatsapp': [daily_data[d]['whatsapp'] for d in days],
        'linkedin': [daily_data[d]['linkedin'] for d in days],
        'other': [daily_data[d]['other'] for d in days]
    })


@app.route('/api/task/edit', methods=['POST'])
def api_edit_task():
    """Edit task content"""
    data = request.json
    filename = data.get('filename')
    content = data.get('content')
    folder = data.get('folder', 'pending-approval')

    folder_map = {
        'needs-action': NEEDS_ACTION,
        'pending-approval': PENDING_APPROVAL,
        'approved': APPROVED,
        'done': DONE,
        'rejected': REJECTED
    }

    file_path = folder_map.get(folder) / filename

    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404

    try:
        file_path.write_text(content, encoding='utf-8')
        return jsonify({'success': True, 'message': 'Task updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/logs/download')
def api_download_logs():
    """Download system logs"""
    try:
        log_file = LOGS_DIR / f"dashboard_log_{datetime.now().strftime('%Y%m%d')}.txt"

        if not log_file.exists():
            # Create a log file with recent activities
            activities = api_recent_activity().get_json()['activities']
            log_content = "AI Employee Vault - Activity Log\n"
            log_content += f"Generated: {datetime.now().isoformat()}\n"
            log_content += "=" * 80 + "\n\n"

            for activity in activities:
                log_content += f"[{activity['timestamp']}] {activity['action']}: {activity['filename']}\n"

            log_file.write_text(log_content, encoding='utf-8')

        return send_file(log_file, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<folder>')
def api_tasks(folder):
    """Get tasks from specific folder"""
    folder_map = {
        'needs-action': NEEDS_ACTION,
        'pending-approval': PENDING_APPROVAL,
        'approved': APPROVED,
        'done': DONE,
        'rejected': REJECTED
    }

    folder_path = folder_map.get(folder)
    if not folder_path:
        return jsonify({'error': 'Invalid folder'}), 400

    tasks = get_tasks_from_folder(folder_path)
    return jsonify({'tasks': tasks})


@app.route('/api/task/<path:filename>')
def api_task_detail(filename):
    """Get detailed task information"""
    # Search in all folders
    folders = [NEEDS_ACTION, PENDING_APPROVAL, APPROVED, DONE, REJECTED]

    for folder in folders:
        filepath = folder / filename
        if filepath.exists():
            task = parse_markdown_file(filepath)
            return jsonify(task)

    return jsonify({'error': 'Task not found'}), 404


@app.route('/api/task/move', methods=['POST'])
def api_move_task():
    """Move task between folders"""
    data = request.json
    filename = data.get('filename')
    from_folder = data.get('from')
    to_folder = data.get('to')

    folder_map = {
        'needs-action': NEEDS_ACTION,
        'pending-approval': PENDING_APPROVAL,
        'approved': APPROVED,
        'done': DONE,
        'rejected': REJECTED
    }

    source_path = folder_map.get(from_folder) / filename
    dest_path = folder_map.get(to_folder) / filename

    if not source_path.exists():
        return jsonify({'error': 'Source file not found'}), 404

    try:
        shutil.move(str(source_path), str(dest_path))

        # Update Dashboard.md if moving to Done
        if to_folder == 'done':
            update_dashboard_completed(filename)

        return jsonify({'success': True, 'message': f'Moved to {to_folder}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/task/approve', methods=['POST'])
def api_approve_task():
    """Approve a task (move from Pending Approval to Approved)"""
    data = request.json
    filename = data.get('filename')

    source = PENDING_APPROVAL / filename
    dest = APPROVED / filename

    if not source.exists():
        return jsonify({'error': 'Task not found'}), 404

    try:
        shutil.move(str(source), str(dest))
        return jsonify({'success': True, 'message': 'Task approved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/task/reject', methods=['POST'])
def api_reject_task():
    """Reject a task (move from Pending Approval to Rejected)"""
    data = request.json
    filename = data.get('filename')

    source = PENDING_APPROVAL / filename
    dest = REJECTED / filename

    if not source.exists():
        return jsonify({'error': 'Task not found'}), 404

    try:
        shutil.move(str(source), str(dest))
        return jsonify({'success': True, 'message': 'Task rejected'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def update_dashboard_completed(filename):
    """Update Dashboard.md with completed task"""
    try:
        if DASHBOARD_MD.exists():
            content = DASHBOARD_MD.read_text(encoding='utf-8')
        else:
            content = "# AI Employee Dashboard\n\n## Pending Tasks\n- None\n\n## Completed Tasks\n"

        # Add new completed task
        today = datetime.now().strftime('%Y-%m-%d')
        new_entry = f"- ✅ {filename} (Completed: {today})\n"

        if "## Completed Tasks" in content:
            content = content.replace("## Completed Tasks\n", f"## Completed Tasks\n{new_entry}")
        else:
            content += f"\n## Completed Tasks\n{new_entry}"

        DASHBOARD_MD.write_text(content, encoding='utf-8')
    except Exception as e:
        print(f"Error updating dashboard: {e}")


if __name__ == '__main__':
    print("=" * 60)
    print("AI Employee Vault Dashboard")
    print("=" * 60)
    print(f"Dashboard URL: http://localhost:5000")
    print(f"Base Directory: {BASE_DIR}")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
