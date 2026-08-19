"""Agent domain models."""

import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from uuid import uuid4


class AgentBase(BaseModel):
    """Base agent model."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    version: str = Field("1.0.0", description="Agent version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional agent metadata")


class AgentCreate(AgentBase):
    """Model for creating a new agent."""
    pass


class AgentUpdate(BaseModel):
    """Model for updating an agent."""
    version: Optional[str] = Field(None, description="Agent version")
    metadata: Optional[Dict[str, Any]] = Field(None)


class AgentInDBBase(AgentBase):
    """Base agent model as stored in database."""
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique agent identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class Agent(AgentInDBBase):
    """Complete agent model."""
    pass


class AgentInDB(AgentInDBBase):
    """Agent model as stored in database (includes any database-specific fields)."""
    pass