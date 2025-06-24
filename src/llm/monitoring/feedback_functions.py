"""
Feedback functions for TruLens evaluation.
"""

from typing import List

# Use modern TruLens API (v1.5+)
from trulens.core.feedback import Feedback
from trulens.providers.litellm import LiteLLM
from trulens.providers.openai import OpenAI as TruLensOpenAI

from src.core.constants import LLMProviderType
from src.core.llm_settings import llm_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FeedbackFunctions:
    """Collection of feedback functions for LLM evaluation."""

    def __init__(self, provider_type: LLMProviderType = LLMProviderType.AZURE_OPENAI):
        """Initialize feedback functions.

        Args:
            provider_type: LLM provider type for feedback evaluation
        """
        self.provider_type = provider_type
        self.provider = self._initialize_provider()

    def _initialize_provider(self):
        """Initialize the TruLens provider based on the configured LLM provider."""
        try:
            if self.provider_type == LLMProviderType.AZURE_OPENAI:
                azure_config = llm_settings.providers[LLMProviderType.AZURE_OPENAI]
                return TruLensOpenAI(
                    model_engine=azure_config.deployment_id,
                    api_key=azure_config.api_key,
                    azure_endpoint=azure_config.endpoint,  # Updated parameter name
                    api_version=azure_config.api_version,
                )
            elif self.provider_type == LLMProviderType.GEMINI:
                gemini_config = llm_settings.providers[LLMProviderType.GEMINI]
                return LiteLLM(
                    model="gemini/gemini-1.5-pro",  # Updated model name
                    api_key=gemini_config.api_key,
                )
            else:
                raise ValueError(f"Unsupported provider type: {self.provider_type}")

        except Exception as e:
            logger.error(f"Failed to initialize TruLens provider: {e}")
            raise

    @staticmethod
    def create_openai_provider() -> TruLensOpenAI:
        """Create OpenAI provider based on configuration."""
        if llm_settings.provider == LLMProviderType.AZURE_OPENAI:
            return TruLensOpenAI(
                # Use azure_endpoint instead of api_base for newer versions
                azure_endpoint=llm_settings.azure_endpoint,
                api_key=llm_settings.azure_api_key,
                api_version=llm_settings.azure_api_version,
                deployment_name=llm_settings.azure_deployment_id,
            )
        else:
            return TruLensOpenAI(
                api_key=llm_settings.openai_api_key,
                model_engine=llm_settings.openai_model or "gpt-3.5-turbo",
            )

    @staticmethod
    def create_litellm_provider() -> LiteLLM:
        """Create LiteLLM provider based on configuration."""
        if llm_settings.provider == LLMProviderType.GEMINI:
            return LiteLLM(
                # Updated model name for newer versions
                model_engine="gemini/gemini-1.5-pro",
                api_key=llm_settings.gemini_api_key,
            )
        else:
            return LiteLLM()

    @classmethod
    def get_relevance_feedback(cls) -> Feedback:
        """Get relevance feedback function."""
        provider = cls.create_openai_provider()
        return (
            Feedback(
                provider.relevance_with_cot_reasons,
                name="Answer Relevance",  # Add name parameter
            )
            .on_input()
            .on_output()
        )

    @classmethod
    def get_context_relevance_feedback(cls) -> Feedback:
        """Get context relevance feedback function."""
        provider = cls.create_openai_provider()
        return (
            Feedback(
                provider.context_relevance_with_cot_reasons,
                name="Context Relevance",  # Add name parameter
            )
            .on_input()
            .on_output()
        )

    @classmethod
    def get_groundedness_feedback(cls) -> Feedback:
        """Get groundedness feedback function."""
        provider = cls.create_openai_provider()
        return (
            Feedback(
                provider.groundedness_measure_with_cot_reasons,
                name="Groundedness",  # Add name parameter
            )
            .on_input()
            .on_output()
        )

    @classmethod
    def get_sentiment_feedback(cls) -> Feedback:
        """Get sentiment feedback function."""
        provider = cls.create_openai_provider()
        return Feedback(
            provider.sentiment_with_cot_reasons,
            name="Sentiment",  # Add name parameter
        ).on_output()

    @classmethod
    def get_toxicity_feedback(cls) -> Feedback:
        """Get toxicity feedback function."""
        provider = cls.create_openai_provider()
        return Feedback(
            provider.harmfulness_with_cot_reasons,
            name="Toxicity",  # Add name parameter
        ).on_output()

    @classmethod
    def get_coherence_feedback(cls) -> Feedback:
        """Get coherence feedback function."""
        provider = cls.create_openai_provider()
        return Feedback(
            provider.coherence_with_cot_reasons,
            name="Coherence",  # Add name parameter
        ).on_output()

    @classmethod
    def get_bias_feedback(cls) -> Feedback:
        """Get bias feedback function."""
        provider = cls.create_openai_provider()
        return (
            Feedback(
                provider.stereotypes_with_cot_reasons,
                name="Bias Detection",  # Add name parameter
            )
            .on_input()
            .on_output()
        )

    def get_standard_feedbacks(self) -> List[Feedback]:
        """Get a standard set of feedback functions for general LLM evaluation.

        Returns:
            List of standard feedback functions
        """
        return [
            self.get_relevance_feedback(),
            self.get_groundedness_feedback(),
            self.get_sentiment_feedback(),
            self.get_toxicity_feedback(),
        ]

    def get_agent_feedbacks(self) -> List[Feedback]:
        """Get feedback functions specifically for agent evaluation.

        Returns:
            List of agent-specific feedback functions
        """
        return [
            self.get_relevance_feedback(),
            self.get_coherence_feedback(),
            self.get_sentiment_feedback(),
            self.get_bias_feedback(),
        ]

    def get_rag_feedbacks(self) -> List[Feedback]:
        """Get feedback functions specifically for RAG evaluation.

        Returns:
            List of RAG-specific feedback functions
        """
        return [
            self.get_relevance_feedback(),
            self.get_groundedness_feedback(),
            self.get_context_relevance_feedback(),
            self.get_toxicity_feedback(),
        ]
