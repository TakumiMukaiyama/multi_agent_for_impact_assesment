from typing import Dict, List, Optional, Set
import logging

from src.agents.base import AgentConfig, PrefectureAgent
from src.agents.persona_factory import PersonaFactory

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for managing and accessing prefecture agents."""
    
    def __init__(self):
        """Initialize the agent registry."""
        self._agents: Dict[str, PrefectureAgent] = {}
    
    def register(self, agent: PrefectureAgent) -> None:
        """Register a new agent.
        
        Args:
            agent: The agent to register.
        """
        self._agents[agent.config.agent_id] = agent
        logger.info(f"Registered agent: {agent.config.agent_id}")
    
    def unregister(self, agent_id: str) -> None:
        """Unregister an agent.
        
        Args:
            agent_id: The ID of the agent to unregister.
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
    
    def get(self, agent_id: str) -> Optional[PrefectureAgent]:
        """Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent to get.
        
        Returns:
            The agent if found, None otherwise.
        """
        return self._agents.get(agent_id)
    
    def get_all(self) -> List[PrefectureAgent]:
        """Get all registered agents.
        
        Returns:
            A list of all registered agents.
        """
        return list(self._agents.values())
    
    def get_ids(self) -> Set[str]:
        """Get all registered agent IDs.
        
        Returns:
            A set of all registered agent IDs.
        """
        return set(self._agents.keys())
    
    def has_agent(self, agent_id: str) -> bool:
        """Check if an agent is registered.
        
        Args:
            agent_id: The ID of the agent to check.
        
        Returns:
            True if the agent is registered, False otherwise.
        """
        return agent_id in self._agents
    
    @classmethod
    def initialize_with_prefectures(cls, prefecture_ids: Optional[List[str]] = None) -> 'AgentRegistry':
        """Initialize the registry with agents for the specified prefectures.
        
        Args:
            prefecture_ids: List of prefecture IDs to initialize. If None, all prefectures will be initialized.
        
        Returns:
            The initialized agent registry.
        """
        registry = cls()
        
        # If no prefecture IDs are specified, use all prefectures
        if prefecture_ids is None:
            prefecture_ids = PersonaFactory.PREFECTURES
        
        # Create and register an agent for each prefecture
        for prefecture_id in prefecture_ids:
            # Create persona config
            persona = PersonaFactory.create_persona(prefecture_id)
            prompt_template = PersonaFactory.get_prompt_template(prefecture_id)
            
            # Create agent config
            config = AgentConfig(
                agent_id=prefecture_id,
                persona_config=persona,
                prompt_template=prompt_template,
                use_memory=True,
            )
            
            # In a real implementation, we would initialize tools here
            # and pass them to the agent constructor
            tools = []
            
            # Create and register agent
            agent = PrefectureAgent(config=config, tools=tools)
            registry.register(agent)
        
        return registry


# Create a singleton instance of the registry
# This will be initialized when needed
agent_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Get the singleton agent registry instance.
    
    Returns:
        The agent registry instance.
    """
    global agent_registry
    
    if agent_registry is None:
        # Initialize with a subset of prefectures for development
        development_prefectures = [
            "Tokyo", "Osaka", "Hokkaido", "Aichi", "Fukuoka",
            "Kyoto", "Okinawa", "Miyagi", "Hiroshima", "Shizuoka"
        ]
        agent_registry = AgentRegistry.initialize_with_prefectures(development_prefectures)
    
    return agent_registry