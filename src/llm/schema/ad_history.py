"""Schemas for ad history analysis."""
from typing import Dict, List, Optional
from pydantic import Field
from datetime import datetime

from src.llm.dependancy.base import BaseInput, BaseOutput


class AdHistoryInput(BaseInput):
    """Input for the ad history analysis chain."""
    
    agent_id: str = Field(description="The agent ID (prefecture) to retrieve ad history for")
    ad_category: Optional[str] = Field(
        default=None,
        description="Optional category to filter ads by"
    )
    limit: Optional[int] = Field(
        default=10,
        description="Maximum number of historical ads to retrieve"
    )
    

class HistoricalAd(BaseOutput):
    """Structure for a single historical ad."""
    
    ad_id: str = Field(description="Unique identifier for the advertisement")
    content: str = Field(description="Content of the advertisement")
    category: Optional[str] = Field(description="Category of the advertisement")
    shown_at: datetime = Field(description="When the ad was shown")
    liking_score: Optional[float] = Field(
        default=None,
        description="Liking score if available (0-5)"
    )
    purchase_intent_score: Optional[float] = Field(
        default=None,
        description="Purchase intent score if available (0-5)"
    )


class AdHistoryOutput(BaseOutput):
    """Output from the ad history analysis chain."""
    
    ads: List[HistoricalAd] = Field(
        description="List of historical ads",
        default_factory=list
    )
    average_liking: Optional[float] = Field(
        default=None,
        description="Average liking score of historical ads (if scores available)"
    )
    average_purchase_intent: Optional[float] = Field(
        default=None,
        description="Average purchase intent score of historical ads (if scores available)"
    )
    category_distribution: Optional[Dict[str, int]] = Field(
        default=None,
        description="Distribution of ad categories in history"
    )