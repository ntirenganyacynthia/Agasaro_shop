from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator


PaymentMethod = Literal["mobile_money", "cash", "card"]


class CheckoutItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class CheckoutCreate(BaseModel):
    customer_id: int | None = Field(default=None, gt=0)
    customer_name: str = Field(default="Walk-in customer", min_length=1, max_length=100)
    items: list[CheckoutItem] = Field(min_length=1, max_length=100)
    payment_method: PaymentMethod = "mobile_money"
    phone_number: str | None = Field(default=None, min_length=9, max_length=20)
    idempotency_key: str = Field(min_length=16, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$")

    @field_validator("phone_number")
    @classmethod
    def clean_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("phone_number cannot be blank")
        return cleaned

    @field_validator("customer_name")
    @classmethod
    def clean_customer_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("customer name cannot be blank")
        return value


class CheckoutResponse(BaseModel):
    sale_id: int
    total_amount: Decimal
    payment_id: int
    payment_status: str
    sale_status: str
    receipt_id: int | None = None
    status_token: str
    status_url: str
    message: str
    payer_phone_masked: str | None = None


class PaymentStatusResponse(BaseModel):
    sale_id: int
    payment_id: int
    sale_status: str
    payment_status: str
    total_amount: Decimal
    receipt_id: int | None = None
    message: str
