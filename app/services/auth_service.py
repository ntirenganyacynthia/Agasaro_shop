from datetime import datetime, timedelta, timezone
import base64
import io

from fastapi import HTTPException, status
import jwt
import pyotp
import qrcode
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decrypt_mfa_secret,
    encrypt_mfa_secret,
    verify_password,
)
from app.models.user import User
from app.repositories.user import user_repository


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _auth_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _check_login_lock(user: User) -> None:
    if user.locked_until and user.locked_until > _now():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked after repeated failed logins.",
        )


def authenticate_user(db: Session, username: str, password: str) -> User:
    user = user_repository.get_by_username(db, username.strip())
    if user is None:
        raise _auth_error()

    _check_login_lock(user)
    if not verify_password(password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.login_max_failed_attempts:
            user.locked_until = _now() + timedelta(minutes=settings.login_lockout_minutes)
            user.failed_login_attempts = 0
        db.commit()
        raise _auth_error()

    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    return user


def login(db: Session, username: str, password: str):
    user = authenticate_user(db, username, password)
    if user.mfa_enabled:
        return {"mfa_required": True}
    return {
        "mfa_required": False,
        "access_token": create_access_token(user.user_id),
        "token_type": "bearer",
    }


def setup_mfa(db: Session, user: User):
    if user.mfa_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is already enabled.")
    secret = pyotp.random_base32()
    user.mfa_secret = encrypt_mfa_secret(secret)
    db.commit()
    db.refresh(user)
    provisioning_uri = pyotp.TOTP(secret).provisioning_uri(
        name=user.username,
        issuer_name=settings.mfa_issuer_name,
    )
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    buffer = io.BytesIO()
    qr.make_image().save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return {
        "message": "MFA setup initialized. Verify one code to enable it.",
        "qr_code": f"data:image/png;base64,{qr_base64}",
    }


def verify_mfa(db: Session, user: User, code: str):
    now = _now()
    if user.mfa_locked_until and user.mfa_locked_until > now:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="MFA temporarily locked after repeated failed codes.",
        )
    if not user.mfa_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA has not been configured.")
    try:
        secret = decrypt_mfa_secret(user.mfa_secret)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="MFA configuration is unavailable.") from exc
    if not pyotp.TOTP(secret).verify(code, valid_window=1):
        user.failed_mfa_attempts += 1
        if user.failed_mfa_attempts >= settings.mfa_max_failed_attempts:
            user.mfa_locked_until = now + timedelta(minutes=settings.mfa_lockout_minutes)
            user.failed_mfa_attempts = 0
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code.")

    user.failed_mfa_attempts = 0
    user.mfa_locked_until = None
    user.mfa_enabled = True
    db.commit()
    return create_access_token(user.user_id)


def verify_token(db: Session, token: str):
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "access":
            raise InvalidTokenError("wrong token type")
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, TypeError, ValueError, OverflowError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
