# HR Hiring Automation - Complete Guide

## 🎯 Overview

Automated hiring workflow from resume collection to interview scheduling with human approval.

```
Resume Email Received
     ↓
Auto-Extract Resume (PDF/DOC/TXT)
     ↓
Parse & Score Candidate (ATS-style)
     ↓
Score >= 80? ──NO──> Reject Email (Auto-send)
     │
    YES
     ↓
Create Interview Approval File
     ↓
Human Reviews in Dashboard
     ↓
Move to Approved/ Folder
     ↓
Auto-Send Interview Email with Google Meet Link
     ↓
Schedule Added to Calendar
```

---

## 📁 Folder Structure

```
AI_Employee_Vault/
├── services/
│   └── hr_resume_parser.py      # Resume parsing service
├── HR_Candidates/                # Candidate records
│   ├── Applied/                  # New applications
│   ├── Interview_Scheduled/      # Interviews booked
│   ├── Hired/                    # Successfully hired
│   └── Rejected/                 # Not selected
├── Resumes/                      # Uploaded resume files
└── Pending Approval/
    └── INTERVIEW_CandidateName_*.md  # Interview approvals
```

---

## 🚀 Features

### **1. Resume Parsing**
- ✅ Extracts: Name, Email, Phone, Location
- ✅ Skills: Technical + Soft Skills
- ✅ Experience: Years, Companies, Roles
- ✅ Education: Degrees, Universities
- ✅ Certifications & Languages

### **2. ATS-Style Scoring**
- **Contact Info:** 10 points
- **Experience:** 40 points (based on years)
- **Education:** 20 points (PhD > Masters > Bachelor)
- **Skills:** 30 points (technical + soft skills)
- **Total:** 100 points

### **3. Grading System**
| Score | Grade | Action |
|-------|-------|--------|
| 90-100 | A+ | High Priority Interview |
| 80-89 | A | Schedule Interview |
| 70-79 | B+ | Review for Interview |
| 60-69 | B | Consider |
| 50-59 | C | Keep on File |
| <50 | D | Reject |

### **4. Approval Workflow**
- **Score >= 80:** Auto-create interview approval
- **Human Review:** Check candidate details in dashboard
- **Approve:** Move to `Approved/` folder
- **Auto-Email:** Send interview invite with Google Meet link

---

## 📧 Email Templates

### **Template 1: Interview Invitation (Auto-Sent After Approval)**

```
Subject: Interview Invitation - [Position] at TechCorp Solutions

Dear [Candidate Name],

Thank you for your interest in the [Position] role at TechCorp Solutions.

We were impressed by your background and would like to invite you for an interview.

─────────────────────────────
INTERVIEW DETAILS
─────────────────────────────
Position: [Job Title]
Format: [Video Call / In-Person]
Duration: 45 minutes

📅 Date: [Date]
🕐 Time: [Time]
🔗 Meeting Link: [Google Meet URL]
─────────────────────────────

Please confirm your availability by replying to this email.

If you need to reschedule, please let us know at least 24 hours in advance.

We look forward to speaking with you!

Best regards,
[HR Manager Name]
Talent Acquisition Team
TechCorp Solutions

📧 careers@techcorp.com
📞 +1 (555) 123-4567
```

### **Template 2: Rejection Email (Auto-Sent for Low Scores)**

```
Subject: Application Update - [Position] at TechCorp Solutions

Dear [Candidate Name],

Thank you for giving us the opportunity to review your application for the [Position] role.

We received many strong applications and have decided to move forward with candidates whose experience more closely matches our current needs.

We will keep your resume on file and reach out if a suitable position opens up in the future.

We wish you the best in your job search.

Best regards,
Talent Acquisition Team
TechCorp Solutions
```

---

## 🔧 Setup Instructions

### **Step 1: Enable Google Calendar Integration**

Ensure Google Calendar API is enabled in your `.env`:

```bash
# Google Calendar
GOOGLE_CALENDAR_ID=primary
AUTO_SCHEDULE_INTERVIEWS=true
```

### **Step 2: Configure HR Settings**

Create `HR_Config.json`:

```json
{
  "interview_duration_minutes": 45,
  "interview_buffer_minutes": 15,
  "min_score_for_interview": 70,
  "auto_reject_below_score": 50,
  "interview_slots_per_day": 5,
  "interview_time_slots": [
    "10:00",
    "11:00",
    "14:00",
    "15:00",
    "16:00"
  ],
  "hr_email": "careers@techcorp.com",
  "hr_name": "HR Team"
}
```

### **Step 3: Add HR Email Monitoring**

Add to orchestrator to detect resume emails:

```python
# Detect resume emails
if 'resume' in subject.lower() or 'cv' in subject.lower() or 'application' in subject.lower():
    # Extract attachment
    # Parse resume
    # Score candidate
    # Create approval if score >= 70
```

---

## 📊 Workflow Examples

### **Example 1: High-Score Candidate (85/100)**

```
1. Email received: "Application for Software Engineer - John Doe"
   Attachment: john_doe_resume.pdf

2. Resume parsed:
   - Name: John Doe
   - Email: john@email.com
   - Experience: 5 years
   - Skills: Python, React, AWS
   - Score: 85/100 (Grade A)

3. Approval file created:
   Pending Approval/INTERVIEW_John_Doe_20260326_143022.md

4. Human reviews in dashboard:
   ✅ Views candidate score
   ✅ Checks parsed resume
   ✅ Selects interview time slot

5. Human moves file to Approved/

6. Auto-email sent:
   ✅ Interview invitation
   ✅ Google Meet link generated
   ✅ Calendar event created

7. Candidate record updated:
   HR_Candidates/Interview_Scheduled/John_Doe.md
```

### **Example 2: Low-Score Candidate (45/100)**

```
1. Email received: "Job Application - Jane Smith"
   Attachment: jane_smith_cv.pdf

2. Resume parsed:
   - Score: 45/100 (Grade D)

3. Auto-rejection:
   ✅ Rejection email sent automatically
   ✅ Candidate filed in HR_Candidates/Rejected/
   ✅ No human approval needed
```

---

## 🎯 Approval File Format

**File:** `Pending Approval/INTERVIEW_CandidateName_Timestamp.md`

```markdown
---
type: interview_approval
action: schedule_interview
candidate_name: John Doe
candidate_email: john@email.com
position: Senior Software Engineer
score: 85
grade: A
experience_years: 5
resume_file: Resumes/john_doe_resume.pdf
---

# Interview Scheduling Approval

## Candidate Information

| Field | Details |
|-------|---------|
| **Name** | John Doe |
| **Email** | john@email.com |
| **Phone** | +1 (555) 123-4567 |
| **Location** | New York |
| **LinkedIn** | linkedin.com/in/johndoe |

## Candidate Score

**Total Score:** 85/100 (Grade A)

### Score Breakdown
- Contact Info: 10/10 ✅
- Experience: 35/40 (5 years)
- Education: 15/20 (Bachelor's)
- Skills: 25/30 (8 technical, 3 soft)

## Experience Summary

**Current Role:** Senior Software Engineer at Tech Corp
**Previous:** Software Engineer at StartupXYZ

**Key Skills:**
- Python, Java, JavaScript
- React, Django, AWS
- Docker, Kubernetes

## Education

- Bachelor of Technology in Computer Science (2017)
- AWS Certified Solutions Architect
- Certified Scrum Master

## Recommendation

**Action:** Schedule Interview
**Priority:** High
**Message:** Excellent candidate - Strong technical background with leadership experience

---

## Interview Details (To Be Filled)

**Proposed Date:** _______________
**Proposed Time:** _______________
**Interviewer:** _______________
**Meeting Link:** [Will be generated]

---

## Instructions

1. **Review** candidate details above
2. **Select** interview date/time from available slots
3. **Approve:** Move to `Approved/` folder
   - Auto-generates Google Meet link
   - Sends interview invitation email
   - Creates calendar event
4. **Reject:** Move to `Rejected/` folder
   - Sends rejection email

---
*Generated by AI Employee Vault HR Automation*
```

---

## 📈 Analytics & Reporting

### **Daily HR Report**

```
HR Hiring Summary - March 26, 2026
═══════════════════════════════════

Applications Received: 15
Resumes Parsed: 15
Average Score: 68/100

Score Distribution:
  A (80-100):  3 candidates (20%)
  B (60-79):   7 candidates (47%)
  C (50-59):   3 candidates (20%)
  D (<50):     2 candidates (13%)

Actions Taken:
  ✅ Interviews Scheduled: 3
  ✅ Rejections Sent: 2
  ⏳ Pending Review: 10

Top Skills Found:
  1. Python (12 candidates)
  2. JavaScript (10 candidates)
  3. React (8 candidates)
  4. AWS (7 candidates)
  5. Docker (6 candidates)

Upcoming Interviews:
  - John Doe (Senior Engineer) - Mar 27, 10:00 AM
  - Jane Smith (Frontend Dev) - Mar 27, 2:00 PM
  - Bob Johnson (DevOps) - Mar 28, 11:00 AM
```

---

## 🔐 Privacy & Compliance

### **GDPR Compliance**
- ✅ Candidate data stored securely
- ✅ Auto-delete after 90 days if no action
- ✅ Option to export candidate data
- ✅ Privacy policy in rejection emails

### **Data Retention**
```
HR_Candidates/
├── Active/           # Current candidates
├── Hired/            # Successfully hired (keep 7 years)
├── Rejected/         # Not selected (delete after 90 days)
└── Archive/          # Older than 1 year
```

---

## 🧪 Testing

### **Test Resume (High Score)**

Send email with subject: `Application for Software Engineer - Test Candidate`

Attach resume with:
- 5+ years experience
- Bachelor's degree
- Python, React, AWS skills
- Email, phone, LinkedIn

**Expected Result:**
- Score: 80+
- Approval file created
- Interview scheduling required

### **Test Resume (Low Score)**

Send email with minimal resume:
- No experience
- No degree
- Few skills

**Expected Result:**
- Score: <50
- Auto-rejection email sent
- No approval needed

---

## 🎯 Next Steps

1. ✅ Resume Parser - DONE
2. ⏳ Create approval workflow - IN PROGRESS
3. ⏳ Add Google Calendar integration
4. ⏳ Create email templates
5. ⏳ Test complete workflow

---

**Ready to automate your hiring process!** 🚀
