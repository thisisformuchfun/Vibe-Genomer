"""
Unit tests for bioinformatics tool wrappers.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class TestBaseTool:
    """Test the base BioinformaticsTool class."""

    def test_tool_creation(self, mock_config, mock_logger):
        """Test creating a base tool."""
        from vibe_genomer.tools.base import BioinformaticsTool

        tool = BioinformaticsTool(
            name="test_tool", config=mock_config, logger=mock_logger
        )
        assert tool.name == "test_tool"
        assert tool.config == mock_config
        assert tool.logger == mock_logger

    def test_tool_validate_file_not_found(self, mock_config, mock_logger):
        """Test file validation fails for non-existent files."""
        from vibe_genomer.tools.base import BioinformaticsTool
        from vibe_genomer.utils.exceptions import ToolExecutionError

        tool = BioinformaticsTool(
            name="test_tool", config=mock_config, logger=mock_logger
        )

        with pytest.raises((ToolExecutionError, FileNotFoundError)):
            tool._validate_file_exists("/nonexistent/file.bam")


class TestSamtoolsView:
    """Test SAMtools view wrapper."""

    def test_samtools_view_creation(self, mock_config, mock_logger):
        """Test creating samtools view tool."""
        from vibe_genomer.tools.samtools.view import SamtoolsView

        tool = SamtoolsView(config=mock_config, logger=mock_logger)
        assert tool.name == "samtools_view"

    @patch("subprocess.run")
    def test_samtools_view_command_building(
        self, mock_run, mock_config, mock_logger, tmp_path
    ):
        """Test building samtools view commands."""
        from vibe_genomer.tools.samtools.view import SamtoolsView

        # Create a fake BAM file
        bam_file = tmp_path / "test.bam"
        bam_file.touch()

        # Mock successful subprocess run
        mock_run.return_value = Mock(returncode=0, stdout=b"@HD\tVN:1.0", stderr=b"")

        tool = SamtoolsView(config=mock_config, logger=mock_logger)
        tool.input(str(bam_file)).header_only()

        # We would normally call execute(), but for unit test just verify setup
        assert tool._input_file == str(bam_file)
        assert tool._header_only is True


class TestSamtoolsStats:
    """Test SAMtools stats wrapper."""

    def test_samtools_stats_creation(self, mock_config, mock_logger):
        """Test creating samtools stats tool."""
        from vibe_genomer.tools.samtools.stats import SamtoolsStats

        tool = SamtoolsStats(config=mock_config, logger=mock_logger)
        assert tool.name == "samtools_stats"

    @patch("subprocess.run")
    def test_samtools_stats_execution(
        self, mock_run, mock_config, mock_logger, tmp_path
    ):
        """Test executing samtools stats."""
        from vibe_genomer.tools.samtools.stats import SamtoolsStats

        # Create a fake BAM file
        bam_file = tmp_path / "test.bam"
        bam_file.touch()

        # Mock successful subprocess run
        mock_run.return_value = Mock(
            returncode=0,
            stdout=b"SN\traw total sequences:\t1000\nSN\tmapped reads:\t950",
            stderr=b"",
        )

        tool = SamtoolsStats(config=mock_config, logger=mock_logger)
        tool.input(str(bam_file))

        # Verify setup (actual execution would need real samtools)
        assert tool._input_file == str(bam_file)
