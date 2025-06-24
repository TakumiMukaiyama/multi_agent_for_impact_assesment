"""Schemas for retrieve neighbor scores tool."""

from typing import List, Optional

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class NeighborScore(ToolOutput):
    """Score data from a neighboring agent."""

    neighbor_id: str = Field(description="ID of the neighboring agent")
    ad_id: str = Field(description="ID of the advertisement")
    liking_score: float = Field(description="Liking score from neighbor (0-5)", ge=0.0, le=5.0)
    purchase_intent_score: float = Field(description="Purchase intent score from neighbor (0-5)", ge=0.0, le=5.0)
    timestamp: str = Field(description="When the score was recorded (ISO format)")
    confidence: Optional[float] = Field(
        description="Confidence in the score quality (0-1)", default=None, ge=0.0, le=1.0
    )


class RetrieveNeighborScoresInput(ToolInput):
    """Input for retrieving neighbor scores."""

    agent_id: str = Field(description="ID of the requesting agent (prefecture)")
    ad_id: str = Field(description="ID of the advertisement to get scores for")
    max_neighbors: Optional[int] = Field(
        description="Maximum number of neighbors to retrieve scores from", default=5, ge=1, le=20
    )


class RetrieveNeighborScoresOutput(ToolOutput):
    """Output containing neighbor scores."""

    neighbor_scores: List[NeighborScore] = Field(description="Scores from neighboring agents", default_factory=list)
    neighbors_found: int = Field(description="Number of neighbors with scores found")
    average_liking: Optional[float] = Field(description="Average liking score across neighbors", default=None)
    average_purchase_intent: Optional[float] = Field(
        description="Average purchase intent score across neighbors", default=None
    )
    neighbor_ids: List[str] = Field(description="List of neighbor IDs found", default_factory=list)
