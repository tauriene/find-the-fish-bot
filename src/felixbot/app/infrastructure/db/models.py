from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, DateTime, func, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_username: Mapped[str] = mapped_column(String(100))
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    wins: Mapped[int] = mapped_column(default=0)
    defeats: Mapped[int] = mapped_column(default=0)


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_win: Mapped[bool]
