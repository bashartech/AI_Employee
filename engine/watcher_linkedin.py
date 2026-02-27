"""
LinkedIn Watcher and Poster module
Monitors LinkedIn messages and creates posts for business generation
Uses Playwright for web automation (LinkedIn API is restricted)
"""

import time
import sys
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from typing import List, Dict, Any, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import NEEDS_ACTION_FOLDER, PENDING_APPROVAL_FOLDER, ensure_folders_exist
from engine.logger import logger


class LinkedInWatcher:
    """
    LinkedIn automation using Playwright
    Monitors messages and creates posts
    """

    def __init__(self, session_path: Optional[str] = None):
        """
        Initialize LinkedIn watcher

        Args:
            session_path: Path to store browser session (stays logged in)
        """
        self.session_path = Path(session_path or "linkedin_session")
        self.session_path.mkdir(exist_ok=True)

        # Keywords to watch for in messages
        self.urgent_keywords = [
            'urgent', 'asap', 'important', 'help', 'inquiry',
            'quote', 'pricing', 'proposal', 'meeting', 'call',
            'interested', 'opportunity', 'project', 'hire', 'work'
        ]

        self.processed_messages = set()
        self.running = False

        logger.info("✅ LinkedIn watcher initialized")

    def is_logged_in(self, page) -> bool:
        """
        Check if user is logged in to LinkedIn

        Args:
            page: Playwright page object

        Returns:
            True if logged in
        """
        try:
            # Check URL
            if 'login' in page.url or 'authwall' in page.url:
                return False

            # Check for feed or messaging elements
            page.wait_for_selector('[class*="global-nav"]', timeout=5000)
            return True

        except:
            return False

    def check_messages(self) -> List[Dict[str, Any]]:
        """
        Check for new LinkedIn messages

        Returns:
            List of new messages
        """
        messages = []

        try:
            with sync_playwright() as p:
                logger.info("🔍 Checking LinkedIn messages...")

                # Launch browser with persistent session
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True,
                    args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                # Navigate to messaging
                page.goto('https://www.linkedin.com/messaging/', timeout=30000)

                # Wait longer for page to load
                time.sleep(5)

                # Check if we got redirected
                current_url = page.url
                if 'messaging' not in current_url:
                    logger.warning(f"⚠️ Redirected to: {current_url}")
                    logger.info("Trying to navigate back to messaging...")
                    page.goto('https://www.linkedin.com/messaging/', timeout=30000)
                    time.sleep(5)

                # Check if logged in
                if not self.is_logged_in(page):
                    logger.warning("⚠️ LinkedIn session expired - manual login required")
                    logger.info("Run: python setup_linkedin.py to login")
                    browser.close()
                    return messages

                # Wait for messaging interface with longer timeout
                try:
                    # Try multiple selectors for the messaging container
                    selectors = [
                        '[class*="msg-conversations-container"]',
                        '[class*="msg-overlay"]',
                        '[class*="messaging-container"]',
                        'main[role="main"]'
                    ]

                    found = False
                    for selector in selectors:
                        try:
                            page.wait_for_selector(selector, timeout=5000)
                            logger.info(f"✅ Found messaging interface with: {selector}")
                            found = True
                            break
                        except:
                            continue

                    if not found:
                        logger.warning("⚠️ Could not load messaging interface")
                        logger.info(f"Current URL: {page.url}")
                        browser.close()
                        return messages

                except PlaywrightTimeout:
                    logger.warning("⚠️ Could not load messaging interface")
                    browser.close()
                    return messages

                # Wait a bit more for conversations to load
                time.sleep(3)

                # Try multiple selectors for unread conversations
                unread_selectors = [
                    '[class*="msg-conversation-listitem"][class*="unread"]',
                    '[class*="msg-conversation-card"][class*="unread"]',
                    'li[class*="unread"]',
                    '[aria-label*="unread"]',
                ]

                unread_convos = []
                for selector in unread_selectors:
                    try:
                        unread_convos = page.query_selector_all(selector)
                        if unread_convos:
                            logger.info(f"✅ Found unread with selector: {selector}")
                            break
                    except:
                        continue

                if not unread_convos:
                    logger.info("📭 No new messages")
                    browser.close()
                    return messages

                logger.info(f"📬 Found {len(unread_convos)} unread conversations")

                for convo in unread_convos[:5]:  # Limit to 5 most recent
                    try:
                        # Click conversation to open
                        convo.click()
                        time.sleep(2)

                        # Get sender name
                        sender_elem = page.query_selector('[class*="msg-thread__link-to-profile"]')
                        sender = sender_elem.inner_text().strip() if sender_elem else "Unknown"

                        # Get latest messages
                        message_elems = page.query_selector_all('[class*="msg-s-message-list__event"]')
                        if message_elems:
                            # Get last message (most recent)
                            latest_msg_elem = message_elems[-1]
                            msg_text_elem = latest_msg_elem.query_selector('[class*="msg-s-event-listitem__body"]')
                            msg_text = msg_text_elem.inner_text().strip() if msg_text_elem else ""

                            if msg_text:
                                # Create unique ID
                                msg_id = f"{sender.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                                if msg_id not in self.processed_messages:
                                    # Check if urgent
                                    is_urgent = any(kw in msg_text.lower() for kw in self.urgent_keywords)

                                    messages.append({
                                        'id': msg_id,
                                        'sender': sender,
                                        'message': msg_text,
                                        'timestamp': datetime.now().isoformat(),
                                        'urgent': is_urgent
                                    })

                                    self.processed_messages.add(msg_id)
                                    logger.info(f"📨 New message from {sender} {'(URGENT)' if is_urgent else ''}")

                    except Exception as e:
                        logger.error(f"❌ Error processing conversation: {e}")
                        continue

                browser.close()

        except Exception as e:
            logger.error(f"❌ Error checking LinkedIn messages: {e}")

        return messages

    def create_message_task(self, message: Dict[str, Any]):
        """
        Create a task file for a new LinkedIn message

        Args:
            message: Message data
        """
        try:
            priority = "🔴 HIGH" if message['urgent'] else "🟢 NORMAL"

            task_content = f"""# LinkedIn Message from {message['sender']}

**From:** {message['sender']}
**Received:** {message['timestamp']}
**Priority:** {priority}
**Type:** LinkedIn Message

## Message Content

{message['message']}

## Suggested Actions

- [ ] Reply to {message['sender']}
- [ ] Send additional information
- [ ] Schedule a call/meeting
- [ ] Forward to team member
- [ ] Create LinkedIn post to attract similar inquiries

## AI Analysis

*Qwen will analyze this message and suggest appropriate actions*

## Notes

Add your notes here...
"""

            filename = f"LINKEDIN_MSG_{message['id']}.md"
            filepath = NEEDS_ACTION_FOLDER / filename
            filepath.write_text(task_content, encoding='utf-8')

            logger.info(f"✅ Created task: {filename}")

        except Exception as e:
            logger.error(f"❌ Error creating message task: {e}")

    def start_monitoring(self, check_interval: int = 300):
        """
        Start monitoring LinkedIn messages

        Args:
            check_interval: Seconds between checks (default: 5 minutes)
        """
        self.running = True
        logger.info(f"👀 LinkedIn monitoring started (checking every {check_interval}s)")
        logger.info("Press Ctrl+C to stop")

        while self.running:
            try:
                # Check for new messages
                messages = self.check_messages()

                # Create tasks for new messages
                for message in messages:
                    self.create_message_task(message)

                if messages:
                    logger.info(f"✅ Processed {len(messages)} new messages")

                # Wait before next check
                logger.info(f"⏳ Next check in {check_interval} seconds...")
                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("🛑 Stopping LinkedIn monitoring...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                logger.info(f"⏳ Retrying in {check_interval} seconds...")
                time.sleep(check_interval)

    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        logger.info("🛑 LinkedIn monitoring stopped")


if __name__ == "__main__":
    # Ensure folders exist
    ensure_folders_exist()

    # Start monitoring
    watcher = LinkedInWatcher()
    watcher.start_monitoring()
