"""
AI Client module
Handles integration with Qwen via Ollama CLI (like Claude Code CLI)
"""

import subprocess
import json
from typing import Optional, Dict, Any
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import QWEN_MODEL
from engine.logger import logger


class AIClient:
    def __init__(self, model: Optional[str] = None):
        """
        Initialize Qwen CLI client

        Args:
            model: Ollama model name (default from config)
        """
        self.model = model or QWEN_MODEL

        # Check if Ollama is available
        if not self._check_ollama():
            raise RuntimeError("Ollama is not installed or not running. Install from https://ollama.ai")

        logger.info(f"✅ Qwen CLI initialized with model: {self.model}")

    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _run_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Run Ollama CLI command

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Model response
        """
        try:
            # Build the full prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt

            logger.info(f"🤖 Qwen is processing...")

            # Run ollama command
            result = subprocess.run(
                ['ollama', 'run', self.model, full_prompt],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr or "Unknown error"
                logger.error(f"Ollama error: {error_msg}")
                return f"Error: {error_msg}"

            response = result.stdout.strip()
            logger.info("✅ Qwen completed processing")
            return response

        except subprocess.TimeoutExpired:
            logger.error("Ollama command timed out")
            return "Error: Request timed out"
        except FileNotFoundError:
            logger.error("Ollama command not found")
            return "Error: Ollama not installed"
        except Exception as e:
            logger.error(f"Error running Ollama: {e}")
            return f"Error: {str(e)}"

    def analyze_task(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Analyze a task and provide response

        Args:
            content: Task content to analyze
            context: Additional context

        Returns:
            AI analysis/response
        """
        system_prompt = """You are an AI assistant helping to process tasks.
Analyze the task and provide:
1. Summary of what needs to be done
2. Recommended actions
3. Any concerns or questions

Be concise and actionable."""

        user_prompt = f"Task Content:\n{content}"

        if context:
            user_prompt += f"\n\nContext: {context}"

        logger.info("📋 Analyzing task...")
        result = self._run_ollama(user_prompt, system_prompt)
        return result

    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response for a given prompt

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            AI response
        """
        return self._run_ollama(prompt, system_prompt)

    def process_approval_task(self, task_content: str, approval_status: str) -> str:
        """
        Process a task after approval/rejection

        Args:
            task_content: Original task content
            approval_status: 'approved' or 'rejected'

        Returns:
            Processing result
        """
        if approval_status == 'approved':
            system_prompt = """You are executing an approved task.
Provide:
1. Confirmation of what was done
2. Results/outcomes
3. Next steps if any

Be specific and factual."""
        else:
            system_prompt = """This task was rejected.
Provide:
1. Acknowledgment of rejection
2. Suggested alternatives
3. What to do next"""

        user_prompt = f"Task: {task_content}\nStatus: {approval_status}"

        logger.info(f"⚙️ Processing {approval_status} task...")
        result = self._run_ollama(user_prompt, system_prompt)
        return result

    def check_if_needs_approval(self, task_content: str) -> tuple[bool, str]:
        """
        Determine if a task needs human approval

        Args:
            task_content: Task content to evaluate

        Returns:
            Tuple of (needs_approval: bool, reason: str)
        """
        system_prompt = """You are a safety checker. Determine if this task needs human approval.

Tasks that NEED approval:
- Financial transactions (payments, transfers)
- Sending emails to new contacts
- Deleting or modifying important data
- Posting on social media
- Any sensitive or risky actions

Tasks that DON'T need approval:
- Reading/analyzing information
- Creating summaries or reports
- Organizing files
- Simple data entry

Respond with ONLY:
NEEDS_APPROVAL: [reason]
or
NO_APPROVAL: [reason]"""

        user_prompt = f"Task: {task_content}"

        logger.info("🔍 Checking if task needs approval...")
        result = self._run_ollama(user_prompt, system_prompt).strip()

        if "NEEDS_APPROVAL:" in result:
            reason = result.split("NEEDS_APPROVAL:", 1)[1].strip()
            logger.info(f"⚠️ Task needs approval: {reason}")
            return True, reason
        else:
            reason = result.split("NO_APPROVAL:", 1)[1].strip() if "NO_APPROVAL:" in result else "Safe to process"
            logger.info("✅ Task is safe to auto-process")
            return False, reason
