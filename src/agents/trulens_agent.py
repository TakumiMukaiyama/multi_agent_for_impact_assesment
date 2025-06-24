"""
TruLens-enhanced Prefecture Agent for monitoring and evaluation.
"""

from typing import Any, Dict, List, Optional

from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from trulens.core.feedback import Feedback

from src.agents.base import AgentConfig, PrefectureAgent
from src.core.constants import LLMProviderType
from src.llm.monitoring import FeedbackFunctions, TruLensSetup, TruLensWrapper
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TruLensPrefectureAgent(PrefectureAgent):
    """TruLens-enhanced prefecture agent with monitoring and evaluation capabilities."""

    def __init__(
        self,
        config: AgentConfig,
        tools: List[BaseTool],
        llm: Optional[ChatOpenAI] = None,
        enable_trulens: bool = True,
        custom_feedbacks: Optional[List[Feedback]] = None,
        trulens_database_url: Optional[str] = None,
    ):
        """Initialize a new TruLens-enhanced prefecture agent.

        Args:
            config: Agent configuration
            tools: List of tools available to the agent
            llm: Language model to use (if None, default will be created)
            enable_trulens: Whether to enable TruLens monitoring
            custom_feedbacks: Custom feedback functions for evaluation
            trulens_database_url: Optional database URL for TruLens
        """
        # Initialize parent class first
        super().__init__(config, tools, llm)

        self.enable_trulens = enable_trulens
        self.trulens_wrapper = None
        self.wrapped_agent = None

        # Initialize TruLens if enabled
        if self.enable_trulens:
            self._setup_trulens(custom_feedbacks, trulens_database_url)

    def _setup_trulens(
        self,
        custom_feedbacks: Optional[List[Feedback]] = None,
        database_url: Optional[str] = None,
    ):
        """Set up TruLens monitoring for the agent.

        Args:
            custom_feedbacks: Custom feedback functions to use
            database_url: Optional database URL for TruLens
        """
        try:
            # Initialize TruLens setup
            trulens_setup = TruLensSetup(database_url=database_url)
            trulens_setup.initialize()

            # Determine provider type based on LLM configuration
            provider_type = LLMProviderType.AZURE_OPENAI
            if hasattr(self.llm, "azure_endpoint"):
                provider_type = LLMProviderType.AZURE_OPENAI
            elif hasattr(self.llm, "google_api_key"):
                provider_type = LLMProviderType.GEMINI

            # Initialize feedback functions
            feedback_functions = FeedbackFunctions(provider_type=provider_type)

            # Initialize TruLens wrapper
            self.trulens_wrapper = TruLensWrapper(
                trulens_setup=trulens_setup,
                feedback_functions=feedback_functions,
            )

            # Use custom feedbacks or agent-specific ones
            feedbacks = custom_feedbacks or feedback_functions.get_agent_feedbacks()

            # Wrap the agent executor
            self.wrapped_agent = self.trulens_wrapper.wrap_agent(
                agent=self.agent_executor,
                app_name=f"prefecture_agent_{self.config.agent_id}",
                app_version="1.0",
                feedbacks=feedbacks,
                metadata={
                    "type": "prefecture_agent",
                    "agent_id": self.config.agent_id,
                    "tools": [tool.name for tool in self.tools],
                    "memory_enabled": self.config.use_memory,
                    "persona": self.config.persona_config,
                },
            )

            logger.info(f"TruLens monitoring enabled for agent {self.config.agent_id}")

        except Exception as e:
            logger.warning(f"Failed to setup TruLens monitoring for agent {self.config.agent_id}: {e}")
            logger.warning("Continuing without TruLens monitoring")
            self.enable_trulens = False

    async def run(self, input_text: str) -> Dict[str, Any]:
        """Run the agent on the given input text with TruLens monitoring.

        Args:
            input_text: Input text for the agent

        Returns:
            Agent execution result
        """
        # Choose which agent to use
        agent_to_use = self.wrapped_agent if (self.enable_trulens and self.wrapped_agent) else self.agent_executor

        try:
            # Run the agent
            result = await agent_to_use.ainvoke({"input": input_text})

            # Add agent-specific metadata to the result
            if isinstance(result, dict):
                result["agent_id"] = self.config.agent_id
                result["trulens_enabled"] = self.enable_trulens

            return result

        except Exception as e:
            logger.error(f"Error running agent {self.config.agent_id}: {e}")
            raise

    def get_trulens_leaderboard(self) -> Any:
        """Get TruLens leaderboard data for this agent.

        Returns:
            TruLens leaderboard data or None if TruLens is not enabled
        """
        if self.enable_trulens and self.trulens_wrapper:
            return self.trulens_wrapper.get_leaderboard()
        return None

    def get_trulens_records(self) -> Any:
        """Get TruLens evaluation records for this agent.

        Returns:
            TruLens evaluation records or None if TruLens is not enabled
        """
        if self.enable_trulens and self.trulens_wrapper:
            app_name = f"prefecture_agent_{self.config.agent_id}"
            return self.trulens_wrapper.get_records(app_name=app_name)
        return None

    def start_trulens_dashboard(self, port: int = 8501, force: bool = False) -> None:
        """Start TruLens dashboard.

        Args:
            port: Port number for the dashboard
            force: Whether to force start even if port is in use
        """
        if self.enable_trulens and self.trulens_wrapper:
            self.trulens_wrapper.trulens_setup.start_dashboard(port=port, force=force)
        else:
            logger.warning(f"TruLens is not enabled for agent {self.config.agent_id}")

    def get_agent_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the agent including TruLens status.

        Returns:
            Dictionary containing agent configuration and status
        """
        info = {
            "agent_id": self.config.agent_id,
            "persona_config": self.config.persona_config,
            "use_memory": self.config.use_memory,
            "tools": [tool.name for tool in self.tools],
            "llm_type": type(self.llm).__name__,
            "trulens_enabled": self.enable_trulens,
        }

        if self.enable_trulens and self.wrapped_agent:
            info["trulens_app_id"] = getattr(self.wrapped_agent, "app_id", None)
            info["trulens_app_name"] = f"prefecture_agent_{self.config.agent_id}"

        return info

    def disable_trulens(self) -> None:
        """Disable TruLens monitoring for this agent."""
        self.enable_trulens = False
        self.wrapped_agent = None
        logger.info(f"TruLens monitoring disabled for agent {self.config.agent_id}")

    def enable_trulens_monitoring(
        self,
        custom_feedbacks: Optional[List[Feedback]] = None,
        database_url: Optional[str] = None,
    ) -> None:
        """Enable TruLens monitoring for this agent.

        Args:
            custom_feedbacks: Custom feedback functions to use
            database_url: Optional database URL for TruLens
        """
        if not self.enable_trulens:
            self.enable_trulens = True
            self._setup_trulens(custom_feedbacks, database_url)
