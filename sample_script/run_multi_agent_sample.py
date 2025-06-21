#!/usr/bin/env python3
"""
Multi-Agent Impact Assessment Sample Script

This script demonstrates how to use the multi-agent system for impact assessment.
Each agent represents a prefecture and evaluates advertisements based on their regional characteristics.
"""

import os
import sys
from typing import Dict, List

from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from src.agents.persona_factory import PersonaFactory
from src.agents.registry import AgentRegistry
from src.core.constants import LLMProviderType
from src.core.llm_settings import llm_settings
from src.llm.client.azure_openai_client import AzureOpenAIClient
from src.llm.client.gemini_client import GeminiClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def setup_azure_openai_client() -> AzureOpenAIClient:
    """Setup Azure OpenAI client."""
    print("Setting up Azure OpenAI client...")
    settings = llm_settings.providers[LLMProviderType.AZURE_OPENAI]
    api_key = settings.api_key.get_secret_value()

    client = AzureOpenAIClient(
        base_url=settings.endpoint,
        api_version=settings.api_version,
        api_key=api_key,
        deployment_name=settings.deployment_id,
        embedding_model=settings.embedding_model,
    )
    print(f"✓ Azure OpenAI client initialized with deployment: {client.deployment_name}")
    return client


def setup_gemini_client() -> GeminiClient:
    """Setup Gemini client."""
    print("Setting up Gemini client...")
    api_key = llm_settings.providers[LLMProviderType.GEMINI].api_key.get_secret_value()
    if not api_key:
        raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in your environment.")

    client = GeminiClient(api_key=api_key, chat_model="gemini-pro", embedding_model="models/embedding-001")
    print("✓ Gemini client initialized")
    return client


def create_sample_ads() -> List[Dict[str, str]]:
    """Create sample advertisements for evaluation."""
    return [
        {
            "ad_id": "ad_001",
            "content": "Discover the authentic flavors of Japan with our premium sake collection. Made with traditional brewing methods passed down through generations. Perfect for special occasions and connoisseurs.",
            "category": "alcoholic_beverages",
        },
        {
            "ad_id": "ad_002",
            "content": "Revolutionary eco-friendly electric car with cutting-edge technology. Zero emissions, smart features, and sleek design. Experience the future of sustainable transportation.",
            "category": "automotive",
        },
        {
            "ad_id": "ad_003",
            "content": "Luxury resort getaway in the heart of nature. Unwind in our premium spa, enjoy gourmet dining, and experience world-class hospitality. Book now for exclusive rates.",
            "category": "travel_hospitality",
        },
    ]


def run_multi_agent_evaluation(registry: AgentRegistry, ads: List[Dict[str, str]], target_agents: List[str]) -> None:
    """Run multi-agent evaluation on sample advertisements."""

    print("\n" + "=" * 80)
    print("Multi-Agent Advertisement Evaluation")
    print("=" * 80)

    # Get agents for evaluation
    agents = registry.get_agents(target_agents)

    for ad in ads:
        print(f"\n{'=' * 60}")
        print(f"Evaluating Advertisement: {ad['ad_id']}")
        print(f"Category: {ad['category']}")
        print(f"Content: {ad['content'][:100]}...")
        print(f"{'=' * 60}")

        # Collect results from all agents
        results = []

        for agent in agents:
            try:
                print(f"\n🤖 Agent {agent.agent_id} is evaluating...")

                # Get agent info for context
                agent_info = agent.get_agent_info()
                profile = agent_info["profile"]

                print(f"   Region: {profile.get('region', 'N/A')}")
                print(f"   Cluster: {profile.get('cluster', 'N/A')}")
                print(
                    f"   Population: {profile.get('population', 'N/A'):,}"
                    if profile.get("population")
                    else "   Population: N/A"
                )
                print(f"   Preferences: {', '.join(profile.get('preferences', []))}")

                # Display available tools
                available_tools = agent.get_available_tools()
                if available_tools:
                    print(f"   🔧 Available Tools: {', '.join(available_tools)}")
                else:
                    print("   ⚠️  No tools available")

                # Evaluate the ad
                result = agent.evaluate_ad(ad_id=ad["ad_id"], ad_content=ad["content"])

                results.append({"agent_id": agent.agent_id, "result": result})

                print("   ✓ Evaluation completed")
                print(f"   📊 Liking Score: {result.liking:.2f}/5.0")
                print(f"   🛒 Purchase Intent: {result.purchase_intent:.2f}/5.0")
                print(f"   💭 Commentary: {result.commentary[:150]}...")

            except Exception as e:
                print(f"   ❌ Error evaluating with {agent.agent_id}: {e}")
                logger.error(f"Error evaluating ad {ad['ad_id']} with agent {agent.agent_id}: {e}")

        # Summary of results
        if results:
            print(f"\n📈 Summary for {ad['ad_id']}:")
            print("-" * 40)

            avg_liking = sum(r["result"].liking for r in results) / len(results)
            avg_purchase = sum(r["result"].purchase_intent for r in results) / len(results)

            print(f"Average Liking Score: {avg_liking:.2f}/5.0")
            print(f"Average Purchase Intent: {avg_purchase:.2f}/5.0")

            # Top scoring agents
            top_liking = max(results, key=lambda x: x["result"].liking)
            top_purchase = max(results, key=lambda x: x["result"].purchase_intent)

            print(f"Highest Liking: {top_liking['agent_id']} ({top_liking['result'].liking:.2f})")
            print(f"Highest Purchase Intent: {top_purchase['agent_id']} ({top_purchase['result'].purchase_intent:.2f})")


def run_cluster_comparison(registry: AgentRegistry, ad: Dict[str, str]) -> None:
    """Compare how different clusters respond to the same advertisement."""

    print("\n" + "=" * 80)
    print("Cluster-Based Comparison Analysis")
    print("=" * 80)

    # Get agents from different clusters
    clusters = ["urban", "rural", "balanced", "tourism-oriented", "industrial"]
    cluster_results = {}

    print(f"\nAnalyzing advertisement: {ad['ad_id']}")
    print(f"Content: {ad['content'][:100]}...")

    for cluster in clusters:
        try:
            cluster_agents = registry.get_agents_by_cluster(cluster)
            if not cluster_agents:
                print(f"\n📊 {cluster.upper()} Cluster: No agents found")
                continue

            print(f"\n📊 {cluster.upper()} Cluster Analysis:")
            print(f"   Agents: {', '.join([a.agent_id for a in cluster_agents])}")

            liking_scores = []
            purchase_scores = []

            for agent in cluster_agents:
                try:
                    result = agent.evaluate_ad(ad_id=ad["ad_id"], ad_content=ad["content"])
                    liking_scores.append(result.liking)
                    purchase_scores.append(result.purchase_intent)

                except Exception as e:
                    print(f"   ❌ Error with {agent.agent_id}: {e}")

            if liking_scores:
                avg_liking = sum(liking_scores) / len(liking_scores)
                avg_purchase = sum(purchase_scores) / len(purchase_scores)

                cluster_results[cluster] = {
                    "avg_liking": avg_liking,
                    "avg_purchase": avg_purchase,
                    "agent_count": len(liking_scores),
                }

                print(f"   Average Liking: {avg_liking:.2f}/5.0")
                print(f"   Average Purchase Intent: {avg_purchase:.2f}/5.0")
                print(f"   Agents Evaluated: {len(liking_scores)}")

        except Exception as e:
            print(f"   ❌ Error analyzing {cluster} cluster: {e}")

    # Display cluster ranking
    if cluster_results:
        print(f"\n🏆 Cluster Rankings for {ad['ad_id']}:")
        print("-" * 50)

        # Sort by average liking score
        sorted_liking = sorted(cluster_results.items(), key=lambda x: x[1]["avg_liking"], reverse=True)
        print("By Liking Score:")
        for i, (cluster, data) in enumerate(sorted_liking, 1):
            print(f"   {i}. {cluster.upper()}: {data['avg_liking']:.2f}/5.0")

        # Sort by average purchase intent
        sorted_purchase = sorted(cluster_results.items(), key=lambda x: x[1]["avg_purchase"], reverse=True)
        print("\nBy Purchase Intent:")
        for i, (cluster, data) in enumerate(sorted_purchase, 1):
            print(f"   {i}. {cluster.upper()}: {data['avg_purchase']:.2f}/5.0")


def main():
    """Main function to run multi-agent evaluation examples."""

    # Load environment variables
    load_dotenv()

    print("Multi-Agent Impact Assessment System")
    print("=" * 50)

    # Check available providers
    available_providers = []
    if llm_settings.providers[LLMProviderType.AZURE_OPENAI].enabled:
        available_providers.append("azure_openai")
    if llm_settings.providers[LLMProviderType.GEMINI].enabled:
        available_providers.append("gemini")

    if not available_providers:
        print("❌ No LLM providers are enabled. Please check your environment variables.")
        print("Available providers: azure_openai, gemini")
        return

    print(f"✓ Available providers: {', '.join(available_providers)}")

    # Choose provider
    provider = os.getenv("SAMPLE_LLM_PROVIDER", available_providers[0])
    if provider not in available_providers:
        print(f"⚠️  Provider '{provider}' is not available. Using: {available_providers[0]}")
        provider = available_providers[0]

    print(f"🚀 Using provider: {provider}")

    try:
        # Setup LLM client
        if provider == "azure_openai":
            llm_client = setup_azure_openai_client()
        elif provider == "gemini":
            llm_client = setup_gemini_client()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Initialize persona factory and agent registry
        print("\n📋 Initializing agent system...")
        persona_factory = PersonaFactory()
        registry = AgentRegistry(persona_factory, llm_client)

        # Display available agents
        all_agent_ids = persona_factory.get_all_agent_ids()
        print(f"✓ Available agents: {', '.join(all_agent_ids)}")

        # Create sample advertisements
        ads = create_sample_ads()
        print(f"✓ Created {len(ads)} sample advertisements")

        # Run multi-agent evaluation with selected agents
        target_agents = ["Tokyo", "Osaka", "Hokkaido", "Kyoto", "Fukuoka"]
        available_targets = [aid for aid in target_agents if aid in all_agent_ids]

        if available_targets:
            run_multi_agent_evaluation(registry, ads, available_targets)
        else:
            print("⚠️  No target agents available for evaluation")

        # Run cluster comparison with first ad
        if ads and len(all_agent_ids) > 1:
            run_cluster_comparison(registry, ads[0])

        print("\n" + "=" * 80)
        print("✅ Multi-agent evaluation completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Error in main execution: {e}")
        print("Please check your environment variables and API keys.")


if __name__ == "__main__":
    main()
