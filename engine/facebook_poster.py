"""
Facebook Page Poster - Official Graph API
100% Reliable - No bans, no issues
Posts to Facebook Page using Graph API
"""

import requests
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))
from engine.logger import logger


class FacebookPoster:
    """Post to Facebook Page using Graph API"""
    
    def __init__(self):
        """Initialize Facebook Poster with credentials from .env"""
        self.page_access_token = os.getenv('FACEBOOK_PAGE_TOKEN', '')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID', '')
        self.graph_url = "https://graph.facebook.com/v18.0"
        
        if not self.page_access_token or not self.page_id:
            logger.error("❌ Facebook credentials not found in .env!")
            logger.error("Add FACEBOOK_PAGE_TOKEN and FACEBOOK_PAGE_ID to .env")
            raise ValueError("Facebook credentials missing")
        
        logger.info("✅ Facebook Poster initialized (Graph API)")
        logger.info(f"   Page ID: {self.page_id}")
    
    def post_to_page(self, message, link=None, photo_url=None):
        """
        Post to Facebook Page
        
        Args:
            message: Post text
            link: Optional link to share
            photo_url: Optional photo URL
        
        Returns:
            dict: Post result with post_id
        """
        try:
            endpoint = f"{self.graph_url}/{self.page_id}/feed"
            
            data = {
                'message': message,
                'access_token': self.page_access_token
            }
            
            if link:
                data['link'] = link
            
            if photo_url:
                data['picture'] = photo_url
            
            logger.info(f"📝 Posting to Facebook: {message[:50]}...")
            
            response = requests.post(endpoint, data=data, timeout=30)
            result = response.json()
            
            if 'id' in result:
                logger.info(f"✅ Facebook post created: {result['id']}")
                return {'success': True, 'post_id': result['id']}
            else:
                logger.error(f"❌ Facebook post failed: {result}")
                return {'success': False, 'error': result}
                
        except Exception as e:
            logger.error(f"❌ Facebook posting error: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_photo_post(self, message, photo_path):
        """
        Post photo to Facebook Page
        
        Args:
            message: Post caption
            photo_path: Local path to photo
        
        Returns:
            dict: Post result
        """
        try:
            endpoint = f"{self.graph_url}/{self.page_id}/photos"
            
            if not Path(photo_path).exists():
                logger.error(f"❌ Photo not found: {photo_path}")
                return {'success': False, 'error': 'Photo not found'}
            
            with open(photo_path, 'rb') as photo_file:
                files = {'photo': photo_file}
                data = {
                    'caption': message,
                    'access_token': self.page_access_token
                }
                
                logger.info(f"📸 Posting photo to Facebook: {message[:50]}...")
                
                response = requests.post(endpoint, files=files, data=data, timeout=60)
                result = response.json()
                
                if 'id' in result:
                    logger.info(f"✅ Facebook photo post created: {result['id']}")
                    return {'success': True, 'post_id': result['id']}
                else:
                    logger.error(f"❌ Facebook photo post failed: {result}")
                    return {'success': False, 'error': result}
                    
        except Exception as e:
            logger.error(f"❌ Facebook photo posting error: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_connection(self):
        """Test Facebook API connection"""
        try:
            endpoint = f"{self.graph_url}/{self.page_id}"
            params = {'access_token': self.page_access_token}
            
            response = requests.get(endpoint, params=params, timeout=10)
            result = response.json()
            
            if 'id' in result:
                logger.info(f"✅ Facebook connection successful!")
                logger.info(f"   Page: {result.get('name', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ Facebook connection failed: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Facebook connection error: {e}")
            return False


# Test the poster
if __name__ == "__main__":
    print("="*60)
    print("FACEBOOK POSTER TEST")
    print("="*60)
    print()
    
    try:
        poster = FacebookPoster()
        
        # Test connection
        print("1. Testing Facebook connection...")
        if poster.test_connection():
            print("   ✅ Connection successful!")
        else:
            print("   ❌ Connection failed!")
            sys.exit(1)
        
        # Test text post
        print("\n2. Testing text post...")
        result = poster.post_to_page(
            message="🚀 Hello from AI Employee Vault!\n\nAutomated Facebook posting works!\n\n#AI #Automation #Facebook"
        )
        
        if result.get('success'):
            print(f"   ✅ Post created: {result['post_id']}")
        else:
            print(f"   ❌ Post failed: {result.get('error')}")
        
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nMake sure you have:")
        print("1. FACEBOOK_PAGE_TOKEN in .env")
        print("2. FACEBOOK_PAGE_ID in .env")
        print("3. Valid Facebook Page Access Token")
