from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(100),
        unique=True,
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        nullable=False
    )

    mfa_enabled = Column(
        Boolean,
        nullable=False,
        default=False
    )

    mfa_secret = Column(
        String(500),
        nullable=True
    )

    failed_login_attempts = Column(Integer, nullable=False, default=0, server_default="0")
    locked_until = Column(DateTime(timezone=True), nullable=True)
    failed_mfa_attempts = Column(Integer, nullable=False, default=0, server_default="0")
    mfa_locked_until = Column(DateTime(timezone=True), nullable=True)

    sales = relationship(
        "Sale",
        back_populates="user"
    )
