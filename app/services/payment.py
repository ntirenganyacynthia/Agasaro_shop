from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.payment import Payment
from app.services.checkout import apply_provider_status, get_status_by_token, refresh_payment_status
from app.services.momo_service import MomoClient


def get_all_payments(db: Session):
    return db.query(Payment).order_by(Payment.payment_id.desc()).limit(500).all()


def get_payment(db: Session, payment_id: int):
    payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
    return payment


def refresh(db: Session, payment_id: int, momo_client: MomoClient | None = None):
    return refresh_payment_status(db, payment_id, momo_client)


def handle_callback(db: Session, provider_reference: str, payload: dict):
    payment = (
        db.query(Payment)
        .options(joinedload(Payment.sale))
        .filter(Payment.provider_reference == provider_reference)
        .with_for_update()
        .first()
    )
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment reference not found.")
    return apply_provider_status(db, payment, payload)


def public_status(db: Session, token: str, momo_client: MomoClient | None = None):
    return get_status_by_token(db, token, momo_client)
