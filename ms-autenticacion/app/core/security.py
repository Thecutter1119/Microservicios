import base64
from datetime import datetime, timezone

import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")


def decrypt_aes_base64(cipher_b64: str) -> str:
    raw = base64.b64decode(cipher_b64)
    key = base64.b64decode(settings.AES_SECRET_KEY_BASE64)
    nonce = raw[:12]
    ciphertext = raw[12:]
    return AESGCM(key).decrypt(nonce, ciphertext, None).decode("utf-8")


def encrypt_aes_base64(plain: str) -> str:
    key = base64.b64decode(settings.AES_SECRET_KEY_BASE64)
    aesgcm = AESGCM(key)
    nonce = b"0123456789ab"
    encrypted = aesgcm.encrypt(nonce, plain.encode("utf-8"), None)
    return base64.b64encode(nonce + encrypted).decode("utf-8")


def verify_password(raw_password: str, password_hash: str) -> bool:
    return pwd_context.verify(raw_password, password_hash)


def build_jwt(usuario_id: int, roles: list[str], permisos: list[str]) -> str:
    payload = {
        "sub": str(usuario_id),
        "roles": roles,
        "permisos": permisos,
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
