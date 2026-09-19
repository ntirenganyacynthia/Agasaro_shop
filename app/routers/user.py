from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.user import (
    UserCreate,
    UserRead,
    UserUpdate
)

from app.services.user import (
    get_all_users,
    get_user,
    register,
    update_user,
    delete_user
)

from app.dependences import require_role


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/",
    response_model=list[UserRead]
)
def read_users(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    return get_all_users(db)


@router.get(
    "/{user_id}",
    response_model=UserRead
)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    return get_user(db, user_id)


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)
def add_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    return register(db, user)


@router.put(
    "/{user_id}",
    response_model=UserRead
)
def edit_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    return update_user(
        db,
        user_id,
        user
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    delete_user(
        db,
        user_id
    )