"""Schemas for analyze_ad_content tool."""
from typing import List

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class AnalyzeAdContentInput(ToolInput):
    """Input for analyzing ad content."""
    
    agent_id: str = Field(description="ID of the agent using the tool")
    ad_id: str = Field(description="ID of the ad to analyze")
    ad_content: str = Field(description="Content of the ad to analyze")


class AnalyzeAdContentOutput(ToolOutput):
    """Output from ad content analysis."""
    
    category: str = Field(description="Main category of the advertisement")
    subcategories: List[str] = Field(
        description="Subcategories the ad fits into", 
        default_factory=list
    )
    target_demographic: List[str] = Field(
        description="Target demographic groups for the ad",
        default_factory=list
    )
    key_selling_points: List[str] = Field(
        description="Key selling points or features emphasized in the ad",
        default_factory=list
    )
    emotional_appeal: List[str] = Field(
        description="Types of emotional appeals used in the ad",
        default_factory=list
    )
    tone: str = Field(description="Overall tone of the advertisement")
    price_emphasis: float = Field(
        description="Degree of emphasis on price (0-1)",
        ge=0.0,
        le=1.0
    )
    quality_emphasis: float = Field(
        description="Degree of emphasis on quality (0-1)",
        ge=0.0,
        le=1.0
    )