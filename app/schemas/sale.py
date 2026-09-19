from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SaleRead(BaseModel):
    sale_id: int
    customer_id: int
    user_id: int | None = None
    total_amount: Decimal
    sale_status: str
    sale_date: datetime
    model_config = ConfigDict(from_attributes=True)
