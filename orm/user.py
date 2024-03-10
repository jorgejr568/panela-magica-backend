from datetime import datetime, timezone

from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from orm import BaseOrm
import models


class User(BaseOrm):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def to_dto(self) -> 'models.User':
        return models.User(
            id=self.id,
            name=self.name,
            username=self.username,
            email=self.email,
            created_at=int(self.created_at.astimezone(timezone.utc).timestamp()),
            is_active=self.is_active,
            hashed_password=self.hashed_password,
        )

    def __repr__(self):
        return f'<User {self.username} - {self.id}>'
