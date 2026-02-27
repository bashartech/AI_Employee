"""
LinkedIn Setup - Login and Save Session
Run this once to login to LinkedIn and save your session
"""

import sys
import os
from pathlib import Path
import time

# Fix emoji encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

VAULT = Path(__file__).parent.parent
LINKEDIN_SESSION = VAULT / "linkedin_session"

def login_to_linkedin():
    """Login to LinkedIn and save session"""
    print("="*60)
    print("LINKEDIN LOGIN")
    print("="*60)
    print()
    print("This will open a browser for you to login to LinkedIn.")
    print("Your session will be saved for future use.")
    print()
    print("IMPORTANT:")
    print("1. Login with your LinkedIn credentials")
    print("2. Wait for the feed to load completely")
    print("3. Close the browser when done")
    print()
    print("Opening browser in 3 seconds...")
    
    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch_persistent_context(
                str(LINKEDIN_SESSION),
                headless=False,  # Show browser for login
                args=['--disable-gpu']
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Go to LinkedIn
            print("\nOpening LinkedIn...")
            page.goto('https://www.linkedin.com/login', wait_until='networkidle')
            
            print("Please login to LinkedIn...")
            print("Waiting for you to login (max 5 minutes)...")
            
            # Wait for user to login (up to 5 minutes)
            start_time = time.time()
            timeout = 300  # 5 minutes
            
            while time.time() - start_time < timeout:
                try:
                    # Check if logged in (feed is visible)
                    if page.query_selector('[data-id="feed"]'):
                        print("\n✅ Login detected!")
                        time.sleep(2)  # Wait for page to fully load
                        break
                except:
                    pass
                time.sleep(1)
            else:
                print("\n⚠️  Login timeout. Please try again.")
            
            print("\nSession saved to:", LINKEDIN_SESSION)
            print()
            print("✅ LinkedIn session saved successfully!")
            print()
            print("You can now run: python linkedin_watcher.py")
            print()
            
            # Keep browser open for a moment
            time.sleep(3)
            browser.close()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease try again.")


if __name__ == "__main__":
    login_to_linkedin()
