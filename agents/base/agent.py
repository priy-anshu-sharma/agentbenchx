"""Abstract base class for AgentBenchX agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Base configuration for agents."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    version: str = Field("1.0.0", description="Agent version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional agent metadata")


class AgentCapabilities(BaseModel):
    """Capabilities that an agent possesses."""
    tool_use: bool = Field(default=False, description="Whether agent can use tools")
    reasoning: bool = Field(default=False, description="Whether agent can perform reasoning")
    memory: bool = Field(default=False, description="Whether agent has memory capabilities")


class AgentResponse(BaseModel):
    """Response from an agent execution."""
    output: Optional[str] = Field(None, description="Final output from the agent")
    actions_requested: List[Dict[str, Any]] = Field(default_factory=list, description="Actions requested by the agent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional response metadata")


class BaseAgent(ABC):
    """Abstract base class for all agents in AgentBenchX."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self._capabilities = self._define_capabilities()

    @property
    def agent_id(self) -> str:
        """Get the agent's unique identifier."""
        return self.config.agent_id

    @property
    def version(self) -> str:
        """Get the agent version."""
        return self.config.version

    @property
    def capabilities(self) -> AgentCapabilities:
        """Get the agent's capabilities."""
        return self._capabilities

    @abstractmethod
    def _define_capabilities(self) -> AgentCapabilities:
        """Define the capabilities of this agent. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def execute(
        self,
        task_instructions: str,
        available_tools: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Execute the agent on a given task.

        Args:
            task_instructions: Instructions for the task to perform
            available_tools: List of tools available to the agent
            context: Optional context information

        Returns:
            AgentResponse containing the agent's output and any actions requested
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get basic information about the agent."""
        return {
            "agent_id": self.agent_id,
            "version": self.version,
            "capabilities": self.capabilities.model_dump(),
            "config": self.config.model_dump()
        }