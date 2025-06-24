from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AgentProfile(BaseModel):
    """Agent profile containing information about the agent's persona."""

    agent_id: str = Field(description="Unique identifier for the agent (e.g., 'Tokyo')")
    age_distribution: Dict[str, float] = Field(
        description="Age distribution of the region (e.g., {'20s': 0.3, '30s': 0.4})",
        default_factory=dict,
    )
    preferences: List[str] = Field(
        description="List of preferences characterizing the agent (e.g., 'price-sensitive')",
        default_factory=list,
    )
    cluster: str = Field(
        description="Cluster the agent belongs to (e.g., 'urban', 'rural')",
        default="",
    )
    population: Optional[int] = Field(description="Population of the region", default=None)
    region: Optional[str] = Field(description="Region the agent represents (e.g., 'Kanto')", default=None)
