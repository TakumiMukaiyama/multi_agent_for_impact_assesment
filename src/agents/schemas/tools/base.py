"""Base schemas for agent tools."""
from typing import Optional

from pydantic import BaseModel, Field


class ToolInput(BaseModel):
    """Base class for tool inputs."""
    
    agent_id: str = Field(description="ID of the agent using the tool")


class ToolOutput(BaseModel):
    """Base class for tool outputs."""
    
    success: bool = Field(description="Whether the tool execution succeeded")
    message: Optional[str] = Field(
        default=None, 
        description="Message explaining the result (especially if failed)"
    )