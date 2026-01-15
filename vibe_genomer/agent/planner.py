"""
Workflow planner for genomic analysis.

Decomposes natural language queries into executable workflow steps.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from ..models import BaseLLMProvider
    from ..utils import Config, VibeLogger
    from .state_machine import AgentState


class StepType(Enum):
    """Types of workflow steps."""

    TOOL_EXECUTION = "tool_execution"  # Execute a bioinformatics tool
    FILE_PARSING = "file_parsing"  # Parse a genomic file
    DATA_VALIDATION = "data_validation"  # Validate data/coordinates
    KNOWLEDGE_QUERY = "knowledge_query"  # Query knowledge base
    RESULT_AGGREGATION = "result_aggregation"  # Combine results


@dataclass
class WorkflowStep:
    """A single step in a workflow."""

    step_id: str
    step_type: StepType
    description: str
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)  # Step IDs this depends on
    output_key: Optional[str] = None  # Where to store the result

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "step_type": self.step_type.value,
            "description": self.description,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "depends_on": self.depends_on,
            "output_key": self.output_key,
        }


@dataclass
class WorkflowPlan:
    """A complete workflow plan."""

    query: str
    steps: List[WorkflowStep]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_next_step(self, completed_steps: List[str]) -> Optional[WorkflowStep]:
        """
        Get the next executable step.

        Args:
            completed_steps: List of completed step IDs

        Returns:
            Next step to execute, or None if all done
        """
        for step in self.steps:
            # Skip if already completed
            if step.step_id in completed_steps:
                continue

            # Check if dependencies are satisfied
            if all(dep in completed_steps for dep in step.depends_on):
                return step

        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": self.metadata,
        }


class WorkflowPlanner:
    """
    Plans multi-step genomic workflows from natural language.

    Uses the LLM to decompose complex queries into executable steps.
    """

    PLANNING_PROMPT = """You are an expert bioinformatics workflow planner. Your job is to decompose
a natural language query into a series of executable steps.

Available step types:
- tool_execution: Execute a bioinformatics tool (samtools, bedtools, bcftools, etc.)
- file_parsing: Parse and extract information from genomic files
- data_validation: Validate genomic coordinates or data
- knowledge_query: Query reference databases (ClinVar, Ensembl, etc.)
- result_aggregation: Combine and summarize results

Given a query, create a detailed workflow plan. For each step, specify:
1. A unique step_id (step_1, step_2, etc.)
2. The step_type
3. A clear description
4. The tool_name (if tool_execution)
5. Required parameters
6. Dependencies (which steps must complete first)

Query: {query}

Context: {context}

Create a JSON workflow plan with the following structure:
{{
    "steps": [
        {{
            "step_id": "step_1",
            "step_type": "file_parsing",
            "description": "Parse the VCF file to understand its structure",
            "parameters": {{"file_path": "sample.vcf"}},
            "depends_on": [],
            "output_key": "vcf_metadata"
        }},
        ...
    ]
}}

Be specific about parameters and ensure steps are in logical order."""

    def __init__(
        self,
        provider: "BaseLLMProvider",
        config: "Config",
        logger: "VibeLogger",
    ):
        """
        Initialize the workflow planner.

        Args:
            provider: LLM provider
            config: Configuration
            logger: Logger
        """
        self.provider = provider
        self.config = config
        self.logger = logger

    def plan(self, query: str, state: "AgentState") -> WorkflowPlan:
        """
        Create a workflow plan for a query.

        Args:
            query: User query
            state: Current agent state

        Returns:
            Workflow plan
        """
        self.logger.info(f"Planning workflow for: {query}")

        try:
            # Format context from state
            context = self._format_context(state)

            # Get plan from LLM
            plan_json = self._get_plan_from_llm(query, context)

            # Parse plan
            plan = self._parse_plan(query, plan_json)

            self.logger.success(f"Created plan with {len(plan.steps)} steps")

            return plan

        except Exception as e:
            self.logger.error(f"Planning failed: {e}")
            # Fall back to simple single-step plan
            return self._create_fallback_plan(query)

    def _format_context(self, state: "AgentState") -> str:
        """Format agent state as context for the LLM."""
        context_parts = []

        # Add relevant context
        if state.context:
            context_parts.append("Context:")
            for key, value in state.context.items():
                context_parts.append(f"  {key}: {value}")

        # Add recent conversation
        if state.messages:
            recent = state.messages[-5:]  # Last 5 messages
            context_parts.append("\nRecent conversation:")
            for msg in recent:
                context_parts.append(f"  {msg.role}: {msg.content[:100]}...")

        return "\n".join(context_parts) if context_parts else "No prior context"

    def _get_plan_from_llm(self, query: str, context: str) -> Dict[str, Any]:
        """Get workflow plan from LLM."""
        from ..models import Message, MessageRole
        import json

        prompt = self.PLANNING_PROMPT.format(query=query, context=context)

        messages = [Message(MessageRole.USER, prompt)]

        response = self.provider.complete(messages)

        # Extract JSON from response
        content = response.content.strip()

        # Try to extract JSON from markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        try:
            plan_json = json.loads(content)
            return plan_json
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse plan JSON: {e}")
            self.logger.debug(f"Response content: {content}")
            raise

    def _parse_plan(self, query: str, plan_json: Dict[str, Any]) -> WorkflowPlan:
        """Parse JSON plan into WorkflowPlan object."""
        steps = []

        for step_data in plan_json.get("steps", []):
            step = WorkflowStep(
                step_id=step_data["step_id"],
                step_type=StepType(step_data["step_type"]),
                description=step_data["description"],
                tool_name=step_data.get("tool_name"),
                parameters=step_data.get("parameters", {}),
                depends_on=step_data.get("depends_on", []),
                output_key=step_data.get("output_key"),
            )
            steps.append(step)

        return WorkflowPlan(
            query=query,
            steps=steps,
            metadata=plan_json.get("metadata", {}),
        )

    def _create_fallback_plan(self, query: str) -> WorkflowPlan:
        """Create a simple fallback plan when LLM planning fails."""
        self.logger.warning("Using fallback plan")

        step = WorkflowStep(
            step_id="step_1",
            step_type=StepType.TOOL_EXECUTION,
            description=f"Process query: {query}",
            parameters={"query": query},
            depends_on=[],
        )

        return WorkflowPlan(
            query=query,
            steps=[step],
            metadata={"fallback": True},
        )
