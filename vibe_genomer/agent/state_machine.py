"""
Agent state management.

Maintains conversation history and context for the agent.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from ..utils import VibeLogger


@dataclass
class Message:
    """A message in the conversation."""

    role: str  # user, assistant, system
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """
    Current state of the agent.

    Contains conversation history, context, and any intermediate results.
    """

    messages: List[Message] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to the conversation history."""
        msg = Message(
            role=role,
            content=content,
            metadata=metadata or {},
        )
        self.messages.append(msg)

    def get_recent_messages(self, n: int = 10) -> List[Message]:
        """Get the n most recent messages."""
        return self.messages[-n:]

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata,
                }
                for msg in self.messages
            ],
            "context": self.context,
            "intermediate_results": self.intermediate_results,
            "errors": self.errors,
        }


class StateManager:
    """Manages the agent's state across interactions."""

    def __init__(self, logger: "VibeLogger"):
        """
        Initialize state manager.

        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.state = AgentState()

    def get_state(self) -> AgentState:
        """Get the current state."""
        return self.state

    def reset(self):
        """Reset the state (clear history and context)."""
        self.logger.debug("Resetting agent state")
        self.state = AgentState()

    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a user message to the history."""
        self.state.add_message("user", content, metadata)
        self.logger.debug(f"Added user message: {content[:100]}...")

    def add_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add an assistant message to the history."""
        self.state.add_message("assistant", content, metadata)
        self.logger.debug(f"Added assistant message: {content[:100]}...")

    def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a system message to the history."""
        self.state.add_message("system", content, metadata)

    def add_error(self, error: str):
        """Add an error to the state."""
        self.state.errors.append(error)
        self.logger.warning(f"Error recorded: {error}")

    def update_context(self, context: Dict[str, Any]):
        """
        Update the context.

        Args:
            context: Dictionary of context updates
        """
        self.state.context.update(context)
        self.logger.debug(f"Context updated: {list(context.keys())}")

    def add_intermediate_result(self, key: str, value: Any):
        """
        Store an intermediate result.

        Args:
            key: Result key
            value: Result value
        """
        self.state.intermediate_results[key] = value
        self.logger.debug(f"Stored intermediate result: {key}")

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history as list of dicts."""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
            }
            for msg in self.state.messages
        ]

    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a context value.

        Args:
            key: Context key
            default: Default value if key not found

        Returns:
            Context value or default
        """
        return self.state.context.get(key, default)

    def format_history_for_llm(self, max_messages: int = 20) -> str:
        """
        Format conversation history for LLM context.

        Args:
            max_messages: Maximum number of recent messages to include

        Returns:
            Formatted history string
        """
        recent = self.state.get_recent_messages(max_messages)

        formatted = []
        for msg in recent:
            formatted.append(f"{msg.role.upper()}: {msg.content}")

        return "\n\n".join(formatted)
