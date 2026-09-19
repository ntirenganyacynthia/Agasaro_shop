from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.dependences import get_current_user
from app.infrastructure.rate_limit import limiter
from app.schemas.auth import LoginRequest, MFAVerifyRequest
from app.services.auth_service import (
    authenticate_user,
    login,
    setup_mfa,
    verify_mfa,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.rate_limit_login)
def login_user(
    request: Request,
    response: Response,
    user: LoginRequest,
    db: Session = Depends(get_db),
):
    return login(
        db,
        user.username,
        user.password,
    )


@router.post(
    "/mfa/setup",
    status_code=status.HTTP_200_OK,
)
def setup_mfa_endpoint(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return setup_mfa(
        db,
        current_user,
    )


@router.post(
    "/mfa/verify",
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.rate_limit_otp_verify)
def verify_mfa_endpoint(
    request: Request,
    response: Response,
    data: MFAVerifyRequest,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        data.username,
        data.password,
    )

    access_token = verify_mfa(
        db,
        user,
        data.code,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me")
def get_my_account(
    current_user=Depends(get_current_user),
):
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "role": current_user.role,
        "mfa_enabled": current_user.mfa_enabled,
    }
