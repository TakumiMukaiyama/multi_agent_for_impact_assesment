"""Schemas for calculate aggregate score tool."""

from typing import Dict, Optional

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class CalculateAggregateScoreInput(ToolInput):
    """Input for calculating aggregate scores."""

    agent_id: str = Field(description="ID of the agent (prefecture)")
    own_liking: float = Field(description="Agent's own liking score (0-5)", ge=0.0, le=5.0)
    own_purchase_intent: float = Field(description="Agent's own purchase intent score (0-5)", ge=0.0, le=5.0)
    neighbor_scores: Optional[Dict[str, Dict[str, float]]] = Field(
        description="Neighbor scores in format {agent_id: {liking: float, purchase_intent: float}}", default=None
    )


class CalculateAggregateScoreOutput(ToolOutput):
    """Output containing aggregate scores."""

    aggregate_liking: float = Field(description="Aggregate liking score (0-5)", ge=0.0, le=5.0)
    aggregate_purchase_intent: float = Field(description="Aggregate purchase intent score (0-5)", ge=0.0, le=5.0)
    weighting_explanation: str = Field(description="Explanation of how neighbors were weighted")
    neighbor_influence: Dict[str, float] = Field(description="Influence weight of each neighbor", default_factory=dict)
