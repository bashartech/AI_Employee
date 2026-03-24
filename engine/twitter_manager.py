"""
Twitter Manager - Free Tier API Integration
Post tweets, threads using OAuth 1.0a (Most Reliable)
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import tweepy
import os
from dotenv import load_dotenv
from datetime import datetime
from engine.logger import logger

load_dotenv()

class TwitterManager:
    """Twitter API Manager - OAuth 1.0a (Most Reliable)"""

    def __init__(self):
        """Initialize with OAuth 1.0a credentials from .env"""
        self.api_key = os.getenv('TWITTER_API_KEY', '')
        self.api_secret = os.getenv('TWITTER_API_SECRET', '')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN', '')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')

        # Check for OAuth 1.0a credentials (preferred)
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            logger.error("❌ Twitter OAuth 1.0a credentials not found in .env!")
            logger.error("   Required: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET")
            raise ValueError("Twitter OAuth 1.0a credentials missing")

        # Authenticate using OAuth 1.0a (most reliable for posting)
        try:
            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret,
                self.access_token,
                self.access_token_secret
            )
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )

            # Test authentication
            me = self.client.get_me()
            logger.info(f"✅ Twitter authenticated as: @{me.data.username}")

        except Exception as e:
            logger.error(f"❌ Twitter authentication failed: {e}")
            raise

    def post_tweet(self, text, media_path=None):
        """
        Post a single tweet
        Free Tier: 1,500 tweets/month
        """
        try:
            logger.info(f"🐦 Posting tweet: {text[:50]}...")

            # If media provided, upload first
            media_id = None
            if media_path and Path(media_path).exists():
                media = self.client.media_upload(filename=media_path)
                media_id = media.media_id
                logger.info(f"✅ Media uploaded: {media_path}")

            # Post tweet
            if media_id:
                result = self.client.create_tweet(text=text, media_ids=[media_id])
            else:
                result = self.client.create_tweet(text=text)

            tweet_id = result.data['id']
            logger.info(f"✅ Tweet posted: {tweet_id}")

            return {
                'success': True,
                'tweet_id': tweet_id,
                'text': text,
                'posted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Tweet post error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def post_thread(self, tweets):
        """
        Post a thread of tweets
        Each tweet in list is a separate tweet in the thread
        """
        try:
            logger.info(f"🧵 Posting thread with {len(tweets)} tweets")
            
            tweet_ids = []
            reply_to = None
            
            for i, tweet_text in enumerate(tweets):
                if i == 0:
                    # First tweet in thread
                    result = self.client.create_tweet(text=tweet_text)
                else:
                    # Reply to previous tweet
                    result = self.client.create_tweet(
                        text=tweet_text,
                        in_reply_to_tweet_id=reply_to
                    )
                
                tweet_ids.append(result.data['id'])
                reply_to = result.data['id']
            
            logger.info(f"✅ Thread posted: {len(tweet_ids)} tweets")
            
            return {
                'success': True,
                'tweet_ids': tweet_ids,
                'count': len(tweet_ids),
                'posted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Thread post error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_tweet(self, tweet_id):
        """Delete a tweet"""
        try:
            logger.info(f"🗑️ Deleting tweet: {tweet_id}")
            
            self.client.delete_tweet(tweet_id)
            
            logger.info(f"✅ Tweet deleted: {tweet_id}")
            return {'success': True, 'tweet_id': tweet_id}
            
        except Exception as e:
            logger.error(f"❌ Tweet delete error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_profile(self):
        """Get your Twitter profile info"""
        try:
            me = self.client.get_me()
            
            return {
                'success': True,
                'profile': {
                    'username': me.data.username,
                    'name': me.data.name,
                    'id': me.data.id,
                    'bio': me.data.description if hasattr(me.data, 'description') else '',
                    'followers': me.data.public_metrics['followers_count'] if hasattr(me.data, 'public_metrics') else 0,
                    'following': me.data.public_metrics['following_count'] if hasattr(me.data, 'public_metrics') else 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Profile fetch error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_recent_tweets(self, limit=10):
        """Get your recent tweets"""
        try:
            me = self.client.get_me()
            user_id = me.data.id
            
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(limit, 5),  # Free tier limit
                tweet_fields=['created_at', 'text', 'public_metrics']
            )
            
            if tweets.data:
                tweet_list = []
                for tweet in tweets.data:
                    tweet_list.append({
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at.isoformat(),
                        'likes': tweet.public_metrics['like_count'],
                        'retweets': tweet.public_metrics['retweet_count'],
                        'replies': tweet.public_metrics['reply_count']
                    })
                
                return {
                    'success': True,
                    'tweets': tweet_list
                }
            else:
                return {
                    'success': True,
                    'tweets': []
                }
            
        except Exception as e:
            logger.error(f"❌ Tweet fetch error: {e}")
            return {
                'success': False,
                'error': str(e)
            }


if __name__ == "__main__":
    # Test Twitter connection by posting a test tweet
    try:
        twitter = TwitterManager()
        print("\n✅ Twitter client initialized successfully!")
        print("   OAuth 1.0a credentials are valid")
        print("\n🧪 Testing tweet posting...")
        
        # Post a test tweet
        result = twitter.post_tweet("Testing Twitter integration from AI Employee Vault! 🚀")
        
        if result.get('success'):
            print(f"\n✅ SUCCESS! Tweet posted!")
            print(f"   Tweet ID: {result['tweet_id']}")
            print(f"   Text: {result['text']}")
        else:
            print(f"\n❌ Tweet failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Twitter test failed: {e}")
