"""
Parsers Module: Genomic File Format Handlers

Intelligent parsers that understand the semantics of genomic file formats,
not just their syntax. These parsers enable the RAG system to index and
retrieve information from massive binary files.
"""

from vibe_genomer.parsers.base import GenomicFileParser
from vibe_genomer.parsers.vcf import VCFParser
from vibe_genomer.parsers.bam import BAMParser
from vibe_genomer.parsers.fastq import FASTQParser

__all__ = ["GenomicFileParser", "VCFParser", "BAMParser", "FASTQParser"]
