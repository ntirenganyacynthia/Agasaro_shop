from datetime import datetime, timedelta, timezone
import secrets

import jwt
from cryptography.fernet import Fernet, InvalidToken as InvalidFernetToken
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expire,
        "jti": secrets.token_urlsafe(16),
        "type": "access",
    }
    return jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[settings.jwt_algorithm])


def encrypt_mfa_secret(secret: str) -> str:
    if settings.mfa_encryption_key is None:
        raise RuntimeError("MFA_ENCRYPTION_KEY is not configured.")
    return Fernet(settings.mfa_encryption_key.get_secret_value().encode()).encrypt(secret.encode()).decode()


def decrypt_mfa_secret(encrypted_secret: str) -> str:
    if settings.mfa_encryption_key is None:
        raise RuntimeError("MFA_ENCRYPTION_KEY is not configured.")
    try:
        return Fernet(settings.mfa_encryption_key.get_secret_value().encode()).decrypt(encrypted_secret.encode()).decode()
    except (InvalidFernetToken, ValueError) as exc:
        raise RuntimeError("Stored MFA secret cannot be decrypted.") from exc
