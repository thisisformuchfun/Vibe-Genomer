"""
Logging configuration for Vibe-Genomer.

This module sets up structured logging with rich formatting for CLI output.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme


# Custom theme for genomic context
GENOMIC_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green bold",
    "coordinate": "blue",
    "gene": "magenta",
    "variant": "yellow bold",
    "tool": "cyan dim",
})


class VibeLogger:
    """Custom logger for Vibe-Genomer with rich formatting."""

    def __init__(
        self,
        name: str = "vibe-genomer",
        level: str = "INFO",
        log_file: Optional[Path] = None,
        enable_rich: bool = True,
    ):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.console = Console(theme=GENOMIC_THEME)

        # Remove existing handlers
        self.logger.handlers.clear()

        # Add rich handler for console output
        if enable_rich:
            rich_handler = RichHandler(
                console=self.console,
                show_time=True,
                show_path=False,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
            )
            rich_handler.setLevel(getattr(logging, level.upper()))
            self.logger.addHandler(rich_handler)
        else:
            # Standard console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, level.upper()))
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Add file handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, extra=kwargs)

    def success(self, message: str):
        """Log success message with special formatting."""
        self.console.print(f"✓ {message}", style="success")

    def tool_execution(self, tool_name: str, command: str):
        """Log tool execution."""
        self.console.print(f"[tool]Running:[/tool] {tool_name}", style="dim")
        self.console.print(f"  {command}", style="dim italic")

    def genomic_context(self, chromosome: str, start: int, end: int, gene: Optional[str] = None):
        """Log genomic context with formatting."""
        location = f"[coordinate]{chromosome}:{start}-{end}[/coordinate]"
        if gene:
            location += f" ([gene]{gene}[/gene])"
        self.console.print(f"📍 {location}")

    def variant(self, variant_id: str, consequence: Optional[str] = None):
        """Log variant information."""
        msg = f"🧬 [variant]{variant_id}[/variant]"
        if consequence:
            msg += f" → {consequence}"
        self.console.print(msg)

    def workflow_step(self, step_number: int, total_steps: int, description: str):
        """Log workflow step progress."""
        self.console.print(f"[cyan]Step {step_number}/{total_steps}:[/cyan] {description}")

    def exception(self, exc: Exception, message: Optional[str] = None):
        """Log exception with rich traceback."""
        if message:
            self.error(message)
        self.logger.exception("Exception occurred:", exc_info=exc)


# Global logger instance
_logger: Optional[VibeLogger] = None


def get_logger() -> VibeLogger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        from .config import get_config
        config = get_config()
        _logger = setup_logging(
            level=config.log_level,
            log_file=config.log_file,
            enable_rich=not config.debug,
        )
    return _logger


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_rich: bool = True,
) -> VibeLogger:
    """
    Set up logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        enable_rich: Whether to use rich formatting

    Returns:
        Configured VibeLogger instance
    """
    logger = VibeLogger(
        name="vibe-genomer",
        level=level,
        log_file=log_file,
        enable_rich=enable_rich,
    )
    return logger
