"""
RAG Module: Retrieval-Augmented Generation for Genomic Files

Enables the agent to "read" 100GB+ BAM files without loading them into
the context window. Uses intelligent indexing and chunking strategies.
"""

from vibe_genomer.rag.indexer import GenomicIndexer
from vibe_genomer.rag.retriever import GenomicRetriever
from vibe_genomer.rag.chunker import GenomicChunker

__all__ = ["GenomicIndexer", "GenomicRetriever", "GenomicChunker"]
