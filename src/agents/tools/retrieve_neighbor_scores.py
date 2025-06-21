"""Tool for retrieving scores from neighboring prefectures."""

from typing import List, Optional

from pydantic import Field

from src.agents.tools.base import BaseAgentTool, ToolInput, ToolOutput
from src.utils.logger import get_logger

logger = get_logger(__name__)


class NeighborScore(ToolOutput):
    """Score data from a neighboring agent."""

    neighbor_id: str = Field(description="ID of the neighboring agent")
    ad_id: str = Field(description="ID of the advertisement")
    liking_score: float = Field(description="Liking score from neighbor (0-5)", ge=0.0, le=5.0)
    purchase_intent_score: float = Field(description="Purchase intent score from neighbor (0-5)", ge=0.0, le=5.0)
    timestamp: str = Field(description="When the score was recorded (ISO format)")
    confidence: Optional[float] = Field(
        description="Confidence in the score quality (0-1)", default=None, ge=0.0, le=1.0
    )


class RetrieveNeighborScoresInput(ToolInput):
    """Input for retrieving neighbor scores."""

    agent_id: str = Field(description="ID of the requesting agent (prefecture)")
    ad_id: str = Field(description="ID of the advertisement to get scores for")
    max_neighbors: Optional[int] = Field(
        description="Maximum number of neighbors to retrieve scores from", default=5, ge=1, le=20
    )


class RetrieveNeighborScoresOutput(ToolOutput):
    """Output containing neighbor scores."""

    neighbor_scores: List[NeighborScore] = Field(description="Scores from neighboring agents", default_factory=list)
    neighbors_found: int = Field(description="Number of neighbors with scores found")
    average_liking: Optional[float] = Field(description="Average liking score across neighbors", default=None)
    average_purchase_intent: Optional[float] = Field(
        description="Average purchase intent score across neighbors", default=None
    )
    neighbor_ids: List[str] = Field(description="List of neighbor IDs found", default_factory=list)


class RetrieveNeighborScores(BaseAgentTool[RetrieveNeighborScoresInput, RetrieveNeighborScoresOutput]):
    """Tool for retrieving scores from neighboring prefectures."""

    def __init__(self):
        """Initialize the tool."""
        super().__init__(
            name="retrieve_neighbor_scores",
            description="Retrieve evaluation scores from neighboring prefectures. Requires agent_id and ad_id. Optional: max_neighbors.",
        )

        # Define prefecture neighbors (simplified geographic/cultural proximity)
        self.neighbor_mapping = {
            "Tokyo": ["Osaka", "Kyoto", "Kanagawa", "Saitama"],
            "Osaka": ["Tokyo", "Kyoto", "Nara", "Hyogo"],
            "Kyoto": ["Tokyo", "Osaka", "Nara", "Shiga"],
            "Hokkaido": ["Aomori", "Iwate", "Akita"],
            "Kanagawa": ["Tokyo", "Shizuoka", "Yamanashi"],
            "Saitama": ["Tokyo", "Gunma", "Tochigi"],
            "Nara": ["Osaka", "Kyoto", "Wakayama"],
            "Hyogo": ["Osaka", "Okayama", "Tottori"],
            "Shiga": ["Kyoto", "Mie", "Gifu"],
            "Aomori": ["Hokkaido", "Iwate", "Akita"],
            "Iwate": ["Hokkaido", "Aomori", "Miyagi"],
            "Akita": ["Hokkaido", "Aomori", "Yamagata"],
        }

        # Mock score database (in real implementation, this would come from actual database)
        from datetime import datetime, timedelta

        current_time = datetime.now()

        self.mock_scores = {
            "ad_001": {
                "Tokyo": {
                    "liking": 4.2,
                    "purchase_intent": 3.9,
                    "timestamp": (current_time - timedelta(hours=2)).isoformat(),
                },
                "Osaka": {
                    "liking": 3.8,
                    "purchase_intent": 3.4,
                    "timestamp": (current_time - timedelta(hours=1)).isoformat(),
                },
                "Kyoto": {
                    "liking": 3.5,
                    "purchase_intent": 3.1,
                    "timestamp": (current_time - timedelta(minutes=45)).isoformat(),
                },
                "Hokkaido": {
                    "liking": 3.0,
                    "purchase_intent": 2.8,
                    "timestamp": (current_time - timedelta(minutes=30)).isoformat(),
                },
                "Kanagawa": {
                    "liking": 4.0,
                    "purchase_intent": 3.7,
                    "timestamp": (current_time - timedelta(minutes=20)).isoformat(),
                },
            },
            "ad_002": {
                "Tokyo": {
                    "liking": 3.5,
                    "purchase_intent": 3.2,
                    "timestamp": (current_time - timedelta(hours=3)).isoformat(),
                },
                "Osaka": {
                    "liking": 4.5,
                    "purchase_intent": 4.2,
                    "timestamp": (current_time - timedelta(hours=2)).isoformat(),
                },
                "Kyoto": {
                    "liking": 4.0,
                    "purchase_intent": 3.8,
                    "timestamp": (current_time - timedelta(hours=1)).isoformat(),
                },
                "Hokkaido": {
                    "liking": 3.2,
                    "purchase_intent": 3.0,
                    "timestamp": (current_time - timedelta(minutes=50)).isoformat(),
                },
                "Nara": {
                    "liking": 3.9,
                    "purchase_intent": 3.6,
                    "timestamp": (current_time - timedelta(minutes=15)).isoformat(),
                },
            },
            "ad_003": {
                "Tokyo": {
                    "liking": 3.8,
                    "purchase_intent": 3.0,
                    "timestamp": (current_time - timedelta(hours=4)).isoformat(),
                },
                "Osaka": {
                    "liking": 3.2,
                    "purchase_intent": 2.8,
                    "timestamp": (current_time - timedelta(hours=3)).isoformat(),
                },
                "Kyoto": {
                    "liking": 4.7,
                    "purchase_intent": 4.2,
                    "timestamp": (current_time - timedelta(hours=2)).isoformat(),
                },
                "Hokkaido": {
                    "liking": 3.5,
                    "purchase_intent": 3.1,
                    "timestamp": (current_time - timedelta(hours=1)).isoformat(),
                },
                "Shiga": {
                    "liking": 4.1,
                    "purchase_intent": 3.7,
                    "timestamp": (current_time - timedelta(minutes=25)).isoformat(),
                },
            },
        }

    async def execute(self, input_data: RetrieveNeighborScoresInput) -> RetrieveNeighborScoresOutput:
        """Execute the tool to retrieve neighbor scores.

        Args:
            input_data: Input containing agent ID and ad ID

        Returns:
            Output containing neighbor scores
        """
        agent_id = input_data.agent_id
        ad_id = input_data.ad_id
        max_neighbors = input_data.max_neighbors or 5

        try:
            logger.info(f"Retrieving neighbor scores for agent {agent_id} on ad {ad_id}")

            # Get list of neighbors for this agent
            neighbors = self.neighbor_mapping.get(agent_id, [])

            if not neighbors:
                logger.warning(f"No neighbors defined for agent {agent_id}")
                return RetrieveNeighborScoresOutput(
                    success=True,
                    neighbor_scores=[],
                    neighbors_found=0,
                    average_liking=None,
                    average_purchase_intent=None,
                    neighbor_ids=[],
                )

            # Get scores for the specified ad
            ad_scores = self.mock_scores.get(ad_id, {})

            neighbor_score_list = []
            found_neighbor_ids = []

            # Collect scores from neighbors (up to max_neighbors)
            for neighbor_id in neighbors[:max_neighbors]:
                if neighbor_id in ad_scores and neighbor_id != agent_id:  # Don't include self
                    score_data = ad_scores[neighbor_id]

                    neighbor_score = NeighborScore(
                        neighbor_id=neighbor_id,
                        ad_id=ad_id,
                        liking_score=score_data["liking"],
                        purchase_intent_score=score_data["purchase_intent"],
                        timestamp=score_data["timestamp"],
                        confidence=0.8,  # Mock confidence value
                    )

                    neighbor_score_list.append(neighbor_score)
                    found_neighbor_ids.append(neighbor_id)

            # Calculate averages
            if neighbor_score_list:
                avg_liking = sum(score.liking_score for score in neighbor_score_list) / len(neighbor_score_list)
                avg_purchase_intent = sum(score.purchase_intent_score for score in neighbor_score_list) / len(
                    neighbor_score_list
                )
            else:
                avg_liking = None
                avg_purchase_intent = None

            neighbors_found = len(neighbor_score_list)

            logger.info(f"Retrieved {neighbors_found} neighbor scores for agent {agent_id}")

            return RetrieveNeighborScoresOutput(
                success=True,
                neighbor_scores=neighbor_score_list,
                neighbors_found=neighbors_found,
                average_liking=avg_liking,
                average_purchase_intent=avg_purchase_intent,
                neighbor_ids=found_neighbor_ids,
            )

        except Exception as e:
            logger.error(f"Error retrieving neighbor scores for agent {agent_id}: {e}")
            return RetrieveNeighborScoresOutput(
                success=False,
                message=f"Failed to retrieve neighbor scores: {str(e)}",
                neighbor_scores=[],
                neighbors_found=0,
                average_liking=None,
                average_purchase_intent=None,
                neighbor_ids=[],
            )

    def add_mock_score(self, ad_id: str, agent_id: str, liking: float, purchase_intent: float) -> None:
        """Add a mock score for testing purposes.

        Args:
            ad_id: Advertisement ID
            agent_id: Agent ID
            liking: Liking score
            purchase_intent: Purchase intent score
        """
        from datetime import datetime

        if ad_id not in self.mock_scores:
            self.mock_scores[ad_id] = {}

        self.mock_scores[ad_id][agent_id] = {
            "liking": liking,
            "purchase_intent": purchase_intent,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"Added mock score for {agent_id} on {ad_id}: liking={liking}, purchase_intent={purchase_intent}")

    def get_neighbor_list(self, agent_id: str) -> List[str]:
        """Get the list of neighbors for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            List of neighbor IDs
        """
        return self.neighbor_mapping.get(agent_id, [])
