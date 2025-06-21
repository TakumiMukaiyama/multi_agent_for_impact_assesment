"""Schemas for log_score_to_db tool."""
from typing import Dict, List, Optional, Any

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class LogScoreToDbInput(ToolInput):
    """Input for logging scores to the database."""
    
    agent_id: str = Field(description="ID of the agent (prefecture)")
    ad_id: str = Field(description="ID of the ad being evaluated")
    liking: float = Field(
        description="Liking score (0-5)",
        ge=0.0,
        le=5.0
    )
    purchase_intent: float = Field(
        description="Purchase intent score (0-5)",
        ge=0.0,
        le=5.0
    )
    commentary: str = Field(description="Commentary explaining the evaluation")
    neighbors_used: List[str] = Field(
        description="List of neighboring agent IDs whose scores were used",
        default_factory=list
    )
    additional_data: Optional[Dict[str, Any]] = Field(
        description="Additional data to log",
        default=None
    )


class LogScoreToDbOutput(ToolOutput):
    """Output from logging scores to the database."""
    
    record_id: str = Field(description="ID of the created database record")
    timestamp: str = Field(description="Timestamp of when the record was created")