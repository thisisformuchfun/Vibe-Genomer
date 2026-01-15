# RAG Module

**The Challenge**: Genomic files are massive. A whole-genome BAM can be 200GB. You can't put that in an LLM context window.

**The Solution**: RAG (Retrieval-Augmented Generation) for genomics.

## Architecture

### 1. Indexing (`indexer.py`)

Build searchable indices of genomic files:
- **BAM/CRAM**: Index by region, read group, alignment quality
- **VCF**: Index by chromosome, gene, variant type
- **FASTQ**: Index by quality metrics, sequence motifs

```python
indexer = GenomicIndexer()
indexer.index_bam("sample.bam")
# Creates: sample.bam.vibeindex (metadata, stats, key positions)
```

### 2. Chunking (`chunker.py`)

Break files into semantically meaningful pieces:
- **Region-based**: "All variants in BRCA1"
- **Feature-based**: "All high-quality SNPs"
- **Statistics-based**: "Coverage summary per chromosome"

Smart chunking respects biological boundaries:
- Don't split a variant across chunks
- Keep read pairs together
- Maintain annotation context

### 3. Retrieval (`retriever.py`)

Fetch only what's needed for the current query:

```python
retriever = GenomicRetriever("sample.bam")
context = retriever.get_context(
    query="What's the coverage in BRCA1?",
    region="chr17:43044295-43125483"
)
# Returns: {stats: {mean_cov: 30.5, ...}, sample_reads: [...]}
```

### 4. Embedding (`embeddings.py`)

Create vector representations of genomic features for semantic search:
- Embed variant descriptions
- Embed gene functions
- Embed quality metrics

Enables: "Find variants similar to this pathogenic deletion"

## Strategies

### For Large BAM Files
1. Read header immediately (small, contains critical info)
2. Create spatial index if missing (.bai)
3. On query, fetch only the requested region
4. Summarize statistics instead of returning raw reads

### For VCF Files
1. Parse header for sample/annotation metadata
2. Index by chromosome/position
3. Cache frequently accessed annotations
4. Stream variants matching query criteria

### For Knowledge Bases
1. Embed gene descriptions, pathways, phenotypes
2. Build vector database for semantic search
3. Cross-reference IDs (HGNC, Ensembl, RefSeq)

## Performance

| File Type | Size | Cold Start | Query Time |
|-----------|------|------------|------------|
| BAM       | 100GB| 2-3s (index load) | 0.1-0.5s per region |
| VCF       | 10GB | 1s         | 0.05-0.2s per query |
| ClinVar   | 500MB| 5s (embed) | 0.01s semantic search |

## Integration with Agent

```
User: "Are there any pathogenic variants in my BAM?"
  ↓
Agent → RAG: "Get variant calls from BAM"
RAG: [Retrieves only variant positions + quality scores]
  ↓
Agent → Knowledge: "Check ClinVar for these positions"
RAG: [Semantic search for known pathogenic variants]
  ↓
Agent → Verification: "Validate coordinates and annotations"
  ↓
Response: "Found 2 pathogenic variants: chr1:12345 (ClinVar ID: 123)"
```
