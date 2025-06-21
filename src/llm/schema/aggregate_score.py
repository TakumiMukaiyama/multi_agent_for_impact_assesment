from typing import Dict, List, Optional
from pydantic import Field, field_validator

from src.llm.dependancy.base import BaseInput, BaseOutput


class AggregateScoreInput(BaseInput):
    """Input schema for aggregate score calculation.
    
    Used to calculate a weighted average of scores from the current prefecture and its neighbors.
    """
    agent_id: str = Field(
        ..., 
        description="The prefecture ID for which to calculate the aggregate score."
    )
    ad_id: str = Field(
        ..., 
        description="The ID of the advertisement."
    )
    own_scores: Dict[str, float] = Field(
        ..., 
        description="The prefecture's own scores: {'liking': float, 'purchase_intent': float}"
    )
    neighbor_scores: Dict[str, Dict[str, float]] = Field(
        ..., 
        description="Scores from neighboring prefectures: {neighbor_id: {'liking': float, 'purchase_intent': float}, ...}"
    )
    weights: Optional[Dict[str, float]] = Field(
        None, 
        description="Optional custom weights for each prefecture: {prefecture_id: weight, ...}. Default is equal weights."
    )


class AggregateScoreOutput(BaseOutput):
    """Output schema for aggregate score calculation.
    
    Provides the weighted average scores and the breakdown of contributions.
    """
    agent_id: str = Field(
        ..., 
        description="The prefecture ID for which the aggregate score was calculated."
    )
    ad_id: str = Field(
        ..., 
        description="The ID of the advertisement."
    )
    aggregate_liking: float = Field(
        ..., 
        description="The aggregate liking score (0.0-5.0).",
        ge=0.0,
        le=5.0
    )
    aggregate_purchase_intent: float = Field(
        ..., 
        description="The aggregate purchase intent score (0.0-5.0).",
        ge=0.0,
        le=5.0
    )
    weights_used: Dict[str, float] = Field(
        ..., 
        description="The weights used for each prefecture."
    )
    neighbors_used: List[str] = Field(
        ..., 
        description="List of neighboring prefecture IDs used in the calculation."
    )
    
    @field_validator('aggregate_liking', 'aggregate_purchase_intent')
    def validate_score_range(cls, v):
        """Ensure scores are within allowed range."""
        if not 0.0 <= v <= 5.0:
            raise ValueError(f"Score must be between 0.0 and 5.0, got {v}")
        return v