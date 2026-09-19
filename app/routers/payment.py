import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.dependences import require_role
from app.schemas.checkout import PaymentStatusResponse
from app.schemas.payment import PaymentRead
from app.services.payment import get_all_payments, get_payment, handle_callback, public_status, refresh


router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/", response_model=list[PaymentRead])
def read_payments(db: Session = Depends(get_db), current_user=Depends(require_role("admin", "cashier"))):
    return get_all_payments(db)


@router.get("/public/{token}", response_model=PaymentStatusResponse)
def public_payment_status(token: str, db: Session = Depends(get_db)):
    return public_status(db, token)


@router.get("/{payment_id}", response_model=PaymentRead)
def read_payment(payment_id: int, db: Session = Depends(get_db), current_user=Depends(require_role("admin", "cashier"))):
    return get_payment(db, payment_id)


@router.post("/{payment_id}/refresh", response_model=PaymentStatusResponse)
def refresh_payment(payment_id: int, db: Session = Depends(get_db), current_user=Depends(require_role("admin", "cashier"))):
    return refresh(db, payment_id)


@router.post("/momo/callback", status_code=status.HTTP_204_NO_CONTENT)
async def momo_callback(
    request: Request,
    x_callback_secret: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    callback_secret = settings.momo_callback_secret
    
    if callback_secret is not None and callback_secret.get_secret_value():
        if not x_callback_secret or not hmac.compare_digest(x_callback_secret, callback_secret.get_secret_value()):

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid callback credentials.")

    payload = await request.json()

    provider_reference = payload.get("referenceId") or payload.get("reference_id") or request.path_params.get("reference_id")
    if not provider_reference:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing provider reference.")
    handle_callback(db, provider_reference, payload)
    return None
