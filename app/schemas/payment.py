from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentRead(BaseModel):
    payment_id: int
    sale_id: int
    payment_method: str
    amount_paid: Decimal
    payment_status: str
    payer_phone: str | None = None
    provider_status: str | None = None
    status_message: str | None = None
    payment_date: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentStatusResponse(BaseModel):
    sale_id: int
    payment_id: int
    sale_status: str
    payment_status: str
    total_amount: Decimal
    receipt_id: int | None = None
    message: str
