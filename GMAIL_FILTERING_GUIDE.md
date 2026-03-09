# 📧 Gmail Smart Filtering - Quick Guide

## 🎯 What Was Added

Your Gmail watcher now has **intelligent filtering** that automatically blocks:
- ❌ Promotional emails (ads, sales, discounts)
- ❌ Social media notifications
- ❌ Receipts and updates
- ❌ Forum/mailing list emails
- ❌ Newsletter spam

And only sends **important emails** to Needs Action:
- ✅ Primary inbox emails
- ✅ Gmail "Important" marked emails
- ✅ Professional/work-related emails
- ✅ Emails from whitelisted senders

## 🚀 How to Use

### 1. Start Gmail Watcher (Same as Before)
```bash
python gmail_watcher.py
```

### 2. Watch the Filtering in Action
```
[10:30:15] Found 5 new email(s)
  ✓ Important: Important email (score: 8)
  ✗ Filtered: Promotional email (Gmail category)
  ✗ Filtered: Social media notification
  ✓ Important: Important email (score: 7)
  ✗ Filtered: Low importance (score: 3)

✓ Created task: EMAIL_a1b2c3d4.md
  From: client@company.com
  Subject: Project Update Required
  Score: 8/10

📊 Statistics:
  Processed: 2
  Filtered: 3
  Filter Rate: 60.0%
```

## ⚙️ Customize Filtering

Edit `gmail_filter_config.py` to customize:

### Adjust Strictness
```python
# More strict (fewer emails pass)
MIN_IMPORTANCE_SCORE = 7

# Less strict (more emails pass)
MIN_IMPORTANCE_SCORE = 3
```

### Add Important Senders (Whitelist)
```python
WHITELIST_DOMAINS = [
    '@importantclient.com',
    '@partner.com',
    'boss@company.com',
]
```

### Block Specific Senders (Blacklist)
```python
BLACKLIST_DOMAINS = [
    'noreply@',
    '@spammer.com',
    'newsletter@',
]
```

### Add Professional Keywords
```python
PROFESSIONAL_KEYWORDS = [
    'meeting', 'project', 'urgent',
    'invoice', 'contract', 'proposal',
    # Add your own
    'custom_keyword',
]
```

## 📊 How Scoring Works

Each email starts with **5/10** importance score:

**Boosts (+):**
- +3: Gmail Primary category
- +3: Gmail "Important" marker
- +3: Whitelisted sender (auto-pass)
- +1: Each professional keyword

**Penalties (-):**
- -2: Promotional keyword
- -3: Spam indicators

**Auto-Block (0):**
- Gmail Promotions/Social/Updates/Forums
- Blacklisted sender
- 2+ promotional keywords

**Decision:**
- Score ≥ 5 → Process ✅
- Score < 5 → Filter ❌

## 🎛️ Quick Adjustments

### Too Many Emails Getting Through?
```python
# In gmail_filter_config.py
MIN_IMPORTANCE_SCORE = 7  # Increase from 5

# Add more promotional keywords
PROMO_KEYWORDS = [
    'unsubscribe', 'discount', 'sale',
    'your_custom_keyword',  # Add here
]
```

### Missing Important Emails?
```python
# In gmail_filter_config.py
MIN_IMPORTANCE_SCORE = 3  # Decrease from 5

# Add sender to whitelist
WHITELIST_DOMAINS = [
    '@important-sender.com',  # Add here
]
```

## 📈 Expected Results

**Before Filtering:**
- 100 emails → 100 tasks in Needs Action
- 90% are promotional/spam
- Hard to find important emails

**After Filtering:**
- 100 emails → 10-20 tasks in Needs Action
- 70-90% noise reduction
- Only important emails reach you

## 🔍 Troubleshooting

### Important Email Was Filtered?
1. Check the console output for filter reason
2. Add sender to `WHITELIST_DOMAINS`
3. Or decrease `MIN_IMPORTANCE_SCORE`

### Still Getting Spam?
1. Check email subject for keywords
2. Add keywords to `PROMO_KEYWORDS`
3. Add sender to `BLACKLIST_DOMAINS`
4. Or increase `MIN_IMPORTANCE_SCORE`

### Want to Review Filtered Emails?
```python
# In gmail_filter_config.py
LOG_FILTERED_EMAILS = True
VERBOSE_FILTERING = True
```

Then check console output or `logs/filtered_emails.log`

## 📝 Example Configuration

```python
# gmail_filter_config.py

# Strict filtering (only very important emails)
MIN_IMPORTANCE_SCORE = 7

# Your important contacts
WHITELIST_DOMAINS = [
    '@client1.com',
    '@client2.com',
    'boss@company.com',
]

# Block these senders
BLACKLIST_DOMAINS = [
    'noreply@',
    '@marketing.com',
    'newsletter@',
]

# Your work-related keywords
PROFESSIONAL_KEYWORDS = [
    'meeting', 'project', 'deadline',
    'invoice', 'contract', 'urgent',
    'client', 'proposal',
]
```

## 🎉 Benefits

✅ **70-90% noise reduction** - Block promotional emails automatically
✅ **Focus on what matters** - Only important emails reach Needs Action
✅ **Save time** - No more manual filtering
✅ **Save API costs** - Fewer Claude Code processing calls
✅ **Customizable** - Adjust filtering to your needs
✅ **Statistics** - See how many emails are filtered

## 🔄 Updating Configuration

After editing `gmail_filter_config.py`:
1. Stop Gmail watcher (Ctrl+C)
2. Restart: `python gmail_watcher.py`
3. New settings take effect immediately

## 📚 Files Modified

- `gmail_watcher.py` - Added filtering logic
- `gmail_filter_config.py` - Configuration file (NEW)

## 💡 Pro Tips

1. **Start with default settings** - See how it works first
2. **Monitor for a day** - Check filter statistics
3. **Adjust as needed** - Fine-tune based on your email patterns
4. **Use whitelist** - For VIP senders that must always get through
5. **Review filtered emails** - Enable logging to ensure nothing important is missed

---

**Ready to use!** Just run `python gmail_watcher.py` and watch the smart filtering in action! 🚀
