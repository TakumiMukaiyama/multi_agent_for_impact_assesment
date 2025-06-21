"""Schemas for generate commentary tool."""

from typing import Any, Dict, List, Optional

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class GenerateCommentaryInput(ToolInput):
    """Input for generating commentary on an advertisement."""

    agent_id: str = Field(description="ID of the agent (prefecture)")
    ad_content: str = Field(description="Content of the ad to comment on")
    agent_profile: Dict[str, Any] = Field(description="Profile of the agent (prefecture)")
    liking_score: Optional[float] = Field(description="Liking score (0-5)", default=3.0, ge=0.0, le=5.0)
    purchase_intent_score: Optional[float] = Field(
        description="Purchase intent score (0-5)", default=3.0, ge=0.0, le=5.0
    )
    cultural_affinity: Optional[float] = Field(description="Cultural affinity score (0-1)", default=None)


class GenerateCommentaryOutput(ToolOutput):
    """Output containing generated commentary."""

    commentary: str = Field(description="Detailed commentary on the advertisement")
    positive_aspects: List[str] = Field(
        description="Positive aspects of the ad from the region's perspective", default_factory=list
    )
    negative_aspects: List[str] = Field(
        description="Negative aspects of the ad from the region's perspective", default_factory=list
    )
    improvement_suggestions: List[str] = Field(
        description="Suggestions for improving the ad for this region", default_factory=list
    )
