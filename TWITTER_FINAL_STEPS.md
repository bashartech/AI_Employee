# 🐦 Twitter Integration - FINAL STEPS

## ✅ COMPLETED (Steps 1-3):

1. ✅ Created `engine/twitter_manager.py`
2. ✅ Updated `dashboard/app.py` with Twitter endpoints
3. ✅ Updated `engine/orchestrator.py` with Twitter processing

---

## 📋 REMAINING STEPS (4-5):

### **STEP 4: Update execute_approved.py**

Add this method to the `ApprovedExecutor` class:

```python
def execute_twitter(self, file_path: Path) -> bool:
    """Execute approved Twitter post/thread"""
    try:
        from engine.twitter_manager import TwitterManager
        
        logger.info(f"[TWITTER] Executing: {file_path.name}")
        
        # Read approval file
        content = file_path.read_text(encoding='utf-8')
        
        # Extract action type
        action = self.extract_yaml_field(content, 'action')
        
        if not action:
            logger.error(f"[TWITTER] No action specified in {file_path.name}")
            return False
        
        manager = TwitterManager()
        
        # Extract content
        if "## Content" in content:
            parts = content.split("## Content", 1)
            if len(parts) > 1:
                msg_part = parts[1].strip()
                if "##" in msg_part:
                    msg_part = msg_part.split("##")[0].strip()
                message = msg_part
            else:
                message = ""
        else:
            message = ""
        
        if not message:
            logger.error(f"[TWITTER] No content found in {file_path.name}")
            return False
        
        # Check if thread
        is_thread = 'thread' in action
        
        if is_thread:
            # Split message into thread tweets (by newlines)
            tweets = [t.strip() for t in message.split('\n\n') if t.strip()]
            result = manager.post_thread(tweets)
        else:
            result = manager.post_tweet(message)
        
        if result.get('success'):
            logger.info(f"[TWITTER] {'Thread' if is_thread else 'Post'} posted successfully")
            self._create_execution_log(file_path, 'twitter', 'success', result)
            return True
        else:
            logger.error(f"[TWITTER] Post failed: {result.get('error')}")
            return False
    
    except Exception as e:
        logger.error(f"[TWITTER] Error: {e}")
        return False
```

**Update `process_approved_file` method:**

```python
def process_approved_file(self, file_path: Path):
    """Process a single approved file"""
    try:
        content = file_path.read_text(encoding='utf-8')

        # Determine action type and execute
        if "APPROVAL_send_email" in file_path.name or "action: send_email" in content:
            success = self.execute_email(file_path)
        elif "APPROVAL_send_whatsapp" in file_path.name or "action: send_whatsapp" in content:
            success = self.execute_whatsapp(file_path)
        elif "APPROVAL_linkedin_post" in file_path.name or "LINKEDIN_POST" in file_path.name or "action: linkedin_post" in content:
            success = self.execute_linkedin(file_path)
        elif "APPROVAL_twitter" in file_path.name or "action: twitter" in content:
            success = self.execute_twitter(file_path)  # NEW!
        elif "APPROVAL_facebook" in file_path.name or "action: facebook" in content:
            success = self.execute_facebook(file_path)
        elif "ODOO_LEAD" in file_path.name or "action: create_lead" in content:
            success = self.execute_odoo_lead(file_path)
        elif "ODOO_INV" in file_path.name or "action: create_invoice" in content:
            success = self.execute_odoo_invoice(file_path)
        elif "ODOO_QUO" in file_path.name or "action: create_quotation" in content:
            success = self.execute_odoo_quotation(file_path)
        else:
            logger.info(f"[SKIP] Unknown action type: {file_path.name}")
            return

        # Move file to Done folder
        if success:
            dest = self.done_folder / file_path.name
            shutil.move(str(file_path), str(dest))
            logger.info(f"[DONE] Moved {file_path.name} to Done/")
        else:
            logger.warning(f"[WAIT] Keeping {file_path.name} in Approved/ due to failure")

    except Exception as e:
        logger.error(f"[ERROR] Processing {file_path.name}: {e}")
```

**Update `process_all_approved` method:**

```python
def process_all_approved(self):
    """Process all approved files in Approved folder"""
    logger.info("[EXECUTOR] Checking for approved actions...")

    # Process email approvals
    for file_path in self.approved_folder.glob("APPROVAL_send_email_*.md"):
        self.process_approved_file(file_path)

    # Process WhatsApp approvals
    for file_path in self.approved_folder.glob("APPROVAL_send_whatsapp_*.md"):
        self.process_approved_file(file_path)

    # Process LinkedIn approvals (both patterns)
    for file_path in self.approved_folder.glob("APPROVAL_linkedin_post_*.md"):
        self.process_approved_file(file_path)
    for file_path in self.approved_folder.glob("APPROVAL_linkedin_*.md"):
        self.process_approved_file(file_path)
    for file_path in self.approved_folder.glob("LINKEDIN_POST_*.md"):
        self.process_approved_file(file_path)

    # Process Twitter approvals (NEW!)
    for file_path in self.approved_folder.glob("APPROVAL_twitter_*.md"):
        self.process_approved_file(file_path)

    # Process Facebook approvals
    for file_path in self.approved_folder.glob("APPROVAL_facebook_*.md"):
        self.process_approved_file(file_path)

    # Process Odoo approvals (Gold Tier)
    for file_path in self.approved_folder.glob("ODOO_LEAD_*.md"):
        self.process_approved_file(file_path)
    for file_path in self.approved_folder.glob("ODOO_INV_*.md"):
        self.process_approved_file(file_path)
    for file_path in self.approved_folder.glob("ODOO_QUO_*.md"):
        self.process_approved_file(file_path)
```

---

### **STEP 5: Add Twitter UI to Dashboard**

Add this HTML section to `dashboard/templates/index.html` after the Facebook section:

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

<style>
/* Twitter tabs use same styles as Facebook (.fb-tabs, .fb-tab-btn, etc.) */
</style>

<script>
// Twitter Tab Switching
function showTwitterTab(tab) {
    document.querySelectorAll('[id^="twitter-tab-"]').forEach(content => content.classList.remove('active'));
    document.querySelectorAll('.fb-tab-btn').forEach(btn => btn.classList.remove('active'));
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
# Upload all files
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

### **Test Twitter:**

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

**All code is ready! Upload and test!** 🚀
