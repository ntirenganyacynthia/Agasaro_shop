from sqlalchemy.orm import Session

from app.models.receipt import Receipt


class ReceiptRepository:

    def get_all(self, db: Session):
        return db.query(Receipt).all()

    def get_by_id(self, db: Session, receipt_id: int):
        return db.query(Receipt).filter(
            Receipt.receipt_id == receipt_id
        ).first()

    def create(self, db: Session, data: dict):

        receipt = Receipt(**data)

        db.add(receipt)
        db.commit()
        db.refresh(receipt)

        return receipt

    def update(
        self,
        db: Session,
        receipt: Receipt,
        data: dict
    ):

        for field, value in data.items():
            setattr(receipt, field, value)

        db.commit()
        db.refresh(receipt)

        return receipt

    def delete(
        self,
        db: Session,
        receipt: Receipt
    ):

        db.delete(receipt)
        db.commit()


receipt_repository = ReceiptRepository()