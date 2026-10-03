import os
from pathlib import Path
import uuid
import requests


BASE_URL = os.getenv(
    "MTN_MOMO_BASE_URL",
    "https://sandbox.momodeveloper.mtn.com",
).rstrip("/")

SUBSCRIPTION_KEY = os.getenv("MTN_MOMO_SUBSCRIPTION_KEY")
CALLBACK_HOST = os.getenv("MOMO_PROVIDER_CALLBACK_HOST")
ENV_FILE_PATH = Path(os.getenv("POS_ENV_FILE", ".env"))
TIMEOUT = float(os.getenv("MTN_MOMO_TIMEOUT_SECONDS", "15"))


def required_config() -> None:
    if not SUBSCRIPTION_KEY:
        raise RuntimeError(
            "MTN_MOMO_SUBSCRIPTION_KEY is not set."
        )

    if not CALLBACK_HOST:
        raise RuntimeError(
            "MOMO_PROVIDER_CALLBACK_HOST is not set."
        )

    print("Configuration:")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Subscription key set: {bool(SUBSCRIPTION_KEY)}")
    print(f"  Subscription key length: {len(SUBSCRIPTION_KEY)}")
    print(f"  Callback host: {CALLBACK_HOST}")
    print()


def create_api_user(reference_id: str) -> None:
    url = f"{BASE_URL}/v1_0/apiuser"

    headers = {
        "X-Reference-Id": reference_id,
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "providerCallbackHost": CALLBACK_HOST,
    }

    print("Creating sandbox API user...")
    print(f"  URL: {url}")
    print(f"  Reference ID: {reference_id}")

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not connect to MTN MoMo: {exc}"
        ) from exc

    print(f"  HTTP status: {response.status_code}")

    if response.status_code != 201:
        print("  MTN response:")
        print(response.text)

        raise RuntimeError(
            f"MoMo API user creation failed with HTTP "
            f"{response.status_code}."
        )

    print("API user created successfully.")
    print()


def create_api_key(reference_id: str) -> str:
    url = f"{BASE_URL}/v1_0/apiuser/{reference_id}/apikey"

    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
    }

    print("Creating sandbox API key...")
    print(f"  URL: {url}")

    try:
        response = requests.post(
            url,
            headers=headers,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not connect to MTN MoMo: {exc}"
        ) from exc

    print(f"  HTTP status: {response.status_code}")

    if response.status_code != 201:
        print("  MTN response:")
        print(response.text)

        raise RuntimeError(
            f"MoMo API key creation failed with HTTP "
            f"{response.status_code}."
        )

    try:
        data = response.json()
    except ValueError as exc:
        print("  MTN returned:")
        print(response.text)
        raise RuntimeError(
            "MTN returned a response that was not valid JSON."
        ) from exc

    api_key = data.get("apiKey")

    if not api_key:
        raise RuntimeError(
            "MoMo returned no API key."
        )

    print("API key created successfully.")
    print()

    return api_key


def update_env_file(api_user: str, api_key: str) -> None:
    values = {
        "MTN_MOMO_BASE_URL": BASE_URL,
        "MTN_MOMO_API_USER": api_user,
        "MTN_MOMO_API_KEY": api_key,
        "MTN_MOMO_TARGET_ENVIRONMENT": os.getenv(
            "MTN_MOMO_TARGET_ENVIRONMENT",
            "sandbox",
        ),
        "MTN_MOMO_CURRENCY": os.getenv(
            "MTN_MOMO_CURRENCY",
            "RWF",
        ),
        "MTN_MOMO_SUBSCRIPTION_KEY": SUBSCRIPTION_KEY,
    }

    existing = (
        ENV_FILE_PATH.read_text()
        if ENV_FILE_PATH.exists()
        else ""
    )

    kept = [
        line
        for line in existing.splitlines()
        if not any(
            line.startswith(f"{key}=")
            for key in values
        )
    ]

    new_content = "\n".join(
        [
            *kept,
            *[
                f"{key}={value}"
                for key, value in values.items()
            ],
        ]
    ) + "\n"

    ENV_FILE_PATH.write_text(new_content)

    print(f"Updated {ENV_FILE_PATH}")
    print("API credentials were written to the environment file.")
    print()


def main() -> None:
    required_config()

    reference_id = str(uuid.uuid4())

    create_api_user(reference_id)

    api_key = create_api_key(reference_id)

    update_env_file(
        reference_id,
        api_key,
    )

    print("========================================")
    print("MoMo sandbox provisioning successful!")
    print("========================================")
    print()
    print("API User was generated.")
    print("API Key was generated.")
    print(f"Credentials saved to: {ENV_FILE_PATH}")
    print()
    print("Keep your .env file private.")


if __name__ == "__main__":
    main()