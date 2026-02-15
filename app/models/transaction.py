import enum
from datetime import date, time

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Action(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class StockTransaction(Base):
    __tablename__ = "stock_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    date: Mapped[date] = mapped_column(Date)
    time: Mapped[time] = mapped_column(Time)
    action: Mapped[Action] = mapped_column(Enum(Action))
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    quantity: Mapped[int]
    price: Mapped[float] = mapped_column(Numeric(12, 4))
    value: Mapped[float] = mapped_column(Numeric(14, 2))
    fee: Mapped[float] = mapped_column(Numeric(10, 2))
    contract_note: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship(back_populates="transactions")


from app.models.user import User  # noqa: E402, F401
