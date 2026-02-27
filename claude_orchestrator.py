"""
Claude Code Orchestrator - Gold Tier Automation
Automatically triggers Claude Code when new tasks appear in Needs Action folder
Uses Ralph Wiggum loop for continuous processing until task completion
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Fix emoji encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

VAULT = Path(__file__).parent
NEEDS_ACTION = VAULT / "Needs Action"
PENDING_APPROVAL = VAULT / "Pending Approval"
APPROVED = VAULT / "Approved"
DONE = VAULT / "Done"
SKILLS_DIR = VAULT / ".claude" / "skills"

# Import Ralph Wiggum hook
sys.path.insert(0, str(VAULT))
from ralph_wiggum_hook import ralph_loop

# Ensure folders exist
for folder in [NEEDS_ACTION, PENDING_APPROVAL, APPROVED, DONE]:
    folder.mkdir(exist_ok=True)


class ClaudeCodeHandler(FileSystemEventHandler):
    """Handles new files in Needs Action folder"""
    
    def __init__(self):
        self.processed_files = set()
        self.last_check = time.time()
        
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Only process markdown files
        if file_path.suffix.lower() not in ['.md', '.txt']:
            return
        
        # Skip if already processed
        if file_path.name in self.processed_files:
            return
        
        # Check if file is in Needs Action folder
        if "Needs Action" not in str(file_path):
            return
        
        print(f"\n📥 New task detected: {file_path.name}")
        self.process_task(file_path)
    
    def process_task(self, file_path: Path):
        """Process a single task with Claude Code"""
        print(f"🤖 Starting Claude Code to process: {file_path.name}")
        
        # Read the task file with retry logic
        max_retries = 5
        task_content = None
        
        for retry in range(max_retries):
            try:
                task_content = file_path.read_text(encoding='utf-8')
                break
            except PermissionError as e:
                print(f"  ⚠️  File locked, waiting... (attempt {retry + 1}/{max_retries})")
                time.sleep(2)  # Wait 2 seconds before retry
            except Exception as e:
                print(f"❌ Error reading file: {e}")
                return
        
        if task_content is None:
            print(f"❌ Could not read file after {max_retries} attempts")
            return
        
        # Determine task type from filename or content
        task_type = self.detect_task_type(file_path.name, task_content)
        
        # Build Claude Code prompt based on task type
        prompt = self.build_prompt(task_type, file_path)
        
        # Run Claude Code with Ralph Wiggum loop
        success = self.run_claude_code(prompt, file_path)
        
        if success:
            self.processed_files.add(file_path.name)
            print(f"✅ Task processed successfully: {file_path.name}")
        else:
            print(f"❌ Task processing failed: {file_path.name}")
    
    def detect_task_type(self, filename: str, content: str) -> str:
        """Detect what type of task this is"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        if 'email' in filename_lower or 'email' in content_lower[:500]:
            return 'email'
        elif 'whatsapp' in filename_lower or 'whatsapp' in content_lower[:500]:
            return 'whatsapp'
        elif 'linkedin' in filename_lower or 'linkedin' in content_lower[:500]:
            if 'post' in filename_lower or 'post' in content_lower[:500]:
                return 'linkedin_post'
            else:
                return 'linkedin_lead'
        elif 'odoo' in filename_lower or 'odoo' in content_lower[:500]:
            if 'invoice' in filename_lower or 'invoice' in content_lower[:500]:
                return 'odoo_invoice'
            elif 'quotation' in filename_lower or 'quotation' in content_lower[:500]:
                return 'odoo_quotation'
            else:
                return 'odoo_lead'
        elif 'inbox' in filename_lower:
            return 'inbox'
        else:
            return 'general'
    
    def build_prompt(self, task_type: str, file_path: Path) -> str:
        """Build appropriate prompt for Claude Code based on task type"""
        
        prompts = {
            'email': """
Process this email task from Needs Action folder.

Follow these steps:
1. Read the email from Needs Action folder
2. Analyze the email content and determine appropriate response
3. Draft a professional email response
4. Create approval file in Pending Approval folder using the format from .claude/skills/email-automation/SKILL.md
5. Update the task status

IMPORTANT: 
- Follow the exact format in .claude/skills/email-automation/SKILL.md
- Include all required fields: to, subject, ## Email Body
- Do NOT send the email directly - create approval file for human review
""",
            
            'whatsapp': """
Process this WhatsApp message task from Needs Action folder.

Follow these steps:
1. Read the WhatsApp message from Needs Action folder
2. Analyze the message and determine appropriate response
3. Draft a WhatsApp response message
4. Create approval file in Pending Approval folder using the format from .claude/skills/whatsapp-automation/SKILL.md
5. Update the task status

IMPORTANT:
- Follow the exact format in .claude/skills/whatsapp-automation/SKILL.md
- Include all required fields: phone, ## Message
- Do NOT send the message directly - create approval file for human review
""",
            
            'linkedin_post': """
Process this LinkedIn post creation task from Needs Action folder.

Follow these steps:
1. Read the post request from Needs Action folder
2. Create a professional LinkedIn post with hashtags
3. Create approval file in Pending Approval folder using the format from .claude/skills/linkedin-automation/SKILL.md
4. Update the task status

IMPORTANT:
- Follow the exact format in .claude/skills/linkedin-automation/SKILL.md
- Include ## Post Content section
- Add 3-5 relevant hashtags
- Do NOT post directly - create approval file for human review
""",
            
            'linkedin_lead': """
Process this LinkedIn lead from Needs Action folder.

Follow these steps:
1. Read the LinkedIn lead/comment/message from Needs Action folder
2. Analyze the lead and determine if it shows interest
3. Create lead approval file in Pending Approval folder
4. Update the task status

IMPORTANT:
- Extract lead details (name, email, phone if available)
- Create approval file for human review before adding to Odoo
""",
            
            'odoo_lead': """
Process this Odoo lead creation task from Needs Action folder.

Follow these steps:
1. Read the lead details from Needs Action folder
2. Extract: name, email, phone, source
3. Create approval file in Pending Approval folder
4. Update the task status

IMPORTANT:
- Follow Odoo skill format in .claude/skills/odoo/
- Include all required YAML fields
- Do NOT create in Odoo directly - create approval file for human review
""",
            
            'odoo_invoice': """
Process this Odoo invoice creation task from Needs Action folder.

Follow these steps:
1. Read the invoice details from Needs Action folder
2. Extract: customer_name, customer_email, amount, description
3. Create approval file in Pending Approval folder
4. Update the task status

IMPORTANT:
- Follow Odoo skill format in .claude/skills/odoo/
- Include all required YAML fields
- Do NOT create invoice directly - create approval file for human review
""",
            
            'odoo_quotation': """
Process this Odoo quotation creation task from Needs Action folder.

Follow these steps:
1. Read the quotation details from Needs Action folder
2. Extract: customer_name, customer_email, amount, products
3. Create approval file in Pending Approval folder
4. Update the task status

IMPORTANT:
- Follow Odoo skill format in .claude/skills/odoo/
- Include all required YAML fields
- Do NOT create quotation directly - create approval file for human review
""",
            
            'inbox': """
Process this inbox file drop task from Needs Action folder.

Follow these steps:
1. Read the file content from Needs Action folder
2. Analyze what action is needed
3. Either:
   - Process directly and move to Done/ if safe
   - Create approval file in Pending Approval/ if action needed
4. Update the task status
""",
            
            'general': """
Process this general task from Needs Action folder.

Follow these steps:
1. Read the task from Needs Action folder
2. Analyze what needs to be done
3. Determine if this requires human approval:
   - If YES: Create approval file in Pending Approval folder
   - If NO: Process the task and move to Done folder
4. Update the task status

IMPORTANT:
- Check .claude/skills/ for relevant skill files
- Follow the formats and workflows specified there
- When in doubt, create approval file for human review
"""
        }
        
        return prompts.get(task_type, prompts['general'])
    
    def run_claude_code(self, prompt: str, file_path: Path, max_iterations: int = 10) -> bool:
        """Run Claude Code with Ralph Wiggum loop for retry logic"""
        
        print(f"\n  🔄 Starting Ralph Wiggum loop (max {max_iterations} iterations)")
        
        # Use Ralph Wiggum hook for automatic retry
        success = ralph_loop(prompt, file_path, max_iterations=max_iterations)
        
        if success:
            print(f"  ✅ Ralph Wiggum loop completed successfully")
        else:
            print(f"  ❌ Ralph Wiggum loop failed after {max_iterations} iterations")
        
        return success
    
    def check_task_completed(self, file_path: Path) -> bool:
        """Check if task file was moved to Done folder"""
        done_file = DONE / file_path.name
        return done_file.exists()
    
    def check_approval_created(self, file_path: Path) -> bool:
        """Check if approval file was created in Pending Approval"""
        # Look for any new approval files
        approval_files = list(PENDING_APPROVAL.glob("APPROVAL_*.md"))
        if approval_files:
            # Check if any were created in last minute
            for af in approval_files:
                if abs(af.stat().st_mtime - time.time()) < 60:
                    return True
        return False


def run_orchestrator():
    """Main orchestrator loop"""
    print("="*60)
    print("🤖 CLAUDE CODE ORCHESTRATOR")
    print("="*60)
    print(f"Monitoring: {NEEDS_ACTION}")
    print(f"Skills directory: {SKILLS_DIR}")
    print(f"Checking: Every 60 seconds")
    print("\nPress Ctrl+C to stop\n")
    
    handler = ClaudeCodeHandler()
    observer = Observer()
    observer.schedule(handler, str(NEEDS_ACTION), recursive=False)
    observer.start()
    
    print("✅ Orchestrator started - watching for new tasks...")
    
    try:
        while True:
            time.sleep(60)
            
            # Periodic status check
            needs_action_count = len(list(NEEDS_ACTION.glob("*.md")))
            pending_count = len(list(PENDING_APPROVAL.glob("*.md")))
            approved_count = len(list(APPROVED.glob("*.md")))
            done_count = len(list(DONE.glob("*.md")))
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Status:")
            print(f"  📥 Needs Action: {needs_action_count}")
            print(f"  ⏳ Pending Approval: {pending_count}")
            print(f"  ✅ Approved: {approved_count}")
            print(f"  ✔️  Done: {done_count}")
            
    except KeyboardInterrupt:
        print("\n\n⏹ Orchestrator stopped by user")
        observer.stop()
    
    observer.join()


if __name__ == "__main__":
    run_orchestrator()
