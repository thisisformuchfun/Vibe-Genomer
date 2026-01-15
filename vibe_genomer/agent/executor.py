"""
Tool execution orchestrator.

Handles the execution of bioinformatics tools with safety checks.
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..utils import Config, VibeLogger
    from .planner import WorkflowStep


@dataclass
class ExecutionResult:
    """Result of a tool execution."""

    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ToolExecutor:
    """
    Executes bioinformatics tools safely.

    Handles:
    - Tool validation
    - Sandbox execution
    - Output parsing
    - Error handling
    """

    def __init__(self, config: "Config", logger: "VibeLogger"):
        """
        Initialize tool executor.

        Args:
            config: Application configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self._initialize_sandbox()

    def _initialize_sandbox(self):
        """Initialize sandbox environment if enabled."""
        if self.config.sandbox.enabled:
            self.logger.debug(f"Initializing sandbox: {self.config.sandbox.backend}")
            # Sandbox initialization will be implemented later
            self.sandbox = None
        else:
            self.logger.warning("Sandbox disabled - tools will run without isolation")
            self.sandbox = None

    def execute_step(
        self,
        step: "WorkflowStep",
        context: Dict[str, Any],
    ) -> ExecutionResult:
        """
        Execute a workflow step.

        Args:
            step: Workflow step to execute
            context: Execution context with intermediate results

        Returns:
            Execution result
        """
        self.logger.info(f"Executing step: {step.step_id} - {step.description}")

        try:
            from .planner import StepType

            if step.step_type == StepType.TOOL_EXECUTION:
                return self._execute_tool(step, context)

            elif step.step_type == StepType.FILE_PARSING:
                return self._parse_file(step, context)

            elif step.step_type == StepType.DATA_VALIDATION:
                return self._validate_data(step, context)

            elif step.step_type == StepType.KNOWLEDGE_QUERY:
                return self._query_knowledge(step, context)

            elif step.step_type == StepType.RESULT_AGGREGATION:
                return self._aggregate_results(step, context)

            else:
                return ExecutionResult(
                    success=False,
                    output=None,
                    error=f"Unknown step type: {step.step_type}",
                )

        except Exception as e:
            self.logger.exception(e, f"Step execution failed: {step.step_id}")
            return ExecutionResult(
                success=False,
                output=None,
                error=str(e),
            )

    def _execute_tool(self, step: "WorkflowStep", context: Dict[str, Any]) -> ExecutionResult:
        """Execute a bioinformatics tool."""
        self.logger.debug(f"Executing tool: {step.tool_name}")

        if not step.tool_name:
            return ExecutionResult(
                success=False,
                output=None,
                error="No tool name specified",
            )

        try:
            from ..tools import get_tool

            # Get tool wrapper
            tool = get_tool(step.tool_name)

            # Resolve parameters from context
            params = self._resolve_parameters(step.parameters, context)

            # Execute tool
            if self.sandbox:
                output = tool.execute_in_sandbox(params, self.sandbox)
            else:
                output = tool.execute(params)

            return ExecutionResult(
                success=True,
                output=output,
                metadata={"tool": step.tool_name},
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                output=None,
                error=f"Tool execution failed: {e}",
            )

    def _parse_file(self, step: "WorkflowStep", context: Dict[str, Any]) -> ExecutionResult:
        """Parse a genomic file."""
        self.logger.debug(f"Parsing file: {step.parameters.get('file_path')}")

        try:
            from ..parsers import get_parser

            file_path = step.parameters.get("file_path")
            if not file_path:
                return ExecutionResult(
                    success=False,
                    output=None,
                    error="No file path specified",
                )

            # Get appropriate parser
            parser = get_parser(file_path)

            # Parse file
            parsed_data = parser.parse(file_path)

            return ExecutionResult(
                success=True,
                output=parsed_data,
                metadata={"file_type": parser.file_type},
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                output=None,
                error=f"File parsing failed: {e}",
            )

    def _validate_data(self, step: "WorkflowStep", context: Dict[str, Any]) -> ExecutionResult:
        """Validate genomic data."""
        self.logger.debug("Validating data")

        try:
            from ..verification import validate

            data_key = step.parameters.get("data_key")
            if not data_key or data_key not in context:
                return ExecutionResult(
                    success=False,
                    output=None,
                    error=f"Data key '{data_key}' not found in context",
                )

            data = context[data_key]

            # Validate
            is_valid, errors = validate(data, step.parameters)

            return ExecutionResult(
                success=is_valid,
                output={"valid": is_valid, "errors": errors},
                error=None if is_valid else f"Validation failed: {errors}",
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                output=None,
                error=f"Validation failed: {e}",
            )

    def _query_knowledge(self, step: "WorkflowStep", context: Dict[str, Any]) -> ExecutionResult:
        """Query knowledge base."""
        self.logger.debug("Querying knowledge base")

        try:
            from ..knowledge import query_database

            database = step.parameters.get("database")
            query = step.parameters.get("query")

            results = query_database(database, query)

            return ExecutionResult(
                success=True,
                output=results,
                metadata={"database": database},
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                output=None,
                error=f"Knowledge query failed: {e}",
            )

    def _aggregate_results(self, step: "WorkflowStep", context: Dict[str, Any]) -> ExecutionResult:
        """Aggregate results from previous steps."""
        self.logger.debug("Aggregating results")

        try:
            result_keys = step.parameters.get("result_keys", [])

            aggregated = {}
            for key in result_keys:
                if key in context:
                    aggregated[key] = context[key]

            return ExecutionResult(
                success=True,
                output=aggregated,
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                output=None,
                error=f"Aggregation failed: {e}",
            )

    def _resolve_parameters(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Resolve parameter values from context.

        Parameters can reference context values using ${key} syntax.

        Args:
            parameters: Raw parameters
            context: Execution context

        Returns:
            Resolved parameters
        """
        resolved = {}

        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Reference to context
                context_key = value[2:-1]
                resolved[key] = context.get(context_key, value)
            else:
                resolved[key] = value

        return resolved
