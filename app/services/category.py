from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.category import category_repository


def get_all_categories(db: Session):

    return category_repository.get_all(db)


def get_category(db: Session, category_id: int):

    db_category = category_repository.get_by_id(
        db,
        category_id
    )

    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    return db_category


def create_category(db: Session, category):

    return category_repository.create(
        db,
        category.model_dump()
    )


def update_category(
    db: Session,
    category_id: int,
    category
):

    db_category = get_category(
        db,
        category_id
    )

    return category_repository.update(
        db,
        db_category,
        category.model_dump(exclude_unset=True)
    )


def delete_category(
    db: Session,
    category_id: int
):

    db_category = get_category(
        db,
        category_id
    )

    category_repository.delete(
        db,
        db_category
    )