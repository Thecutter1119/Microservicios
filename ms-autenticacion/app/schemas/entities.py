from pydantic import BaseModel


class LoginIn(BaseModel):
    login: str
    password_encrypted: str


class LogoutIn(BaseModel):
    token: str


class ValidateSessionIn(BaseModel):
    token: str


class AppTokenIn(BaseModel):
    service_name: str
    token_plain: str
    descripcion: str | None = None
    updated_by: int | None = None
