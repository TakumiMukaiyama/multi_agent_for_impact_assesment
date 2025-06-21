from typing import Dict, List, Optional
from pydantic import Field

from src.llm.dependancy.base import BaseInput, BaseOutput


class AdContentAnalysisInput(BaseInput):
    """Input schema for advertisement content analysis.
    
    This is used when analyzing the content of an advertisement to extract
    key features, themes, and target demographics.
    """
    ad_id: str = Field(
        ..., 
        description="The ID of the advertisement to analyze."
    )
    ad_title: str = Field(
        ..., 
        description="The title of the advertisement."
    )
    ad_content: str = Field(
        ..., 
        description="The textual content of the advertisement to analyze."
    )
    ad_category: Optional[str] = Field(
        None, 
        description="The category of the advertisement if known."
    )


class AdContentAnalysisOutput(BaseOutput):
    """Output schema for advertisement content analysis.
    
    Contains structured information extracted from the advertisement content.
    """
    ad_id: str = Field(
        ..., 
        description="The ID of the analyzed advertisement."
    )
    primary_category: str = Field(
        ..., 
        description="The primary category of the advertisement."
    )
    secondary_categories: List[str] = Field(
        default_factory=list, 
        description="Additional categories that apply to this advertisement."
    )
    target_demographics: Dict[str, float] = Field(
        ..., 
        description="Target demographic groups with estimated relevance scores (0.0-1.0)."
    )
    key_themes: List[str] = Field(
        ..., 
        description="Main themes or topics addressed in the advertisement."
    )
    key_benefits: List[str] = Field(
        ..., 
        description="Key benefits or value propositions highlighted in the advertisement."
    )
    emotional_appeal: Dict[str, float] = Field(
        ..., 
        description="Emotional appeals used in the ad with estimated strength scores (0.0-1.0)."
    )
    cultural_context: List[str] = Field(
        default_factory=list, 
        description="Cultural contexts or references used in the advertisement."
    )
    tone: str = Field(
        ..., 
        description="Overall tone of the advertisement (e.g., 'informative', 'humorous', 'serious')."
    )
    call_to_action: Optional[str] = Field(
        None, 
        description="The main call to action in the advertisement, if present."
    )