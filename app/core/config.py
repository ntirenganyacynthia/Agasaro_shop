from functools import lru_cache

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    
    database_url: SecretStr
    secret_key: SecretStr = Field(
        validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET_KEY")
    )

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1440)
    app_env: str = Field(
        default="development",
        validation_alias=AliasChoices("APP_ENV", "ENVIRONMENT")
    )
    debug: bool = False
    backend_url: str = "http://127.0.0.1:8000"

    mfa_encryption_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("MFA_ENCRYPTION_KEY", "PHONE_ENCRYPTION_KEY")
    )

    mfa_issuer_name: str = "Agasaro POS"
    mfa_max_failed_attempts: int = Field(default=5, ge=1, le=20)
    mfa_lockout_minutes: int = Field(default=15, ge=1, le=1440)
    login_max_failed_attempts: int = Field(default=5, ge=1, le=20)
    login_lockout_minutes: int = Field(default=15, ge=1, le=1440)

  
    rate_limit_login: str = "5/minute"
    rate_limit_otp_verify: str = "8/minute"

    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    allow_all_cors: bool = False


    momo_base_url: str = "https://sandbox.momodeveloper.mtn.com"
    momo_subscription_key: SecretStr | None = None
    momo_api_user: SecretStr | None = None
    momo_api_key: SecretStr | None = None
    momo_target_environment: str = "sandbox"
    momo_currency: str = "RWF"
    momo_callback_secret: SecretStr | None = None
    momo_timeout_seconds: float = Field(default=15.0, gt=0, le=60)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

__all__ = ["Settings", "settings", "get_settings"]
