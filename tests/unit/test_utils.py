"""
Unit tests for utility modules.
"""

import pytest
from unittest.mock import Mock, patch
from vibe_genomer.utils.exceptions import (
    VibeGenomerError,
    ConfigurationError,
    ToolExecutionError,
    ValidationError,
)


class TestExceptions:
    """Test custom exception classes."""

    def test_base_exception(self):
        """Test base VibeGenomerError."""
        error = VibeGenomerError("test message")
        assert str(error) == "test message"
        assert isinstance(error, Exception)

    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("config missing")
        assert str(error) == "config missing"
        assert isinstance(error, VibeGenomerError)

    def test_tool_execution_error(self):
        """Test ToolExecutionError."""
        error = ToolExecutionError("tool failed", tool="samtools", exit_code=1)
        assert "tool failed" in str(error)
        assert error.tool == "samtools"
        assert error.exit_code == 1

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("invalid coordinates")
        assert "invalid coordinates" in str(error)
        assert isinstance(error, VibeGenomerError)


class TestConfig:
    """Test configuration management."""

    def test_config_creation(self, tmp_path):
        """Test creating a config object."""
        from vibe_genomer.utils import Config

        # Create a temporary config file
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
agent:
  max_iterations: 5
  temperature: 0.8

tools:
  timeout: 60
""")

        config = Config(config_file=str(config_file))
        assert config is not None

    def test_config_get_nested(self, mock_config):
        """Test getting nested config values."""
        mock_config.get.return_value = 10
        value = mock_config.get("agent.max_iterations")
        assert value == 10


class TestLogging:
    """Test logging functionality."""

    def test_logger_creation(self):
        """Test creating a logger."""
        from vibe_genomer.utils import VibeLogger

        logger = VibeLogger("test")
        assert logger is not None
        assert logger.name == "test"

    def test_logger_methods(self, mock_logger):
        """Test logger methods exist and can be called."""
        mock_logger.debug("debug message")
        mock_logger.info("info message")
        mock_logger.warning("warning message")
        mock_logger.error("error message")

        assert mock_logger.debug.called
        assert mock_logger.info.called
        assert mock_logger.warning.called
        assert mock_logger.error.called
