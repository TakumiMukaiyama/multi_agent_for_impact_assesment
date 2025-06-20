from enum import Enum
from typing import Dict, Union
from pydantic import BaseModel, Field, SecretStr


class LLMProviderType(str, Enum):
    """Supported LLM provider types."""

    AZURE_OPENAI = "azure_openai"
    OPENAI = "openai"
    GEMINI = "gemini"
    NOMUCHAT = "nomuchat"


class BaseProviderSettings(BaseModel):
    """Base model for LLM provider settings."""

    enabled: bool = Field(default=False)
    api_key: SecretStr = Field(default="")


class AzureOpenAISettings(BaseProviderSettings):
    """Azure OpenAI specific settings."""

    api_version: str = Field(default="2023-05-15")
    endpoint: str = Field(default="")
    deployment_id: str = Field(default="")


class OpenAISettings(BaseProviderSettings):
    """OpenAI specific settings."""

    model_name: str = Field(default="gpt-4o")


class GeminiSettings(BaseProviderSettings):
    """Google Gemini specific settings."""

    model_name: str = Field(default="gemini-pro")


class NomuchatSettings(BaseProviderSettings):
    """Nomuchat specific settings."""

    endpoint: str = Field(default="")
    model_name: str = Field(default="")


class LLMSettings(BaseModel):
    """LLM settings for the application."""

    default_provider: LLMProviderType = Field(default=LLMProviderType.OPENAI)
    providers: Dict[
        LLMProviderType,
        Union[AzureOpenAISettings, OpenAISettings, GeminiSettings, NomuchatSettings],
    ] = Field(
        default_factory=lambda: {
            LLMProviderType.AZURE_OPENAI: AzureOpenAISettings(),
            LLMProviderType.OPENAI: OpenAISettings(),
            LLMProviderType.GEMINI: GeminiSettings(),
            LLMProviderType.NOMUCHAT: NomuchatSettings(),
        }
    )

    @classmethod
    def from_env(cls) -> "LLMSettings":
        """Create settings from environment variables."""
        from os import environ
        from dotenv import load_dotenv

        load_dotenv()

        # Default provider
        default_provider = LLMProviderType(
            environ.get("DEFAULT_LLM_PROVIDER", LLMProviderType.OPENAI.value)
        )

        # Azure OpenAI settings
        azure_openai = AzureOpenAISettings(
            enabled=environ.get("AZURE_OPENAI_ENABLED", "false").lower() == "true",
            api_key=SecretStr(environ.get("AZURE_OPENAI_API_KEY", "")),
            api_version=environ.get("AZURE_OPENAI_API_VERSION", "2023-05-15"),
            endpoint=environ.get("AZURE_OPENAI_ENDPOINT", ""),
            deployment_id=environ.get("AZURE_OPENAI_DEPLOYMENT_ID", ""),
        )

        # OpenAI settings
        openai = OpenAISettings(
            enabled=environ.get("OPENAI_ENABLED", "false").lower() == "true",
            api_key=SecretStr(environ.get("OPENAI_API_KEY", "")),
            model_name=environ.get("OPENAI_MODEL_NAME", "gpt-4o"),
        )

        # Gemini settings
        gemini = GeminiSettings(
            enabled=environ.get("GEMINI_ENABLED", "false").lower() == "true",
            api_key=SecretStr(environ.get("GEMINI_API_KEY", "")),
            model_name=environ.get("GEMINI_MODEL_NAME", "gemini-pro"),
        )

        # Nomuchat settings
        nomuchat = NomuchatSettings(
            enabled=environ.get("NOMUCHAT_ENABLED", "false").lower() == "true",
            api_key=SecretStr(environ.get("NOMUCHAT_API_KEY", "")),
            endpoint=environ.get("NOMUCHAT_ENDPOINT", ""),
            model_name=environ.get("NOMUCHAT_MODEL_NAME", ""),
        )

        return cls(
            default_provider=default_provider,
            providers={
                LLMProviderType.AZURE_OPENAI: azure_openai,
                LLMProviderType.OPENAI: openai,
                LLMProviderType.GEMINI: gemini,
                LLMProviderType.NOMUCHAT: nomuchat,
            },
        )
