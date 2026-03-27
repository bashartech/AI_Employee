# 🔧 GMAIL WATCHER - HEADLESS SERVER AUTHENTICATION FIX

## **PROBLEM:**
When running `gmail_watcher.py` on a headless server (DigitalOcean/VPS), you get this error:

```
webbrowser.Error: could not locate runnable browser
```

**Reason:** The server has no browser, but `flow.run_local_server()` tries to open one.

---

## **SOLUTION: Update authenticate() Method**

### **Replace the authenticate() method in gmail_watcher.py with this:**

```python
def authenticate(self):
    """
    Authenticate with Gmail API - Headless Server Version
    Works on DigitalOcean/VPS without browser
    
    Based on: GMAIL_PRODUCTION_AUTOMATION Skill
    """
    try:
        # Load existing token from JSON
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
            
            # Create Credentials from JSON
            creds = Credentials(
                token=token_data["token"],
                refresh_token=token_data["refresh_token"],
                token_uri=token_data["token_uri"],
                client_id=token_data["client_id"],
                client_secret=token_data["client_secret"],
                scopes=token_data["scopes"]
            )
            
            # Refresh if expired
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                print("✅ Token refreshed successfully")
            
            # Set credentials and build service
            self.creds = creds
            self.service = build('gmail', 'v1', credentials=self.creds)
            
            print("✅ Gmail authentication successful")
            print("👁️ Watching Gmail inbox...")
            return True
        
        else:
            # No token.json found
            print("❌ token.json not found!")
            print("\n📋 SOLUTION:")
            print("1. Generate token on LOCAL machine:")
            print("   python generate_token.py")
            print("2. Upload to server:")
            print(f"   scp token.json root@167.71.237.77:/home/AI_Employee/")
            print("\n📋 OR use headless generation:")
            print("   python generate_token_headless.py")
            return False
    
    except FileNotFoundError as e:
        print(f"❌ Token file not found: {e}")
        print("\n📋 Please upload token.json from local machine")
        return False
    
    except json.JSONDecodeError as e:
        print(f"❌ Invalid token.json format: {e}")
        print("\n📋 Regenerate token.json")
        return False
    
    except Exception as e:
        print(f"❌ Gmail authentication error: {e}")
        print("\n📋 Common fixes:")
        print("1. Check credentials.json exists")
        print("2. Regenerate token.json")
        print("3. Ensure OAuth scopes match")
        return False
```

---

## **IMPORTANT: Required Imports**

Make sure these imports are at the top of `gmail_watcher.py`:

```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json
from pathlib import Path
```

---

## **HOW TO USE:**

### **Step 1: Update gmail_watcher.py on Server**

```bash
# SSH into server
ssh -i "C:\Users\H P\.ssh\digitaloceonsshkey" root@167.71.237.77

cd /home/AI_Employee
nano gmail_watcher.py

# Find the authenticate() method (around line 180-200)
# Replace ENTIRE method with the code above
# Save: Ctrl+O, Enter, Ctrl+X
```

### **Step 2: Ensure token.json Exists**

```bash
# Check if token.json exists
ls -la token.json credentials.json

# If missing, upload from local:
# From LOCAL PowerShell:
scp -i "C:\Users\H P\.ssh\digitaloceonsshkey" token.json root@167.71.237.77:/home/AI_Employee/
scp -i "C:\Users\H P\.ssh\digitaloceonsshkey" credentials.json root@167.71.237.77:/home/AI_Employee/
```

### **Step 3: Test Authentication**

```bash
# Activate venv
source /home/venv/bin/activate

# Test
python -c "from gmail_watcher import GmailWatcher; w = GmailWatcher(); w.authenticate()"

# Should show:
# ✅ Gmail authentication successful
# 👁️ Watching Gmail inbox...
```

### **Step 4: Run Gmail Watcher**

```bash
python gmail_watcher.py

# Output should be:
# ✅ Gmail authentication successful
# 👁️ Watching Gmail inbox...
# [Checking every 2 minutes...]
```

---

## **IF TOKEN.JSON IS MISSING:**

### **Option A: Generate Locally & Upload**

```powershell
# LOCAL machine (Windows)
cd D:\DATA\HACKATHON_0\AI_Employee_Vault
.\venv\Scripts\activate
python generate_token.py
# Browser opens → Login → Authorize
# token.json created

# Upload to server
scp -i "C:\Users\H P\.ssh\digitaloceonsshkey" token.json root@167.71.237.77:/home/AI_Employee/
```

### **Option B: Generate on Server (Headless)**

```bash
# On SERVER
ssh -i "C:\Users\H P\.ssh\digitaloceonsshkey" root@167.71.237.77
cd /home/AI_Employee
source /home/venv/bin/activate

# Create headless generation script
nano generate_token_headless.py
```

**Paste:**

```python
from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

# Delete old token
if os.path.exists(TOKEN_FILE):
    os.remove(TOKEN_FILE)
    print("🗑️ Deleted old token.json")

# Create flow
flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)

# Generate URL
auth_url, _ = flow.authorization_url(prompt='consent')

print("\n" + "="*60)
print("📋 STEP 1: Open this URL in LOCAL browser:")
print("="*60)
print(auth_url)
print("="*60)
print("\n📋 STEP 2: Login & Authorize")
print("📋 STEP 3: Copy authorization code")
print("📋 STEP 4: Paste below\n")

code = input("Enter authorization code: ")

# Fetch token
flow.fetch_token(code=code)
creds = flow.credentials

# Save as JSON
with open(TOKEN_FILE, "w") as f:
    json.dump({
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }, f)

print("\n✅ token.json created!")
```

**Run:**
```bash
python generate_token_headless.py
# Copy URL → Open locally → Authorize → Paste code → Done!
```

---

## **KEEP RUNNING 24/7:**

### **Use tmux:**

```bash
# Install tmux
apt install tmux -y

# Create session
tmux new -s gmail_watcher

# Run watcher
python gmail_watcher.py

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t gmail_watcher
```

### **Or systemd:**

```bash
cat > /etc/systemd/system/gmail_watcher.service << 'EOF'
[Unit]
Description=Gmail Watcher Service
After=network.target

[Service]
User=root
WorkingDirectory=/home/AI_Employee
Environment="PATH=/home/venv/bin"
ExecStart=/home/venv/bin/python /home/AI_Employee/gmail_watcher.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gmail_watcher
systemctl start gmail_watcher
systemctl status gmail_watcher
```

---

## **TROUBLESHOOTING:**

| Error | Solution |
|-------|----------|
| `token.json not found` | Upload from local or generate headless |
| `credentials.json not found` | Download from Google Cloud Console |
| `Token expired` | Auto-refreshes with refresh_token |
| `Invalid scopes` | Ensure scopes match in credentials.json |
| `Port in use` | Use headless flow (no port needed) |

---

## **✅ VERIFICATION:**

```bash
# Test authentication
python -c "from gmail_watcher import GmailWatcher; w = GmailWatcher(); w.authenticate()"

# Expected output:
# ✅ Gmail authentication successful
# 👁️ Watching Gmail inbox...
```

---

**Based on: GMAIL_PRODUCTION_AUTOMATION Skill**
**Works on: DigitalOcean, AWS, VPS, Headless Servers**
**Tested: Ubuntu 20.04/22.04, Python 3.10+**
