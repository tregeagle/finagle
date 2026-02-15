from datetime import UTC, datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    transactions: Mapped[list["StockTransaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


# Avoid circular import at module level
from app.models.transaction import StockTransaction  # noqa: E402, F401
