"""
Gmail Watcher - Email Filtering Configuration
Customize these settings to control which emails reach Needs Action
"""

# ==================== IMPORTANCE THRESHOLD ====================

# Minimum importance score (1-10) to process email
# Lower = more emails pass through, Higher = stricter filtering
MIN_IMPORTANCE_SCORE = 5

# ==================== PROMOTIONAL KEYWORDS ====================

# Emails with these keywords in subject are likely promotional
PROMO_KEYWORDS = [
    # Sales & Discounts
    'unsubscribe', 'discount', 'sale', 'offer', 'limited time',
    'act now', 'click here', 'buy now', 'shop now', 'deal',
    'coupon', 'promo', 'advertisement', 'sponsored', 'free shipping',
    'save now', 'exclusive offer', 'special offer', 'clearance',

    # Marketing
    'newsletter', 'subscribe', 'sign up', 'join now', 'register',
    'webinar', 'event invitation', 'rsvp',

    # Add your own keywords here
    # 'keyword1', 'keyword2',
]

# ==================== SENDER WHITELIST ====================

# Emails from these domains ALWAYS pass through (highest priority)
# Format: '@domain.com' or 'email@domain.com'
WHITELIST_DOMAINS = [
    # Example: Important clients/partners
    # '@importantclient.com',
    # '@partner.com',
    # 'boss@company.com',

    # Add your important domains/emails here
]

# ==================== SENDER BLACKLIST ====================

# Emails from these domains are ALWAYS blocked
# Format: '@domain.com' or 'noreply@'
BLACKLIST_DOMAINS = [
    # No-reply addresses
    'noreply@', 'no-reply@', 'donotreply@', 'do-not-reply@',

    # Marketing/Newsletter addresses
    'newsletter@', 'marketing@', 'promotions@', 'notifications@',
    'updates@', 'news@', 'info@',

    # Add your own blocked domains here
    # '@spammer.com',
]

# ==================== PROFESSIONAL KEYWORDS ====================

# Emails with these keywords get importance boost
PROFESSIONAL_KEYWORDS = [
    # Work-related
    'meeting', 'project', 'deadline', 'urgent', 'asap',
    'invoice', 'contract', 'proposal', 'review', 'approval',
    'request', 'inquiry', 'question', 'follow up', 'followup',

    # Business
    'client', 'customer', 'partner', 'vendor', 'supplier',
    'payment', 'order', 'delivery', 'shipment',

    # Add your own professional keywords
    # 'keyword1', 'keyword2',
]

# ==================== SPAM INDICATORS ====================

# Emails with these keywords get importance penalty
SPAM_INDICATORS = [
    'congratulations', 'winner', 'claim', 'prize', 'lottery',
    'verify your account', 'suspended', 'unusual activity',
    'confirm your identity', 'security alert', 'account locked',
    'click to verify', 'update payment', 'expired',

    # Add your own spam indicators
    # 'keyword1', 'keyword2',
]

# ==================== FILTERING BEHAVIOR ====================

# Enable/disable specific filters
ENABLE_CATEGORY_FILTER = True      # Filter by Gmail categories (Promotions, Social, etc.)
ENABLE_KEYWORD_FILTER = True       # Filter by promotional keywords
ENABLE_WHITELIST = True            # Allow whitelisted senders
ENABLE_BLACKLIST = True            # Block blacklisted senders
ENABLE_IMPORTANCE_MARKER = True    # Boost Gmail "Important" marked emails
ENABLE_PROFESSIONAL_BOOST = True   # Boost emails with professional keywords
ENABLE_SPAM_DETECTION = True       # Penalize emails with spam indicators

# ==================== LOGGING ====================

# Show detailed filtering reasons in console
VERBOSE_FILTERING = True

# Log filtered emails to file (for review)
LOG_FILTERED_EMAILS = False
FILTERED_LOG_FILE = "logs/filtered_emails.log"

# ==================== NOTES ====================

"""
HOW IMPORTANCE SCORING WORKS:

Base Score: 5/10

Boosts (+):
  +3: Gmail Primary category
  +3: Gmail "Important" marker
  +3: Whitelisted sender (auto-pass)
  +1 per professional keyword found

Penalties (-):
  -2: One promotional keyword
  -3: Spam indicators

Auto-Block (score = 0):
  - Gmail Promotions category
  - Gmail Social category
  - Gmail Updates category
  - Gmail Forums category
  - Blacklisted sender
  - 2+ promotional keywords

Final Decision:
  Score >= MIN_IMPORTANCE_SCORE → Process
  Score < MIN_IMPORTANCE_SCORE → Filter out

CUSTOMIZATION TIPS:

1. Too many emails getting through?
   → Increase MIN_IMPORTANCE_SCORE to 6 or 7
   → Add more PROMO_KEYWORDS
   → Add more BLACKLIST_DOMAINS

2. Missing important emails?
   → Decrease MIN_IMPORTANCE_SCORE to 4 or 3
   → Add sender domains to WHITELIST_DOMAINS
   → Add keywords to PROFESSIONAL_KEYWORDS

3. Want to review filtered emails?
   → Set LOG_FILTERED_EMAILS = True
   → Check logs/filtered_emails.log

4. Want to see why emails are filtered?
   → Set VERBOSE_FILTERING = True
   → Watch console output
"""
