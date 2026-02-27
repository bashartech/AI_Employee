"""
LinkedIn Poster module
Handles creating LinkedIn posts with approval workflow
"""

import time
import sys
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import APPROVED_FOLDER, DONE_FOLDER, REJECTED_FOLDER
from engine.logger import logger


class LinkedInPoster:
    """
    Handles LinkedIn post creation with approval workflow
    """

    def __init__(self, session_path: Optional[str] = None):
        """
        Initialize LinkedIn poster

        Args:
            session_path: Path to browser session
        """
        self.session_path = Path(session_path or "linkedin_session")
        logger.info("✅ LinkedIn poster initialized")

    def extract_post_content(self, filepath: Path) -> tuple[str, Optional[str]]:
        """
        Extract post content from approval file

        Args:
            filepath: Path to approved post file

        Returns:
            Tuple of (post_content, image_path)
        """
        try:
            content = filepath.read_text(encoding='utf-8')

            # Extract post content (between ## Post Content and next ##)
            if "## Post Content" in content:
                parts = content.split("## Post Content")
                if len(parts) > 1:
                    # Get everything after ## Post Content
                    post_section = parts[1]

                    # Find next ## marker
                    if "##" in post_section:
                        post_content = post_section.split("##")[0].strip()
                    else:
                        post_content = post_section.strip()

                    # Extract image path if present
                    image_path = None
                    if "**Image:**" in content:
                        for line in content.split('\n'):
                            if '**Image:**' in line:
                                img = line.split('**Image:**')[1].strip()
                                if img and img != 'None':
                                    image_path = img
                                break

                    return post_content, image_path

            logger.error("❌ Could not find post content in file")
            return "", None

        except Exception as e:
            logger.error(f"❌ Error extracting post content: {e}")
            return "", None

    def create_post(self, content: str, image_path: Optional[str] = None) -> bool:
        """
        Create a LinkedIn post

        Args:
            content: Post content
            image_path: Optional path to image

        Returns:
            True if post was created successfully
        """
        browser = None
        try:
            with sync_playwright() as p:
                logger.info("📝 Creating LinkedIn post...")

                # Launch browser with session - increased timeout
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Show browser for posting
                    args=['--no-sandbox'],
                    timeout=120000  # 2 minute timeout for browser launch
                )

                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn with longer timeout and wait for network
                logger.info("🌐 Navigating to LinkedIn...")
                page.goto('https://www.linkedin.com/feed/', timeout=60000, wait_until='networkidle')
                
                # Wait a bit more for page to fully load
                time.sleep(5)

                # Check if logged in
                current_url = page.url
                if 'login' in current_url or 'authwall' in current_url:
                    logger.error("❌ Not logged in to LinkedIn")
                    logger.info("⚠️ Please login in the browser window")
                    logger.info("⏳ Waiting 60 seconds for manual login...")
                    time.sleep(60)
                    # Check again
                    current_url = page.url
                    if 'login' in current_url or 'authwall' in current_url:
                        logger.error("❌ Still not logged in. Please run setup first.")
                        browser.close()
                        return False

                logger.info("✅ Logged in to LinkedIn")

                # Wait for feed to load with longer timeout
                logger.info("⏳ Waiting for feed to load...")
                try:
                    page.wait_for_selector('[class*="share-box"]', timeout=30000)
                except PlaywrightTimeout:
                    logger.warning("⚠️ Share box not found, trying alternative...")
                    # Try scrolling to trigger lazy loading
                    page.evaluate("window.scrollTo(0, 200)")
                    time.sleep(3)
                    page.wait_for_selector('[class*="share-box"]', timeout=10000)

                logger.info("✅ Feed loaded successfully")

                # Click "Start a post" button
                start_post_btn = page.query_selector('[class*="share-box"]')
                if not start_post_btn:
                    logger.error("❌ Could not find 'Start a post' button")
                    browser.close()
                    return False

                start_post_btn.click()
                logger.info("⏳ Waiting for post dialog to open...")
                time.sleep(5)  # Wait longer for dialog animation

                # Find the post editor - try multiple selectors
                editor = None
                editor_selectors = [
                    '[class*="ql-editor"]',
                    '.ql-editor',
                    '[contenteditable="true"]',
                    '[role="textbox"]',
                    'div[data-placeholder*="share"]',
                    '[aria-label*="What do you want to share?"]',
                ]

                for selector in editor_selectors:
                    try:
                        logger.info(f"🔍 Trying selector: {selector}")
                        if page.wait_for_selector(selector, timeout=5000):
                            editor = page.query_selector(selector)
                            if editor:
                                logger.info(f"✅ Found editor with: {selector}")
                                break
                    except Exception as e:
                        logger.info(f"⚠️ Selector {selector} not found")
                        continue

                if not editor:
                    logger.error("❌ Could not find post editor with any selector")
                    logger.info("🔍 Keeping browser open for 30 seconds for inspection...")
                    time.sleep(30)
                    browser.close()
                    return False

                # Type the content - use slower typing for reliability
                logger.info("⌨️ Typing post content...")
                editor.click()
                time.sleep(2)
                
                # Type content in chunks to avoid issues
                editor.fill(content)
                time.sleep(3)  # Wait for fill to complete

                # Add image if provided
                if image_path and Path(image_path).exists():
                    try:
                        logger.info(f"🖼️ Adding image: {image_path}")

                        # Find image button
                        image_btn = page.query_selector('[aria-label*="Add a photo"]')
                        if not image_btn:
                            image_btn = page.query_selector('[data-test-icon="image-medium"]')

                        if image_btn:
                            image_btn.click()
                            time.sleep(2)

                            # Upload image
                            file_input = page.query_selector('input[type="file"]')
                            if file_input:
                                file_input.set_input_files(str(Path(image_path).absolute()))
                                time.sleep(5)  # Wait for upload
                                logger.info("✅ Image uploaded")
                            else:
                                logger.warning("⚠️ Could not find file input")
                        else:
                            logger.warning("⚠️ Could not find image button")

                    except Exception as e:
                        logger.warning(f"⚠️ Could not add image: {e}")

                # Find and click Post button
                logger.info("📤 Publishing post...")
                
                # Wait for post button to be enabled
                time.sleep(3)
                
                post_btn = page.query_selector('[class*="share-actions__primary-action"]')

                if not post_btn:
                    # Try alternative selector
                    post_btn = page.query_selector('button[type="submit"]')

                if not post_btn:
                    # Try text-based selector
                    post_btn = page.query_selector('button:has-text("Post")')

                if post_btn:
                    post_btn.click()
                    logger.info("⏳ Waiting for post to publish...")
                    time.sleep(8)  # Wait for post to complete

                    logger.info("✅ LinkedIn post published successfully!")
                    browser.close()
                    return True
                else:
                    logger.error("❌ Could not find Post button")
                    logger.info("🔍 Keeping browser open for 30 seconds for inspection...")
                    time.sleep(30)
                    browser.close()
                    return False

        except Exception as e:
            logger.error(f"❌ Error creating LinkedIn post: {e}")
            if browser:
                try:
                    browser.close()
                except:
                    pass
            return False

    def process_approved_post(self, filepath: Path) -> bool:
        """
        Process an approved post file

        Args:
            filepath: Path to approved post file

        Returns:
            True if post was created successfully
        """
        try:
            logger.info(f"📋 Processing approved post: {filepath.name}")

            # Extract content
            post_content, image_path = self.extract_post_content(filepath)

            if not post_content:
                logger.error("❌ No post content found")
                return False

            # Create the post
            success = self.create_post(post_content, image_path)

            if success:
                # Move to Done folder
                done_path = DONE_FOLDER / filepath.name
                filepath.rename(done_path)
                logger.info(f"✅ Post published and moved to Done: {filepath.name}")
                return True
            else:
                logger.error("❌ Failed to publish post")
                return False

        except Exception as e:
            logger.error(f"❌ Error processing approved post: {e}")
            return False

    def watch_approved_folder(self, check_interval: int = 30):
        """
        Watch Approved folder for LinkedIn posts

        Args:
            check_interval: Seconds between checks
        """
        logger.info(f"👀 Watching Approved folder for LinkedIn posts (every {check_interval}s)")
        logger.info("Press Ctrl+C to stop")

        while True:
            try:
                # Check for LinkedIn post files in Approved folder
                approved_posts = list(APPROVED_FOLDER.glob("LINKEDIN_POST_*.md"))

                if approved_posts:
                    logger.info(f"📬 Found {len(approved_posts)} approved posts")

                    for post_file in approved_posts:
                        self.process_approved_post(post_file)

                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("🛑 Stopping approved folder watcher...")
                break
            except Exception as e:
                logger.error(f"❌ Error in watch loop: {e}")
                time.sleep(check_interval)


if __name__ == "__main__":
    # Watch for approved posts
    poster = LinkedInPoster()
    poster.watch_approved_folder()
