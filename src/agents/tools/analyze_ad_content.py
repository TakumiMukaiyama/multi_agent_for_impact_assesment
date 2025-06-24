"""Tool for analyzing ad content."""

from src.agents.schemas.tools.analyze_ad_content import AnalyzeAdContentInput, AnalyzeAdContentOutput
from src.agents.tools.base import BaseAgentTool
from src.llm.chain.pydantic_chain import PydanticChain
from src.llm.prompts.ad_content import ad_content_analysis_prompt
from src.llm.schema.ad_content_analysis import AdContentAnalysisInput, AdContentAnalysisOutput
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnalyzeAdContent(BaseAgentTool[AnalyzeAdContentInput, AnalyzeAdContentOutput]):
    """Tool for analyzing ad content."""

    def __init__(self, llm_client):
        """Initialize the tool.

        Args:
            llm_client: LLM client for content analysis
        """
        super().__init__(
            name="analyze_ad_content",
            description="Analyze advertisement content to identify categories, target demographics, and key features. Requires agent_id and ad_content.",
        )
        self.llm_client = llm_client

        # Create a PydanticChain for content analysis
        self.analysis_chain = PydanticChain(
            prompt_template=ad_content_analysis_prompt,
            input_schema=AdContentAnalysisInput,
            output_schema=AdContentAnalysisOutput,
            llm_client=self.llm_client,
        )

    async def execute(self, input_data: AnalyzeAdContentInput) -> AnalyzeAdContentOutput:
        """Execute the tool to analyze ad content.

        Args:
            input_data: Input containing ad content

        Returns:
            Output containing content analysis
        """
        agent_id = input_data.agent_id
        ad_content = input_data.ad_content

        try:
            # Create input for the LLM chain
            chain_input = AdContentAnalysisInput(
                ad_id=f"ad_from_{agent_id}",  # Generate a simple ID
                ad_content=ad_content,
            )

            # Invoke the chain
            logger.info(f"Analyzing content for agent {agent_id}")
            analysis_result = await self._invoke_chain(chain_input)

            # Convert to tool output
            return AnalyzeAdContentOutput(
                success=True,
                category=analysis_result.category,
                subcategories=analysis_result.subcategories,
                target_demographic=analysis_result.target_demographic,
                key_selling_points=analysis_result.key_selling_points,
                emotional_appeal=analysis_result.emotional_appeal,
                tone=analysis_result.tone,
                price_emphasis=analysis_result.price_emphasis,
                quality_emphasis=analysis_result.quality_emphasis,
            )

        except Exception as e:
            logger.error(f"Error analyzing ad content: {e}")
            return AnalyzeAdContentOutput(
                success=False,
                message=f"Failed to analyze ad content: {str(e)}",
                category="unknown",
                target_demographic="unknown",
                emotional_appeal="unknown",
                tone="unknown",
                price_emphasis=0.0,
                quality_emphasis=0.0,
            )

    async def _invoke_chain(self, chain_input: AdContentAnalysisInput) -> AdContentAnalysisOutput:
        """Invoke the chain with retry logic.

        Args:
            chain_input: Input for the chain

        Returns:
            Output from the chain
        """
        return self.analysis_chain.invoke_with_retry(inputs=chain_input, max_retries=2)
