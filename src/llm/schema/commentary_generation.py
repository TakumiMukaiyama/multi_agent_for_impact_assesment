from typing import Dict, Optional
from pydantic import Field

from src.llm.dependancy.base import BaseInput, BaseOutput


class CommentaryGenerationInput(BaseInput):
    """Input schema for generating a natural language commentary.
    
    This is used to generate a natural language explanation of an advertisement evaluation.
    """
    agent_id: str = Field(
        ..., 
        description="The prefecture ID for which to generate commentary."
    )
    ad_id: str = Field(
        ..., 
        description="The ID of the advertisement."
    )
    ad_content: str = Field(
        ..., 
        description="The content of the advertisement."
    )
    agent_profile: Dict = Field(
        ..., 
        description="The demographic and preference profile of the prefecture."
    )
    liking_score: float = Field(
        ..., 
        description="The liking score (0.0-5.0) given to the advertisement.",
        ge=0.0,
        le=5.0
    )
    purchase_intent_score: float = Field(
        ..., 
        description="The purchase intent score (0.0-5.0) given to the advertisement.",
        ge=0.0,
        le=5.0
    )
    cultural_affinity: Optional[Dict] = Field(
        None, 
        description="Cultural affinity assessment results if available."
    )


class CommentaryGenerationOutput(BaseOutput):
    """Output schema for the generated commentary.
    
    Provides a natural language commentary on the advertisement evaluation.
    """
    agent_id: str = Field(
        ..., 
        description="The prefecture ID for which the commentary was generated."
    )
    ad_id: str = Field(
        ..., 
        description="The ID of the advertisement."
    )
    commentary: str = Field(
        ..., 
        description="A natural language explanation of the advertisement evaluation."
    )
    positive_aspects: str = Field(
        ..., 
        description="Positive aspects of the advertisement from the prefecture's perspective."
    )
    negative_aspects: str = Field(
        ..., 
        description="Negative aspects or areas for improvement from the prefecture's perspective."
    )
    local_perspective: str = Field(
        ..., 
        description="Insights specific to the local culture and preferences of the prefecture."
    )