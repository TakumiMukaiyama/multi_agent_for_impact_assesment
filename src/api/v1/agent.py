from typing import Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


# Agent schemas
class PersonaConfig(BaseModel):
    age_distribution: Dict[str, float]
    preferences: Dict[str, float]
    region: str


class AgentCreate(BaseModel):
    agent_id: str
    persona_config: PersonaConfig
    prompt_template: str


class AgentResponse(AgentCreate):
    created_at: str


@router.get("/")
async def list_agents() -> List[str]:
    """Get all available agent IDs."""
    # This is a placeholder, implementation will be added later
    return ["Tokyo", "Osaka", "Hokkaido"]


@router.post("/", status_code=201)
async def create_agent(agent: AgentCreate) -> AgentResponse:
    """Create a new agent."""
    # This is a placeholder, implementation will be added later
    return AgentResponse(
        agent_id=agent.agent_id,
        persona_config=agent.persona_config,
        prompt_template=agent.prompt_template,
        created_at="2023-06-20T00:00:00",
    )


@router.get("/{agent_id}")
async def get_agent(agent_id: str) -> AgentResponse:
    """Get an agent by ID."""
    # This is a placeholder, implementation will be added later
    if agent_id not in ["Tokyo", "Osaka", "Hokkaido"]:
        raise HTTPException(status_code=404, detail="Agent not found")

    return AgentResponse(
        agent_id=agent_id,
        persona_config=PersonaConfig(
            age_distribution={"20s": 0.3, "30s": 0.4, "40s": 0.2, "50s+": 0.1},
            preferences={"tech": 0.8, "fashion": 0.6, "food": 0.7},
            region="Kanto",
        ),
        prompt_template="You are an agent representing {agent_id} prefecture in Japan.",
        created_at="2023-06-20T00:00:00",
    )


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str) -> Dict[str, str]:
    """Delete an agent by ID."""
    # This is a placeholder, implementation will be added later
    if agent_id not in ["Tokyo", "Osaka", "Hokkaido"]:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {"message": f"Agent {agent_id} deleted successfully"}
