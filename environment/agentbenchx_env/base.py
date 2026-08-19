"""Abstract base class for AgentBenchX environments."""

import abc
import asyncio
import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from backend.app.domain.tools.models import ActionResult


class EnvironmentConfig(BaseModel):
    """Base configuration for environments."""
    environment_id: str = Field(..., description="Unique identifier for the environment")
    version: str = Field("1.0.0", description="Environment version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional environment metadata")


class State(BaseModel):
    """Represents the state of the environment."""
    # This can be extended by specific environment implementations
    # For now, we'll keep it generic with a dict for flexibility
    data: Dict[str, Any] = Field(default_factory=dict, description="Environment state data")
    timestamp: float = Field(default_factory=time.time, description="Timestamp of the state")


class Tool(BaseModel):
    """Definition of a tool available in the environment."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    input_schema: Dict[str, Any] = Field(..., description="JSON schema for tool input")
    # Optional: output schema, side effects, etc.


class BaseEnvironment(abc.ABC):
    """Abstract base class for all environments in AgentBenchX."""

    def __init__(self, config: EnvironmentConfig):
        self.config = config
        self._tools: Dict[str, Tool] = {}
        self._state = State()
        self._is_initialized = False

    @property
    def environment_id(self) -> str:
        """Get the environment's unique identifier."""
        return self.config.environment_id

    @property
    def version(self) -> str:
        """Get the environment version."""
        return self.config.version

    @property
    def state(self) -> State:
        """Get the current environment state."""
        return self._state

    @property
    def tools(self) -> List[Tool]:
        """Get list of available tools in the environment."""
        return list(self._tools.values())

    @abc.abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the environment.
        Should set up any necessary resources and return True if successful.
        """
        pass

    @abc.abstractmethod
    async def reset(self) -> State:
        """
        Reset the environment to its initial state.
        Returns the initial state.
        """
        pass

    @abc.abstractmethod
    async def get_state(self) -> State:
        """
        Get the current state of the environment.
        """
        pass

    @abc.abstractmethod
    async def execute_action(
        self,
        action_name: str,
        action_args: Dict[str, Any]
    ) -> ActionResult:
        """
        Execute an action (tool usage) in the environment.

        Args:
            action_name: Name of the tool/action to execute
            action_args: Arguments for the action

        Returns:
            ActionResult containing the outcome
        """
        pass

    @abc.abstractmethod
    async def cleanup(self) -> bool:
        """
        Clean up any resources used by the environment.
        Should return True if successful.
        """
        pass

    def register_tool(self, tool: Tool) -> None:
        """Register a tool with the environment."""
        self._tools[tool.name] = tool

    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool from the environment."""
        if tool_name in self._tools:
            del self._tools[tool_name]
            return True
        return False

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(tool_name)