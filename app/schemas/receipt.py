from datetime import datetime

from pydantic import BaseModel


class ReceiptBase(BaseModel):

    sale_id: int
    receipt_number: str


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptUpdate(BaseModel):

    sale_id: int | None = None
    receipt_number: str | None = None


class ReceiptRead(ReceiptBase):

    receipt_id: int
    issued_at: datetime

    class Config:
        from_attributes = True