from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from src.llm.dependancy.base import BaseInput, BaseOutput


class AdHistoryInput(BaseInput):
    """Input schema for fetching advertisement history.
    
    Used to retrieve the history of advertisements shown in a specific prefecture.
    """
    agent_id: str = Field(
        ..., 
        description="The prefecture ID for which to fetch advertisement history."
    )
    limit: int = Field(
        10, 
        description="Maximum number of advertisements to retrieve.",
        ge=1,
        le=100
    )
    category: Optional[str] = Field(
        None, 
        description="Optional category filter for the advertisements."
    )
    start_date: Optional[datetime] = Field(
        None, 
        description="Optional start date for filtering advertisements."
    )
    end_date: Optional[datetime] = Field(
        None, 
        description="Optional end date for filtering advertisements."
    )


class AdHistoryItem(BaseModel):
    """Individual advertisement history item."""
    ad_id: str = Field(
        ..., 
        description="The advertisement ID."
    )
    title: str = Field(
        ..., 
        description="The advertisement title."
    )
    content: str = Field(
        ..., 
        description="The advertisement content."
    )
    category: Optional[str] = Field(
        None, 
        description="The advertisement category."
    )
    shown_at: datetime = Field(
        ..., 
        description="The date and time when the advertisement was shown."
    )
    liking_score: Optional[float] = Field(
        None, 
        description="The liking score if evaluated."
    )
    purchase_intent_score: Optional[float] = Field(
        None, 
        description="The purchase intent score if evaluated."
    )


class AdHistoryOutput(BaseOutput):
    """Output schema for advertisement history.
    
    Provides a list of advertisements shown in the prefecture.
    """
    agent_id: str = Field(
        ..., 
        description="The prefecture ID for which the history was fetched."
    )
    total_count: int = Field(
        ..., 
        description="Total number of advertisements matching the criteria."
    )
    ads: List[AdHistoryItem] = Field(
        ..., 
        description="List of advertisements in the history."
    )
    category_counts: Dict[str, int] = Field(
        ..., 
        description="Count of advertisements per category."
    )