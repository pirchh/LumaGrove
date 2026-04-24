from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="LumaGrove API", validation_alias=AliasChoices("APP_NAME", "app_name"))
    environment: str = Field(default="development", validation_alias=AliasChoices("ENVIRONMENT", "APP_ENV", "environment"))
    app_host: str = Field(default="127.0.0.1", validation_alias=AliasChoices("APP_HOST", "app_host"))
    app_port: int = Field(default=8003, validation_alias=AliasChoices("APP_PORT", "app_port"))
    log_level: str = Field(default="INFO", validation_alias=AliasChoices("LOG_LEVEL", "log_level"))
    debug: bool = Field(default=True, validation_alias=AliasChoices("DEBUG", "debug"))

    postgres_user: str = Field(default="postgres", validation_alias=AliasChoices("POSTGRES_USER", "postgres_user"))
    postgres_password: str = Field(default="", validation_alias=AliasChoices("POSTGRES_PASSWORD", "postgres_password"))
    postgres_db: str = Field(default="lumagrove", validation_alias=AliasChoices("POSTGRES_DB", "postgres_db"))
    postgres_host: str = Field(default="127.0.0.1", validation_alias=AliasChoices("POSTGRES_HOST", "POSTGRES_SERVER", "postgres_host"))
    postgres_port: int = Field(default=5432, validation_alias=AliasChoices("POSTGRES_PORT", "postgres_port"))
    database_url_override: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
    )

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override

        auth = self.postgres_user
        if self.postgres_password:
            auth = f"{auth}:{self.postgres_password}"

        return (
            f"postgresql+psycopg://{auth}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
