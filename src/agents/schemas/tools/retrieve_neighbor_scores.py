"""Schemas for retrieve_neighbor_scores tool."""
from typing import Dict, List

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class RetrieveNeighborScoresInput(ToolInput):
    """Input for retrieving scores from neighboring prefectures."""
    
    agent_id: str = Field(description="ID of the agent (prefecture)")
    ad_id: str = Field(description="ID of the ad to retrieve scores for")


class RetrieveNeighborScoresOutput(ToolOutput):
    """Output containing scores from neighboring prefectures."""
    
    neighbor_scores: Dict[str, Dict[str, float]] = Field(
        description="Scores from neighboring prefectures",
        default_factory=dict
    )
    neighbors: List[str] = Field(
        description="List of neighboring prefecture IDs",
        default_factory=list
    )