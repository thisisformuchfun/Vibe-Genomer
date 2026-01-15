"""
Core Genomic Agent implementation.

This is the main "brain" that orchestrates genomic analysis workflows.
"""

from typing import Optional, Dict, Any, List, TYPE_CHECKING

from .planner import WorkflowPlanner
from .executor import ToolExecutor
from .react_loop import ReActLoop
from .state_machine import AgentState, StateManager

if TYPE_CHECKING:
    from ..models import BaseLLMProvider
    from ..utils import Config, VibeLogger


class GenomicAgent:
    """
    Main genomic agent that translates natural language into
    executable bioinformatics workflows.

    This agent:
    1. Understands biological context
    2. Plans multi-step workflows
    3. Executes tools safely
    4. Validates results
    5. Self-corrects on errors
    """

    def __init__(
        self,
        provider: "BaseLLMProvider",
        config: "Config",
        logger: "VibeLogger",
    ):
        """
        Initialize the genomic agent.

        Args:
            provider: LLM provider for reasoning
            config: Application configuration
            logger: Logger instance
        """
        self.provider = provider
        self.config = config
        self.logger = logger

        # Initialize components
        self.planner = WorkflowPlanner(provider, config, logger)
        self.executor = ToolExecutor(config, logger)
        self.react_loop = ReActLoop(provider, self.executor, config, logger)
        self.state_manager = StateManager(logger)

        self.logger.debug("GenomicAgent initialized")

    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute a genomic analysis query.

        Args:
            query: Natural language query
            context: Optional context (file paths, previous results, etc.)

        Returns:
            Analysis result as formatted text

        This is the main entry point that:
        1. Parses the query
        2. Plans the workflow
        3. Executes each step
        4. Returns formatted results
        """
        self.logger.info(f"Executing query: {query}")

        try:
            # Update state with new query
            self.state_manager.add_user_message(query)

            if context:
                self.state_manager.update_context(context)

            # Parse and plan
            plan = self._create_plan(query)
            self.logger.info(f"Created plan with {len(plan.steps)} steps")

            # Execute plan using ReAct loop
            result = self.react_loop.execute_plan(
                plan=plan,
                state=self.state_manager.get_state(),
            )

            # Update state with result
            self.state_manager.add_assistant_message(result)

            return result

        except Exception as e:
            self.logger.exception(e, "Agent execution failed")
            error_msg = f"Analysis failed: {str(e)}"
            self.state_manager.add_error(str(e))
            return error_msg

    def _create_plan(self, query: str) -> "WorkflowPlan":
        """
        Create an execution plan for the query.

        Args:
            query: User query

        Returns:
            Workflow plan
        """
        from .planner import WorkflowPlan

        # Get current state for context
        state = self.state_manager.get_state()

        # Use planner to create workflow
        plan = self.planner.plan(query, state)

        return plan

    def reset(self):
        """Reset the agent state (clear conversation history)."""
        self.logger.info("Resetting agent state")
        self.state_manager.reset()

    def get_state(self) -> AgentState:
        """Get the current agent state."""
        return self.state_manager.get_state()

    def add_context(self, key: str, value: Any):
        """
        Add context to the agent state.

        Args:
            key: Context key (e.g., "working_dir", "reference_genome")
            value: Context value
        """
        self.state_manager.update_context({key: value})

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history."""
        return self.state_manager.get_history()
