"""Pydantic models for agent input and output."""

from typing import Dict, List, Optional

from pydantic import Field

from src.agents.schemas.agent.agent_profile import AgentProfile
from src.llm.dependancy.base import BaseInput, BaseOutput


class AdEvaluationInput(BaseInput):
    """Input for ad evaluation by an agent."""

    agent_id: str = Field(description="Agent identifier (prefectural code)")
    ad_id: str = Field(description="Ad identifier")
    ad_content: str = Field(description="Ad content text")
    ad_category: Optional[str] = Field(description="Category of the ad", default=None)
    agent_profile: AgentProfile = Field(description="Agent profile information")
    neighbor_scores: Optional[Dict[str, Dict[str, float]]] = Field(
        description="Scores from neighboring prefectures", default=None
    )


class AdEvaluationOutput(BaseOutput):
    """Output from ad evaluation by an agent."""

    agent_id: str = Field(description="Agent identifier that evaluated the ad")
    ad_id: str = Field(description="Ad identifier that was evaluated")
    liking: float = Field(
        description="Liking score (0-5)",
        ge=0.0,
        le=5.0,
    )
    purchase_intent: float = Field(
        description="Purchase intent score (0-5)",
        ge=0.0,
        le=5.0,
    )
    neighbors_used: List[str] = Field(
        description="List of neighboring agent IDs whose scores were used",
        default_factory=list,
    )
    commentary: str = Field(description="Textual commentary explaining the evaluation")
