"""Schemas for fetch_previous_ads tool."""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class FetchPreviousAdsInput(ToolInput):
    """Input for fetching previous ads."""
    
    agent_id: str = Field(description="ID of the agent (prefecture)")
    ad_category: Optional[str] = Field(
        description="Optional category to filter ads by",
        default=None
    )
    limit: int = Field(
        description="Maximum number of ads to retrieve",
        default=10,
        ge=1,
        le=50
    )


class AdRecord(BaseModel):
    """Model for a single ad record."""
    
    ad_id: str = Field(description="Unique ID for the advertisement")
    content: str = Field(description="Content of the advertisement")
    category: Optional[str] = Field(description="Category of the advertisement", default=None)
    shown_at: str = Field(description="When the ad was shown (ISO datetime)")
    liking_score: Optional[float] = Field(
        description="Average liking score if available (0-5)",
        default=None
    )
    purchase_intent_score: Optional[float] = Field(
        description="Average purchase intent score if available (0-5)",
        default=None
    )


class FetchPreviousAdsOutput(ToolOutput):
    """Output containing fetched previous ads."""
    
    ads: List[AdRecord] = Field(
        description="List of previous ads",
        default_factory=list
    )
    total_count: int = Field(description="Total number of ads available")
    average_liking: Optional[float] = Field(
        description="Average liking score across all ads (if available)",
        default=None
    )
    average_purchase_intent: Optional[float] = Field(
        description="Average purchase intent score across all ads (if available)",
        default=None
    )
    category_distribution: Optional[Dict[str, int]] = Field(
        description="Distribution of ad categories",
        default=None
    )