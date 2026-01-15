"""
Pytest configuration and shared fixtures.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

# Test data directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    from vibe_genomer.utils import Config

    config = Mock(spec=Config)
    config.get.return_value = None
    config.agent_config = {
        "max_iterations": 10,
        "temperature": 0.7,
        "max_tokens": 2000,
    }
    config.tool_config = {
        "timeout": 300,
        "max_retries": 3,
    }
    config.sandbox_enabled = False
    return config


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    from vibe_genomer.utils import VibeLogger

    logger = Mock(spec=VibeLogger)
    return logger


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLM provider for testing."""
    from vibe_genomer.models import BaseLLMProvider

    provider = Mock(spec=BaseLLMProvider)
    provider.generate.return_value = "Mock LLM response"
    provider.generate_structured.return_value = {"mock": "data"}
    return provider


@pytest.fixture
def sample_vcf_path(fixtures_dir):
    """Return path to sample VCF file."""
    return fixtures_dir / "sample.vcf"


@pytest.fixture
def sample_bam_path(fixtures_dir):
    """Return path to sample BAM file."""
    return fixtures_dir / "sample.bam"


@pytest.fixture
def sample_fastq_path(fixtures_dir):
    """Return path to sample FASTQ file."""
    return fixtures_dir / "sample.fastq"
