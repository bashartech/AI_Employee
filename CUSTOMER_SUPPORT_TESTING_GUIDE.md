# Customer Support AI - Testing Guide

## 🎯 Overview

The Customer Support AI now handles **TWO types of queries**:

1. **Support Tickets** - Issues, problems, complaints (requires human approval)
2. **General Inquiries** - Company info, products, locations, FAQs (can auto-respond)

---

## 📁 Knowledge Base Structure

```
Knowledge_Base/
├── company_info.md       # Company details, mission, values
├── products.md           # Products, courses, prices
├── locations.md          # Office locations, training centers
├── faq.md               # Frequently asked questions
└── (add more as needed)
```

---

## 🧪 Test Scenarios

### **Test 1: General Inquiry - Auto-Response**

**Send email with:**
```
From: customer@example.com
Subject: What are your business hours?

Hi,

I would like to know your business hours. When are you open?

Thanks,
John
```

**Expected Result:**
- ✅ Query classified as `general_inquiry`
- ✅ Knowledge base searched automatically
- ✅ Answer found in `faq.md` or `company_info.md`
- ✅ **Auto-response generated** (no human approval needed if confidence > 0.6)
- ✅ Email sent with answer

---

### **Test 2: Support Issue - Human Approval Required**

**Send email with:**
```
From: customer@example.com
Subject: Software not working - URGENT

Hello,

Your software is not working! I'm getting an error when I try to login. This is urgent!

Please help immediately.

Angry Customer
```

**Expected Result:**
- ✅ Query classified as `support_ticket` (urgent)
- ✅ Ticket ID generated: `SUP-20260326...`
- ✅ Google Doc created
- ✅ Logged to Google Sheets (if available)
- ✅ **Approval file created** in `Pending Approval/` folder
- ✅ **Requires human approval** before sending
- ✅ Move to `Approved/` to send response

---

### **Test 3: Product Question - Auto-Response**

**Send email with:**
```
From: student@example.com
Subject: Full Stack course price

Hi,

I'm interested in your Full Stack Development course. How much does it cost and when is the next batch?

Thanks,
Sarah
```

**Expected Result:**
- ✅ Query classified as `general_inquiry`
- ✅ Answer found in `products.md`
- ✅ **Auto-response** with course details:
  - Price: $2,499 (Part-time), $3,999 (Full-time)
  - Next batch: April 15, 2026
- ✅ Email sent automatically

---

### **Test 4: Location Question - Auto-Response**

**Send email with:**
```
From: visitor@example.com
Subject: Office location

Hello,

Where are your offices located? I'd like to visit.

Best,
Mike
```

**Expected Result:**
- ✅ Query classified as `general_inquiry`
- ✅ Answer found in `locations.md`
- ✅ **Auto-response** with office addresses:
  - Headquarters: Tech City
  - Regional: New York, San Francisco, Chicago
  - Training: Boston, Seattle, Austin
- ✅ Email sent automatically

---

### **Test 5: Billing Issue - Human Approval**

**Send email with:**
```
From: customer@example.com
Subject: I want a refund!

This is unacceptable! Your product doesn't work and I want my money back!

I demand a refund immediately!

Frustrated Customer
```

**Expected Result:**
- ✅ Query classified as `support_ticket` (billing + urgent)
- ✅ **High priority** ticket created
- ✅ **Human approval required**
- ✅ Approval file created in `Pending Approval/`
- ✅ Move to `Approved/` to send response

---

## 🔍 How to Test

### **Step 1: Start Required Services**

```bash
# Terminal 1: Start orchestrator
python orchestrator.py

# Terminal 2: Start email executor (for auto-sending)
python execute_approved.py
```

### **Step 2: Send Test Emails**

Create test email files in `Needs Action/` folder:

```markdown
---
from: test@example.com
subject: Test Question
---

# Test Email

This is a test question about [topic].

## Email Content

[Your question here]
```

### **Step 3: Observe Results**

**Check logs for:**
- Query classification
- Knowledge base search results
- Auto-response or approval file creation

**Check folders:**
- `Pending Approval/` - Approval files (support tickets)
- `Approved/` - Ready to send
- `Done/` - Processed emails
- `Support_Tickets/` - Ticket records

---

## 📊 Expected Behavior Matrix

| Query Type | Example | Classification | Auto-Response | Human Approval |
|------------|---------|----------------|---------------|----------------|
| **General Info** | "What are your hours?" | `general_inquiry` | ✅ Yes (if confidence > 0.6) | ❌ No |
| **Product Question** | "How much is the course?" | `general_inquiry` | ✅ Yes | ❌ No |
| **Location** | "Where are you located?" | `general_inquiry` | ✅ Yes | ❌ No |
| **Technical Issue** | "Software not working" | `support_ticket` | ❌ No | ✅ Yes |
| **Billing/Refund** | "I want refund" | `support_ticket` | ❌ No | ✅ Yes |
| **Complaint** | "This is unacceptable!" | `support_ticket` | ❌ No | ✅ Yes |
| **Urgent** | "URGENT! Need help!" | `support_ticket` (high) | ❌ No | ✅ Yes |

---

## 🎯 Confidence Scoring

The AI uses confidence scoring to decide auto-response vs human:

- **Confidence > 0.6**: Auto-respond with answer from knowledge base
- **Confidence 0.3 - 0.6**: Provide partial info, escalate to human
- **Confidence < 0.3**: Escalate to human immediately

---

## 📝 Sample Test Commands

### Test Knowledge Base Search

```python
from services.knowledge_base import KnowledgeBaseService

kb = KnowledgeBaseService()

# Test search
results = kb.search("What is the refund policy?", top_k=3)
for result in results:
    print(f"Document: {result['document']}")
    print(f"Section: {result['section']}")
    print(f"Score: {result['score']}")
    print(f"Content: {result['content'][:200]}...")
    print()

# Test classification
classification = kb.classify_query("My software is broken!")
print(f"Type: {classification['type']}")
print(f"Priority: {classification['priority']}")
```

### Test Query Response

```python
from services.knowledge_base import KnowledgeBaseService

kb = KnowledgeBaseService()

# Test full response generation
response = kb.generate_response("How much does Full Stack cost?")
print(f"Requires Human: {response['requires_human']}")
print(f"Type: {response['type']}")
print(f"Answer: {response['answer'][:500]}...")
print(f"Confidence: {response['confidence']}")
```

---

## ✅ Success Criteria

### **For General Inquiries:**
- [ ] Query correctly classified as `general_inquiry`
- [ ] Relevant information found in knowledge base
- [ ] Auto-response generated (if confidence high)
- [ ] Email sent without human intervention
- [ ] Response is accurate and helpful

### **For Support Tickets:**
- [ ] Query correctly classified as `support_ticket`
- [ ] Priority correctly assigned (normal/high/urgent)
- [ ] Ticket file created in `Support_Tickets/`
- [ ] Approval file created in `Pending Approval/`
- [ ] Human approval required before sending
- [ ] Google Doc created (if Google services available)
- [ ] Logged to Google Sheets (if available)

---

## 🚀 Next Steps

After testing:

1. **Add more knowledge base articles** as needed
2. **Fine-tune confidence thresholds** based on results
3. **Add more response templates** for common queries
4. **Monitor auto-responses** for quality assurance
5. **Expand KB** with company-specific information

---

## 📞 Support

If you encounter issues during testing:

- Check logs in `logs/` folder
- Verify knowledge base files exist in `Knowledge_Base/`
- Ensure Google credentials are valid (for Docs/Sheets)
- Run `python -m services.knowledge_base` to test KB service

---

**Happy Testing! 🎉**
