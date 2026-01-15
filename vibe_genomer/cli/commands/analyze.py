"""
Analysis command implementation.

This module handles the main "vibe analyze" command that processes
natural language queries and executes genomic workflows.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...utils import Config, VibeLogger


def run_analysis(query: str, config: "Config", logger: "VibeLogger"):
    """
    Run analysis based on natural language query.

    Args:
        query: User's natural language query
        config: Application configuration
        logger: Logger instance

    This is the main entry point for genomic analysis.
    It will:
    1. Parse the query using the agent
    2. Plan the execution steps
    3. Execute tools in the sandbox
    4. Verify results
    5. Return formatted output
    """
    from ...models import create_provider, Message, MessageRole
    from ...agent import GenomicAgent

    logger.info(f"Starting analysis: {query}")

    try:
        # Create LLM provider
        provider = create_provider(
            provider_name=config.model.provider,
            api_key=config.model.api_key,
            model_name=config.model.model_name,
            temperature=config.model.temperature,
            max_tokens=config.max_tokens,
        )

        logger.debug(f"Initialized {config.model.provider} provider")

        # Create genomic agent
        agent = GenomicAgent(
            provider=provider,
            config=config,
            logger=logger,
        )

        # Execute the query
        result = agent.execute(query)

        # Display results
        logger.success("Analysis complete!")
        print("\n" + "=" * 80)
        print(result)
        print("=" * 80 + "\n")

    except Exception as e:
        logger.exception(e, "Analysis failed")
        raise
