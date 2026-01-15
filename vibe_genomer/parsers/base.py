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
    from ..utils.exceptions import UnsupportedFormatError

    path = Path(file_path)
    suffix = path.suffix.lower()

    # Handle compressed files
    if suffix == ".gz":
        suffix = path.stem.split(".")[-1].lower()

    # Map extensions to parsers
    parser_map = {
        "vcf": "VCFParser",
        "bam": "BAMParser",
        "sam": "BAMParser",
        "fastq": "FASTQParser",
        "fq": "FASTQParser",
    }

    parser_class_name = parser_map.get(suffix)
    if not parser_class_name:
        raise UnsupportedFormatError(
            f"No parser available for file type: {suffix}. "
            f"Supported formats: {', '.join(parser_map.keys())}"
        )

    # Import and instantiate the parser
    if parser_class_name == "VCFParser":
        from .vcf import VCFParser

        return VCFParser()
    elif parser_class_name == "BAMParser":
        from .bam import BAMParser

        return BAMParser()
    elif parser_class_name == "FASTQParser":
        from .fastq import FASTQParser

        return FASTQParser()

    raise UnsupportedFormatError(f"Parser for {file_path} not yet implemented")
