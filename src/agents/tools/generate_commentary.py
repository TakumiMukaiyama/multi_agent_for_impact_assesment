"""Tool for generating detailed commentary on advertisements."""

from src.agents.schemas.tools.generate_commentary import GenerateCommentaryInput, GenerateCommentaryOutput
from src.agents.tools.base import BaseAgentTool
from src.llm.chain.pydantic_chain import PydanticChain
from src.llm.prompts.commentary import commentary_generation_prompt
from src.llm.schema.commentary_generation import CommentaryGenerationInput, CommentaryGenerationOutput
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GenerateCommentary(BaseAgentTool[GenerateCommentaryInput, GenerateCommentaryOutput]):
    """Tool for generating detailed commentary on advertisements."""

    def __init__(self, llm_client):
        """Initialize the tool.

        Args:
            llm_client: LLM client for commentary generation
        """
        super().__init__(
            name="generate_commentary",
            description="Generate detailed commentary on an advertisement from a regional perspective. Requires agent_id and ad_content. Optional: liking_score and purchase_intent_score.",
        )
        self.llm_client = llm_client

        # Create a PydanticChain for commentary generation
        self.commentary_chain = PydanticChain(
            prompt_template=commentary_generation_prompt,
            input_schema=CommentaryGenerationInput,
            output_schema=CommentaryGenerationOutput,
            llm_client=self.llm_client,
        )

        # Mock agent profiles (in real implementation, this would come from a database)
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

    async def execute(self, input_data: GenerateCommentaryInput) -> GenerateCommentaryOutput:
        """Execute the tool to generate commentary.

        Args:
            input_data: Input containing agent_id and ad content

        Returns:
            Output containing generated commentary
        """
        agent_id = input_data.agent_id
        ad_content = input_data.ad_content
        liking_score = input_data.liking_score or 3.0
        purchase_intent_score = input_data.purchase_intent_score or 3.0

        try:
            # Get agent profile from mock data (in real implementation, from database)
            agent_profile = self.agent_profiles.get(
                agent_id, {"region": "Unknown", "preferences": [], "cluster": "unknown", "age_distribution": {}}
            )

            # Prepare the data for the prompt
            profile_data = {
                "agent_id": agent_id,
                "region": agent_profile.get("region", "Unknown"),
                "age_distribution": agent_profile.get("age_distribution", {}),
                "preferences": agent_profile.get("preferences", []),
                "cluster": agent_profile.get("cluster", ""),
            }

            # Create input for the LLM chain
            chain_input = CommentaryGenerationInput(
                ad_content=ad_content,
                agent_profile=profile_data,
                liking_score=liking_score,
                purchase_intent_score=purchase_intent_score,
                cultural_affinity=0.7,  # Default value
            )

            # Invoke the chain
            logger.info(f"Generating commentary for agent {agent_id}")
            commentary_result = await self._invoke_chain(chain_input)

            # Return the output
            return GenerateCommentaryOutput(
                success=True,
                commentary=commentary_result.commentary,
                positive_aspects=commentary_result.positive_aspects,
                negative_aspects=commentary_result.negative_aspects,
                improvement_suggestions=commentary_result.improvement_suggestions,
            )

        except Exception as e:
            logger.error(f"Error generating commentary: {e}")
            return GenerateCommentaryOutput(
                success=False,
                message=f"Failed to generate commentary: {str(e)}",
                commentary="Unable to generate commentary due to an error.",
                positive_aspects=[],
                negative_aspects=[],
                improvement_suggestions=[],
            )

    async def _invoke_chain(self, chain_input: CommentaryGenerationInput) -> CommentaryGenerationOutput:
        """Invoke the chain with retry logic.

        Args:
            chain_input: Input for the chain

        Returns:
            Output from the chain
        """
        # In a real implementation, we would use the asynchronous version of invoke_with_retry
        # For simplicity, we're using a synchronous call with await
        return self.commentary_chain.invoke_with_retry(inputs=chain_input, max_retries=2)
