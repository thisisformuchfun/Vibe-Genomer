"""
OpenAI GPT provider implementation.
"""

from typing import List, Optional, AsyncIterator
from openai import OpenAI, AsyncOpenAI
import tiktoken

from .base import BaseLLMProvider, Message, ModelResponse, MessageRole
from ..utils import get_logger, APIError, TokenLimitError, MissingConfigError


class OpenAIProvider(BaseLLMProvider):
    """LLM provider for OpenAI's GPT models."""

    DEFAULT_MODEL = "gpt-4o"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        timeout: int = 300,
        **kwargs,
    ):
        """Initialize OpenAI provider."""
        super().__init__(
            api_key=api_key,
            model_name=model_name or self.DEFAULT_MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            **kwargs,
        )
        self.logger = get_logger()
        self.client: Optional[OpenAI] = None
        self.async_client: Optional[AsyncOpenAI] = None
        self.tokenizer = None

        if self.api_key:
            self._initialize_clients()

    def _initialize_clients(self):
        """Initialize OpenAI clients."""
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                timeout=self.timeout,
            )
            self.async_client = AsyncOpenAI(
                api_key=self.api_key,
                timeout=self.timeout,
            )

            # Initialize tokenizer for accurate token counting
            try:
                self.tokenizer = tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                # Fall back to default encoding if model not found
                self.tokenizer = tiktoken.get_encoding("cl100k_base")

        except Exception as e:
            raise APIError(f"Failed to initialize OpenAI client: {e}")

    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        if not self.api_key:
            raise MissingConfigError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable."
            )

        if not self.client:
            self._initialize_clients()

        return True

    def _convert_messages(self, messages: List[Message], system: Optional[str] = None) -> List[dict]:
        """Convert internal messages to OpenAI format."""
        converted = []

        # Add system message first if provided
        if system:
            converted.append({
                "role": "system",
                "content": system,
            })

        # Add conversation messages
        for msg in messages:
            if msg.role != MessageRole.SYSTEM:  # Skip system messages (already handled)
                converted.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })
            elif not system:  # Use system message if not provided separately
                converted.insert(0, {
                    "role": "system",
                    "content": msg.content,
                })

        return converted

    def complete(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        **kwargs,
    ) -> ModelResponse:
        """Generate completion using GPT."""
        self.validate_config()

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self._convert_messages(messages, system),
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs,
            )

            return ModelResponse(
                content=response.choices[0].message.content,
                model=response.model,
                stop_reason=response.choices[0].finish_reason,
                usage={
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                metadata={"id": response.id},
            )

        except Exception as e:
            error_str = str(e).lower()
            if "context_length_exceeded" in error_str or "maximum context length" in error_str:
                raise TokenLimitError(f"Token limit exceeded: {e}")
            raise APIError(f"OpenAI API error: {e}")

    async def complete_async(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        **kwargs,
    ) -> ModelResponse:
        """Generate completion asynchronously."""
        self.validate_config()

        try:
            response = await self.async_client.chat.completions.create(
                model=self.model_name,
                messages=self._convert_messages(messages, system),
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs,
            )

            return ModelResponse(
                content=response.choices[0].message.content,
                model=response.model,
                stop_reason=response.choices[0].finish_reason,
                usage={
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                metadata={"id": response.id},
            )

        except Exception as e:
            error_str = str(e).lower()
            if "context_length_exceeded" in error_str:
                raise TokenLimitError(f"Token limit exceeded: {e}")
            raise APIError(f"OpenAI API error: {e}")

    async def stream(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion tokens."""
        self.validate_config()

        try:
            stream = await self.async_client.chat.completions.create(
                model=self.model_name,
                messages=self._convert_messages(messages, system),
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
                **kwargs,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise APIError(f"Streaming error: {e}")

    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        if not self.tokenizer:
            self._initialize_clients()

        return len(self.tokenizer.encode(text))

    def get_model_info(self) -> dict:
        """Get information about the current model."""
        model_info = {
            "gpt-4o": {
                "context_window": 128_000,
                "max_output": 16_384,
                "description": "Most capable GPT-4 model",
            },
            "gpt-4o-mini": {
                "context_window": 128_000,
                "max_output": 16_384,
                "description": "Affordable small model for fast tasks",
            },
            "gpt-4-turbo": {
                "context_window": 128_000,
                "max_output": 4_096,
                "description": "Previous GPT-4 Turbo model",
            },
        }
        return model_info.get(self.model_name, {
            "context_window": 128_000,
            "max_output": 4_096,
            "description": "Unknown model",
        })
