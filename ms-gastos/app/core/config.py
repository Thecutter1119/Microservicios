from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ms-gastos"
    SERVICE_CODE: str = "GAS"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_gastos"
    PRE_BASE_URL: str = "http://localhost:8007"
    NOVEDAD_ESCALACION_UMBRAL: float = 1000000
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


settings = Settings()
