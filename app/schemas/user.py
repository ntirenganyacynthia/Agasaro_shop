from pydantic import BaseModel, Field, field_validator


ALLOWED_ROLES = {"admin", "cashier"}


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100
    )

    password: str = Field(
        min_length=8,
        max_length=128
    )


class UserUpdate(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=100
    )

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128
    )

    role: str | None = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        if value is not None and value not in ALLOWED_ROLES:
            raise ValueError(
                "Role must be either 'admin' or 'cashier'."
            )
        return value


class UserRead(BaseModel):
    user_id: int
    username: str
    role: str
    mfa_enabled: bool

    class Config:
        from_attributes = True