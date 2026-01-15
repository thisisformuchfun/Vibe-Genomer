"""
Anthropic Claude provider implementation.
"""

from typing import List, Optional, AsyncIterator
import anthropic
from anthropic import Anthropic, AsyncAnthropic

from .base import BaseLLMProvider, Message, ModelResponse, MessageRole
from ..utils import get_logger, APIError, TokenLimitError, MissingConfigError


class AnthropicProvider(BaseLLMProvider):
    """LLM provider for Anthropic's Claude models."""

    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        timeout: int = 300,
        **kwargs,
    ):
        """Initialize Anthropic provider."""
        super().__init__(
            api_key=api_key,
            model_name=model_name or self.DEFAULT_MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            **kwargs,
        )
        self.logger = get_logger()
        self.client: Optional[Anthropic] = None
        self.async_client: Optional[AsyncAnthropic] = None

        if self.api_key:
            self._initialize_clients()

    def _initialize_clients(self):
        """Initialize Anthropic clients."""
        try:
            self.client = Anthropic(
                api_key=self.api_key,
                timeout=self.timeout,
            )
            self.async_client = AsyncAnthropic(
                api_key=self.api_key,
                timeout=self.timeout,
            )
        except Exception as e:
            raise APIError(f"Failed to initialize Anthropic client: {e}")

    def validate_config(self) -> bool:
        """Validate Anthropic configuration."""
        if not self.api_key:
            raise MissingConfigError(
                "Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable."
            )

        if not self.client:
            self._initialize_clients()

        return True

    def _convert_messages(self, messages: List[Message]) -> List[dict]:
        """Convert internal messages to Anthropic format."""
        converted = []
        for msg in messages:
            if msg.role != MessageRole.SYSTEM:  # System messages handled separately
                converted.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })
        return converted

    def complete(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        **kwargs,
    ) -> ModelResponse:
        """Generate completion using Claude."""
        self.validate_config()

        # Extract system message if present
        system_prompt = system
        if not system_prompt and messages and messages[0].role == MessageRole.SYSTEM:
            system_prompt = messages[0].content
            messages = messages[1:]

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt or "",
                messages=self._convert_messages(messages),
                **kwargs,
            )

            return ModelResponse(
                content=response.content[0].text,
                model=response.model,
                stop_reason=response.stop_reason,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                metadata={"id": response.id},
            )

        except anthropic.BadRequestError as e:
            if "maximum context length" in str(e).lower():
                raise TokenLimitError(f"Token limit exceeded: {e}")
            raise APIError(f"Bad request to Anthropic API: {e}")

        except anthropic.AuthenticationError as e:
            raise APIError(f"Authentication failed: {e}")

        except anthropic.RateLimitError as e:
            raise APIError(f"Rate limit exceeded: {e}")

        except Exception as e:
            raise APIError(f"Anthropic API error: {e}")

    async def complete_async(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        **kwargs,
    ) -> ModelResponse:
        """Generate completion asynchronously."""
        self.validate_config()

        # Extract system message if present
        system_prompt = system
        if not system_prompt and messages and messages[0].role == MessageRole.SYSTEM:
            system_prompt = messages[0].content
            messages = messages[1:]

        try:
            response = await self.async_client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt or "",
                messages=self._convert_messages(messages),
                **kwargs,
            )

            return ModelResponse(
                content=response.content[0].text,
                model=response.model,
                stop_reason=response.stop_reason,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                metadata={"id": response.id},
            )

        except anthropic.BadRequestError as e:
            if "maximum context length" in str(e).lower():
                raise TokenLimitError(f"Token limit exceeded: {e}")
            raise APIError(f"Bad request to Anthropic API: {e}")

        except Exception as e:
            raise APIError(f"Anthropic API error: {e}")

    async def stream(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion tokens."""
        self.validate_config()

        # Extract system message if present
        system_prompt = system
        if not system_prompt and messages and messages[0].role == MessageRole.SYSTEM:
            system_prompt = messages[0].content
            messages = messages[1:]

        try:
            async with self.async_client.messages.stream(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt or "",
                messages=self._convert_messages(messages),
                **kwargs,
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            raise APIError(f"Streaming error: {e}")

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Note: This is an approximation. Claude uses a different tokenizer
        than the standard GPT tokenizers.
        """
        # Rough approximation: ~4 characters per token for English text
        # This is conservative (overestimates) to be safe
        return len(text) // 3

    def get_model_info(self) -> dict:
        """Get information about the current model."""
        model_info = {
            "claude-3-5-sonnet-20241022": {
                "context_window": 200_000,
                "max_output": 8_192,
                "description": "Most intelligent Claude model",
            },
            "claude-3-5-haiku-20241022": {
                "context_window": 200_000,
                "max_output": 8_192,
                "description": "Fastest Claude model",
            },
            "claude-3-opus-20240229": {
                "context_window": 200_000,
                "max_output": 4_096,
                "description": "Previous generation flagship model",
            },
        }
        return model_info.get(self.model_name, {
            "context_window": 200_000,
            "max_output": 4_096,
            "description": "Unknown model",
        })
