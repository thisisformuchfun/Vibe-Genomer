# Vibe-Genomer Documentation

Welcome to **Vibe-Genomer** - the Claude Code for Genomics.

## What is Vibe-Genomer?

Vibe-Genomer is an autonomous genomic agent that translates natural language requests into executable bioinformatics workflows. Instead of writing complex bash pipelines, you simply describe what you want to do:

```bash
vibe "Align these FASTQ files to hg38 and give me a QC report"
vibe "Find pathogenic variants in BRCA1 from my VCF"
vibe "What's the average coverage in exonic regions?"
```

## Key Features

- **Natural Language Interface**: Describe your analysis goals in plain English
- **Biological Awareness**: Understands genomic semantics (chr1 == 1, coordinate systems, etc.)
- **Verification Layer**: Validates all genomic claims against biological constraints
- **Safety First**: Sandboxed execution prevents dangerous operations
- **Efficient**: RAG system handles 100GB+ files without loading them into memory
- **Flexible**: Supports multiple LLM providers (Claude, GPT-4, local models)

## Quick Links

- [Getting Started](guides/getting_started.md)
- [Architecture Overview](../ARCHITECTURE.md)
- [Project Structure](../PROJECT_STRUCTURE.md)
- [API Reference](api/)
- [Examples](examples/)

## Installation

```bash
pip install vibe-genomer
```

## Basic Usage

```bash
# One-shot command
vibe "Analyze sample.bam for variants in TP53"

# Interactive mode
vibe repl
```

## Documentation Sections

### Guides
- [Getting Started](guides/getting_started.md) - First steps with Vibe-Genomer
- [Basic Usage](guides/basic_usage.md) - Common operations
- [Advanced Workflows](guides/advanced_workflows.md) - Complex analyses
- [Contributing](guides/contributing.md) - How to contribute

### API Reference
- [Agent](api/agent.md) - Core agent system
- [Tools](api/tools.md) - Bioinformatics tool wrappers
- [Parsers](api/parsers.md) - File format handlers
- [Verification](api/verification.md) - Validation system
- [RAG](api/rag.md) - Retrieval system

### Examples
- [Alignment Workflow](examples/alignment_example.md)
- [Variant Calling](examples/variant_calling_example.md)
- [Custom Workflows](examples/custom_workflow_example.md)

## Architecture

Vibe-Genomer follows a modular architecture:

```
User → CLI → Agent → [Tools, Parsers, RAG, Knowledge]
                  ↓
              Verification
                  ↓
              Sandbox → Shell
```

See [ARCHITECTURE.md](../ARCHITECTURE.md) for detailed system design.

## Contributing

We welcome contributions! See [Contributing Guide](guides/contributing.md).

## License

Apache 2.0 - See [LICENSE](../LICENSE)

## Status

**Pre-Alpha** - Under active development. APIs may change.
