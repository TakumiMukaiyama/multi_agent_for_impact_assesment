from typing import List, Optional
from pydantic import Field, field_validator

from src.llm.dependancy.base import BaseInput, BaseOutput


class AdEvaluationInput(BaseInput):
    """Input schema for advertisement evaluation by prefecture agents.
    
    This is used when an agent evaluates an advertisement based on its prefecture's characteristics.
    """
    agent_id: str = Field(
        ..., 
        description="The prefecture ID of the agent (e.g., 'Tokyo', 'Osaka')."
    )
    ad_id: str = Field(
        ..., 
        description="The ID of the advertisement being evaluated."
    )
    ad_title: str = Field(
        ..., 
        description="The title of the advertisement."
    )
    ad_content: str = Field(
        ..., 
        description="The textual content of the advertisement."
    )
    ad_category: Optional[str] = Field(
        None, 
        description="The category of the advertisement (e.g., 'Technology', 'Fashion', 'Food')."
    )
    use_neighbors: bool = Field(
        True, 
        description="Whether to use neighboring prefecture evaluations in the assessment."
    )


class AdEvaluationOutput(BaseOutput):
    """Output schema for advertisement evaluation by prefecture agents.
    
    This is the structured response that each prefecture agent produces when evaluating an ad.
    """
    agent_id: str = Field(
        ..., 
        description="The prefecture ID of the agent that produced this evaluation."
    )
    ad_id: str = Field(
        ..., 
        description="The ID of the evaluated advertisement."
    )
    liking: float = Field(
        ..., 
        description="Score indicating how much the prefecture's population would like the advertisement (0.0-5.0).",
        ge=0.0,
        le=5.0
    )
    purchase_intent: float = Field(
        ..., 
        description="Score indicating the purchase intent level of the prefecture's population (0.0-5.0).",
        ge=0.0,
        le=5.0
    )
    neighbors_used: List[str] = Field(
        default_factory=list, 
        description="List of neighboring prefecture IDs whose evaluations influenced this assessment."
    )
    commentary: str = Field(
        ..., 
        description="Human-readable explanation of the evaluation result, explaining the scores."
    )
    
    @field_validator('liking', 'purchase_intent')
    def validate_score_range(cls, v):
        """Ensure scores are within allowed range."""
        if not 0.0 <= v <= 5.0:
            raise ValueError(f"Score must be between 0.0 and 5.0, got {v}")
        return v