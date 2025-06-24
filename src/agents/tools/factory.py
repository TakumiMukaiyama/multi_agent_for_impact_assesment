"""Factory for creating and managing agent tools."""

from typing import Dict, List, Optional, Union

from src.agents.tools.access_local_statistics import AccessLocalStatistics
from src.agents.tools.analyze_ad_content import AnalyzeAdContent
from src.agents.tools.base import BaseAgentTool
from src.agents.tools.calculate_aggregate_score import CalculateAggregateScore
from src.agents.tools.estimate_cultural_affinity import EstimateCulturalAffinity
from src.agents.tools.fetch_previous_ads import FetchPreviousAds
from src.agents.tools.generate_commentary import GenerateCommentary
from src.agents.tools.log_score_to_db import LogScoreToDb
from src.agents.tools.retrieve_neighbor_scores import RetrieveNeighborScores
from src.agents.tools.validate_input_format import ValidateInputFormat
from src.llm.client.azure_openai_client import AzureOpenAIClient
from src.llm.client.gemini_client import GeminiClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ToolFactory:
    """Factory for creating and managing agent tools."""

    def __init__(self, llm_client: Optional[Union[AzureOpenAIClient, GeminiClient]] = None):
        """Initialize the factory.

        Args:
            llm_client: Optional LLM client for tools that require it
        """
        self.llm_client = llm_client

        # Cache for created tools
        self._tool_cache: Dict[str, BaseAgentTool] = {}

    def create_essential_tools(self) -> Dict[str, BaseAgentTool]:
        """Create essential tools that are commonly used by agents.

        Returns:
            Dictionary mapping tool names to tool instances
        """
        tools = {}

        try:
            # Tools that don't require LLM client
            tools["access_local_statistics"] = self._get_or_create_tool("access_local_statistics")
            tools["validate_input_format"] = self._get_or_create_tool("validate_input_format")

            # Tools that require LLM client (only if available)
            if self.llm_client:
                tools["analyze_ad_content"] = self._get_or_create_tool("analyze_ad_content")
                tools["estimate_cultural_affinity"] = self._get_or_create_tool("estimate_cultural_affinity")
                tools["generate_commentary"] = self._get_or_create_tool("generate_commentary")
            else:
                logger.warning("LLM client not available, skipping LLM-dependent tools")

            logger.info(f"Created {len(tools)} essential tools")
            return tools

        except Exception as e:
            logger.error(f"Failed to create essential tools: {e}")
            return {}

    def create_all_tools(self) -> Dict[str, BaseAgentTool]:
        """Create all available tools.

        Returns:
            Dictionary mapping tool names to tool instances
        """
        tools = self.create_essential_tools()

        # Add additional tools if LLM client is available
        if self.llm_client:
            try:
                # These tools require more complex dependencies
                tools["calculate_aggregate_score"] = self._get_or_create_tool("calculate_aggregate_score")
                tools["fetch_previous_ads"] = self._get_or_create_tool("fetch_previous_ads")
                tools["log_score_to_db"] = self._get_or_create_tool("log_score_to_db")
                tools["retrieve_neighbor_scores"] = self._get_or_create_tool("retrieve_neighbor_scores")

                logger.info(f"Created {len(tools)} total tools")

            except Exception as e:
                logger.error(f"Failed to create additional tools: {e}")

        return tools

    def create_specific_tools(self, tool_names: List[str]) -> Dict[str, BaseAgentTool]:
        """Create specific tools by name.

        Args:
            tool_names: List of tool names to create

        Returns:
            Dictionary mapping tool names to tool instances
        """
        tools = {}

        for tool_name in tool_names:
            try:
                tool = self._get_or_create_tool(tool_name)
                if tool:
                    tools[tool_name] = tool
                else:
                    logger.warning(f"Failed to create tool: {tool_name}")
            except Exception as e:
                logger.error(f"Error creating tool {tool_name}: {e}")

        logger.info(f"Created {len(tools)} specific tools from {len(tool_names)} requested")
        return tools

    def get_available_tool_names(self) -> List[str]:
        """Get list of all available tool names.

        Returns:
            List of tool names
        """
        return [
            "access_local_statistics",
            "analyze_ad_content",
            "calculate_aggregate_score",
            "estimate_cultural_affinity",
            "fetch_previous_ads",
            "generate_commentary",
            "log_score_to_db",
            "retrieve_neighbor_scores",
            "validate_input_format",
        ]

    def update_llm_client(self, new_llm_client: Union[AzureOpenAIClient, GeminiClient]) -> None:
        """Update the LLM client and clear cache of tools that depend on it.

        Args:
            new_llm_client: New LLM client to use
        """
        self.llm_client = new_llm_client

        # Clear cache for LLM-dependent tools
        llm_dependent_tools = [
            "analyze_ad_content",
            "estimate_cultural_affinity",
            "generate_commentary",
            "calculate_aggregate_score",
            "fetch_previous_ads",
        ]

        for tool_name in llm_dependent_tools:
            if tool_name in self._tool_cache:
                del self._tool_cache[tool_name]

        logger.info("Updated LLM client and cleared cache for dependent tools")

    def _get_or_create_tool(self, tool_name: str) -> Optional[BaseAgentTool]:
        """Get or create a tool by name.

        Args:
            tool_name: Name of the tool to create

        Returns:
            Tool instance or None if creation fails
        """
        # Return cached tool if available
        if tool_name in self._tool_cache:
            return self._tool_cache[tool_name]

        # Create new tool
        try:
            tool = self._create_tool(tool_name)
            if tool:
                self._tool_cache[tool_name] = tool
            return tool
        except Exception as e:
            logger.error(f"Failed to create tool {tool_name}: {e}")
            return None

    def _create_tool(self, tool_name: str) -> Optional[BaseAgentTool]:
        """Create a specific tool by name.

        Args:
            tool_name: Name of the tool to create

        Returns:
            Tool instance or None if unknown tool
        """
        # Tools that don't require LLM client
        if tool_name == "access_local_statistics":
            return AccessLocalStatistics()

        elif tool_name == "validate_input_format":
            return ValidateInputFormat()

        elif tool_name == "calculate_aggregate_score":
            return CalculateAggregateScore()

        elif tool_name == "fetch_previous_ads":
            return FetchPreviousAds()

        elif tool_name == "log_score_to_db":
            return LogScoreToDb()

        elif tool_name == "retrieve_neighbor_scores":
            return RetrieveNeighborScores()

        # Tools that require LLM client
        elif tool_name == "analyze_ad_content":
            if not self.llm_client:
                logger.error("LLM client required for analyze_ad_content")
                return None
            return AnalyzeAdContent(self.llm_client)

        elif tool_name == "estimate_cultural_affinity":
            if not self.llm_client:
                logger.error("LLM client required for estimate_cultural_affinity")
                return None
            return EstimateCulturalAffinity(self.llm_client)

        elif tool_name == "generate_commentary":
            if not self.llm_client:
                logger.error("LLM client required for generate_commentary")
                return None
            return GenerateCommentary(self.llm_client)

        else:
            logger.warning(f"Unknown tool name: {tool_name}")
            return None
