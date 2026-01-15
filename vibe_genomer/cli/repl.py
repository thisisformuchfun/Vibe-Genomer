"""
Interactive REPL (Read-Eval-Print Loop) for Vibe-Genomer.

This provides an interactive session for genomic data exploration.
"""

from typing import TYPE_CHECKING, List
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown

if TYPE_CHECKING:
    from ..utils import Config, VibeLogger

console = Console()


class GenomicREPL:
    """Interactive REPL for genomic analysis."""

    def __init__(self, config: "Config", logger: "VibeLogger"):
        self.config = config
        self.logger = logger
        self.history: List[str] = []
        self.agent = None
        self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the genomic agent."""
        from ..models import create_provider
        from ..agent import GenomicAgent

        try:
            provider = create_provider(
                provider_name=self.config.model.provider,
                api_key=self.config.model.api_key,
                model_name=self.config.model.model_name,
            )

            self.agent = GenomicAgent(
                provider=provider,
                config=self.config,
                logger=self.logger,
            )

            console.print("[green]✓[/green] Agent initialized")

        except Exception as e:
            console.print(f"[red]Failed to initialize agent:[/red] {e}")
            console.print("[yellow]Tip:[/yellow] Run 'vibe auth' to set up your API key")
            raise

    def run(self):
        """Run the REPL loop."""
        console.print("[dim]Loading...[/dim]")

        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]vibe>[/bold cyan]").strip()

                if not user_input:
                    continue

                # Handle REPL commands
                if user_input.lower() in ["exit", "quit", "q"]:
                    console.print("[yellow]Exiting...[/yellow]")
                    break

                elif user_input.lower() in ["help", "?"]:
                    self._show_help()
                    continue

                elif user_input.lower() == "clear":
                    console.clear()
                    continue

                elif user_input.lower() == "history":
                    self._show_history()
                    continue

                elif user_input.lower() == "reset":
                    self._reset_agent()
                    continue

                # Process query
                self.history.append(user_input)
                self._process_query(user_input)

            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
                continue

            except EOFError:
                break

            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
                if self.config.debug:
                    raise

    def _process_query(self, query: str):
        """Process a user query."""
        console.print("[dim]Thinking...[/dim]")

        try:
            result = self.agent.execute(query)

            # Display result
            console.print("\n" + "─" * 80)
            console.print(Markdown(result))
            console.print("─" * 80)

        except Exception as e:
            console.print(f"[red]Analysis failed:[/red] {e}")
            if self.config.debug:
                raise

    def _show_help(self):
        """Show help message."""
        help_text = """
[bold]Vibe-Genomer REPL Commands[/bold]

[cyan]Query Commands:[/cyan]
  Just type your question in natural language!

  Examples:
    • Find variants in BRCA1 from sample.vcf
    • What's the coverage in chr1:1000-2000?
    • Align reads to hg38

[cyan]REPL Commands:[/cyan]
  [bold]help[/bold], [bold]?[/bold]       Show this help message
  [bold]history[/bold]      Show command history
  [bold]clear[/bold]        Clear the screen
  [bold]reset[/bold]        Reset the agent (clear context)
  [bold]exit[/bold], [bold]quit[/bold]   Exit the REPL

[cyan]Tips:[/cyan]
  • Be specific about file paths and genomic coordinates
  • The agent maintains context between queries
  • Use 'reset' if you want to start fresh
  • Press Ctrl+C to interrupt a running query
"""
        console.print(help_text)

    def _show_history(self):
        """Show command history."""
        if not self.history:
            console.print("[dim]No history yet[/dim]")
            return

        console.print("\n[bold]Command History:[/bold]")
        for i, cmd in enumerate(self.history, 1):
            console.print(f"  {i}. {cmd}")

    def _reset_agent(self):
        """Reset the agent to clear context."""
        console.print("[yellow]Resetting agent...[/yellow]")
        self._initialize_agent()
        self.history.clear()
        console.print("[green]✓[/green] Agent reset")


def start_repl(config: "Config", logger: "VibeLogger"):
    """
    Start the interactive REPL.

    Args:
        config: Application configuration
        logger: Logger instance
    """
    repl = GenomicREPL(config, logger)
    repl.run()
