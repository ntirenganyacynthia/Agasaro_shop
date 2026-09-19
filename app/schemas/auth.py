from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100
    )

    password: str = Field(
        min_length=8,
        max_length=128
    )


class MFAVerifyRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100
    )

    password: str = Field(
        min_length=8,
        max_length=128
    )

    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$"
    )