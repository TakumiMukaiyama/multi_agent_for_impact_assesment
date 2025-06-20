from fastapi import APIRouter

from src.api.v1 import agent, ad, graph

api_router = APIRouter()

# Include all v1 routers
api_router.include_router(agent.router, prefix="/agents", tags=["agents"])
api_router.include_router(ad.router, prefix="/ads", tags=["ads"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
