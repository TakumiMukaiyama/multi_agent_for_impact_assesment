"""Tool for accessing local statistics and demographic data."""

from src.agents.schemas.tools.access_local_statistics import (
    AccessLocalStatisticsInput,
    AccessLocalStatisticsOutput,
)
from src.agents.tools.base import BaseAgentTool
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AccessLocalStatistics(BaseAgentTool[AccessLocalStatisticsInput, AccessLocalStatisticsOutput]):
    """Tool for accessing local statistics and demographic data."""

    def __init__(self):
        """Initialize the tool."""
        super().__init__(
            name="access_local_statistics",
            description="Access local statistics and demographic data for a prefecture. Requires agent_id. Optional: statistic_type.",
        )

        # Mock statistics data (in real implementation, this would come from a database)
        self.statistics_data = {
            "Tokyo": {
                "demographics": {
                    "population": 14000000,
                    "age_distribution": {"0-14": 0.12, "15-24": 0.09, "25-54": 0.37, "55-64": 0.12, "65+": 0.30},
                    "household_income": 6200000,  # yen
                    "urban_ratio": 1.0,
                },
                "economic_indicators": {
                    "gdp_per_capita": 5500000,  # yen
                    "unemployment_rate": 0.025,
                    "major_industries": ["finance", "technology", "services"],
                },
                "lifestyle_preferences": ["tech-savvy", "quality-oriented", "luxury-oriented", "convenience-focused"],
                "consumer_behavior": {"online_shopping_ratio": 0.8, "brand_loyalty": 0.6, "price_sensitivity": 0.3},
                "regional_characteristics": [
                    "highly urbanized",
                    "global outlook",
                    "trend-setting",
                    "fast-paced lifestyle",
                ],
            },
            "Osaka": {
                "demographics": {
                    "population": 8800000,
                    "age_distribution": {"0-14": 0.12, "15-24": 0.09, "25-54": 0.36, "55-64": 0.13, "65+": 0.30},
                    "household_income": 5500000,  # yen
                    "urban_ratio": 0.9,
                },
                "economic_indicators": {
                    "gdp_per_capita": 4800000,  # yen
                    "unemployment_rate": 0.028,
                    "major_industries": ["manufacturing", "trade", "food"],
                },
                "lifestyle_preferences": ["price-sensitive", "traditional", "food-loving", "pragmatic"],
                "consumer_behavior": {"online_shopping_ratio": 0.7, "brand_loyalty": 0.5, "price_sensitivity": 0.7},
                "regional_characteristics": [
                    "merchant culture",
                    "food-focused",
                    "practical approach",
                    "value-conscious",
                ],
            },
            "Hokkaido": {
                "demographics": {
                    "population": 5200000,
                    "age_distribution": {"0-14": 0.11, "15-24": 0.08, "25-54": 0.34, "55-64": 0.14, "65+": 0.33},
                    "household_income": 4500000,  # yen
                    "urban_ratio": 0.6,
                },
                "economic_indicators": {
                    "gdp_per_capita": 3800000,  # yen
                    "unemployment_rate": 0.032,
                    "major_industries": ["agriculture", "tourism", "manufacturing"],
                },
                "lifestyle_preferences": [
                    "traditional",
                    "environmentally-conscious",
                    "outdoor-oriented",
                    "community-focused",
                ],
                "consumer_behavior": {"online_shopping_ratio": 0.6, "brand_loyalty": 0.7, "price_sensitivity": 0.6},
                "regional_characteristics": [
                    "nature-oriented",
                    "community bonds",
                    "seasonal lifestyle",
                    "agricultural heritage",
                ],
            },
            "Kyoto": {
                "demographics": {
                    "population": 2500000,
                    "age_distribution": {"0-14": 0.10, "15-24": 0.10, "25-54": 0.32, "55-64": 0.14, "65+": 0.34},
                    "household_income": 5000000,  # yen
                    "urban_ratio": 0.8,
                },
                "economic_indicators": {
                    "gdp_per_capita": 4500000,  # yen
                    "unemployment_rate": 0.025,
                    "major_industries": ["tourism", "traditional_crafts", "education"],
                },
                "lifestyle_preferences": ["traditional", "quality-oriented", "culture-oriented", "aesthetics-focused"],
                "consumer_behavior": {"online_shopping_ratio": 0.65, "brand_loyalty": 0.8, "price_sensitivity": 0.4},
                "regional_characteristics": [
                    "cultural heritage",
                    "tradition-preservation",
                    "aesthetic values",
                    "tourism-centric",
                ],
            },
        }

    async def execute(self, input_data: AccessLocalStatisticsInput) -> AccessLocalStatisticsOutput:
        """Execute the tool to access local statistics.

        Args:
            input_data: Input containing agent_id and statistic type

        Returns:
            Output containing local statistics
        """
        agent_id = input_data.agent_id
        statistic_type = input_data.statistic_type or "general"

        try:
            # Get statistics data for the specified agent
            agent_stats = self.statistics_data.get(agent_id, {})

            if not agent_stats:
                logger.warning(f"No statistics found for agent {agent_id}")
                return AccessLocalStatisticsOutput(
                    success=False,
                    message=f"No statistics available for {agent_id}",
                    agent_id=agent_id,
                    demographics={},
                    economic_indicators={},
                    lifestyle_preferences=[],
                    consumer_behavior={},
                    regional_characteristics=[],
                )

            # Filter by statistic type if specified
            if statistic_type == "demographics":
                # Return only demographics
                output = AccessLocalStatisticsOutput(
                    success=True,
                    agent_id=agent_id,
                    demographics=agent_stats.get("demographics", {}),
                    economic_indicators={},
                    lifestyle_preferences=[],
                    consumer_behavior={},
                    regional_characteristics=[],
                )
            elif statistic_type == "economy":
                # Return only economic data
                output = AccessLocalStatisticsOutput(
                    success=True,
                    agent_id=agent_id,
                    demographics={},
                    economic_indicators=agent_stats.get("economic_indicators", {}),
                    lifestyle_preferences=[],
                    consumer_behavior=agent_stats.get("consumer_behavior", {}),
                    regional_characteristics=[],
                )
            elif statistic_type == "lifestyle":
                # Return lifestyle and preferences
                output = AccessLocalStatisticsOutput(
                    success=True,
                    agent_id=agent_id,
                    demographics={},
                    economic_indicators={},
                    lifestyle_preferences=agent_stats.get("lifestyle_preferences", []),
                    consumer_behavior=agent_stats.get("consumer_behavior", {}),
                    regional_characteristics=agent_stats.get("regional_characteristics", []),
                )
            else:
                # Return all data (general)
                output = AccessLocalStatisticsOutput(
                    success=True,
                    agent_id=agent_id,
                    demographics=agent_stats.get("demographics", {}),
                    economic_indicators=agent_stats.get("economic_indicators", {}),
                    lifestyle_preferences=agent_stats.get("lifestyle_preferences", []),
                    consumer_behavior=agent_stats.get("consumer_behavior", {}),
                    regional_characteristics=agent_stats.get("regional_characteristics", []),
                )

            logger.info(f"Successfully retrieved {statistic_type} statistics for {agent_id}")
            return output

        except Exception as e:
            logger.error(f"Error accessing local statistics for {agent_id}: {e}")
            return AccessLocalStatisticsOutput(
                success=False,
                message=f"Failed to access statistics: {str(e)}",
                agent_id=agent_id,
                demographics={},
                economic_indicators={},
                lifestyle_preferences=[],
                consumer_behavior={},
                regional_characteristics=[],
            )
