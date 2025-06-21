"""Tool for calculating aggregate scores from multiple sources."""

from typing import Dict, Optional

from pydantic import Field

from src.agents.tools.base import BaseAgentTool, ToolInput, ToolOutput
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CalculateAggregateScoreInput(ToolInput):
    """Input for calculating aggregate scores."""

    agent_id: str = Field(description="ID of the agent (prefecture)")
    own_liking: float = Field(description="Agent's own liking score (0-5)", ge=0.0, le=5.0)
    own_purchase_intent: float = Field(description="Agent's own purchase intent score (0-5)", ge=0.0, le=5.0)
    neighbor_scores: Optional[Dict[str, Dict[str, float]]] = Field(
        description="Neighbor scores in format {agent_id: {liking: float, purchase_intent: float}}", default=None
    )


class CalculateAggregateScoreOutput(ToolOutput):
    """Output containing aggregate scores."""

    aggregate_liking: float = Field(description="Aggregate liking score (0-5)", ge=0.0, le=5.0)
    aggregate_purchase_intent: float = Field(description="Aggregate purchase intent score (0-5)", ge=0.0, le=5.0)
    weighting_explanation: str = Field(description="Explanation of how neighbors were weighted")
    neighbor_influence: Dict[str, float] = Field(description="Influence weight of each neighbor", default_factory=dict)


class CalculateAggregateScore(BaseAgentTool[CalculateAggregateScoreInput, CalculateAggregateScoreOutput]):
    """Tool for calculating aggregate scores from multiple sources."""

    def __init__(self):
        """Initialize the tool."""
        super().__init__(
            name="calculate_aggregate_score",
            description="Calculate aggregate scores from own scores and neighbor scores. Requires agent_id, own_liking, and own_purchase_intent. Optional: neighbor_scores.",
        )

        # Regional similarity weights (simplified example)
        self.regional_similarity = {
            "Tokyo": {"Osaka": 0.7, "Kyoto": 0.6, "Hokkaido": 0.3},
            "Osaka": {"Tokyo": 0.7, "Kyoto": 0.8, "Hokkaido": 0.4},
            "Kyoto": {"Tokyo": 0.6, "Osaka": 0.8, "Hokkaido": 0.5},
            "Hokkaido": {"Tokyo": 0.3, "Osaka": 0.4, "Kyoto": 0.5},
        }

    async def execute(self, input_data: CalculateAggregateScoreInput) -> CalculateAggregateScoreOutput:
        """Execute the tool to calculate aggregate scores.

        Args:
            input_data: Input containing own scores and neighbor scores

        Returns:
            Output containing aggregate scores
        """
        agent_id = input_data.agent_id
        own_liking = input_data.own_liking
        own_purchase_intent = input_data.own_purchase_intent
        neighbor_scores = input_data.neighbor_scores or {}

        try:
            logger.info(f"Calculating aggregate scores for {agent_id}")

            # Start with own scores (base weight)
            total_weight = 1.0
            weighted_liking = own_liking * 1.0
            weighted_purchase_intent = own_purchase_intent * 1.0

            neighbor_influence = {}

            # Add neighbor scores with similarity-based weighting
            similarities = self.regional_similarity.get(agent_id, {})

            for neighbor_id, scores in neighbor_scores.items():
                if neighbor_id in similarities:
                    # Calculate influence weight based on regional similarity
                    influence_weight = similarities[neighbor_id] * 0.5  # Cap at 50% of own weight
                    neighbor_influence[neighbor_id] = influence_weight

                    # Add weighted neighbor scores
                    neighbor_liking = scores.get("liking", 0.0)
                    neighbor_purchase_intent = scores.get("purchase_intent", 0.0)

                    weighted_liking += neighbor_liking * influence_weight
                    weighted_purchase_intent += neighbor_purchase_intent * influence_weight
                    total_weight += influence_weight

                    logger.debug(f"Added neighbor {neighbor_id} with weight {influence_weight}")

            # Calculate final aggregate scores
            aggregate_liking = weighted_liking / total_weight
            aggregate_purchase_intent = weighted_purchase_intent / total_weight

            # Ensure scores are within valid range
            aggregate_liking = max(0.0, min(5.0, aggregate_liking))
            aggregate_purchase_intent = max(0.0, min(5.0, aggregate_purchase_intent))

            # Create weighting explanation
            if neighbor_scores:
                explanation = f"Weighted average of own scores (weight: 1.0) and {len(neighbor_scores)} neighbors based on regional similarity."
            else:
                explanation = "No neighbor scores provided, using own scores only."

            logger.info(
                f"Calculated aggregate scores for {agent_id}: liking={aggregate_liking:.2f}, purchase_intent={aggregate_purchase_intent:.2f}"
            )

            return CalculateAggregateScoreOutput(
                success=True,
                aggregate_liking=aggregate_liking,
                aggregate_purchase_intent=aggregate_purchase_intent,
                weighting_explanation=explanation,
                neighbor_influence=neighbor_influence,
            )

        except Exception as e:
            logger.error(f"Error calculating aggregate scores for {agent_id}: {e}")
            return CalculateAggregateScoreOutput(
                success=False,
                message=f"Failed to calculate aggregate scores: {str(e)}",
                aggregate_liking=own_liking,  # Fallback to own scores
                aggregate_purchase_intent=own_purchase_intent,
                weighting_explanation="Error occurred, using own scores as fallback",
                neighbor_influence={},
            )
