"""Tool for retrieving scores from neighboring prefectures."""

from datetime import datetime, timedelta
from typing import List

from src.agents.schemas.tools.retrieve_neighbor_scores import (
    NeighborScore,
    RetrieveNeighborScoresInput,
    RetrieveNeighborScoresOutput,
)
from src.agents.tools.base import BaseAgentTool
from src.utils.logger import get_logger

logger = get_logger(__name__)


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
                if neighbor_id in ad_scores:
                    score_data = ad_scores[neighbor_id]
                    neighbor_score = NeighborScore(
                        neighbor_id=neighbor_id,
                        ad_id=ad_id,
                        liking_score=score_data["liking"],
                        purchase_intent_score=score_data["purchase_intent"],
                        timestamp=score_data["timestamp"],
                        confidence=0.85,  # Mock confidence
                    )
                    neighbor_score_list.append(neighbor_score)
                    found_neighbor_ids.append(neighbor_id)

            # Calculate averages if we have scores
            average_liking = None
            average_purchase_intent = None

            if neighbor_score_list:
                total_liking = sum(score.liking_score for score in neighbor_score_list)
                total_purchase_intent = sum(score.purchase_intent_score for score in neighbor_score_list)
                count = len(neighbor_score_list)

                average_liking = total_liking / count
                average_purchase_intent = total_purchase_intent / count

            logger.info(f"Retrieved {len(neighbor_score_list)} neighbor scores for agent {agent_id} on ad {ad_id}")

            return RetrieveNeighborScoresOutput(
                success=True,
                neighbor_scores=neighbor_score_list,
                neighbors_found=len(neighbor_score_list),
                average_liking=average_liking,
                average_purchase_intent=average_purchase_intent,
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
        if ad_id not in self.mock_scores:
            self.mock_scores[ad_id] = {}

        self.mock_scores[ad_id][agent_id] = {
            "liking": liking,
            "purchase_intent": purchase_intent,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"Added mock score for {agent_id} on {ad_id}")

    def get_neighbor_list(self, agent_id: str) -> List[str]:
        """Get the list of neighbors for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            List of neighbor IDs
        """
        return self.neighbor_mapping.get(agent_id, [])
