import logging
from functools import lru_cache

from fastapi import Depends
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("app.settings")



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )

    API_KEY: str | None = Field(default=None, validation_alias="API_KEY")
    DATABASE_URL: str | None = Field(default=None, validation_alias="DATABASE_URL")
    ENVIRONMENT: str = Field(default="development", validation_alias="ENVIRONMENT")

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, value: str) -> str:
        if not value:
            raise ValueError("DATABASE_URL is required")
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql+asyncpg://"):
            return value
        raise ValueError("DATABASE_URL must use postgresql+asyncpg scheme")


class SettingsBuilder:
    @staticmethod
    @lru_cache(maxsize=1)
    def build() -> "Settings":
        try:
            instance = Settings()
        except Exception as exc:
            logger.error("Error loading settings: %s", type(exc).__name__)
            raise
        return instance


def get_settings() -> "Settings":
    return SettingsBuilder.build()


settings_dep = Depends(get_settings)
settings = get_settings()
