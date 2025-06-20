from typing import Dict, Any, Type
from pydantic import BaseModel, Field

from langchain.tools import BaseTool

from src.agents.persona_factory import PersonaFactory


class AccessLocalStatisticsInput(BaseModel):
    """Input for the access_local_statistics tool."""
    agent_id: str = Field(..., description="The prefecture ID to get statistics for.")


class AccessLocalStatisticsTool(BaseTool):
    """Tool for accessing local statistics about a prefecture."""
    
    name = "access_local_statistics"
    description = """
    Access detailed statistics for the specified prefecture, including demographic
    information, consumer trends, and local economic indicators.
    
    INPUT:
    agent_id: The prefecture ID (e.g., "Tokyo")
    
    OUTPUT:
    A dictionary containing detailed statistics about the prefecture.
    """
    args_schema: Type[BaseModel] = AccessLocalStatisticsInput
    
    def _run(self, agent_id: str) -> Dict[str, Any]:
        """Get detailed statistics for a prefecture.
        
        Args:
            agent_id: The prefecture ID to get statistics for.
        
        Returns:
            A dictionary containing detailed statistics about the prefecture.
        """
        # In a real implementation, we would query a database to get
        # detailed statistics about the prefecture. For now, we'll just
        # return the persona information plus some mock data.
        
        # Get the base persona
        if agent_id not in PersonaFactory.PREFECTURES:
            return {"error": f"Invalid prefecture ID: {agent_id}"}
        
        persona = PersonaFactory.create_persona(agent_id)
        cluster = PersonaFactory.PREFECTURE_CLUSTERS.get(agent_id, "rural")
        
        # Add additional mock statistics
        statistics = {
            "demographics": {
                "age_distribution": persona["age_distribution"],
                "total_population": 1_000_000 + (hash(agent_id) % 10_000_000),
                "population_density": 100 + (hash(f"{agent_id}_density") % 5000),
                "gender_ratio": {"male": 0.48 + (hash(f"{agent_id}_gender") % 10) / 100, "female": 0.52 - (hash(f"{agent_id}_gender") % 10) / 100},
            },
            "economy": {
                "average_income": 4_000_000 + (hash(f"{agent_id}_income") % 4_000_000),
                "unemployment_rate": 0.02 + (hash(f"{agent_id}_unemployment") % 10) / 100,
                "major_industries": self._get_major_industries(cluster),
            },
            "consumer_trends": {
                "preferences": persona["preferences"],
                "spending_categories": self._get_spending_categories(cluster),
            },
            "geography": {
                "region": persona["region"],
                "area_sqkm": 1000 + (hash(f"{agent_id}_area") % 80_000),
                "coastline": agent_id in ["Hokkaido", "Aomori", "Iwate", "Miyagi", "Chiba", "Tokyo", "Kanagawa", "Shizuoka", "Mie", "Wakayama", "Osaka", "Hyogo", "Tottori", "Shimane", "Yamaguchi", "Kagawa", "Ehime", "Kochi", "Fukuoka", "Saga", "Nagasaki", "Kumamoto", "Oita", "Miyazaki", "Kagoshima", "Okinawa"],
                "mountainous": agent_id in ["Nagano", "Yamanashi", "Gifu", "Toyama", "Niigata", "Fukushima", "Gunma"],
            },
        }
        
        return statistics
    
    async def _arun(self, agent_id: str) -> Dict[str, Any]:
        """Async version of _run."""
        return self._run(agent_id=agent_id)
    
    def _get_major_industries(self, cluster: str) -> Dict[str, float]:
        """Get major industries based on the prefecture cluster."""
        if cluster == "urban":
            return {"finance": 0.8, "technology": 0.9, "services": 0.8, "manufacturing": 0.6, "tourism": 0.7}
        elif cluster == "suburban":
            return {"manufacturing": 0.8, "services": 0.7, "retail": 0.7, "logistics": 0.6, "tourism": 0.6}
        elif cluster == "rural":
            return {"agriculture": 0.9, "manufacturing": 0.5, "tourism": 0.6, "forestry": 0.7, "fishing": 0.4}
        elif cluster == "elderly":
            return {"agriculture": 0.7, "healthcare": 0.8, "tourism": 0.5, "traditional_crafts": 0.7, "retirement_services": 0.8}
        else:  # youthful
            return {"technology": 0.7, "tourism": 0.9, "services": 0.8, "education": 0.7, "entertainment": 0.8}
    
    def _get_spending_categories(self, cluster: str) -> Dict[str, float]:
        """Get spending categories based on the prefecture cluster."""
        if cluster == "urban":
            return {"dining_out": 0.8, "entertainment": 0.8, "fashion": 0.8, "technology": 0.9, "housing": 0.9}
        elif cluster == "suburban":
            return {"groceries": 0.7, "transportation": 0.8, "education": 0.7, "housing": 0.8, "healthcare": 0.6}
        elif cluster == "rural":
            return {"groceries": 0.8, "utilities": 0.7, "transportation": 0.7, "healthcare": 0.6, "agriculture": 0.6}
        elif cluster == "elderly":
            return {"healthcare": 0.9, "groceries": 0.7, "utilities": 0.8, "traditional_goods": 0.7, "gifts": 0.6}
        else:  # youthful
            return {"entertainment": 0.9, "dining_out": 0.8, "fashion": 0.9, "technology": 0.8, "travel": 0.7}