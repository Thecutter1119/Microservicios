from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ms-reservas"
    SERVICE_CODE: str = "RES"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_reservas"
    ESP_BASE_URL: str = "http://localhost:8005"
    HOR_BASE_URL: str = "http://localhost:8016"
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


settings = Settings()
