"""Schemas for analyze ad content tool."""

from typing import List

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class AnalyzeAdContentInput(ToolInput):
    """Input for analyzing ad content."""

    agent_id: str = Field(description="ID of the agent using the tool")
    ad_content: str = Field(description="Content of the ad to analyze")


class AnalyzeAdContentOutput(ToolOutput):
    """Output containing ad content analysis."""

    category: str = Field(description="Primary category of the advertisement")
    subcategories: List[str] = Field(description="Secondary categories or tags", default_factory=list)
    target_demographic: str = Field(description="Identified target demographic")
    key_selling_points: List[str] = Field(description="Key selling points identified in the ad", default_factory=list)
    emotional_appeal: str = Field(description="Type of emotional appeal used")
    tone: str = Field(description="Overall tone of the advertisement")
    price_emphasis: float = Field(description="Emphasis on price/value (0.0-1.0)", default=0.0, ge=0.0, le=1.0)
    quality_emphasis: float = Field(
        description="Emphasis on quality/premium aspects (0.0-1.0)", default=0.0, ge=0.0, le=1.0
    )
