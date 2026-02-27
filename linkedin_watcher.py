"""
LinkedIn Watcher - Silver/Gold Tier
Monitors LinkedIn for comments and messages, creates tasks in Needs Action folder
Browser stays OPEN continuously and checks every 1 minute
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import time
import json

# Fix emoji encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import sync_playwright
from engine.audit_logger import log_action

VAULT = Path(__file__).parent
LINKEDIN_SESSION = VAULT / "linkedin_session"
NEEDS_ACTION = VAULT / "Needs Action"

# Ensure folders exist
NEEDS_ACTION.mkdir(exist_ok=True)

# Keywords that indicate business interest
INTEREST_KEYWORDS = [
    "interested", "interest", "more info", "more information",
    "pricing", "price", "cost", "quote", "quotation",
    "contact me", "call me", "email me", "dm me",
    "how much", "what's the cost", "send details",
    "need this", "want this", "looking for",
    "service", "services", "hire", "working with",
    "partnership", "collaborate", "business",
    "urgently", "urgent", "asap", "immediately"
]


def check_linkedin_activity(page, processed_comments, processed_messages):
    """Check LinkedIn for new comments and messages"""
    leads = []
    
    if not page:
        print("  ❌ Page not available!")
        return leads, processed_comments, processed_messages
    
    try:
        # Go to feed and check posts
        print("  Checking posts for comments...")
        try:
            page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=30000)
            time.sleep(8)  # Wait for feed to load
        except Exception as e:
            print(f"  ⚠️  Feed navigation issue: {e}")
            print("  Continuing anyway...")
            time.sleep(3)
        
        # Check recent posts for comments
        posts = page.query_selector_all('div.feed-shared-update-v2')
        print(f"  Found {len(posts)} recent posts...")
        
        for post in posts[:5]:  # Check last 5 posts
            try:
                post_content = post.inner_text()[:500]
                
                # DO NOT click on posts - stay on feed page
                # Just check visible comments
                
                # Get comments - try multiple selectors
                comments_section = post.query_selector('ul.comments-list')
                if not comments_section:
                    comments_section = post.query_selector('div.comments-comments-list')
                if not comments_section:
                    comments_section = post.query_selector('[class*="comment"]')
                
                if comments_section:
                    # Try multiple selectors for individual comments
                    comments = comments_section.query_selector_all('li.comments-list__comment')
                    if not comments:
                        comments = comments_section.query_selector_all('div.comment')
                    if not comments:
                        comments = comments_section.query_selector_all('[class*="comment"]')
                    
                    print(f"    Found {len(comments)} comments on this post...")
                    
                    for comment in comments[:10]:
                        try:
                            comment_id = comment.get_attribute('data-comment-id')
                            if not comment_id:
                                # Use element handle as fallback ID
                                comment_id = f"comment_{hash(comment.inner_text())}"
                            
                            if comment_id and comment_id not in processed_comments:
                                try:
                                    commenter_name = comment.query_selector('.feed-shared-actor__name')
                                    commenter_headline = comment.query_selector('.feed-shared-actor__sub-description')
                                    comment_text = comment.query_selector('.comment-body')
                                    
                                    if commenter_name and comment_text:
                                        name = commenter_name.inner_text().strip()
                                        headline = commenter_headline.inner_text().strip() if commenter_headline else ''
                                        text = comment_text.inner_text().strip()
                                        
                                        # Check if shows interest
                                        if any(keyword in text.lower() for keyword in INTEREST_KEYWORDS):
                                            lead = {
                                                'type': 'comment',
                                                'name': name,
                                                'headline': headline,
                                                'comment': text,
                                                'post_content': post_content[:200],
                                                'timestamp': datetime.now().isoformat()
                                            }
                                            leads.append(lead)
                                            processed_comments.add(comment_id)
                                            
                                            print(f"  🎯 Interested comment from: {name}")
                                except Exception as e:
                                    continue
                        except Exception as e:
                            continue
            except Exception as e:
                continue
        
        # Check LinkedIn Messages
        print("  Checking messages...")
        try:
            page.goto('https://www.linkedin.com/messaging/', wait_until='domcontentloaded', timeout=30000)
            time.sleep(10)  # Wait longer for messages to load
        except Exception as e:
            print(f"  ⚠️  Messages navigation issue: {e}")
            time.sleep(5)
        
        # Try multiple selectors for conversations
        conversations = []
        
        # Try different selectors
        selectors_to_try = [
            'div.msg-conversations-container__conversation',
            'div.conversations-list-item',
            'a.msg-conversations-container__conversation-link',
            'div.artdeco-list__item',
            'ul.conversations-list > li',
            'li.artdeco-list__item',
            'div.msg-conversation-card',
            'div.conversation-item'
        ]
        
        for selector in selectors_to_try:
            try:
                conversations = page.query_selector_all(selector)
                if len(conversations) > 0:
                    print(f"  Found {len(conversations)} conversations (using: {selector})...")
                    break
            except:
                continue
        
        if len(conversations) == 0:
            print("  ⚠️  No conversations found. Checking inbox...")
            # Get all list items as fallback
            all_items = page.query_selector_all('li, div')
            print(f"  Found {len(all_items)} total elements on page")
            
            # Try to find any conversation-like elements
            for item in all_items[:50]:
                try:
                    text = item.inner_text()
                    if len(text) > 10 and len(text) < 200:
                        # Might be a conversation
                        conversations.append(item)
                except:
                    continue
            
            print(f"  Found {len(conversations)} potential conversations...")
        
        for conv in conversations[:10]:  # Check last 10 conversations
            try:
                # Get all text from conversation
                try:
                    conv_text = conv.inner_text()
                except:
                    continue
                
                # Try to get conversation ID
                conv_id = conv.get_attribute('data-conversation-id')
                if not conv_id:
                    conv_id = conv.get_attribute('href')
                if not conv_id:
                    conv_id = f"conv_{hash(conv_text)}"  # Use hash as fallback
                
                # Get message text
                sender_name = ""
                message_text = ""
                
                # Try multiple selectors for sender name
                name_selectors = [
                    '.msg-conversation-card__name',
                    '.msg-conversation-sender__name',
                    'h4.artdeco-entity-lockup__title',
                    '.artdeco-entity-lockup__title',
                    '.msg-sender__name'
                ]
                
                for selector in name_selectors:
                    name_elem = conv.query_selector(selector)
                    if name_elem:
                        try:
                            sender_name = name_elem.inner_text().strip()
                            break
                        except:
                            continue
                
                # Try multiple selectors for message text
                message_selectors = [
                    '.msg-conversation-card__text-preview',
                    '.msg-conversation-snippet',
                    'p.artdeco-entity-lockup__subtitle',
                    '.artdeco-entity-lockup__subtitle',
                    '.msg-last-message',
                    '.msg-preview'
                ]
                
                for selector in message_selectors:
                    msg_elem = conv.query_selector(selector)
                    if msg_elem:
                        try:
                            message_text = msg_elem.inner_text().strip()
                            break
                        except:
                            continue
                
                # Fallback: parse from full text if selectors didn't work
                if not message_text or len(message_text) < 5:
                    lines = conv_text.split('\n')
                    # Filter out common non-message lines
                    filtered_lines = []
                    for line in lines:
                        line = line.strip()
                        # Skip status lines, dates, etc.
                        if line and \
                           'Status is' not in line and \
                           'online' not in line and \
                           'Feb' not in line and \
                           'Jan' not in line and \
                           'Mar' not in line and \
                           '202' not in line and \
                           ':' not in line[:3] and \
                           len(line) > 5 and len(line) < 100:
                            filtered_lines.append(line)
                    
                    if len(filtered_lines) >= 2:
                        sender_name = filtered_lines[0]
                        message_text = filtered_lines[1]
                    elif len(filtered_lines) == 1:
                        message_text = filtered_lines[0]
                
                # Clean up the message text
                message_text = message_text.replace('•', '').replace('\n', ' ').strip()
                
                if sender_name and message_text and len(message_text) > 3:
                    print(f"  Message from {sender_name}: {message_text[:80]}...")
                    
                    # Check if message shows interest
                    if any(keyword in message_text.lower() for keyword in INTEREST_KEYWORDS):
                        # Check if this is a NEW message (different from last processed)
                        message_hash = hash(message_text)
                        last_hash = processed_messages.get(conv_id, None)
                        
                        if message_hash != last_hash:
                            # New message! Create lead
                            lead = {
                                'type': 'message',
                                'name': sender_name,
                                'message': message_text,
                                'timestamp': datetime.now().isoformat()
                            }
                            leads.append(lead)
                            processed_messages[conv_id] = message_hash  # Update last message
                            
                            print(f"  🎯 NEW interested message from: {sender_name}")
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error checking LinkedIn: {e}")
        log_action("LINKEDIN_WATCHER_ERROR", {"error": str(e)})
    
    return leads, processed_comments, processed_messages


def create_task_file(lead: dict):
    """Create task file in Needs Action folder"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if lead['type'] == 'comment':
        filename = f"LINKEDIN_COMMENT_{lead['name'].replace(' ', '_')}_{timestamp}.md"
        
        content = f"""---
type: linkedin_lead
source: LinkedIn Comment
name: {lead['name']}
headline: {lead['headline']}
detected: {lead['timestamp']}
priority: high
status: pending
---

# LinkedIn Lead - Comment Detected

## Lead Details

**Name:** {lead['name']}
**Headline:** {lead['headline']}
**Source:** LinkedIn Comment
**Detected:** {lead['timestamp']}

## Interest Detected

**Comment:**
> {lead['comment']}

## Original Post Context

**Post:**
> {lead['post_content']}

## Suggested Actions

- [ ] Respond to comment
- [ ] Send connection request
- [ ] Create lead in Odoo
- [ ] Send more information

## Instructions

Analyze this LinkedIn comment and determine appropriate response.
If lead qualification needed, create approval file to add to Odoo CRM.
"""
    else:  # message
        filename = f"LINKEDIN_MESSAGE_{lead['name'].replace(' ', '_')}_{timestamp}.md"
        
        content = f"""---
type: linkedin_lead
source: LinkedIn Message
name: {lead['name']}
detected: {lead['timestamp']}
priority: high
status: pending
---

# LinkedIn Lead - Message Received

## Lead Details

**Name:** {lead['name']}
**Source:** LinkedIn Message
**Detected:** {lead['timestamp']}

## Message Content

> {lead['message']}

## Suggested Actions

- [ ] Respond to message
- [ ] Create lead in Odoo
- [ ] Schedule call/meeting
- [ ] Send pricing information

## Instructions

Analyze this LinkedIn message and determine appropriate response.
If lead qualification needed, create approval file to add to Odoo CRM.
"""
    
    filepath = NEEDS_ACTION / filename
    filepath.write_text(content, encoding='utf-8')
    
    print(f"  ✓ Created task: {filename}")
    log_action("LINKEDIN_TASK_CREATED", {
        "lead_name": lead['name'],
        "type": lead['type'],
        "file": filename
    })
    
    return filepath


def run_watcher():
    """Run watcher with browser staying OPEN"""
    print("="*60)
    print("LINKEDIN WATCHER STARTED")
    print("="*60)
    print(f"Monitoring: LinkedIn for comments and messages")
    print(f"Checking: Every 1 minute")
    print(f"Browser: STAYS OPEN (visible)")
    print(f"Output to: Needs Action/")
    print("\nPress Ctrl+C to stop\n")
    
    log_action("LINKEDIN_WATCHER_START", {"status": "started"})

    processed_comments = set()
    processed_messages = {}  # Track: {conversation_id: last_message_hash}
    
    # Open browser ONCE and keep it open
    try:
        with sync_playwright() as p:
            # Launch browser with saved session - VISIBLE MODE - STAYS OPEN
            browser = p.chromium.launch_persistent_context(
                str(LINKEDIN_SESSION),
                headless=False,  # VISIBLE browser
                args=[
                    '--disable-gpu',
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ],
                viewport={'width': 1280, 'height': 720}
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Go to LinkedIn
            print("  Opening LinkedIn...")
            page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=60000)
            time.sleep(5)  # Wait for page to fully load
            
            # Check if logged in
            if not page.query_selector('[data-id="feed"]'):
                print("  ⚠️  Not logged in yet. Please login in the browser window.")
                print("  Waiting up to 60 seconds for login...")
                
                # Wait for login (up to 60 seconds)
                for i in range(12):  # Check 12 times, 5 seconds each = 60 seconds
                    time.sleep(5)
                    if page.query_selector('[data-id="feed"]'):
                        print("  ✓ Login detected!")
                        break
                else:
                    print("  ⚠️  Still not logged in. You can login now and watcher will detect...")
            
            print("  ✓ LinkedIn loaded and ready!")
            print()
            
            # Main loop - browser stays open
            while True:
                try:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking LinkedIn...")
                    
                    leads, processed_comments, processed_messages = check_linkedin_activity(
                        page, processed_comments, processed_messages
                    )
                    
                    if leads:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(leads)} interested leads!")
                        
                        for lead in leads:
                            create_task_file(lead)
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] No new leads found")
                    
                    # Wait for next check (browser stays open)
                    print(f"  Waiting 60 seconds for next check... (browser stays open)")
                    time.sleep(60)
                    
                except KeyboardInterrupt:
                    print("\n\n⏹ LinkedIn Watcher stopped by user")
                    log_action("LINKEDIN_WATCHER_STOP", {"status": "stopped"})
                    break
                except Exception as e:
                    print(f"Error in watcher loop: {e}")
                    time.sleep(60)
            
            browser.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        log_action("LINKEDIN_WATCHER_ERROR", {"error": str(e)})


if __name__ == "__main__":
    run_watcher()
