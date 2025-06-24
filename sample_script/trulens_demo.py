#!/usr/bin/env python3
"""
TruLens Demo Script

This script demonstrates how to use TruLens with the multi-agent system
for LLM monitoring and evaluation.
"""

import asyncio
import os
import sys
from typing import List

from dotenv import load_dotenv
from langchain.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from pydantic import Field

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from src.agents.base import AgentConfig
from src.agents.trulens_agent import TruLensPrefectureAgent
from src.core.constants import LLMProviderType
from src.core.llm_settings import llm_settings
from src.llm.chain.pydantic_chain_with_trulens import TruLensPydanticChain
from src.llm.client.azure_openai_client import AzureOpenAIClient
from src.llm.client.gemini_client import GeminiClient
from src.llm.dependancy.base import BaseInput, BaseOutput


# Define sample input and output schemas for chain demo
class ImpactAssessmentInput(BaseInput):
    """Input schema for impact assessment."""

    advertisement_content: str = Field(description="Advertisement content to assess")
    prefecture: str = Field(description="Target prefecture")
    demographic: str = Field(description="Target demographic")


class ImpactAssessmentOutput(BaseOutput):
    """Output schema for impact assessment."""

    impact_score: float = Field(description="Impact score from 0 to 10")
    reasoning: str = Field(description="Reasoning behind the score")
    cultural_considerations: List[str] = Field(description="Cultural considerations")
    recommendations: List[str] = Field(description="Recommendations for improvement")


# Sample tool for agent demo
class SampleTool(BaseTool):
    """Sample tool for prefecture agent."""

    name: str = "sample_analysis"
    description: str = "Analyze advertisement impact for a specific prefecture"

    def _run(self, query: str) -> str:
        """Run the tool."""
        return f"Analysis result for: {query}"

    async def _arun(self, query: str) -> str:
        """Run the tool asynchronously."""
        return self._run(query)


def setup_environment():
    """Setup environment variables."""
    load_dotenv()

    # Check required environment variables
    required_vars = []

    if llm_settings.providers[LLMProviderType.AZURE_OPENAI].enabled:
        required_vars.extend(
            [
                "AZURE_OPENAI_API_KEY",
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_OPENAI_DEPLOYMENT_ID",
            ]
        )

    if llm_settings.providers[LLMProviderType.GEMINI].enabled:
        required_vars.append("GEMINI_API_KEY")

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Warning: Missing environment variables: {missing_vars}")
        print("Some features may not work properly.")


def demo_pydantic_chain_with_trulens():
    """Demonstrate PydanticChain with TruLens monitoring."""

    print("\n" + "=" * 60)
    print("TruLens PydanticChain Demo")
    print("=" * 60)

    # Create prompt template
    template = """
    You are an expert in advertising impact assessment for Japan.
    
    Analyze the following advertisement for its potential impact in {prefecture} among {demographic} demographic:
    
    Advertisement: {advertisement_content}
    
    Provide a detailed impact assessment with:
    1. Impact score (0-10)
    2. Detailed reasoning
    3. Cultural considerations
    4. Recommendations for improvement
    
    {format_instructions}
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=["advertisement_content", "prefecture", "demographic"],
        partial_variables={"format_instructions": ""},
    )

    # Initialize LLM client
    if llm_settings.providers[LLMProviderType.AZURE_OPENAI].enabled:
        llm_client = AzureOpenAIClient()
    elif llm_settings.providers[LLMProviderType.GEMINI].enabled:
        gemini_config = llm_settings.providers[LLMProviderType.GEMINI]
        llm_client = GeminiClient(
            api_key=gemini_config.api_key,
            chat_model=gemini_config.model_name,
            embedding_model=gemini_config.embedding_model,
        )
    else:
        print("No LLM provider is available.")
        return

    # Create TruLens-enhanced chain
    chain = TruLensPydanticChain(
        prompt_template=prompt,
        input_schema=ImpactAssessmentInput,
        output_schema=ImpactAssessmentOutput,
        llm_client=llm_client,
        app_name="impact_assessment_chain",
        app_version="1.0",
        enable_trulens=True,
    )

    # Sample inputs
    test_cases = [
        {
            "advertisement_content": "新しいスマートフォンが登場！最新技術でより便利な生活を。",
            "prefecture": "Tokyo",
            "demographic": "20-30代",
        },
        {
            "advertisement_content": "伝統的な日本料理を現代風にアレンジした新レストラン。",
            "prefecture": "Kyoto",
            "demographic": "30-50代",
        },
        {
            "advertisement_content": "環境に優しい電気自動車で、未来への第一歩を踏み出そう。",
            "prefecture": "Hokkaido",
            "demographic": "40-60代",
        },
    ]

    # Run test cases
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Advertisement: {test_case['advertisement_content']}")
        print(f"Prefecture: {test_case['prefecture']}")
        print(f"Demographic: {test_case['demographic']}")

        try:
            input_data = ImpactAssessmentInput(**test_case)
            result = chain.invoke_with_retry(input_data)

            print(f"Impact Score: {result.impact_score}")
            print(f"Reasoning: {result.reasoning}")
            print(f"Cultural Considerations: {', '.join(result.cultural_considerations)}")
            print(f"Recommendations: {', '.join(result.recommendations)}")

        except Exception as e:
            print(f"Error processing test case {i}: {e}")

    # Display TruLens information
    print("\nTruLens Chain Info:")
    chain_info = chain.get_chain_info()
    for key, value in chain_info.items():
        print(f"  {key}: {value}")

    # Start TruLens dashboard
    try:
        print("\nStarting TruLens dashboard...")
        print("Dashboard will be available at: http://localhost:8501")
        print("Note: You may need to stop the dashboard manually after viewing.")

        # Uncomment to start dashboard automatically
        # chain.start_trulens_dashboard(port=8501, force=True)

    except Exception as e:
        print(f"Note: Dashboard start failed (this is normal): {e}")


async def demo_agent_with_trulens():
    """Demonstrate Prefecture Agent with TruLens monitoring."""

    print("\n" + "=" * 60)
    print("TruLens Prefecture Agent Demo")
    print("=" * 60)

    # Create agent configuration
    config = AgentConfig(
        agent_id="tokyo",
        persona_config={
            "age_distribution": {"20s": 0.3, "30s": 0.4, "40s": 0.2, "50s+": 0.1},
            "preferences": {"tech": 0.8, "fashion": 0.6, "food": 0.7},
            "region": "Kanto",
            "values": ["innovation", "efficiency", "diversity"],
        },
        prompt_template="""
        You are an agent representing Tokyo prefecture in Japan.
        Your role is to assess advertisements and their potential impact on the local population.
        
        Consider the following persona characteristics:
        - Age distribution: {persona[age_distribution]}
        - Preferences: {persona[preferences]} 
        - Regional characteristics: {persona[region]}
        - Values: {persona[values]}
        
        Provide thoughtful analysis based on Tokyo's unique demographic and cultural context.
        """,
        use_memory=True,
    )

    # Create tools
    tools = [SampleTool()]

    # Create TruLens-enhanced agent
    agent = TruLensPrefectureAgent(
        config=config,
        tools=tools,
        enable_trulens=True,
    )

    # Sample queries
    test_queries = [
        "この新しいテクノロジー製品の広告は東京の住民にどのような影響を与えますか？",
        "伝統的な日本文化を取り入れた現代的なサービスについて評価してください。",
        "環境に配慮した商品の広告キャンペーンの効果を分析してください。",
    ]

    # Run test queries
    for i, query in enumerate(test_queries, 1):
        print(f"\nAgent Query {i}: {query}")

        try:
            result = await agent.run(query)
            print(f"Agent Response: {result.get('output', 'No output')}")
            print(f"Agent ID: {result.get('agent_id', 'N/A')}")
            print(f"TruLens Enabled: {result.get('trulens_enabled', False)}")

        except Exception as e:
            print(f"Error processing query {i}: {e}")

    # Display agent information
    print("\nAgent Information:")
    agent_info = agent.get_agent_info()
    for key, value in agent_info.items():
        print(f"  {key}: {value}")


def main():
    """Main function to run TruLens demos."""

    print("TruLens Demo for Multi-Agent Impact Assessment System")
    print("=" * 60)

    # Setup environment
    setup_environment()

    # Check available providers
    available_providers = []
    if llm_settings.providers[LLMProviderType.AZURE_OPENAI].enabled:
        available_providers.append("Azure OpenAI")
    if llm_settings.providers[LLMProviderType.GEMINI].enabled:
        available_providers.append("Gemini")

    if not available_providers:
        print("No LLM providers are enabled. Please check your environment variables.")
        return

    print(f"Available providers: {', '.join(available_providers)}")

    # Run demos
    try:
        # Demo 1: PydanticChain with TruLens
        demo_pydantic_chain_with_trulens()

        # Demo 2: Agent with TruLens
        asyncio.run(demo_agent_with_trulens())

        # Final instructions
        print("\n" + "=" * 60)
        print("Demo Complete!")
        print("=" * 60)
        print("To view TruLens dashboard:")
        print("1. Use the API endpoint: POST /api/v1/trulens/dashboard/start")
        print("2. Or call start_trulens_dashboard() method on any TruLens-enhanced component")
        print("3. Open http://localhost:8501 in your browser")
        print()
        print("To view evaluation data:")
        print("- GET /api/v1/trulens/leaderboard")
        print("- GET /api/v1/trulens/records")
        print("- GET /api/v1/trulens/apps")

    except Exception as e:
        print(f"Error running demo: {e}")
        raise


if __name__ == "__main__":
    main()
