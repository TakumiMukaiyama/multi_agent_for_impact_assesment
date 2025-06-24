"""
TruLens setup and configuration module.
"""

from typing import Optional

# Use modern TruLens API (v1.5+)
from trulens.core import Tru

from src.utils.logger import get_logger

logger = get_logger(__name__)


class TruLensSetup:
    """Setup and configuration class for TruLens monitoring."""

    def __init__(
        self,
        database_url: Optional[str] = None,
        database_prefix: str = "trulens",
        reset_database: bool = False,
    ):
        """Initialize TruLens setup.

        Args:
            database_url: Database URL for TruLens data storage
            database_prefix: Prefix for TruLens database tables
            reset_database: Whether to reset the database on initialization
        """
        self.database_url = database_url
        self.database_prefix = database_prefix
        self.reset_database = reset_database
        self._session: Optional[Tru] = None

    def initialize(self) -> Tru:
        """Initialize TruLens session.

        Returns:
            Initialized TruLens session
        """
        try:
            # Initialize TruLens session
            if self.database_url:
                self._session = Tru(database_url=self.database_url)
            else:
                # Use default SQLite database
                self._session = Tru()

            # Reset database if requested
            if self.reset_database:
                self._session.reset_database()
                logger.info("TruLens database reset completed")

            logger.info("TruLens session initialized successfully")
            return self._session

        except Exception as e:
            logger.error(f"Failed to initialize TruLens session: {e}")
            raise

    def get_session(self) -> Tru:
        """Get the current TruLens session.

        Returns:
            Current TruLens session

        Raises:
            RuntimeError: If session is not initialized
        """
        if self._session is None:
            raise RuntimeError("TruLens session not initialized. Call initialize() first.")
        return self._session

    def start_dashboard(self, port: int = 8501, force: bool = False) -> None:
        """Start TruLens dashboard.

        Args:
            port: Port number for the dashboard
            force: Whether to force start even if port is in use
        """
        try:
            if self._session is None:
                self.initialize()

            logger.info(f"Starting TruLens dashboard on port {port}")
            self._session.run_dashboard(port=port, force=force)

        except Exception as e:
            logger.error(f"Failed to start TruLens dashboard: {e}")
            raise

    def stop_dashboard(self) -> None:
        """Stop TruLens dashboard."""
        try:
            if self._session is not None:
                self._session.stop_dashboard()
                logger.info("TruLens dashboard stopped")

        except Exception as e:
            logger.error(f"Failed to stop TruLens dashboard: {e}")
            raise
