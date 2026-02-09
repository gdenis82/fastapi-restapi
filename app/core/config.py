from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_key: str = None
    database_url: str = None

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, value: str) -> str:
        if not value:
            raise ValueError("DATABASE_URL is required")
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql+asyncpg://"):
            return value
        raise ValueError("DATABASE_URL must use postgresql or postgresql+asyncpg scheme")


settings = Settings()
