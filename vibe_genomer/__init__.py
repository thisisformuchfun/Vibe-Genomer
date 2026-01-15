"""
Vibe-Genomer: The Claude Code for Genomics

An autonomous genomic agent that translates natural language into
bioinformatics workflows.
"""

__version__ = "0.1.0"
__author__ = "Vibe-Genomer Contributors"

from vibe_genomer.agent.core import GenomicAgent
from vibe_genomer.cli.main import main

__all__ = ["GenomicAgent", "main", "__version__"]
