"""
Unit tests for agent components.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestGenomicAgent:
    """Test the main GenomicAgent class."""

    def test_agent_creation(self, mock_llm_provider, mock_config, mock_logger):
        """Test creating a GenomicAgent."""
        from vibe_genomer.agent.core import GenomicAgent

        agent = GenomicAgent(
            provider=mock_llm_provider, config=mock_config, logger=mock_logger
        )
        assert agent is not None
        assert agent.provider == mock_llm_provider
        assert agent.config == mock_config
        assert agent.logger == mock_logger

    def test_agent_has_components(self, mock_llm_provider, mock_config, mock_logger):
        """Test agent has required components."""
        from vibe_genomer.agent.core import GenomicAgent

        agent = GenomicAgent(
            provider=mock_llm_provider, config=mock_config, logger=mock_logger
        )
        assert hasattr(agent, "planner")
        assert hasattr(agent, "executor")
        assert hasattr(agent, "react_loop")
        assert hasattr(agent, "state_manager")

    def test_agent_execute(self, mock_llm_provider, mock_config, mock_logger):
        """Test agent execution with mock components."""
        from vibe_genomer.agent.core import GenomicAgent
        from vibe_genomer.agent.planner import WorkflowPlan, WorkflowStep

        agent = GenomicAgent(
            provider=mock_llm_provider, config=mock_config, logger=mock_logger
        )

        # Mock the planner to return a simple plan
        mock_plan = WorkflowPlan(
            query="test query",
            steps=[
                WorkflowStep(
                    name="test_step",
                    description="A test step",
                    tool="samtools",
                    parameters={},
                )
            ],
        )
        agent.planner.plan = Mock(return_value=mock_plan)

        # Mock the react loop to return a result
        agent.react_loop.execute_plan = Mock(return_value="Test result")

        result = agent.execute("Test query")
        assert result == "Test result"
        assert agent.planner.plan.called
        assert agent.react_loop.execute_plan.called


class TestStateManager:
    """Test the StateManager class."""

    def test_state_manager_creation(self, mock_logger):
        """Test creating a StateManager."""
        from vibe_genomer.agent.state_machine import StateManager

        sm = StateManager(logger=mock_logger)
        assert sm is not None

    def test_state_manager_add_message(self, mock_logger):
        """Test adding messages to state."""
        from vibe_genomer.agent.state_machine import StateManager

        sm = StateManager(logger=mock_logger)
        sm.add_user_message("Hello")
        sm.add_assistant_message("Hi there")

        history = sm.get_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there"

    def test_state_manager_context(self, mock_logger):
        """Test managing context."""
        from vibe_genomer.agent.state_machine import StateManager

        sm = StateManager(logger=mock_logger)
        sm.update_context({"working_dir": "/data", "genome": "hg38"})

        state = sm.get_state()
        assert state.context["working_dir"] == "/data"
        assert state.context["genome"] == "hg38"

    def test_state_manager_reset(self, mock_logger):
        """Test resetting state."""
        from vibe_genomer.agent.state_machine import StateManager

        sm = StateManager(logger=mock_logger)
        sm.add_user_message("Test message")
        sm.update_context({"key": "value"})

        sm.reset()
        state = sm.get_state()
        assert len(state.messages) == 0
        assert len(state.context) == 0


class TestWorkflowPlanner:
    """Test the WorkflowPlanner class."""

    def test_planner_creation(self, mock_llm_provider, mock_config, mock_logger):
        """Test creating a WorkflowPlanner."""
        from vibe_genomer.agent.planner import WorkflowPlanner

        planner = WorkflowPlanner(
            provider=mock_llm_provider, config=mock_config, logger=mock_logger
        )
        assert planner is not None

    def test_workflow_plan_creation(self):
        """Test creating a WorkflowPlan."""
        from vibe_genomer.agent.planner import WorkflowPlan, WorkflowStep

        step1 = WorkflowStep(
            name="step1", description="First step", tool="samtools", parameters={}
        )
        step2 = WorkflowStep(
            name="step2", description="Second step", tool="bedtools", parameters={}
        )

        plan = WorkflowPlan(query="Test query", steps=[step1, step2])
        assert plan.query == "Test query"
        assert len(plan.steps) == 2
        assert plan.steps[0].name == "step1"
        assert plan.steps[1].name == "step2"


class TestToolExecutor:
    """Test the ToolExecutor class."""

    def test_executor_creation(self, mock_config, mock_logger):
        """Test creating a ToolExecutor."""
        from vibe_genomer.agent.executor import ToolExecutor

        executor = ToolExecutor(config=mock_config, logger=mock_logger)
        assert executor is not None

    def test_executor_tool_registry(self, mock_config, mock_logger):
        """Test tool registry."""
        from vibe_genomer.agent.executor import ToolExecutor

        executor = ToolExecutor(config=mock_config, logger=mock_logger)
        assert hasattr(executor, "tools")
        assert isinstance(executor.tools, dict)
