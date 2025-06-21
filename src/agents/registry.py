"""Registry for managing agent instances."""

from typing import Dict, List, Optional, Set, Union

from src.agents.base import BaseAgent
from src.agents.persona_factory import PersonaFactory
from src.agents.tools.factory import ToolFactory
from src.llm.client.azure_openai_client import AzureOpenAIClient
from src.llm.client.gemini_client import GeminiClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AgentRegistry:
    """Registry for managing agent instances.

    This class is responsible for creating, caching, and retrieving agent instances.
    It ensures that only one instance of each agent exists at a time.
    """

    def __init__(
        self,
        persona_factory: PersonaFactory,
        default_llm_client: Union[AzureOpenAIClient, GeminiClient],
        tool_factory: Optional[ToolFactory] = None,
        use_tools: bool = True,
    ):
        """Initialize the agent registry.

        Args:
            persona_factory: Factory for creating agent personas
            default_llm_client: Default LLM client to use for agents
            tool_factory: Optional tool factory for creating agent tools
            use_tools: Whether to enable tools for agents
        """
        self.persona_factory = persona_factory
        self.default_llm_client = default_llm_client
        self.use_tools = use_tools

        # Initialize tool factory if not provided and tools are enabled
        if use_tools and tool_factory is None:
            self.tool_factory = ToolFactory(llm_client=default_llm_client)
        else:
            self.tool_factory = tool_factory

        self._agents: Dict[str, BaseAgent] = {}

    def get_agent(self, agent_id: str) -> BaseAgent:
        """Get or create an agent with the specified ID.

        Args:
            agent_id: Identifier for the agent

        Returns:
            Agent instance

        Raises:
            ValueError: If the agent_id is not found in the persona factory
        """
        # Return existing agent if available
        if agent_id in self._agents:
            logger.info(f"Retrieved cached agent for {agent_id}")
            return self._agents[agent_id]

        # Create new agent
        try:
            # Get persona from factory
            persona = self.persona_factory.create_persona(agent_id)

            # Create tools if enabled
            tools = None
            if self.use_tools and self.tool_factory:
                try:
                    tools = self.tool_factory.create_essential_tools()
                    logger.info(f"Created {len(tools)} tools for agent {agent_id}")
                except Exception as e:
                    logger.error(f"Failed to create tools for agent {agent_id}: {e}")
                    tools = None

            # Create new agent
            agent = BaseAgent(
                agent_id=agent_id,
                profile=persona,
                llm_client=self.default_llm_client,
                tools=tools,
            )

            # Cache agent
            self._agents[agent_id] = agent
            logger.info(f"Created new agent for {agent_id} with tools: {bool(tools)}")

            return agent
        except ValueError as e:
            logger.error(f"Failed to create agent for {agent_id}: {e}")
            raise

    def get_agents(self, agent_ids: List[str]) -> List[BaseAgent]:
        """Get or create multiple agents.

        Args:
            agent_ids: List of agent identifiers

        Returns:
            List of agent instances
        """
        return [self.get_agent(agent_id) for agent_id in agent_ids]

    def get_all_agents(self) -> List[BaseAgent]:
        """Get all available agents.

        Returns:
            List of all agent instances
        """
        agent_ids = self.persona_factory.get_all_agent_ids()
        return self.get_agents(agent_ids)

    def get_agents_by_cluster(self, cluster: str) -> List[BaseAgent]:
        """Get all agents in the specified cluster.

        Args:
            cluster: Cluster name

        Returns:
            List of agent instances in the cluster
        """
        agent_ids = self.persona_factory.get_agents_by_cluster(cluster)
        return self.get_agents(agent_ids)

    def get_agents_by_region(self, region: str) -> List[BaseAgent]:
        """Get all agents in the specified region.

        Args:
            region: Region name

        Returns:
            List of agent instances in the region
        """
        agent_ids = self.persona_factory.get_agents_by_region(region)
        return self.get_agents(agent_ids)

    def update_llm_client(
        self, new_llm_client: Union[AzureOpenAIClient, GeminiClient], agent_ids: Optional[List[str]] = None
    ) -> None:
        """Update the LLM client for the specified agents.

        Args:
            new_llm_client: New LLM client to use
            agent_ids: Optional list of agent IDs to update. If None, updates all agents.
        """
        self.default_llm_client = new_llm_client

        # Update tool factory if present
        if self.tool_factory:
            self.tool_factory.update_llm_client(new_llm_client)

        # Determine which agents to update
        ids_to_update = agent_ids if agent_ids is not None else list(self._agents.keys())

        # Update each agent
        for agent_id in ids_to_update:
            if agent_id in self._agents:
                self._agents[agent_id].update_llm_client(new_llm_client)
                logger.info(f"Updated LLM client for agent {agent_id}")

    def enable_tools_for_agent(self, agent_id: str, tool_names: Optional[List[str]] = None) -> None:
        """Enable specific tools for an agent.

        Args:
            agent_id: Agent identifier
            tool_names: Optional list of tool names. If None, enables all essential tools.
        """
        if not self.tool_factory:
            logger.warning(f"No tool factory available to enable tools for agent {agent_id}")
            return

        if agent_id not in self._agents:
            logger.warning(f"Agent {agent_id} not found in registry")
            return

        agent = self._agents[agent_id]

        try:
            if tool_names:
                tools = self.tool_factory.create_specific_tools(tool_names)
            else:
                tools = self.tool_factory.create_essential_tools()

            # Add tools to agent
            for tool_name, tool in tools.items():
                agent.add_tool(tool_name, tool)

            logger.info(f"Enabled {len(tools)} tools for agent {agent_id}")

        except Exception as e:
            logger.error(f"Failed to enable tools for agent {agent_id}: {e}")

    def disable_tools_for_agent(self, agent_id: str) -> None:
        """Disable all tools for an agent.

        Args:
            agent_id: Agent identifier
        """
        if agent_id not in self._agents:
            logger.warning(f"Agent {agent_id} not found in registry")
            return

        agent = self._agents[agent_id]
        tool_names = agent.get_available_tools().copy()

        for tool_name in tool_names:
            agent.remove_tool(tool_name)

        logger.info(f"Disabled {len(tool_names)} tools for agent {agent_id}")

    def clear_cache(self) -> None:
        """Clear the agent cache."""
        self._agents.clear()
        logger.info("Cleared agent cache")

    def get_cached_agent_ids(self) -> Set[str]:
        """Get the IDs of all cached agents.

        Returns:
            Set of agent IDs
        """
        return set(self._agents.keys())

    def get_registry_info(self) -> Dict:
        """Get information about the registry state.

        Returns:
            Dictionary with registry information
        """
        cached_agents = {}
        for agent_id, agent in self._agents.items():
            cached_agents[agent_id] = {
                "tools_count": len(agent.get_available_tools()),
                "available_tools": agent.get_available_tools(),
            }

        return {
            "total_cached_agents": len(self._agents),
            "tools_enabled": self.use_tools,
            "tool_factory_available": self.tool_factory is not None,
            "cached_agents": cached_agents,
        }
