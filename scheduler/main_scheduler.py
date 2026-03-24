"""
Main Scheduler Runner - Checks every minute for scheduled posts
Creates approval files in Pending Approval folder for human approval
Does NOT post directly - requires human approval via execute_approved.py
"""
import time
from datetime import datetime
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scheduler.scheduler_db import init_db, get_pending_posts
from scheduler.twitter_scheduler import process_scheduled_twitter_post
from scheduler.facebook_scheduler import process_scheduled_facebook_post
from engine.logger import logger


class PostScheduler:
    """
    Main scheduler that runs continuously
    Checks every 60 seconds for posts that should be processed
    """
    
    def __init__(self):
        self.running = False
        self.check_interval = 60  # Check every 60 seconds
    
    def start(self):
        """Start the scheduler"""
        logger.info("🕐 Starting Post Scheduler...")
        logger.info("⏰ Checking every 60 seconds for scheduled posts")
        logger.info("📝 Creates approval files in Pending Approval folder")
        logger.info("✅ Human approval required before posting")
        
        # Initialize database
        init_db()
        
        self.running = True
        
        while self.running:
            try:
                self.check_and_process()
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                logger.info("⏹️ Scheduler stopped by user")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(self.check_interval)
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("⏹️ Stopping scheduler...")
        self.running = False
    
    def check_and_process(self):
        """Check for pending scheduled posts and process them"""
        pending_posts = get_pending_posts()
        
        if not pending_posts:
            logger.debug("📭 No pending scheduled posts")
            return
        
        logger.info(f"📬 Found {len(pending_posts)} scheduled post(s) to process")
        
        for post in pending_posts:
            post_id, platform, content, hashtags, is_thread, approval_file = post
            
            logger.info(f"📮 Processing {platform} post ID: {post_id}")
            
            if platform == 'twitter':
                success = process_scheduled_twitter_post(
                    post_id, 
                    content, 
                    hashtags, 
                    bool(is_thread)
                )
            elif platform == 'facebook':
                success = process_scheduled_facebook_post(
                    post_id, 
                    content, 
                    hashtags
                )
            else:
                logger.warning(f"⚠️ Unknown platform: {platform}")
                from scheduler.scheduler_db import update_post_status
                update_post_status(post_id, 'failed', error_message=f"Unknown platform: {platform}")
                success = False
            
            if success:
                logger.info(f"✅ Successfully processed post {post_id}")
            else:
                logger.error(f"❌ Failed to process post {post_id}")


def main():
    """Main entry point"""
    print("=" * 60)
    print("AI Employee Vault - Post Scheduler")
    print("=" * 60)
    print()
    print("🕐 Scheduler is running...")
    print("⏰ Checking every 60 seconds")
    print("📝 Creates approval files for human approval")
    print("✅ Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    scheduler = PostScheduler()
    scheduler.start()


if __name__ == "__main__":
    main()
