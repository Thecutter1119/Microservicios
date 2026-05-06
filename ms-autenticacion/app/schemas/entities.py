from pydantic import BaseModel


class LoginIn(BaseModel):
    login: str
    password: str | None = None
    password_encrypted: str | None = None


class LogoutIn(BaseModel):
    token: str


class ValidateSessionIn(BaseModel):
    token: str


class AppTokenIn(BaseModel):
    service_name: str
    token_plain: str
    descripcion: str | None = None
    updated_by: int | None = None
