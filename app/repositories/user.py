from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:

    def get_all(self, db: Session):
        return db.query(User).all()

    def get_by_id(self, db: Session, user_id: int):
        return db.query(User).filter(
            User.user_id == user_id
        ).first()

    def get_by_username(self, db: Session, username: str):
        return db.query(User).filter(
            User.username == username
        ).first()

    def create(self, db: Session, data: dict):
        user = User(**data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, user: User, data: dict):
        for field, value in data.items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user

    def delete(self, db: Session, user: User):
        db.delete(user)
        db.commit()

user_repository = UserRepository()
