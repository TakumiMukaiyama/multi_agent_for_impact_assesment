"""Schemas for access_local_statistics tool."""
from typing import Dict, List

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class AccessLocalStatisticsInput(ToolInput):
    """Input for accessing local statistics."""
    
    agent_id: str = Field(description="ID of the agent (prefecture)")


class LocalStatistics(ToolOutput):
    """Output containing local statistics data."""
    
    population: int = Field(description="Population of the prefecture")
    age_distribution: Dict[str, float] = Field(
        description="Age distribution of the prefecture",
        default_factory=dict,
    )
    income_level: str = Field(description="Average income level")
    urban_rural_ratio: float = Field(
        description="Ratio of urban to rural population (0-1, 1 being fully urban)",
        ge=0.0,
        le=1.0,
    )
    industry_breakdown: Dict[str, float] = Field(
        description="Industry breakdown by percentage",
        default_factory=dict,
    )
    consumer_trends: List[str] = Field(
        description="List of current consumer trends in the prefecture",
        default_factory=list,
    )
    digital_adoption: float = Field(
        description="Digital adoption rate (0-1)",
        ge=0.0,
        le=1.0,
    )