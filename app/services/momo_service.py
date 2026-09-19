"""MTN MoMo Collection client used by the checkout service.

Request to Pay is asynchronous. A successful HTTP 202 only means that the
request was accepted by MoMo; the sale remains pending until a later status
check or verified callback reports SUCCESSFUL.
"""

from dataclasses import dataclass
from decimal import Decimal
import uuid

import requests

from app.core.config import settings
from app.infrastructure.runtime_config import momo_is_configured


@dataclass
class MomoProviderError(Exception):
    message: str
    uncertain: bool = False
    provider_status: str | None = None


class MomoClient:
    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()
        self.timeout = settings.momo_timeout_seconds

    def _ensure_configured(self) -> None:
        if not momo_is_configured(settings):
            raise MomoProviderError(
                "Mobile money is not configured. Add MTN MoMo credentials before accepting mobile-money payments.",
                uncertain=False,
            )

    def get_access_token(self) -> str:
        self._ensure_configured()
        url = f"{settings.momo_base_url.rstrip('/')}/collection/token/"
        headers = {"Ocp-Apim-Subscription-Key": settings.momo_subscription_key.get_secret_value()}
        try:
            response = self.session.post(
                url,
                headers=headers,
                auth=(settings.momo_api_user.get_secret_value(), settings.momo_api_key.get_secret_value()),
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise MomoProviderError("Unable to reach the mobile-money provider.", uncertain=True) from exc
        if response.status_code != 200:
            raise MomoProviderError("The mobile-money provider rejected authentication.", provider_status=str(response.status_code))
        token = response.json().get("access_token")
        if not token:
            raise MomoProviderError("The mobile-money provider returned an invalid access token.", uncertain=True)
        return token

    def request_to_pay(self, amount: Decimal, phone_number: str, sale_id: int) -> str:
        token = self.get_access_token()
        reference_id = str(uuid.uuid4())
        url = f"{settings.momo_base_url.rstrip('/')}/collection/v1_0/requesttopay"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": settings.momo_target_environment,
            "Ocp-Apim-Subscription-Key": settings.momo_subscription_key.get_secret_value(),
            "Content-Type": "application/json",
        }
        body = {
            "amount": str(amount.quantize(Decimal("0.01"))),
            "currency": settings.momo_currency,
            "externalId": f"POS-{sale_id}",
            "payer": {"partyIdType": "MSISDN", "partyId": phone_number},
            "payerMessage": f"POS purchase #{sale_id}",
            "payeeNote": f"POS sale #{sale_id}",
        }
        try:
            response = self.session.post(url, json=body, headers=headers, timeout=self.timeout)
        except requests.RequestException as exc:
            raise MomoProviderError("Payment request status is uncertain; do not retry immediately.", uncertain=True) from exc
        if response.status_code == 202:
            return reference_id
        if response.status_code in {408, 409, 429} or response.status_code >= 500:
            raise MomoProviderError("Payment request status is uncertain; check the payment status before retrying.", uncertain=True, provider_status=str(response.status_code))
        raise MomoProviderError("The mobile-money payment request was rejected.", uncertain=False, provider_status=str(response.status_code))

    def check_payment_status(self, reference_id: str) -> dict:
        token = self.get_access_token()
        url = f"{settings.momo_base_url.rstrip('/')}/collection/v1_0/requesttopay/{reference_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Target-Environment": settings.momo_target_environment,
            "Ocp-Apim-Subscription-Key": settings.momo_subscription_key.get_secret_value(),
        }
        try:
            response = self.session.get(url, headers=headers, timeout=self.timeout)
        except requests.RequestException as exc:
            raise MomoProviderError("Payment status is temporarily unavailable.", uncertain=True) from exc
        if response.status_code != 200:
            raise MomoProviderError("Payment status could not be verified.", uncertain=True, provider_status=str(response.status_code))
        return response.json()


_default_client = MomoClient()


def get_momo_client() -> MomoClient:
    return _default_client


# Compatibility wrappers for existing callers.
def get_access_token():
    return _default_client.get_access_token()


def request_to_pay(amount, phone_number, payer_message="", payee_note=""):
    from app.services.phone import normalize_rwanda_phone
    return _default_client.request_to_pay(Decimal(str(amount)), normalize_rwanda_phone(phone_number), 0)


def check_payment_status(reference_id):
    return _default_client.check_payment_status(reference_id)
