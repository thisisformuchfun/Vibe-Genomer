# Parsers Module

Biologically-aware file parsers that understand genomic semantics.

## Key Capabilities

### Semantic Understanding
- Knows `chr1` and `1` refer to the same chromosome
- Understands coordinate systems (0-based vs 1-based)
- Recognizes when headers contain critical metadata

### Efficient Streaming
- Never loads entire files into memory
- Uses indexed access for BAM/VCF files
- Chunks large files for RAG processing

### Format Support

**`vcf.py`** - Variant Call Format
- Parses headers for sample information
- Extracts variant annotations
- Handles multi-allelic sites
- Supports both VCF and BCF

**`bam.py`** - Binary Alignment Map
- Reads headers for reference sequences
- Extracts read groups and metadata
- Streams alignments by region
- Calculates on-the-fly statistics

**`fastq.py`** - Raw Sequencing Reads
- Quality score parsing
- Read length distribution
- Adapter detection hints

**`gff.py`** - Gene Feature Format
- Feature hierarchy (gene → transcript → exon)
- Attribute parsing
- Coordinate extraction

**`bed.py`** - Browser Extensible Data
- Interval operations
- Score and name extraction
- BED3/BED6/BED12 support

## Integration with RAG

Parsers work with the RAG module to:
1. **Index**: Build searchable indices of file contents
2. **Chunk**: Break large files into meaningful segments
3. **Retrieve**: Fetch specific regions without full file reads

Example:
```python
bam_parser = BAMParser("sample.bam")
# Agent asks: "What's the average coverage in BRCA1?"
brca1_region = knowledge.get_gene_coords("BRCA1")  # chr17:43044295-43125483
coverage = bam_parser.calculate_coverage(brca1_region)  # Streams only that region
```
