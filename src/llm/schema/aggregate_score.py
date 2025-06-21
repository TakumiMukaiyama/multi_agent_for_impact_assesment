"""Schemas for aggregate score calculation."""
from typing import Dict
from pydantic import Field

from src.llm.dependancy.base import BaseInput, BaseOutput


class AggregateScoreInput(BaseInput):
    """Input for the aggregate score calculation chain."""
    
    own_scores: Dict[str, float] = Field(
        description="The agent's own scores for liking and purchase intent"
    )
    neighbor_scores: Dict[str, Dict[str, float]] = Field(
        description="Scores from neighboring prefectures"
    )
    agent_profile: Dict = Field(
        description="Profile information about the agent/region"
    )
    

class AggregateScoreOutput(BaseOutput):
    """Output from the aggregate score calculation chain."""
    
    aggregate_liking: float = Field(
        description="Aggregated liking score incorporating neighbor scores (0-5)",
        ge=0.0,
        le=5.0
    )
    aggregate_purchase_intent: float = Field(
        description="Aggregated purchase intent score incorporating neighbor scores (0-5)",
        ge=0.0,
        le=5.0
    )
    weighting_explanation: str = Field(
        description="Explanation of how neighbors were weighted in the aggregation"
    )
    neighbor_influence: Dict[str, float] = Field(
        description="Influence weight of each neighbor on the final scores",
        default_factory=dict
    )