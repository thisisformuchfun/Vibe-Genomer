"""
Base LLM provider interface.

This module defines the abstract base class for all LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, AsyncIterator
from enum import Enum


class MessageRole(Enum):
    """Message roles in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """A message in a conversation."""

    role: MessageRole
    content: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "role": self.role.value,
            "content": self.content,
        }


@dataclass
class ModelResponse:
    """Response from an LLM."""

    content: str
    model: str
    stop_reason: str
    usage: Dict[str, int]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All LLM providers (Anthropic, OpenAI, local) must implement this interface.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "default",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        timeout: int = 300,
        **kwargs,
    ):
        """
        Initialize the LLM provider.

        Args:
            api_key: API key for the provider (if required)
            model_name: Name of the model to use
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            **kwargs: Additional provider-specific parameters
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.extra_params = kwargs

    @abstractmethod
    def complete(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        **kwargs,
    ) -> ModelResponse:
        """
        Generate a completion from the model.

        Args:
            messages: List of conversation messages
            system: Optional system prompt
            **kwargs: Additional parameters for this request

        Returns:
            Model response

        Raises:
            APIError: If the API call fails
            TokenLimitError: If token limits are exceeded
        """
        pass

    @abstractmethod
    async def complete_async(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        **kwargs,
    ) -> ModelResponse:
        """
        Generate a completion asynchronously.

        Args:
            messages: List of conversation messages
            system: Optional system prompt
            **kwargs: Additional parameters for this request

        Returns:
            Model response
        """
        pass

    @abstractmethod
    def stream(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """
        Stream completion tokens from the model.

        Args:
            messages: List of conversation messages
            system: Optional system prompt
            **kwargs: Additional parameters for this request

        Yields:
            Content chunks as they are generated
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the provider is properly configured.

        Returns:
            True if configuration is valid

        Raises:
            ConfigurationError: If configuration is invalid
        """
        pass

    def format_genomic_context(
        self,
        file_type: str,
        context: str,
        question: str,
    ) -> str:
        """
        Format genomic context into a prompt.

        Args:
            file_type: Type of genomic file (VCF, BAM, etc.)
            context: Relevant context from the file
            question: User's question

        Returns:
            Formatted prompt
        """
        return f"""You are analyzing a {file_type} file. Here is the relevant context:

```
{context}
```

User question: {question}

Please provide a detailed analysis, including:
1. What the data shows
2. Any notable findings or patterns
3. Biological interpretation
4. Recommendations for next steps

Remember to:
- Use proper genomic terminology
- Validate coordinates and references
- Consider biological constraints
- Explain your reasoning
"""

    def format_tool_execution(
        self,
        tool_name: str,
        description: str,
        parameters: Dict[str, Any],
    ) -> str:
        """
        Format a tool execution request.

        Args:
            tool_name: Name of the tool to execute
            description: Description of what the tool does
            parameters: Tool parameters

        Returns:
            Formatted prompt
        """
        params_str = "\n".join(f"- {k}: {v}" for k, v in parameters.items())
        return f"""Execute the following bioinformatics tool:

Tool: {tool_name}
Description: {description}

Parameters:
{params_str}

Please:
1. Construct the correct command
2. Validate the parameters
3. Explain what the command will do
4. Execute it safely
"""
