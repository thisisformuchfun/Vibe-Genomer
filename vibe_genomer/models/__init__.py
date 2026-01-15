"""
Models Module: LLM Provider Integrations

Abstracts away the differences between LLM providers.
Supports Anthropic Claude, OpenAI, local models via Ollama, and more.
"""

from typing import Optional

from vibe_genomer.models.base import BaseLLMProvider, Message, MessageRole, ModelResponse
from vibe_genomer.models.anthropic import AnthropicProvider
from vibe_genomer.models.openai import OpenAIProvider
from vibe_genomer.models.local import LocalProvider
from vibe_genomer.utils import InvalidConfigError


def create_provider(
    provider_name: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    **kwargs,
) -> BaseLLMProvider:
    """
    Factory function to create the appropriate LLM provider.

    Args:
        provider_name: Name of the provider ("anthropic", "openai", "local")
        api_key: API key (if required)
        model_name: Model name to use
        **kwargs: Additional provider-specific parameters

    Returns:
        Initialized LLM provider

    Raises:
        InvalidConfigError: If provider name is invalid

    Example:
        >>> provider = create_provider("anthropic", api_key="sk-...")
        >>> response = provider.complete([Message(MessageRole.USER, "Hello")])
    """
    providers = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "local": LocalProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise InvalidConfigError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {', '.join(providers.keys())}"
        )

    return provider_class(api_key=api_key, model_name=model_name, **kwargs)


__all__ = [
    "BaseLLMProvider",
    "Message",
    "MessageRole",
    "ModelResponse",
    "AnthropicProvider",
    "OpenAIProvider",
    "LocalProvider",
    "create_provider",
]
