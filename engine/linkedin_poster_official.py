"""
LinkedIn Poster - Official API
100% Reliable - Official LinkedIn API
Requires approved LinkedIn Developer App
"""

import requests
import time
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.logger import logger


class LinkedInPoster:
    """Posts to LinkedIn using Official API"""
    
    def __init__(self):
        # LinkedIn API Credentials
        # Get from: https://www.linkedin.com/developers/apps
        self.client_id = "YOUR_CLIENT_ID"
        self.client_secret = "YOUR_CLIENT_SECRET"
        self.access_token = "YOUR_ACCESS_TOKEN"
        self.person_urn = "YOUR_PERSON_URN"
        
        logger.info("✅ LinkedIn Official API poster initialized")
    
    def extract_post_content(self, filepath):
        """Extract post content from approval file"""
        try:
            content = filepath.read_text(encoding='utf-8')
            
            if "## Post Content" in content:
                parts = content.split("## Post Content", 1)
                if len(parts) > 1:
                    post_section = parts[1]
                    if "##" in post_section:
                        post_content = post_section.split("##")[0].strip()
                    else:
                        post_content = post_section.strip()
                    
                    return post_content, None
            
            logger.error("❌ Could not find post content")
            return "", None
        except Exception as e:
            logger.error(f"❌ Error extracting content: {e}")
            return "", None
    
    def create_post(self, text):
        """Create LinkedIn post via Official API"""
        try:
            logger.info(f"📝 Creating LinkedIn post via Official API...")
            logger.info(f"   Content length: {len(text)} characters")
            
            # LinkedIn API endpoint for creating posts
            url = "https://api.linkedin.com/v2/shares"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            # Prepare post data
            data = {
                "owner": f"urn:li:person:{self.person_urn}",
                "text": {
                    "text": text[:3000]  # LinkedIn limit: 3000 characters
                },
                "distribution": {
                    "feedDistribution": "MAIN_FEED",
                    "targetEntities": [],
                    "thirdPartyDistributionChannels": []
                }
            }
            
            # Send request
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                result = response.json()
                post_id = result.get('id', 'Unknown')
                logger.info(f"✅ LinkedIn post published!")
                logger.info(f"   Post ID: {post_id}")
                return True
            else:
                logger.error(f"❌ Post failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating post: {e}")
            return False
    
    def refresh_token(self):
        """Refresh access token (if using refresh token flow)"""
        # Implement if needed for long-term use
        pass
    
    def process_approved_post(self, filepath):
        """Process approved post"""
        try:
            logger.info(f"📋 Processing: {filepath.name}")
            
            # Extract content
            content, _ = self.extract_post_content(filepath)
            if not content:
                logger.error("❌ No content")
                return False
            
            # Create post
            success = self.create_post(content)
            
            if success:
                logger.info("✅ Post published successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False


if __name__ == "__main__":
    print("="*60)
    print("LINKEDIN OFFICIAL API - TEST")
    print("="*60)
    print()
    print("Before using this, you must:")
    print("1. Create LinkedIn Developer App")
    print("2. Get API permissions approved")
    print("3. Generate access token")
    print("4. Update credentials in linkedin_poster.py")
    print()
    print("Get started: https://www.linkedin.com/developers/apps")
    print()
