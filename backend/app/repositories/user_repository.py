from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.persistence.entities import User
from app.core.config import get_settings
from app.core.snowflake import SnowflakeIdGenerator

id_generator = SnowflakeIdGenerator(get_settings().snowflake_worker_id)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def count(self) -> int:
        return self.db.scalar(select(func.count()).select_from(User)) or 0

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_identifier(self, identifier: str) -> User | None:
        return self.db.scalar(select(User).where(or_(User.username == identifier, User.email == identifier)))

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def list(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.id)).all())

    def count_admins(self) -> int:
        return self.db.scalar(select(func.count()).select_from(User).where(User.role == "admin")) or 0

    def create(self, *, username: str, email: str, password_hash: str, role: str) -> User:
        user = User(id=id_generator.next_id(), username=username, email=email, password_hash=password_hash, role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, *, role: str | None, is_active: bool | None) -> User:
        if role is not None:
            user.role = role
        if is_active is not None:
            user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        return user
