# 🔧 TWITTER APP SETUP - COMPLETE GUIDE

## ERROR: Missing Required Fields
When you enable "Read and Write" permissions, Twitter requires:
- ✅ Callback URL / Redirect URI
- ✅ Website URL  
- ✅ Organization info (sometimes)

---

## ✅ CORRECT VALUES TO USE

### **For Server-to-Server Posting (Our Use Case)**

Since we're posting tweets from a server (not a web app with login), use these values:

### **1. Callback URL / Redirect URI**
```
http://localhost:5000
```
**OR** (if you don't have a frontend):
```
https://example.com
```
*(This won't actually be used, just needs to be a valid URL)*

### **2. Website URL**
```
https://example.com
```
*(Can be any valid URL - we're not using web login)*

### **3. Organization Info** (if asked)
- **Organization Name:** Your company name (or your name)
- **Organization Country:** Pakistan
- **Contact Email:** bashartc14@gmail.com

### **4. App Description** (if asked)
```
Automated posting bot for AI Employee Vault system. 
Posts business updates, announcements, and automated content.
Server-to-server application, no user login required.
```

### **5. How Will You Use This?** (if asked)
```
This app will:
- Post automated tweets from our AI Employee Vault system
- Create tweets and threads programmatically
- No user authentication needed (server-to-server only)
- Used for business automation and scheduled posting
```

---

## 📋 STEP-BY-STEP SETUP

### **STEP 1: Go to Twitter Developer Portal**
```
https://developer.twitter.com/en/portal/dashboard
```

### **STEP 2: Select Your App**
- Click on your project: "AI Employee Vault"
- Click on your app

### **STEP 3: Enable Read & Write**
1. Click **"Keys and tokens"** tab
2. Scroll to **"OAuth 1.0a"** section
3. Click **"Edit"** next to App permissions
4. Select: **"Read and Write"**
5. Click **"Save"**

### **STEP 4: Fill Required Fields**

**When it asks for additional info:**

| Field | What to Enter |
|-------|--------------|
| **Callback URL / Redirect URI** | `http://localhost:5000` |
| **Website URL** | `https://example.com` |
| **Organization Name** | Your name or company |
| **Organization Country** | Pakistan |
| **Contact Email** | `bashartc14@gmail.com` |
| **App Description** | "Automated posting bot for AI Employee Vault" |
| **How will you use this?** | "Post automated tweets from server. No user login." |

### **STEP 5: Submit for Review** (if required)
- Some apps need Twitter approval
- Usually takes 1-24 hours
- You'll get email when approved

### **STEP 6: Regenerate ALL Keys**

**After permissions are enabled:**

1. **API Key:**
   - Click **"Regenerate"**
   - Copy the NEW key
   - Update `.env`: `TWITTER_API_KEY=new_key_here`

2. **API Secret Key:**
   - Click **"Regenerate"**
   - Copy the NEW secret
   - Update `.env`: `TWITTER_API_SECRET=new_secret_here`

3. **Access Token:**
   - Click **"Regenerate"**
   - Copy the NEW token
   - Update `.env`: `TWITTER_ACCESS_TOKEN=new_token_here`

4. **Access Token Secret:**
   - Click **"Regenerate"**
   - Copy the NEW secret
   - Update `.env`: `TWITTER_ACCESS_TOKEN_SECRET=new_secret_here`

5. **Bearer Token:**
   - Click **"Regenerate"**
   - Copy the NEW token
   - Update `.env`: `TWITTER_BEARER_TOKEN=new_bearer_here`

### **STEP 7: Update .env File**

**On Your PC:**
```bash
# Open .env
notepad D:\DATA\HACKATHON_0\AI_Employee_Vault\.env

# Update ALL Twitter credentials
TWITTER_API_KEY=new_api_key_here
TWITTER_API_SECRET=new_api_secret_here
TWITTER_BEARER_TOKEN=new_bearer_token_here
TWITTER_ACCESS_TOKEN=new_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=new_access_token_secret_here

# Save and close
```

**Upload to Server:**
```powershell
scp -i "C:\Users\H P\.ssh\digitaloceonsshkey" D:\DATA\HACKATHON_0\AI_Employee_Vault\.env root@167.71.237.77:/home/AI_Employee_Vault/
```

### **STEP 8: Restart Services**

```bash
# SSH to server
ssh -i "C:\Users\H P\.ssh\digitaloceonsshkey" root@167.71.237.77

# Restart execute-approved
pm2 restart execute-approved

# Check logs
pm2 logs execute-approved --lines 30
```

### **STEP 9: Test Twitter Posting**

1. **Open dashboard:** http://167.71.237.77:5000
2. **Go to:** Twitter → Create Tweet
3. **Type:** "Testing new Twitter permissions! #AIEmployee"
4. **Click:** "Post to Twitter"
5. **Approve the task**
6. **Check logs:** Should see `✅ Tweet posted successfully`

---

## ⚠️ TROUBLESHOOTING

### **Still Getting 403 Error?**

**Check these:**

1. **App Permissions:**
   ```
   Must be: "Read and Write"
   NOT: "Read" only
   ```

2. **All Keys Regenerated:**
   ```
   Must regenerate ALL 5 keys after permission change
   API Key, API Secret, Access Token, Access Token Secret, Bearer Token
   ```

3. **Both .env Files Updated:**
   ```
   Local: D:\DATA\HACKATHON_0\AI_Employee_Vault\.env
   Server: /home/AI_Employee_Vault/.env
   ```

4. **Services Restarted:**
   ```bash
   pm2 restart execute-approved
   ```

### **App Under Review?**

- Some apps need Twitter approval before posting works
- Check email for approval status
- Usually takes 1-24 hours
- Can still test with your own account during review

---

## ✅ CORRECT SETTINGS SUMMARY

Your Twitter App should have:

```
✅ App Permissions: Read and Write
✅ Type of App: Web App, Automated App or Bot
✅ Callback URL: http://localhost:5000
✅ Website URL: https://example.com
✅ Organization: Your name/company
✅ Country: Pakistan
✅ Email: bashartc14@gmail.com
✅ All 5 keys regenerated after permission change
```

---

**After completing these steps, Twitter posting will work!** 🐦✅
