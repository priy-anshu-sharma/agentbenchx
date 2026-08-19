"""Tool and Action domain models for AgentBenchX."""

import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from uuid import uuid4


class ToolBase(BaseModel):
    """Base tool model."""
    name: str = Field(..., min_length=1, max_length=100, description="Tool name")
    description: str = Field(..., max_length=500, description="Tool description")
    input_schema: Dict[str, Any] = Field(..., description="JSON schema for tool input")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for tool output")
    is_safe: bool = Field(True, description="Whether the tool is considered safe to execute")
    categories: List[str] = Field(default_factory=list, description="Tool categories for organization")


class ToolCreate(ToolBase):
    """Model for creating a new tool."""
    pass


class ToolUpdate(BaseModel):
    """Model for updating a tool."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    input_schema: Optional[Dict[str, Any]] = Field(None)
    output_schema: Optional[Dict[str, Any]] = Field(None)
    is_safe: Optional[bool] = Field(None)
    categories: Optional[List[str]] = Field(None)


class ToolInDBBase(ToolBase):
    """Base tool model as stored in database."""
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique tool identifier")
    version: str = Field(..., description="Tool version")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class Tool(ToolInDBBase):
    """Complete tool model."""
    pass


class ToolInDB(ToolInDBBase):
    """Tool model as stored in database (includes any database-specific fields)."""


class Action(BaseModel):
    """Represents an action (tool usage) requested by an agent."""
    action_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique action identifier")
    tool_name: str = Field(..., min_length=1, description="Name of the tool to execute")
    arguments: Dict[str, Any] = Field(..., description="Arguments to pass to the tool")
    timestamp: float = Field(default_factory=time.time, description="When the action was requested")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional action metadata")


class ActionResult(BaseModel):
    """Result of executing an action."""
    success: bool = Field(..., description="Whether the action was successful")
    output: Optional[Any] = Field(None, description="Output from the action")
    error: Optional[str] = Field(None, description="Error message if action failed")
    execution_time: float = Field(..., description="Time taken to execute the action (seconds)")
    state_change: Optional[Dict[str, Any]] = Field(None, description="Changes to environment state")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional result metadata")


# Import time at the module level to avoid circular imports
import time