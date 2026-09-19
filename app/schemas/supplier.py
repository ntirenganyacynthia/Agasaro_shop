from pydantic import BaseModel


class SupplierBase(BaseModel):
    supplier_name: str
    email: str | None = None
    phone_number: str | None = None
    address: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    supplier_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    address: str | None = None


class SupplierRead(SupplierBase):
    supplier_id: int

    class Config:
        from_attributes = True