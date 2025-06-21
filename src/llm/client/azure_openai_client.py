from langchain_openai.chat_models import AzureChatOpenAI
from langchain_openai.embeddings import AzureOpenAIEmbeddings

from src.core.constants import LLMProviderType
from src.core.llm_settings import llm_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AzureOpenAIClient:
    """Azure OpenAI API client class.

    Provides chat and embedding functionality.
    """

    def __init__(
        self,
        base_url: str = None,
        api_version: str = None,
        api_key: str = None,
        deployment_name: str = None,
        embedding_model: str = None,
    ) -> None:
        """Constructor.

        Retrieves necessary information from configuration file

        Args:
            base_url: Azure OpenAI API endpoint URL
            api_version: Azure OpenAI API version
            api_key: Azure OpenAI API key
            deployment_name: Deployment name
            embedding_model: Embedding model name
        """
        self.base_url: str = base_url or llm_settings.providers[LLMProviderType.AZURE_OPENAI].endpoint
        self.api_version: str = api_version or llm_settings.providers[LLMProviderType.AZURE_OPENAI].api_version
        self.api_key: str = api_key or llm_settings.providers[LLMProviderType.AZURE_OPENAI].api_key
        self.deployment_name: str = deployment_name or llm_settings.providers[LLMProviderType.AZURE_OPENAI].deployment_id
        self.embedding_model: str = embedding_model or llm_settings.providers[LLMProviderType.AZURE_OPENAI].embedding_model
        self.chat_model: AzureChatOpenAI | None = None
        self.embedding_model_instance: AzureOpenAIEmbeddings | None = None

    def initialize_chat(self) -> AzureChatOpenAI:
        """Initialize chat model.

        Returns:
            ChatOpenAI: Initialized chat model
        """
        # Disable parallel_tool_calls for o3-mini model
        if self.deployment_name and "o3-mini" in self.deployment_name:
            return AzureChatOpenAI(
                azure_endpoint=self.base_url,
                azure_deployment=self.deployment_name,
                api_version=self.api_version,
                api_key=self.api_key,
                disabled_params={"parallel_tool_calls": None},
            )
        return AzureChatOpenAI(
            azure_endpoint=self.base_url,
            azure_deployment=self.deployment_name,
            api_version=self.api_version,
            api_key=self.api_key,
        )

    def initialize_embedding(self) -> AzureOpenAIEmbeddings:
        """Initialize embedding model.

        Returns:
            OpenAIEmbeddings: Initialized embedding model
        """
        return AzureOpenAIEmbeddings(
            model=self.embedding_model,
            azure_endpoint=self.base_url,
            azure_deployment=self.embedding_model,
            api_version=self.api_version,
            api_key=self.api_key,
        )
