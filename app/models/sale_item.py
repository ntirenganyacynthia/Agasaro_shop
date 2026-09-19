from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class SaleItem(Base):
    __tablename__ = "sale_items"

    sale_item_id = Column(Integer, primary_key=True, index=True)

    sale_id = Column(
        Integer,
        ForeignKey("sales.sale_id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.product_id"),
        nullable=False
    )

    quantity = Column(
        Numeric(10, 2),
        nullable=False
    )

    unit_price = Column(
        Numeric(10, 2),
        nullable=False
    )

    sub_total = Column(
        Numeric(10, 2),
        nullable=False
    )

    sale = relationship(
        "Sale",
        back_populates="sale_items"
    )

    product = relationship(
        "Product",
        back_populates="sale_items"
    )