from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ms-presupuesto"
    SERVICE_CODE: str = "PRE"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_presupuesto"
    ALERTA_DEFAULT_PERCENT: int = 80
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


settings = Settings()
