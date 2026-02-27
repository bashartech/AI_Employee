"""
Ralph Wiggum Hook - Gold Tier Implementation
Automatically restarts Claude Code if task is not complete
Based on: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

How it works:
1. Claude Code processes a task
2. Claude tries to exit
3. Ralph hook checks: Is task file in Done/ or Pending Approval/?
4. YES → Allow exit (task complete)
5. NO → Block exit, restart Claude Code with previous output
6. Repeat until complete or max iterations
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Fix emoji encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

VAULT = Path(__file__).parent
NEEDS_ACTION = VAULT / "Needs Action"
PENDING_APPROVAL = VAULT / "Pending Approval"
APPROVED = VAULT / "Approved"
DONE = VAULT / "Done"


class RalphWiggumHook:
    """Ralph Wiggum auto-retry hook for Claude Code"""
    
    def __init__(self, max_iterations: int = 10):
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.previous_output = ""
        
    def run_with_retry(self, prompt: str, task_file: Path) -> bool:
        """
        Run Claude Code with Ralph Wiggum retry logic
        
        Returns True if task completed successfully
        """
        print(f"\n{'='*60}")
        print(f"🔄 RALPH WIGGUM LOOP - Starting")
        print(f"{'='*60}")
        print(f"Task: {task_file.name}")
        print(f"Max iterations: {self.max_iterations}")
        print()
        
        for iteration in range(1, self.max_iterations + 1):
            self.current_iteration = iteration
            print(f"\n{'='*60}")
            print(f"🔁 ITERATION {iteration}/{self.max_iterations}")
            print(f"{'='*60}")
            
            # Build enhanced prompt with previous output if retrying
            if iteration > 1:
                enhanced_prompt = self._build_retry_prompt(prompt, self.previous_output)
            else:
                enhanced_prompt = prompt
            
            # Run Claude Code
            success, output = self._run_claude(enhanced_prompt)
            
            # Save output for potential retry
            self.previous_output = output
            
            # Check if task is complete
            if self._check_task_complete(task_file):
                print(f"\n✅ Task completed successfully on iteration {iteration}")
                print(f"{'='*60}")
                return True
            
            # Check if we should retry
            if self._should_retry(output):
                print(f"\n⚠️  Task not complete, retrying...")
                time.sleep(2)  # Brief pause before retry
                continue
            else:
                print(f"\n❌ Task failed or stuck, stopping retry")
                print(f"{'='*60}")
                return False
        
        print(f"\n❌ Max iterations ({self.max_iterations}) reached")
        print(f"{'='*60}")
        return False
    
    def _build_retry_prompt(self, original_prompt: str, previous_output: str) -> str:
        """Build prompt that includes previous attempt output"""
        
        retry_prompt = f"""
{original_prompt}

---

**PREVIOUS ATTEMPT OUTPUT:**

{previous_output}

---

**INSTRUCTIONS:**

Review your previous attempt above. The task is NOT complete yet.

Continue from where you left off. Do NOT repeat what you already did.

Check:
1. Did you create the approval file in Pending Approval/ folder?
2. Did you follow the skill file format exactly?
3. Did you move the task file to appropriate folder?

If the task is still not complete, try again with a different approach.
"""
        
        return retry_prompt
    
    def _run_claude(self, prompt: str) -> tuple[bool, str]:
        """Run Claude Code and return success status + output"""

        try:
            # On Windows, use shell=True and command string for .cmd files
            shell = sys.platform == 'win32'
            
            # For long prompts, write to temp file and pipe to claude
            # Windows cmd.exe has ~8191 character limit
            MAX_CMD_LENGTH = 7000  # Safe limit
            temp_file = None
            
            if shell and len(prompt) > MAX_CMD_LENGTH:
                # Write prompt to temp file and use PowerShell to pipe it
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
                temp_file.write(prompt)
                temp_file.close()
                # Use PowerShell to read file and pipe to claude
                cmd = f'powershell -Command "Get-Content -Raw \'{temp_file.name}\' | claude -p"'
            elif shell:
                # On Windows with shell=True, use command string with escaped quotes
                escaped_prompt = prompt.replace('"', '\\"').replace('\n', ' ')
                cmd = f'claude -p "{escaped_prompt}"'
            else:
                # On Unix, use list format
                cmd = ['claude', '-p', prompt]

            print(f"  🤖 Running Claude Code...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                shell=shell,
                cwd=str(VAULT)
            )

            output = result.stdout + result.stderr

            if result.returncode == 0:
                print(f"  ✅ Claude Code completed")
                return True, output
            else:
                print(f"  ❌ Claude Code failed with code {result.returncode}")
                print(f"  📄 Output: {output[:500]}..." if len(output) > 500 else f"  📄 Output: {output}")
                return False, output

        except FileNotFoundError as e:
            # On Windows, try with full path to claude.cmd
            if sys.platform == 'win32':
                import shutil
                claude_path = shutil.which('claude')
                if claude_path:
                    print(f"  ⚠️  'claude' not found in PATH, trying full path: {claude_path}")
                    try:
                        if len(prompt) > MAX_CMD_LENGTH:
                            import tempfile
                            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
                            temp_file.write(prompt)
                            temp_file.close()
                            cmd = f'powershell -Command "Get-Content -Raw \'{temp_file.name}\' | \'{claude_path}\' -p"'
                        else:
                            escaped_prompt = prompt.replace('"', '\\"').replace('\n', ' ')
                            cmd = f'"{claude_path}" -p "{escaped_prompt}"'
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=300,
                            encoding='utf-8',
                            shell=True,
                            cwd=str(VAULT)
                        )
                        output = result.stdout + result.stderr
                        if result.returncode == 0:
                            print(f"  ✅ Claude Code completed (via full path)")
                            return True, output
                        else:
                            print(f"  ❌ Claude Code failed with code {result.returncode}")
                            return False, output
                    except Exception as full_path_error:
                        print(f"  ❌ Full path also failed: {full_path_error}")
                        return False, str(full_path_error)

            print(f"  ❌ Claude command not found. Make sure Claude Code is installed:")
            print(f"     npm install -g @anthropic-ai/claude-code")
            return False, f"FileNotFoundError: {e}"
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  Claude Code timed out (5 min limit)")
            return False, "Timeout expired"
        except Exception as e:
            print(f"  ❌ Error running Claude Code: {e}")
            return False, str(e)
        finally:
            # Clean up temp file if created
            if temp_file:
                try:
                    import os
                    os.unlink(temp_file.name)
                except:
                    pass
    
    def _check_task_complete(self, task_file: Path) -> bool:
        """
        Check if task is complete
        
        Task is complete if:
        1. File moved to Done/ folder, OR
        2. Approval file created in Pending Approval/ folder
        """
        
        # Check if original file moved to Done
        done_file = DONE / task_file.name
        if done_file.exists():
            print(f"  ✅ Task file moved to Done/: {done_file.name}")
            return True
        
        # Check if original file moved to Rejected
        rejected_file = VAULT / "Rejected" / task_file.name
        if rejected_file.exists():
            print(f"  ✅ Task file moved to Rejected/: {rejected_file.name}")
            return True
        
        # Check if approval file was created (for tasks requiring approval)
        approval_files = list(PENDING_APPROVAL.glob("APPROVAL_*.md"))
        if approval_files:
            # Check if any approval file was created in last 2 minutes
            for af in approval_files:
                file_age = time.time() - af.stat().st_mtime
                if file_age < 120:  # Created in last 2 minutes
                    print(f"  ✅ Approval file created: {af.name}")
                    return True
        
        # Check if file still in Needs Action (not processed yet)
        if task_file.exists():
            print(f"  ⚠️  Task file still in Needs Action/: {task_file.name}")
            return False
        
        print(f"  ⚠️  Task status unknown")
        return False
    
    def _should_retry(self, output: str) -> bool:
        """
        Determine if we should retry based on output
        
        Retry if:
        - Output contains errors
        - Output suggests incomplete work
        - No approval file mentioned
        """
        
        output_lower = output.lower()
        
        # Don't retry if these are present (indicates fundamental failure)
        fatal_errors = [
            "authentication failed",
            "permission denied",
            "not found",
            "invalid command",
            "claude: command not found"
        ]
        
        for error in fatal_errors:
            if error in output_lower:
                print(f"  ❌ Fatal error detected: {error}")
                return False
        
        # Retry if task seems incomplete
        incomplete_indicators = [
            "still need to",
            "remaining steps",
            "continue with",
            "next i need to",
            "i should also",
        ]
        
        for indicator in incomplete_indicators:
            if indicator in output_lower:
                print(f"  ⚠️  Task appears incomplete: {indicator}")
                return True
        
        # Default: retry if we got some output (means Claude is working)
        if len(output) > 100:
            print(f"  ⚠️  Got output, assuming work in progress")
            return True
        
        return False


def ralph_loop(prompt: str, task_file: Path, max_iterations: int = 10) -> bool:
    """
    Convenience function to run Ralph Wiggum loop
    
    Usage:
        success = ralph_loop("Process this email", Path("Needs Action/email.md"))
    """
    
    ralph = RalphWiggumHook(max_iterations=max_iterations)
    return ralph.run_with_retry(prompt, task_file)


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("RALPH WIGGUM HOOK - Test Mode")
    print("="*60)
    print()
    print("This is a library module, not meant to be run directly.")
    print()
    print("Usage in your code:")
    print()
    print("  from ralph_wiggum_hook import ralph_loop")
    print()
    print("  success = ralph_loop(")
    print("      prompt='Process this task...',")
    print("      task_file=Path('Needs Action/task.md'),")
    print("      max_iterations=10")
    print("  )")
    print()
    print("  if success:")
    print("      print('Task completed!')")
    print("  else:")
    print("      print('Task failed after max iterations')")
    print()
