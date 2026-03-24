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
            elif "APPROVAL_linkedin_post" in file_path.name or "LINKEDIN_POST" in file_path.name or "action: linkedin_post" in content:
                success = self.execute_linkedin(file_path)
            elif "APPROVAL_twitter" in file_path.name or "action: twitter" in content:
                success = self.execute_twitter(file_path)  # NEW!
            elif "APPROVAL_facebook_reply" in file_path.name or "action: facebook_reply" in content:
                success = self.execute_facebook_reply(file_path)
            elif "APPROVAL_facebook" in file_path.name or "action: facebook" in content:
                success = self.execute_facebook(file_path)
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

    def execute_facebook(self, file_path: Path) -> bool:
        """Execute approved Facebook action"""
        try:
            from engine.facebook_manager import FacebookPageManager

            logger.info(f"[FACEBOOK] Executing: {file_path.name}")

            # Read approval file
            content = file_path.read_text(encoding='utf-8')

            # Extract action type
            action = self.extract_yaml_field(content, 'action')

            if not action:
                logger.error(f"[FACEBOOK] No action specified in {file_path.name}")
                return False

            manager = FacebookPageManager()

            if action == 'facebook_post':
                # Extract message from content - check multiple formats
                message = None

                # Try "## AI-Generated Content" first (new format from scheduler)
                if "## AI-Generated Content" in content:
                    parts = content.split("## AI-Generated Content", 1)
                    if len(parts) > 1:
                        msg_part = parts[1].strip()
                        # Stop at next section (## Diagram or ## Instructions)
                        if "## AI-Generated Diagram" in msg_part:
                            msg_part = msg_part.split("## AI-Generated Diagram")[0].strip()
                        elif "## Instructions" in msg_part:
                            msg_part = msg_part.split("## Instructions")[0].strip()
                        elif "## Uploaded Image" in msg_part:
                            msg_part = msg_part.split("## Uploaded Image")[0].strip()
                        message = msg_part

                # Fallback to "## Message" or "## Content"
                if not message:
                    for marker in ["## Message", "## Content"]:
                        if marker in content:
                            parts = content.split(marker, 1)
                            if len(parts) > 1:
                                msg_part = parts[1].strip()
                                if "##" in msg_part:
                                    msg_part = msg_part.split("##")[0].strip()
                                message = msg_part
                                break

                if not message:
                    logger.error(f"[FACEBOOK] No message found in {file_path.name}")
                    logger.error(f"   Content preview: {content[:500]}...")
                    return False

                # Extract image path - check BOTH image_path: and diagram_path: in YAML
                image_path = None
                
                # Check YAML frontmatter first
                if "image_path:" in content:
                    yaml_match = re.search(r'image_path:\s*(.+)', content)
                    if yaml_match:
                        image_path = yaml_match.group(1).strip()
                        logger.info(f"[FACEBOOK] ✅ Found uploaded image in YAML: {image_path}")
                
                # Also check for diagram_path: (generated diagrams)
                if not image_path and "diagram_path:" in content:
                    yaml_match = re.search(r'diagram_path:\s*(.+)', content)
                    if yaml_match:
                        image_path = yaml_match.group(1).strip()
                        logger.info(f"[FACEBOOK] ✅ Found generated diagram in YAML: {image_path}")
                
                # Also check for diagram image section (for auto-generated diagrams)
                if not image_path and "## Diagram Image" in content:
                    parts = content.split("## Diagram Image", 1)
                    if len(parts) > 1:
                        image_part = parts[1].strip()
                        image_match = re.search(r'Image file:\s*`([^`]+)`', image_part)
                        if image_match:
                            image_path = image_match.group(1).strip()
                            logger.info(f"[FACEBOOK] ✅ Found diagram image: {image_path}")
                
                # Log what we found
                if image_path:
                    logger.info(f"[FACEBOOK] 📷 Will post with image: {image_path}")
                    # Verify file exists
                    if not Path(image_path).exists():
                        logger.warning(f"[FACEBOOK] ⚠️ Image file not found: {image_path}")
                        image_path = None
                else:
                    logger.info(f"[FACEBOOK] 📝 Posting text only (no image found)")

                # Post to Facebook (with image if available)
                if image_path and Path(image_path).exists():
                    logger.info(f"[FACEBOOK] Posting with image: {image_path}")
                    result = manager.create_post_with_local_image(message, image_path)
                else:
                    logger.info(f"[FACEBOOK] Posting text only")
                    result = manager.create_post(message)

                if result.get('success'):
                    logger.info(f"[FACEBOOK] Post created: {result['post_id']}")
                    self._create_execution_log(file_path, 'facebook_post', 'success', {
                        'post_id': result['post_id'],
                        'has_image': 'Yes' if image_path else 'No'
                    })
                    return True
                else:
                    logger.error(f"[FACEBOOK] Post failed: {result.get('error')}")
                    self._create_execution_log(file_path, 'facebook_post', 'failed', {
                        'error': result.get('error')
                    })
                    return False

            elif action == 'facebook_delete':
                # Extract post ID
                post_id = self.extract_yaml_field(content, 'post_id')

                if not post_id:
                    logger.error(f"[FACEBOOK] No post_id found in {file_path.name}")
                    return False

                # Delete post
                result = manager.delete_post(post_id)

                if result.get('success'):
                    logger.info(f"[FACEBOOK] Post deleted: {post_id}")
                    self._create_execution_log(file_path, 'facebook_delete', 'success', {
                        'post_id': post_id
                    })
                    return True
                else:
                    logger.error(f"[FACEBOOK] Delete failed: {result.get('error')}")
                    return False

            elif action == 'facebook_reply':
                # Extract comment ID and message
                comment_id = self.extract_yaml_field(content, 'comment_id')

                if not comment_id:
                    logger.error(f"[FACEBOOK] No comment_id found in {file_path.name}")
                    return False

                # Extract reply message
                if "## Message" in content or "## Reply" in content:
                    for marker in ["## Message", "## Reply"]:
                        if marker in content:
                            parts = content.split(marker, 1)
                            if len(parts) > 1:
                                msg_part = parts[1].strip()
                                if "##" in msg_part:
                                    msg_part = msg_part.split("##")[0].strip()
                                message = msg_part
                                break

                if not message:
                    message = "Thank you for your comment!"

                # Reply to comment
                result = manager.reply_to_comment(comment_id, message)

                if result.get('success'):
                    logger.info(f"[FACEBOOK] Reply posted to comment: {comment_id}")
                    self._create_execution_log(file_path, 'facebook_reply', 'success', {
                        'comment_id': comment_id
                    })
                    return True
                else:
                    logger.error(f"[FACEBOOK] Reply failed: {result.get('error')}")
                    return False

            elif action == 'facebook_hide':
                # Extract comment ID
                comment_id = self.extract_yaml_field(content, 'comment_id')

                if not comment_id:
                    logger.error(f"[FACEBOOK] No comment_id found in {file_path.name}")
                    return False

                # Hide comment
                result = manager.hide_comment(comment_id)

                if result.get('success'):
                    logger.info(f"[FACEBOOK] Comment hidden: {comment_id}")
                    self._create_execution_log(file_path, 'facebook_hide', 'success', {
                        'comment_id': comment_id
                    })
                    return True
                else:
                    logger.error(f"[FACEBOOK] Hide failed: {result.get('error')}")
                    return False

            else:
                logger.error(f"[FACEBOOK] Unknown action: {action}")
                return False

        except Exception as e:
            logger.error(f"[FACEBOOK] Error: {e}")
            return False
    
    def execute_facebook_reply(self, file_path: Path) -> bool:
        """Execute approved Facebook reply (separate method for clarity)"""
        try:
            from engine.facebook_manager import FacebookPageManager
            
            logger.info(f"[FACEBOOK] Executing reply: {file_path.name}")
            
            # Read approval file
            content = file_path.read_text(encoding='utf-8')
            
            # Extract comment ID
            comment_id = self.extract_yaml_field(content, 'comment_id')
            
            if not comment_id:
                logger.error(f"[FACEBOOK] No comment_id found in {file_path.name}")
                return False
            
            # Extract reply message from "## AI-Generated Response" section
            if "## AI-Generated Response" in content:
                parts = content.split("## AI-Generated Response", 1)
                if len(parts) > 1:
                    msg_part = parts[1].strip()
                    if "##" in msg_part:
                        msg_part = msg_part.split("##")[0].strip()
                    message = msg_part
                else:
                    message = "Thanks for your interest!"
            else:
                message = "Thanks for your interest!"
            
            # Post reply using Facebook manager
            manager = FacebookPageManager()
            result = manager.post_comment_reply(comment_id, message)
            
            if result.get('success'):
                logger.info(f"[FACEBOOK] Reply posted to comment: {comment_id}")
                self._create_execution_log(file_path, 'facebook_reply', 'success', {
                    'comment_id': comment_id,
                    'reply_id': result.get('reply_id')
                })
                return True
            else:
                logger.error(f"[FACEBOOK] Reply failed: {result.get('error')}")
                return False
        
        except Exception as e:
            logger.error(f"[FACEBOOK] Reply error: {e}")
            return False
    
    def execute_twitter(self, file_path: Path) -> bool:
        """Execute approved Twitter post - MANUAL POSTING WITH IMAGE SUPPORT (FREE)"""
        try:
            logger.info(f"[TWITTER] Processing manual post: {file_path.name}")

            # Read approval file
            content = file_path.read_text(encoding='utf-8')

            # Extract content - check for both "## Content" and "## AI-Generated Content"
            message = ""

            if "## AI-Generated Content" in content:
                # Format from orchestrator with Claude
                parts = content.split("## AI-Generated Content", 1)
                if len(parts) > 1:
                    msg_part = parts[1].strip()
                    if "##" in msg_part:
                        msg_part = msg_part.split("##")[0].strip()
                    message = msg_part
            elif "## Content" in content:
                # Legacy format
                parts = content.split("## Content", 1)
                if len(parts) > 1:
                    msg_part = parts[1].strip()
                    if "##" in msg_part:
                        msg_part = msg_part.split("##")[0].strip()
                    message = msg_part

            if not message:
                logger.error(f"[TWITTER] No content found in {file_path.name}")
                return False

            # Extract diagram image path if present
            image_path = None
            if "## Diagram Image" in content:
                # Extract image path from approval file
                parts = content.split("## Diagram Image", 1)
                if len(parts) > 1:
                    image_part = parts[1].strip()
                    # Look for "Image file: `path`" pattern
                    import re
                    image_match = re.search(r'Image file:\s*`([^`]+)`', image_part)
                    if image_match:
                        image_path = image_match.group(1).strip()
                        logger.info(f"[TWITTER] Found diagram image: {image_path}")

            # Check if thread
            is_thread = 'thread' in file_path.name.lower() or 'thread' in content.lower()

            # Create manual posting instructions
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            manual_post_file = self.done_folder / f"TWITTER_MANUAL_{timestamp}.md"

            # Create URL-encoded tweet for Twitter intent
            import urllib.parse
            tweet_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(message)}"

            if is_thread:
                # For threads, create multiple URLs
                tweets = [t.strip() for t in message.split('\n\n') if t.strip()]
                tweet_urls = []
                for i, tweet in enumerate(tweets):
                    encoded = urllib.parse.quote(tweet)
                    tweet_urls.append(f"https://twitter.com/intent/tweet?text={encoded}")

                # Build thread instructions
                thread_instructions = ""
                for i, url in enumerate(tweet_urls):
                    if i == 0:
                        thread_instructions += f"### Tweet {i+1}:\n**Click:** {url}\n\n"
                    elif i == 1:
                        thread_instructions += f"### Tweet {i+1}:\n**Click:** {url}\n*(Reply to Tweet 1)*\n\n"
                    else:
                        thread_instructions += f"### Tweet {i+1}:\n**Click:** {url}\n*(Reply to Tweet {i})*\n\n"

                manual_content = f"""---
type: twitter_manual_post
action: post_thread
original_file: {file_path.name}
---

# Twitter Thread - Manual Posting Instructions

## Thread Content ({len(tweets)} tweets)

{message}

---

## How to Post This Thread

{thread_instructions}
## Step-by-Step Instructions

1. **Click the first tweet link** above
2. **Click "Tweet"** to post
3. **Click the second tweet link** (it will auto-reply to first)
4. **Click "Tweet"** to post
5. **Repeat** for remaining tweets

---

## Original Approval File

{file_path.name}

---
*Posted manually via AI Employee Vault*
"""
            else:
                # Single tweet with optional image
                if image_path and Path(image_path).exists():
                    manual_content = f"""---
type: twitter_manual_post
action: post_with_image
original_file: {file_path.name}
image_path: {image_path}
---

# Twitter Post with Image - Manual Posting Instructions

## Tweet Content

{message}

---

## Diagram Image

**Image File:** `{image_path}`

**Full Path:** {Path(image_path).absolute()}

---

## How to Post This Tweet with Image

### Option 1: Manual Upload (Recommended)

1. **Open Twitter:** https://twitter.com/home
2. **Click "What is happening?!"**
3. **Paste this text:**

```
{message}
```

4. **Click the image icon** 🖼️
5. **Select the image file:** `{Path(image_path).absolute()}`
6. **Click "Tweet"**

### Option 2: Quick Tweet (Text Only)

**Click:** {tweet_url}

*(Note: Twitter intent URLs don't support image uploads. Use Option 1 for images.)*

---

## Original Approval File

{file_path.name}

---
*Posted manually via AI Employee Vault*
*Image: {Path(image_path).name if image_path else 'None'}*
"""
                else:
                    # No image - just text
                    manual_content = f"""---
type: twitter_manual_post
action: post_text_only
original_file: {file_path.name}
---

# Twitter Post - Manual Posting Instructions

## Tweet Content

{message}

---

## How to Post This Tweet

### Option 1: Quick Tweet

**Click:** {tweet_url}

### Option 2: Manual Post

1. **Open Twitter:** https://twitter.com/home
2. **Click "What is happening?!"**
3. **Paste this text:**

```
{message}
```

4. **Click "Tweet"**

---

## Original Approval File

{file_path.name}

---
*Posted manually via AI Employee Vault*
"""

            # Write manual posting instructions
            manual_post_file.write_text(manual_content, encoding='utf-8')
            logger.info(f"[TWITTER] Created manual post instructions: {manual_post_file.name}")

            # Move original approval file to Done
            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"[TWITTER] Moved to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"[TWITTER] Error: {e}")
            return False

    def process_all_approved(self):
        """Process all approved files in Approved folder"""
        logger.info("[EXECUTOR] Checking for approved actions...")

        # Process email approvals
        for file_path in self.approved_folder.glob("APPROVAL_send_email_*.md"):
            self.process_approved_file(file_path)

        # Process WhatsApp approvals
        for file_path in self.approved_folder.glob("APPROVAL_send_whatsapp_*.md"):
            self.process_approved_file(file_path)

        # Process LinkedIn approvals (both patterns)
        for file_path in self.approved_folder.glob("APPROVAL_linkedin_post_*.md"):
            self.process_approved_file(file_path)
        for file_path in self.approved_folder.glob("APPROVAL_linkedin_*.md"):
            self.process_approved_file(file_path)
        for file_path in self.approved_folder.glob("LINKEDIN_POST_*.md"):
            self.process_approved_file(file_path)

        # Process Twitter approvals (NEW!)
        for file_path in self.approved_folder.glob("APPROVAL_twitter_*.md"):
            self.process_approved_file(file_path)

        # Process Facebook approvals
        for file_path in self.approved_folder.glob("APPROVAL_facebook_*.md"):
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
