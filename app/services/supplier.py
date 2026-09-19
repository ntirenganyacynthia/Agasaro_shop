from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.supplier import supplier_repository


def get_all_suppliers(db: Session):
    return supplier_repository.get_all(db)


def get_supplier(db: Session, supplier_id: int):

    supplier = supplier_repository.get_by_id(
        db,
        supplier_id
    )

    if supplier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found."
        )

    return supplier


def create_supplier(db: Session, supplier):

    return supplier_repository.create(
        db,
        supplier.model_dump()
    )


def update_supplier(db: Session, supplier_id: int, supplier):

    db_supplier = get_supplier(
        db,
        supplier_id
    )

    return supplier_repository.update(
        db,
        db_supplier,
        supplier.model_dump(exclude_unset=True)
    )


def delete_supplier(db: Session, supplier_id: int):

    db_supplier = get_supplier(
        db,
        supplier_id
    )

    supplier_repository.delete(
        db,
        db_supplier
    )