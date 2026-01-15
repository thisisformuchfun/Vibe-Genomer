"""
Base class for bioinformatics tool wrappers.

All tool wrappers inherit from BioinformaticsTool and implement
a consistent interface for execution, validation, and error handling.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import shutil
import subprocess

from ..utils import (
    get_logger,
    ToolError,
    ToolNotFoundError,
    ToolExecutionError,
    require_tool,
)


@dataclass
class ToolResult:
    """Result from a tool execution."""

    success: bool
    stdout: str
    stderr: str
    returncode: int
    command: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BioinformaticsTool(ABC):
    """
    Abstract base class for bioinformatics tools.

    All tool wrappers must implement:
    - validate_params: Validate input parameters
    - build_command: Construct the command
    - parse_output: Parse the output
    """

    def __init__(self):
        """Initialize the tool."""
        self.logger = get_logger()
        self.tool_name = self.__class__.__name__.replace("Tool", "").lower()

    @property
    @abstractmethod
    def binary_name(self) -> str:
        """Name of the binary executable."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does."""
        pass

    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        Validate input parameters.

        Args:
            params: Parameters dictionary

        Returns:
            True if valid

        Raises:
            ToolError: If parameters are invalid
        """
        pass

    @abstractmethod
    def build_command(self, params: Dict[str, Any]) -> List[str]:
        """
        Build the command to execute.

        Args:
            params: Parameters dictionary

        Returns:
            Command as list of strings (for subprocess)
        """
        pass

    def parse_output(self, result: ToolResult) -> Any:
        """
        Parse the tool output.

        Default implementation returns stdout.
        Override for custom parsing.

        Args:
            result: Tool execution result

        Returns:
            Parsed output
        """
        return result.stdout

    def is_installed(self) -> bool:
        """Check if the tool is installed and available."""
        return shutil.which(self.binary_name) is not None

    def get_version(self) -> Optional[str]:
        """
        Get the tool version.

        Returns:
            Version string or None if not available
        """
        try:
            result = subprocess.run(
                [self.binary_name, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() or result.stderr.strip()
        except Exception:
            return None

    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Execute the tool with given parameters.

        Args:
            params: Parameters dictionary

        Returns:
            Parsed output

        Raises:
            ToolNotFoundError: If tool is not installed
            ToolExecutionError: If execution fails
        """
        # Check if tool is installed
        if not self.is_installed():
            raise ToolNotFoundError(
                f"{self.binary_name} not found. Please install it before using this tool."
            )

        # Validate parameters
        self.validate_params(params)

        # Build command
        command = self.build_command(params)
        command_str = " ".join(command)

        self.logger.tool_execution(self.binary_name, command_str)

        # Execute command
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=params.get("timeout", 300),
            )

            tool_result = ToolResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                command=command_str,
            )

            if not tool_result.success:
                raise ToolExecutionError(
                    f"{self.binary_name} failed with return code {result.returncode}\n"
                    f"Command: {command_str}\n"
                    f"Error: {result.stderr}"
                )

            # Parse and return output
            parsed = self.parse_output(tool_result)

            self.logger.debug(f"{self.binary_name} completed successfully")

            return parsed

        except subprocess.TimeoutExpired:
            raise ToolExecutionError(
                f"{self.binary_name} timed out after {params.get('timeout', 300)} seconds"
            )

        except Exception as e:
            raise ToolExecutionError(f"{self.binary_name} execution failed: {e}")

    def execute_in_sandbox(self, params: Dict[str, Any], sandbox: Any) -> Any:
        """
        Execute the tool in a sandbox environment.

        Args:
            params: Parameters dictionary
            sandbox: Sandbox instance

        Returns:
            Parsed output
        """
        # For now, just execute normally
        # Sandbox integration will be implemented later
        self.logger.warning("Sandbox execution not yet implemented, running without isolation")
        return self.execute(params)

    def __repr__(self) -> str:
        """String representation of the tool."""
        return f"{self.__class__.__name__}(binary={self.binary_name})"
