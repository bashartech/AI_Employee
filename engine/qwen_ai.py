"""
Qwen AI Integration for AI Employee Vault
Uses Ollama to run Qwen locally - FREE!

Requirements:
1. Ollama installed: curl -fsSL https://ollama.com/install.sh | sh
2. Qwen model downloaded: ollama pull qwen2.5:1.5b
3. Ollama running: systemctl start ollama
"""

import subprocess
import sys
from pathlib import Path

# Check if Ollama is available
def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

# Check if Qwen model is available
def check_qwen_model():
    """Check if Qwen model is downloaded"""
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return 'qwen' in result.stdout.lower()
    except:
        return False

def run_qwen(prompt, model="qwen2.5:0.5b", timeout=600):
    """
    Run Qwen AI and get response
    
    Args:
        prompt: The prompt to send to Qwen
        model: The model to use (default: qwen2.5:0.5b - FAST!)
        timeout: Timeout in seconds (default: 60)
    
    Returns:
        str: Qwen's response, or None if error
    """
    try:
        result = subprocess.run(
            ['ollama', 'run', model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            print(f"Qwen error: {result.stderr}", file=sys.stderr)
            return None
            
    except subprocess.TimeoutExpired:
        print(f"Qwen timed out after {timeout}s - using template instead", file=sys.stderr)
        return None
    except FileNotFoundError:
        print("Ollama not found. Install: curl -fsSL https://ollama.com/install.sh | sh", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Qwen error: {e}", file=sys.stderr)
        return None

def format_email(request):
    """
    Format a professional email using Qwen
    
    Args:
        request: The email request (e.g., "send email to john@example.com about pricing")
    
    Returns:
        str: Formatted email body, or None if error
    """
    system_prompt = """You are a professional email assistant. Write a professional email based on the request.

Rules:
- Use professional but friendly tone
- Include proper greeting and closing
- Keep it concise and clear (100-200 words)
- Sign off as "M. Bashar Sheikh, AI Employee Vault"
- Do not include subject line, just the email body

Request:"""

    full_prompt = f"{system_prompt}\n\n{request}"
    result = run_qwen(full_prompt)
    
    # If Qwen returns empty or None, return None to trigger fallback
    if not result or len(result.strip()) < 50:
        return None
    
    return result

def format_linkedin_post(request):
    """
    Create a professional LinkedIn post using Qwen
    
    Args:
        request: The post request (e.g., "create post about AI automation")
    
    Returns:
        str: Formatted LinkedIn post with hashtags, or None if error
    """
    system_prompt = """You are a professional LinkedIn content creator. Write an engaging LinkedIn post.

Rules:
- Start with an engaging hook (use 1-2 emojis)
- Use 2-3 short paragraphs (150-250 words total)
- Add 3-5 relevant hashtags at the end
- Make it professional but conversational
- Include a call-to-action or question

Topic:"""

    full_prompt = f"{system_prompt}\n\n{request}"
    return run_qwen(full_prompt)

def format_whatsapp_message(request):
    """
    Format a friendly WhatsApp message using Qwen
    
    Args:
        request: The message request (e.g., "follow up with client about invoice")
    
    Returns:
        str: Formatted WhatsApp message, or None if error
    """
    system_prompt = """You are a friendly messaging assistant. Write a casual but professional WhatsApp message.

Rules:
- Keep it short and friendly (50-100 words)
- Use casual but respectful tone
- Include greeting
- Get straight to the point
- Sign off briefly

Request:"""

    full_prompt = f"{system_prompt}\n\n{request}"
    return run_qwen(full_prompt)

def format_odoo_lead(request):
    """
    Extract lead information from text using Qwen
    
    Args:
        request: The lead request (e.g., "create lead: John Smith, john@test.com, +1234567890, from website")
    
    Returns:
        str: Formatted lead info (Name, Email, Phone, Source), or None if error
    """
    system_prompt = """Extract lead information from this text and return in this exact format:

Name: [full name]
Email: [email address]
Phone: [phone number with country code]
Source: [where the lead came from]

If any field is not found, write "Not provided" for that field.

Text:"""

    full_prompt = f"{system_prompt}\n\n{request}"
    return run_qwen(full_prompt)

def parse_lead_info(formatted_text):
    """
    Parse Qwen's formatted lead info into a dictionary
    
    Args:
        formatted_text: Qwen's formatted response
    
    Returns:
        dict: Dictionary with name, email, phone, source keys
    """
    import re
    
    result = {
        'name': 'Unknown Lead',
        'email': '',
        'phone': '',
        'source': 'Dashboard'
    }
    
    if not formatted_text:
        return result
    
    # Extract name
    name_match = re.search(r'Name:\s*(.+?)(?:\n|$)', formatted_text, re.IGNORECASE)
    if name_match and name_match.group(1).strip() != 'Not provided':
        result['name'] = name_match.group(1).strip()
    
    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', formatted_text)
    if email_match:
        result['email'] = email_match.group(0)
    
    # Extract phone
    phone_match = re.search(r'Phone:\s*(\+?[\d\s-]{8,})', formatted_text, re.IGNORECASE)
    if phone_match and 'Not provided' not in phone_match.group(1):
        result['phone'] = phone_match.group(1).strip()
    
    # Extract source
    source_match = re.search(r'Source:\s*(.+?)(?:\n|$)', formatted_text, re.IGNORECASE)
    if source_match and 'Not provided' not in source_match.group(1):
        result['source'] = source_match.group(1).strip()
    
    return result

# Test function
if __name__ == "__main__":
    print("="*60)
    print("QWEN AI INTEGRATION TEST")
    print("="*60)
    print()
    
    # Check Ollama
    print("1. Checking Ollama...")
    if check_ollama():
        print("   ✅ Ollama is installed")
    else:
        print("   ❌ Ollama not found")
        print("   Install: curl -fsSL https://ollama.com/install.sh | sh")
        sys.exit(1)
    
    # Check Qwen model
    print("2. Checking Qwen model...")
    if check_qwen_model():
        print("   ✅ Qwen model is available")
    else:
        print("   ❌ Qwen model not found")
        print("   Download: ollama pull qwen2.5:1.5b")
        sys.exit(1)
    
    # Test email formatting
    print("3. Testing email formatting...")
    test_email = "send email to bashartc13@gmail.com about AI automation services pricing"
    result = format_email(test_email)
    if result:
        print(f"   ✅ Email formatted ({len(result)} chars)")
        print(f"   Preview: {result[:100]}...")
    else:
        print("   ❌ Email formatting failed")
    
    # Test LinkedIn post
    print("4. Testing LinkedIn post...")
    test_post = "AI automation for business productivity"
    result = format_linkedin_post(test_post)
    if result:
        print(f"   ✅ Post created ({len(result)} chars)")
        print(f"   Preview: {result[:100]}...")
    else:
        print("   ❌ Post creation failed")
    
    # Test WhatsApp message
    print("5. Testing WhatsApp message...")
    test_whatsapp = "follow up with client about pending invoice payment"
    result = format_whatsapp_message(test_whatsapp)
    if result:
        print(f"   ✅ Message formatted ({len(result)} chars)")
        print(f"   Preview: {result[:80]}...")
    else:
        print("   ❌ Message formatting failed")
    
    # Test lead extraction
    print("6. Testing lead extraction...")
    test_lead = "create new lead: Sarah Johnson, sarah@techcorp.com, +923001234567, from LinkedIn"
    result = format_odoo_lead(test_lead)
    if result:
        parsed = parse_lead_info(result)
        print(f"   ✅ Lead extracted")
        print(f"   Name: {parsed['name']}")
        print(f"   Email: {parsed['email']}")
        print(f"   Phone: {parsed['phone']}")
        print(f"   Source: {parsed['source']}")
    else:
        print("   ❌ Lead extraction failed")
    
    print()
    print("="*60)
    print("✅ QWEN AI TEST COMPLETE")
    print("="*60)
