


import os
from pathlib import Path
import uuid

import requests


BASE_URL = os.getenv("MTN_MOMO_BASE_URL", "https://sandbox.momodeveloper.mtn.com").rstrip("/")

SUBSCRIPTION_KEY = os.getenv("MTN_MOMO_SUBSCRIPTION_KEY")
CALLBACK_HOST = os.getenv("MOMO_PROVIDER_CALLBACK_HOST")
ENV_FILE_PATH = Path(os.getenv("POS_ENV_FILE", ".env"))
TIMEOUT = float(os.getenv("MTN_MOMO_TIMEOUT_SECONDS", "15"))


def required_config() -> None:
    if not SUBSCRIPTION_KEY:
        raise RuntimeError("Set MTN_MOMO_SUBSCRIPTION_KEY before provisioning.")
    if not CALLBACK_HOST:
        raise RuntimeError("Set MOMO_PROVIDER_CALLBACK_HOST to a real HTTPS callback host before provisioning.")


def create_api_user(reference_id: str) -> None:
    response = requests.post(
        f"{BASE_URL}/v1_0/apiuser",
        json={"providerCallbackHost": CALLBACK_HOST},
        headers={"X-Reference-Id": reference_id, "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY, "Content-Type": "application/json"},
        timeout=TIMEOUT,
    )
    if response.status_code != 201:
        raise RuntimeError(f"MoMo API user creation failed with HTTP {response.status_code}.")


def create_api_key(reference_id: str) -> str:
    response = requests.post(
        f"{BASE_URL}/v1_0/apiuser/{reference_id}/apikey",
        headers={"Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY},
        timeout=TIMEOUT,
    )
    if response.status_code != 201:
        raise RuntimeError(f"MoMo API key creation failed with HTTP {response.status_code}.")
    api_key = response.json().get("apiKey")
    if not api_key:
        raise RuntimeError("MoMo returned no API key.")
    return api_key


def update_env_file(api_user: str, api_key: str) -> None:
    values = {
        "MTN_MOMO_BASE_URL": BASE_URL,
        "MTN_MOMO_API_USER": api_user,
        "MTN_MOMO_API_KEY": api_key,
        "MTN_MOMO_TARGET_ENVIRONMENT": os.getenv("MTN_MOMO_TARGET_ENVIRONMENT", "sandbox"),
        "MTN_MOMO_CURRENCY": os.getenv("MTN_MOMO_CURRENCY", "RWF"),
        "MTN_MOMO_SUBSCRIPTION_KEY": SUBSCRIPTION_KEY,
    }
    existing = ENV_FILE_PATH.read_text() if ENV_FILE_PATH.exists() else ""

    kept = [line for line in existing.splitlines() if not any(line.startswith(f"{key}=") for key in values)]
    ENV_FILE_PATH.write_text("\n".join([*kept, *[f"{key}={value}" for key, value in values.items()]]) + "\n")


def main() -> None:
    required_config()
    reference_id = str(uuid.uuid4())
    create_api_user(reference_id)
    api_key = create_api_key(reference_id)
    update_env_file(reference_id, api_key)
    print(f"Provisioned MoMo API user and updated {ENV_FILE_PATH}. Keep that file private.")


if __name__ == "__main__":
    main()
