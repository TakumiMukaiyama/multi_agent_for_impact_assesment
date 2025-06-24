"""Schemas for commentary generation."""
from typing import Dict, List, Optional
from pydantic import Field

from src.llm.dependancy.base import BaseInput, BaseOutput


class CommentaryGenerationInput(BaseInput):
    """Input for the commentary generation chain."""
    
    ad_content: str = Field(description="The content of the ad to comment on")
    agent_profile: Dict = Field(description="Profile information about the agent/region")
    liking_score: float = Field(
        description="The liking score given to the ad (0-5)",
        ge=0.0,
        le=5.0
    )
    purchase_intent_score: float = Field(
        description="The purchase intent score given to the ad (0-5)",
        ge=0.0,
        le=5.0
    )
    cultural_affinity: Optional[float] = Field(
        default=None,
        description="Cultural affinity score (0-1) if available"
    )
    

class CommentaryGenerationOutput(BaseOutput):
    """Output from the commentary generation chain."""
    
    commentary: str = Field(
        description="Detailed commentary explaining the evaluation of the ad from the perspective of the region"
    )
    positive_aspects: List[str] = Field(
        description="Positive aspects of the ad from the region's perspective",
        default_factory=list
    )
    negative_aspects: List[str] = Field(
        description="Negative aspects of the ad from the region's perspective",
        default_factory=list
    )
    improvement_suggestions: List[str] = Field(
        description="Suggestions for improving the ad for this region",
        default_factory=list
    )