from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ms-espacios"
    SERVICE_CODE: str = "ESP"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_espacios"
    INV_BASE_URL: str = "http://localhost:8004"
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


settings = Settings()
