"""
Custom exceptions for Vibe-Genomer.

This module defines all custom exception classes used throughout the application.
"""

from typing import Optional


class VibeGenomerError(Exception):
    """Base exception for all Vibe-Genomer errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


# Agent Errors
class AgentError(VibeGenomerError):
    """Base exception for agent-related errors."""
    pass


class PlanningError(AgentError):
    """Raised when the agent fails to create a valid execution plan."""
    pass


class ExecutionError(AgentError):
    """Raised when tool execution fails."""
    pass


class StateError(AgentError):
    """Raised when state management encounters an issue."""
    pass


# Tool Errors
class ToolError(VibeGenomerError):
    """Base exception for bioinformatics tool errors."""
    pass


class ToolNotFoundError(ToolError):
    """Raised when a required bioinformatics tool is not available."""
    pass


class ToolExecutionError(ToolError):
    """Raised when a tool execution fails."""
    pass


class ToolConfigurationError(ToolError):
    """Raised when tool configuration is invalid."""
    pass


# Parser Errors
class ParserError(VibeGenomerError):
    """Base exception for file parsing errors."""
    pass


class InvalidFileFormatError(ParserError):
    """Raised when a file format is invalid or corrupted."""
    pass


class UnsupportedFormatError(ParserError):
    """Raised when attempting to parse an unsupported file format."""
    pass


# Verification Errors
class VerificationError(VibeGenomerError):
    """Base exception for biological verification errors."""
    pass


# Alias for backward compatibility with tests
ValidationError = VerificationError


class CoordinateValidationError(VerificationError):
    """Raised when genomic coordinates are invalid."""
    pass


class VariantValidationError(VerificationError):
    """Raised when a variant fails validation."""
    pass


class ReferenceCheckError(VerificationError):
    """Raised when reference database checks fail."""
    pass


class BiologicalConstraintError(VerificationError):
    """Raised when biological constraints are violated."""
    pass


# Sandbox Errors
class SandboxError(VibeGenomerError):
    """Base exception for sandbox execution errors."""
    pass


class SecurityViolationError(SandboxError):
    """Raised when a security policy is violated."""
    pass


class ResourceLimitError(SandboxError):
    """Raised when resource limits are exceeded."""
    pass


class ContainerError(SandboxError):
    """Raised when container operations fail."""
    pass


# RAG Errors
class RAGError(VibeGenomerError):
    """Base exception for RAG system errors."""
    pass


class IndexingError(RAGError):
    """Raised when file indexing fails."""
    pass


class RetrievalError(RAGError):
    """Raised when context retrieval fails."""
    pass


class EmbeddingError(RAGError):
    """Raised when vector embedding generation fails."""
    pass


# Knowledge Base Errors
class KnowledgeBaseError(VibeGenomerError):
    """Base exception for knowledge base errors."""
    pass


class DatabaseConnectionError(KnowledgeBaseError):
    """Raised when database connection fails."""
    pass


class QueryError(KnowledgeBaseError):
    """Raised when a database query fails."""
    pass


class CacheError(KnowledgeBaseError):
    """Raised when cache operations fail."""
    pass


# Model Errors
class ModelError(VibeGenomerError):
    """Base exception for LLM provider errors."""
    pass


class ModelNotAvailableError(ModelError):
    """Raised when a requested model is not available."""
    pass


class APIError(ModelError):
    """Raised when an API call to an LLM provider fails."""
    pass


class TokenLimitError(ModelError):
    """Raised when token limits are exceeded."""
    pass


# Configuration Errors
class ConfigurationError(VibeGenomerError):
    """Base exception for configuration errors."""
    pass


class InvalidConfigError(ConfigurationError):
    """Raised when configuration is invalid."""
    pass


class MissingConfigError(ConfigurationError):
    """Raised when required configuration is missing."""
    pass


# CLI Errors
class CLIError(VibeGenomerError):
    """Base exception for CLI-related errors."""
    pass


class InvalidCommandError(CLIError):
    """Raised when an invalid command is provided."""
    pass


class AuthenticationError(CLIError):
    """Raised when authentication fails."""
    pass
