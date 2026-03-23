from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from .models import User, Game
from datetime import datetime


class DbRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, tg_id: int, tg_username: str) -> None:
        stmt = insert(User).values(tg_id=tg_id, tg_username=tg_username)
        stmt = stmt.on_conflict_do_nothing(index_elements=["tg_id"])

        await self.session.execute(stmt)
        await self.session.commit()

    async def get_user(self, tg_id: int) -> User | None:
        stmt = select(User).where(User.tg_id == tg_id)

        return await self.session.scalar(stmt)

    async def delete_user(self, tg_id: int) -> None:
        stmt = delete(User).where(User.tg_id == tg_id)

        await self.session.execute(stmt)
        await self.session.commit()

    async def increment_user_wins(self, tg_id: int) -> None:
        stmt = update(User).where(User.tg_id == tg_id).values(wins=User.wins + 1)
        await self.session.execute(stmt)
        await self.session.commit()

    async def increment_user_defeats(self, tg_id: int) -> None:
        stmt = update(User).where(User.tg_id == tg_id).values(defeats=User.defeats + 1)
        await self.session.execute(stmt)
        await self.session.commit()

    async def add_game(self, tg_id: int, ended_at: datetime, is_win: bool) -> None:
        user = await self.get_user(tg_id)

        if not user:
            return

        game = Game(user_id=user.id, ended_at=ended_at, is_win=is_win)

        self.session.add(game)
        await self.session.commit()

    async def get_user_games(self, tg_id: int) -> list[Game]:
        user = await self.get_user(tg_id)
        if not user:
            return []

        stmt = select(Game).where(Game.user_id == user.id)

        result = await self.session.scalars(stmt)
        return list(result)

    async def get_top_users(self, limit: int) -> list[User]:
        stmt = select(User).order_by(User.wins).limit(limit)

        result = await self.session.scalars(stmt)
        return list(result)
