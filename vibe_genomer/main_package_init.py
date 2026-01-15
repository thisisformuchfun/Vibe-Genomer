"""
Vibe-Genomer: The Claude Code for Genomics

An autonomous genomic agent that translates natural language into
executable bioinformatics workflows.
"""

__version__ = "0.1.0"
__author__ = "Vibe-Genomer Contributors"
__license__ = "Apache 2.0"

from vibe_genomer.agent import GenomicAgent
from vibe_genomer.models import create_provider
from vibe_genomer.utils import get_config, get_logger

__all__ = [
    "GenomicAgent",
    "create_provider",
    "get_config",
    "get_logger",
    "__version__",
]
