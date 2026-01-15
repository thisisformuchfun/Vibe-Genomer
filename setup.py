"""
Vibe-Genomer Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme = Path(__file__).parent / "README.md"
long_description = readme.read_text(encoding="utf-8") if readme.exists() else ""

setup(
    name="vibe-genomer",
    version="0.1.0",
    description="The Claude Code for Genomics - An autonomous genomic agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Vibe-Genomer Contributors",
    author_email="",
    url="https://github.com/yourusername/vibe-genomer",
    license="Apache 2.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "anthropic>=0.18.0",
        "openai>=1.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
        "pydantic>=2.0.0",
        "httpx>=0.25.0",
        "pysam>=0.21.0",  # BAM/VCF parsing
        "biopython>=1.81",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "langchain>=0.1.0",
        "langgraph>=0.0.1",
        "faiss-cpu>=1.7.4",  # Vector search
        "docker>=7.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "hypothesis>=6.82.0",
            "black>=23.7.0",
            "ruff>=0.0.280",
            "mypy>=1.4.0",
            "pre-commit>=3.3.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.1.0",
            "mkdocstrings[python]>=0.22.0",
        ],
        "local": [
            "ollama>=0.1.0",
            "llama-cpp-python>=0.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vibe=vibe_genomer.cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="genomics bioinformatics ai agent llm claude automation",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/vibe-genomer/issues",
        "Source": "https://github.com/yourusername/vibe-genomer",
        "Documentation": "https://vibe-genomer.readthedocs.io/",
    },
)
