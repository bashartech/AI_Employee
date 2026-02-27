# 🤖 AI Employee Vault - Qwen Automation

## Fully Automated Task Processing with Qwen AI

**Previous Issue**: Claude Code (CCR) free version doesn't have claude.exe for automation.

**Solution**: Use Qwen AI with folder-based automation - completely FREE and fully automatic!

---

## How It Works

```
📥 Needs Action → 🤖 Qwen Analyzes → ⏳ Pending Approval (if risky)
                                    ↓
                              👤 Human Reviews
                                    ↓
                              ✅ Approved → 🤖 Qwen Processes → ✔️ Done
```

**Automatic workflow:**
1. Drop task file in `Needs Action/`
2. Qwen automatically analyzes it
3. Safe tasks → processed immediately → `Done/`
4. Risky tasks → moved to `Pending Approval/`
5. You approve → Qwen processes → `Done/`

---

## Quick Start (5 minutes)

### Step 1: Install Ollama (FREE)
```bash
# Download from: https://ollama.ai
# Then install Qwen model:
ollama pull qwen2.5:latest
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Test Setup
```bash
python test_setup.py
```

### Step 4: Start Automation
```bash
python run_automation.py
```

**That's it!** The system is now watching for tasks and processing them automatically.

---

## Usage

### Create a Task

Create a file in `Needs Action/` folder:

**Example: `Needs Action/analyze_data.md`**
```markdown
# Analyze Sales Data

Review Q1-Q4 sales figures and identify trends:
- Q1: $50,000
- Q2: $65,000
- Q3: $70,000
- Q4: $85,000
```

**What happens:**
- Qwen analyzes it automatically
- Safe task → processed immediately → appears in `Done/`
- Results include AI analysis and insights

### Tasks Requiring Approval

**Example: `Needs Action/send_email.md`**
```markdown
# Send Client Email

Send email to client@example.com about project delay.
```

**What happens:**
- Qwen detects this needs approval (email sending)
- Moved to `Pending Approval/` with AI analysis
- You review and move to `Approved/` folder
- Qwen processes it → appears in `Done/`

---

## Folder Structure

```
AI_Employee_Vault/
├── Needs Action/       ← Drop new tasks here
├── Pending Approval/   ← Tasks waiting for your approval
├── Approved/           ← Move approved tasks here
├── Done/               ← Completed tasks appear here
└── Rejected/           ← Rejected tasks go here
```

---

## Commands

**Start automation:**
```bash
python run_automation.py
```

**View dashboard:**
```bash
python dashboard.py
```

**Test setup:**
```bash
python test_setup.py
```

---

## What Gets Auto-Approved vs Needs Approval

### Auto-Processed (Safe):
✅ Data analysis and summaries
✅ Reading and organizing information
✅ Creating reports
✅ Simple calculations
✅ File organization

### Requires Approval (Risky):
⚠️ Sending emails
⚠️ Financial transactions
⚠️ Deleting data
⚠️ Posting on social media
⚠️ Modifying sensitive information

---

## Features

✅ **Fully Automatic** - No manual triggering needed
✅ **FREE** - Uses local Qwen via Ollama
✅ **Smart Approval** - AI decides what needs human review
✅ **Real-time Processing** - Tasks processed as they arrive
✅ **Complete Audit Trail** - All tasks logged with timestamps
✅ **Dashboard** - Live view of task status

---

## Troubleshooting

### Qwen not responding
```bash
# Check Ollama is running
ollama list

# Restart Ollama if needed
ollama serve
```

### Tasks not being processed
- Ensure `run_automation.py` is running
- Check files are `.md` or `.txt` format
- Review console output for errors

### Connection errors
- Verify Ollama is running: `ollama list`
- Check `.env` file has correct `QWEN_BASE_URL`

---

## Configuration

Edit `.env` file to customize:

```bash
# Local Ollama (default - FREE)
QWEN_BASE_URL=http://localhost:11434/v1
QWEN_MODEL=qwen2.5:latest

# Or use Qwen Cloud API
# QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# QWEN_API_KEY=your-api-key
```

---

## Documentation

- `QWEN_SETUP.md` - Detailed setup guide
- `prompt.md` - System architecture
- `engine/README.md` - Technical documentation

---

## Comparison: CCR vs Qwen

| Feature | CCR Free | Qwen (This System) |
|---------|----------|-------------------|
| Cost | Free | Free |
| Automation | ❌ Manual trigger | ✅ Fully automatic |
| Approval Flow | ❌ Not built-in | ✅ Built-in |
| Setup | Complex | Simple |
| Dependencies | claude.exe needed | Just Ollama |

---

## Next Steps

1. **Test it now:**
   ```bash
   python test_setup.py
   python run_automation.py
   ```

2. **Create a test task** in `Needs Action/`

3. **Watch it get processed** automatically

4. **Check results** in `Done/` folder

---

**Ready to automate? Run `python test_setup.py` to begin!** 🚀
