"""
TruLens wrapper for LangChain applications.
"""

from typing import Any, Dict, List, Optional, Union

from langchain.chains.base import Chain
from langchain_core.runnables import Runnable

# Use modern TruLens API (v1.5+)
from trulens.apps.app import TruApp
from trulens.core import Tru
from trulens.core.feedback import Feedback

from src.llm.monitoring.feedback_functions import FeedbackFunctions
from src.llm.monitoring.trulens_setup import TruLensSetup
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TruLensWrapper:
    """Wrapper class for integrating TruLens with LangChain applications."""

    def __init__(
        self,
        trulens_setup: TruLensSetup,
        feedback_functions: Optional[FeedbackFunctions] = None,
    ):
        """Initialize TruLens wrapper.

        Args:
            trulens_setup: TruLens setup instance
            feedback_functions: Feedback functions for evaluation
        """
        self.trulens_setup = trulens_setup
        self.feedback_functions = feedback_functions or FeedbackFunctions()
        self.session: Tru = trulens_setup.get_session()
        self._wrapped_apps: Dict[str, TruApp] = {}

    def wrap_chain(
        self,
        chain: Union[Chain, Runnable],
        app_name: str,
        app_version: str = "1.0",
        feedbacks: Optional[List[Feedback]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TruApp:
        """Wrap a LangChain chain with TruLens monitoring.

        Args:
            chain: LangChain chain to wrap
            app_name: Name of the application
            app_version: Version of the application
            feedbacks: List of feedback functions to apply
            metadata: Additional metadata for the application

        Returns:
            TruLens-wrapped chain
        """
        try:
            # Use standard feedbacks if none provided
            if feedbacks is None:
                feedbacks = self.feedback_functions.get_standard_feedbacks()

            # Create TruApp wrapper (modern API)
            wrapped_chain = TruApp(
                chain,
                app_name=app_name,
                app_version=app_version,
                feedbacks=feedbacks,
                metadata=metadata,
            )

            # Store wrapped app for later reference
            app_key = f"{app_name}_{app_version}"
            self._wrapped_apps[app_key] = wrapped_chain

            logger.info(f"Successfully wrapped chain: {app_name} v{app_version}")
            return wrapped_chain

        except Exception as e:
            logger.error(f"Failed to wrap chain {app_name}: {e}")
            raise

    def wrap_agent(
        self,
        agent: Union[Chain, Runnable],
        app_name: str,
        app_version: str = "1.0",
        feedbacks: Optional[List[Feedback]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TruApp:
        """Wrap an agent with TruLens monitoring.

        Args:
            agent: Agent to wrap
            app_name: Name of the application
            app_version: Version of the application
            feedbacks: List of feedback functions to apply
            metadata: Additional metadata for the application

        Returns:
            TruLens-wrapped agent
        """
        try:
            # Use agent-specific feedbacks if none provided
            if feedbacks is None:
                feedbacks = self.feedback_functions.get_agent_feedbacks()

            # Add agent-specific metadata
            agent_metadata = {
                "type": "agent",
                "framework": "langchain",
                **(metadata or {}),
            }

            return self.wrap_chain(
                agent,
                app_name,
                app_version,
                feedbacks,
                agent_metadata,
            )

        except Exception as e:
            logger.error(f"Failed to wrap agent {app_name}: {e}")
            raise

    def get_wrapped_app(self, app_name: str, app_version: str = "1.0") -> Optional[TruApp]:
        """Get a previously wrapped application.

        Args:
            app_name: Name of the application
            app_version: Version of the application

        Returns:
            Wrapped application if found, None otherwise
        """
        app_key = f"{app_name}_{app_version}"
        return self._wrapped_apps.get(app_key)

    def get_leaderboard(self) -> Any:
        """Get the TruLens leaderboard.

        Returns:
            TruLens leaderboard data
        """
        try:
            return self.session.get_leaderboard()
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}")
            raise

    def get_records(self, app_name: Optional[str] = None) -> Any:
        """Get evaluation records.

        Args:
            app_name: Optional app name to filter records

        Returns:
            Evaluation records
        """
        try:
            if app_name:
                return self.session.get_records_and_feedback(app_ids=[app_name])
            else:
                return self.session.get_records_and_feedback()
        except Exception as e:
            logger.error(f"Failed to get records: {e}")
            raise

    def reset_database(self) -> None:
        """Reset the TruLens database."""
        try:
            self.session.reset_database()
            self._wrapped_apps.clear()
            logger.info("TruLens database reset completed")
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            raise
