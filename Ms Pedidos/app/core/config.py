from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ms-pedidos"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/db_pedidos"
    
    AUTH_BASE_URL: str = "http://ms-autenticacion"
    ROL_BASE_URL: str = "http://ms-roles"
    PRV_BASE_URL: str = "http://ms-proveedores"
    INV_BASE_URL: str = "http://ms-inventario"
    AUD_BASE_URL: str = "http://ms-auditoria"
    
    PED_APP_TOKEN: str = "default-ped-token"
    DOM_APP_TOKEN: str = "default-dom-token"

    SECURITY_MOCK_ENABLED: bool = False
    EXTERNAL_SERVICES_MOCK_ENABLED: bool = False
    
    HTTP_TIMEOUT_SECONDS: int = 5
    
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()
