from typing import Optional
from pydantic import BaseModel, Field, SecretStr


class PostgresDBSettings(BaseModel):
    """PostgreSQL database settings."""

    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    user: str = Field(default="postgres")
    password: SecretStr = Field(default="")
    database: str = Field(default="impact_assessment")


class MongoDBSettings(BaseModel):
    """MongoDB database settings."""

    host: str = Field(default="localhost")
    port: int = Field(default=27017)
    user: Optional[str] = Field(default=None)
    password: Optional[SecretStr] = Field(default=None)
    database: str = Field(default="impact_assessment")
    auth_source: Optional[str] = Field(default="admin")


class DatabaseSettings(BaseModel):
    """Database settings for the application."""

    postgres: PostgresDBSettings = Field(default_factory=PostgresDBSettings)
    mongodb: MongoDBSettings = Field(default_factory=MongoDBSettings)

    @classmethod
    def from_env(cls) -> "DatabaseSettings":
        """Create settings from environment variables."""
        from os import environ
        from dotenv import load_dotenv

        load_dotenv()

        # PostgreSQL settings
        postgres = PostgresDBSettings(
            host=environ.get("POSTGRES_HOST", "localhost"),
            port=int(environ.get("POSTGRES_PORT", "5432")),
            user=environ.get("POSTGRES_USER", "postgres"),
            password=SecretStr(environ.get("POSTGRES_PASSWORD", "")),
            database=environ.get("POSTGRES_DB", "impact_assessment"),
        )

        # MongoDB settings
        mongo_user = environ.get("MONGO_USER")
        mongo_password = environ.get("MONGO_PASSWORD")

        mongodb = MongoDBSettings(
            host=environ.get("MONGO_HOST", "localhost"),
            port=int(environ.get("MONGO_PORT", "27017")),
            user=mongo_user if mongo_user else None,
            password=SecretStr(mongo_password) if mongo_password else None,
            database=environ.get("MONGO_DB", "impact_assessment"),
            auth_source=environ.get("MONGO_AUTH_SOURCE", "admin"),
        )

        return cls(
            postgres=postgres,
            mongodb=mongodb,
        )
