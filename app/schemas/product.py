from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    category_id: int
    supplier_id: int
    product_name: str = Field(min_length=1, max_length=100)
    unit_price: Decimal = Field(gt=0)
    cost_price: Decimal = Field(gt=0)
    stock_quantity: Decimal = Field(ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    category_id: int | None = None
    supplier_id: int | None = None
    product_name: str | None = Field(default=None, min_length=1, max_length=100)
    unit_price: Decimal | None = Field(default=None, gt=0)
    cost_price: Decimal | None = Field(default=None, gt=0)
    stock_quantity: Decimal | None = Field(default=None, ge=0)


class ProductPublicRead(BaseModel):
    product_id: int
    category_id: int
    supplier_id: int
    product_name: str
    unit_price: Decimal
    stock_quantity: Decimal
    reserved_quantity: Decimal
    available_quantity: Decimal
    model_config = ConfigDict(from_attributes=True)


class ProductAdminRead(ProductPublicRead):
    cost_price: Decimal
