"""Tool for estimating cultural affinity between ads and regional preferences."""

from typing import List

from pydantic import Field

from src.agents.tools.base import BaseAgentTool, ToolInput, ToolOutput
from src.llm.chain.pydantic_chain import PydanticChain
from src.llm.prompts.cultural_affinity import cultural_affinity_prompt
from src.llm.schema.cultural_affinity import CulturalAffinityInput, CulturalAffinityOutput
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AlignmentFactor(ToolOutput):
    """Factor that affects cultural alignment."""

    factor: str = Field(description="Description of the alignment factor")
    strength: float = Field(description="Strength of this factor (-1.0 to 1.0)", ge=-1.0, le=1.0)


class EstimateCulturalAffinityInput(ToolInput):
    """Input for estimating cultural affinity."""

    agent_id: str = Field(description="ID of the agent (prefecture)")
    ad_content: str = Field(description="Content of the ad to evaluate")


class EstimateCulturalAffinityOutput(ToolOutput):
    """Output containing cultural affinity estimation."""

    affinity_score: float = Field(description="Cultural affinity score (0.0-1.0)", ge=0.0, le=1.0)
    confidence: float = Field(description="Confidence in the estimation (0.0-1.0)", ge=0.0, le=1.0)
    alignment_factors: List[AlignmentFactor] = Field(
        description="Factors that contribute to the affinity score", default_factory=list
    )
    regional_insights: str = Field(description="Insights about how this ad aligns with regional culture")


class EstimateCulturalAffinity(BaseAgentTool[EstimateCulturalAffinityInput, EstimateCulturalAffinityOutput]):
    """Tool for estimating cultural affinity between ads and regional preferences."""

    def __init__(self, llm_client):
        """Initialize the tool.

        Args:
            llm_client: LLM client for affinity estimation
        """
        super().__init__(
            name="estimate_cultural_affinity",
            description="Estimate cultural affinity between an advertisement and regional preferences. Requires agent_id and ad_content.",
        )
        self.llm_client = llm_client

        # Create a PydanticChain for affinity estimation
        self.affinity_chain = PydanticChain(
            prompt_template=cultural_affinity_prompt,
            input_schema=CulturalAffinityInput,
            output_schema=CulturalAffinityOutput,
            llm_client=self.llm_client,
        )

        # Mock agent profiles (same as in generate_commentary)
        self.agent_profiles = {
            "Tokyo": {
                "region": "Kanto",
                "preferences": ["tech-savvy", "quality-oriented", "luxury-oriented"],
                "cluster": "urban",
                "age_distribution": {"0-14": 0.12, "15-24": 0.09, "25-54": 0.37, "55-64": 0.12, "65+": 0.30},
            },
            "Osaka": {
                "region": "Kansai",
                "preferences": ["price-sensitive", "traditional", "food-loving"],
                "cluster": "urban",
                "age_distribution": {"0-14": 0.12, "15-24": 0.09, "25-54": 0.36, "55-64": 0.13, "65+": 0.30},
            },
            "Hokkaido": {
                "region": "Hokkaido",
                "preferences": ["traditional", "environmentally-conscious", "outdoor-oriented"],
                "cluster": "rural",
                "age_distribution": {"0-14": 0.11, "15-24": 0.08, "25-54": 0.34, "55-64": 0.14, "65+": 0.33},
            },
            "Kyoto": {
                "region": "Kansai",
                "preferences": ["traditional", "quality-oriented", "culture-oriented"],
                "cluster": "tourism-oriented",
                "age_distribution": {"0-14": 0.10, "15-24": 0.10, "25-54": 0.32, "55-64": 0.14, "65+": 0.34},
            },
        }

    async def execute(self, input_data: EstimateCulturalAffinityInput) -> EstimateCulturalAffinityOutput:
        """Execute the tool to estimate cultural affinity.

        Args:
            input_data: Input containing agent_id and ad content

        Returns:
            Output containing affinity estimation
        """
        agent_id = input_data.agent_id
        ad_content = input_data.ad_content

        try:
            # Get agent profile from mock data
            agent_profile = self.agent_profiles.get(
                agent_id, {"region": "Unknown", "preferences": [], "cluster": "unknown", "age_distribution": {}}
            )

            # Prepare the data for the prompt
            profile_data = {
                "agent_id": agent_id,
                "region": agent_profile.get("region", "Unknown"),
                "population": agent_profile.get("population", 0),
                "age_distribution": agent_profile.get("age_distribution", {}),
                "preferences": agent_profile.get("preferences", []),
                "cluster": agent_profile.get("cluster", ""),
                "urban_rural_ratio": 0.5,  # Default value
                "consumer_trends": agent_profile.get("preferences", []),
            }

            # Create input for the LLM chain
            chain_input = CulturalAffinityInput(ad_content=ad_content, agent_profile=profile_data)

            # Invoke the chain
            logger.info(f"Estimating cultural affinity for {agent_id}")
            affinity_result = await self._invoke_chain(chain_input)

            # Process alignment factors
            alignment_factors = [
                AlignmentFactor(factor=f.get("factor", ""), strength=f.get("strength", 0.5))
                for f in affinity_result.alignment_factors
            ]

            return EstimateCulturalAffinityOutput(
                success=True,
                affinity_score=affinity_result.affinity_score,
                confidence=affinity_result.confidence,
                alignment_factors=alignment_factors,
                regional_insights=affinity_result.regional_insights,
            )

        except Exception as e:
            logger.error(f"Error estimating cultural affinity for {agent_id}: {e}")
            return EstimateCulturalAffinityOutput(
                success=False,
                message=f"Failed to estimate cultural affinity: {str(e)}",
                affinity_score=0.5,  # Neutral score
                confidence=0.0,
                alignment_factors=[],
                regional_insights="Unable to estimate due to an error.",
            )

    async def _invoke_chain(self, chain_input: CulturalAffinityInput) -> CulturalAffinityOutput:
        """Invoke the chain with retry logic.

        Args:
            chain_input: Input for the chain

        Returns:
            Output from the chain
        """
        return self.affinity_chain.invoke_with_retry(inputs=chain_input, max_retries=2)
