from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:

    def get_all(self, db: Session):
        return db.query(Category).all()

    def get_by_id(self, db: Session, category_id: int):
        return db.query(Category).filter(
            Category.category_id == category_id
        ).first()

    def create(self, db: Session, data: dict):
        category = Category(**data)

        db.add(category)
        db.commit()
        db.refresh(category)

        return category

    def update(self, db: Session, category, data: dict):

        for field, value in data.items():
            setattr(category, field, value)

        db.commit()
        db.refresh(category)

        return category

    def delete(self, db: Session, category):

        db.delete(category)
        db.commit()


category_repository = CategoryRepository()