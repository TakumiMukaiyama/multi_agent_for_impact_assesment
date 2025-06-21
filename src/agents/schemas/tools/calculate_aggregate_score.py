"""Schemas for calculate_aggregate_score tool."""
from typing import Dict, Any

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class CalculateAggregateScoreInput(ToolInput):
    """Input for calculating aggregate scores."""
    
    agent_id: str = Field(description="ID of the agent (prefecture)")
    own_scores: Dict[str, float] = Field(
        description="The agent's own scores for liking and purchase intent"
    )
    neighbor_scores: Dict[str, Dict[str, float]] = Field(
        description="Scores from neighboring prefectures"
    )
    agent_profile: Dict[str, Any] = Field(
        description="Profile of the agent (prefecture)"
    )


class CalculateAggregateScoreOutput(ToolOutput):
    """Output containing aggregate scores."""
    
    aggregate_liking: float = Field(
        description="Aggregate liking score (0-5)",
        ge=0.0,
        le=5.0
    )
    aggregate_purchase_intent: float = Field(
        description="Aggregate purchase intent score (0-5)",
        ge=0.0,
        le=5.0
    )
    weighting_explanation: str = Field(
        description="Explanation of how neighbors were weighted"
    )
    neighbor_influence: Dict[str, float] = Field(
        description="Influence weight of each neighbor",
        default_factory=dict
    )