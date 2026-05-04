from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ms-usuarios"
    SERVICE_CODE: str = "USR"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_usuarios"
    ROL_BASE_URL: str = "http://localhost:8002"
    AES_SECRET_KEY_BASE64: str = "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo0NDQ0NDU1NTY2NjY="
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


settings = Settings()
