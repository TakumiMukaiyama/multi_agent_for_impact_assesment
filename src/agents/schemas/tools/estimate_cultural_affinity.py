"""Schemas for estimate cultural affinity tool."""

from typing import List

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class AlignmentFactor(ToolOutput):
    """Factor that affects cultural alignment."""

    factor: str = Field(description="Description of the alignment factor")
    strength: float = Field(description="Strength of this factor (-1.0 to 1.0)", ge=-1.0, le=1.0)


class EstimateCulturalAffinityInput(ToolInput):
    """Input for estimating cultural affinity."""

    agent_id: str = Field(description="ID of the agent (prefecture)")
    ad_content: str = Field(description="Content of the ad to evaluate")


class EstimateCulturalAffinityOutput(ToolOutput):
    """Output containing cultural affinity estimation."""

    affinity_score: float = Field(description="Cultural affinity score (0.0-1.0)", ge=0.0, le=1.0)
    confidence: float = Field(description="Confidence in the estimation (0.0-1.0)", ge=0.0, le=1.0)
    alignment_factors: List[AlignmentFactor] = Field(
        description="Factors that contribute to the affinity score", default_factory=list
    )
    regional_insights: str = Field(description="Insights about how this ad aligns with regional culture")
