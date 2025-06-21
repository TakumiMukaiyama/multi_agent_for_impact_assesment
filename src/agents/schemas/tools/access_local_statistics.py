"""Schemas for access local statistics tool."""

from typing import Any, Dict, List, Optional

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class AccessLocalStatisticsInput(ToolInput):
    """Input for accessing local statistics."""

    agent_id: str = Field(description="ID of the agent (prefecture)")
    statistic_type: Optional[str] = Field(
        description="Type of statistic to retrieve (e.g., 'demographics', 'economy', 'lifestyle')", default="general"
    )


class AccessLocalStatisticsOutput(ToolOutput):
    """Output containing local statistics data."""

    agent_id: str = Field(description="ID of the agent (prefecture)")
    demographics: Dict[str, Any] = Field(description="Demographic information", default_factory=dict)
    economic_indicators: Dict[str, Any] = Field(description="Economic indicators", default_factory=dict)
    lifestyle_preferences: List[str] = Field(
        description="Common lifestyle preferences in the region", default_factory=list
    )
    consumer_behavior: Dict[str, Any] = Field(description="Consumer behavior patterns", default_factory=dict)
    regional_characteristics: List[str] = Field(description="Key characteristics of the region", default_factory=list)
