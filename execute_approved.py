"""
Execute Approved Actions
Watches Approved folder and executes approved emails, WhatsApp messages, and LinkedIn posts
"""

import sys
import time
import re
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# Fix emoji encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from config import APPROVED_FOLDER, DONE_FOLDER, ensure_folders_exist
from engine.logger import logger


class ApprovedExecutor:
    """Executes approved actions from Approved folder"""

    def __init__(self):
        """Initialize executor"""
        ensure_folders_exist()
        self.approved_folder = APPROVED_FOLDER
        self.done_folder = DONE_FOLDER
        logger.info("[EXECUTOR] Approved executor initialized")

    def extract_yaml_field(self, content: str, field: str) -> str:
        """Extract a field from YAML frontmatter"""
        pattern = rf"{field}:\s*(.+)"
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
        return ""

    def extract_email_body(self, content: str) -> str:
        """Extract email body from approval file"""
        # Look for "## Email Body" section
        if "## Email Body" in content:
            parts = content.split("## Email Body", 1)
            if len(parts) > 1:
                # Get content after "## Email Body" and before next "##"
                body_part = parts[1].strip()
                if "##" in body_part:
                    body_part = body_part.split("##")[0].strip()
                return body_part
        return ""

    def extract_whatsapp_message(self, content: str) -> str:
        """Extract WhatsApp message from approval file"""
        # Look for "## Message" or "## WhatsApp Message" section
        for marker in ["## WhatsApp Message", "## Message"]:
            if marker in content:
                parts = content.split(marker, 1)
                if len(parts) > 1:
                    msg_part = parts[1].strip()
                    if "##" in msg_part:
                        msg_part = msg_part.split("##")[0].strip()
                    return msg_part
        return ""

    def execute_email(self, file_path: Path) -> bool:
        """Execute approved email"""
        try:
            logger.info(f"[EMAIL] Executing: {file_path.name}")

            # Read approval file
            content = file_path.read_text(encoding='utf-8')

            # Extract fields from YAML frontmatter
            to_email = self.extract_yaml_field(content, 'to')
            subject = self.extract_yaml_field(content, 'subject')

            # Extract email body
            body = self.extract_email_body(content)

            if not to_email or not subject or not body:
                logger.error(f"[EMAIL] Missing required fields in {file_path.name}")
                logger.error(f"   to: '{to_email}', subject: '{subject}', body: '{body[:50]}...'")
                return False

            # Run send_email.js - write to temp file to avoid command line escaping issues
            logger.info(f"[EMAIL] Sending to: {to_email}")
            
            # Write email data to temp file
            import json
            temp_file = Path(__file__).parent / ".email_temp.json"
            email_data = {
                "to": to_email,
                "subject": subject,
                "body": body
            }
            temp_file.write_text(json.dumps(email_data, ensure_ascii=False), encoding='utf-8')
            
            # Run send_email.js with temp file
            result = subprocess.run(
                ['node', 'send_email.js', '--from-file', str(temp_file)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                cwd=str(Path(__file__).parent)
            )
            
            # Clean up temp file
            try:
                temp_file.unlink()
            except:
                pass

            if result.returncode == 0:
                logger.info(f"[EMAIL] Sent successfully: {to_email}")
                self._create_execution_log(file_path, 'email', 'success', {
                    'to': to_email,
                    'subject': subject,
                    'output': result.stdout
                })
                return True
            else:
                logger.error(f"[EMAIL] Send failed: {result.stderr}")
                self._create_execution_log(file_path, 'email', 'failed', {
                    'to': to_email,
                    'subject': subject,
                    'error': result.stderr
                })
                return False

        except Exception as e:
            logger.error(f"[EMAIL] Error: {e}")
            return False

    def execute_whatsapp(self, file_path: Path) -> bool:
        """Execute approved WhatsApp message by adding to Send_Queue"""
        try:
            logger.info(f"[WHATSAPP] Processing: {file_path.name}")

            # Read approval file
            content = file_path.read_text(encoding='utf-8')

            # Extract fields from YAML frontmatter
            phone = self.extract_yaml_field(content, 'phone')
            
            # Extract message
            message = self.extract_whatsapp_message(content)

            if not phone or not message:
                logger.error(f"[WHATSAPP] Missing required fields in {file_path.name}")
                logger.error(f"   phone: {phone}, message: {message[:50]}...")
                return False

            # Format phone number (remove + if present)
            formatted_phone = phone.replace('+', '').replace(' ', '')
            
            # Add to Send_Queue for whatsapp_watcher_node.js to process
            send_queue_folder = Path(__file__).parent / "Send_Queue"
            send_queue_folder.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            queue_filename = f"QUEUE_approved_{formatted_phone}_{timestamp}.md"
            queue_path = send_queue_folder / queue_filename
            
            queue_content = f"""---
to: {formatted_phone}
queued_at: {datetime.now().isoformat()}
type: approved_action
original_approval: {file_path.name}
---

# Queued WhatsApp Message (Approved)

## Contact

**Phone:** {formatted_phone}

## Message

{message}

## Status

✅ Human approved - Ready to send
"""
            
            queue_path.write_text(queue_content, encoding='utf-8')
            logger.info(f"[WHATSAPP] Added to Send_Queue: {queue_filename}")
            logger.info(f"[WHATSAPP] whatsapp_watcher_node.js will send it automatically")
            
            # Create execution log
            self._create_execution_log(file_path, 'whatsapp', 'queued', {
                'phone': formatted_phone,
                'queue_file': queue_filename,
                'note': 'Added to Send_Queue - waiting for whatsapp_watcher_node.js to send'
            })
            
            # Move approval file to Done
            dest = self.done_folder / file_path.name
            shutil.move(str(file_path), str(dest))
            logger.info(f"[DONE] Moved {file_path.name} to Done/")
            
            return True

        except Exception as e:
            logger.error(f"[WHATSAPP] Error: {e}")
            return False

    def execute_linkedin(self, file_path: Path) -> bool:
        """Execute approved LinkedIn post"""
        try:
            logger.info(f"[LINKEDIN] Executing: {file_path.name}")

            # Import LinkedIn poster
            from engine.linkedin_poster import LinkedInPoster

            # Create poster instance
            poster = LinkedInPoster()

            # Process the post
            success = poster.process_approved_post(file_path)

            if success:
                logger.info(f"[LINKEDIN] Post published: {file_path.name}")
                self._create_execution_log(file_path, 'linkedin', 'success', {})
                return True
            else:
                logger.error(f"[LINKEDIN] Post failed: {file_path.name}")
                self._create_execution_log(file_path, 'linkedin', 'failed', {})
                return False

        except Exception as e:
            logger.error(f"[LINKEDIN] Error: {e}")
            return False

    def execute_linkedin_lead(self, file_path: Path) -> bool:
        """Execute approved LinkedIn lead creation in Odoo"""
        try:
            logger.info(f"[LINKEDIN] Executing Lead: {file_path.name}")

            # Import Odoo server
            from mcp_servers.odoo_server import OdooMCPServer
            
            # Create Odoo instance
            odoo = OdooMCPServer()

            # Read approval file
            content = file_path.read_text(encoding='utf-8')

            # Extract fields from YAML frontmatter
            lead_name = self.extract_yaml_field(content, 'lead_name')
            odoo_id = self.extract_yaml_field(content, 'odoo_id')

            if not lead_name:
                logger.error(f"[LINKEDIN] Missing lead_name in {file_path.name}")
                return False

            logger.info(f"[LINKEDIN] Lead ready for review: {lead_name} (Odoo ID: {odoo_id})")
            
            # Lead already created in Odoo, just log it
            self._create_execution_log(file_path, 'linkedin_lead', 'success', {
                'lead_name': lead_name,
                'odoo_id': odoo_id,
                'note': 'Lead created in Odoo, ready for contact'
            })
            return True

        except Exception as e:
            logger.error(f"[LINKEDIN] Lead Error: {e}")
            return False

    def execute_odoo_lead(self, file_path: Path) -> bool:
        """Execute approved Odoo lead creation"""
        try:
            logger.info(f"[ODOO] Executing: {file_path.name}")

            # Import Odoo server
            from mcp_servers.odoo_server import OdooMCPServer
            
            # Create Odoo instance
            odoo = OdooMCPServer()

            # Read approval file
            content = file_path.read_text(encoding='utf-8')

            # Extract fields from YAML frontmatter
            lead_name = self.extract_yaml_field(content, 'lead_name')
            email = self.extract_yaml_field(content, 'email')
            phone = self.extract_yaml_field(content, 'phone')
            source = self.extract_yaml_field(content, 'source')

            if not lead_name:
                logger.error(f"[ODOO] Missing lead_name in {file_path.name}")
                return False

            # Create lead in Odoo
            result = odoo.create_lead(lead_name, email, phone, source)

            if result.get('success'):
                logger.info(f"[ODOO] Lead created: {lead_name} (ID: {result['lead_id']})")
                
                # Save to Odoo_Data/Leads/
                leads_folder = Path(__file__).parent / "Odoo_Data" / "Leads"
                leads_folder.mkdir(exist_ok=True)
                
                lead_file = leads_folder / f"LEAD_{lead_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
                lead_content = f"""# Odoo Lead Created

**Name:** {lead_name}
**Email:** {email}
**Phone:** {phone}
**Source:** {source}
**Odoo ID:** {result['lead_id']}
**Created:** {datetime.now().isoformat()}
**Approval File:** {file_path.name}
"""
                lead_file.write_text(lead_content, encoding='utf-8')
                
                self._create_execution_log(file_path, 'odoo_lead', 'success', {
                    'lead_name': lead_name,
                    'email': email,
                    'odoo_id': result['lead_id']
                })
                return True
            else:
                logger.error(f"[ODOO] Lead creation failed: {result.get('error')}")
                self._create_execution_log(file_path, 'odoo_lead', 'failed', {
                    'error': result.get('error')
                })
                return False

        except Exception as e:
            logger.error(f"[ODOO] Error: {e}")
            return False

    def execute_odoo_invoice(self, file_path: Path) -> bool:
        """Execute approved Odoo invoice creation"""
        try:
            logger.info(f"[ODOO] Executing Invoice: {file_path.name}")

            from mcp_servers.odoo_server import OdooMCPServer
            odoo = OdooMCPServer()

            content = file_path.read_text(encoding='utf-8')

            # Extract fields
            customer_name = self.extract_yaml_field(content, 'customer_name')
            customer_email = self.extract_yaml_field(content, 'customer_email')
            amount = self.extract_yaml_field(content, 'amount')
            description = self.extract_yaml_field(content, 'description')

            if not customer_name or not amount:
                logger.error(f"[ODOO] Missing required fields in {file_path.name}")
                return False

            # Find or create partner
            partner = odoo.get_partner_by_email(customer_email)
            if partner:
                partner_id = partner['id']
            else:
                partner_result = odoo.create_partner(customer_name, customer_email)
                if partner_result.get('success'):
                    partner_id = partner_result['partner_id']
                else:
                    return False

            # Create invoice
            result = odoo.create_invoice(partner_id, float(amount), description=description)

            if result.get('success'):
                logger.info(f"[ODOO] Invoice created: ID {result['invoice_id']}")
                self._create_execution_log(file_path, 'odoo_invoice', 'success', result)
                return True
            else:
                logger.error(f"[ODOO] Invoice creation failed: {result.get('error')}")
                return False

        except Exception as e:
            logger.error(f"[ODOO] Invoice Error: {e}")
            return False

    def execute_odoo_quotation(self, file_path: Path) -> bool:
        """Execute approved Odoo quotation creation"""
        try:
            logger.info(f"[ODOO] Executing Quotation: {file_path.name}")

            from mcp_servers.odoo_server import OdooMCPServer
            odoo = OdooMCPServer()

            content = file_path.read_text(encoding='utf-8')

            # Extract fields
            customer_name = self.extract_yaml_field(content, 'customer_name')
            customer_email = self.extract_yaml_field(content, 'customer_email')
            amount = self.extract_yaml_field(content, 'amount')
            products = self.extract_yaml_field(content, 'products')

            if not customer_name or not amount:
                logger.error(f"[ODOO] Missing required fields in {file_path.name}")
                return False

            # Find or create partner
            partner = odoo.get_partner_by_email(customer_email)
            if partner:
                partner_id = partner['id']
            else:
                partner_result = odoo.create_partner(customer_name, customer_email)
                if partner_result.get('success'):
                    partner_id = partner_result['partner_id']
                else:
                    return False

            # Create quotation
            result = odoo.create_quotation(partner_id, amount=float(amount))

            if result.get('success'):
                logger.info(f"[ODOO] Quotation created: ID {result['quotation_id']}")
                self._create_execution_log(file_path, 'odoo_quotation', 'success', result)
                return True
            else:
                logger.error(f"[ODOO] Quotation creation failed: {result.get('error')}")
                return False

        except Exception as e:
            logger.error(f"[ODOO] Quotation Error: {e}")
            return False

    def _create_execution_log(self, file_path: Path, action_type: str, status: str, details: dict):
        """Create execution log in Done folder"""
        timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        log_filename = f"EXECUTED_{file_path.name}"
        log_path = self.done_folder / log_filename

        # Read original approval content
        original_content = file_path.read_text(encoding='utf-8')

        log_content = f"""---
type: execution_log
action: {action_type}
original_approval: {file_path.name}
executed_at: {timestamp}
status: {status}
---

# {action_type.title()} Send Execution Log

## Original Approval

{original_content}

## Execution Result

**Status:** {'success ✅' if status == 'success' else 'failed ❌'}
**Executed at:** {timestamp}

## Details

"""
        for key, value in details.items():
            log_content += f"**{key.title()}:** {value}\n"

        log_content += f"""
## File Movement

**Original:** Approved/{file_path.name}
**Moved to:** Done/{log_filename}

---
*Executed by AI Employee Vault*
"""

        log_path.write_text(log_content, encoding='utf-8')

    def process_approved_file(self, file_path: Path):
        """Process a single approved file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Determine action type and execute
            if "APPROVAL_send_email" in file_path.name or "action: send_email" in content:
                success = self.execute_email(file_path)
            elif "APPROVAL_send_whatsapp" in file_path.name or "action: send_whatsapp" in content:
                success = self.execute_whatsapp(file_path)
            elif "LINKEDIN_POST" in file_path.name or "action: linkedin_post" in content:
                success = self.execute_linkedin(file_path)
            elif "ODOO_LEAD" in file_path.name or "action: create_lead" in content:
                success = self.execute_odoo_lead(file_path)
            elif "ODOO_INV" in file_path.name or "action: create_invoice" in content:
                success = self.execute_odoo_invoice(file_path)
            elif "ODOO_QUO" in file_path.name or "action: create_quotation" in content:
                success = self.execute_odoo_quotation(file_path)
            else:
                logger.info(f"[SKIP] Unknown action type: {file_path.name}")
                return

            # Move file to Done folder
            if success:
                dest = self.done_folder / file_path.name
                shutil.move(str(file_path), str(dest))
                logger.info(f"[DONE] Moved {file_path.name} to Done/")
            else:
                logger.warning(f"[WAIT] Keeping {file_path.name} in Approved/ due to failure")

        except Exception as e:
            logger.error(f"[ERROR] Processing {file_path.name}: {e}")

    def process_all_approved(self):
        """Process all approved files in Approved folder"""
        logger.info("[EXECUTOR] Checking for approved actions...")

        # Process email approvals
        for file_path in self.approved_folder.glob("APPROVAL_send_email_*.md"):
            self.process_approved_file(file_path)

        # Process WhatsApp approvals
        for file_path in self.approved_folder.glob("APPROVAL_send_whatsapp_*.md"):
            self.process_approved_file(file_path)

        # Process LinkedIn approvals
        for file_path in self.approved_folder.glob("APPROVAL_linkedin_*.md"):
            self.process_approved_file(file_path)
        for file_path in self.approved_folder.glob("LINKEDIN_POST_*.md"):
            self.process_approved_file(file_path)

        # Process Odoo approvals (Gold Tier)
        for file_path in self.approved_folder.glob("ODOO_LEAD_*.md"):
            self.process_approved_file(file_path)
        for file_path in self.approved_folder.glob("ODOO_INV_*.md"):
            self.process_approved_file(file_path)
        for file_path in self.approved_folder.glob("ODOO_QUO_*.md"):
            self.process_approved_file(file_path)

    def start(self):
        """Start watching Approved folder"""
        logger.info("[EXECUTOR] Starting Approved folder watcher...")
        print()
        print("=" * 60)
        print("APPROVED ACTIONS EXECUTOR")
        print("=" * 60)
        print()
        print(f"Monitoring: {self.approved_folder}")
        print("Move approval files here to execute them")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        print()

        # Process existing files first
        self.process_all_approved()

        # Watch for new files
        try:
            while True:
                time.sleep(5)
                self.process_all_approved()
        except KeyboardInterrupt:
            logger.info("[EXECUTOR] Stopping...")
            print()
            print("=" * 60)
            print("EXECUTOR STOPPED")
            print("=" * 60)


if __name__ == "__main__":
    executor = ApprovedExecutor()
    executor.start()
