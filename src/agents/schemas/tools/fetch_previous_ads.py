"""Schemas for fetch previous ads tool."""

from typing import Any, Dict, List, Optional

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class AdRecord(ToolOutput):
    """Record of a previous advertisement."""

    ad_id: str = Field(description="Advertisement ID")
    ad_content: str = Field(description="Content of the advertisement")
    category: str = Field(description="Category of the advertisement")
    brand: Optional[str] = Field(description="Brand name", default=None)
    created_date: str = Field(description="Creation date (ISO format)")
    liking_scores: Dict[str, float] = Field(description="Liking scores from different regions", default_factory=dict)
    purchase_intent_scores: Dict[str, float] = Field(
        description="Purchase intent scores from different regions", default_factory=dict
    )


class FetchPreviousAdsInput(ToolInput):
    """Input for fetching previous advertisements."""

    agent_id: str = Field(description="ID of the agent requesting ads")
    category: Optional[str] = Field(description="Category filter for advertisements", default=None)
    brand: Optional[str] = Field(description="Brand filter for advertisements", default=None)
    limit: Optional[int] = Field(description="Maximum number of ads to fetch", default=10, ge=1, le=100)


class FetchPreviousAdsOutput(ToolOutput):
    """Output containing previous advertisements."""

    ads: List[AdRecord] = Field(description="List of previous advertisements", default_factory=list)
    total_count: int = Field(description="Total number of ads matching criteria")
    filters_applied: Dict[str, Any] = Field(description="Filters that were applied", default_factory=dict)
