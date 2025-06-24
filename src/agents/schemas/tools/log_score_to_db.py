"""Schemas for log score to db tool."""

from typing import Any, Dict, List, Optional

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class LogScoreToDbInput(ToolInput):
    """Input for logging scores to the database."""

    agent_id: str = Field(description="ID of the agent (prefecture)")
    ad_id: str = Field(description="ID of the ad being evaluated")
    liking: float = Field(description="Liking score (0-5)", ge=0.0, le=5.0)
    purchase_intent: float = Field(description="Purchase intent score (0-5)", ge=0.0, le=5.0)
    commentary: Optional[str] = Field(description="Commentary explaining the evaluation", default=None)
    neighbors_used: Optional[List[str]] = Field(
        description="List of neighboring agent IDs whose scores were used", default=None
    )
    additional_data: Optional[Dict[str, Any]] = Field(description="Additional data to log", default=None)


class LogScoreToDbOutput(ToolOutput):
    """Output from logging scores to database."""

    log_id: str = Field(description="ID of the created log entry")
    logged_at: str = Field(description="Timestamp when logged (ISO format)")
    record_count: int = Field(description="Number of records logged")
    storage_location: str = Field(description="Where the data was stored")
