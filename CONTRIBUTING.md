# Contributing to Vibe-Genomer

Thank you for your interest in contributing to Vibe-Genomer! This document provides guidelines and information for contributors.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How Can I Contribute?](#how-can-i-contribute)
3. [Development Setup](#development-setup)
4. [Project Structure](#project-structure)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Submitting Changes](#submitting-changes)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Prioritize the project's scientific integrity

## How Can I Contribute?

### 1. Bioinformaticians ("Ground Truth")

**Build the verification layer** - LLMs hallucinate; we need validators.

**Tasks**:
- Implement coordinate validators
- Add variant validation logic
- Create biological constraint checks
- Build database cross-reference tools

**Example contribution**:
```python
# vibe_genomer/verification/structural_variant_validator.py
class SVValidator(BiologicalValidator):
    def validate_deletion(self, chrom, start, end, ref_genome):
        """Validate a deletion makes biological sense"""
        # Check coordinates are in bounds
        # Verify deletion size is reasonable
        # Cross-check with known SVs
```

### 2. LLM/Agent Engineers ("Brain")

**Build the agent system** - Tool use, context management, planning.

**Tasks**:
- Implement ReAct loops
- Build workflow planners
- Create RAG indexing for large files
- Optimize token usage

**Example contribution**:
```python
# vibe_genomer/agent/planner.py
class WorkflowPlanner:
    def decompose_request(self, user_query: str) -> List[Step]:
        """Break complex requests into executable steps"""
        # Use LLM to generate plan
        # Validate plan makes sense
        # Return ordered steps
```

### 3. Systems Engineers ("Plumbing")

**Build the sandboxing layer** - Safe, isolated execution.

**Tasks**:
- Implement Docker/Singularity runners
- Build command validators
- Create resource limits
- Add audit logging

**Example contribution**:
```python
# vibe_genomer/sandbox/docker_runner.py
class DockerRunner(SandboxRunner):
    def execute(self, command: str, **kwargs) -> Result:
        """Execute command in isolated container"""
        # Validate command is safe
        # Set up volume mounts (read-only refs)
        # Run with resource limits
        # Capture output
```

### 4. Tool Integration

**Wrap bioinformatics tools** - Make them agent-friendly.

**Tasks**:
- Create tool wrappers (samtools, bedtools, etc.)
- Parse tool outputs into structured data
- Handle errors gracefully
- Write integration tests

**Example contribution**:
```python
# vibe_genomer/tools/samtools/depth.py
class SamtoolsDepth(BioinformaticsTool):
    def execute(self, bam_file: str, region: str) -> CoverageResult:
        """Calculate coverage depth for a region"""
        cmd = f"samtools depth -r {region} {bam_file}"
        output = self.run_command(cmd)
        return self.parse_output(output)
```

## Development Setup

### Prerequisites

- Python 3.10+
- Docker (for sandboxing)
- Git

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/yourusername/vibe-genomer.git
cd vibe-genomer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests to verify setup
pytest
```

## Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed layout.

Key directories:
- `vibe_genomer/agent/` - Core agent logic
- `vibe_genomer/tools/` - Bioinformatics tool wrappers
- `vibe_genomer/verification/` - Validation layer
- `vibe_genomer/rag/` - RAG system for large files
- `tests/` - Test suite

## Coding Standards

### Python Style

We follow PEP 8 with some modifications:

```python
# Use Black for formatting (100 char line length)
black vibe_genomer/

# Use Ruff for linting
ruff check vibe_genomer/

# Use MyPy for type checking
mypy vibe_genomer/
```

### Type Hints

**Always use type hints**:

```python
def validate_coordinates(
    chrom: str,
    start: int,
    end: int,
    genome_build: str = "hg38"
) -> bool:
    """Validate genomic coordinates."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def align_reads(fastq_files: List[str], reference: str) -> str:
    """Align FASTQ reads to reference genome.

    Args:
        fastq_files: List of FASTQ file paths
        reference: Path to reference genome FASTA

    Returns:
        Path to output BAM file

    Raises:
        FileNotFoundError: If FASTQ or reference doesn't exist
        AlignmentError: If alignment fails
    """
    ...
```

### Error Handling

Create custom exceptions:

```python
# vibe_genomer/utils/exceptions.py
class GenomicError(Exception):
    """Base exception for genomic operations"""

class CoordinateError(GenomicError):
    """Invalid genomic coordinates"""

class ValidationError(GenomicError):
    """Biological validation failed"""
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/              # Fast, isolated tests
├── integration/       # Multi-component tests
└── fixtures/          # Test data
```

### Writing Tests

```python
import pytest
from vibe_genomer.verification import CoordinateValidator

def test_coordinate_validator_valid():
    """Test valid coordinates pass validation"""
    validator = CoordinateValidator(genome_build="hg38")
    assert validator.validate("chr1", 1000000, 2000000) is True

def test_coordinate_validator_invalid_chrom():
    """Test invalid chromosome fails validation"""
    validator = CoordinateValidator(genome_build="hg38")
    with pytest.raises(CoordinateError):
        validator.validate("chr99", 1000000, 2000000)
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_verification.py

# Run with coverage
pytest --cov=vibe_genomer --cov-report=html

# Run only fast tests (skip slow/integration)
pytest -m "not slow"
```

## Submitting Changes

### Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Write tests**
5. **Run tests and linting**
   ```bash
   pytest
   black vibe_genomer/
   ruff check vibe_genomer/
   mypy vibe_genomer/
   ```
6. **Commit with clear messages**
   ```bash
   git commit -m "Add coordinate validator for hg38"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Open a Pull Request**

### PR Guidelines

**Good PR**:
- Clear title and description
- References related issues
- Includes tests
- Passes all CI checks
- Updates documentation if needed

**PR Description Template**:
```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes Made
- Added X
- Modified Y
- Fixed Z

## Testing
How was this tested?

## Checklist
- [ ] Tests pass locally
- [ ] Code is formatted (black)
- [ ] Code is linted (ruff)
- [ ] Type hints added (mypy clean)
- [ ] Documentation updated
```

## Getting Help

- **Questions?** Open a GitHub Discussion
- **Bugs?** Open an Issue
- **Chat?** Join our [Discord/Slack]

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Acknowledged in relevant modules

---

**Thank you for contributing to Vibe-Genomer!**

Together, we're building the future of genomic analysis.
