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
        self.last_report_date = None  # Track last report generation
    
    def start(self):
        """Start the scheduler"""
        logger.info("🕐 Starting Post Scheduler...")
        logger.info("⏰ Checking every 60 seconds for scheduled posts")
        logger.info("📝 Creates approval files for human approval")
        logger.info("✅ Human approval required before posting")
        
        # Initialize database
        init_db()
        
        self.running = True
        
        while self.running:
            try:
                # Check for scheduled posts
                self.check_and_process()
                
                # Check if it's time for daily report (9 AM)
                self.check_daily_report()
                
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
    
    def check_daily_report(self):
        """Check if it's time to generate daily business report (9 AM)"""
        now = datetime.now()
        
        # Check if it's 9 AM and we haven't generated today's report yet
        if now.hour == 9 and now.minute == 0:
            if self.last_report_date != now.date():
                logger.info("📊 Time to generate Daily Business Report!")
                self.generate_daily_report()
                self.last_report_date = now.date()
    
    def generate_daily_report(self):
        """Generate daily business report"""
        try:
            logger.info("📊 Generating Daily Business Report...")
            
            from services.google import GoogleDocsService, GoogleDriveService
            
            # 1. Get data from Odoo (mock data for now - will integrate with real Odoo)
            leads_count = 15  # Mock - replace with: get_odoo_leads_today()
            deals_closed = 5  # Mock - replace with: get_odoo_deals_today()
            
            # 2. Get Gmail stats (mock data - will integrate with real Gmail API)
            emails_sent = 127  # Mock - replace with: get_gmail_stats_today()
            
            # 3. Get social media stats (mock data - will integrate with real APIs)
            fb_posts = 8  # Mock - replace with: get_facebook_stats_today()
            twitter_posts = 5  # Mock
            
            # 4. Generate AI summary
            report_content = f"""
DAILY BUSINESS REPORT
=====================
Date: {datetime.now().strftime('%Y-%m-%d')}
Generated: {datetime.now().strftime('%H:%M:%S')}

KEY METRICS:
------------
📈 Leads Generated: {leads_count}
💰 Deals Closed: {deals_closed}
📧 Emails Sent: {emails_sent}
📱 Social Posts: {fb_posts + twitter_posts}
   - Facebook: {fb_posts}
   - Twitter: {twitter_posts}

AI INSIGHTS:
------------
Based on today's metrics:
- Lead generation is performing well with {leads_count} new leads
- Conversion rate: {(deals_closed/leads_count*100) if leads_count > 0 else 0:.1f}%
- Email activity: {emails_sent} emails sent
- Social media presence: {fb_posts + twitter_posts} posts across platforms

RECOMMENDATIONS:
----------------
1. Follow up with {leads_count} new leads within 24 hours
2. Review conversion funnel - optimize for better close rate
3. Maintain consistent email outreach
4. Continue social media engagement

NEXT ACTIONS:
-------------
- Review hot leads in Odoo CRM
- Send follow-up emails to pending prospects
- Schedule social media posts for tomorrow
- Monitor email open rates

---
Generated by AI Employee Vault
"""
            
            # 5. Create Google Doc
            logger.info("📄 Creating Google Doc...")
            docs = GoogleDocsService()
            doc_title = f"Daily Business Report - {datetime.now().strftime('%Y-%m-%d')}"
            doc = docs.create_document(doc_title, report_content)
            
            if doc['success']:
                logger.info(f"✅ Google Doc created: {doc['link']}")
                
                # 6. Save to Drive folder
                logger.info("📁 Saving to Google Drive...")
                drive = GoogleDriveService()
                
                # Try to get or create "Daily Reports" folder
                folder = drive.get_folder_by_name("Daily Reports")
                if not folder['success']:
                    # Create folder if it doesn't exist
                    folder = drive.create_folder("Daily Reports")
                
                if folder['success']:
                    drive.move_file_to_folder(doc['id'], folder['id'])
                    logger.info(f"✅ Report saved to Drive folder: {folder['link']}")
                
                # 7. Create approval file for CEO review
                logger.info("📋 Creating approval file for CEO review...")
                
                approval_content = f"""---
type: google_docs
action: google_docs
title: {doc_title}
drive_link: {doc['link']}
---

# Daily Business Report Approval

## Report Details

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Title:** {doc_title}
**Google Doc:** {doc['link']}

## Summary

This automated daily business report includes:
- Leads generated: {leads_count}
- Deals closed: {deals_closed}
- Emails sent: {emails_sent}
- Social media posts: {fb_posts + twitter_posts}

## Instructions

1. **Review** the report content above
2. **Edit** if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder

---
*Generated automatically by AI Employee Vault at 9:00 AM*
"""
                
                # Save approval file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                approval_filename = f"APPROVAL_google_docs_daily_report_{timestamp}.md"
                approval_path = Path(__file__).parent.parent / "Pending Approval" / approval_filename
                approval_path.parent.mkdir(exist_ok=True)
                approval_path.write_text(approval_content, encoding='utf-8')
                
                logger.info(f"✅ Approval file created: {approval_filename}")
                logger.info(f"📊 Daily Business Report generation complete!")
                
            else:
                logger.error(f"❌ Failed to create Google Doc: {doc['error']}")
        
        except Exception as e:
            logger.error(f"❌ Daily report generation failed: {e}")


def main():
    """Main entry point"""
    print("=" * 60)
    print("AI Employee Vault - Post Scheduler")
    print("=" * 60)
    print()
    print("🕐 Scheduler is running...")
    print("⏰ Checking every 60 seconds")
    print("📊 Daily Report: Generated at 9:00 AM")
    print("✅ Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    scheduler = PostScheduler()
    scheduler.start()


if __name__ == "__main__":
    main()
