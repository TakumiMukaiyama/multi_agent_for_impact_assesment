from typing import Dict, Type
from pydantic import BaseModel, Field

from langchain.tools import BaseTool

from src.agents.persona_factory import PersonaFactory


class RetrieveNeighborScoresInput(BaseModel):
    """Input for the retrieve_neighbor_scores tool."""
    agent_id: str = Field(..., description="The prefecture ID to get neighbors for.")
    ad_id: str = Field(..., description="The advertisement ID to get scores for.")


class RetrieveNeighborScoresTool(BaseTool):
    """Tool for retrieving scores from neighboring prefectures."""
    
    name = "retrieve_neighbor_scores"
    description = """
    Get the scores that neighboring prefectures have given for the same advertisement.
    This helps provide context from surrounding areas.
    
    INPUT:
    agent_id: The prefecture ID (e.g., "Tokyo")
    ad_id: The advertisement ID to get scores for
    
    OUTPUT:
    A dictionary mapping neighboring prefecture IDs to their scores.
    """
    args_schema: Type[BaseModel] = RetrieveNeighborScoresInput
    
    def _run(self, agent_id: str, ad_id: str) -> Dict[str, Dict[str, float]]:
        """Get scores from neighboring prefectures.
        
        Args:
            agent_id: The prefecture ID to get neighbors for.
            ad_id: The advertisement ID to get scores for.
        
        Returns:
            A dictionary mapping neighboring prefecture IDs to their scores.
        """
        # Get the neighboring prefectures
        neighbor_ids = PersonaFactory.NEIGHBORS.get(agent_id, [])
        
        # In a real implementation, we would query a database to get the
        # scores that neighboring prefectures have given for this advertisement.
        # For now, we'll just return mock data.
        
        scores = {}
        for neighbor_id in neighbor_ids:
            # Create mock scores
            # In a real implementation, these would come from a database
            scores[neighbor_id] = {
                "liking": 3.5 + (hash(f"{neighbor_id}:{ad_id}") % 30) / 10.0,
                "purchase_intent": 3.0 + (hash(f"{neighbor_id}:{ad_id}:purchase") % 30) / 10.0,
            }
        
        return scores
    
    async def _arun(self, agent_id: str, ad_id: str) -> Dict[str, Dict[str, float]]:
        """Async version of _run."""
        return self._run(agent_id=agent_id, ad_id=ad_id)