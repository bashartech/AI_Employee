"""
Facebook Page Manager - Complete API Integration
Manage posts, comments, analytics, and page settings
"""

import requests
from pathlib import Path
import sys
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))
from engine.logger import logger


class FacebookPageManager:
    """Complete Facebook Page management via Graph API"""
    
    def __init__(self):
        """Initialize with credentials from .env"""
        self.page_access_token = os.getenv('FACEBOOK_PAGE_TOKEN', '')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID', '')
        self.graph_url = "https://graph.facebook.com/v18.0"
        
        if not self.page_access_token or not self.page_id:
            logger.error("❌ Facebook credentials not found in .env!")
            raise ValueError("Facebook credentials missing")
        
        logger.info(f"✅ Facebook Page Manager initialized")
        logger.info(f"   Page ID: {self.page_id}")
    
    # ==================== POST MANAGEMENT ====================
    
    def create_post(self, message, link=None, photo_url=None, scheduled_time=None):
        """Create a post on Facebook Page"""
        try:
            if scheduled_time:
                # Scheduled post
                endpoint = f"{self.graph_url}/{self.page_id}/scheduled_posts"
                data = {
                    'message': message,
                    'published': False,
                    'scheduled_publish_time': int(scheduled_time.timestamp()),
                    'access_token': self.page_access_token
                }
            else:
                # Immediate post
                endpoint = f"{self.graph_url}/{self.page_id}/feed"
                data = {
                    'message': message,
                    'access_token': self.page_access_token
                }

            if link:
                data['link'] = link
            if photo_url:
                data['picture'] = photo_url

            response = requests.post(endpoint, data=data, timeout=30)
            result = response.json()

            if 'id' in result:
                logger.info(f"✅ Facebook post created: {result['id']}")
                return {'success': True, 'post_id': result['id']}
            else:
                logger.error(f"❌ Facebook post failed: {result}")
                return {'success': False, 'error': result}

        except Exception as e:
            logger.error(f"❌ Facebook post error: {e}")
            return {'success': False, 'error': str(e)}

    def create_post_with_local_image(self, message, image_path):
        """Create a post on Facebook Page with local image file"""
        try:
            endpoint = f"{self.graph_url}/{self.page_id}/photos"
            
            # Read image file
            with open(image_path, 'rb') as img_file:
                files = {'source': img_file}
                data = {
                    'message': message,
                    'access_token': self.page_access_token
                }
                
                response = requests.post(endpoint, files=files, data=data, timeout=30)
                result = response.json()

                if 'id' in result:
                    logger.info(f"✅ Facebook post with image created: {result['id']}")
                    return {'success': True, 'post_id': result['id']}
                else:
                    logger.error(f"❌ Facebook post with image failed: {result}")
                    return {'success': False, 'error': result}

        except Exception as e:
            logger.error(f"❌ Facebook post with image error: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_post(self, post_id):
        """Delete a post from Facebook Page"""
        try:
            endpoint = f"{self.graph_url}/{post_id}"
            data = {'access_token': self.page_access_token}
            
            response = requests.delete(endpoint, data=data, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ Facebook post deleted: {post_id}")
                return {'success': True}
            else:
                logger.error(f"❌ Failed to delete post: {response.json()}")
                return {'success': False, 'error': response.json()}
                
        except Exception as e:
            logger.error(f"❌ Facebook delete error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_posts(self, limit=10):
        """Get recent posts from Page"""
        try:
            endpoint = f"{self.graph_url}/{self.page_id}/posts"
            params = {
                'limit': limit,
                'fields': 'id,message,created_time,updated_time,permalink_url,shares,reactions.summary(true),comments.summary(true)',
                'access_token': self.page_access_token
            }
            
            response = requests.get(endpoint, params=params, timeout=30)
            result = response.json()
            
            if 'data' in result:
                return {'success': True, 'posts': result['data']}
            else:
                return {'success': False, 'error': result}
                
        except Exception as e:
            logger.error(f"❌ Facebook get posts error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==================== COMMENT MANAGEMENT ====================
    
    def get_comments(self, post_id, limit=10):
        """Get comments on a post"""
        try:
            endpoint = f"{self.graph_url}/{post_id}/comments"
            params = {
                'limit': limit,
                'fields': 'id,from,message,created_time,like_count',
                'access_token': self.page_access_token
            }

            response = requests.get(endpoint, params=params, timeout=30)
            result = response.json()

            if 'data' in result:
                return {'success': True, 'comments': result['data']}
            else:
                return {'success': False, 'error': result}

        except Exception as e:
            logger.error(f"❌ Facebook get comments error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_page_comments(self, limit=50):
        """
        Get recent comments from all page posts
        Used by facebook_comment_monitor.py
        """
        try:
            # First get recent posts
            posts_result = self.get_posts(limit=10)
            
            if not posts_result.get('success'):
                return posts_result
            
            all_comments = []
            
            # Get comments from each post
            for post in posts_result.get('posts', [])[:5]:  # Check last 5 posts
                post_id = post.get('id')
                if post_id:
                    comments_result = self.get_comments(post_id, limit=limit//5)
                    if comments_result.get('success'):
                        comments = comments_result.get('comments', [])
                        # Add post_id to each comment for reference
                        for comment in comments:
                            comment['post_id'] = post_id
                        all_comments.extend(comments)
            
            # Sort by created_time (newest first)
            all_comments.sort(
                key=lambda x: x.get('created_time', ''),
                reverse=True
            )
            
            logger.info(f"✅ Retrieved {len(all_comments)} page comments")
            return {'success': True, 'comments': all_comments}
            
        except Exception as e:
            logger.error(f"❌ Facebook get page comments error: {e}")
            return {'success': False, 'error': str(e)}
    
    def reply_to_comment(self, comment_id, message):
        """Reply to a comment"""
        try:
            endpoint = f"{self.graph_url}/{comment_id}/comments"
            data = {
                'message': message,
                'access_token': self.page_access_token
            }

            response = requests.post(endpoint, data=data, timeout=30)
            result = response.json()

            if 'id' in result:
                logger.info(f"✅ Reply posted to comment: {comment_id}")
                return {'success': True, 'comment_id': result['id']}
            else:
                return {'success': False, 'error': result}

        except Exception as e:
            logger.error(f"❌ Facebook reply error: {e}")
            return {'success': False, 'error': str(e)}
    
    def post_comment_reply(self, comment_id, message):
        """
        Reply to a comment on your page
        Alias for reply_to_comment - used by execute_approved.py
        """
        return self.reply_to_comment(comment_id, message)
    
    def hide_comment(self, comment_id):
        """Hide a comment (still visible to commenter)"""
        try:
            endpoint = f"{self.graph_url}/{comment_id}"
            data = {
                'is_hidden': True,
                'access_token': self.page_access_token
            }
            
            response = requests.post(endpoint, data=data, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ Comment hidden: {comment_id}")
                return {'success': True}
            else:
                return {'success': False, 'error': response.json()}
                
        except Exception as e:
            logger.error(f"❌ Facebook hide comment error: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_comment(self, comment_id):
        """Delete a comment"""
        try:
            endpoint = f"{self.graph_url}/{comment_id}"
            data = {'access_token': self.page_access_token}
            
            response = requests.delete(endpoint, data=data, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ Comment deleted: {comment_id}")
                return {'success': True}
            else:
                return {'success': False, 'error': response.json()}
                
        except Exception as e:
            logger.error(f"❌ Facebook delete comment error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==================== ANALYTICS ====================
    
    def get_page_insights(self, metric='page_impressions', days=7):
        """Get page insights/analytics"""
        try:
            endpoint = f"{self.graph_url}/{self.page_id}/insights"

            since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            until = datetime.now().strftime('%Y-%m-%d')

            params = {
                'metric': metric,
                'since': since,
                'until': until,
                'access_token': self.page_access_token
            }

            response = requests.get(endpoint, params=params, timeout=30)
            result = response.json()

            if 'data' in result:
                return {'success': True, 'insights': result['data']}
            else:
                # Extract error message properly
                error_msg = 'Unknown error'
                if isinstance(result, dict):
                    if 'error' in result:
                        error_msg = result['error'].get('message', 'Unknown error')
                    else:
                        error_msg = str(result)
                return {'success': False, 'error': error_msg}

        except Exception as e:
            logger.error(f"❌ Facebook insights error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_post_insights(self, post_id):
        """Get insights for a specific post"""
        try:
            endpoint = f"{self.graph_url}/{post_id}/insights"
            params = {
                'metric': 'post_impressions,post_engagements,post_clicks,post_reactions_by_type_total',
                'access_token': self.page_access_token
            }
            
            response = requests.get(endpoint, params=params, timeout=30)
            result = response.json()
            
            if 'data' in result:
                return {'success': True, 'insights': result['data']}
            else:
                return {'success': False, 'error': result}
                
        except Exception as e:
            logger.error(f"❌ Facebook post insights error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==================== PAGE MANAGEMENT ====================
    
    def get_page_info(self):
        """Get page information"""
        try:
            endpoint = f"{self.graph_url}/{self.page_id}"
            params = {
                'fields': 'id,name,about,category,fan_count,website,phone,emails,location,description',
                'access_token': self.page_access_token
            }
            
            response = requests.get(endpoint, params=params, timeout=30)
            result = response.json()
            
            if 'id' in result:
                return {'success': True, 'page_info': result}
            else:
                return {'success': False, 'error': result}
                
        except Exception as e:
            logger.error(f"❌ Facebook page info error: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_page_info(self, field, value):
        """Update page information"""
        try:
            endpoint = f"{self.graph_url}/{self.page_id}"
            data = {
                field: value,
                'access_token': self.page_access_token
            }
            
            response = requests.post(endpoint, data=data, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ Page {field} updated")
                return {'success': True}
            else:
                return {'success': False, 'error': response.json()}
                
        except Exception as e:
            logger.error(f"❌ Facebook update page error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==================== TESTING ====================
    
    def test_connection(self):
        """Test Facebook API connection"""
        result = self.get_page_info()
        if result.get('success'):
            page_name = result['page_info'].get('name', 'Unknown')
            logger.info(f"✅ Facebook connection successful! Page: {page_name}")
            return True
        else:
            logger.error(f"❌ Facebook connection failed: {result.get('error')}")
            return False


# Test the manager
if __name__ == "__main__":
    print("="*60)
    print("FACEBOOK PAGE MANAGER TEST")
    print("="*60)
    
    try:
        manager = FacebookPageManager()
        
        # Test connection
        print("\n1. Testing connection...")
        if manager.test_connection():
            print("   ✅ Connected!")
        else:
            print("   ❌ Connection failed!")
            sys.exit(1)
        
        # Get page info
        print("\n2. Getting page info...")
        info = manager.get_page_info()
        if info.get('success'):
            page = info['page_info']
            print(f"   Page: {page.get('name')}")
            print(f"   Likes: {page.get('fan_count', 'N/A')}")
            print(f"   Category: {page.get('category', 'N/A')}")
        
        # Get recent posts
        print("\n3. Getting recent posts...")
        posts = manager.get_posts(limit=3)
        if posts.get('success'):
            for i, post in enumerate(posts['posts'], 1):
                message = post.get('message', '')[:50] if post.get('message') else ''
                print(f"   {i}. {message}...")
        
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
