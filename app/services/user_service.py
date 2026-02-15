from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_or_create_user(db: Session, username: str) -> User:
    stmt = select(User).where(User.username == username)
    user = db.scalars(stmt).first()
    if user:
        return user
    user = User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def delete_user(db: Session, user_id: int) -> bool:
    user = db.get(User, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
