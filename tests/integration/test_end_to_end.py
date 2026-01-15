"""
Integration tests for end-to-end workflows.
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete agent workflows."""

    def test_simple_query_flow(self, mock_llm_provider, mock_config, mock_logger):
        """Test a simple query from start to finish."""
        from vibe_genomer.agent.core import GenomicAgent
        from vibe_genomer.agent.planner import WorkflowPlan, WorkflowStep

        # Create agent
        agent = GenomicAgent(
            provider=mock_llm_provider, config=mock_config, logger=mock_logger
        )

        # Mock planner to return a simple workflow
        mock_plan = WorkflowPlan(
            query="Get BAM file statistics",
            steps=[
                WorkflowStep(
                    name="get_stats",
                    description="Run samtools stats",
                    tool="samtools_stats",
                    parameters={"input_file": "/path/to/test.bam"},
                )
            ],
        )
        agent.planner.plan = Mock(return_value=mock_plan)

        # Mock react loop to return result
        agent.react_loop.execute_plan = Mock(
            return_value="Total reads: 1000\nMapped reads: 950\nMapping rate: 95%"
        )

        # Execute query
        result = agent.execute("Get statistics for test.bam")

        # Verify flow
        assert agent.planner.plan.called
        assert agent.react_loop.execute_plan.called
        assert "1000" in result
        assert "950" in result

    def test_multi_step_workflow(self, mock_llm_provider, mock_config, mock_logger):
        """Test a multi-step workflow."""
        from vibe_genomer.agent.core import GenomicAgent
        from vibe_genomer.agent.planner import WorkflowPlan, WorkflowStep

        # Create agent
        agent = GenomicAgent(
            provider=mock_llm_provider, config=mock_config, logger=mock_logger
        )

        # Mock planner to return multi-step workflow
        mock_plan = WorkflowPlan(
            query="Extract region and get stats",
            steps=[
                WorkflowStep(
                    name="extract_region",
                    description="Extract chr1:1000-2000",
                    tool="samtools_view",
                    parameters={
                        "input_file": "/path/to/test.bam",
                        "region": "chr1:1000-2000",
                    },
                ),
                WorkflowStep(
                    name="get_stats",
                    description="Get statistics",
                    tool="samtools_stats",
                    parameters={"input_file": "/path/to/extracted.bam"},
                ),
            ],
        )
        agent.planner.plan = Mock(return_value=mock_plan)
        agent.react_loop.execute_plan = Mock(
            return_value="Extracted region: chr1:1000-2000\nReads in region: 42"
        )

        # Execute query
        result = agent.execute("Extract chr1:1000-2000 from test.bam and get stats")

        # Verify
        assert agent.planner.plan.called
        assert len(mock_plan.steps) == 2
        assert "42" in result

    def test_error_handling(self, mock_llm_provider, mock_config, mock_logger):
        """Test error handling in workflow."""
        from vibe_genomer.agent.core import GenomicAgent

        # Create agent
        agent = GenomicAgent(
            provider=mock_llm_provider, config=mock_config, logger=mock_logger
        )

        # Mock planner to raise an error
        agent.planner.plan = Mock(side_effect=Exception("Planning failed"))

        # Execute query (should handle error gracefully)
        result = agent.execute("Invalid query")

        # Verify error was handled
        assert "failed" in result.lower()

    def test_state_persistence(self, mock_llm_provider, mock_config, mock_logger):
        """Test that conversation state persists across queries."""
        from vibe_genomer.agent.core import GenomicAgent
        from vibe_genomer.agent.planner import WorkflowPlan, WorkflowStep

        # Create agent
        agent = GenomicAgent(
            provider=mock_llm_provider, config=mock_config, logger=mock_logger
        )

        # Mock components
        mock_plan = WorkflowPlan(
            query="test", steps=[WorkflowStep("step", "desc", "tool", {})]
        )
        agent.planner.plan = Mock(return_value=mock_plan)
        agent.react_loop.execute_plan = Mock(return_value="Result 1")

        # Execute first query
        agent.execute("First query")

        # Execute second query
        agent.react_loop.execute_plan = Mock(return_value="Result 2")
        agent.execute("Second query")

        # Check state has both queries
        history = agent.get_conversation_history()
        assert len(history) >= 2
        assert any("First query" in msg.get("content", "") for msg in history)
        assert any("Second query" in msg.get("content", "") for msg in history)


@pytest.mark.integration
@pytest.mark.requires_tools
class TestRealToolExecution:
    """Integration tests with real bioinformatics tools (skipped if tools not available)."""

    def test_samtools_available(self):
        """Test if samtools is available."""
        import subprocess

        try:
            result = subprocess.run(
                ["samtools", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            assert result.returncode == 0
            assert "samtools" in result.stdout.lower()
        except FileNotFoundError:
            pytest.skip("samtools not installed")
        except subprocess.TimeoutExpired:
            pytest.skip("samtools timeout")
