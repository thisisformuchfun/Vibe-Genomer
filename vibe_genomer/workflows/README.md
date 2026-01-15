# Workflows Module

Pre-built, validated workflow templates for common genomic analysis patterns.

## Design Philosophy

Instead of planning every step from scratch, the agent can invoke tested workflow "skills" that encode bioinformatics best practices.

## Workflow Templates

### `alignment.py` - Read Alignment Workflows
**Short-read alignment (Illumina)**:
```
FASTQ → (QC) → BWA-MEM → Sort → Mark Duplicates → Index → QC Report
```

**Long-read alignment (PacBio/Nanopore)**:
```
FASTQ → Minimap2 → Sort → Index → QC Report
```

### `variant_calling.py` - Variant Discovery Workflows
**Germline variant calling**:
```
BAM → GATK HaplotypeCaller → Filter → Annotate → VCF
```

**Somatic variant calling (tumor-normal)**:
```
Tumor BAM + Normal BAM → Mutect2 → FilterMutectCalls → Annotate → VCF
```

**Structural variant calling**:
```
BAM → Manta/LUMPY → Filter → Annotate → VCF
```

### `qc.py` - Quality Control Workflows
**Pre-alignment QC**:
```
FASTQ → FastQC → MultiQC → Adapter Content Check → Quality Report
```

**Post-alignment QC**:
```
BAM → Coverage Analysis → Insert Size → Duplication Rate → QC Report
```

### `annotation.py` - Variant Annotation Workflows
```
VCF → VEP/SnpEff → ClinVar → CADD scores → dbSNP → Annotated VCF
```

### `comparative.py` - Differential Analysis Workflows
**Tumor-normal comparison**:
```
Tumor VCF + Normal VCF → Filter germline → Prioritize somatic → Report
```

## Workflow Definition Format

Each workflow is defined as a DAG (Directed Acyclic Graph):

```python
class AlignmentWorkflow(Workflow):
    name = "short_read_alignment"
    description = "Align Illumina short reads to reference genome"

    required_inputs = ["fastq_files", "reference_genome"]
    outputs = ["aligned_bam", "qc_report"]

    steps = [
        Step("qc_check", tool="fastqc", inputs=["fastq_files"]),
        Step("align", tool="bwa_mem", inputs=["fastq_files", "reference_genome"]),
        Step("sort", tool="samtools_sort", inputs=["align.output"]),
        Step("mark_dups", tool="picard_markdup", inputs=["sort.output"]),
        Step("index", tool="samtools_index", inputs=["mark_dups.output"]),
        Step("stats", tool="samtools_stats", inputs=["mark_dups.output"]),
    ]

    def validate(self):
        """Ensure inputs are valid before starting"""

    def on_error(self, step, error):
        """Handle step failures gracefully"""
```

## Integration with Agent

```
User: "Align these FASTQ files to hg38"
  ↓
Agent: Recognizes this as a standard alignment task
  ↓
Planner: Loads AlignmentWorkflow template
  ↓
Executor: Runs each step, monitors progress
  ↓
Verification: Validates BAM file integrity
  ↓
Response: "Alignment complete. Mean coverage: 30x, 98% mapped."
```

## Benefits

1. **Consistency**: Every alignment follows best practices
2. **Validation**: Steps include sanity checks
3. **Monitoring**: Progress tracking for long workflows
4. **Recovery**: Automatic retry on transient failures
5. **Optimization**: Parallel execution where possible

## Custom Workflows

Users can define custom workflows via YAML:

```yaml
name: "my_custom_pipeline"
description: "Custom variant calling with specific filters"

steps:
  - name: "call_variants"
    tool: "bcftools_mpileup"
    params:
      min_BQ: 30
      max_depth: 1000

  - name: "filter"
    tool: "bcftools_filter"
    params:
      min_qual: 30
      min_depth: 10

  - name: "annotate"
    tool: "vep"
    database: "ensembl"
```

The agent can then invoke: `vibe "Run my_custom_pipeline on sample.bam"`
