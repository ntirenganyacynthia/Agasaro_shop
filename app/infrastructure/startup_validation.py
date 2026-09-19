from app.core.config import settings


def validate_startup_configuration() -> None:

    if settings.app_env.lower() in {"production", "prod"}:

        if len(settings.secret_key.get_secret_value()) < 32:
            raise RuntimeError("SECRET_KEY must be a strong, unique value in production.")
        if not settings.mfa_encryption_key or not settings.mfa_encryption_key.get_secret_value():
            raise RuntimeError("MFA_ENCRYPTION_KEY must be configured in production.")
