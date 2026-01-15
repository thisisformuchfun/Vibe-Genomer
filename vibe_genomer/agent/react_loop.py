"""
ReAct (Reasoning + Acting) loop implementation.

This implements the ReAct pattern where the agent alternates between
reasoning about what to do and acting on those decisions.
"""

from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import BaseLLMProvider
    from ..utils import Config, VibeLogger
    from .planner import WorkflowPlan
    from .executor import ToolExecutor, ExecutionResult
    from .state_machine import AgentState


class ReActLoop:
    """
    ReAct loop for agentic execution.

    The agent follows this pattern:
    1. Thought: Reason about the current state and next action
    2. Action: Execute a tool or make a decision
    3. Observation: Observe the result
    4. Repeat until task is complete
    """

    REACT_PROMPT = """You are an expert bioinformatics agent executing a genomic analysis workflow.

Current Plan:
{plan_summary}

Completed Steps: {completed_steps}

Current Step: {current_step}

Previous Results:
{previous_results}

Your task:
1. THOUGHT: Reason about what needs to be done for the current step
2. ACTION: Specify how to execute this step
3. Wait for OBSERVATION of the result
4. If successful, move to next step. If failed, reason about how to fix it.

Provide your response in this format:

THOUGHT: [Your reasoning about the current step]
ACTION: [What action to take]

Be specific and biological. Consider:
- Are the genomic coordinates valid?
- Is the file format correct?
- What biological meaning do the results have?
"""

    def __init__(
        self,
        provider: "BaseLLMProvider",
        executor: "ToolExecutor",
        config: "Config",
        logger: "VibeLogger",
    ):
        """
        Initialize ReAct loop.

        Args:
            provider: LLM provider
            executor: Tool executor
            config: Configuration
            logger: Logger
        """
        self.provider = provider
        self.executor = executor
        self.config = config
        self.logger = logger

    def execute_plan(
        self,
        plan: "WorkflowPlan",
        state: "AgentState",
    ) -> str:
        """
        Execute a workflow plan using the ReAct pattern.

        Args:
            plan: Workflow plan to execute
            state: Current agent state

        Returns:
            Final result as formatted text
        """
        self.logger.info(f"Executing plan with {len(plan.steps)} steps")

        completed_steps: List[str] = []
        results: Dict[str, Any] = {}
        max_iterations = 50  # Safety limit
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Get next step
            next_step = plan.get_next_step(completed_steps)

            if next_step is None:
                # Plan complete!
                self.logger.success("Plan execution complete")
                return self._format_final_result(plan, results)

            self.logger.info(f"Executing step {len(completed_steps) + 1}/{len(plan.steps)}: {next_step.description}")

            # Execute step
            result = self._execute_step_with_reasoning(
                step=next_step,
                plan=plan,
                completed_steps=completed_steps,
                results=results,
            )

            if result.success:
                # Step succeeded
                completed_steps.append(next_step.step_id)

                # Store result
                if next_step.output_key:
                    results[next_step.output_key] = result.output

                self.logger.success(f"Step {next_step.step_id} completed")

            else:
                # Step failed - try to recover
                self.logger.warning(f"Step {next_step.step_id} failed: {result.error}")

                # For now, we'll just fail. In the future, we can add retry logic
                return self._format_error_result(next_step, result.error, results)

        # Hit iteration limit
        self.logger.error(f"Reached maximum iterations ({max_iterations})")
        return self._format_incomplete_result(plan, completed_steps, results)

    def _execute_step_with_reasoning(
        self,
        step: "WorkflowStep",
        plan: "WorkflowPlan",
        completed_steps: List[str],
        results: Dict[str, Any],
    ) -> "ExecutionResult":
        """
        Execute a step with ReAct-style reasoning.

        Args:
            step: Step to execute
            plan: Full plan
            completed_steps: List of completed step IDs
            results: Results so far

        Returns:
            Execution result
        """
        from ..models import Message, MessageRole

        # Build reasoning prompt
        prompt = self._build_react_prompt(
            step=step,
            plan=plan,
            completed_steps=completed_steps,
            results=results,
        )

        # Get reasoning from LLM
        messages = [Message(MessageRole.USER, prompt)]

        try:
            response = self.provider.complete(messages)
            reasoning = response.content

            self.logger.debug(f"Agent reasoning:\n{reasoning}")

            # Extract thought and action (for logging/debugging)
            self._parse_reasoning(reasoning)

        except Exception as e:
            self.logger.warning(f"Reasoning failed: {e}. Proceeding with execution anyway.")

        # Execute the step
        result = self.executor.execute_step(step, results)

        return result

    def _build_react_prompt(
        self,
        step: "WorkflowStep",
        plan: "WorkflowPlan",
        completed_steps: List[str],
        results: Dict[str, Any],
    ) -> str:
        """Build the ReAct prompt for current state."""
        plan_summary = "\n".join(
            f"{i+1}. {s.description}" for i, s in enumerate(plan.steps)
        )

        completed_str = ", ".join(completed_steps) if completed_steps else "None"

        current_step_str = f"{step.step_id}: {step.description}"

        # Format previous results
        results_str = ""
        if results:
            results_str = "\n".join(
                f"- {key}: {str(value)[:200]}..." if len(str(value)) > 200 else f"- {key}: {value}"
                for key, value in results.items()
            )
        else:
            results_str = "No previous results"

        return self.REACT_PROMPT.format(
            plan_summary=plan_summary,
            completed_steps=completed_str,
            current_step=current_step_str,
            previous_results=results_str,
        )

    def _parse_reasoning(self, reasoning: str) -> Dict[str, str]:
        """
        Parse THOUGHT and ACTION from reasoning text.

        Args:
            reasoning: Raw reasoning text

        Returns:
            Dictionary with thought and action
        """
        parsed = {"thought": "", "action": ""}

        lines = reasoning.split("\n")
        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("THOUGHT:"):
                current_section = "thought"
                parsed["thought"] = line.replace("THOUGHT:", "").strip()
            elif line.startswith("ACTION:"):
                current_section = "action"
                parsed["action"] = line.replace("ACTION:", "").strip()
            elif current_section and line:
                parsed[current_section] += " " + line

        return parsed

    def _format_final_result(
        self,
        plan: "WorkflowPlan",
        results: Dict[str, Any],
    ) -> str:
        """Format the final successful result."""
        output = f"# Analysis Complete\n\n"
        output += f"Query: {plan.query}\n\n"

        output += "## Results\n\n"

        for key, value in results.items():
            output += f"### {key}\n"
            output += f"```\n{value}\n```\n\n"

        return output

    def _format_error_result(
        self,
        step: "WorkflowStep",
        error: str,
        results: Dict[str, Any],
    ) -> str:
        """Format an error result."""
        output = f"# Analysis Failed\n\n"
        output += f"Failed at step: {step.description}\n\n"
        output += f"Error: {error}\n\n"

        if results:
            output += "## Partial Results\n\n"
            for key, value in results.items():
                output += f"### {key}\n"
                output += f"```\n{value}\n```\n\n"

        return output

    def _format_incomplete_result(
        self,
        plan: "WorkflowPlan",
        completed_steps: List[str],
        results: Dict[str, Any],
    ) -> str:
        """Format an incomplete result (hit iteration limit)."""
        output = f"# Analysis Incomplete\n\n"
        output += f"Completed {len(completed_steps)}/{len(plan.steps)} steps\n\n"

        if results:
            output += "## Partial Results\n\n"
            for key, value in results.items():
                output += f"### {key}\n"
                output += f"```\n{value}\n```\n\n"

        return output
