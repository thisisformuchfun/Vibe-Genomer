# Tools Module

Standardized wrappers for bioinformatics tools. Each tool provides:
- **Input validation**: Ensures parameters make sense
- **Error handling**: Graceful failures with actionable messages
- **Progress tracking**: For long-running operations
- **Output parsing**: Structured results the agent can understand

## Tool Categories

### `samtools/`
BAM/SAM/CRAM file manipulation
- `view.py` - Filter and convert alignment files
- `index.py` - Index BAM files
- `sort.py` - Sort alignments
- `stats.py` - Generate alignment statistics

### `bedtools/`
Genomic interval operations
- `intersect.py` - Find overlapping regions
- `merge.py` - Merge intervals
- `coverage.py` - Calculate coverage

### `bcftools/`
VCF/BCF variant manipulation
- `query.py` - Extract variant information
- `filter.py` - Filter variants by criteria
- `annotate.py` - Add annotations

### `nextflow/`
Workflow orchestration for complex pipelines

### `custom/`
Custom tools built specifically for Vibe-Genomer
- `variant_context.py` - Extract surrounding genomic context
- `gene_lookup.py` - Quick gene coordinate lookups
- `qc_report.py` - Generate standardized QC reports

## Design Pattern

All tools inherit from `BioinformaticsTool` base class:

```python
class SamtoolsView(BioinformaticsTool):
    def validate_inputs(self, **kwargs) -> bool:
        """Check inputs before execution"""

    def build_command(self, **kwargs) -> str:
        """Construct the shell command"""

    def execute(self, **kwargs) -> ToolResult:
        """Run the tool and capture output"""

    def parse_output(self, raw_output: str) -> dict:
        """Parse results into structured data"""
```
