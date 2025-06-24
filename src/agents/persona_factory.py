"""Factory for creating agent personas."""
import json
import os
from typing import Dict, List, Optional

from src.agents.schemas.agent.agent_profile import AgentProfile
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PersonaFactory:
    """Factory for creating agent personas."""

    def __init__(self, persona_data_path: Optional[str] = None):
        """Initialize the persona factory.
        
        Args:
            persona_data_path: Optional path to JSON file containing persona data.
                               If not provided, will use default personas.
        """
        self.persona_data_path = persona_data_path
        self.persona_data: Dict[str, Dict] = {}
        self.load_personas()
    
    def load_personas(self) -> None:
        """Load persona data from file or use defaults."""
        if self.persona_data_path and os.path.exists(self.persona_data_path):
            try:
                with open(self.persona_data_path, "r") as f:
                    self.persona_data = json.load(f)
                logger.info(f"Loaded personas from {self.persona_data_path}")
            except Exception as e:
                logger.error(f"Failed to load personas from {self.persona_data_path}: {e}")
                self._load_default_personas()
        else:
            self._load_default_personas()
    
    def _load_default_personas(self) -> None:
        """Load default personas."""
        # Default persona data for 47 prefectures
        # These are simplified examples; in a real implementation, these would be more detailed
        logger.info("Loading default personas")
        
        # Define clusters
        urban_cluster = "urban"
        rural_cluster = "rural"
        balanced_cluster = "balanced"
        tourism_cluster = "tourism-oriented"
        industrial_cluster = "industrial"
        
        # Define some common preferences
        price_sensitive = "price-sensitive"
        quality_oriented = "quality-oriented"
        tech_savvy = "tech-savvy"
        traditional = "traditional"
        health_conscious = "health-conscious"
        luxury_oriented = "luxury-oriented"
        environmentally_conscious = "environmentally-conscious"
        
        # Helper function to create a basic profile
        def create_profile(agent_id, population, region, cluster, preferences, age_dist):
            return {
                "agent_id": agent_id,
                "population": population,
                "region": region,
                "cluster": cluster,
                "preferences": preferences,
                "age_distribution": age_dist
            }
        
        # Create basic profiles for each prefecture
        # This is simplified data; a real implementation would have more accurate data
        self.persona_data = {
            "Tokyo": create_profile(
                "Tokyo", 13960000, "Kanto", urban_cluster,
                [tech_savvy, quality_oriented, luxury_oriented],
                {"20s": 0.15, "30s": 0.18, "40s": 0.16, "50s": 0.14, "60s+": 0.37}
            ),
            "Osaka": create_profile(
                "Osaka", 8809000, "Kansai", urban_cluster,
                [price_sensitive, traditional, "food-loving"],
                {"20s": 0.12, "30s": 0.15, "40s": 0.15, "50s": 0.16, "60s+": 0.42}
            ),
            "Hokkaido": create_profile(
                "Hokkaido", 5250000, "Hokkaido", rural_cluster,
                [traditional, environmentally_conscious, "outdoor-oriented"],
                {"20s": 0.10, "30s": 0.12, "40s": 0.14, "50s": 0.18, "60s+": 0.46}
            ),
            "Kyoto": create_profile(
                "Kyoto", 2583000, "Kansai", tourism_cluster,
                [traditional, quality_oriented, "culture-oriented"],
                {"20s": 0.12, "30s": 0.14, "40s": 0.15, "50s": 0.16, "60s+": 0.43}
            ),
            "Aichi": create_profile(
                "Aichi", 7552000, "Chubu", industrial_cluster,
                [tech_savvy, price_sensitive, "manufacturing-oriented"],
                {"20s": 0.13, "30s": 0.16, "40s": 0.16, "50s": 0.15, "60s+": 0.40}
            ),
            "Fukuoka": create_profile(
                "Fukuoka", 5104000, "Kyushu", balanced_cluster,
                [tech_savvy, "food-loving", health_conscious],
                {"20s": 0.14, "30s": 0.15, "40s": 0.15, "50s": 0.15, "60s+": 0.41}
            ),
            # Add more prefectures as needed
        }
        
        logger.info(f"Loaded {len(self.persona_data)} default personas")
    
    def create_persona(self, agent_id: str) -> AgentProfile:
        """Create a persona for the specified agent.
        
        Args:
            agent_id: Identifier for the agent (prefecture name)
            
        Returns:
            Agent profile for the specified agent
            
        Raises:
            ValueError: If the agent_id is not found in the persona data
        """
        if agent_id not in self.persona_data:
            raise ValueError(f"No persona data found for agent {agent_id}")
        
        persona_data = self.persona_data[agent_id]
        logger.info(f"Creating persona for {agent_id}")
        
        return AgentProfile(
            agent_id=agent_id,
            age_distribution=persona_data.get("age_distribution", {}),
            preferences=persona_data.get("preferences", []),
            cluster=persona_data.get("cluster", ""),
            population=persona_data.get("population"),
            region=persona_data.get("region")
        )
    
    def get_all_agent_ids(self) -> List[str]:
        """Get a list of all available agent IDs.
        
        Returns:
            List of agent IDs
        """
        return list(self.persona_data.keys())
    
    def get_agents_by_cluster(self, cluster: str) -> List[str]:
        """Get a list of agent IDs in the specified cluster.
        
        Args:
            cluster: Cluster name
            
        Returns:
            List of agent IDs in the cluster
        """
        return [
            agent_id 
            for agent_id, data in self.persona_data.items() 
            if data.get("cluster") == cluster
        ]
    
    def get_agents_by_region(self, region: str) -> List[str]:
        """Get a list of agent IDs in the specified region.
        
        Args:
            region: Region name
            
        Returns:
            List of agent IDs in the region
        """
        return [
            agent_id 
            for agent_id, data in self.persona_data.items() 
            if data.get("region") == region
        ]