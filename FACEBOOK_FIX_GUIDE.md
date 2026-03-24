# 🔧 Facebook Issues - Complete Fix Guide

## Issues Identified & Solutions:

---

## **ISSUE 1: Facebook Post Creates Wrong Approval File**

**Problem:** Creates `APPROVAL_task_review_*.md` instead of `APPROVAL_facebook_post_*.md`

**Cause:** Orchestrator wasn't detecting Facebook tasks properly

**Fix:** ✅ **ALREADY FIXED** - Updated `_detect_task_type()` to check for Facebook FIRST:

```python
# First check for Facebook tasks (NEW - must be before Odoo)
if 'facebook' in filename_lower or 'facebook' in content_lower:
    return 'facebook'
```

**Also added at end of detection:**
```python
elif 'facebook' in filename_lower or 'type: facebook' in content_lower:
    return 'facebook'
```

---

## **ISSUE 2: Execute Approved Doesn't Detect Facebook Files**

**Status:** ✅ **ALREADY WORKING** - execute_approved.py already has:

```python
elif "APPROVAL_facebook" in file_path.name or "action: facebook" in content:
    success = self.execute_facebook(file_path)
```

And the `execute_facebook()` method is already implemented!

---

## **ISSUE 3: Facebook API Stops Working After 5-6 Hours**

**Error:** `Error loading posts: [object Object]`

**Cause:** **Facebook Page Access Token Expiration**

### **Understanding Facebook Token Types:**

| Token Type | Lifespan | Can Be Extended |
|------------|----------|-----------------|
| **Short-Lived Token** | 1-2 hours | ❌ No |
| **Long-Lived Token** | 60 days | ✅ Yes |
| **Never-Expiring Token** | Never | ✅ For Pages only |

### **Why Token Expires:**

You're likely using a **short-lived user token** instead of a **long-lived page token**.

### **Solution: Get Long-Lived Page Token**

#### **Step 1: Get Long-Lived User Token**

1. Go to: [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Click "Get Token" → "Get User Access Token"
4. Select these permissions:
   - ✅ `pages_show_list`
   - ✅ `pages_read_engagement`
   - ✅ `pages_manage_posts`
   - ✅ `pages_manage_metadata`
   - ✅ `read_insights`
5. Click "Get Access Token"
6. Login & approve

#### **Step 2: Exchange for Long-Lived Token**

**Use this URL (replace YOUR_SHORT_TOKEN):**

```
https://graph.facebook.com/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id=YOUR_APP_ID&
  client_secret=YOUR_APP_SECRET&
  fb_exchange_token=YOUR_SHORT_TOKEN
```

**Or use this Python script:**

```python
import requests

APP_ID = 'your_app_id'
APP_SECRET = 'your_app_secret'
SHORT_TOKEN = 'your_short_token'

url = 'https://graph.facebook.com/oauth/access_token'
params = {
    'grant_type': 'fb_exchange_token',
    'client_id': APP_ID,
    'client_secret': APP_SECRET,
    'fb_exchange_token': SHORT_TOKEN
}

response = requests.get(url, params=params)
result = response.json()

print(f"Long-lived token: {result['access_token']}")
print(f"Expires in: {result.get('expires_in', 'Never')} seconds")
```

#### **Step 3: Get Page Token from Long-Lived User Token**

```python
import requests

LONG_LIVED_USER_TOKEN = 'your_long_lived_user_token'

# Get pages you manage
url = 'https://graph.facebook.com/v18.0/me/accounts'
params = {'access_token': LONG_LIVED_USER_TOKEN}

response = requests.get(url, params=params)
result = response.json()

for page in result['data']:
    print(f"Page: {page['name']}")
    print(f"Page ID: {page['id']}")
    print(f"Page Token: {page['access_token']}")  # ← This is your page token!
```

#### **Step 4: Update .env File**

```bash
# Replace with your NEW long-lived page token
FACEBOOK_PAGE_TOKEN=EAAG... (long token here)
FACEBOOK_PAGE_ID=976642828873094
```

#### **Step 5: Restart Services**

```bash
ssh -i "C:\Users\H P\.ssh\digitaloceonsshkey" root@167.71.237.77

pm2 restart dashboard
pm2 restart orchestrator
pm2 restart execute-approved
```

---

## **ISSUE 4: Token Limits & Best Practices**

### **Facebook API Rate Limits:**

| Action | Rate Limit | Reset Period |
|--------|------------|--------------|
| **Page Posts** | 200 posts/day | Per day |
| **API Calls** | 4800 calls/hour | Per hour |
| **Insights** | 5000 calls/hour | Per hour |

### **Token Best Practices:**

1. **Use Long-Lived Page Tokens** (60 days)
2. **Store tokens securely** in .env (never commit to Git)
3. **Monitor token expiration** - set reminder to refresh every 50 days
4. **Use app access token** for server-to-server calls
5. **Implement token refresh logic** before expiration

### **Token Refresh Schedule:**

```python
# Add to your orchestrator or a scheduled task
def check_token_expiration():
    """Check if Facebook token is expiring soon"""
    import requests
    import os
    
    token = os.getenv('FACEBOOK_PAGE_TOKEN')
    
    # Debug token to get expiration
    url = 'https://graph.facebook.com/debug_token'
    params = {
        'input_token': token,
        'access_token': f'{APP_ID}|{APP_SECRET}'
    }
    
    response = requests.get(url, params=params)
    result = response.json()
    
    expires_at = result['data']['expires_at']
    days_until_expiry = (expires_at - time.time()) / 86400
    
    if days_until_expiry < 7:
        logger.warning(f"⚠️ Facebook token expires in {days_until_expiry:.1f} days!")
        # Send alert email or notification
```

---

## **COMPLETE FIX - Upload & Test:**

### **Step 1: Upload Updated Orchestrator**

```powershell
scp -i "C:\Users\H P\.ssh\digitaloceonsshkey" D:\DATA\HACKATHON_0\AI_Employee_Vault\engine\orchestrator.py root@167.71.237.77:/home/AI_Employee/engine/
```

### **Step 2: Get New Long-Lived Token**

Follow the steps above to get a 60-day token.

### **Step 3: Update .env on Server**

```bash
ssh -i "C:\Users\H P\.ssh\digitaloceonsshkey" root@167.71.237.77

nano /home/AI_Employee/.env

# Update with NEW long-lived token
FACEBOOK_PAGE_TOKEN=EAAGmX... (your new 60-day token)
FACEBOOK_PAGE_ID=976642828873094

# Save (Ctrl+X, Y, Enter)
```

### **Step 4: Restart All Services**

```bash
pm2 restart all
pm2 status
```

### **Step 5: Test Facebook Posting**

1. Open dashboard: `http://167.71.237.77:5000`
2. Go to Facebook Management → Create Post
3. Type a test message
4. Click "Create Post (Requires Approval)"
5. Check `Needs Action/` folder for task
6. Orchestrator should detect and create `APPROVAL_facebook_post_*.md`
7. Approve from dashboard
8. Check execute_approved logs - should post to Facebook

---

## **Expected Workflow:**

```
Dashboard → Create Post
    ↓
Needs Action/facebook_create_*.md
    ↓
Orchestrator detects "facebook" → Creates APPROVAL_facebook_post_*.md
    ↓
Pending Approval/APPROVAL_facebook_post_*.md
    ↓
You approve (dashboard or move file)
    ↓
Approved/APPROVAL_facebook_post_*.md
    ↓
execute_approved detects → Posts to Facebook
    ↓
Done/EXECUTED_APPROVAL_facebook_post_*.md
```

---

## **Summary:**

| Issue | Status | Solution |
|-------|--------|----------|
| Wrong approval file | ✅ Fixed | Updated orchestrator detection |
| Execute not detecting | ✅ Already Working | Code already has Facebook support |
| Token expires after 5-6 hours | ⚠️ **Needs Action** | Get 60-day long-lived page token |
| Rate limits | ℹ️ Info Only | Stay within API limits |

---

**Get your long-lived token and update .env to fix the expiration issue!** 🚀
