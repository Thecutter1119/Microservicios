from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ms-roles"
    SERVICE_CODE: str = "ROL"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_roles"
    CONTRADICTORY_ROLE_PAIRS: str = "DOCENTE:ESTUDIANTE"
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


settings = Settings()
