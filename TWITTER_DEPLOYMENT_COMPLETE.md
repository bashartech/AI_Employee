# 🐦 Twitter Integration - COMPLETE DEPLOYMENT GUIDE

## ✅ ALL STEPS COMPLETED!

### **Files Created/Modified:**

**Created:**
1. ✅ `engine/twitter_manager.py` - Twitter API integration
2. ✅ `TWITTER_FINAL_STEPS.md` - Implementation guide

**Modified:**
1. ✅ `engine/orchestrator.py` - Added Twitter task processing
2. ✅ `dashboard/app.py` - Added Twitter API endpoints
3. ✅ `execute_approved.py` - Added Twitter execution
4. ✅ `.env` - Twitter credentials added

---

## 📋 REMAINING STEP: Dashboard UI

The ONLY thing left is adding the Twitter UI to the dashboard HTML.

**File to update:** `dashboard/templates/index.html`

**Add this section** after the Facebook section (around line 600):

```html
<!-- Twitter Management Section -->
<section class="upload-section">
    <div class="section-header">
        <h3>🐦 Twitter Management</h3>
        <p>Post tweets and threads (requires approval)</p>
    </div>
    
    <div class="fb-tabs">
        <button class="fb-tab-btn active" onclick="showTwitterTab('create')">✍️ Create Tweet</button>
        <button class="fb-tab-btn" onclick="showTwitterTab('tweets')">📝 Recent Tweets</button>
        <button class="fb-tab-btn" onclick="showTwitterTab('profile')">ℹ️ Profile</button>
    </div>
    
    <!-- Create Tweet Tab -->
    <div class="fb-tab-content active" id="twitter-tab-create">
        <form id="twitterCreateForm" class="upload-form">
            <div class="form-group">
                <label for="twitterMessage">Tweet Content:</label>
                <textarea id="twitterMessage" name="message" placeholder="What's happening?" required style="min-height: 150px;"></textarea>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="twitterIsThread" name="is_thread">
                    Post as Thread (split by blank lines)
                </label>
            </div>
            <button type="submit" class="btn btn-primary">🐦 Post to Twitter (Requires Approval)</button>
        </form>
        <div id="twitterCreateStatus" class="upload-status"></div>
    </div>
    
    <!-- Recent Tweets Tab -->
    <div class="fb-tab-content" id="twitter-tab-tweets">
        <button class="btn btn-primary" onclick="loadTwitterTweets()">🔄 Load Recent Tweets</button>
        <div id="twitterTweetsList" style="margin-top: 20px;"></div>
    </div>
    
    <!-- Profile Tab -->
    <div class="fb-tab-content" id="twitter-tab-profile">
        <button class="btn btn-primary" onclick="loadTwitterProfile()">ℹ️ Load Profile</button>
        <div id="twitterProfileInfo" style="margin-top: 20px;"></div>
    </div>
</section>

<script>
// Twitter Tab Switching
function showTwitterTab(tab) {
    document.querySelectorAll('[id^="twitter-tab-"]').forEach(content => content.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('twitter-tab-' + tab).classList.add('active');
}

// Create Twitter Post
document.getElementById('twitterCreateForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = document.getElementById('twitterMessage').value;
    const isThread = document.getElementById('twitterIsThread').checked;
    const statusDiv = document.getElementById('twitterCreateStatus');
    
    try {
        statusDiv.className = 'upload-status';
        statusDiv.textContent = '⏳ Creating approval task...';
        statusDiv.style.display = 'block';
        
        const response = await fetch('/api/twitter/post', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: message, is_thread: isThread})
        });
        
        const result = await response.json();
        
        if (result.success) {
            statusDiv.className = 'upload-status success';
            statusDiv.textContent = `✅ Twitter task created! Awaiting approval in Needs Action folder.`;
            statusDiv.style.display = 'block';
            document.getElementById('twitterCreateForm').reset();
            refreshDashboard();
        } else {
            throw new Error(result.error || 'Failed to create task');
        }
    } catch (error) {
        statusDiv.className = 'upload-status error';
        statusDiv.textContent = '❌ Error: ' + error.message;
        statusDiv.style.display = 'block';
    }
    
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
});

// Load Twitter Profile
async function loadTwitterProfile() {
    const infoDiv = document.getElementById('twitterProfileInfo');
    infoDiv.innerHTML = '<p>Loading profile...</p>';
    
    try {
        const response = await fetch('/api/twitter/profile');
        const result = await response.json();
        
        if (result.success && result.profile) {
            const p = result.profile;
            infoDiv.innerHTML = `
                <div class="fb-post-item">
                    <div><strong>👤 Name:</strong> ${p.name}</div>
                    <div><strong>📧 Username:</strong> @${p.username}</div>
                    <div><strong>📊 Followers:</strong> ${p.followers}</div>
                    <div><strong>👥 Following:</strong> ${p.following}</div>
                    <div><strong>📝 Bio:</strong> ${p.bio || 'N/A'}</div>
                </div>
            `;
        } else {
            infoDiv.innerHTML = '<p>Error loading profile: ' + (result.error || 'Unknown error') + '</p>';
        }
    } catch (error) {
        infoDiv.innerHTML = '<p>Error: ' + error.message + '</p>';
    }
}

// Load Twitter Tweets
async function loadTwitterTweets() {
    const tweetsDiv = document.getElementById('twitterTweetsList');
    tweetsDiv.innerHTML = '<p>Loading tweets...</p>';
    
    try {
        const response = await fetch('/api/twitter/tweets?limit=5');
        const result = await response.json();
        
        if (result.success && result.tweets) {
            let html = '';
            result.tweets.forEach(tweet => {
                const created = new Date(tweet.created_at).toLocaleDateString();
                html += `
                    <div class="fb-post-item">
                        <div><strong>📅 Posted:</strong> ${created}</div>
                        <div style="margin: 10px 0;">${tweet.text}</div>
                        <div style="margin: 10px 0; color: var(--text-secondary);">
                            ❤️ ${tweet.likes} | 🔄 ${tweet.retweets} | 💬 ${tweet.replies}
                        </div>
                    </div>
                `;
            });
            tweetsDiv.innerHTML = html;
        } else {
            tweetsDiv.innerHTML = '<p>Error loading tweets: ' + (result.error || 'Unknown error') + '</p>';
        }
    } catch (error) {
        tweetsDiv.innerHTML = '<p>Error: ' + error.message + '</p>';
    }
}
</script>
```

---

## 🚀 DEPLOYMENT

### **Upload All Files:**

```powershell
# Upload all files to server
scp -i "C:\Users\H P\.ssh\digitaloceonsshkey" D:\DATA\HACKATHON_0\AI_Employee_Vault\engine\twitter_manager.py root@167.71.237.77:/home/AI_Employee_Vault/engine/
scp -i "C:\Users\H P\.ssh\digitaloceonsshkey" D:\DATA\HACKATHON_0\AI_Employee_Vault\dashboard\app.py root@167.71.237.77:/home/AI_Employee_Vault/dashboard/
scp -i "C:\Users\H P\.ssh\digitaloceonsshkey" D:\DATA\HACKATHON_0\AI_Employee_Vault\dashboard\templates\index.html root@167.71.237.77:/home/AI_Employee_Vault/dashboard/templates/
scp -i "C:\Users\H P\.ssh\digitaloceonsshkey" D:\DATA\HACKATHON_0\AI_Employee_Vault\engine\orchestrator.py root@167.71.237.77:/home/AI_Employee_Vault/engine/
scp -i "C:\Users\H P\.ssh\digitaloceonsshkey" D:\DATA\HACKATHON_0\AI_Employee_Vault\execute_approved.py root@167.71.237.77:/home/AI_Employee_Vault/

echo "✅ All files uploaded!"
```

### **Install Tweepy:**

```bash
ssh -i "C:\Users\H P\.ssh\digitaloceonsshkey" root@167.71.237.77
cd /home/AI_Employee_Vault
source venv/bin/activate
pip install tweepy
```

### **Restart Services:**

```bash
pm2 restart all
pm2 status
```

### **Test Twitter Connection:**

```bash
cd /home/AI_Employee_Vault
python engine/twitter_manager.py
```

**Expected output:**
```
✅ Twitter authenticated as: @YourUsername
   Name: Your Name
   Followers: 123
```

---

## ✅ COMPLETE WORKFLOW

```
Dashboard → Create Tweet → Needs Action/ → Orchestrator → Pending Approval/
  → You Approve → execute_approved.py → Posted to Twitter → Done/
```

**Limits:** 1,500 tweets/month (50/day)

---

## 🧪 TEST IT

1. **Open dashboard:** http://167.71.237.77:5000
2. **Go to:** Twitter tab
3. **Create Tweet:** Type "Testing Twitter integration! #AIEmployee"
4. **Click:** "Post to Twitter"
5. **Check:** `Needs Action/` folder for task file
6. **Approve:** Move file to `Approved/`
7. **Check logs:** `pm2 logs execute-approved --lines 30`
8. **Verify:** Check your Twitter profile - tweet should appear!

---

**All code is ready! Just add the UI and deploy!** 🚀
