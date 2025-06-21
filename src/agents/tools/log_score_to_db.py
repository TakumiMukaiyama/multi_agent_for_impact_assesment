"""Tool for logging agent scores to the database."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.agents.schemas.tools.log_score_to_db import LogScoreToDbInput, LogScoreToDbOutput
from src.agents.tools.base import BaseAgentTool
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LogScoreToDb(BaseAgentTool[LogScoreToDbInput, LogScoreToDbOutput]):
    """Tool for logging agent scores to the database."""

    def __init__(self):
        """Initialize the tool."""
        super().__init__(
            name="log_score_to_db",
            description="Log agent evaluation scores to the database. Requires agent_id, ad_id, liking, and purchase_intent. Optional: commentary, neighbors_used, additional_data.",
        )

        # Mock database storage (in real implementation, this would be a real database)
        self.mock_database = []
        self._log_counter = 1

    async def execute(self, input_data: LogScoreToDbInput) -> LogScoreToDbOutput:
        """Execute the tool to log scores to database.

        Args:
            input_data: Input containing scores and metadata to log

        Returns:
            Output containing log information
        """
        agent_id = input_data.agent_id
        ad_id = input_data.ad_id
        liking = input_data.liking
        purchase_intent = input_data.purchase_intent
        commentary = input_data.commentary
        neighbors_used = input_data.neighbors_used or []
        additional_data = input_data.additional_data or {}

        try:
            # Create log entry
            current_time = datetime.now()
            log_id = f"log_{self._log_counter:06d}_{agent_id}_{ad_id}"

            log_entry = {
                "log_id": log_id,
                "agent_id": agent_id,
                "ad_id": ad_id,
                "liking_score": liking,
                "purchase_intent_score": purchase_intent,
                "commentary": commentary,
                "neighbors_used": neighbors_used,
                "additional_data": additional_data,
                "logged_at": current_time.isoformat(),
                "created_by": "LogScoreToDb_tool",
            }

            # Store in mock database
            self.mock_database.append(log_entry)
            self._log_counter += 1

            logger.info(f"Logged scores for agent {agent_id} on ad {ad_id} - Log ID: {log_id}")

            # In a real implementation, you would:
            # 1. Connect to your database (MongoDB, PostgreSQL, etc.)
            # 2. Create appropriate tables/collections if they don't exist
            # 3. Insert the log entry
            # 4. Handle any database errors
            # 5. Return confirmation of successful storage

            return LogScoreToDbOutput(
                success=True,
                log_id=log_id,
                logged_at=current_time.isoformat(),
                record_count=1,  # Single record logged
                storage_location="mock_database",  # In real implementation: database name/table
            )

        except Exception as e:
            logger.error(f"Error logging scores to database for agent {agent_id}: {e}")
            return LogScoreToDbOutput(
                success=False,
                message=f"Failed to log scores: {str(e)}",
                log_id="",
                logged_at="",
                record_count=0,
                storage_location="",
            )

    def get_logged_entries(self, agent_id: Optional[str] = None, ad_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get logged entries (for testing/debugging purposes).

        Args:
            agent_id: Optional filter by agent ID
            ad_id: Optional filter by ad ID

        Returns:
            List of logged entries matching criteria
        """
        entries = self.mock_database.copy()

        if agent_id:
            entries = [e for e in entries if e["agent_id"] == agent_id]

        if ad_id:
            entries = [e for e in entries if e["ad_id"] == ad_id]

        return entries

    def clear_logs(self) -> int:
        """Clear all logged entries (for testing purposes).

        Returns:
            Number of entries cleared
        """
        count = len(self.mock_database)
        self.mock_database.clear()
        self._log_counter = 1
        logger.info(f"Cleared {count} log entries")
        return count
