from sqlalchemy.orm import Session

from app.models.supplier import Supplier


class SupplierRepository:

    def get_all(self, db: Session):
        return db.query(Supplier).all()

    def get_by_id(self, db: Session, supplier_id: int):
        return db.query(Supplier).filter(
            Supplier.supplier_id == supplier_id
        ).first()

    def create(self, db: Session, data: dict):
        supplier = Supplier(**data)

        db.add(supplier)
        db.commit()
        db.refresh(supplier)

        return supplier

    def update(self, db: Session, supplier, data: dict):

        for field, value in data.items():
            setattr(supplier, field, value)

        db.commit()
        db.refresh(supplier)

        return supplier

    def delete(self, db: Session, supplier):

        db.delete(supplier)
        db.commit()


supplier_repository = SupplierRepository()