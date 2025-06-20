from typing import List
from pydantic import BaseModel, Field

from src.core.db_settings import DatabaseSettings
from src.core.llm_settings import LLMSettings


class AppSettings(BaseModel):
    """Application settings."""

    app_name: str = Field(default="Multi-Agent Impact Assessment System")
    debug: bool = Field(default=False)
    environment: str = Field(default="development")
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    allowed_origins: List[str] = Field(default=["*"])

    @classmethod
    def from_env(cls) -> "AppSettings":
        """Create settings from environment variables."""
        from os import environ
        from dotenv import load_dotenv

        load_dotenv()

        return cls(
            app_name=environ.get("APP_NAME", "Multi-Agent Impact Assessment System"),
            debug=environ.get("DEBUG", "false").lower() == "true",
            environment=environ.get("ENVIRONMENT", "development"),
            database=DatabaseSettings.from_env(),
            llm=LLMSettings.from_env(),
            allowed_origins=environ.get("ALLOWED_ORIGINS", "*").split(","),
        )


# Create a singleton instance of AppSettings
settings = AppSettings.from_env()
