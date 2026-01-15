# Vibe-Genomer Project Structure

This document explains the complete directory structure of Vibe-Genomer.

```
Vibe-Genomer/
│
├── vibe_genomer/                    # Main Python package
│   ├── __init__.py                  # Package initialization
│   │
│   ├── agent/                       # 🧠 The "Brain" - Core agent logic
│   │   ├── __init__.py
│   │   ├── README.md                # Agent architecture documentation
│   │   ├── core.py                  # Main GenomicAgent class
│   │   ├── planner.py               # Multi-step workflow planning
│   │   ├── executor.py              # Tool execution orchestration
│   │   ├── react_loop.py            # ReAct (Reasoning + Acting) pattern
│   │   └── state_machine.py         # Conversation state management
│   │
│   ├── tools/                       # 🔧 Bioinformatics tool integrations
│   │   ├── __init__.py
│   │   ├── README.md                # Tool wrapper documentation
│   │   ├── base.py                  # Base BioinformaticsTool class
│   │   ├── samtools/                # SAMtools wrappers (BAM/SAM/CRAM)
│   │   │   ├── __init__.py
│   │   │   ├── view.py              # samtools view
│   │   │   ├── sort.py              # samtools sort
│   │   │   ├── index.py             # samtools index
│   │   │   └── stats.py             # samtools stats
│   │   ├── bedtools/                # BEDtools wrappers (intervals)
│   │   │   ├── __init__.py
│   │   │   ├── intersect.py         # bedtools intersect
│   │   │   ├── merge.py             # bedtools merge
│   │   │   └── coverage.py          # bedtools coverage
│   │   ├── bcftools/                # BCFtools wrappers (VCF/BCF)
│   │   │   ├── __init__.py
│   │   │   ├── query.py             # bcftools query
│   │   │   ├── filter.py            # bcftools filter
│   │   │   └── annotate.py          # bcftools annotate
│   │   ├── nextflow/                # Nextflow pipeline integration
│   │   │   ├── __init__.py
│   │   │   └── runner.py            # Nextflow workflow executor
│   │   └── custom/                  # Vibe-specific tools
│   │       ├── __init__.py
│   │       ├── variant_context.py   # Extract variant context
│   │       ├── gene_lookup.py       # Fast gene coordinate lookups
│   │       └── qc_report.py         # Generate QC reports
│   │
│   ├── parsers/                     # 📄 Genomic file format handlers
│   │   ├── __init__.py
│   │   ├── README.md                # Parser documentation
│   │   ├── base.py                  # Base GenomicFileParser class
│   │   ├── vcf.py                   # VCF/BCF parser
│   │   ├── bam.py                   # BAM/SAM/CRAM parser
│   │   ├── fastq.py                 # FASTQ parser
│   │   ├── gff.py                   # GFF/GTF parser
│   │   └── bed.py                   # BED parser
│   │
│   ├── verification/                # ✅ Biological validation layer
│   │   ├── __init__.py
│   │   ├── README.md                # Verification system documentation
│   │   ├── base.py                  # Base BiologicalValidator class
│   │   ├── coordinate_validator.py  # Validate genomic coordinates
│   │   ├── variant_validator.py     # Validate variant calls
│   │   ├── reference_checker.py     # Cross-check with databases
│   │   └── constraints.py           # Biological sanity checks
│   │
│   ├── rag/                         # 🔍 RAG for large genomic files
│   │   ├── __init__.py
│   │   ├── README.md                # RAG system documentation
│   │   ├── indexer.py               # Build searchable indices
│   │   ├── chunker.py               # Chunk files semantically
│   │   ├── retriever.py             # Retrieve relevant context
│   │   └── embeddings.py            # Vector embeddings for search
│   │
│   ├── cli/                         # 💻 Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py                  # Main CLI entry point
│   │   ├── commands/                # CLI command implementations
│   │   │   ├── __init__.py
│   │   │   ├── analyze.py           # `vibe analyze` command
│   │   │   ├── auth.py              # `vibe auth` command
│   │   │   └── update.py            # `vibe update-knowledge` command
│   │   └── repl.py                  # Interactive REPL
│   │
│   ├── workflows/                   # 🔄 Multi-step pipeline templates
│   │   ├── __init__.py
│   │   ├── README.md                # Workflow system documentation
│   │   ├── base.py                  # Base Workflow class
│   │   ├── alignment.py             # Read alignment workflows
│   │   ├── variant_calling.py       # Variant discovery workflows
│   │   ├── qc.py                    # Quality control workflows
│   │   └── annotation.py            # Variant annotation workflows
│   │
│   ├── models/                      # 🤖 LLM provider integrations
│   │   ├── __init__.py
│   │   ├── base.py                  # Base LLM provider interface
│   │   ├── anthropic.py             # Anthropic Claude integration
│   │   ├── openai.py                # OpenAI GPT integration
│   │   └── local.py                 # Local model (Ollama) integration
│   │
│   ├── sandbox/                     # 🔒 Safe execution environment
│   │   ├── __init__.py
│   │   ├── README.md                # Sandboxing documentation
│   │   ├── base.py                  # Base SandboxRunner interface
│   │   ├── docker_runner.py         # Docker containerization
│   │   ├── singularity_runner.py    # Singularity containerization
│   │   └── security.py              # Command validation & filtering
│   │
│   ├── knowledge/                   # 📚 Genomic reference databases
│   │   ├── __init__.py
│   │   ├── README.md                # Knowledge base documentation
│   │   ├── base.py                  # Base database interface
│   │   ├── clinvar/                 # ClinVar integration
│   │   │   ├── __init__.py
│   │   │   ├── client.py            # ClinVar API/database client
│   │   │   └── cache.py             # Local ClinVar cache
│   │   ├── ensembl/                 # Ensembl integration
│   │   │   ├── __init__.py
│   │   │   ├── client.py            # Ensembl REST API client
│   │   │   └── cache.py             # Local Ensembl cache
│   │   └── ucsc/                    # UCSC Genome Browser integration
│   │       ├── __init__.py
│   │       ├── client.py            # UCSC API client
│   │       └── reference.py         # Reference genome handler
│   │
│   └── utils/                       # 🛠️ Common utilities
│       ├── __init__.py
│       ├── logging.py               # Logging configuration
│       ├── config.py                # Configuration management
│       ├── exceptions.py            # Custom exceptions
│       └── decorators.py            # Utility decorators
│
├── tests/                           # 🧪 Test suite
│   ├── __init__.py
│   ├── unit/                        # Unit tests
│   │   ├── test_agent.py
│   │   ├── test_parsers.py
│   │   ├── test_verification.py
│   │   └── ...
│   ├── integration/                 # Integration tests
│   │   ├── test_workflows.py
│   │   ├── test_tool_execution.py
│   │   └── ...
│   └── fixtures/                    # Test data fixtures
│       ├── sample.bam
│       ├── sample.vcf
│       ├── sample.fastq
│       └── ...
│
├── docs/                            # 📖 Documentation
│   ├── index.md                     # Documentation home
│   ├── guides/                      # User guides
│   │   ├── getting_started.md
│   │   ├── basic_usage.md
│   │   ├── advanced_workflows.md
│   │   └── contributing.md
│   ├── api/                         # API documentation
│   │   ├── agent.md
│   │   ├── tools.md
│   │   ├── parsers.md
│   │   └── ...
│   └── examples/                    # Usage examples
│       ├── alignment_example.md
│       ├── variant_calling_example.md
│       └── custom_workflow_example.md
│
├── config/                          # ⚙️ Configuration files
│   ├── default.yaml                 # Default configuration
│   ├── development.yaml             # Development settings
│   ├── production.yaml              # Production settings
│   └── schemas/                     # Configuration schemas
│       ├── agent_config.json
│       ├── tool_config.json
│       └── workflow_config.json
│
├── scripts/                         # 📜 Utility scripts
│   ├── setup_dev_env.sh             # Development environment setup
│   ├── download_references.sh       # Download reference genomes
│   ├── update_databases.sh          # Update knowledge databases
│   └── build_containers.sh          # Build Docker/Singularity images
│
├── examples/                        # 💡 Usage examples
│   ├── basic_alignment.sh           # Basic alignment example
│   ├── variant_discovery.sh         # Variant calling example
│   ├── custom_workflow.yaml         # Custom workflow definition
│   └── clinical_pipeline.sh         # Clinical analysis pipeline
│
├── benchmarks/                      # ⚡ Performance benchmarks
│   ├── indexing_benchmark.py        # RAG indexing performance
│   ├── parser_benchmark.py          # File parser performance
│   └── workflow_benchmark.py        # Workflow execution performance
│
├── .github/                         # GitHub-specific files
│   ├── workflows/                   # GitHub Actions
│   │   ├── ci.yml                   # Continuous integration
│   │   ├── tests.yml                # Test automation
│   │   └── release.yml              # Release automation
│   └── ISSUE_TEMPLATE/              # Issue templates
│
├── README.md                        # Project README
├── ARCHITECTURE.md                  # System architecture document
├── PROJECT_STRUCTURE.md             # This file
├── LICENSE                          # Apache 2.0 License
├── setup.py                         # Python package setup
├── pyproject.toml                   # Python project configuration
├── requirements.txt                 # Python dependencies
├── requirements-dev.txt             # Development dependencies
└── .gitignore                       # Git ignore rules
```

## Module Responsibilities

### Core Execution Flow

```
User Input (CLI)
    ↓
Agent (Brain)
    ↓
Planner → Executor → ReAct Loop
    ↓
Tools (Bioinformatics)
    ↓
Sandbox (Safe Execution)
    ↓
Verification (Validation)
    ↓
Response to User
```

### Supporting Systems

- **Parsers**: Understand genomic file formats
- **RAG**: Handle large files efficiently
- **Knowledge**: Access reference databases
- **Models**: Interface with LLM providers

## Design Patterns

### 1. **Base Classes**
Each major component has a base class:
- `BioinformaticsTool` (tools)
- `GenomicFileParser` (parsers)
- `BiologicalValidator` (verification)
- `SandboxRunner` (sandbox)
- `BaseLLMProvider` (models)

### 2. **Plugin Architecture**
New tools, parsers, and validators can be added by:
1. Inheriting from the base class
2. Implementing required methods
3. Registering in `__init__.py`

### 3. **Fail-Safe Verification**
Every operation passes through verification:
```python
result = tool.execute(...)
if not verifier.validate(result):
    raise ValidationError("Failed sanity check")
```

### 4. **Immutable References**
Reference genomes and databases are read-only by default.

## File Naming Conventions

- **Python modules**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase`
- **Functions**: `lowercase_with_underscores`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Test files**: `test_*.py`

## Documentation Standards

Every module should have:
1. **Docstring** at the top explaining purpose
2. **README.md** for complex modules
3. **Type hints** for all functions
4. **Examples** in docstrings

## Testing Strategy

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **Fixtures**: Real (but small) genomic files for testing
- **Property tests**: Use Hypothesis for robust testing

## Development Workflow

1. Read `ARCHITECTURE.md` for system design
2. Identify the module you want to contribute to
3. Read that module's `README.md`
4. Write tests first (TDD)
5. Implement the feature
6. Ensure all tests pass
7. Submit PR with clear description

## Questions?

- **For architecture**: See `ARCHITECTURE.md`
- **For specific modules**: See module-specific `README.md` files
- **For contributing**: See `docs/guides/contributing.md`
