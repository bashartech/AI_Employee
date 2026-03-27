---
name: "hr-resume-automation"
description: "Complete HR hiring automation with resume parsing from multiple formats (PDF, Word, Images, Google Docs, Email), OCR support, candidate scoring, Google Sheets/Docs/Calendar integration, and interview scheduling"
---

# HR Resume Automation - Complete Guide

## Overview

This automation handles the **complete hiring workflow**:
1. **Receive** resumes via email (multiple formats)
2. **Parse** resume data (OCR for scanned PDFs)
3. **Score** candidates (0-100 with breakdown)
4. **Log** to Google Sheets
5. **Create** Google Doc profile
6. **Schedule** interview (if score >= 80)
7. **Send** rejection/interview email

---

## Quick Start

### Step 1: Installation (First Time Only)

```bash
# Core dependencies
pip install pdfplumber python-docx pillow pytesseract pdf2image

# Google APIs (for Sheets, Docs, Calendar)
pip install google-auth google-auth-oauthlib google-api-python-client

# OCR for Windows (Download & Install)
# https://github.com/UB-Mannheim/tesseract/wiki
# Download: tesseract-ocr-w64-setup-5.x.x.exe
# Install to: C:\Program Files\Tesseract-OCR

# Poppler for PDF OCR (Download)
# https://github.com/oschwartz10612/poppler-windows/releases
# Extract to: C:\Program Files\poppler
# Add to PATH: C:\Program Files\poppler\Library\bin
```

### Step 2: Google Authentication

```bash
# Generate Google token
python generate_token.py
```
- Browser opens → Login to Google
- Authorize: Gmail, Sheets, Docs, Calendar
- Token saved to `token.json`

### Step 3: Start Automation

```bash
# Keep running (monitors Gmail)
python gmail_watcher.py

# Keep running (processes approvals)
python execute_approved.py
```

---

## Supported Resume Formats

| Format | Support | Details |
|--------|---------|---------|
| **Email Body Text** | ✅ Full | Paste resume directly in email |
| **PDF (Text-based)** | ✅ Full | From Word/Google Docs export |
| **PDF (Scanned)** | ✅ OCR | Image-based PDFs with OCR |
| **Word Documents** | ✅ Full | .docx, .doc via python-docx |
| **Google Docs** | ✅ Full | Share link → Fetch content |
| **Images** | ✅ OCR | PNG, JPG, JPEG via OCR |
| **Text Files** | ✅ Full | .txt, .md files |

---

## Workflow (Automatic)

```
Email with Resume
       ↓
Gmail Watcher (every 2 min)
       ↓
Detect Job Application (70%+ confidence)
       ↓
Extract Resume (attachment OR email body OR Google Docs link)
       ↓
Parse Resume (OCR if scanned/image)
       ↓
Score Candidate (0-100)
       ↓
┌──────────────────────────────────────┐
│ Score >= 80: Interview Path          │
│ - Log to Google Sheets               │
│ - Create Google Doc                  │
│ - Schedule Interview (Calendar)      │
│ - Create Interview Email Approval    │
└──────────────────────────────────────┘
       OR
┌──────────────────────────────────────┐
│ Score < 80: Review/Reject Path       │
│ - Log to Google Sheets               │
│ - Create Google Doc                  │
│ - Create Rejection Email Approval    │
└──────────────────────────────────────┘
       ↓
Human Reviews Approval File
       ↓
Move to Approved/ Folder
       ↓
execute_approved.py Sends Email
       ↓
Move to Done/
```

---

## Commands Summary

| Action | Command |
|--------|---------|
| Start Gmail monitoring | `python gmail_watcher.py` |
| Process HR applications | `Process HR applications` |
| Send approved emails | **Automatic** (via `execute_approved.py`) |

**Keep these running:**
```bash
# Terminal 1: Gmail watcher
python gmail_watcher.py

# Terminal 2: Approval executor
python execute_approved.py
```

---

## Example: Email with PDF Attachment

**Email received:**
- **From:** candidate@example.com
- **Subject:** Apply for Full Stack Developer
- **Attachment:** resume.pdf

**Automation Flow:**

1. **Gmail Watcher** detects job application (70% confidence)
2. **Extracts** PDF attachment → `Resumes/RESUME_*.pdf`
3. **Creates** task: `Needs Action/HR_APPLICATION_*.md`
4. **Orchestrator** processes HR application
5. **Resume Parser** extracts:
   ```
   Name: John Doe
   Email: john.doe@email.com
   Phone: +1 (555) 123-4567
   Skills: Python, React, Node.js, AWS (15 skills)
   Experience: 5 years
   Education: Bachelor Computer Science
   Score: 82/100 (Grade: A)
   ```
6. **Google Sheets** logs candidate
7. **Google Docs** creates profile
8. **Google Calendar** schedules interview
9. **Creates approval**: `Pending Approval/APPROVAL_interview_*.md`
10. **You** move to `Approved/`
11. **Executor** sends interview email! ✅

---

## Example: Email with Resume in Body

**Email received:**
```
From: candidate@example.com
Subject: Full Stack Developer Application

MUHAMMAD AHMED KHAN
Karachi, Pakistan
ahmed.khan.dev@gmail.com
+92 312 3456789

EXPERIENCE
Junior Full Stack Developer
TechNova Solutions (2024-Present)
- Developed web apps with React.js and Node.js
- Built REST APIs...

EDUCATION
Bachelor of Science in Computer Science
University of Karachi (2023)

SKILLS
JavaScript, TypeScript, React.js, Next.js, Node.js, MongoDB
```

**Automation:**
1. Detects job application
2. **No attachment** → Uses email body text
3. Parses resume from text
4. Score: 75/100 (Grade: B+)
5. Creates rejection email approval (score < 80)

---

## Example: Email with Google Docs Link

**Email received:**
```
From: candidate@example.com
Subject: Developer Position

Hi,

Please find my resume here:
https://docs.google.com/document/d/ABC123/edit

Thanks,
Jane Smith
```

**Automation:**
1. Detects job application
2. **Finds Google Docs URL** in email body
3. **Fetches** document content via Google API
4. Parses resume from fetched content
5. Scores candidate
6. Creates approval file

---

## Scoring System

### Score Breakdown (100 points total)

| Category | Points | Criteria |
|----------|--------|----------|
| **Contact Info** | 10 | Email (4) + Phone (3) + LinkedIn (2) + GitHub (1) |
| **Experience** | 40 | 10+ yrs (40) | 7+ yrs (35) | 5+ yrs (30) | 3+ yrs (25) | 1+ yrs (15) |
| **Education** | 20 | PhD (20) | Master (17) | Bachelor (14) | Other (10) |
| **Skills** | 30 | 25+ skills (25) | 20+ (22) | 15+ (18) | 10+ (14) + Soft skills bonus (5) |

### Grade Scale

| Score | Grade | Action |
|-------|-------|--------|
| 90-100 | A+ | **Auto-Interview** |
| 80-89 | A | **Auto-Interview** |
| 70-79 | B+ | Manual Review |
| 60-69 | B | Manual Review |
| 50-59 | C | Manual Review |
| < 50 | D | **Auto-Reject** |

---

## Google Sheets Integration

### Candidate Tracker Columns

| Column | Description |
|--------|-------------|
| Candidate ID | Auto-generated (CAND-YYYYMMDDHHMMSS) |
| Name | Extracted from resume |
| Email | Extracted from resume |
| Phone | Extracted from resume |
| Location | City detected |
| Position Applied | From email subject |
| Total Experience | Years extracted |
| Current Role | Latest position |
| Skills | Top 10 skills (comma-separated) |
| Education | Degrees (comma-separated) |
| Score | 0-100 |
| Grade | A+ to D |
| Recommendation | Interview/Review/Reject |
| Status | New/Interview Scheduled/Rejected |
| Resume File | Path to saved resume |
| Google Doc Link | Profile document URL |
| Interview Date | If scheduled |
| Interview Link | Google Meet URL |
| Created Date | Timestamp |

### Access Tracker

```
https://docs.google.com/spreadsheets/d/[ID]/edit
```
(Spreadsheet created automatically on first candidate)

---

## Google Docs Integration

### Profile Document Sections

1. **Personal Information**
   - Name, Email, Phone, Location
   - LinkedIn, GitHub URLs

2. **Position & Scoring**
   - Position Applied
   - Total Score / 100 (Grade)
   - Recommendation
   - Score Breakdown

3. **Professional Experience**
   - Total Years
   - Current Role
   - Previous Positions

4. **Education**
   - Degrees
   - Universities
   - Graduation Year

5. **Skills**
   - Technical Skills (categorized)
   - Soft Skills
   - Certifications
   - Languages

6. **Interview Notes**
   - Date, Time, Interviewers
   - Format (Video/Phone/In-Person)
   - Notes section

7. **Evaluation**
   - Technical Skills rating
   - Communication rating
   - Culture Fit rating
   - Overall Recommendation

---

## Google Calendar Integration

### Interview Scheduling (Score >= 80)

**Automatic:**
1. Finds next available slot (business hours)
2. Creates calendar event
3. Generates Google Meet link
4. Adds candidate email as attendee
5. Includes interview details in description

**Interview Email Template:**
```markdown
Dear [Candidate Name],

Thank you for your interest in the [Position] position.

We were impressed by your background and would like to invite you for an interview.

─────────────────────────────
INTERVIEW DETAILS
─────────────────────────────
Position: [Position]
Format: Video Call (Google Meet)
Duration: 45 minutes

📅 Date: [Date/Time]
🔗 Meeting Link: [Google Meet URL]
─────────────────────────────

Please confirm your availability by replying to this email.

Best regards,
Talent Acquisition Team
```

---

## Approval File Formats

### Interview Invitation Approval

```markdown
---
type: email_approval
action: send_email
to: candidate@example.com
subject: Interview Invitation - Full Stack Developer
candidate_id: CAND-20260327120000
candidate_name: John Doe
position: Full Stack Developer
score: 85
grade: A
---

# Interview Invitation Approval

## Candidate Details
- **Name:** John Doe
- **Email:** candidate@example.com
- **Position:** Full Stack Developer
- **Score:** 85/100 (Grade: A)

## Interview Details
- **Date/Time:** 2026-03-28 10:00:00
- **Format:** Video Call (Google Meet)
- **Duration:** 45 minutes
- **Meet Link:** https://meet.google.com/abc-defg-hij

## Email Body

Dear John Doe,

Thank you for your interest in the Full Stack Developer position...

[Full email content]

---

## Instructions
1. **Review** the interview details above
2. **Edit** if needed (date/time, message)
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
```

### Rejection Email Approval

```markdown
---
type: email_approval
action: send_email
to: candidate@example.com
subject: Re: Full Stack Developer Application
candidate_id: CAND-20260327120000
candidate_name: Jane Smith
score: 65
---

# Rejection Email Approval

## Candidate Details
- **Name:** Jane Smith
- **Email:** candidate@example.com
- **Position:** Full Stack Developer
- **Score:** 65/100

## Email Body

Dear Jane Smith,

Thank you for your interest in the Full Stack Developer position...

[Polite rejection message]

---

## Instructions
1. **Review** the rejection email above
2. **Edit** if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
```

---

## Folder Structure

```
AI_Employee_Vault/
├── Needs Action/
│   └── HR_APPLICATION_*.md      # New job applications
├── Pending Approval/
│   ├── APPROVAL_interview_*.md  # Interview invitations
│   └── APPROVAL_rejection_*.md  # Rejection emails
├── Approved/
│   └── [Move files here to send]
├── Done/
│   └── EXECUTED_*.md            # Sent emails log
├── Resumes/
│   ├── RESUME_*.pdf             # Saved PDF resumes
│   ├── RESUME_*.docx            # Saved Word resumes
│   └── GOOGLE_DOCS_*.txt        # Fetched Google Docs
└── services/
    ├── hr_resume_parser.py      # Resume parsing
    ├── hr_ocr_parser.py         # OCR for images
    ├── hr_robust_ocr_parser.py  # Advanced OCR
    ├── hr_candidate_tracker.py  # Google Sheets
    ├── hr_resume_doc_creator.py # Google Docs
    └── hr_interview_scheduler.py# Google Calendar
```

---

## Troubleshooting

### Resume Not Parsed Correctly

**Problem:** Name shows "Unknown" or skills missing

**Solutions:**
1. Check OCR extracted text (look for garbled characters)
2. Verify Poppler installed for PDF OCR
3. Check Tesseract path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
4. Try text-based PDF instead of scanned

### Score Too Low

**Problem:** Qualified candidate scored < 60

**Solutions:**
1. Check if skills were extracted (500+ skill database)
2. Verify experience years detected (check date formats)
3. Ensure education section parsed correctly
4. Manual override: Edit approval file score before sending

### Google Sheets Not Updating

**Problem:** "Failed to log to tracker" error

**Solutions:**
1. Verify `token.json` has Sheets permission
2. Check internet connection
3. Re-run: `python generate_token.py`
4. Check spreadsheet not deleted

### Interview Not Scheduled

**Problem:** Score >= 80 but no interview

**Solutions:**
1. Check Calendar API enabled in Google Cloud
2. Verify `token.json` has Calendar permission
3. Check business hours configuration
4. Review orchestrator logs for errors

### OCR Fails on Scanned PDF

**Problem:** "Poppler not installed" error

**Solutions:**
1. Download Poppler: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to: `C:\Program Files\poppler`
3. Add to PATH: `C:\Program Files\poppler\Library\bin`
4. Restart Python script

---

## Best Practices

### For Candidates (Resume Format)

**Recommended:**
- ✅ Text-based PDF (export from Word)
- ✅ Word document (.docx)
- ✅ Paste resume in email body
- ✅ Google Docs link (with view access)

**Avoid:**
- ❌ Scanned/image PDF (OCR may miss details)
- ❌ Image files (PNG/JPG of resume)
- ❌ Password-protected PDFs

### For HR Teams

**Review Process:**
1. Check parsed data accuracy (name, email, phone)
2. Verify skill extraction (should find 20-50+ skills)
3. Review score breakdown (adjust if needed)
4. Edit interview email before approving
5. Personalize rejection emails

**Score Thresholds:**
- **80+:** Auto-interview (highly qualified)
- **60-79:** Manual review (potential fit)
- **< 60:** Auto-reject (not qualified)

---

## Testing

### Test with Sample Resume

1. **Create test email:**
   - To: Your monitored Gmail
   - Subject: "Apply for Full Stack Developer"
   - Body: Paste sample resume text
   - OR attach: Sample PDF resume

2. **Wait 2 minutes** (Gmail watcher cycle)

3. **Check logs:**
   ```
   💼 Detected job application (confidence: 70%)
   📄 Parsing resume from email body...
   ✅ Resume parsed successfully
   Name: [Your Name]
   Score: XX/100 (Grade: X)
   ```

4. **Verify:**
   - Google Sheets: New row added
   - Google Docs: Profile created
   - Approval file: In `Pending Approval/`

---

## Advanced Configuration

### Custom Score Weights

Edit `services/hr_robust_ocr_parser.py`:

```python
# Adjust point values
if years >= 10: exp = 40  # Change 40 to different value
elif years >= 7: exp = 35  # Adjust as needed
```

### Custom Skills Database

Add skills to `services/hr_robust_ocr_parser.py`:

```python
self.all_skills = {
    'your-skill': ['variation1', 'variation2', 'variation3'],
    # Add more...
}
```

### Business Hours for Interviews

Edit `services/hr_interview_scheduler.py`:

```python
# Change interview slots
self.interview_slots = [
    "10:00", "11:00",  # Morning
    "14:00", "15:00", "16:00"  # Afternoon
]
```

---

## API Reference

### Resume Parser

```python
from services.hr_resume_parser import ResumeParser

parser = ResumeParser()
result = parser.parse_file(Path("resume.pdf"))

# Result structure:
{
    'success': True,
    'candidate': {'name': '...', 'email': '...', ...},
    'experience': {'total_years': 5, ...},
    'education': {'degrees': [...], ...},
    'skills': {'technical': [...], 'soft_skills': [...]},
    'score': {'total': 85, 'breakdown': {...}, 'grade': 'A'},
    'recommendation': {'action': 'interview', ...}
}
```

### Candidate Tracker

```python
from services.hr_candidate_tracker import CandidateTracker

tracker = CandidateTracker()
tracker.initialize()

result = tracker.add_candidate(candidate_data)
# Returns: {'success': True, 'candidate_id': 'CAND-...'}

tracker.schedule_interview(candidate_id, datetime, meet_link)
```

### Interview Scheduler

```python
from services.hr_interview_scheduler import InterviewScheduler

scheduler = InterviewScheduler()
scheduler.initialize()

result = scheduler.schedule_interview(candidate_data)
# Returns: {
#     'success': True,
#     'interview_datetime': '2026-03-28 10:00:00',
#     'meet_link': 'https://meet.google.com/...'
# }
```

---

## Related Skills

- [`email-automation`](../email-automation/SKILL.md) - General email processing
- [`odoo`](../odoo/SKILL.md) - CRM integration for leads
- [`whatsapp-automation`](../whatsapp-automation/SKILL.md) - WhatsApp messaging

---

## Support

**Common Issues:**
- Resume parsing errors → Check OCR setup
- Google API errors → Re-run `generate_token.py`
- Score calculation → Review scoring weights
- Interview scheduling → Check Calendar API

**Logs Location:**
```
Logs/orchestrator.log
Logs/gmail_watcher.log
```
