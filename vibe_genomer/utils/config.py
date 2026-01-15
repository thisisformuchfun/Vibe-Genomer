"""
Configuration management for Vibe-Genomer.

This module handles loading, validating, and accessing configuration settings.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

from .exceptions import ConfigurationError, InvalidConfigError, MissingConfigError


@dataclass
class ModelConfig:
    """Configuration for LLM providers."""

    provider: str = "anthropic"  # anthropic, openai, local
    model_name: str = "claude-3-5-sonnet-20241022"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 4096
    timeout: int = 300


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution."""

    enabled: bool = True
    backend: str = "docker"  # docker, singularity, none
    image: str = "vibe-genomer:latest"
    memory_limit: str = "8G"
    cpu_limit: int = 4
    timeout: int = 3600
    allow_network: bool = True
    read_only_paths: list = field(default_factory=list)


@dataclass
class RAGConfig:
    """Configuration for RAG system."""

    enabled: bool = True
    chunk_size: int = 10000
    overlap: int = 1000
    embedding_model: str = "text-embedding-3-small"
    vector_store: str = "faiss"
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".vibe-genomer" / "rag_cache")


@dataclass
class KnowledgeConfig:
    """Configuration for knowledge bases."""

    cache_dir: Path = field(default_factory=lambda: Path.home() / ".vibe-genomer" / "knowledge")
    clinvar_enabled: bool = True
    ensembl_enabled: bool = True
    ucsc_enabled: bool = True
    update_interval_days: int = 30


@dataclass
class VerificationConfig:
    """Configuration for verification layer."""

    enabled: bool = True
    strict_mode: bool = False
    check_coordinates: bool = True
    check_variants: bool = True
    check_references: bool = True
    max_coordinate_size: int = 1_000_000_000


@dataclass
class Config:
    """Main configuration class."""

    # Core settings
    debug: bool = False
    verbose: bool = False
    log_level: str = "INFO"
    log_file: Optional[Path] = None

    # Component configurations
    model: ModelConfig = field(default_factory=ModelConfig)
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    knowledge: KnowledgeConfig = field(default_factory=KnowledgeConfig)
    verification: VerificationConfig = field(default_factory=VerificationConfig)

    # Paths
    config_dir: Path = field(default_factory=lambda: Path.home() / ".vibe-genomer")
    data_dir: Path = field(default_factory=lambda: Path.home() / ".vibe-genomer" / "data")

    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file."""
        if not config_path.exists():
            raise MissingConfigError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise InvalidConfigError(f"Invalid YAML in configuration file: {e}")

        return cls.from_dict(data or {})

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create configuration from dictionary."""
        config = cls()

        # Load basic settings
        config.debug = data.get("debug", config.debug)
        config.verbose = data.get("verbose", config.verbose)
        config.log_level = data.get("log_level", config.log_level)

        if log_file := data.get("log_file"):
            config.log_file = Path(log_file)

        # Load model config
        if model_data := data.get("model"):
            config.model = ModelConfig(**model_data)

        # Load sandbox config
        if sandbox_data := data.get("sandbox"):
            config.sandbox = SandboxConfig(**sandbox_data)

        # Load RAG config
        if rag_data := data.get("rag"):
            if "cache_dir" in rag_data:
                rag_data["cache_dir"] = Path(rag_data["cache_dir"])
            config.rag = RAGConfig(**rag_data)

        # Load knowledge config
        if knowledge_data := data.get("knowledge"):
            if "cache_dir" in knowledge_data:
                knowledge_data["cache_dir"] = Path(knowledge_data["cache_dir"])
            config.knowledge = KnowledgeConfig(**knowledge_data)

        # Load verification config
        if verification_data := data.get("verification"):
            config.verification = VerificationConfig(**verification_data)

        # Load paths
        if config_dir := data.get("config_dir"):
            config.config_dir = Path(config_dir)
        if data_dir := data.get("data_dir"):
            config.data_dir = Path(data_dir)

        return config

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        config = cls()

        # Model configuration from env
        if api_key := os.getenv("ANTHROPIC_API_KEY"):
            config.model.api_key = api_key
            config.model.provider = "anthropic"
        elif api_key := os.getenv("OPENAI_API_KEY"):
            config.model.api_key = api_key
            config.model.provider = "openai"

        if model_name := os.getenv("VIBE_MODEL"):
            config.model.model_name = model_name

        # Debug mode
        if os.getenv("VIBE_DEBUG"):
            config.debug = True
            config.log_level = "DEBUG"

        return config

    def validate(self) -> None:
        """Validate configuration."""
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.rag.cache_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge.cache_dir.mkdir(parents=True, exist_ok=True)

        # Validate model config
        if not self.model.api_key and self.model.provider != "local":
            raise MissingConfigError(
                f"API key required for provider '{self.model.provider}'. "
                f"Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable."
            )

        # Validate sandbox config
        if self.sandbox.enabled and self.sandbox.backend not in ["docker", "singularity", "none"]:
            raise InvalidConfigError(
                f"Invalid sandbox backend: {self.sandbox.backend}. "
                f"Must be one of: docker, singularity, none"
            )


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration with priority:
    1. Provided config file
    2. User config file (~/.vibe-genomer/config.yaml)
    3. Environment variables
    4. Default values
    """
    # Start with defaults and environment
    config = Config.from_env()

    # Try to load from file
    if config_path is None:
        config_path = Path.home() / ".vibe-genomer" / "config.yaml"

    if config_path.exists():
        file_config = Config.from_file(config_path)
        # Merge configs (file overrides env)
        config = file_config
        # But preserve API keys from env if not in file
        if not config.model.api_key:
            env_config = Config.from_env()
            config.model.api_key = env_config.model.api_key

    # Validate final configuration
    config.validate()

    return config
