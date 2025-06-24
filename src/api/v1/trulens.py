"""
TruLens monitoring and visualization API endpoints.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.llm.monitoring import FeedbackFunctions, TruLensSetup, TruLensWrapper
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Global TruLens setup instance
_trulens_setup: Optional[TruLensSetup] = None
_trulens_wrapper: Optional[TruLensWrapper] = None


class TruLensStatus(BaseModel):
    """TruLens system status."""

    initialized: bool
    dashboard_running: bool
    database_url: Optional[str]
    total_apps: int
    total_records: int


class DashboardConfig(BaseModel):
    """Dashboard configuration."""

    port: int = 8501
    force: bool = False


class LeaderboardEntry(BaseModel):
    """Leaderboard entry."""

    app_name: str
    app_version: str
    avg_score: float
    total_records: int


def _get_trulens_setup() -> TruLensSetup:
    """Get or initialize TruLens setup."""
    global _trulens_setup
    if _trulens_setup is None:
        _trulens_setup = TruLensSetup()
        _trulens_setup.initialize()
    return _trulens_setup


def _get_trulens_wrapper() -> TruLensWrapper:
    """Get or initialize TruLens wrapper."""
    global _trulens_wrapper
    if _trulens_wrapper is None:
        setup = _get_trulens_setup()
        feedback_functions = FeedbackFunctions()
        _trulens_wrapper = TruLensWrapper(
            trulens_setup=setup,
            feedback_functions=feedback_functions,
        )
    return _trulens_wrapper


@router.get("/status")
async def get_trulens_status() -> TruLensStatus:
    """Get TruLens system status."""
    try:
        setup = _get_trulens_setup()
        session = setup.get_session()

        # Get basic statistics
        leaderboard = session.get_leaderboard()
        records = session.get_records_and_feedback()

        return TruLensStatus(
            initialized=True,
            dashboard_running=False,  # We can't easily check this, assume false
            database_url=setup.database_url,
            total_apps=len(leaderboard) if leaderboard is not None else 0,
            total_records=len(records) if records is not None else 0,
        )

    except Exception as e:
        logger.error(f"Failed to get TruLens status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get TruLens status: {str(e)}")


@router.post("/dashboard/start")
async def start_dashboard(config: DashboardConfig) -> Dict[str, str]:
    """Start TruLens dashboard."""
    try:
        setup = _get_trulens_setup()
        setup.start_dashboard(port=config.port, force=config.force)

        return {
            "message": f"TruLens dashboard started on port {config.port}",
            "url": f"http://localhost:{config.port}",
        }

    except Exception as e:
        logger.error(f"Failed to start TruLens dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start dashboard: {str(e)}")


@router.post("/dashboard/stop")
async def stop_dashboard() -> Dict[str, str]:
    """Stop TruLens dashboard."""
    try:
        setup = _get_trulens_setup()
        setup.stop_dashboard()

        return {"message": "TruLens dashboard stopped"}

    except Exception as e:
        logger.error(f"Failed to stop TruLens dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop dashboard: {str(e)}")


@router.get("/leaderboard")
async def get_leaderboard() -> List[Dict[str, Any]]:
    """Get TruLens leaderboard."""
    try:
        wrapper = _get_trulens_wrapper()
        leaderboard = wrapper.get_leaderboard()

        if leaderboard is None:
            return []

        # Convert to list of dictionaries if needed
        if hasattr(leaderboard, "to_dict"):
            return leaderboard.to_dict("records")
        elif hasattr(leaderboard, "__iter__"):
            return list(leaderboard)
        else:
            return [leaderboard]

    except Exception as e:
        logger.error(f"Failed to get leaderboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get leaderboard: {str(e)}")


@router.get("/records")
async def get_records(
    app_name: Optional[str] = Query(None, description="Filter by app name"),
    limit: Optional[int] = Query(100, description="Maximum number of records to return"),
) -> List[Dict[str, Any]]:
    """Get TruLens evaluation records."""
    try:
        wrapper = _get_trulens_wrapper()
        records = wrapper.get_records(app_name=app_name)

        if records is None:
            return []

        # Convert to list of dictionaries if needed
        if hasattr(records, "to_dict"):
            record_list = records.to_dict("records")
        elif hasattr(records, "__iter__"):
            record_list = list(records)
        else:
            record_list = [records]

        # Apply limit
        if limit and len(record_list) > limit:
            record_list = record_list[:limit]

        return record_list

    except Exception as e:
        logger.error(f"Failed to get records: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get records: {str(e)}")


@router.get("/apps")
async def get_apps() -> List[Dict[str, Any]]:
    """Get list of monitored applications."""
    try:
        wrapper = _get_trulens_wrapper()
        session = wrapper.session

        # Get app information from leaderboard
        leaderboard = session.get_leaderboard()

        if leaderboard is None:
            return []

        apps = []
        if hasattr(leaderboard, "iterrows"):
            # Pandas DataFrame
            for _, row in leaderboard.iterrows():
                apps.append(
                    {
                        "app_name": row.get("app_name", "unknown"),
                        "app_version": row.get("app_version", "unknown"),
                        "total_records": row.get("total_records", 0),
                        "avg_score": row.get("avg_score", 0.0),
                    }
                )
        elif hasattr(leaderboard, "__iter__"):
            # List or similar iterable
            for item in leaderboard:
                if isinstance(item, dict):
                    apps.append(item)

        return apps

    except Exception as e:
        logger.error(f"Failed to get apps: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get apps: {str(e)}")


@router.delete("/reset")
async def reset_database() -> Dict[str, str]:
    """Reset TruLens database (caution: this will delete all data)."""
    try:
        wrapper = _get_trulens_wrapper()
        wrapper.reset_database()

        return {"message": "TruLens database reset successfully"}

    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset database: {str(e)}")


@router.get("/feedback-functions")
async def get_available_feedback_functions() -> List[Dict[str, Any]]:
    """Get available feedback functions."""
    return [
        {
            "name": "relevance",
            "description": "Measures how relevant the response is to the input",
            "type": "input_output",
        },
        {
            "name": "groundedness",
            "description": "Measures how grounded the response is in factual information",
            "type": "input_output",
        },
        {
            "name": "context_relevance",
            "description": "Measures how relevant the context is to the input",
            "type": "input_output",
        },
        {
            "name": "sentiment",
            "description": "Analyzes the sentiment of the response",
            "type": "output",
        },
        {
            "name": "comprehensiveness",
            "description": "Measures how comprehensive the response is",
            "type": "input_output",
        },
        {
            "name": "toxicity",
            "description": "Detects harmful or toxic content in the response",
            "type": "output",
        },
        {
            "name": "bias",
            "description": "Detects bias and stereotypes in the response",
            "type": "output",
        },
    ]
