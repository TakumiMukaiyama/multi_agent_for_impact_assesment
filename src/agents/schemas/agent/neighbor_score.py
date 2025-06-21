from pydantic import BaseModel, Field

class NeighborScore(BaseModel):
    """Score provided by a neighboring agent."""

    agent_id: str = Field(description="Neighboring agent identifier")
    liking: float = Field(description="Liking score (0-5)")
    purchase_intent: float = Field(description="Purchase intent score (0-5)")
