"""
Parsers Module: Genomic File Format Handlers

Intelligent parsers that understand the semantics of genomic file formats,
not just their syntax. These parsers enable the RAG system to index and
retrieve information from massive binary files.
"""

from vibe_genomer.parsers.base import GenomicFileParser, get_parser
from vibe_genomer.parsers.vcf import VCFParser, VCFHeader, VCFVariant
from vibe_genomer.parsers.bam import BAMParser, BAMHeader, BAMAlignment
from vibe_genomer.parsers.fastq import FASTQParser, FASTQRead

__all__ = [
    "GenomicFileParser",
    "get_parser",
    "VCFParser",
    "VCFHeader",
    "VCFVariant",
    "BAMParser",
    "BAMHeader",
    "BAMAlignment",
    "FASTQParser",
    "FASTQRead",
]
