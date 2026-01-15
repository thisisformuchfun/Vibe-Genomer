# Vibe-Genomer

**The "Claude Code" for Genomics.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/Status-Pre--Alpha-orange)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()

## The Mission

We are building the **Autonomous Genomic Agent**.

Bioinformatics is stuck in a loop of manual piping, dependency hell, and fragile bash scripts. **Vibe-Genomer** breaks this loop. It is an agentic CLI—similar to Claude Code or OpenAI Codex—but deeply trained on the syntax of biology.

You don't write the pipeline; you define the *intent*.
> **User:** "Analyze this BAM file for large deletions in the BRCA1 region and cross-reference with ClinVar."
> **Vibe-Genomer:** *Parses file headers -> Generates filtering strategy -> Runs `samtools` & `bcftools` -> queries API -> Returns summarized report.*

## Core Philosophy

We are moving from **imperative** ("run this awk command") to **declarative** ("find these variants").
* **Agentic Execution:** The tool plans a multi-step workflow, executes it in your shell, and self-corrects if a tool fails.
* **Biologically Aware:** It understands that `chr1` and `1` are the same chromosome, and that a VCF header is not just a comment.
* **Privacy First:** Like the best CLI agents, it runs locally where possible, keeping sensitive patient data off public cloud inference wherever you choose.

## Architecture

```
User (CLI) → Agent (Brain) → [Planner → Executor → ReAct Loop → State Machine]
                    ↓
    Tools (samtools, bedtools, bcftools)
    Parsers (VCF, BAM, FASTQ)
    RAG (for large files)
    Knowledge (ClinVar, Ensembl, UCSC)
                    ↓
    Verification (Ground Truth Validation)
                    ↓
    Sandbox (Docker/Singularity - controlled execution)
```

### Module Overview

| Module | Description | Status |
|--------|-------------|--------|
| **Agent** | Planner, Executor, ReAct loop, State machine | Implemented |
| **Parsers** | VCF, BAM, FASTQ with semantic understanding | Implemented |
| **Verification** | Coordinate, variant, and constraint validators | Implemented |
| **Tools** | samtools, bedtools, bcftools wrappers | Partial |
| **RAG** | Retrieval for large genomic files | Framework |
| **Knowledge** | ClinVar, Ensembl, UCSC integrations | Framework |
| **Sandbox** | Docker/Singularity execution isolation | Framework |

## Tech Stack

* **Core Logic:** Python 3.10+ (Bridge between LLM and Shell)
* **Agent Framework:** LangGraph / Custom ReAct Loop (The "Brain")
* **Genomics:** pysam, biopython (File parsing and biological operations)
* **Integrations:** `samtools`, `bedtools`, `bcftools`, `nextflow`
* **Model Support:** Agnostic (Claude 3.5 Sonnet, GPT-4o, DeepSeek-Coder, Local via Ollama)

## Implemented Features

### Biological Verification Layer
The verification layer validates agent outputs against biological ground truth—critical because a hallucinated SNP could mean a misdiagnosis.

- **Coordinate Validator**: Validates genomic coordinates exist in reference, positions within bounds, correct genome build (hg19/hg38)
- **Variant Validator**: Validates REF alleles match reference, ALT alleles are valid DNA, ClinVar cross-reference
- **Constraint Checker**: Enforces biological sanity (GC content 0-1, PHRED scores 0-60, coverage non-negative)
- **Reference Checker**: Cross-references Ensembl, RefSeq, ClinVar, HGVS nomenclature

Validation severity levels: CRITICAL (patient implications), HIGH (technical artifact), MEDIUM (incomplete report), LOW (formatting)

### Genomic File Parsers
Biologically-aware parsers that understand file semantics, not just text:

- **VCF Parser**: Headers, multi-allelic sites, INFO/FORMAT fields, annotations
- **BAM Parser**: Headers, read groups, streaming by region, CIGAR operations
- **FASTQ Parser**: Quality scores, read distribution, paired-end support

Key design: Never loads entire files into memory—efficient streaming and indexing for 100GB+ files.

### Agent Core
- **Planner**: Decomposes complex requests into multi-step workflows
- **Executor**: Runs individual tools with error handling and retries
- **ReAct Loop**: Implements Reasoning + Acting pattern for autonomous operation
- **State Machine**: Manages conversation state and context

### Tool Wrappers
Standardized interfaces for bioinformatics tools with input validation, error handling, and structured output:
- samtools (view, index, sort, stats)
- bedtools (framework)
- bcftools (framework)

## Call for Experts

We are building the foundational "OS" for genomic agents. We need contributors who can bridge the gap between LLM reasoning and biological ground truth.

### 1. Bioinformaticians (The "Ground Truth")
Extend the **verification layer**.
* *Challenge:* LLMs hallucinate. In biology, a hallucinated SNP is a misdiagnosis.
* *Task:* Add more validators and biological constraints beyond what's implemented.

### 2. LLM / Agent Engineers (The "Brain")
Build the **RAG system** for large files.
* *Challenge:* Genomic files are massive (100GB+ BAMs). You can't put them in the context window.
* *Task:* Implement the RAG indexer/retriever that lets the agent "read" binary genomic files without loading them whole.

### 3. Systems Engineers (The "Plumbing")
Implement **sandboxing**.
* *Challenge:* An agent running shell commands is dangerous.
* *Task:* Build Docker/Singularity runners that prevent the agent from accidentally `rm -rf /` your cluster.

## Quick Start (Pre-Alpha)

**Requirements:** Python 3.10+

1.  **Install:**
    ```bash
    pip install vibe-genomer
    ```
2.  **Authenticate (Bring your own API key):**
    ```bash
    vibe auth --provider anthropic
    ```
3.  **Run:**
    ```bash
    vibe "Take the fastq files in /data, align them to hg38, and give me a QC report."
    ```

**CLI Commands:**
```bash
vibe "..."                       # One-shot analysis
vibe auth --provider anthropic   # Set up authentication
vibe repl                        # Interactive REPL (planned)
vibe update-knowledge --all      # Update local databases
vibe info                        # Show configuration
```

## Development

```bash
# Clone and install dev dependencies
git clone https://github.com/thisisformuchfun/Vibe-Genomer.git
cd Vibe-Genomer
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=vibe_genomer --cov-report=html

# Type checking
mypy vibe_genomer

# Linting
ruff check vibe_genomer
```

### Configuration

Configuration files in `config/`:
- `default.yaml`: Production settings
- `development.yaml`: Development/testing settings

Key settings: agent behavior, LLM provider, tool timeouts, verification strictness, sandbox controls.

## Roadmap

- [x] **Phase 1:** CLI Agent that translates Natural Language to `samtools`/`bedtools` one-liners
- [x] **Phase 1:** Biological verification layer (coordinate, variant, constraint validators)
- [x] **Phase 1:** Genomic file parsers (VCF, BAM, FASTQ)
- [ ] **Phase 2:** "Planner" module for multi-step workflows (e.g., Alignment -> Sorting -> Calling) — *in progress*
- [ ] **Phase 2:** RAG system for large file handling
- [ ] **Phase 3:** Interactive REPL (Read-Eval-Print Loop) for iterative data exploration
- [ ] **Phase 4:** Local Model Support (Ollama integration) for fully offline analysis

## License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.
