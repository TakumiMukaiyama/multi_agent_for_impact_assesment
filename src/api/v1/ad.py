from typing import Dict, List, Optional
from uuid import UUID, uuid4
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


# Ad schemas
class AdCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None


class AdResponse(AdCreate):
    id: UUID = Field(default_factory=uuid4)
    published_at: str


class AgentScoreResponse(BaseModel):
    agent_id: str
    liking: float
    purchase_intent: float
    neighbors_used: List[str]
    commentary: str


class AdEvaluationResponse(BaseModel):
    ad_id: UUID
    scores: List[AgentScoreResponse]


@router.get("/")
async def list_ads() -> List[AdResponse]:
    """Get all available ads."""
    # This is a placeholder, implementation will be added later
    return [
        AdResponse(
            id=uuid4(),
            title="New Smartphone Launch",
            content="Introducing our latest smartphone with amazing features!",
            category="Technology",
            published_at="2023-06-20T00:00:00"
        ),
        AdResponse(
            id=uuid4(),
            title="Summer Fashion Collection",
            content="Discover our new summer fashion collection with great discounts!",
            category="Fashion",
            published_at="2023-06-21T00:00:00"
        )
    ]


@router.post("/", status_code=201)
async def create_ad(ad: AdCreate) -> AdResponse:
    """Create a new ad."""
    # This is a placeholder, implementation will be added later
    return AdResponse(
        id=uuid4(),
        title=ad.title,
        content=ad.content,
        category=ad.category,
        published_at="2023-06-20T00:00:00"
    )


@router.get("/{ad_id}")
async def get_ad(ad_id: UUID) -> AdResponse:
    """Get an ad by ID."""
    # This is a placeholder, implementation will be added later
    return AdResponse(
        id=ad_id,
        title="New Smartphone Launch",
        content="Introducing our latest smartphone with amazing features!",
        category="Technology",
        published_at="2023-06-20T00:00:00"
    )


@router.delete("/{ad_id}")
async def delete_ad(ad_id: UUID) -> Dict[str, str]:
    """Delete an ad by ID."""
    # This is a placeholder, implementation will be added later
    return {"message": f"Ad {ad_id} deleted successfully"}


@router.post("/{ad_id}/evaluate")
async def evaluate_ad(ad_id: UUID) -> AdEvaluationResponse:
    """Evaluate an ad using the multi-agent system."""
    # This is a placeholder, implementation will be added later
    return AdEvaluationResponse(
        ad_id=ad_id,
        scores=[
            AgentScoreResponse(
                agent_id="Tokyo",
                liking=4.2,
                purchase_intent=3.8,
                neighbors_used=["Chiba", "Saitama"],
                commentary="This ad would resonate well with the tech-savvy population, especially young professionals"
            ),
            AgentScoreResponse(
                agent_id="Osaka",
                liking=3.9,
                purchase_intent=3.5,
                neighbors_used=["Kyoto", "Hyogo"],
                commentary="The ad has a good appeal, but could use more regional references to connect better"
            )
        ]
    )