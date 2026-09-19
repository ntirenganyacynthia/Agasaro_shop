from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.customer import customer_repository


def get_all_customers(db: Session):
    return customer_repository.get_all(db)


def get_customer(db: Session, customer_id: int):

    customer = customer_repository.get_by_id(
        db,
        customer_id
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found."
        )

    return customer


def create_customer(db: Session, customer):

    return customer_repository.create(
        db,
        customer.model_dump()
    )


def update_customer(
    db: Session,
    customer_id: int,
    customer
):

    db_customer = get_customer(
        db,
        customer_id
    )

    return customer_repository.update(
        db,
        db_customer,
        customer.model_dump(exclude_unset=True)
    )


def delete_customer(
    db: Session,
    customer_id: int
):

    db_customer = get_customer(
        db,
        customer_id
    )

    customer_repository.delete(
        db,
        db_customer
    )