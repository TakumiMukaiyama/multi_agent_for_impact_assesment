"""Schemas for estimate_cultural_affinity tool."""
from typing import Dict, List, Any, Optional

from pydantic import Field, BaseModel

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class AlignmentFactor(BaseModel):
    """Model for a cultural alignment factor."""
    
    factor: str = Field(description="Description of the alignment factor")
    strength: float = Field(
        description="Strength of the alignment (0-1)",
        ge=0.0,
        le=1.0
    )


class EstimateCulturalAffinityInput(ToolInput):
    """Input for estimating cultural affinity."""
    
    agent_id: str = Field(description="ID of the agent (prefecture)")
    ad_content: str = Field(description="Content of the ad to evaluate")
    agent_profile: Dict[str, Any] = Field(
        description="Profile of the agent (prefecture)"
    )
    local_statistics: Optional[Dict[str, Any]] = Field(
        description="Additional local statistics for the prefecture",
        default=None
    )


class EstimateCulturalAffinityOutput(ToolOutput):
    """Output for cultural affinity estimation."""
    
    affinity_score: float = Field(
        description="Overall cultural affinity score (0-1)",
        ge=0.0,
        le=1.0
    )
    alignment_factors: List[AlignmentFactor] = Field(
        description="Factors that align between the ad and region",
        default_factory=list
    )
    misalignment_factors: List[AlignmentFactor] = Field(
        description="Factors that don't align between the ad and region",
        default_factory=list
    )
    regional_considerations: str = Field(
        description="Additional regional considerations"
    )