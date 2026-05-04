from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ms-auditoria"
    SERVICE_CODE: str = "AUD"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_auditoria"
    DEFAULT_RETENTION_DAYS: int = 30
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


settings = Settings()
