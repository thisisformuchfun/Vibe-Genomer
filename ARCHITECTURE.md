# Vibe-Genomer Architecture

**Status**: Pre-Alpha Design Document
**Last Updated**: 2026-01-15

---

## Overview

Vibe-Genomer is an **autonomous genomic agent** - think "Claude Code for Genomics". It translates natural language requests into executable bioinformatics workflows, with built-in verification, safety, and biological awareness.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User (CLI)                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent (The "Brain")                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Planner  │→ │ Executor │→ │  ReAct   │→ │  State   │   │
│  │          │  │          │  │   Loop   │  │ Machine  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└───┬─────────────────┬─────────────────┬─────────────────┬──┘
    │                 │                 │                 │
    ▼                 ▼                 ▼                 ▼
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Tools  │     │ Parsers  │     │   RAG    │     │Knowledge │
│ samtools│     │ VCF/BAM  │     │ Indexer  │     │ ClinVar  │
│ bedtools│     │ FASTQ    │     │ Chunker  │     │ Ensembl  │
│ bcftools│     │          │     │Retriever │     │  UCSC    │
└─────────┘     └──────────┘     └──────────┘     └──────────┘
    │                 │                 │                 │
    └─────────────────┴─────────────────┴─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Verification    │
                    │  (Ground Truth)  │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │    Sandbox       │
                    │ (Docker/Sing.)   │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Shell Execution │
                    └──────────────────┘
```

## Module Descriptions

### 1. **Agent** (`vibe_genomer/agent/`)
The "brain" that orchestrates everything.

- **`core.py`**: Main `GenomicAgent` class
- **`planner.py`**: Decomposes requests into multi-step plans
- **`executor.py`**: Executes individual tools
- **`react_loop.py`**: Implements Reasoning + Acting pattern
- **`state_machine.py`**: Manages conversation state

**Example Flow**:
```
"Analyze this BAM for BRCA1 deletions"
  → Parse intent
  → Plan: [Extract region → Detect SVs → Validate → Report]
  → Execute each step
  → Verify results
  → Return summary
```

### 2. **Tools** (`vibe_genomer/tools/`)
Wrappers for bioinformatics command-line tools.

Each tool wrapper provides:
- Input validation
- Command construction
- Error handling
- Output parsing

**Structure**:
```
tools/
├── samtools/      # BAM/SAM manipulation
├── bedtools/      # Genomic intervals
├── bcftools/      # VCF/BCF operations
├── nextflow/      # Workflow orchestration
└── custom/        # Vibe-specific tools
```

### 3. **Parsers** (`vibe_genomer/parsers/`)
Biologically-aware file format parsers.

- **Semantic understanding**: Knows `chr1` == `1`
- **Efficient streaming**: Never loads full files
- **Format support**: VCF, BAM, FASTQ, GFF, BED

Enables RAG to index massive files.

### 4. **Verification** (`vibe_genomer/verification/`)
The **critical safety layer**. Validates all genomic claims.

- **Coordinate validation**: Are coordinates in bounds?
- **Variant validation**: Does REF allele match reference?
- **Reference checking**: Cross-check with ClinVar/Ensembl
- **Biological constraints**: Sanity checks (coverage can't be negative)

> "In biology, a hallucinated SNP is a misdiagnosis."

### 5. **RAG** (`vibe_genomer/rag/`)
Retrieval-Augmented Generation for genomic files.

**Problem**: 100GB BAM files don't fit in context windows.

**Solution**:
- **Index**: Build searchable metadata
- **Chunk**: Break into meaningful segments
- **Retrieve**: Fetch only what's needed

### 6. **Workflows** (`vibe_genomer/workflows/`)
Pre-built pipeline templates.

- `alignment.py`: Read alignment workflows
- `variant_calling.py`: Germline/somatic calling
- `qc.py`: Quality control pipelines
- `annotation.py`: Variant annotation

### 7. **Models** (`vibe_genomer/models/`)
LLM provider abstractions.

- Anthropic Claude (via SDK)
- OpenAI (GPT-4o)
- Local models (Ollama)
- Model-agnostic interface

### 8. **Sandbox** (`vibe_genomer/sandbox/`)
Safe execution environment.

- Docker/Singularity containerization
- Read-only reference genomes
- Resource limits (CPU, memory, time)
- Command whitelisting

### 9. **Knowledge** (`vibe_genomer/knowledge/`)
Genomic reference databases.

- ClinVar (variant interpretations)
- Ensembl (gene annotations)
- UCSC (reference genomes)
- Vector embeddings for semantic search

### 10. **CLI** (`vibe_genomer/cli/`)
User interface.

```bash
# One-shot command
vibe "Align FASTQ files to hg38"

# Interactive REPL
vibe repl
```

---

## Data Flow Example

**User Request**: "Find pathogenic variants in my VCF"

1. **CLI** → Agent: Parses request
2. **Agent** → RAG: "Index this VCF"
3. **RAG** → Parser: Streams VCF, builds index
4. **Agent** → Knowledge: "Query ClinVar for pathogenic variants"
5. **Knowledge** → Agent: Returns known pathogenic positions
6. **Agent** → Tools: "Filter VCF for these positions"
7. **Tools** → Sandbox: Executes `bcftools view` in container
8. **Sandbox** → Agent: Returns filtered variants
9. **Agent** → Verification: "Validate these variants"
10. **Verification** → Agent: Confirms coordinates + annotations valid
11. **Agent** → User: "Found 3 pathogenic variants: [...]"

---

## Key Design Principles

### 1. **Biological Awareness**
Not just text processing - understands genomic semantics.

### 2. **Safety First**
Every operation is validated, sandboxed, and auditable.

### 3. **Efficiency**
Never loads entire files - intelligent streaming and indexing.

### 4. **Modularity**
Each component is independent and testable.

### 5. **Privacy**
Local-first architecture - sensitive data stays on-premises.

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.10+ (main), Rust (performance modules) |
| **Agent Framework** | LangGraph / Custom ReAct loop |
| **LLM Interface** | Anthropic SDK, OpenAI SDK, Ollama |
| **Containerization** | Docker, Singularity |
| **Databases** | SQLite (local cache), FAISS (vector search) |
| **Bioinformatics** | htslib, samtools, bedtools, bcftools, nextflow |
| **CLI Framework** | Click, Rich (formatting) |
| **Testing** | pytest, hypothesis (property testing) |

---

## Future Roadmap

### Phase 1: Foundation (Current)
- Basic agent that translates NL → command-line tools
- Core tool wrappers (samtools, bedtools, bcftools)
- Simple verification layer

### Phase 2: Intelligence
- Multi-step workflow planning
- RAG for large file handling
- ClinVar/Ensembl integration

### Phase 3: Interaction
- Interactive REPL for iterative analysis
- Workflow debugging and inspection
- Result visualization

### Phase 4: Autonomy
- Self-correction on tool failures
- Adaptive planning based on intermediate results
- Local model support (offline operation)

---

## Contributing

See the module-specific README files for detailed contribution guidelines:
- `agent/README.md` - Agent logic
- `tools/README.md` - Tool integrations
- `verification/README.md` - Validation layer
- `rag/README.md` - RAG system
- `sandbox/README.md` - Sandboxing

---

## Questions?

This is a **pre-alpha** design. Everything is subject to change. If you're interested in contributing or have ideas, please open an issue!
