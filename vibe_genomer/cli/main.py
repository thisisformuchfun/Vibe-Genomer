"""
Main CLI entry point for Vibe-Genomer.

This is the command-line interface that users interact with.
"""

import sys
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from ..utils import (
    get_config,
    set_config,
    load_config,
    get_logger,
    setup_logging,
    CLIError,
)

console = Console()


def print_banner():
    """Print the Vibe-Genomer banner."""
    banner = """
[bold cyan]┏┓ ╻╻┏┓ ┏━╸   ┏━╸┏━╸┏┓╻┏━┓┏┳┓┏━╸┏━┓[/bold cyan]
[bold cyan]┃┃ ┃┣┻┓┣╸    ┃╺┓┣╸ ┃┗┫┃ ┃┃┃┃┣╸ ┣┳┛[/bold cyan]
[bold cyan]┗┛ ╹╹ ╹┗━╸   ┗━┛┗━╸╹ ╹┗━┛╹ ╹┗━╸╹┗╸[/bold cyan]

[dim]The "Claude Code" for Genomics[/dim]
[dim]Version 0.1.0 (Pre-Alpha)[/dim]
"""
    console.print(banner)


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--config", type=click.Path(exists=True), help="Path to config file")
@click.pass_context
def cli(ctx, debug, config):
    """
    Vibe-Genomer: Autonomous Genomic Agent

    Transform natural language into bioinformatics workflows.

    \b
    Examples:
        vibe "Align these FASTQ files to hg38"
        vibe auth --provider anthropic
        vibe repl
    """
    # Ensure ctx.obj exists
    ctx.ensure_object(dict)

    # Load configuration
    if config:
        cfg = load_config(Path(config))
    else:
        cfg = get_config()

    if debug:
        cfg.debug = True
        cfg.log_level = "DEBUG"

    set_config(cfg)

    # Setup logging
    logger = setup_logging(
        level=cfg.log_level,
        log_file=cfg.log_file,
        enable_rich=not cfg.debug,
    )

    ctx.obj["config"] = cfg
    ctx.obj["logger"] = logger


@cli.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--model", help="Model to use (overrides config)")
@click.option("--provider", help="Provider to use (anthropic, openai, local)")
@click.pass_context
def analyze(ctx, query, model, provider):
    """
    Analyze genomic data with natural language.

    \b
    Examples:
        vibe analyze "Find variants in BRCA1 from this VCF"
        vibe analyze "Align sample1.fastq to hg38"
        vibe analyze "What's the coverage in chr1:1000-2000?"
    """
    from .commands.analyze import run_analysis

    config = ctx.obj["config"]
    logger = ctx.obj["logger"]

    # Override model/provider if specified
    if model:
        config.model.model_name = model
    if provider:
        config.model.provider = provider

    query_text = " ".join(query)
    logger.info(f"Analyzing: {query_text}")

    try:
        run_analysis(query_text, config, logger)
    except CLIError as e:
        logger.error(f"Analysis failed: {e.message}")
        sys.exit(1)
    except Exception as e:
        logger.exception(e, "Unexpected error during analysis")
        sys.exit(1)


@cli.command()
@click.option("--provider", type=click.Choice(["anthropic", "openai", "local"]), required=True)
@click.option("--api-key", help="API key (will prompt if not provided)")
@click.pass_context
def auth(ctx, provider, api_key):
    """
    Authenticate with an LLM provider.

    \b
    Examples:
        vibe auth --provider anthropic
        vibe auth --provider openai --api-key sk-...
        vibe auth --provider local  # No API key needed
    """
    from .commands.auth import setup_authentication

    config = ctx.obj["config"]
    logger = ctx.obj["logger"]

    try:
        setup_authentication(provider, api_key, config, logger)
        logger.success(f"Successfully authenticated with {provider}")
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def repl(ctx):
    """
    Start an interactive REPL session.

    This launches an interactive session where you can iteratively
    explore and analyze genomic data.

    \b
    Features:
        - Multi-turn conversations
        - Persistent context
        - Tab completion
        - Command history
    """
    from .repl import start_repl

    config = ctx.obj["config"]
    logger = ctx.obj["logger"]

    print_banner()
    console.print("[cyan]Starting interactive REPL...[/cyan]\n")
    console.print("[dim]Type 'help' for commands, 'exit' to quit[/dim]\n")

    try:
        start_repl(config, logger)
    except KeyboardInterrupt:
        console.print("\n[yellow]Session interrupted[/yellow]")
    except Exception as e:
        logger.exception(e, "REPL error")
        sys.exit(1)


@cli.command()
@click.option("--all", "update_all", is_flag=True, help="Update all knowledge bases")
@click.option("--clinvar", is_flag=True, help="Update ClinVar database")
@click.option("--ensembl", is_flag=True, help="Update Ensembl database")
@click.option("--ucsc", is_flag=True, help="Update UCSC database")
@click.pass_context
def update_knowledge(ctx, update_all, clinvar, ensembl, ucsc):
    """
    Update genomic knowledge bases.

    Downloads and updates reference databases like ClinVar, Ensembl, etc.

    \b
    Examples:
        vibe update-knowledge --all
        vibe update-knowledge --clinvar
        vibe update-knowledge --clinvar --ensembl
    """
    from .commands.update import update_databases

    config = ctx.obj["config"]
    logger = ctx.obj["logger"]

    # Determine which databases to update
    databases = []
    if update_all:
        databases = ["clinvar", "ensembl", "ucsc"]
    else:
        if clinvar:
            databases.append("clinvar")
        if ensembl:
            databases.append("ensembl")
        if ucsc:
            databases.append("ucsc")

    if not databases:
        logger.warning("No databases specified. Use --all or specify individual databases.")
        sys.exit(1)

    logger.info(f"Updating databases: {', '.join(databases)}")

    try:
        update_databases(databases, config, logger)
        logger.success("Knowledge bases updated successfully")
    except Exception as e:
        logger.error(f"Update failed: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def info(ctx):
    """
    Show system information and configuration.

    Displays current configuration, model status, available tools, etc.
    """
    config = ctx.obj["config"]
    logger = ctx.obj["logger"]

    console.print(Panel.fit(
        f"""[bold]Vibe-Genomer Configuration[/bold]

[cyan]Model:[/cyan]
  Provider: {config.model.provider}
  Model: {config.model.model_name}
  API Key: {'✓ Set' if config.model.api_key else '✗ Not set'}

[cyan]Sandbox:[/cyan]
  Enabled: {config.sandbox.enabled}
  Backend: {config.sandbox.backend}
  Memory Limit: {config.sandbox.memory_limit}

[cyan]Verification:[/cyan]
  Enabled: {config.verification.enabled}
  Strict Mode: {config.verification.strict_mode}

[cyan]Paths:[/cyan]
  Config Dir: {config.config_dir}
  Data Dir: {config.data_dir}
  RAG Cache: {config.rag.cache_dir}
  Knowledge Cache: {config.knowledge.cache_dir}
""",
        title="System Information",
        border_style="cyan",
    ))


@cli.command()
@click.pass_context
def version(ctx):
    """Show version information."""
    console.print("[bold cyan]Vibe-Genomer v0.1.0[/bold cyan] (Pre-Alpha)")
    console.print("[dim]The 'Claude Code' for Genomics[/dim]")


def main():
    """Main entry point for the CLI."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if "--debug" in sys.argv:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
