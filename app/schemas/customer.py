from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class CustomerBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    customer_email: EmailStr | None = None
    customer_phonenumber: str | None = Field(default=None, min_length=9, max_length=20)

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("full_name cannot be blank")
        return value

    @field_validator("customer_phonenumber")
    @classmethod
    def clean_phone(cls, value: str | None) -> str | None:
        return value.strip() if value else None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    customer_email: EmailStr | None = None
    customer_phonenumber: str | None = Field(default=None, min_length=9, max_length=20)

    model_config = ConfigDict(extra="forbid")


class CustomerRead(CustomerBase):
    customer_id: int
    model_config = ConfigDict(from_attributes=True)
