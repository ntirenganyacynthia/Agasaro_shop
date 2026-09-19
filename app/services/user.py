from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.repositories.user import user_repository


def register(db: Session, user):
    existing_user = user_repository.get_by_username(
        db,
        user.username
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists."
        )

    data = {
        "username": user.username,
        "hashed_password": hash_password(user.password),
        "role": "cashier",
    }

    return user_repository.create(
        db,
        data
    )


def get_all_users(db: Session):
    return user_repository.get_all(db)


def get_user(db: Session, user_id: int):
    user = user_repository.get_by_id(
        db,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return user


def create_user(db: Session, user):
    data = {
        "username": user.username,
        "hashed_password": hash_password(user.password),
        "role": "cashier",
    }

    return user_repository.create(
        db,
        data
    )


def update_user(db: Session, user_id: int, user):
    db_user = get_user(
        db,
        user_id
    )

    data = user.model_dump(
        exclude_unset=True
    )

    if "password" in data:
        data["hashed_password"] = hash_password(
            data.pop("password")
        )

    return user_repository.update(
        db,
        db_user,
        data
    )


def delete_user(db: Session, user_id: int):
    db_user = get_user(
        db,
        user_id
    )

    user_repository.delete(
        db,
        db_user
    )