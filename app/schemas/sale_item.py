from decimal import Decimal

from pydantic import BaseModel


class SaleItemBase(BaseModel):

    sale_id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    sub_total: Decimal


class SaleItemCreate(SaleItemBase):
    pass


class SaleItemUpdate(BaseModel):

    sale_id: int | None = None
    product_id: int | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    sub_total: Decimal | None = None


class SaleItemRead(SaleItemBase):

    sale_item_id: int

    class Config:
        from_attributes = True