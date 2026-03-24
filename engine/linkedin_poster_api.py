"""
LinkedIn Poster - API Version
Posts to LinkedIn using linkedin-api package
No browser automation needed!
"""

from linkedin_api import Linkedin
from pathlib import Path
import json
import time
from datetime import datetime
import sys
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import APPROVED_FOLDER, DONE_FOLDER, REJECTED_FOLDER
from engine.logger import logger


class LinkedInPoster:
    """Posts to LinkedIn using API"""
    
    def __init__(self, session_path: Optional[str] = None):
        """Initialize LinkedIn API client"""
        self.api = None
        self.session_path = Path(session_path or "linkedin_session")
        self.config_file = Path("/home/AI_Employee/linkedin_config.py")
        logger.info("✅ LinkedIn API poster initialized")
    
    def authenticate(self):
        """Authenticate with LinkedIn API"""
        try:
            # Import credentials from config
            import importlib.util
            spec = importlib.util.spec_from_file_location("linkedin_config", str(self.config_file))
            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)
            
            email = config.LINKEDIN_EMAIL
            password = config.LINKEDIN_PASSWORD
            
            logger.info(f"🔑 Authenticating with LinkedIn API...")
            
            # Create LinkedIn API client
            self.api = Linkedin(email, password)
            
            # Test connection
            try:
                profile = self.api.get_profile()
                if profile:
                    logger.info(f"✅ LinkedIn authenticated successfully!")
                    first_name = profile.get('firstName', 'User')
                    logger.info(f"   Profile: {first_name}")
                    return True
                else:
                    logger.error("❌ LinkedIn authentication failed!")
                    return False
            except Exception as profile_error:
                # Profile might not be available, but auth worked
                logger.info(f"✅ LinkedIn authenticated (profile access limited)")
                return True
                
        except Exception as e:
            logger.error(f"❌ LinkedIn API authentication error: {e}")
            logger.error("   Make sure credentials in linkedin_config.py are correct")
            return False
    
    def extract_post_content(self, filepath: Path) -> tuple[str, Optional[str]]:
        """Extract post content from approval file"""
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
    
    def create_post(self, text: str, image_path: Optional[str] = None) -> bool:
        """Create LinkedIn post via API"""
        try:
            logger.info(f"📝 Creating LinkedIn post...")
            logger.info(f"   Content length: {len(text)} characters")
            
            # LinkedIn API allows up to 3000 characters
            if len(text) > 3000:
                text = text[:2997] + "..."
                logger.warning("⚠️  Post truncated to 3000 characters")
            
            # Create post using LinkedIn API
            # Note: Image posting requires additional API permissions
            # For now, we'll post text-only
            if image_path:
                logger.info(f"📎 Image detected: {image_path}")
                logger.warning("⚠️  Image posting requires LinkedIn API approval - posting text only")
            
            # Post to LinkedIn
            response = self.api.create_post(text)
            
            if response:
                logger.info(f"✅ LinkedIn post published successfully!")
                logger.info(f"   Post ID: {response}")
                return True
            else:
                logger.error("❌ Failed to create LinkedIn post")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating LinkedIn post: {e}")
            return False
    
    def process_approved_post(self, filepath: Path) -> bool:
        """Process an approved LinkedIn post"""
        try:
            logger.info(f"📋 Processing approved post: {filepath.name}")
            
            # Authenticate if not already done
            if not self.api:
                if not self.authenticate():
                    logger.error("❌ Authentication failed")
                    return False
            
            # Extract post content
            post_content, image_path = self.extract_post_content(filepath)
            
            if not post_content:
                logger.error("❌ No post content found")
                return False
            
            # Create the post
            success = self.create_post(post_content, image_path)
            
            if success:
                logger.info(f"✅ Post published successfully")
                return True
            else:
                logger.error("❌ Failed to publish post")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error processing approved post: {e}")
            return False
    
    def watch_approved_folder(self, check_interval: int = 30):
        """Watch Approved folder for LinkedIn posts"""
        logger.info(f"👀 Watching Approved folder for LinkedIn posts (every {check_interval}s)")
        logger.info("Press Ctrl+C to stop")

        while True:
            try:
                # Check for LinkedIn post files in Approved folder
                approved_posts = list(APPROVED_FOLDER.glob("LINKEDIN_POST_*.md"))
                approved_posts += list(APPROVED_FOLDER.glob("APPROVAL_linkedin_post_*.md"))

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
    # Test the poster
    print("Testing LinkedIn API Poster...")
    poster = LinkedInPoster()
    
    if poster.authenticate():
        print("\n✅ Authentication successful!")
        
        # Test post
        test_post = """🚀 Excited to share our new AI automation project!

We've built an AI Employee that can:
✅ Monitor emails 24/7
✅ Auto-respond to messages
✅ Create CRM leads
✅ Post to social media

#AI #Automation #Innovation #Tech"""
        
        if poster.create_post(test_post):
            print("\n✅ Test post published!")
        else:
            print("\n❌ Test post failed")
    else:
        print("\n❌ Authentication failed")
