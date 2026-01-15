# Agent Module

The **Agent** is the "brain" of Vibe-Genomer. It translates natural language requests into executable bioinformatics workflows.

## Architecture

### Core Components

1. **`core.py`** - Main `GenomicAgent` class that orchestrates the entire system
2. **`planner.py`** - Decomposes complex requests into multi-step plans
3. **`executor.py`** - Executes individual tools and handles errors
4. **`react_loop.py`** - Implements the ReAct (Reasoning + Acting) pattern
5. **`state_machine.py`** - Manages conversation state and context

## Example Flow

```
User: "Analyze this BAM file for large deletions in BRCA1"
  ↓
Planner: [Parse BAM → Filter BRCA1 → Detect SVs → Validate → Report]
  ↓
Executor: Runs samtools view | bcftools query | custom_validator
  ↓
Verification: Checks coordinates are valid, variants make sense
  ↓
Response: "Found 3 large deletions in BRCA1, coordinates validated"
```

## Integration Points

- **Tools Module**: Calls bioinformatics tool wrappers
- **Parsers Module**: Understands file formats
- **Verification Module**: Validates biological constraints
- **RAG Module**: Retrieves relevant context from large files
- **Models Module**: Interfaces with LLM providers
