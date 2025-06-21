from enum import Enum

class LLMProviderType(str, Enum):
    """Supported LLM provider types."""

    AZURE_OPENAI = "azure_openai"
    OPENAI = "openai"
    GEMINI = "gemini"
