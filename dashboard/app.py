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
from werkzeug.utils import secure_filename
import sys
# Add parent directory to path for engine imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine.logger import logger

app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = 'Inbox'

# Paths
BASE_DIR = Path(__file__).parent.parent
NEEDS_ACTION = BASE_DIR / "Needs Action"
PENDING_APPROVAL = BASE_DIR / "Pending Approval"
APPROVED = BASE_DIR / "Approved"
DONE = BASE_DIR / "Done"
REJECTED = BASE_DIR / "Rejected"
SEND_QUEUE = BASE_DIR / "Send_Queue"
INBOX = BASE_DIR / "Inbox"
DASHBOARD_MD = BASE_DIR / "Dashboard.md"
LOGS_DIR = BASE_DIR / "logs"

# Ensure folders exist
for folder in [INBOX, LOGS_DIR]:
    folder.mkdir(exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'md', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        elif filename.startswith('APPROVAL_facebook'):
            task_type = 'facebook_approval'
        elif filename.startswith('APPROVAL_twitter'):
            task_type = 'twitter_approval'
        elif filename.startswith('ODOO_LEAD'):
            task_type = 'odoo_lead'

        # Extract key information from body
        lines = body.split('\n')
        
        # For approval files, use filename as title for better display
        # Otherwise use first line of body
        if filename.startswith('APPROVAL_') or filename.startswith('ODOO_LEAD'):
            title = filename.replace('.md', '').replace('_', ' ')
        else:
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


@app.route('/api/upload', methods=['POST'])
def upload_to_inbox():
    """Upload file to Inbox folder"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Get message from form
            message = request.form.get('message', '')
            task_type = request.form.get('type', 'general')
            
            # Secure filename
            filename = secure_filename(file.filename)
            
            # Add timestamp to avoid overwrites
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_{timestamp}{ext}"
            
            # Save file to Inbox
            filepath = INBOX / new_filename
            file.save(str(filepath))
            
            # If message provided, create task file
            if message:
                task_filename = f"INBOX_{name}_{timestamp}.md"
                task_filepath = NEEDS_ACTION / task_filename
                
                task_content = f"""# Task from Inbox: {filename}

**Source:** Dashboard Upload
**Original File:** {filename}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Type:** {task_type}

## Content

{message}

## Suggested Actions

- [ ] Review the content
- [ ] Take appropriate action
- [ ] Mark as complete when done

## Notes

Add your notes here...
"""
                task_filepath.write_text(task_content, encoding='utf-8')
            
            return jsonify({
                'success': True,
                'message': f'File uploaded: {new_filename}',
                'filename': new_filename
            })
        else:
            return jsonify({'error': 'File type not allowed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-text', methods=['POST'])
def upload_text_to_inbox():
    """Create text file in Inbox from dashboard message"""
    try:
        data = request.json
        message = data.get('message', '')
        task_type = data.get('type', 'general')
        filename = data.get('filename', f'task_{datetime.now().strftime("%Y%m%d_%H%M%S")}')

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        # Create task file directly in Needs Action (skip Inbox)
        task_filename = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        task_filepath = NEEDS_ACTION / task_filename

        # Use YAML frontmatter format for proper detection
        task_content = f"""---
type: {task_type}
source: Dashboard
---

# Task from Dashboard

**Source:** Dashboard
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Type:** {task_type}

## Content

{message}

## Suggested Actions

- [ ] Review the content
- [ ] Take appropriate action
- [ ] Mark as complete when done
"""
        task_filepath.write_text(task_content, encoding='utf-8')

        return jsonify({
            'success': True,
            'message': f'Task created: {task_filename}',
            'filename': task_filename
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/facebook/post', methods=['POST'])
def facebook_post():
    """Create Facebook post task (goes through approval workflow) with optional image upload"""
    try:
        # Check if request is multipart/form-data (image upload) or JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # FormData request with image
            message = request.form.get('message', '')
            hashtags = request.form.get('hashtags', '')
            image = request.files.get('image')
        else:
            # JSON request (backward compatibility)
            data = request.get_json(force=True, silent=True) or {}
            message = data.get('message', '')
            hashtags = data.get('hashtags', '')
            image = None

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        # Save image if provided
        image_path = None
        if image and image.filename:
            upload_folder = BASE_DIR / "Post_Images"
            upload_folder.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_filename = f"facebook_{timestamp}_{image.filename}"
            image_path = upload_folder / image_filename
            image.save(str(image_path))
            logger.info(f"📷 Facebook image saved: {image_path}")

        # Create task file in Needs Action folder
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        task_filename = f"facebook_post_{timestamp}.md"
        task_filepath = NEEDS_ACTION / task_filename

        if image_path:
            task_content = f"""---
type: facebook
action: facebook_post
image_path: {image_path}
---

# Facebook Post Creation Request

**Source:** Dashboard
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Action:** Create Post
**Image:** {image_path.name}

## Content

{message}

## Hashtags

{hashtags}

## Action Required
Create Facebook post with above content and image after approval
"""
        else:
            task_content = f"""---
type: facebook
action: facebook_post
---

# Facebook Post Creation Request

**Source:** Dashboard
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Action:** Create Post

## Content

{message}

## Hashtags

{hashtags}

## Action Required
Create Facebook post with above content after approval
"""

        task_filepath.write_text(task_content, encoding='utf-8')

        return jsonify({
            'success': True,
            'message': 'Facebook task created! Awaiting approval in Needs Action folder.',
            'task_file': task_filename,
            'has_image': image_path is not None
        })

    except Exception as e:
        logger.error(f"Facebook task creation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/facebook/posts', methods=['GET'])
def facebook_get_posts():
    """Get recent Facebook posts"""
    try:
        from engine.facebook_manager import FacebookPageManager
        manager = FacebookPageManager()

        limit = request.args.get('limit', 10, type=int)
        result = manager.get_posts(limit=limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Facebook get posts error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/facebook/analytics', methods=['GET'])
def facebook_get_analytics():
    """Get Facebook page analytics"""
    try:
        from engine.facebook_manager import FacebookPageManager
        manager = FacebookPageManager()

        days = request.args.get('days', 7, type=int)
        
        # Get multiple metrics
        metrics = [
            'page_impressions',
            'page_reach',
            'page_engaged_users',
            'page_followers',
            'page_fans'
        ]
        
        result = manager.get_page_insights(metric=','.join(metrics), days=days)

        if result.get('success'):
            return jsonify(result)
        else:
            # Return the actual error message
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"Analytics failed: {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 500

    except Exception as e:
        logger.error(f"Facebook analytics error: {e}")
        return jsonify({'success': False, 'error': f'Analytics error: {str(e)}'}), 500


@app.route('/api/facebook/page-info', methods=['GET'])
def facebook_get_page_info():
    """Get Facebook page information"""
    try:
        from engine.facebook_manager import FacebookPageManager
        manager = FacebookPageManager()

        result = manager.get_page_info()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Facebook page info error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/facebook/comments', methods=['GET'])
def facebook_get_post_comments():
    """Get comments on a specific Facebook post"""
    try:
        from engine.facebook_manager import FacebookPageManager
        manager = FacebookPageManager()

        # Get parameters from query string (GET request - no JSON)
        post_id = request.args.get('post_id')
        limit = request.args.get('limit', 20, type=int)

        if not post_id:
            return jsonify({'success': False, 'error': 'Post ID required'}), 400

        # Get comments from Facebook
        result = manager.get_comments(post_id, limit=limit)

        # Return result
        return jsonify(result)

    except Exception as e:
        logger.error(f"Facebook comments error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== TWITTER ENDPOINTS ====================

@app.route('/api/twitter/post', methods=['POST'])
def twitter_post():
    """Create Twitter post task (goes through approval workflow) with optional image upload"""
    try:
        # Handle both JSON and FormData (for image uploads)
        if request.files and 'image' in request.files:
            # FormData request with image
            message = request.form.get('message', '')
            hashtags = request.form.get('hashtags', '')
            is_thread = request.form.get('is_thread', 'false').lower() == 'true'
            image = request.files.get('image')
        else:
            # JSON request (backward compatibility)
            data = request.json
            message = data.get('message', '')
            hashtags = data.get('hashtags', '')
            is_thread = data.get('is_thread', False)
            image = None

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        # Save image if provided
        image_path = None
        if image and image.filename:
            upload_folder = BASE_DIR / "Post_Images"
            upload_folder.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_filename = f"twitter_{timestamp}_{image.filename}"
            image_path = upload_folder / image_filename
            image.save(str(image_path))
            logger.info(f"📷 Image saved: {image_path}")

        # Create task file in Needs Action folder
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        task_filename = f"twitter_{'thread' if is_thread else 'post'}_{timestamp}.md"
        task_filepath = NEEDS_ACTION / task_filename

        if is_thread:
            if image_path:
                task_content = f"""---
type: twitter
action: twitter_thread
image_path: {image_path}
---

# Twitter Thread Creation Request

**Source:** Dashboard
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Action:** Create Thread
**Image:** {image_path.name}

## Content

{message}

## Hashtags

{hashtags}

## Action Required
Create Twitter thread with above content and image after approval
"""
            else:
                task_content = f"""---
type: twitter
action: twitter_thread
---

# Twitter Thread Creation Request

**Source:** Dashboard
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Action:** Create Thread

## Content

{message}

## Hashtags

{hashtags}

## Action Required
Create Twitter thread with above content after approval
"""
        else:
            if image_path:
                task_content = f"""---
type: twitter
action: twitter_post
image_path: {image_path}
---

# Twitter Post Creation Request

**Source:** Dashboard
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Action:** Create Post
**Image:** {image_path.name}

## Content

{message}

## Hashtags

{hashtags}

## Action Required
Create Twitter post with above content and image after approval
"""
            else:
                task_content = f"""---
type: twitter
action: twitter_post
---

# Twitter Post Creation Request

**Source:** Dashboard
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Action:** Create Post

## Content

{message}

## Hashtags

{hashtags}

## Action Required
Create Twitter post with above content after approval
"""

        task_filepath.write_text(task_content, encoding='utf-8')

        return jsonify({
            'success': True,
            'message': 'Twitter task created! Awaiting approval in Needs Action folder.',
            'task_file': task_filename,
            'has_image': image_path is not None
        })

    except Exception as e:
        logger.error(f"Twitter task creation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/twitter/schedule', methods=['POST'])
def schedule_twitter_post():
    """Schedule a Twitter post for later with optional image upload"""
    try:
        from scheduler.scheduler_db import init_db, add_scheduled_post

        # Handle both JSON and FormData (for image uploads)
        if request.files and 'image' in request.files:
            # FormData request with image
            content = request.form.get('content', '')
            hashtags = request.form.get('hashtags', '')
            scheduled_time_str = request.form.get('scheduled_time', '')
            is_thread = request.form.get('is_thread', 'false').lower() == 'true'
            image = request.files.get('image')
        else:
            # JSON request (backward compatibility)
            data = request.json
            content = data.get('content', '')
            hashtags = data.get('hashtags', '')
            scheduled_time_str = data.get('scheduled_time', '')
            is_thread = data.get('is_thread', False)
            image = None

        if not content or not scheduled_time_str:
            return jsonify({'error': 'Content and scheduled_time required'}), 400

        # Save image if provided
        image_path = None
        if image and image.filename:
            upload_folder = BASE_DIR / "Post_Images"
            upload_folder.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_filename = f"twitter_{timestamp}_{image.filename}"
            image_path = upload_folder / image_filename
            image.save(str(image_path))
            logger.info(f"📷 Scheduled image saved: {image_path}")

        # Initialize DB
        init_db()

        # Parse scheduled time
        scheduled_time = datetime.strptime(scheduled_time_str, '%Y-%m-%d %H:%M')

        # Check if time is in the future
        if scheduled_time <= datetime.now():
            return jsonify({'error': 'Scheduled time must be in the future'}), 400

        # Add to schedule (scheduler will enhance with Claude at scheduled time)
        post_id = add_scheduled_post(
            platform='twitter',
            content=content,  # Raw content - scheduler will enhance with Claude
            scheduled_time=scheduled_time,
            hashtags=hashtags,
            is_thread=is_thread
        )

        # Save image path to database (add custom field or store separately)
        if image_path:
            # Store image path in a separate file for the scheduled post
            image_ref_file = BASE_DIR / "Scheduled_Images" / f"scheduled_twitter_{post_id}.txt"
            image_ref_file.parent.mkdir(exist_ok=True)
            image_ref_file.write_text(str(image_path), encoding='utf-8')

        return jsonify({
            'success': True,
            'message': f'Twitter post scheduled for {scheduled_time}. Claude AI will enhance the content and generate diagrams at scheduled time!',
            'post_id': post_id,
            'scheduled_time': scheduled_time_str,
            'has_image': image_path is not None
        })

    except Exception as e:
        logger.error(f"Schedule Twitter error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/facebook/schedule', methods=['POST'])
def schedule_facebook_post():
    """Schedule a Facebook post for later"""
    try:
        from scheduler.scheduler_db import init_db, add_scheduled_post
        
        data = request.json
        content = data.get('content', '')
        scheduled_time_str = data.get('scheduled_time', '')
        hashtags = data.get('hashtags', '')
        
        if not content or not scheduled_time_str:
            return jsonify({'error': 'Content and scheduled_time required'}), 400
        
        init_db()
        scheduled_time = datetime.strptime(scheduled_time_str, '%Y-%m-%d %H:%M')
        
        if scheduled_time <= datetime.now():
            return jsonify({'error': 'Scheduled time must be in the future'}), 400
        
        post_id = add_scheduled_post(
            platform='facebook',
            content=content,
            scheduled_time=scheduled_time,
            hashtags=hashtags
        )
        
        return jsonify({
            'success': True,
            'message': f'Facebook post scheduled for {scheduled_time}',
            'post_id': post_id,
            'scheduled_time': scheduled_time_str
        })
        
    except Exception as e:
        logger.error(f"Schedule Facebook error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduled/posts', methods=['GET'])
def get_scheduled_posts():
    """Get all scheduled posts"""
    try:
        from scheduler.scheduler_db import get_all_scheduled_posts
        
        posts = get_all_scheduled_posts(limit=100)
        
        return jsonify({
            'success': True,
            'posts': posts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduled/post/<int:post_id>', methods=['DELETE'])
def delete_scheduled_post(post_id):
    """Delete/cancel a scheduled post"""
    try:
        from scheduler.scheduler_db import delete_scheduled_post
        
        deleted = delete_scheduled_post(post_id)
        
        if deleted:
            return jsonify({
                'success': True,
                'message': 'Scheduled post deleted'
            })
        else:
            return jsonify({'error': 'Post not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/twitter/profile', methods=['GET'])
def twitter_get_profile():
    """Get Twitter profile info"""
    try:
        from engine.twitter_manager import TwitterManager
        manager = TwitterManager()
        result = manager.get_profile()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Twitter profile error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/twitter/tweets', methods=['GET'])
def twitter_get_tweets():
    """Get recent Twitter tweets"""
    try:
        from engine.twitter_manager import TwitterManager
        manager = TwitterManager()
        limit = request.args.get('limit', 5, type=int)
        result = manager.get_recent_tweets(limit=limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Twitter tweets error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


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


# ============================================
# GOOGLE WORKSPACE API ENDPOINTS
# ============================================

@app.route('/api/google/calendar/create', methods=['POST'])
def create_calendar_event_new():
    """Create calendar event with Google Meet link (new endpoint for dashboard form)"""
    try:
        from services.google import GoogleCalendarService
        
        data = request.json
        title = data.get('title', 'Meeting')
        description = data.get('description', '')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        attendees = data.get('attendees', '')
        meet_link = data.get('meet_link', '')
        
        logger.info(f"Calendar API called with: start={start_time}, end={end_time}")
        
        if not all([start_time, end_time]):
            return jsonify({'error': 'Start time and end time required'}), 400
        
        # Parse attendees from comma-separated string
        attendee_list = [a.strip() for a in attendees.split(',') if a.strip()] if attendees else []
        
        calendar = GoogleCalendarService()
        result = calendar.create_event(
            summary=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            attendees=attendee_list
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Event created successfully',
                'event': result,
                'meet_link': meet_link or result.get('meet_link', '')
            })
        else:
            logger.error(f"Calendar creation failed: {result.get('error')}")
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        logger.error(f"Calendar event creation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/google/calendar/create-event', methods=['POST'])
def create_calendar_event():
    """Create calendar event with Google Meet link (legacy endpoint)"""
    try:
        from services.google import GoogleCalendarService
        
        data = request.json
        summary = data.get('summary', 'Meeting')
        description = data.get('description', '')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        attendees = data.get('attendees', [])
        
        if not all([start_time, end_time]):
            return jsonify({'error': 'Start time and end time required'}), 400
        
        calendar = GoogleCalendarService()
        result = calendar.create_event(
            summary=summary,
            description=description,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Event created successfully',
                'event': result
            })
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        logger.error(f"Calendar event creation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/google/calendar/upcoming', methods=['GET'])
def get_upcoming_events():
    """Get upcoming calendar events"""
    try:
        from services.google import GoogleCalendarService
        
        days = request.args.get('days', 7, type=int)
        
        calendar = GoogleCalendarService()
        result = calendar.get_upcoming_events(days=days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'events': result['events']
            })
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        logger.error(f"Get events error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/google/drive/create-folder', methods=['POST'])
def create_drive_folder():
    """Create folder in Google Drive"""
    try:
        from services.google import GoogleDriveService
        
        data = request.json
        folder_name = data.get('name', 'New Folder')
        parent_id = data.get('parent_id')
        
        drive = GoogleDriveService()
        result = drive.create_folder(folder_name, parent_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Folder created successfully',
                'folder': result
            })
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        logger.error(f"Drive folder creation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/google/docs/create', methods=['POST'])
def create_google_doc():
    """Create Google Doc"""
    try:
        from services.google import GoogleDocsService
        
        data = request.json
        title = data.get('title', 'Untitled Document')
        content = data.get('content', '')
        
        docs = GoogleDocsService()
        result = docs.create_document(title, content)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Document created successfully',
                'document': result
            })
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        logger.error(f"Docs creation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/google/sheets/create', methods=['POST'])
def create_google_sheet():
    """Create Google Sheet"""
    try:
        from services.google import GoogleSheetsService
        
        data = request.json
        title = data.get('title', 'Untitled Spreadsheet')
        data_rows = data.get('data', [])
        
        sheets = GoogleSheetsService()
        result = sheets.create_spreadsheet(title, data_rows)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Spreadsheet created successfully',
                'spreadsheet': result
            })
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        logger.error(f"Sheets creation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/google/sheets/import', methods=['POST'])
def import_google_sheet_data():
    """Import data to Google Sheet"""
    try:
        from services.google import GoogleSheetsService
        
        if 'import_file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['import_file']
        target_sheet = request.form.get('target_sheet', '')
        
        # Save uploaded file temporarily
        import os
        temp_path = f"/tmp/{file.filename}"
        file.save(temp_path)
        
        # Read file based on extension
        import pandas as pd
        if file.filename.endswith('.csv'):
            df = pd.read_csv(temp_path)
        else:
            df = pd.read_excel(temp_path)
        
        # Convert to list of lists
        data = df.values.tolist()
        
        # Import to sheet
        sheets = GoogleSheetsService()
        result = sheets.import_data(target_sheet, data)
        
        # Clean up temp file
        os.remove(temp_path)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Data imported successfully',
                'rows': len(data)
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        logger.error(f"Sheets import error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/google/meet/schedule', methods=['POST'])
def schedule_google_meet():
    """Schedule Google Meet meeting"""
    try:
        from services.google import GoogleCalendarService, GoogleMeetService
        
        data = request.json
        title = data.get('title', 'Meeting')
        description = data.get('description', '')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        participants = data.get('participants', '').split(',') if data.get('participants') else []
        agenda = data.get('agenda', '')
        create_calendar = data.get('create_calendar', True)
        send_invites = data.get('send_invites', True)
        
        # Create Meet link
        meet = GoogleMeetService()
        meet_result = meet.create_meet(title, description)
        
        if not meet_result['success']:
            return jsonify({'error': meet_result['error']}), 500
        
        meet_link = meet_result['meet_link']
        
        # Create calendar event if requested
        if create_calendar:
            calendar = GoogleCalendarService()
            calendar_result = calendar.create_event(
                title=title,
                description=f"{description}\n\nAgenda:\n{agenda}\n\nJoin Meet: {meet_link}",
                start_time=start_time,
                end_time=end_time,
                attendees=participants
            )
            
            if not calendar_result['success']:
                logger.warning(f"Calendar event creation failed: {calendar_result['error']}")
        
        return jsonify({
            'success': True,
            'message': 'Meeting scheduled successfully',
            'meet_link': meet_link,
            'calendar_event': calendar_result if create_calendar else None
        })
        
    except Exception as e:
        logger.error(f"Meet scheduling error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/google/docs/parse-resume', methods=['POST'])
def parse_resume():
    """Parse resume and create approval task"""
    try:
        if 'resume_file' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume_file']
        save_to = request.form.get('save_to', 'odoo')
        
        # Save uploaded file - ensure folder exists
        import os
        upload_folder = BASE_DIR / "Uploads" / "Resumes"
        upload_folder.mkdir(parents=True, exist_ok=True)  # Create parent folders if needed
        
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = upload_folder / filename
        file.save(str(file_path))
        
        # Create approval task for resume parsing
        from pathlib import Path as FilePath
        task_filename = f"resume_parse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        task_filepath = NEEDS_ACTION / task_filename
        
        task_content = f"""---
type: resume_parse
action: parse_resume
save_to: {save_to}
resume_file: {file_path}
---

# Resume Parsing Request

## File Details

**Original File:** {file.filename}
**Saved To:** {file_path}
**Parse To:** {save_to}

## Action Required

Parse resume and extract:
- Name
- Email
- Phone
- Skills
- Experience
- Education

## Save To

{'✅ Odoo CRM (Create Lead)' if save_to == 'odoo' else '✅ Google Sheets' if save_to == 'sheets' else '✅ Google Doc'}
"""
        
        task_filepath.write_text(task_content, encoding='utf-8')
        
        return jsonify({
            'success': True,
            'message': 'Resume uploaded for parsing! Check Pending Approval.',
            'task_file': task_filename
        })
        
    except Exception as e:
        logger.error(f"Resume parse error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/google/drive/process', methods=['POST'])
def process_google_drive():
    """Process Google Drive operations"""
    try:
        from services.google import GoogleDriveService
        
        action = request.form.get('action', 'create_folder')
        drive = GoogleDriveService()
        
        if action == 'create_folder':
            folder_name = request.form.get('folder_name', 'New Folder')
            parent_folder = request.form.get('parent_folder', None)
            
            result = drive.create_folder(folder_name, parent_folder if parent_folder else None)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': f"Folder '{folder_name}' created successfully",
                    'folder': result
                })
            else:
                return jsonify({'error': result['error']}), 500
                
        elif action == 'upload_file':
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            upload_folder = request.form.get('upload_folder', None)
            
            # Save file temporarily
            import os
            temp_path = f"/tmp/{file.filename}"
            file.save(temp_path)
            
            # Upload to Drive
            result = drive.upload_file(temp_path, parent_id=upload_folder)
            
            # Clean up
            os.remove(temp_path)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': f"File '{file.filename}' uploaded successfully",
                    'file': result
                })
            else:
                return jsonify({'error': result['error']}), 500
                
        elif action == 'organize':
            source_folder = request.form.get('source_folder', '')
            organize_by = request.form.get('organize_by', 'date')
            
            # Create approval task for organizing
            task_filename = f"drive_organize_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            task_filepath = NEEDS_ACTION / task_filename
            
            task_content = f"""---
type: drive_organize
action: organize_files
source_folder: {source_folder}
organize_by: {organize_by}
---

# Drive Organization Request

## Details

**Source Folder:** {source_folder}
**Organize By:** {organize_by.title()}

## Action Required

Organize files in the specified folder by {organize_by}.

## Approval

Move to Approved/ to execute organization.
"""
            
            task_filepath.write_text(task_content, encoding='utf-8')
            
            return jsonify({
                'success': True,
                'message': 'Organization task created! Check Needs Action folder.'
            })
        
        return jsonify({'error': 'Unknown action'}), 400
        
    except Exception as e:
        logger.error(f"Drive process error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/workflows/daily-report/generate', methods=['POST'])
def generate_daily_report_now():
    """Generate daily business report immediately"""
    try:
        from scheduler.main_scheduler import generate_daily_report
        
        # Run report generation
        result = generate_daily_report()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Daily report generated!',
                'doc_link': result.get('doc_link'),
                'email_sent': result.get('email_sent', False)
            })
        else:
            return jsonify({'error': result.get('error', 'Failed to generate report')}), 500
            
    except Exception as e:
        logger.error(f"Daily report generation error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("AI Employee Vault Dashboard")
    print("=" * 60)
    print(f"Dashboard URL: http://localhost:5000")
    print(f"Base Directory: {BASE_DIR}")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
