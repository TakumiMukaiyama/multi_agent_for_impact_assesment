"""Schemas for cultural affinity evaluation."""
from typing import Dict, List
from pydantic import Field

from src.llm.dependancy.base import BaseInput, BaseOutput


class CulturalAffinityInput(BaseInput):
    """Input for the cultural affinity evaluation chain."""
    
    ad_content: str = Field(description="The content of the ad to be evaluated")
    agent_profile: Dict = Field(description="Profile information about the agent/region")
    

class CulturalAffinityOutput(BaseOutput):
    """Output from the cultural affinity evaluation chain."""
    
    affinity_score: float = Field(
        description="Overall cultural affinity score between the ad and region (0-1)",
        ge=0.0,
        le=1.0
    )
    alignment_factors: List[Dict[str, float]] = Field(
        description="Cultural factors that align between the ad and region with their strength",
        default_factory=list
    )
    misalignment_factors: List[Dict[str, float]] = Field(
        description="Cultural factors that don't align between the ad and region with their strength",
        default_factory=list
    )
    regional_considerations: str = Field(
        description="Additional regional considerations related to cultural fit"
    )