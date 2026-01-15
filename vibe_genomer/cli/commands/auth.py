"""
Authentication command implementation.

Handles setting up API keys and authentication for LLM providers.
"""

import os
from pathlib import Path
from typing import Optional, TYPE_CHECKING
import click
import yaml

if TYPE_CHECKING:
    from ...utils import Config, VibeLogger


def setup_authentication(
    provider: str,
    api_key: Optional[str],
    config: "Config",
    logger: "VibeLogger",
):
    """
    Set up authentication for an LLM provider.

    Args:
        provider: Provider name (anthropic, openai, local)
        api_key: API key (optional, will prompt if not provided)
        config: Application configuration
        logger: Logger instance
    """
    logger.info(f"Setting up authentication for {provider}")

    # Local provider doesn't need API key
    if provider == "local":
        config.model.provider = "local"
        logger.info("Local provider selected - no API key needed")
        _save_config(config, logger)
        return

    # Get API key
    if not api_key:
        api_key = click.prompt(
            f"Enter your {provider.upper()} API key",
            hide_input=True,
        )

    # Validate API key format
    if provider == "anthropic" and not api_key.startswith("sk-ant-"):
        logger.warning("API key doesn't look like an Anthropic key (should start with 'sk-ant-')")

    if provider == "openai" and not api_key.startswith("sk-"):
        logger.warning("API key doesn't look like an OpenAI key (should start with 'sk-')")

    # Test the API key
    logger.info("Testing API key...")
    try:
        from ...models import create_provider, Message, MessageRole

        test_provider = create_provider(
            provider_name=provider,
            api_key=api_key,
        )

        # Try a simple completion to verify the key works
        test_provider.complete([
            Message(MessageRole.USER, "Say 'OK' if you can read this.")
        ])

        logger.success("API key validated successfully!")

    except Exception as e:
        logger.error(f"API key validation failed: {e}")
        raise click.ClickException("Invalid API key or provider unavailable")

    # Save configuration
    config.model.provider = provider
    config.model.api_key = api_key

    _save_config(config, logger)

    # Optionally save to environment variable
    if click.confirm("Save API key to environment variable?"):
        env_var = f"{provider.upper()}_API_KEY"
        logger.info(f"Add this to your shell configuration (~/.bashrc or ~/.zshrc):")
        logger.info(f"  export {env_var}={api_key}")


def _save_config(config: "Config", logger: "VibeLogger"):
    """Save configuration to file."""
    config_path = config.config_dir / "config.yaml"
    config.config_dir.mkdir(parents=True, exist_ok=True)

    config_data = {
        "model": {
            "provider": config.model.provider,
            "model_name": config.model.model_name,
            "api_key": config.model.api_key,
            "temperature": config.model.temperature,
            "max_tokens": config.model.max_tokens,
        },
        "sandbox": {
            "enabled": config.sandbox.enabled,
            "backend": config.sandbox.backend,
        },
        "verification": {
            "enabled": config.verification.enabled,
            "strict_mode": config.verification.strict_mode,
        },
    }

    with open(config_path, "w") as f:
        yaml.dump(config_data, f, default_flow_style=False)

    logger.success(f"Configuration saved to {config_path}")
