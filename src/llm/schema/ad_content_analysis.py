"""Schemas for ad content analysis."""
from typing import List
from pydantic import Field

from src.llm.dependancy.base import BaseInput, BaseOutput


class AdContentAnalysisInput(BaseInput):
    """Input for the ad content analysis chain."""
    
    ad_id: str = Field(description="Unique identifier for the advertisement")
    ad_content: str = Field(description="The content of the ad to be analyzed")
    


class AdContentAnalysisOutput(BaseOutput):
    """Output from the ad content analysis chain."""
    
    category: str = Field(
        description="Main category of the advertisement"
    )
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
    tone: str = Field(
        description="Overall tone of the advertisement"
    )
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