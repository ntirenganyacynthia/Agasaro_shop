from app.core.config import Settings


def cors_origin_list(settings: Settings) -> list[str]:
    return [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]


def momo_is_configured(settings: Settings) -> bool:
    credentials = (
        settings.momo_subscription_key,
        settings.momo_api_user,
        settings.momo_api_key,
    )
    return all(
        credential is not None
        and bool(credential.get_secret_value())
        and not credential.get_secret_value().startswith("PUT_YOUR_")
        for credential in credentials
    )
