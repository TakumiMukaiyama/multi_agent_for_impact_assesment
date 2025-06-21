"""Schemas for ad evaluation."""
from typing import Dict, List, Optional
from pydantic import Field

from src.llm.dependancy.base import BaseInput, BaseOutput


class AdEvaluationInput(BaseInput):
    """Input for the ad evaluation chain."""
    
    ad_id: str = Field(description="Unique identifier for the advertisement")
    ad_content: str = Field(description="The content of the ad to be evaluated")
    agent_id: str = Field(description="The agent ID (prefecture) evaluating the ad")
    agent_profile: Dict = Field(description="Profile information about the agent/region")
    neighbor_scores: Optional[Dict[str, Dict[str, float]]] = Field(
        default=None,
        description="Scores from neighboring prefectures (if available)"
    )
    

class AdEvaluationOutput(BaseOutput):
    """Output from the ad evaluation chain."""
    
    liking: float = Field(
        description="Score indicating how much the target audience would like the ad (0-5)",
        ge=0.0,
        le=5.0
    )
    purchase_intent: float = Field(
        description="Score indicating purchase intent for the advertised product (0-5)",
        ge=0.0,
        le=5.0
    )
    commentary: str = Field(
        description="Detailed commentary explaining the rationale behind the scores"
    )
    neighbors_considered: List[str] = Field(
        default_factory=list,
        description="List of neighboring prefectures whose scores were considered"
    )