from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ms-inventario"
    SERVICE_CODE: str = "INV"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_inventario"

    AUTH_BASE_URL: str = "http://localhost:8001"
    ROL_BASE_URL: str = "http://localhost:8002"
    AUD_BASE_URL: str = "http://localhost:8018"
    APP_TOKEN: str = "replace-me-token-inv"

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


settings = Settings()
