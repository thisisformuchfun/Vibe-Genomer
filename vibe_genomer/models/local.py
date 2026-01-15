"""
Local model provider implementation (using Ollama).
"""

from typing import List, Optional, AsyncIterator
import httpx

from .base import BaseLLMProvider, Message, ModelResponse, MessageRole
from ..utils import get_logger, APIError, ModelNotAvailableError


class LocalProvider(BaseLLMProvider):
    """LLM provider for local models via Ollama."""

    DEFAULT_MODEL = "deepseek-coder:6.7b"
    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(
        self,
        api_key: Optional[str] = None,  # Not used for local models
        model_name: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        timeout: int = 300,
        base_url: Optional[str] = None,
        **kwargs,
    ):
        """Initialize local model provider."""
        super().__init__(
            api_key=None,  # Not needed for local models
            model_name=model_name or self.DEFAULT_MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            **kwargs,
        )
        self.logger = get_logger()
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.client = httpx.Client(base_url=self.base_url, timeout=self.timeout)
        self.async_client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    def validate_config(self) -> bool:
        """Validate that Ollama is running and model is available."""
        try:
            # Check if Ollama is running
            response = self.client.get("/api/tags")
            if response.status_code != 200:
                raise ModelNotAvailableError(
                    f"Ollama API not accessible at {self.base_url}. "
                    f"Ensure Ollama is running."
                )

            # Check if model is available
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]

            if self.model_name not in model_names:
                self.logger.warning(
                    f"Model {self.model_name} not found. Available models: {model_names}. "
                    f"Attempting to pull model..."
                )
                self._pull_model()

            return True

        except httpx.ConnectError:
            raise ModelNotAvailableError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Please install and start Ollama: https://ollama.ai"
            )
        except Exception as e:
            raise ModelNotAvailableError(f"Failed to validate local model: {e}")

    def _pull_model(self):
        """Pull the model if not available."""
        try:
            self.logger.info(f"Pulling model {self.model_name}...")
            response = self.client.post(
                "/api/pull",
                json={"name": self.model_name},
                timeout=600,  # Model pulling can take a while
            )
            if response.status_code == 200:
                self.logger.success(f"Model {self.model_name} pulled successfully")
            else:
                raise APIError(f"Failed to pull model: {response.text}")
        except Exception as e:
            raise APIError(f"Error pulling model: {e}")

    def _convert_messages(self, messages: List[Message], system: Optional[str] = None) -> List[dict]:
        """Convert internal messages to Ollama format."""
        converted = []

        # Add system message first if provided
        if system:
            converted.append({
                "role": "system",
                "content": system,
            })

        # Add conversation messages
        for msg in messages:
            if msg.role != MessageRole.SYSTEM:
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
        """Generate completion using local model."""
        self.validate_config()

        try:
            response = self.client.post(
                "/api/chat",
                json={
                    "model": self.model_name,
                    "messages": self._convert_messages(messages, system),
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    },
                },
            )

            if response.status_code != 200:
                raise APIError(f"Ollama API error: {response.text}")

            data = response.json()

            return ModelResponse(
                content=data["message"]["content"],
                model=self.model_name,
                stop_reason=data.get("done_reason", "stop"),
                usage={
                    "input_tokens": data.get("prompt_eval_count", 0),
                    "output_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                },
            )

        except httpx.HTTPError as e:
            raise APIError(f"HTTP error: {e}")
        except Exception as e:
            raise APIError(f"Local model error: {e}")

    async def complete_async(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        **kwargs,
    ) -> ModelResponse:
        """Generate completion asynchronously."""
        self.validate_config()

        try:
            response = await self.async_client.post(
                "/api/chat",
                json={
                    "model": self.model_name,
                    "messages": self._convert_messages(messages, system),
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    },
                },
            )

            if response.status_code != 200:
                raise APIError(f"Ollama API error: {response.text}")

            data = response.json()

            return ModelResponse(
                content=data["message"]["content"],
                model=self.model_name,
                stop_reason=data.get("done_reason", "stop"),
                usage={
                    "input_tokens": data.get("prompt_eval_count", 0),
                    "output_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                },
            )

        except Exception as e:
            raise APIError(f"Local model error: {e}")

    async def stream(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion tokens."""
        self.validate_config()

        try:
            async with self.async_client.stream(
                "POST",
                "/api/chat",
                json={
                    "model": self.model_name,
                    "messages": self._convert_messages(messages, system),
                    "stream": True,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    },
                },
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if content := data.get("message", {}).get("content"):
                            yield content

        except Exception as e:
            raise APIError(f"Streaming error: {e}")

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Note: This is a rough approximation for local models.
        """
        # Simple approximation: ~4 characters per token
        return len(text) // 4

    def get_model_info(self) -> dict:
        """Get information about the current model."""
        try:
            response = self.client.post(
                "/api/show",
                json={"name": self.model_name},
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "model": self.model_name,
                    "parameters": data.get("parameters"),
                    "template": data.get("template"),
                }
        except Exception:
            pass

        return {
            "model": self.model_name,
            "description": "Local model via Ollama",
        }

    def list_available_models(self) -> List[str]:
        """List all available local models."""
        try:
            response = self.client.get("/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m["name"] for m in models]
        except Exception:
            pass
        return []
