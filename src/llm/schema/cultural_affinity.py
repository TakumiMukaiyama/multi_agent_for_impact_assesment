from typing import Dict
from pydantic import Field, field_validator

from src.llm.dependancy.base import BaseInput, BaseOutput


class CulturalAffinityInput(BaseInput):
    """Input schema for cultural affinity assessment.
    
    This is used to evaluate how well an advertisement aligns with a prefecture's
    cultural and demographic characteristics.
    """
    agent_id: str = Field(
        ..., 
        description="The prefecture ID for which to assess cultural affinity."
    )
    ad_id: str = Field(
        ..., 
        description="The ID of the advertisement being evaluated."
    )
    ad_content: str = Field(
        ..., 
        description="The content of the advertisement."
    )
    agent_profile: Dict = Field(
        ..., 
        description="The demographic and preference profile of the prefecture."
    )


class CulturalAffinityOutput(BaseOutput):
    """Output schema for cultural affinity assessment.
    
    Provides a detailed breakdown of how well the advertisement aligns with
    various aspects of the prefecture's culture and demographics.
    """
    agent_id: str = Field(
        ..., 
        description="The prefecture ID for which the assessment was made."
    )
    ad_id: str = Field(
        ..., 
        description="The ID of the evaluated advertisement."
    )
    overall_affinity_score: float = Field(
        ..., 
        description="Overall cultural affinity score (0.0-1.0).",
        ge=0.0,
        le=1.0
    )
    demographic_alignment: Dict[str, float] = Field(
        ..., 
        description="Alignment scores with demographic segments of the prefecture (0.0-1.0)."
    )
    preference_alignment: Dict[str, float] = Field(
        ..., 
        description="Alignment scores with preference categories of the prefecture (0.0-1.0)."
    )
    regional_relevance: float = Field(
        ..., 
        description="How relevant the advertisement is to the region's specific characteristics (0.0-1.0).",
        ge=0.0,
        le=1.0
    )
    explanation: str = Field(
        ..., 
        description="Explanation of the cultural affinity assessment."
    )
    
    @field_validator('overall_affinity_score', 'regional_relevance')
    def validate_score_range(cls, v):
        """Ensure scores are within allowed range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Affinity score must be between 0.0 and 1.0, got {v}")
        return v
        
    @field_validator('demographic_alignment', 'preference_alignment')
    def validate_alignment_scores(cls, v):
        """Validate alignment scores."""
        for key, score in v.items():
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"Alignment score for {key} must be between 0.0 and 1.0, got {score}")
        return v