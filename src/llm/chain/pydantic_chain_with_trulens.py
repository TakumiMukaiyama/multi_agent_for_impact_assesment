"""
TruLens-integrated version of PydanticChain for LLM monitoring and evaluation.
"""

import time
from typing import Any, Dict, List, Optional, Type, Union

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from trulens.core.feedback import Feedback

from src.core.constants import LLMProviderType
from src.llm.client.azure_openai_client import AzureOpenAIClient
from src.llm.client.gemini_client import GeminiClient
from src.llm.dependancy.base import BaseInput, BaseOutput
from src.llm.monitoring import FeedbackFunctions, TruLensSetup, TruLensWrapper
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TruLensPydanticChain:
    """TruLens-enhanced version of PydanticChain with monitoring and evaluation."""

    def __init__(
        self,
        prompt_template: PromptTemplate,
        input_schema: Type[BaseInput],
        output_schema: Type[BaseOutput],
        llm_client: Union[AzureOpenAIClient, GeminiClient],
        app_name: str,
        app_version: str = "1.0",
        enable_trulens: bool = True,
        custom_feedbacks: Optional[List[Feedback]] = None,
        trulens_database_url: Optional[str] = None,
    ):
        """Initialize the TruLens-enhanced Pydantic chain.

        Args:
            prompt_template: LangChain prompt template to use
            input_schema: Pydantic schema for input validation
            output_schema: Pydantic schema for output parsing
            llm_client: LLM client instance (AzureOpenAI or Gemini)
            app_name: Name of the application for TruLens tracking
            app_version: Version of the application
            enable_trulens: Whether to enable TruLens monitoring
            custom_feedbacks: Custom feedback functions to use
            trulens_database_url: Optional database URL for TruLens
        """
        self.prompt_template = prompt_template
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.llm_client = llm_client
        self.app_name = app_name
        self.app_version = app_version
        self.enable_trulens = enable_trulens

        # Initialize LLM chat model
        if isinstance(llm_client, AzureOpenAIClient):
            self.chat_llm = llm_client.initialize_chat()
        elif isinstance(llm_client, GeminiClient):
            self.chat_llm = llm_client.initialize_chat()
        else:
            raise ValueError(f"Unsupported LLM client type: {type(llm_client)}")

        # Set up output parser and basic chain
        self.parser = PydanticOutputParser(pydantic_object=self.output_schema)
        self.base_chain = self.prompt_template | self.chat_llm | self.parser

        # Initialize TruLens if enabled
        self.trulens_wrapper = None
        self.wrapped_chain = None

        if self.enable_trulens:
            self._setup_trulens(custom_feedbacks, trulens_database_url)

    def _setup_trulens(
        self,
        custom_feedbacks: Optional[List[Feedback]] = None,
        database_url: Optional[str] = None,
    ):
        """Set up TruLens monitoring.

        Args:
            custom_feedbacks: Custom feedback functions to use
            database_url: Optional database URL for TruLens
        """
        try:
            # Initialize TruLens setup
            trulens_setup = TruLensSetup(database_url=database_url)
            trulens_setup.initialize()

            # Initialize feedback functions based on LLM provider
            provider_type = (
                LLMProviderType.AZURE_OPENAI
                if isinstance(self.llm_client, AzureOpenAIClient)
                else LLMProviderType.GEMINI
            )
            feedback_functions = FeedbackFunctions(provider_type=provider_type)

            # Initialize TruLens wrapper
            self.trulens_wrapper = TruLensWrapper(
                trulens_setup=trulens_setup,
                feedback_functions=feedback_functions,
            )

            # Use custom feedbacks or default ones
            feedbacks = custom_feedbacks or feedback_functions.get_standard_feedbacks()

            # Wrap the chain
            self.wrapped_chain = self.trulens_wrapper.wrap_chain(
                chain=self.base_chain,
                app_name=self.app_name,
                app_version=self.app_version,
                feedbacks=feedbacks,
                metadata={
                    "type": "pydantic_chain",
                    "input_schema": self.input_schema.__name__,
                    "output_schema": self.output_schema.__name__,
                    "llm_client": type(self.llm_client).__name__,
                },
            )

            logger.info(f"TruLens monitoring enabled for {self.app_name}")

        except Exception as e:
            logger.warning(f"Failed to setup TruLens monitoring: {e}")
            logger.warning("Continuing without TruLens monitoring")
            self.enable_trulens = False

    def invoke_with_retry(self, inputs: BaseInput, max_retries: int = 10, **kwargs) -> Any:
        """Invoke the chain with retry logic for error handling.

        Args:
            inputs: Input data matching the input schema
            max_retries: Maximum number of retry attempts
            **kwargs: Additional arguments passed to chain invoke

        Returns:
            Parsed output matching the output schema

        Raises:
            Exception: If all retry attempts fail
        """
        try:
            return self.invoke(inputs, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()

            # Handle API key issues
            if any(msg in error_msg for msg in ["invalid api key", "invalid authorization"]):
                # For Azure OpenAI, re-initialize the chat model
                if isinstance(self.llm_client, AzureOpenAIClient):
                    self.chat_llm = self.llm_client.initialize_chat()
                    self.base_chain = self.prompt_template | self.chat_llm | self.parser

                    # Re-wrap if TruLens is enabled
                    if self.enable_trulens and self.trulens_wrapper:
                        self._rewrap_chain()

                    return self.invoke(inputs, **kwargs)
                raise e

            # Handle rate limiting with exponential backoff
            elif any(msg in error_msg for msg in ["rate limit", "requests", "threshold"]):
                last_error = e
                for attempt in range(max_retries - 1):
                    wait_time = min(60 * (2**attempt), 300)
                    time.sleep(wait_time)
                    try:
                        return self.invoke(inputs, **kwargs)
                    except Exception as retry_e:
                        last_error = retry_e
                        continue
                raise last_error

            # Re-raise other errors
            raise e

    def invoke(self, inputs: BaseInput, **kwargs) -> Any:
        """Invoke the chain with input validation.

        Args:
            inputs: Input data matching the input schema
            **kwargs: Additional arguments passed to chain invoke

        Returns:
            Parsed output matching the output schema
        """
        # Validate input
        if not isinstance(inputs, self.input_schema):
            raise ValueError(f"Input must be instance of {self.input_schema.__name__}")

        # Choose which chain to invoke
        chain_to_use = self.wrapped_chain if (self.enable_trulens and self.wrapped_chain) else self.base_chain

        # Invoke chain with validated input
        return chain_to_use.invoke(inputs.model_dump(), **kwargs)

    def _rewrap_chain(self):
        """Re-wrap the chain after LLM client update."""
        if self.enable_trulens and self.trulens_wrapper:
            feedbacks = self.trulens_wrapper.feedback_functions.get_standard_feedbacks()
            self.wrapped_chain = self.trulens_wrapper.wrap_chain(
                chain=self.base_chain,
                app_name=self.app_name,
                app_version=self.app_version,
                feedbacks=feedbacks,
            )

    def update_llm_client(self, llm_client: Union[AzureOpenAIClient, GeminiClient]) -> None:
        """Update the LLM client and reinitialize the chain.

        Args:
            llm_client: New LLM client instance
        """
        self.llm_client = llm_client

        # Re-initialize chat model
        if isinstance(llm_client, AzureOpenAIClient):
            self.chat_llm = llm_client.initialize_chat()
        elif isinstance(llm_client, GeminiClient):
            self.chat_llm = llm_client.initialize_chat()
        else:
            raise ValueError(f"Unsupported LLM client type: {type(llm_client)}")

        # Rebuild chain
        self.base_chain = self.prompt_template | self.chat_llm | self.parser

        # Re-wrap if TruLens is enabled
        if self.enable_trulens and self.trulens_wrapper:
            self._rewrap_chain()

    def get_trulens_leaderboard(self) -> Any:
        """Get TruLens leaderboard data.

        Returns:
            TruLens leaderboard data or None if TruLens is not enabled
        """
        if self.enable_trulens and self.trulens_wrapper:
            return self.trulens_wrapper.get_leaderboard()
        return None

    def get_trulens_records(self) -> Any:
        """Get TruLens evaluation records.

        Returns:
            TruLens evaluation records or None if TruLens is not enabled
        """
        if self.enable_trulens and self.trulens_wrapper:
            return self.trulens_wrapper.get_records(app_name=self.app_name)
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
            logger.warning("TruLens is not enabled for this chain")

    def get_chain_info(self) -> Dict[str, Any]:
        """Get information about the current chain configuration.

        Returns:
            Dictionary containing chain configuration details
        """
        info = {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "input_schema": self.input_schema.__name__,
            "output_schema": self.output_schema.__name__,
            "llm_client_type": type(self.llm_client).__name__,
            "chat_model_type": type(self.chat_llm).__name__,
            "prompt_variables": list(self.prompt_template.input_variables),
            "trulens_enabled": self.enable_trulens,
        }

        if self.enable_trulens and self.wrapped_chain:
            info["trulens_app_id"] = getattr(self.wrapped_chain, "app_id", None)

        return info
