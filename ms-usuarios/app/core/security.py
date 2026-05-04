import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")


def hash_password(raw_password: str) -> str:
    return pwd_context.hash(raw_password)


def verify_password(raw_password: str, password_hash: str) -> bool:
    return pwd_context.verify(raw_password, password_hash)


def decrypt_aes_base64(cipher_b64: str) -> str:
    raw = base64.b64decode(cipher_b64)
    if len(raw) < 28:
        raise ValueError("Ciphertext invalido")
    key = base64.b64decode(settings.AES_SECRET_KEY_BASE64)
    nonce = raw[:12]
    ciphertext = raw[12:]
    aesgcm = AESGCM(key)
    plain = aesgcm.decrypt(nonce, ciphertext, None)
    return plain.decode("utf-8")
