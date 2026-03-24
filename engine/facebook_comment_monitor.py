"""
Facebook Comment Monitor
Detects potential leads from Facebook Page comments
Creates tasks in Needs Action folder for processing
"""

import time
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.facebook_manager import FacebookPageManager
from engine.logger import logger


class FacebookCommentMonitor:
    """Monitor Facebook page comments for leads"""
    
    def __init__(self):
        self.facebook = FacebookPageManager()
        self.last_check = datetime.now()
        self.processed_comments = set()
        
        # Paths (using your existing folder structure)
        self.base_dir = Path(__file__).parent.parent
        self.needs_action = self.base_dir / "Needs Action"
        
        # Ensure folders exist
        self.needs_action.mkdir(exist_ok=True)
    
    def start_monitoring(self, check_interval=300):
        """
        Start monitoring loop
        check_interval: Check every N seconds (default: 5 minutes)
        """
        logger.info("🚀 Starting Facebook Comment Monitor...")
        logger.info(f"Checking every {check_interval} seconds")
        logger.info(f"Monitoring Page ID: {self.facebook.page_id}")
        
        while True:
            try:
                self.check_new_comments()
                time.sleep(check_interval)
            except KeyboardInterrupt:
                logger.info("⏹️  Stopping monitor...")
                break
            except Exception as e:
                logger.error(f"❌ Monitor error: {e}")
                time.sleep(60)  # Wait 1 minute before retry
    
    def check_new_comments(self):
        """Check for new comments since last check"""
        logger.info("🔍 Checking for new comments...")
        
        # Get recent comments
        result = self.facebook.get_page_comments(limit=50)
        
        if not result.get('success'):
            logger.error(f"Failed to get comments: {result.get('error')}")
            return
        
        comments = result.get('comments', [])
        new_count = 0
        
        for comment in comments:
            comment_id = comment.get('id')
            
            # Skip already processed comments
            if comment_id in self.processed_comments:
                continue
            
            # Skip old comments
            try:
                comment_time = datetime.fromisoformat(
                    comment.get('created_time', '').replace('Z', '+00:00')
                )
                if comment_time < self.last_check:
                    continue
            except:
                pass
            
            # Process new comment
            self.process_comment(comment)
            new_count += 1
            
            # Mark as processed
            self.processed_comments.add(comment_id)
        
        # Update last check time
        self.last_check = datetime.now()
        
        if new_count > 0:
            logger.info(f"✅ Found {new_count} new comments")
        logger.info(f"✅ Checked {len(comments)} total comments")
    
    def process_comment(self, comment):
        """Process a single comment - Create task in Needs Action"""
        comment_id = comment.get('id')
        message = comment.get('message', '')
        user = comment.get('from', {})
        user_name = user.get('name', 'Unknown')
        user_id = user.get('id', '')
        
        logger.info(f"📝 Processing comment from {user_name}")
        
        # Calculate lead score
        lead_score = self.score_lead(message)
        logger.info(f"🎯 Lead Score: {lead_score}/100")
        
        # Create task file in Needs Action folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_filename = f"FACEBOOK_COMMENT_{user_name.replace(' ', '_')}_{timestamp}.md"
        task_path = self.needs_action / task_filename
        
        task_content = f"""---
type: facebook_comment
source: Facebook Page
facebook_id: {user_id}
comment_id: {comment_id}
lead_score: {lead_score}
---

# Facebook Comment - Potential Lead

## Comment Details

**Posted By:** {user_name}
**Facebook ID:** {user_id}
**Comment ID:** {comment_id}
**Time:** {comment.get('created_time', '')}
**Lead Score:** {lead_score}/100

## Comment Content

{message}

## Lead Analysis

{self.get_lead_analysis(lead_score)}

---

## Instructions

1. **Review** the comment above
2. **Orchestrator will auto-process this**
3. **Approval files will be created in Pending Approval/:**
   - Save lead to Odoo CRM
   - Send Email notification
   - Send WhatsApp notification (if score >= 80)
   - Reply to Facebook comment
4. **Human:** Approve each file in dashboard

---

## Quick Reference

**Lead Score Guide:**
- 80-100: 🔥 HOT LEAD - Respond immediately!
- 50-79: ⚡ WARM LEAD - Respond within 2 hours
- < 50: 📌 COOL LEAD - Respond within 24 hours
"""
        
        task_path.write_text(task_content, encoding='utf-8')
        logger.info(f"✅ Task created: {task_filename}")
    
    def score_lead(self, text):
        """
        Score lead from 1-100 based on keywords and intent
        """
        score = 0
        text_lower = text.lower()
        
        # HIGH VALUE keywords (+25 points each)
        high_value = [
            'hire', 'looking for', 'need developer',
            'budget', 'payment', 'salary', 'contract', 'price'
        ]
        for keyword in high_value:
            if keyword in text_lower:
                score += 25
        
        # TECHNICAL keywords (+15 points each)
        tech_keywords = [
            'full stack', 'react', 'node.js', 'ai automation',
            'machine learning', 'chatbot', 'website', 'web app'
        ]
        for keyword in tech_keywords:
            if keyword in text_lower:
                score += 15
        
        # URGENCY indicators (+20 points each)
        urgency = ['urgent', 'immediately', 'asap', 'right away', 'deadline']
        for word in urgency:
            if word in text_lower:
                score += 20
        
        # Cap at 100
        return min(score, 100)
    
    def get_lead_analysis(self, score):
        """Get analysis text based on score"""
        if score >= 80:
            return "🔥 **HOT LEAD** - High intent, budget mentioned, urgent. Respond immediately!"
        elif score >= 50:
            return "⚡ **WARM LEAD** - Interested, good potential. Respond within 2 hours."
        else:
            return "📌 **COOL LEAD** - General inquiry. Standard follow-up within 24 hours."


if __name__ == "__main__":
    monitor = FacebookCommentMonitor()
    monitor.start_monitoring(check_interval=120)  # Check every 2 minutes
