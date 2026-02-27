# AI Employee Vault Engine

Autonomous AI agent system for processing tasks from multiple sources.

## Architecture

```
engine/
├── logger.py              # Centralized logging
├── ai_client.py          # AI API integration (Claude/OpenAI)
├── processor.py          # Task processing logic
├── reasoning_loop.py     # Multi-step reasoning
├── approval_manager.py   # Human-in-the-loop approvals
├── scheduler.py          # Periodic task execution
├── watcher_file.py       # File system monitoring
├── watcher_gmail.py      # Gmail integration
├── watcher_whatsapp.py   # WhatsApp integration
└── watcher_linkedin.py   # LinkedIn integration
```

## Features

- **Multi-Source Input**: Monitor files, Gmail, WhatsApp, LinkedIn
- **AI Processing**: Automated task analysis using Claude/OpenAI
- **Approval System**: Human oversight for sensitive tasks
- **Scheduling**: Periodic task execution
- **Reasoning Loop**: Multi-step problem solving

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:

```env
ANTHROPIC_API_KEY=your_api_key_here
# or
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Run the engine

```bash
python main.py
```

### Process tasks manually

```bash
python process_tasks.py
```

## Components

### File Watcher
Monitors the `Inbox` folder for new files and creates tasks automatically.

### Task Processor
Analyzes tasks using AI and generates responses.

### Approval Manager
Flags sensitive tasks for human review before execution.

### Scheduler
Runs periodic tasks like checking for new emails or processing queued items.

### Reasoning Loop
Implements multi-step reasoning for complex tasks.

## Workflow

1. **Input**: File dropped in Inbox / Email received / Message received
2. **Task Creation**: System creates task file in Needs_Action
3. **Analysis**: AI analyzes task content
4. **Approval** (if needed): Human reviews and approves
5. **Processing**: Task is executed
6. **Completion**: Task moved to Done, Dashboard updated

## Integration

### Gmail
Configure OAuth credentials and enable Gmail API.

### WhatsApp
Use Twilio API or WhatsApp Business API.

### LinkedIn
Use unofficial LinkedIn API (requires credentials).

## Development

All modules are designed to be modular and extensible. Add new watchers or processors by following the existing patterns.

## Security

- API keys stored in environment variables
- Sensitive tasks require approval
- All actions logged for audit trail
