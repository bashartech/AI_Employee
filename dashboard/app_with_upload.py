"""
AI Employee Vault - Dashboard with File Upload
Flask web application with inbox file upload feature
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from pathlib import Path
import yaml
import re
from datetime import datetime
import subprocess
import shutil
import psutil
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Allow file uploads
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = 'Inbox'

# Paths
BASE_DIR = Path(__file__).parent.parent
NEEDS_ACTION = BASE_DIR / "Needs Action"
PENDING_APPROVAL = BASE_DIR / "Pending Approval"
APPROVED = BASE_DIR / "Approved"
DONE = BASE_DIR / "Done"
REJECTED = BASE_DIR / "Rejected"
INBOX = BASE_DIR / "Inbox"
SEND_QUEUE = BASE_DIR / "Send_Queue"
DASHBOARD_MD = BASE_DIR / "Dashboard.md"
LOGS_DIR = BASE_DIR / "logs"

# Ensure folders exist
for folder in [INBOX, NEEDS_ACTION, PENDING_APPROVAL, APPROVED, DONE, REJECTED, LOGS_DIR]:
    folder.mkdir(exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'md', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve dashboard HTML"""
    return render_template('index.html')


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
                task_filepath = INBOX / task_filename
                
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
        
        task_content = f"""# Task from Dashboard

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


@app.route('/api/overview')
def api_overview():
    """Get system overview"""
    return jsonify({
        'needs_action': len(list(NEEDS_ACTION.glob('*.md'))),
        'pending_approval': len(list(PENDING_APPROVAL.glob('*.md'))),
        'approved': len(list(APPROVED.glob('*.md'))),
        'done': len(list(DONE.glob('*.md'))),
        'rejected': len(list(REJECTED.glob('*.md')))
    })


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
    
    tasks = []
    if folder_path.exists():
        for file in folder_path.glob('*.md'):
            tasks.append(parse_markdown_file(file))
    
    return jsonify(tasks)


@app.route('/api/task/<path:filename>')
def api_get_task(filename):
    """Get specific task"""
    folders = [NEEDS_ACTION, PENDING_APPROVAL, APPROVED, DONE, REJECTED]
    
    for folder in folders:
        filepath = folder / filename
        if filepath.exists():
            return jsonify(parse_markdown_file(filepath))
    
    return jsonify({'error': 'Task not found'}), 404


@app.route('/api/task/approve', methods=['POST'])
def api_approve_task():
    """Approve task (move from Pending to Approved)"""
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'Filename required'}), 400
    
    source = PENDING_APPROVAL / filename
    dest = APPROVED / filename
    
    if not source.exists():
        return jsonify({'error': 'Task not found'}), 404
    
    shutil.move(str(source), str(dest))
    return jsonify({'success': True, 'message': 'Task approved'})


@app.route('/api/task/reject', methods=['POST'])
def api_reject_task():
    """Reject task (move from Pending to Rejected)"""
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'Filename required'}), 400
    
    source = PENDING_APPROVAL / filename
    dest = REJECTED / filename
    
    if not source.exists():
        return jsonify({'error': 'Task not found'}), 404
    
    shutil.move(str(source), str(dest))
    return jsonify({'success': True, 'message': 'Task rejected'})


@app.route('/api/system/metrics')
def api_system_metrics():
    """Get system metrics"""
    return jsonify({
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent
    })


@app.route('/api/activity/recent')
def api_activity_recent():
    """Get recent activity"""
    activities = []
    
    for folder, folder_type, action in [
        (DONE, 'done', 'Completed'),
        (PENDING_APPROVAL, 'pending_approval', 'Pending Approval'),
        (NEEDS_ACTION, 'needs_action', 'Needs Action')
    ]:
        if folder.exists():
            for file in sorted(folder.glob('*.md'), key=lambda f: f.stat().st_mtime, reverse=True)[:5]:
                activities.append({
                    'filename': file.name,
                    'type': folder_type,
                    'action': action,
                    'time': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
    
    return jsonify(activities[:15])


def parse_markdown_file(filepath):
    """Parse markdown file with YAML frontmatter"""
    try:
        content = filepath.read_text(encoding='utf-8')
        
        frontmatter = {}
        body = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2]
                except:
                    pass
        
        return {
            'filename': filepath.name,
            'filepath': str(filepath),
            'title': filepath.stem,
            'frontmatter': frontmatter,
            'body': body[:500],
            'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
        }
    except Exception as e:
        return {'filename': filepath.name, 'error': str(e)}


if __name__ == '__main__':
    print("="*60)
    print("AI Employee Vault Dashboard")
    print("="*60)
    print(f"Dashboard URL: http://localhost:5000")
    print(f"Base Directory: {BASE_DIR}")
    print("="*60)
    print()
    print("Features:")
    print("  ✓ File Upload to Inbox")
    print("  ✓ Text Message to Inbox")
    print("  ✓ Task Management")
    print("  ✓ Real-time Monitoring")
    print("="*60)
    print()
    
    app.run(debug=False, host='0.0.0.0', port=5000)
