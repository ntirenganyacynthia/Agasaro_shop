from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.product import product_repository

from app.models.category import Category
from app.models.supplier import Supplier


def get_all_products(db: Session):
    return product_repository.get_all(db)


def get_product(db: Session, product_id: int):

    product = product_repository.get_by_id(
        db,
        product_id
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

    return product


def validate_product_values(product):

    if hasattr(product, "unit_price") and product.unit_price is not None:
        if product.unit_price <= Decimal("0"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unit price must be greater than zero."
            )

    if hasattr(product, "cost_price") and product.cost_price is not None:
        if product.cost_price <= Decimal("0"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cost price must be greater than zero."
            )

    if hasattr(product, "stock_quantity") and product.stock_quantity is not None:
        if product.stock_quantity < Decimal("0"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock quantity cannot be negative."
            )

    if hasattr(product, "product_name") and product.product_name is not None:
        if not product.product_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product name cannot be empty."
            )


def create_product(db: Session, product):

    validate_product_values(product)

    category = db.query(Category).filter(
        Category.category_id == product.category_id
    ).first()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    supplier = db.query(Supplier).filter(
        Supplier.supplier_id == product.supplier_id
    ).first()

    if supplier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found."
        )

    return product_repository.create(
        db,
        product.model_dump()
    )


def update_product(
    db: Session,
    product_id: int,
    product
):

    db_product = get_product(
        db,
        product_id
    )

    validate_product_values(product)

    update_data = product.model_dump(
        exclude_unset=True
    )

    if "stock_quantity" in update_data and update_data["stock_quantity"] < db_product.reserved_quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stock quantity cannot be lower than stock reserved for pending payments."
        )

    if "category_id" in update_data:

        category = db.query(Category).filter(
            Category.category_id == update_data["category_id"]
        ).first()

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )

    if "supplier_id" in update_data:

        supplier = db.query(Supplier).filter(
            Supplier.supplier_id == update_data["supplier_id"]
        ).first()

        if supplier is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found."
            )

    return product_repository.update(
        db,
        db_product,
        update_data
    )


def delete_product(
    db: Session,
    product_id: int
):

    db_product = get_product(
        db,
        product_id
    )

    product_repository.delete(
        db,
        db_product
    )
