"""
Tools Module: Bioinformatics Tool Integrations

Wrappers and integrations for common bioinformatics tools.
Each tool wrapper provides a consistent interface for the agent to use.
"""

from typing import Dict, Type
from vibe_genomer.tools.base import BioinformaticsTool, ToolResult
from vibe_genomer.tools.samtools import SamtoolsView, SamtoolsStats, SamtoolsIndex
from vibe_genomer.utils import ToolNotFoundError


# Tool registry
_TOOL_REGISTRY: Dict[str, Type[BioinformaticsTool]] = {}


def register_tool(name: str, tool_class: Type[BioinformaticsTool]):
    """
    Register a tool in the global registry.

    Args:
        name: Tool name (e.g., "samtools_view")
        tool_class: Tool class
    """
    _TOOL_REGISTRY[name] = tool_class


def get_tool(name: str) -> BioinformaticsTool:
    """
    Get a tool instance by name.

    Args:
        name: Tool name

    Returns:
        Tool instance

    Raises:
        ToolNotFoundError: If tool is not registered
    """
    tool_class = _TOOL_REGISTRY.get(name)
    if not tool_class:
        raise ToolNotFoundError(
            f"Tool '{name}' not found in registry. "
            f"Available tools: {', '.join(_TOOL_REGISTRY.keys())}"
        )
    return tool_class()


def list_tools() -> Dict[str, str]:
    """
    List all registered tools.

    Returns:
        Dictionary mapping tool names to descriptions
    """
    return {
        name: tool_class().description
        for name, tool_class in _TOOL_REGISTRY.items()
    }


# Register built-in tools
register_tool("samtools_view", SamtoolsView)
register_tool("samtools_stats", SamtoolsStats)
register_tool("samtools_index", SamtoolsIndex)


__all__ = [
    "BioinformaticsTool",
    "ToolResult",
    "SamtoolsView",
    "SamtoolsStats",
    "SamtoolsIndex",
    "register_tool",
    "get_tool",
    "list_tools",
]
