"""
Reasoning Loop module
Implements multi-step reasoning and decision-making for complex tasks
"""

from typing import List, Dict, Any, Optional
from engine.logger import logger
from engine.ai_client import AIClient


class ReasoningLoop:
    def __init__(self, ai_client: Optional[AIClient] = None, max_iterations: int = 5):
        self.ai_client = ai_client or AIClient()
        self.max_iterations = max_iterations
        self.reasoning_history = []

        logger.info("Reasoning loop initialized")

    def reason(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute reasoning loop for a complex task

        Args:
            task: The task to reason about
            context: Additional context

        Returns:
            Reasoning result with steps and conclusion
        """
        logger.info(f"Starting reasoning loop for task: {task[:50]}...")

        self.reasoning_history = []
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            logger.debug(f"Reasoning iteration {iteration}/{self.max_iterations}")

            # Generate reasoning step
            step_result = self._reasoning_step(task, context, iteration)
            self.reasoning_history.append(step_result)

            # Check if reasoning is complete
            if step_result.get('complete', False):
                logger.info(f"Reasoning complete after {iteration} iteration(s)")
                break

        return self._compile_result()

    def _reasoning_step(self, task: str, context: Optional[Dict[str, Any]], iteration: int) -> Dict[str, Any]:
        """Execute a single reasoning step"""

        # Build prompt with history
        prompt = self._build_reasoning_prompt(task, context, iteration)

        # Get AI response
        response = self.ai_client.generate_response(
            prompt,
            system_prompt="You are a reasoning assistant. Break down complex tasks into steps."
        )

        # Parse response
        step_result = {
            'iteration': iteration,
            'thought': response,
            'complete': self._is_reasoning_complete(response)
        }

        return step_result

    def _build_reasoning_prompt(self, task: str, context: Optional[Dict[str, Any]], iteration: int) -> str:
        """Build prompt for reasoning step"""
        prompt = f"Task: {task}\n\n"

        if context:
            prompt += f"Context: {context}\n\n"

        if self.reasoning_history:
            prompt += "Previous reasoning steps:\n"
            for i, step in enumerate(self.reasoning_history, 1):
                prompt += f"{i}. {step['thought']}\n"
            prompt += "\n"

        prompt += f"Reasoning step {iteration}: What should we consider next?"

        return prompt

    def _is_reasoning_complete(self, response: str) -> bool:
        """Determine if reasoning is complete"""
        # Simple heuristic - check for completion indicators
        completion_keywords = ['complete', 'done', 'finished', 'conclusion', 'final']
        response_lower = response.lower()

        return any(keyword in response_lower for keyword in completion_keywords)

    def _compile_result(self) -> Dict[str, Any]:
        """Compile final reasoning result"""
        return {
            'steps': self.reasoning_history,
            'total_iterations': len(self.reasoning_history),
            'conclusion': self.reasoning_history[-1]['thought'] if self.reasoning_history else None
        }

    def explain_reasoning(self) -> str:
        """Generate human-readable explanation of reasoning process"""
        if not self.reasoning_history:
            return "No reasoning steps recorded."

        explanation = "## Reasoning Process\n\n"

        for i, step in enumerate(self.reasoning_history, 1):
            explanation += f"**Step {i}:**\n{step['thought']}\n\n"

        return explanation
