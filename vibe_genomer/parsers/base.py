"""
Base parser for genomic file formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class GenomicFileParser(ABC):
    """Base class for genomic file parsers."""

    def __init__(self):
        self.file_type = self.__class__.__name__.replace("Parser", "").lower()

    @abstractmethod
    def parse(self, file_path: Path) -> Any:
        """Parse the file and return structured data."""
        pass


def get_parser(file_path: str) -> GenomicFileParser:
    """Get appropriate parser for a file based on extension."""
    from ..utils import UnsupportedFormatError

    # Stub implementation
    raise UnsupportedFormatError(f"Parser for {file_path} not yet implemented")
