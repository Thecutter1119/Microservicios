from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ms-domicilios"
    app_env: str = "dev"
    app_port: int = 8000
    database_url: str = "postgresql+psycopg://postgres:CHANGE_ME@localhost:5432/ms_domicilios"
    ped_mock_enabled: bool = True
    ped_base_url: str = "http://localhost:8010"
    ped_timeout_seconds: float = 3.0
    ped_app_token: str = "default-dom-token"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
