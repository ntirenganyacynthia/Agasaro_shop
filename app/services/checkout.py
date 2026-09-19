from collections import defaultdict
from decimal import Decimal
import secrets

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.customer import Customer
from app.models.payment import Payment
from app.models.product import Product
from app.models.receipt import Receipt
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.services.momo_service import MomoClient, MomoProviderError, get_momo_client
from app.services.phone import mask_phone, normalize_rwanda_phone


PENDING_STATUSES = {"pending", "uncertain"}
SUCCESS_PROVIDER_STATUSES = {"SUCCESSFUL", "SUCCESS", "COMPLETED"}
FAILURE_PROVIDER_STATUSES = {"FAILED", "REJECTED", "CANCELLED", "EXPIRED"}


def _status_url(token: str) -> str:
    return f"/payments/public/{token}"


def _message(payment_status: str, payment_method: str) -> str:
    if payment_status == "completed":
        return "Payment confirmed. Your purchase is complete."
    if payment_status == "failed":
        return "Payment was not completed. Your reserved stock has been released."
    if payment_status == "uncertain":
        return "Payment is still being verified. Do not submit another payment request yet."
    if payment_method == "mobile_money":
        return "Approve the payment request on your MTN MoMo phone, then keep this screen open while we verify it."
    return "Payment is pending."


def _get_existing_checkout(db: Session, idempotency_key: str):
    return (
        db.query(Payment)
        .options(joinedload(Payment.sale).joinedload(Sale.receipt))
        .filter(Payment.idempotency_key == idempotency_key)
        .first()
    )


def _response(payment: Payment):
    sale = payment.sale
    return {
        "sale_id": sale.sale_id,
        "total_amount": sale.total_amount,
        "payment_id": payment.payment_id,
        "payment_status": payment.payment_status,
        "sale_status": sale.sale_status,
        "receipt_id": sale.receipt.receipt_id if sale.receipt else None,
        "status_token": sale.public_status_token,
        "status_url": _status_url(sale.public_status_token),
        "message": _message(payment.payment_status, payment.payment_method),
        "payer_phone_masked": mask_phone(payment.payer_phone),
    }


def _release_reservation(db: Session, sale: Sale) -> None:
    for item in sale.sale_items:
        product = (
            db.query(Product)
            .with_for_update()
            .filter(Product.product_id == item.product_id)
            .one()
        )
        product.reserved_quantity = max(Decimal("0"), product.reserved_quantity - item.quantity)


def _finalize_success(db: Session, payment: Payment, provider_payload: dict | None = None) -> Payment:
    payment = (
        db.query(Payment)
        .options(joinedload(Payment.sale).joinedload(Sale.sale_items))
        .with_for_update()
        .filter(Payment.payment_id == payment.payment_id)
        .one()
    )
    sale = payment.sale
    if payment.payment_status == "completed":
        return payment
    if payment.payment_status in {"failed", "expired", "cancelled"}:
        return payment

    for item in sale.sale_items:
        product = db.query(Product).with_for_update().filter(Product.product_id == item.product_id).one()
        if product.reserved_quantity < item.quantity or product.stock_quantity < item.quantity:
            payment.payment_status = "uncertain"
            payment.status_message = "Inventory changed while payment was processing; manual review is required."
            sale.sale_status = "pending"
            db.commit()
            return payment
        product.reserved_quantity -= item.quantity
        product.stock_quantity -= item.quantity

    payment.payment_status = "completed"
    payment.status_message = "Payment confirmed by the provider." if provider_payload else "Cash payment recorded."
    if provider_payload:
        payment.provider_status = provider_payload.get("status")
        payment.provider_transaction_id = provider_payload.get("financialTransactionId") or provider_payload.get("transactionId")
    sale.sale_status = "completed"
    if sale.receipt is None:
        sale.receipt = Receipt(receipt_number=f"REC-{secrets.token_hex(8).upper()}")
    db.commit()
    db.refresh(payment)
    return payment


def _finalize_failure(db: Session, payment: Payment, provider_payload: dict | None = None) -> Payment:
    payment = (
        db.query(Payment)
        .options(joinedload(Payment.sale).joinedload(Sale.sale_items))
        .with_for_update()
        .filter(Payment.payment_id == payment.payment_id)
        .one()
    )
    if payment.payment_status in {"completed", "failed", "expired", "cancelled"}:
        return payment
    _release_reservation(db, payment.sale)
    payment.payment_status = "failed"
    payment.status_message = "Payment was rejected or expired."
    if provider_payload:
        payment.provider_status = provider_payload.get("status")
        payment.provider_transaction_id = provider_payload.get("financialTransactionId") or provider_payload.get("transactionId")
    payment.sale.sale_status = "cancelled"
    db.commit()
    db.refresh(payment)
    return payment


def apply_provider_status(db: Session, payment: Payment, provider_payload: dict) -> Payment:
    provider_status = str(provider_payload.get("status", "")).upper()
    payment.provider_status = provider_status or None
    payment.provider_transaction_id = provider_payload.get("financialTransactionId") or provider_payload.get("transactionId")
    if provider_status in SUCCESS_PROVIDER_STATUSES:
        return _finalize_success(db, payment, provider_payload)
    if provider_status in FAILURE_PROVIDER_STATUSES:
        return _finalize_failure(db, payment, provider_payload)
    payment.payment_status = "pending"
    payment.status_message = "Waiting for the customer to approve the payment."
    db.commit()
    db.refresh(payment)
    return payment


def checkout(db: Session, data, current_user=None, momo_client: MomoClient | None = None):
    existing = _get_existing_checkout(db, data.idempotency_key)
    if existing is not None:
        return _response(existing)

    phone_number = None
    if data.payment_method == "mobile_money":
        if not data.phone_number:
            raise HTTPException(status_code=422, detail="phone_number is required for mobile_money payments.")
        phone_number = normalize_rwanda_phone(data.phone_number)
    elif data.phone_number:
        phone_number = normalize_rwanda_phone(data.phone_number)

    if data.customer_id is not None:
        customer = db.query(Customer).filter(Customer.customer_id == data.customer_id).first()
        if customer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
        if phone_number:
            customer.customer_phonenumber = phone_number
    else:
        customer = Customer(full_name=data.customer_name, customer_phonenumber=phone_number)
        db.add(customer)
        db.flush()

    quantities = defaultdict(lambda: Decimal("0"))
    for item in data.items:
        quantities[item.product_id] += item.quantity

    products = {}
    for product_id in sorted(quantities):
        product = db.query(Product).with_for_update().filter(Product.product_id == product_id).first()
        if product is None:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found.")
        quantity = quantities[product_id]
        available = product.stock_quantity - product.reserved_quantity
        if available < quantity:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Insufficient available stock for {product.product_name}.")
        products[product_id] = product

    sale = Sale(
        customer_id=customer.customer_id,
        user_id=current_user.user_id if current_user else None,
        total_amount=Decimal("0.00"),
        sale_status="pending",
        public_status_token=secrets.token_urlsafe(32),
    )
    db.add(sale)
    db.flush()

    total = Decimal("0.00")
    for product_id, quantity in quantities.items():
        product = products[product_id]
        unit_price = Decimal(product.unit_price)
        subtotal = (unit_price * quantity).quantize(Decimal("0.01"))
        total += subtotal
        product.reserved_quantity += quantity
        db.add(SaleItem(sale_id=sale.sale_id, product_id=product_id, quantity=quantity, unit_price=unit_price, sub_total=subtotal))

    sale.total_amount = total
    payment = Payment(
        sale_id=sale.sale_id,
        payment_method=data.payment_method,
        amount_paid=total,
        payment_status="pending",
        payer_phone=phone_number,
        idempotency_key=data.idempotency_key,
        status_message="Payment request is being prepared.",
    )
    db.add(payment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = _get_existing_checkout(db, data.idempotency_key)
        if existing is not None:
            return _response(existing)
        raise
    db.refresh(payment)

    if data.payment_method == "cash":
        return _response(_finalize_success(db, payment))
    if data.payment_method == "card":
        payment.payment_status = "failed"
        payment.status_message = "Card payments are not configured yet."
        _release_reservation(db, sale)
        sale.sale_status = "cancelled"
        db.commit()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Card payments are not configured yet.")

    momo_client = momo_client or get_momo_client()
    try:
        provider_reference = momo_client.request_to_pay(total, phone_number, sale.sale_id)
    except MomoProviderError as exc:
        payment = db.query(Payment).filter(Payment.payment_id == payment.payment_id).one()
        payment.payment_status = "uncertain" if exc.uncertain else "failed"
        payment.status_message = exc.message
        payment.provider_status = exc.provider_status
        if not exc.uncertain:
            _release_reservation(db, sale)
            sale.sale_status = "cancelled"
        db.commit()
        return _response(payment)

    payment = db.query(Payment).filter(Payment.payment_id == payment.payment_id).one()
    payment.provider_reference = provider_reference
    payment.payment_status = "pending"
    payment.status_message = "Payment request sent. Approve it on the customer's phone."
    db.commit()
    db.refresh(payment)
    return _response(payment)


def get_status_by_token(db: Session, token: str, momo_client: MomoClient | None = None):
    sale = db.query(Sale).filter(Sale.public_status_token == token).first()
    if sale is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment status not found.")
    payment = db.query(Payment).filter(Payment.sale_id == sale.sale_id).order_by(Payment.payment_id.desc()).first()
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment status not found.")
    if payment.payment_status in PENDING_STATUSES and payment.provider_reference:
        try:
            provider_payload = (momo_client or get_momo_client()).check_payment_status(payment.provider_reference)
            payment = apply_provider_status(db, payment, provider_payload)
        except MomoProviderError as exc:
            payment.status_message = exc.message
            db.commit()
    return _status_response(payment)


def refresh_payment_status(db: Session, payment_id: int, momo_client: MomoClient | None = None):
    payment = db.query(Payment).options(joinedload(Payment.sale)).filter(Payment.payment_id == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
    if payment.payment_status in PENDING_STATUSES and payment.provider_reference:
        try:
            payment = apply_provider_status(db, payment, (momo_client or get_momo_client()).check_payment_status(payment.provider_reference))
        except MomoProviderError as exc:
            payment.status_message = exc.message
            db.commit()
    return _status_response(payment)


def _status_response(payment: Payment):
    sale = payment.sale
    return {
        "sale_id": sale.sale_id,
        "payment_id": payment.payment_id,
        "sale_status": sale.sale_status,
        "payment_status": payment.payment_status,
        "total_amount": sale.total_amount,
        "receipt_id": sale.receipt.receipt_id if sale.receipt else None,
        "message": payment.status_message or _message(payment.payment_status, payment.payment_method),
    }
